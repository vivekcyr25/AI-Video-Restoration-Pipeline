/* ============================================================
   FrameIllustrations.jsx
   All named exports — SVG-only, no real photos
   ============================================================ */

/** Degraded archival frame: tape noise, block artifacts, amber tones */
export function DegradedFrameSVG({ className = '' }) {
  return (
    <svg viewBox="0 0 480 360" xmlns="http://www.w3.org/2000/svg" className={className}>
      <defs>
        <linearGradient id="dfbg" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor="#2a1a0e" />
          <stop offset="50%" stopColor="#3d2b1f" />
          <stop offset="100%" stopColor="#1a100a" />
        </linearGradient>
      </defs>
      <rect width="480" height="360" fill="url(#dfbg)" />
      {/* Block artifacts */}
      <rect x="80" y="80" width="48" height="36" fill="#52300f" opacity="0.7" />
      <rect x="200" y="110" width="64" height="48" fill="#3a2010" opacity="0.6" />
      <rect x="320" y="70" width="44" height="32" fill="#60380f" opacity="0.75" />
      {/* Person silhouettes */}
      <ellipse cx="160" cy="270" rx="22" ry="70" fill="#0e0906" opacity="0.72" />
      <ellipse cx="160" cy="190" rx="20" ry="20" fill="#0e0906" opacity="0.68" />
      <ellipse cx="240" cy="265" rx="26" ry="80" fill="#0b0705" opacity="0.78" />
      <ellipse cx="240" cy="178" rx="23" ry="23" fill="#0b0705" opacity="0.72" />
      <ellipse cx="320" cy="275" rx="20" ry="65" fill="#120a05" opacity="0.68" />
      <ellipse cx="320" cy="202" rx="18" ry="18" fill="#120a05" opacity="0.65" />
      {/* CRT scanlines */}
      {Array.from({ length: 90 }).map((_, i) => (
        <line key={i} x1="0" y1={i * 4} x2="480" y2={i * 4} stroke="#000" strokeWidth="1.5" opacity="0.15" />
      ))}
      {/* Tape damage streaks */}
      <rect x="0" y="112" width="480" height="2" fill="#fff" opacity="0.04" />
      <rect x="0" y="215" width="380" height="1" fill="#fff" opacity="0.03" />
      <rect x="40" y="290" width="440" height="2" fill="#fff" opacity="0.05" />
      {/* Sepia overlay */}
      <rect width="480" height="360" fill="#c47830" opacity="0.06" />
      {/* Vignette */}
      <radialGradient id="dfv" cx="50%" cy="50%" r="70%">
        <stop offset="0%" stopColor="#000" stopOpacity="0" />
        <stop offset="100%" stopColor="#000" stopOpacity="0.6" />
      </radialGradient>
      <rect width="480" height="360" fill="url(#dfv)" />
      {/* Detection box */}
      <rect x="140" y="155" width="200" height="160" fill="none" stroke="#d97706" strokeWidth="1.5" strokeDasharray="6,4" opacity="0.7" />
      <text x="148" y="150" fill="#d97706" fontSize="10" fontFamily="monospace" opacity="0.9">RetinaFace: 0.97</text>
      {/* Landmarks */}
      <circle cx="183" cy="178" r="2.5" fill="#d97706" opacity="0.8" />
      <circle cx="217" cy="178" r="2.5" fill="#d97706" opacity="0.8" />
      <circle cx="200" cy="198" r="2" fill="#d97706" opacity="0.75" />
      <circle cx="188" cy="218" r="2" fill="#d97706" opacity="0.75" />
      <circle cx="212" cy="218" r="2" fill="#d97706" opacity="0.75" />
      {/* Bottom badge */}
      <rect x="8" y="338" width="176" height="16" rx="3" fill="#000" opacity="0.75" />
      <text x="14" y="349" fill="#d97706" fontSize="9" fontFamily="monospace">512-D Latent Vector Encoded</text>
      {/* Top telemetry */}
      <rect x="320" y="8" width="152" height="14" rx="3" fill="#000" opacity="0.65" />
      <text x="326" y="18" fill="#d97706" fontSize="8.5" fontFamily="monospace">DEGRADED · 360p · TAPE</text>
    </svg>
  )
}

/** Restored high-res frame: sharp, color-corrected, cyan overlays */
export function RestoredFrameSVG({ className = '' }) {
  return (
    <svg viewBox="0 0 480 360" xmlns="http://www.w3.org/2000/svg" className={className}>
      <defs>
        <linearGradient id="rfbg" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor="#0c1a2e" />
          <stop offset="30%" stopColor="#1a3a5c" />
          <stop offset="60%" stopColor="#2d5a40" />
          <stop offset="100%" stopColor="#8b5e1a" />
        </linearGradient>
        <radialGradient id="rflight" cx="50%" cy="40%" r="55%">
          <stop offset="0%" stopColor="#fff" stopOpacity="0.07" />
          <stop offset="100%" stopColor="#000" stopOpacity="0" />
        </radialGradient>
      </defs>
      <rect width="480" height="360" fill="url(#rfbg)" />
      <rect width="480" height="360" fill="url(#rflight)" />
      {/* Sharp silhouettes */}
      <ellipse cx="160" cy="270" rx="24" ry="72" fill="#071510" opacity="0.88" />
      <ellipse cx="160" cy="190" rx="21" ry="21" fill="#071510" opacity="0.85" />
      <ellipse cx="240" cy="265" rx="28" ry="82" fill="#050f0a" opacity="0.9" />
      <ellipse cx="240" cy="178" rx="24" ry="24" fill="#050f0a" opacity="0.87" />
      <ellipse cx="320" cy="275" rx="22" ry="66" fill="#071510" opacity="0.82" />
      <ellipse cx="320" cy="204" rx="19" ry="19" fill="#071510" opacity="0.8" />
      {/* Skin tone warm */}
      <ellipse cx="160" cy="190" rx="13" ry="13" fill="#d4a070" opacity="0.35" />
      <ellipse cx="240" cy="178" rx="15" ry="15" fill="#d4a070" opacity="0.32" />
      <ellipse cx="320" cy="204" rx="12" ry="12" fill="#d4a070" opacity="0.3" />
      {/* Bokeh dots */}
      <circle cx="60" cy="60" r="5" fill="#fff" opacity="0.04" />
      <circle cx="420" cy="70" r="7" fill="#fff" opacity="0.03" />
      <circle cx="400" cy="290" r="5" fill="#fff" opacity="0.04" />
      {/* Detection box */}
      <rect x="140" y="155" width="200" height="160" fill="none" stroke="#00f0ff" strokeWidth="1.5" strokeDasharray="6,4" opacity="0.75" />
      <text x="148" y="150" fill="#00f0ff" fontSize="10" fontFamily="monospace" opacity="0.9">5-Pt Aligned · ArcFace 0.942</text>
      {/* Landmarks */}
      <circle cx="183" cy="178" r="2.5" fill="#00f0ff" opacity="0.9" />
      <circle cx="217" cy="178" r="2.5" fill="#00f0ff" opacity="0.9" />
      <circle cx="200" cy="198" r="2" fill="#00f0ff" opacity="0.85" />
      <circle cx="188" cy="218" r="2" fill="#00f0ff" opacity="0.85" />
      <circle cx="212" cy="218" r="2" fill="#00f0ff" opacity="0.85" />
      {/* Bottom badges */}
      <rect x="292" y="338" width="180" height="16" rx="3" fill="#000" opacity="0.75" />
      <text x="298" y="349" fill="#00f0ff" fontSize="9" fontFamily="monospace">Ground Truth Texture Anchor</text>
      <text x="10" y="349" fill="#34d399" fontSize="9" fontFamily="monospace" opacity="0.85">Real-ESRGAN · FP16 · 1080p</text>
      {/* Top telemetry */}
      <rect x="8" y="8" width="160" height="14" rx="3" fill="#000" opacity="0.65" />
      <text x="14" y="18" fill="#00f0ff" fontSize="8.5" fontFamily="monospace">AI RESTORED · 1080p · SHARP</text>
    </svg>
  )
}

/** Degraded film for hero / before-after slider (landscape 4:3) */
export function DegradedFilmSVG({ className = '' }) {
  return (
    <svg viewBox="0 0 640 480" xmlns="http://www.w3.org/2000/svg" className={className}>
      <defs>
        <linearGradient id="dfsbg" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor="#3d2b1f" />
          <stop offset="60%" stopColor="#2a1810" />
          <stop offset="100%" stopColor="#1a0d06" />
        </linearGradient>
      </defs>
      <rect width="640" height="480" fill="url(#dfsbg)" />
      <rect width="640" height="480" fill="#c4782a" opacity="0.06" />
      {/* Block artifacts */}
      <rect x="80" y="120" width="64" height="48" fill="#52300f" opacity="0.65" />
      <rect x="280" y="150" width="80" height="60" fill="#3a2010" opacity="0.58" />
      <rect x="440" y="100" width="60" height="44" fill="#60380f" opacity="0.7" />
      {/* Figures */}
      <ellipse cx="200" cy="340" rx="28" ry="90" fill="#0e0906" opacity="0.72" />
      <ellipse cx="200" cy="240" rx="26" ry="26" fill="#0e0906" opacity="0.68" />
      <ellipse cx="340" cy="330" rx="34" ry="100" fill="#0b0705" opacity="0.78" />
      <ellipse cx="340" cy="222" rx="30" ry="30" fill="#0b0705" opacity="0.73" />
      <ellipse cx="480" cy="345" rx="26" ry="82" fill="#120a05" opacity="0.67" />
      <ellipse cx="480" cy="254" rx="24" ry="24" fill="#120a05" opacity="0.63" />
      {/* Scanlines */}
      {Array.from({ length: 120 }).map((_, i) => (
        <line key={i} x1="0" y1={i * 4} x2="640" y2={i * 4} stroke="#000" strokeWidth="1.5" opacity="0.14" />
      ))}
      {/* Tape streaks */}
      <rect x="0" y="155" width="640" height="2" fill="#fff" opacity="0.04" />
      <rect x="0" y="290" width="540" height="1" fill="#fff" opacity="0.03" />
      <rect x="50" y="390" width="590" height="2" fill="#fff" opacity="0.04" />
      {/* Vignette */}
      <radialGradient id="dfsv" cx="50%" cy="50%" r="70%">
        <stop offset="0%" stopColor="#000" stopOpacity="0" />
        <stop offset="100%" stopColor="#000" stopOpacity="0.55" />
      </radialGradient>
      <rect width="640" height="480" fill="url(#dfsv)" />
      <text x="10" y="468" fill="#d97706" fontSize="11" fontFamily="monospace" opacity="0.85">DEGRADED · TAPE NOISE · 360p</text>
    </svg>
  )
}

/** Restored film for hero / before-after slider (landscape 4:3) */
export function RestoredFilmSVG({ className = '' }) {
  return (
    <svg viewBox="0 0 640 480" xmlns="http://www.w3.org/2000/svg" className={className}>
      <defs>
        <linearGradient id="rfsbg" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor="#0c1929" />
          <stop offset="35%" stopColor="#1a4a6e" />
          <stop offset="65%" stopColor="#2d6a4f" />
          <stop offset="100%" stopColor="#8b6914" />
        </linearGradient>
        <radialGradient id="rfslight" cx="50%" cy="40%" r="55%">
          <stop offset="0%" stopColor="#fff" stopOpacity="0.07" />
          <stop offset="100%" stopColor="#000" stopOpacity="0" />
        </radialGradient>
      </defs>
      <rect width="640" height="480" fill="url(#rfsbg)" />
      <rect width="640" height="480" fill="url(#rfslight)" />
      {/* Sharp silhouettes */}
      <ellipse cx="200" cy="340" rx="30" ry="92" fill="#071510" opacity="0.88" />
      <ellipse cx="200" cy="240" rx="28" ry="28" fill="#071510" opacity="0.85" />
      <ellipse cx="340" cy="330" rx="36" ry="102" fill="#050f0a" opacity="0.9" />
      <ellipse cx="340" cy="220" rx="32" ry="32" fill="#050f0a" opacity="0.87" />
      <ellipse cx="480" cy="345" rx="28" ry="84" fill="#071510" opacity="0.82" />
      <ellipse cx="480" cy="254" rx="26" ry="26" fill="#071510" opacity="0.8" />
      {/* Skin */}
      <ellipse cx="200" cy="240" rx="16" ry="16" fill="#d4a070" opacity="0.35" />
      <ellipse cx="340" cy="220" rx="19" ry="19" fill="#d4a070" opacity="0.32" />
      <ellipse cx="480" cy="254" rx="15" ry="15" fill="#d4a070" opacity="0.3" />
      {/* Bokeh */}
      <circle cx="80" cy="80" r="6" fill="#fff" opacity="0.04" />
      <circle cx="560" cy="90" r="8" fill="#fff" opacity="0.03" />
      <circle cx="540" cy="380" r="6" fill="#fff" opacity="0.04" />
      <text x="10" y="468" fill="#00f0ff" fontSize="11" fontFamily="monospace" opacity="0.88">AI RESTORED · REAL-ESRGAN · 1080p</text>
    </svg>
  )
}
