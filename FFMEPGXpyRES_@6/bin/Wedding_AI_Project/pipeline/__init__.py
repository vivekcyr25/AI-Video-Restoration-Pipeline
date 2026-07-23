"""
AI Video Restoration Pipeline Packages.
"""

from __future__ import annotations

from .video_repair import VideoRepairStage
from .frame_extractor import FrameExtractorStage
from .clip_embedder import CLIPEmbedderStage
from .face_embedder import FaceEmbedderStage
from .reference_selector import ReferenceSelectorStage
from .main_restoration import ReferenceRestorer
from .video_propagation import VideoPropagationStage
from .realesrgan_engine import RealESRGANEngine
from .quality_validator import QualityValidator

# Keep alias for backwards compatibility
HybridMatcherStage = ReferenceSelectorStage

__all__ = [
    "VideoRepairStage",
    "FrameExtractorStage",
    "CLIPEmbedderStage",
    "FaceEmbedderStage",
    "ReferenceSelectorStage",
    "HybridMatcherStage",
    "ReferenceRestorer",
    "VideoPropagationStage",
    "RealESRGANEngine",
    "QualityValidator",
]
