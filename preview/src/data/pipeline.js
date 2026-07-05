export const PROJECT = {
  name: 'AI Video Restoration Pipeline',
  tagline: 'Recover irreplaceable memories from degraded legacy video',
  question:
    'Can AI recover visual quality in a degraded video by leveraging high-quality still photos taken at the same event?',
  stats: {
    scenes: 411,
    duration: '2h 7m',
    frames: '411 representative frames',
    embeddingDim: 512,
    clipWeight: 0.3,
    faceWeight: 0.7,
  },
}

export const INTRO_BEATS = [
  {
    id: 'problem-1',
    eyebrow: 'The Problem',
    headline: 'Some memories only exist\non degraded tape.',
    sub: 'Legacy wedding footage — compressed, artifacted, fading with every playback.',
    tone: 'vintage',
  },
  {
    id: 'problem-2',
    eyebrow: null,
    headline: 'Compression stole\nthe sharpness.',
    sub: 'Fine detail lost. Colors washed out. Blocky AAC artifacts across every frame.',
    tone: 'vintage',
  },
  {
    id: 'problem-3',
    eyebrow: null,
    headline: "You can't\nre-shoot a wedding.",
    sub: 'The moment is gone. The original raw footage is gone. What remains is irreplaceable — but broken.',
    tone: 'vintage',
  },
  {
    id: 'insight',
    eyebrow: 'The Insight',
    headline: 'But the photographer\nwas there.',
    sub: 'High-quality album photos captured the same moments — same faces, same scenes — at full resolution.',
    tone: 'transition',
  },
  {
    id: 'solution',
    eyebrow: 'The Solution',
    headline: 'A lighting-invariant\nrestoration algorithm.',
    sub: 'Match degraded video frames to album references using CLIP semantics + face identity. Propagate recovery across every frame.',
    tone: 'modern',
  },
]

export const TECH_STACK = [
  { name: 'FFmpeg 8.x', role: 'Video processing & audio mux' },
  { name: 'OpenCLIP ViT-B-32', role: '512-dim semantic embeddings' },
  { name: 'InsightFace buffalo_l', role: 'Face identity matching' },
  { name: 'PySceneDetect', role: 'Scene boundary detection' },
  { name: 'OpenCV Farnebäck', role: 'Optical flow propagation' },
  { name: 'PyTorch 2.0+', role: 'Deep learning backend' },
]

export const STAGES = [
  {
    id: 1,
    label: 'Scene Detect',
    short: 'Scenes',
    tool: 'PySceneDetect',
    icon: '🎬',
    color: 'from-amber-600/40 to-orange-800/20',
    description:
      'Analyzes inter-frame histogram differences to divide the video into shots. Reduces billions of frame comparisons to ~411 representative scenes.',
    detail:
      'ContentDetector flags scene boundaries when HSV histogram delta exceeds threshold 27.0. Each scene gets one midpoint frame for AI processing.',
    output: 'scenes.csv',
  },
  {
    id: 2,
    label: 'Frame Extract',
    short: 'Frames',
    tool: 'FFmpeg',
    icon: '🖼️',
    color: 'from-yellow-700/30 to-amber-900/20',
    description:
      'Extracts one representative JPEG per scene — the midpoint frame — avoiding motion blur at cut points.',
    detail:
      'FFmpeg selects the settled composition of each shot at near-lossless quality (-q:v 2). These frames become anchors for restoration and optical flow.',
    output: 'Representative_Frames/',
  },
  {
    id: 3,
    label: 'CLIP Embed',
    short: 'CLIP',
    tool: 'OpenCLIP ViT-B-32',
    icon: '🧠',
    color: 'from-teal-600/30 to-cyan-900/20',
    description:
      'Encodes album photos and video frames into 512-dimensional semantic vectors capturing scene, objects, and composition.',
    detail:
      'LAION-2B pretrained ViT-B-32. L2-normalized embeddings enable efficient cosine similarity via matrix multiplication.',
    output: 'models/*.npy',
  },
  {
    id: 4,
    label: 'Face Match',
    short: 'Face',
    tool: 'InsightFace ArcFace',
    icon: '👤',
    color: 'from-blue-600/30 to-indigo-900/20',
    description:
      'RetinaFace detects faces; ArcFace ResNet-50 extracts pose-invariant 512-dim identity embeddings for wedding subjects.',
    detail:
      'Largest face per image selected as primary subject. Face embeddings provide lighting-invariant identity matching CLIP alone cannot guarantee.',
    output: 'models/*_face_*.npy',
  },
  {
    id: 5,
    label: 'Hybrid Match',
    short: 'Match',
    tool: 'Advanced Matcher',
    icon: '🔗',
    color: 'from-violet-600/30 to-purple-900/20',
    description:
      'Ranks album photos per frame: final_score = 0.70 × face + 0.30 × CLIP. Wedding videos are identity-centric.',
    detail:
      'Batch cosine similarity across 411 frames × album photos. Top-K candidates logged with CLIPScore, FaceScore, and FinalScore to CSV.',
    output: 'advanced_matches.csv',
  },
  {
    id: 6,
    label: 'Restore',
    short: 'Restore',
    tool: 'Face-Affine v2',
    icon: '✨',
    color: 'from-emerald-600/30 to-green-900/20',
    description:
      'Face-guided affine alignment + high-frequency detail transfer from matched album photos. CLAHE, bilateral filter, unsharp mask.',
    detail:
      'Confidence maps from Canny edges, Sobel gradients, and texture similarity. Detail gain clamped to prevent over-restoration. SIFT v1 fallback.',
    output: 'Restored_Frames/',
  },
  {
    id: 7,
    label: 'Flow Propagate',
    short: 'Flow',
    tool: 'Farnebäck Optical Flow',
    icon: '🌊',
    color: 'from-sky-600/30 to-blue-900/20',
    description:
      'Propagates restoration delta from representative frames to every frame in the scene — temporal coherence without per-frame AI.',
    detail:
      'Delta decomposed into low-freq + detail bands. Flow-warped with confidence from residual. Temporal smoothing prevents flicker within scenes.',
    output: 'Restored_Wedding_silent.mp4',
  },
  {
    id: 8,
    label: 'Audio Merge',
    short: 'Audio',
    tool: 'FFmpeg Stream Copy',
    icon: '🎵',
    color: 'from-slate-500/30 to-zinc-800/20',
    description:
      'Original AAC audio stream copied byte-for-byte into the reconstructed video. Zero re-encoding, ~30 seconds.',
    detail:
      'Stream copy preserves quality. -shortest flag handles any length discrepancy between video and audio tracks.',
    output: 'Restored_Wedding_final.mp4',
  },
]

export const FEATURES = [
  'Scene-aware processing — one frame per shot, not every frame',
  'Dual embedding matching — CLIP semantics + face identity',
  'Confidence-weighted blending — no over-restoration',
  'Optical flow propagation — temporally coherent output',
  'Lossless audio preservation — original AAC stream copied',
]
