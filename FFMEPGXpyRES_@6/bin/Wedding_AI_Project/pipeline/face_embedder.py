"""
pipeline/face_embedder.py
=========================
Stage 4: Face Detection and Embedding Generation.
Uses InsightFace (buffalo_l) on GPU (using ONNX Runtime CUDA provider if available).
Implements a face cache (JSON format) containing landmarks, bounding boxes, and embeddings
to avoid redundant detection runs on resume.
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
from pathlib import Path

import cv2
import numpy as np

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("face_embedder")

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
DETECTION_SIZE = (640, 640)


class FaceEmbedderStage:
    def __init__(self, config: dict):
        self.config = config
        self.device = config["global"]["device"]
        self.albums_dir = Path(config["global"]["albums_dir"])
        self.frames_dir = Path(config["frame_extractor"]["output_dir"])
        self.models_dir = Path(config["global"]["models_dir"])
        
        cfg = config["face_embeddings"]
        self.detection_size = tuple(cfg["detection_size"])
        self.face_cache_path = Path(cfg["face_cache_path"])
        
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.cache = self._load_cache()

    def _load_cache(self) -> dict:
        if self.face_cache_path.exists():
            try:
                with open(self.face_cache_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load face cache: {e}. Starting fresh.")
        return {}

    def _save_cache(self) -> None:
        self.face_cache_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(self.face_cache_path, "w", encoding="utf-8") as f:
                json.dump(self.cache, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save face cache: {e}")

    def _get_image_paths(self, folder: Path) -> list[Path]:
        if not folder.exists():
            return []
        return sorted(
            [p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS],
            key=lambda x: x.name.lower()
        )

    def _initialize_detector(self):
        from insightface.app import FaceAnalysis
        logger.info("Initializing InsightFace detector...")
        providers = ["CUDAExecutionProvider", "CPUExecutionProvider"] if self.device == "cuda" else ["CPUExecutionProvider"]
        # Prepare app with correct execution providers
        app = FaceAnalysis(name="buffalo_l", providers=providers)
        ctx_id = 0 if self.device == "cuda" else -1
        app.prepare(ctx_id=ctx_id, det_size=self.detection_size)
        return app

    def _extract_and_cache(self, image_paths: list[Path], force: bool = False) -> None:
        # Check which paths need detection
        missing_paths = [p for p in image_paths if force or p.name not in self.cache]
        
        if not missing_paths:
            logger.info("All images already present in face cache. Skipping face detection run.")
            return

        logger.info(f"Extracting faces for {len(missing_paths)} / {len(image_paths)} images...")
        app = self._initialize_detector()
        
        for p in missing_paths:
            try:
                img = cv2.imread(str(p))
                if img is None:
                    continue
                    
                faces = app.get(img)
                if not faces:
                    # Save as null to indicate no face detected, avoiding future re-detection
                    self.cache[p.name] = None
                    continue
                    
                # Store the largest face by bounding box area
                largest_face = max(
                    faces,
                    key=lambda f: (f.bbox[2] - f.bbox[0]) * (f.bbox[3] - f.bbox[1])
                )
                
                self.cache[p.name] = {
                    "bbox": [float(val) for val in largest_face.bbox],
                    "kps": [[float(coord) for coord in pt] for pt in largest_face.kps],
                    "embedding": [float(val) for val in largest_face.embedding],
                    "score": float(largest_face.det_score)
                }
            except Exception as e:
                logger.error(f"Error processing face for {p.name}: {e}")
                self.cache[p.name] = None
                
        # Save cache immediately
        self._save_cache()
        
        # Free ORT sessions
        del app

    def _export_numpy_and_csv(self, all_paths: list[Path], prefix: str) -> None:
        embeddings = []
        names = []
        mapping = []
        
        emb_index = 0
        for p in all_paths:
            cache_val = self.cache.get(p.name)
            if cache_val is not None and cache_val.get("embedding") is not None:
                embeddings.append(np.array(cache_val["embedding"], dtype=np.float32))
                names.append(p.name)
                
                bbox = cache_val["bbox"]
                mapping.append({
                    "image": p.name,
                    "embedding_index": emb_index,
                    "x1": bbox[0],
                    "y1": bbox[1],
                    "x2": bbox[2],
                    "y2": bbox[3],
                    "score": cache_val["score"]
                })
                emb_index += 1
                
        emb_arr = np.stack(embeddings, axis=0) if embeddings else np.empty((0, 512), dtype=np.float32)
        names_arr = np.array(names)
        
        # Save .npy and .csv files
        emb_path = self.models_dir / f"{prefix}_face_embeddings.npy"
        names_path = self.models_dir / f"{prefix}_face_names.npy"
        csv_path = self.models_dir / f"{prefix}_face_names.csv"
        
        np.save(emb_path, emb_arr)
        np.save(names_path, names_arr)
        
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            if mapping:
                writer = csv.DictWriter(f, fieldnames=mapping[0].keys())
                writer.writeheader()
                writer.writerows(mapping)
            else:
                writer = csv.writer(f)
                writer.writerow(["image", "embedding_index", "x1", "y1", "x2", "y2", "score"])
                
        logger.info(f"Exported {len(embeddings)} face embeddings to {emb_path} and metadata to {csv_path}")

    def run(self, force: bool = False) -> None:
        logger.info("Starting Stage 4: InsightFace Detection and Embedding")
        
        album_paths = self._get_image_paths(self.albums_dir)
        frame_paths = self._get_image_paths(self.frames_dir)
        
        if not album_paths and not frame_paths:
            logger.warning("No album photos or representative frames found. Skipping stage.")
            return
            
        # Run face detection and fill cache
        self._extract_and_cache(album_paths + frame_paths, force=force)
        
        # Export individual embedding arrays for matcher stage
        self._export_numpy_and_csv(album_paths, "album")
        self._export_numpy_and_csv(frame_paths, "frame")
        
        logger.info("Stage 4 completed.")


if __name__ == "__main__":
    import yaml
    p = argparse.ArgumentParser(description="Stage 4: Face Detection and Embedding")
    p.add_argument("--config", type=Path, default=Path("configs/pipeline_config.yaml"))
    p.add_argument("--force", action="store_true", help="Force rebuild of face embeddings and ignore cache")
    args = p.parse_args()
    
    with open(args.config, "r") as f:
        cfg = yaml.safe_load(f)
        
    stage = FaceEmbedderStage(cfg)
    stage.run(force=args.force)
