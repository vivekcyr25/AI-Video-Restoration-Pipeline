> See also: [Interactive preview site](preview.md)

# Pipeline Architecture

This document describes the full 9-stage AI Video Restoration pipeline using a
Mermaid diagram, followed by data-flow notes for each connection.

---

## High-Level Pipeline Diagram

```mermaid
flowchart TD
    A([🎬 Input Video\nWedding_Compressed_AAC.mp4]) --> B

    subgraph STAGE1 ["Stage 1 — Scene Detection"]
        B["PySceneDetect\n+ FFmpeg Probe\n\nDetects scene boundaries\nby analysing inter-frame\nhistogram differences"]
    end

    B --> C

    subgraph STAGE2 ["Stage 2 — Frame Extraction"]
        C["FFmpeg\nframe extractor\n\nExports one representative\nframe per scene as JPEG"]
    end

    C --> D
    C --> E

    subgraph STAGE3 ["Stage 3A — CLIP Embeddings"]
        D["OpenCLIP ViT-B-32\n(LAION-2B weights)\n\nEncodes album photos\nand representative frames\ninto 512-dim vectors"]
    end

    subgraph STAGE4 ["Stage 3B — Face Embeddings"]
        E["InsightFace buffalo_l\n\nDetects largest face per image\nExtracts 512-dim ArcFace\nidentity embeddings"]
    end

    D --> F
    E --> F

    subgraph STAGE5 ["Stage 4 — Hybrid Matching"]
        F["Advanced Matcher\n\nCLIP score × 0.30\n+ Face score × 0.70\n= Ranked album candidates\nper representative frame"]
    end

    F --> G
    F --> H

    subgraph STAGE6A ["Stage 5A — Restoration v1\n(SIFT Homography)"]
        G["restore_frame.py\n\nSIFT keypoints → homography\nCLAHE luminance enhance\nBilateral + Unsharp mask\nConfidence-weighted blend"]
    end

    subgraph STAGE6B ["Stage 5B — Restoration v2\n(Face-Affine + Detail Transfer)"]
        H["restore_frame_v2.py\n\nFace-guided affine alignment\nTexture/gradient confidence map\nHigh-frequency detail transfer\nAdaptive CLAHE + unsharp"]
    end

    G --> I
    H --> I

    subgraph STAGE7 ["Stage 6 — Video Reconstruction"]
        I["rebuild_video.py\n\nOptical flow propagation\n(Farnebäck dense flow)\nPropagates restored delta\nfrom representative frame\nto every frame in scene"]
    end

    A --> J

    subgraph STAGE8 ["Stage 7 — Audio Merge"]
        J["FFmpeg mux\n\nCopies original AAC audio\nstream into reconstructed\nvideo container\n(zero re-encoding)"]
    end

    I --> J
    J --> K([✅ Final Output\nRestored_Wedding.mp4\nwith original audio])
```

---

## Data Flow Summary

| Connection | Data Transferred |
|---|---|
| Video → Scene Detection | Raw video stream (pixel data) |
| Scene Detection → Frame Extraction | Scene CSV (start frame, end frame, length) |
| Frame Extraction → CLIP | Representative frame JPEGs |
| Frame Extraction → Face | Representative frame JPEGs |
| Album Photos → CLIP | Album photo JPEGs |
| Album Photos → Face | Album photo JPEGs |
| CLIP + Face → Matcher | `.npy` embedding matrices + name lists |
| Matcher → Restore | `advanced_matches.csv` (Frame, AlbumImage, Rank, Scores) |
| Restore → Rebuild | Restored representative frame JPEGs |
| Rebuild → Audio Merge | Silent reconstructed `.mp4` |
| Video → Audio Merge | Original AAC audio stream |

---

## Key Design Decisions

### Why scene-based processing?
Processing every frame individually against every album photo would be
computationally intractable (~30 fps × hours of video × hundreds of album
photos = billions of comparisons). Scene detection reduces this to one
representative frame per scene (~50–200 scenes per hour of video).

### Why 70% face / 30% CLIP weighting?
Wedding videos are identity-centric. A frame containing the couple's faces
must match an album photo of the same faces even if the background, lighting,
or clothing color shifts the CLIP score. Face embeddings provide pose- and
lighting-invariant identity matching that CLIP alone cannot guarantee.

### Why optical flow propagation?
Directly applying the restoration to only representative frames would produce
visible temporal discontinuities (flicker) at scene transitions. The
Farnebäck dense optical flow warps the enhancement delta from the reference
frame to all neighboring frames in the scene, preserving temporal coherence.

### Why two restoration versions?
- **v1** (SIFT homography): Robust when faces are small or absent; uses global
  geometric alignment between album and frame.
- **v2** (Face affine): More accurate when both images contain large, matching
  faces; uses face-landmark-guided affine transform for sub-pixel alignment.

