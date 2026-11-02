"""
tests/test_preconditions.py
===========================
Unit tests for precondition enhancements:
  1. Real-ESRGAN config-driven num_block parameterization (nb=23 for x4plus vs nb=6 for anime)
  2. FaceEmbedderStage CUDA provider check and require_gpu guard
  3. Identity precision evaluator: Wilson score confidence interval and empty-label handling
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest
import torch

from pipeline.realesrgan_engine import RealESRGANEngine, _get_model_classes
from pipeline.face_embedder import FaceEmbedderStage
from scripts.identity_precision import evaluate_identity_precision, wilson_score_interval


# ─────────────────────────────────────────────────────────────────────────────
# 1. Real-ESRGAN Model Configuration & Block Architecture
# ─────────────────────────────────────────────────────────────────────────────

def test_realesrgan_num_block_classes():
    """Verify that RRDBNet architecture dynamically sets block count."""
    _, _, RRDBNet = _get_model_classes()
    
    # x4plus photo model uses 23 blocks
    net_photo = RRDBNet(in_nc=3, out_nc=3, nf=64, nb=23, gc=32, scale=4)
    assert len(net_photo.body) == 23
    
    # anime model uses 6 blocks
    net_anime = RRDBNet(in_nc=3, out_nc=3, nf=64, nb=6, gc=32, scale=4)
    assert len(net_anime.body) == 6


def test_realesrgan_photo_model_weights_and_keys(tmp_path):
    """Verify RealESRGAN_x4plus weights load strictly without missing/unexpected keys."""
    weights_path = Path("Models/RealESRGAN_x4plus.pth")
    if not weights_path.exists():
        pytest.skip("Models/RealESRGAN_x4plus.pth not downloaded locally")
        
    _, _, RRDBNet = _get_model_classes()
    model = RRDBNet(in_nc=3, out_nc=3, nf=64, nb=23, gc=32, scale=4)
    state_dict = torch.load(str(weights_path), map_location="cpu")
    if "params_ema" in state_dict:
        state_dict = state_dict["params_ema"]
    elif "params" in state_dict:
        state_dict = state_dict["params"]
        
    # strict=True confirms exact architecture match
    model.load_state_dict(state_dict, strict=True)
    assert len(model.body) == 23


# ─────────────────────────────────────────────────────────────────────────────
# 2. InsightFace CUDA Provider Check & require_gpu
# ─────────────────────────────────────────────────────────────────────────────

def test_face_embedder_require_gpu_guard(monkeypatch):
    """Verify that require_gpu=True raises when CUDAExecutionProvider is missing."""
    import onnxruntime as ort
    
    # Mock get_available_providers to only return CPU
    monkeypatch.setattr(ort, "get_available_providers", lambda: ["CPUExecutionProvider"])
    
    cfg = {
        "global": {"device": "cuda", "albums_dir": "Albums_sample", "models_dir": "Models"},
        "frame_extractor": {"output_dir": "Representative_Frames"},
        "face_embeddings": {
            "detection_size": [640, 640],
            "face_cache_path": "Models/face_cache.json",
            "require_gpu": True
        }
    }
    stage = FaceEmbedderStage(cfg)
    
    with pytest.raises(RuntimeError, match="CUDAExecutionProvider is not available"):
        stage._initialize_detector()


def test_face_embedder_cpu_fallback_when_allowed(monkeypatch):
    """Verify that require_gpu=False allows fallback to CPU."""
    import onnxruntime as ort
    monkeypatch.setattr(ort, "get_available_providers", lambda: ["CPUExecutionProvider"])
    
    cfg = {
        "global": {"device": "cuda", "albums_dir": "Albums_sample", "models_dir": "Models"},
        "frame_extractor": {"output_dir": "Representative_Frames"},
        "face_embeddings": {
            "detection_size": [640, 640],
            "face_cache_path": "Models/face_cache.json",
            "require_gpu": False
        }
    }
    stage = FaceEmbedderStage(cfg)
    # Detector will initialize using CPU without raising
    app = stage._initialize_detector()
    assert app is not None


# ─────────────────────────────────────────────────────────────────────────────
# 3. Identity Precision & Wilson Interval Tests
# ─────────────────────────────────────────────────────────────────────────────

def test_wilson_score_interval_math():
    """Verify Wilson score confidence interval mathematical bounds."""
    # Perfect score: 20/20
    low, high = wilson_score_interval(20, 20, confidence=0.95)
    assert 0.83 <= low <= 0.86
    assert high == 1.0
    
    # Zero trials
    low, high = wilson_score_interval(0, 0)
    assert (low, high) == (0.0, 0.0)
    
    # 50% score: 50/100
    low, high = wilson_score_interval(50, 100, confidence=0.95)
    assert 0.40 <= low <= 0.45
    assert 0.55 <= high <= 0.60


def test_identity_precision_skips_empty_labels_and_enforces_minimum(tmp_path):
    """Verify that identity_precision skips empty labels and errors on < min_required."""
    labels_csv = tmp_path / "labels.csv"
    cands_csv = tmp_path / "cands.csv"
    out_json = tmp_path / "out.json"
    
    # Write 25 rows, but only 10 populated
    with open(labels_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["frame_path", "face_index", "true_person_id"])
        for i in range(10):
            w.writerow([f"frame_{i}.jpg", 0, "person_A"])
        for i in range(10, 25):
            w.writerow([f"frame_{i}.jpg", 0, ""])  # Empty labels
            
    # Should raise ValueError because only 10 valid labels exist (< 20 required)
    with pytest.raises(ValueError, match="Fewer than 20 labeled faces found"):
        evaluate_identity_precision(labels_csv, cands_csv, out_json, min_required_labels=20)


def test_identity_precision_calculation(tmp_path):
    """Verify precision, coverage, and Wilson intervals with >= 20 labels."""
    labels_csv = tmp_path / "labels.csv"
    cands_csv = tmp_path / "cands.csv"
    out_json = tmp_path / "out.json"
    
    with open(labels_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["frame_path", "face_index", "true_person_id"])
        for i in range(20):
            w.writerow([f"frame_{i}.jpg", 0, f"person_{i}"])
            
    with open(cands_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["frame_path", "face_index", "top1_album_match"])
        for i in range(20):
            # 19 correct matches, 1 mismatch
            match_name = f"person_{i}_photo.jpg" if i < 19 else "different_person.jpg"
            w.writerow([f"frame_{i}.jpg", 0, match_name])
            
    res = evaluate_identity_precision(labels_csv, cands_csv, out_json, min_required_labels=20)
    assert res["labeled_faces_count"] == 20
    assert res["assigned_faces_count"] == 20
    assert res["correct_references_count"] == 19
    assert res["precision"] == 0.95
    assert res["coverage"] == 1.0
    assert res["wilson_95_ci"][0] > 0.70
    assert res["wilson_95_ci"][1] <= 1.0
    assert out_json.exists()

