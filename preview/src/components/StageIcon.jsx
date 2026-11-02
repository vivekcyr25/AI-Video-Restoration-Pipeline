import React from 'react'

/**
 * Perfectly crafted vector logos for each pipeline stage and restoration phase,
 * replacing standard generic emojis with precision-engineered SVG glyphs.
 */

// ── Stage 01: Video Repair & CFR Transcode (FFmpeg & PySceneDetect) ──
export function VideoRepairIcon({ className = 'w-6 h-6' }) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
      aria-hidden="true"
    >
      {/* Outer film/clapper slate body */}
      <rect x="2.5" y="4" width="19" height="16" rx="2.5" />
      {/* Clapper header bar with diagonal synchronization slashes */}
      <path d="M2.5 9h19" />
      <path d="M6.5 4l2.5 5" />
      <path d="M11 4l2.5 5" />
      <path d="M15.5 4l2.5 5" />
      {/* CFR frame synchronization / play glyph */}
      <polygon points="10,12 15,14.5 10,17" fill="currentColor" fillOpacity="0.25" />
    </svg>
  )
}

// ── Stage 02: Representative Frame Extraction (FFmpeg Fast-Seek Midpoint) ──
export function FrameExtractIcon({ className = 'w-6 h-6' }) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
      aria-hidden="true"
    >
      {/* High-precision camera viewfinder corner reticles */}
      <path d="M3.5 7.5V4.5A1 1 0 0 1 4.5 3.5h3" />
      <path d="M16.5 3.5h3a1 1 0 0 1 1 1v3" />
      <path d="M20.5 16.5v3a1 1 0 0 1-1 1h-3" />
      <path d="M7.5 20.5h-3a1 1 0 0 1-1-1v-3" />
      {/* Target anchor frame with midpoint crosshair */}
      <rect x="6.5" y="6.5" width="11" height="11" rx="1.5" />
      <circle cx="10" cy="10" r="1.25" fill="currentColor" fillOpacity="0.3" />
      <path d="M7.5 15l2.5-3 2 2.5 1.5-1.5 3 3" />
      <circle cx="12" cy="12" r="0.75" fill="currentColor" />
    </svg>
  )
}

// ── Stage 03: Batch CLIP Semantic Embeddings (OpenCLIP ViT-B-32 FP16) ──
export function ClipEmbedIcon({ className = 'w-6 h-6' }) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
      aria-hidden="true"
    >
      {/* Vision Transformer / Neural network latent node architecture */}
      <circle cx="6" cy="6" r="2" fill="currentColor" fillOpacity="0.2" />
      <circle cx="6" cy="18" r="2" fill="currentColor" fillOpacity="0.2" />
      <circle cx="18" cy="6" r="2" fill="currentColor" fillOpacity="0.2" />
      <circle cx="18" cy="18" r="2" fill="currentColor" fillOpacity="0.2" />
      <circle cx="12" cy="12" r="2.5" fill="currentColor" fillOpacity="0.3" />
      {/* Multi-modal cross-attention vector bridges */}
      <line x1="7.8" y1="7.4" x2="10.2" y2="10.6" />
      <line x1="7.8" y1="16.6" x2="10.2" y2="13.4" />
      <line x1="16.2" y1="7.4" x2="13.8" y2="10.6" />
      <line x1="16.2" y1="16.6" x2="13.8" y2="13.4" />
      <line x1="6" y1="8" x2="6" y2="16" strokeDasharray="1 2" />
      <line x1="18" y1="8" x2="18" y2="16" strokeDasharray="1 2" />
    </svg>
  )
}

// ── Stage 04: InsightFace Identity Detection & Cache (ArcFace + RetinaFace) ──
export function FaceEmbedIcon({ className = 'w-6 h-6' }) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
      aria-hidden="true"
    >
      {/* Biometric scanning target corner brackets */}
      <path d="M3 7V4.5A1.5 1.5 0 0 1 4.5 3H7" />
      <path d="M17 3h2.5A1.5 1.5 0 0 1 21 4.5V7" />
      <path d="M21 17v2.5a1.5 1.5 0 0 1-1.5 1.5H17" />
      <path d="M7 21H4.5A1.5 1.5 0 0 1 3 19.5V17" />
      {/* Biometric face contour */}
      <circle cx="12" cy="10" r="3.2" fill="currentColor" fillOpacity="0.15" />
      <path d="M7.5 18a4.5 4.5 0 0 1 9 0" />
      {/* 5-point facial landmark nodes */}
      <circle cx="10.7" cy="9.6" r="0.8" fill="currentColor" />
      <circle cx="13.3" cy="9.6" r="0.8" fill="currentColor" />
      <circle cx="12" cy="11.4" r="0.6" fill="currentColor" />
      {/* Laser scan line */}
      <line x1="4.5" y1="12" x2="19.5" y2="12" strokeDasharray="1.5 2" opacity="0.6" />
    </svg>
  )
}

// ── Stage 05: Hybrid Coarse-to-Fine Matcher (Dual-Vector Cosine + LPIPS) ──
export function SemanticMatcherIcon({ className = 'w-6 h-6' }) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
      aria-hidden="true"
    >
      {/* Dual interconnected precision orbital rings */}
      <circle cx="8.5" cy="12" r="5" fill="currentColor" fillOpacity="0.1" />
      <circle cx="15.5" cy="12" r="5" fill="currentColor" fillOpacity="0.1" />
      {/* Interlocking overlap nexus (0.7 face + 0.3 context) */}
      <path d="M12 8.5a5 5 0 0 1 0 7" strokeWidth="2.2" />
      <path d="M12 15.5a5 5 0 0 1 0-7" strokeWidth="2.2" />
      {/* Central cosine alignment target */}
      <circle cx="12" cy="12" r="1.25" fill="currentColor" />
      <line x1="4" y1="12" x2="6" y2="12" />
      <line x1="18" y1="12" x2="20" y2="12" />
    </svg>
  )
}

// ── Stage 06: Reference-Guided Face & Frame Restoration (Face-Affine + Real-ESRGAN) ──
export function RestorationIcon({ className = 'w-6 h-6' }) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
      aria-hidden="true"
    >
      {/* Primary super-resolution diamond brilliance star */}
      <path
        d="M12 2.5l2.2 6.3 6.3 2.2-6.3 2.2L12 19.5l-2.2-6.3-6.3-2.2 6.3-2.2L12 2.5z"
        fill="currentColor"
        fillOpacity="0.18"
      />
      {/* High-frequency micro-sparkle detail satellites */}
      <path d="M19 3.5l.8 1.8 1.8.8-1.8.8-.8 1.8-.8-1.8-1.8-.8 1.8-.8.8-1.8z" fill="currentColor" fillOpacity="0.3" />
      <path d="M5.5 16l.6 1.4 1.4.6-1.4.6-.6 1.4-.6-1.4-1.4-.6 1.4-.6.6-1.4z" fill="currentColor" fillOpacity="0.3" />
    </svg>
  )
}

// ── Stage 07: Batched RAFT Optical Flow Detail Propagation (torchvision RAFT-small) ──
export function OpticalFlowIcon({ className = 'w-6 h-6' }) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
      aria-hidden="true"
    >
      {/* Multi-layered dense sub-pixel motion vector streamlines */}
      <path d="M3 7c3.5-3 6.5-3 10 0s6.5 3 10 0" />
      <path d="M19.5 5.5l2.5 1.5-2.5 1.5" />

      <path d="M3 12c3.5-3 6.5-3 10 0s6.5 3 10 0" />
      <path d="M19.5 10.5l2.5 1.5-2.5 1.5" />

      <path d="M3 17c3.5-3 6.5-3 10 0s6.5 3 10 0" />
      <path d="M19.5 15.5l2.5 1.5-2.5 1.5" />
    </svg>
  )
}

// ── Stage 08: Lossless Audio Stream Multiplexing (FFmpeg Stream-Copy) ──
export function AudioMuxIcon({ className = 'w-6 h-6' }) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
      aria-hidden="true"
    >
      {/* Studio acoustic equalizer waveform frequency bands */}
      <line x1="3.5" y1="10" x2="3.5" y2="14" strokeWidth="2.2" />
      <line x1="7" y1="6.5" x2="7" y2="17.5" strokeWidth="2.2" />
      <line x1="10.5" y1="3.5" x2="10.5" y2="20.5" strokeWidth="2.2" />
      <line x1="14" y1="7" x2="14" y2="17" strokeWidth="2.2" />
      <line x1="17.5" y1="9.5" x2="17.5" y2="14.5" strokeWidth="2.2" />
      <line x1="21" y1="11" x2="21" y2="13" strokeWidth="2.2" />
      {/* Multiplex stream sync dot */}
      <circle cx="10.5" cy="12" r="1.5" fill="currentColor" />
    </svg>
  )
}

// ── Restoration Showcase Phase Icons ──
export function CassetteTapeIcon({ className = 'w-6 h-6' }) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
      aria-hidden="true"
    >
      <rect x="2.5" y="5" width="19" height="14" rx="2" fill="currentColor" fillOpacity="0.1" />
      <circle cx="7.5" cy="12" r="2.2" />
      <circle cx="16.5" cy="12" r="2.2" />
      <path d="M7.5 14.2h9" />
      <path d="M5.5 19l1.5-2.5h10l1.5 2.5" />
    </svg>
  )
}

export function AffineTargetIcon({ className = 'w-6 h-6' }) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
      aria-hidden="true"
    >
      <circle cx="12" cy="12" r="8" fill="currentColor" fillOpacity="0.1" />
      <circle cx="12" cy="12" r="3.5" />
      <circle cx="12" cy="12" r="1" fill="currentColor" />
      <line x1="12" y1="2" x2="12" y2="5" />
      <line x1="12" y1="19" x2="12" y2="22" />
      <line x1="2" y1="12" x2="5" y2="12" />
      <line x1="19" y1="12" x2="22" y2="12" />
    </svg>
  )
}

export function SuperResolutionRocketIcon({ className = 'w-6 h-6' }) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
      aria-hidden="true"
    >
      <path d="M4.5 16.5c-1.5 1.26-2 5-2 5s3.74-.5 5-2c.71-.84.7-2.13-.09-2.91a2.18 2.18 0 0 0-2.91-.09z" />
      <path d="M12 15l-3-3a22 22 0 0 1 2-3.95A12.88 12.88 0 0 1 22 2c0 2.72-.78 7.5-6 11a22.35 22.35 0 0 1-4 2z" />
      <circle cx="15.5" cy="8.5" r="1.5" fill="currentColor" fillOpacity="0.4" />
      <path d="M9 12H4.5s.55-3.03 2-4c1.62-1.08 5 0 5 0" />
      <path d="M12 15v4.5s3.03-.55 4-2c1.08-1.62 0-5 0-5" />
    </svg>
  )
}

/**
 * Universal StageIcon resolver component.
 * Maps any stage ID, emoji, or icon key to its dedicated SVG logo.
 */
export default function StageIcon({ id, stageId, icon, className = 'w-6 h-6' }) {
  const key = id || stageId || icon

  // Check by numeric stage ID
  if (key === 1 || key === '1' || key === '01' || key === '🎬' || key === 'video-repair') {
    return <VideoRepairIcon className={className} />
  }
  if (key === 2 || key === '2' || key === '02' || key === '🖼️' || key === 'frame-extract') {
    return <FrameExtractIcon className={className} />
  }
  if (key === 3 || key === '3' || key === '03' || key === '🧠' || key === 'clip-embed') {
    return <ClipEmbedIcon className={className} />
  }
  if (key === 4 || key === '4' || key === '04' || key === '👤' || key === 'face-embed') {
    return <FaceEmbedIcon className={className} />
  }
  if (key === 5 || key === '5' || key === '05' || key === '🔗' || key === 'semantic-matcher') {
    return <SemanticMatcherIcon className={className} />
  }
  if (key === 6 || key === '6' || key === '06' || key === '✨' || key === 'restoration') {
    return <RestorationIcon className={className} />
  }
  if (key === 7 || key === '7' || key === '07' || key === '🌊' || key === 'optical-flow') {
    return <OpticalFlowIcon className={className} />
  }
  if (key === 8 || key === '8' || key === '08' || key === '🎵' || key === 'audio-mux') {
    return <AudioMuxIcon className={className} />
  }

  // Restoration Showcase phase checks
  if (key === 'phase-1' || key === '📼') {
    return <CassetteTapeIcon className={className} />
  }
  if (key === 'phase-2' || key === '🎯') {
    return <AffineTargetIcon className={className} />
  }
  if (key === 'phase-3') {
    return <RestorationIcon className={className} />
  }
  if (key === 'phase-4' || key === '🚀') {
    return <SuperResolutionRocketIcon className={className} />
  }

  // Fallback to default restoration sparkle logo if unknown
  return <RestorationIcon className={className} />
}

