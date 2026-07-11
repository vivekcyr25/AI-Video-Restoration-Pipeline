"""
tests/test_matcher_utils.py
===========================
Unit tests for utils/matcher_utils.py.

All tests operate on in-memory NumPy arrays and Python dicts, so no files
or external dependencies are required beyond NumPy and pytest.
"""

from __future__ import annotations

import numpy as np
import pytest

from utils.matcher_utils import (
    normalize_embeddings,
    cosine_similarity_matrix,
    batch_cosine_similarity,
    top_k_indices,
    align_embeddings,
    embedding_stats,
    filter_low_confidence,
    save_match_results,
)


# ---------------------------------------------------------------------------
# normalize_embeddings
# ---------------------------------------------------------------------------

class TestNormalizeEmbeddings:
    def test_unit_norm_after_normalization(self):
        emb = np.array([[3.0, 4.0], [1.0, 0.0]], dtype=np.float32)
        normed = normalize_embeddings(emb)
        norms = np.linalg.norm(normed, axis=1)
        np.testing.assert_allclose(norms, [1.0, 1.0], atol=1e-6)

    def test_zero_vector_stays_zero(self):
        emb = np.array([[0.0, 0.0], [1.0, 0.0]], dtype=np.float32)
        normed = normalize_embeddings(emb)
        np.testing.assert_array_equal(normed[0], [0.0, 0.0])
        np.testing.assert_allclose(np.linalg.norm(normed[1]), 1.0, atol=1e-6)

    def test_empty_input_returns_empty(self):
        emb = np.empty((0, 512), dtype=np.float32)
        normed = normalize_embeddings(emb)
        assert normed.shape == (0, 512)


# ---------------------------------------------------------------------------
# cosine_similarity_matrix
# ---------------------------------------------------------------------------

class TestCosineSimilarityMatrix:
    def _unit(self, v):
        return (v / np.linalg.norm(v)).astype(np.float32)

    def test_self_similarity_is_one(self):
        q = self._unit(np.array([[1.0, 0.0, 0.0]]))
        sim = cosine_similarity_matrix(q, q)
        np.testing.assert_allclose(sim[0, 0], 1.0, atol=1e-6)

    def test_orthogonal_similarity_is_zero(self):
        q = self._unit(np.array([[1.0, 0.0]]))
        g = self._unit(np.array([[0.0, 1.0]]))
        sim = cosine_similarity_matrix(q, g)
        np.testing.assert_allclose(sim[0, 0], 0.0, atol=1e-6)

    def test_output_shape(self):
        q = normalize_embeddings(np.random.rand(5, 128).astype(np.float32))
        g = normalize_embeddings(np.random.rand(10, 128).astype(np.float32))
        sim = cosine_similarity_matrix(q, g)
        assert sim.shape == (5, 10)

    def test_incompatible_dims_returns_empty(self):
        q = np.random.rand(5, 64).astype(np.float32)
        g = np.random.rand(3, 128).astype(np.float32)
        sim = cosine_similarity_matrix(q, g)
        assert sim.shape == (0, 0)


# ---------------------------------------------------------------------------
# batch_cosine_similarity
# ---------------------------------------------------------------------------

class TestBatchCosineSimilarity:
    def test_matches_cosine_similarity_matrix(self):
        rng = np.random.default_rng(42)
        q = normalize_embeddings(rng.random((8, 64)).astype(np.float32))
        g = normalize_embeddings(rng.random((20, 64)).astype(np.float32))
        expected = cosine_similarity_matrix(q, g)
        result = batch_cosine_similarity(q, g, chunk_size=5)
        np.testing.assert_allclose(result, expected, atol=1e-5)

    def test_small_chunk_matches_large_chunk(self):
        rng = np.random.default_rng(7)
        q = normalize_embeddings(rng.random((4, 32)).astype(np.float32))
        g = normalize_embeddings(rng.random((12, 32)).astype(np.float32))
        r1 = batch_cosine_similarity(q, g, chunk_size=3)
        r2 = batch_cosine_similarity(q, g, chunk_size=100)
        np.testing.assert_allclose(r1, r2, atol=1e-5)


# ---------------------------------------------------------------------------
# top_k_indices
# ---------------------------------------------------------------------------

class TestTopKIndices:
    def test_returns_top_3_sorted_desc(self):
        scores = np.array([0.1, 0.9, 0.5, 0.3, 0.8], dtype=np.float32)
        idx = top_k_indices(scores, k=3)
        assert list(idx) == [1, 4, 2]

    def test_k_larger_than_scores_is_clamped(self):
        scores = np.array([0.5, 0.2], dtype=np.float32)
        idx = top_k_indices(scores, k=10)
        assert len(idx) == 2

    def test_empty_scores_returns_empty(self):
        idx = top_k_indices(np.array([], dtype=np.float32), k=5)
        assert len(idx) == 0


# ---------------------------------------------------------------------------
# align_embeddings
# ---------------------------------------------------------------------------

class TestAlignEmbeddings:
    def test_trims_longer_list(self):
        emb = np.ones((5, 10), dtype=np.float32)
        names = ["a", "b", "c"]
        emb_out, names_out = align_embeddings(emb, names)
        assert emb_out.shape[0] == 3
        assert len(names_out) == 3

    def test_no_trim_when_equal(self):
        emb = np.ones((4, 8), dtype=np.float32)
        names = ["a", "b", "c", "d"]
        emb_out, names_out = align_embeddings(emb, names)
        assert emb_out.shape[0] == 4


# ---------------------------------------------------------------------------
# embedding_stats
# ---------------------------------------------------------------------------

class TestEmbeddingStats:
    def test_basic_stats(self):
        emb = np.eye(4, dtype=np.float32)  # 4 unit vectors
        stats = embedding_stats(emb)
        assert stats["n_rows"] == 4
        assert stats["dim"] == 4
        assert stats["n_zero"] == 0
        np.testing.assert_allclose(stats["mean_norm"], 1.0, atol=1e-5)

    def test_detects_zero_vectors(self):
        emb = np.array([[1.0, 0.0], [0.0, 0.0]], dtype=np.float32)
        stats = embedding_stats(emb)
        assert stats["n_zero"] == 1

    def test_empty_returns_zeros(self):
        emb = np.empty((0, 512), dtype=np.float32)
        stats = embedding_stats(emb)
        assert stats["n_rows"] == 0


# ---------------------------------------------------------------------------
# filter_low_confidence
# ---------------------------------------------------------------------------

class TestFilterLowConfidence:
    def _rows(self):
        return [
            {"Frame": "f1.jpg", "Album": "a1.jpg", "Score": 0.9},
            {"Frame": "f2.jpg", "Album": "a2.jpg", "Score": 0.2},
            {"Frame": "f3.jpg", "Album": "a3.jpg", "Score": 0.5},
            {"Frame": "f4.jpg", "Album": "a4.jpg", "Score": 0.29},
        ]

    def test_default_threshold(self):
        result = filter_low_confidence(self._rows())
        scores = [r["Score"] for r in result]
        assert all(s >= 0.3 for s in scores)
        assert len(result) == 2  # 0.9 and 0.5

    def test_custom_threshold(self):
        result = filter_low_confidence(self._rows(), threshold=0.8)
        assert len(result) == 1
        assert result[0]["Score"] == 0.9

    def test_empty_input(self):
        assert filter_low_confidence([]) == []


# ---------------------------------------------------------------------------
# save_match_results
# ---------------------------------------------------------------------------

class TestSaveMatchResults:
    def test_creates_csv_with_header(self, tmp_path):
        rows = [
            {"Frame": "f1.jpg", "Album": "a1.jpg", "Score": 0.85},
            {"Frame": "f2.jpg", "Album": "a2.jpg", "Score": 0.72},
        ]
        out = tmp_path / "results.csv"
        save_match_results(rows, out)
        assert out.exists()
        lines = out.read_text().splitlines()
        assert lines[0] == "Frame,Album,Score"
        assert "f1.jpg" in lines[1]

    def test_raises_on_empty_rows_without_fieldnames(self, tmp_path):
        with pytest.raises(ValueError):
            save_match_results([], tmp_path / "out.csv")

    def test_creates_parent_directory(self, tmp_path):
        rows = [{"Frame": "x", "Score": 1.0}]
        out = tmp_path / "nested" / "deep" / "out.csv"
        save_match_results(rows, out)
        assert out.exists()
