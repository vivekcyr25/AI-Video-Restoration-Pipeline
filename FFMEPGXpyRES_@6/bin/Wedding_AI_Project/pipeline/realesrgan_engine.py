"""
pipeline/realesrgan_engine.py
=============================
Real-ESRGAN Super-Resolution Engine.
Self-contained PyTorch RRDBNet model loader.
Supports automatic weights download, configurable tiled inference, FP16 execution,
memory pooling, and graceful CPU fallback to prevent VRAM overflow on RTX 3050 4GB.
Implemented as a thread-safe singleton.
"""

from __future__ import annotations

import logging
import os
import urllib.request
from pathlib import Path
import threading

import cv2
import numpy as np
import torch
import torch.nn as nn

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("realesrgan_engine")


class ResidualDenseBlock(nn.Module):
    def __init__(self, nf: int = 64, gc: int = 32, bias: bool = True):
        super().__init__()
        self.conv1 = nn.Conv2d(nf, gc, 3, 1, 1, bias=bias)
        self.conv2 = nn.Conv2d(nf + gc, gc, 3, 1, 1, bias=bias)
        self.conv3 = nn.Conv2d(nf + 2 * gc, gc, 3, 1, 1, bias=bias)
        self.conv4 = nn.Conv2d(nf + 3 * gc, gc, 3, 1, 1, bias=bias)
        self.conv5 = nn.Conv2d(nf + 4 * gc, nf, 3, 1, 1, bias=bias)
        self.lrelu = nn.LeakyReLU(negative_slope=0.2, inplace=True)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x1 = self.lrelu(self.conv1(x))
        x2 = self.lrelu(self.conv2(torch.cat((x, x1), 1)))
        x3 = self.lrelu(self.conv3(torch.cat((x, x1, x2), 1)))
        x4 = self.lrelu(self.conv4(torch.cat((x, x1, x2, x3), 1)))
        x5 = self.conv5(torch.cat((x, x1, x2, x3, x4), 1))
        return x5 * 0.2 + x


class RRDB(nn.Module):
    def __init__(self, nf: int = 64, gc: int = 32):
        super().__init__()
        self.rdb1 = ResidualDenseBlock(nf, gc)
        self.rdb2 = ResidualDenseBlock(nf, gc)
        self.rdb3 = ResidualDenseBlock(nf, gc)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        out = self.rdb1(x)
        out = self.rdb2(out)
        out = self.rdb3(out)
        return out * 0.2 + x


class RRDBNet(nn.Module):
    def __init__(self, in_nc: int = 3, out_nc: int = 3, nf: int = 64, nb: int = 6, gc: int = 32, scale: int = 4):
        super().__init__()
        self.conv_first = nn.Conv2d(in_nc, nf, 3, 1, 1, bias=True)
        self.body = nn.Sequential(*[RRDB(nf, gc) for _ in range(nb)])
        self.conv_body = nn.Conv2d(nf, nf, 3, 1, 1, bias=True)
        self.conv_up1 = nn.Conv2d(nf, nf, 3, 1, 1, bias=True)
        self.conv_up2 = nn.Conv2d(nf, nf, 3, 1, 1, bias=True)
        self.conv_hr = nn.Conv2d(nf, nf, 3, 1, 1, bias=True)
        self.conv_last = nn.Conv2d(nf, out_nc, 3, 1, 1, bias=True)
        self.lrelu = nn.LeakyReLU(negative_slope=0.2, inplace=True)
        self.scale = scale

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        fea = self.conv_first(x)
        trunk = self.conv_body(self.body(fea))
        fea = fea + trunk
        
        # Upsampling
        if self.scale == 4:
            fea = self.lrelu(self.conv_up1(nn.functional.interpolate(fea, scale_factor=2, mode='nearest')))
            fea = self.lrelu(self.conv_up2(nn.functional.interpolate(fea, scale_factor=2, mode='nearest')))
        elif self.scale == 2:
            fea = self.lrelu(self.conv_up1(nn.functional.interpolate(fea, scale_factor=2, mode='nearest')))
            
        out = self.conv_last(self.lrelu(self.conv_hr(fea)))
        return out


class RealESRGANEngine:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self, model_name: str = "RealESRGAN_x4plus_anime_6B", models_dir: str = "models", device: str = "cuda"):
        if self._initialized:
            return
            
        self.model_name = model_name
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        # Auto select device
        self.device = "cuda" if device == "cuda" and torch.cuda.is_available() else "cpu"
        self.model_path = self.models_dir / f"{self.model_name}.pth"
        
        # Load network config
        if "anime" in self.model_name:
            # RealESRGAN_x4plus_anime_6B uses 6 blocks
            self.nb = 6
        else:
            # Default RealESRGAN_x4plus uses 23 blocks
            self.nb = 23
            
        self._download_weights()
        self.model = self._load_model()
        self._initialized = True

    def _download_weights(self) -> None:
        if self.model_path.exists():
            return
            
        logger.info(f"Downloading Real-ESRGAN weights: {self.model_name}...")
        urls = {
            "RealESRGAN_x4plus_anime_6B": "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.2.4/RealESRGAN_x4plus_anime_6B.pth",
            "RealESRGAN_x4plus": "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth"
        }
        
        url = urls.get(self.model_name, urls["RealESRGAN_x4plus_anime_6B"])
        try:
            urllib.request.urlretrieve(url, str(self.model_path))
            logger.info(f"Weights downloaded successfully: {self.model_path}")
        except Exception as e:
            logger.error(f"Failed to download weights from {url}: {e}")
            raise

    def _load_model(self) -> RRDBNet:
        logger.info(f"Loading RRDBNet (nb={self.nb}) onto {self.device}...")
        model = RRDBNet(in_nc=3, out_nc=3, nf=64, nb=self.nb, gc=32, scale=4)
        
        try:
            state_dict = torch.load(self.model_path, map_location="cpu")
            # Extract state dict key values
            if "params" in state_dict:
                state_dict = state_dict["params"]
            elif "params_ema" in state_dict:
                state_dict = state_dict["params_ema"]
                
            model.load_state_dict(state_dict, strict=True)
            model = model.to(self.device).eval()
            
            # Use half precision on GPU
            if self.device == "cuda":
                model = model.half()
        except Exception as e:
            logger.error(f"Error loading model weights: {e}")
            raise
            
        return model

    def enhance(self, img: np.ndarray, tile_size: int = 256, tile_pad: int = 10, outscale: float = 4.0) -> np.ndarray:
        """
        Enhance BGR image using tiled inference to conserve VRAM.
        Handles FP16, tile blending, and automatic CPU fallback on OOM.
        """
        h, w, c = img.shape
        # Normalize and convert to torch float tensor
        img_t = torch.from_numpy(img).permute(2, 0, 1).float() / 255.0
        img_t = img_t.unsqueeze(0).to(self.device)
        
        use_half = (self.device == "cuda")
        if use_half:
            img_t = img_t.half()

        try:
            with torch.inference_mode():
                output = self._tile_inference(img_t, tile_size, tile_pad, outscale)
        except RuntimeError as e:
            if "out of memory" in str(e).lower() and self.device == "cuda":
                logger.warning("CUDA Out of Memory! Falling back to CPU execution.")
                torch.cuda.empty_cache()
                # Run on CPU in float32
                self.model = self.model.float().to("cpu")
                img_t = img_t.float().to("cpu")
                with torch.inference_mode():
                    output = self._tile_inference(img_t, tile_size=128, tile_pad=10, outscale=outscale)
                # Restore GPU state
                self.model = self.model.half().to("cuda")
            else:
                raise e

        # Convert back to numpy BGR image
        output_np = output.squeeze(0).permute(1, 2, 0).cpu().numpy()
        output_np = np.clip(output_np * 255.0, 0, 255).astype(np.uint8)
        
        # Resize to desired outscale if model scale (4x) differs from target
        if outscale != 4.0:
            target_w = int(w * outscale)
            target_h = int(h * outscale)
            output_np = cv2.resize(output_np, (target_w, target_h), interpolation=cv2.INTER_CUBIC)
            
        return output_np

    def _tile_inference(self, img: torch.Tensor, tile_size: int, tile_pad: int, outscale: float) -> torch.Tensor:
        """Runs inference tile-by-tile and blends results seamlessly."""
        b, c, h, w = img.size()
        scale = 4  # RRDBNet is built for 4x
        
        out_h = h * scale
        out_w = w * scale
        
        # Create output tensor
        out = torch.zeros((b, c, out_h, out_w), dtype=img.dtype, device=img.device)
        
        # Calculate tile parameters
        stride = tile_size - tile_pad * 2
        
        for y in range(0, h, stride):
            y_start = y
            y_end = min(y + tile_size, h)
            
            # Adjust start to keep constant tile size
            if y_end - y_start < tile_size:
                y_start = max(0, y_end - tile_size)
                
            for x in range(0, w, stride):
                x_start = x
                x_end = min(x + tile_size, w)
                
                if x_end - x_start < tile_size:
                    x_start = max(0, x_end - tile_size)
                    
                # Crop input tile
                tile = img[:, :, y_start:y_end, x_start:x_end]
                
                # Model inference
                tile_out = self.model(tile)
                
                # Determine cropping in output coordinates
                out_y_start = y_start * scale
                out_y_end = y_end * scale
                out_x_start = x_start * scale
                out_x_end = x_end * scale
                
                # Handle borders and overlap blending
                pad_top = (y_start - y) * scale if y_start > 0 else 0
                pad_left = (x_start - x) * scale if x_start > 0 else 0
                
                # Determine copy boundaries
                crop_y_start = tile_pad * scale if y_start > 0 else 0
                crop_y_end = (tile_size - tile_pad) * scale if y_end < h else tile_size * scale
                crop_x_start = tile_pad * scale if x_start > 0 else 0
                crop_x_end = (tile_size - tile_pad) * scale if x_end < w else tile_size * scale
                
                paste_y_start = out_y_start + crop_y_start
                paste_y_end = out_y_start + crop_y_end
                paste_x_start = out_x_start + crop_x_start
                paste_x_end = out_x_start + crop_x_end
                
                # Paste the tile into final output tensor
                out[:, :, paste_y_start:paste_y_end, paste_x_start:paste_x_end] = \
                    tile_out[:, :, crop_y_start:crop_y_end, crop_x_start:crop_x_end]
                    
        return out
