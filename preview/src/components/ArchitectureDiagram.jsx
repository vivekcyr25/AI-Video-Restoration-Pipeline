import { useState } from 'react'

export default function ArchitectureDiagram() {
  const [activeNode, setActiveNode] = useState(null)

  const nodes = [
    { id: 'input', label: 'Legacy Video & Album Photos', sub: 'MP4 (VFR) + JPEG Still Anchors', type: 'source' },
    { id: 's1', label: 'Stage 1: Container Repair & CFR', sub: 'FFmpeg CFR 25.0 + PySceneDetect (410 Scenes)', type: 'process' },
    { id: 's2', label: 'Stage 2: Midpoint Frame Extraction', sub: 'FFmpeg -q:v 2 Lossless Anchor Extraction', type: 'process' },
    { id: 's34', label: 'Stages 3 & 4: Dual Vector Embeddings', sub: 'OpenCLIP ViT-B-32 (Scene) + ArcFace (512-D Biometrics)', type: 'embed' },
    { id: 's5', label: 'Stage 5: Hybrid Coarse-to-Fine Matcher', sub: '0.70 Face + 0.30 CLIP + Color / LPIPS Re-ranking', type: 'match' },
    { id: 's6', label: 'Stage 6: Face-Affine v2 & Real-ESRGAN', sub: '5-Point Landmark Texture Transfer + Background Upscaling', type: 'restore' },
    { id: 's7', label: 'Stage 7: Batched RAFT-small Optical Flow', sub: 'Sub-pixel motion warping across 180k frames + Lab de-flicker', type: 'flow' },
    { id: 's8', label: 'Stage 8: Byte-Copy Audio Muxing', sub: 'FFmpeg AAC direct stream-copy sync', type: 'mux' },
    { id: 'output', label: 'Restored Master Asset', sub: '1080p 25fps Master MP4 with Synchronized Lossless Audio', type: 'sink' },
  ]

  return (
    <section id="architecture" className="py-24 px-4 sm:px-6 relative bg-[#05060b] border-t border-white/[0.06]">
      <div className="max-w-6xl mx-auto">
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-16 space-y-3">
          <p className="text-xs font-mono tracking-[0.25em] uppercase text-electric-cyan font-semibold">
            DATA PIPELINE TOPOLOGY
          </p>
          <h2 className="text-3xl sm:text-5xl font-extrabold tracking-tight text-white font-display uppercase">
            System Architecture
          </h2>
          <p className="text-sm sm:text-base text-slate-400 font-light leading-relaxed">
            Data flow diagram illustrating sequential model lifecycles and tensor transformations from ingest to final audio multiplexing.
          </p>
        </div>

        {/* Architecture Flow Canvas */}
        <div className="p-8 sm:p-12 rounded-3xl bg-gradient-to-b from-white/[0.04] to-white/[0.01] border border-white/[0.1] shadow-2xl backdrop-blur-xl relative overflow-hidden">
          {/* Subtle grid background */}
          <div className="absolute inset-0 tech-grid-bg opacity-20 pointer-events-none" />

          {/* Node Progression Flow */}
          <div className="relative z-10 space-y-6">
            {/* Top Row: Input Source */}
            <div className="flex justify-center">
              <div className="w-full max-w-md p-4 rounded-2xl bg-amber-500/10 border border-amber-500/30 text-center space-y-1">
                <span className="text-[10px] font-mono text-amber-400 uppercase tracking-widest block font-semibold">
                  INGEST ARTIFACTS
                </span>
                <p className="text-sm font-bold text-white font-display">
                  Raw Legacy Video (VFR) & High-Resolution Album Photos
                </p>
                <p className="text-xs text-slate-400 font-mono">
                  Input: 2h 07m MP4 + 65 High-Res Photographs
                </p>
              </div>
            </div>

            {/* Downward Connector */}
            <div className="flex justify-center">
              <div className="w-0.5 h-6 bg-gradient-to-b from-amber-500/60 to-electric-cyan" />
            </div>

            {/* Middle Stages Sequence */}
            <div className="grid md:grid-cols-2 gap-4">
              {/* Left Column: Video Preparation & Embeddings */}
              <div className="space-y-4 p-5 rounded-2xl bg-white/[0.02] border border-white/[0.06]">
                <span className="text-[10px] font-mono text-electric-cyan uppercase tracking-widest block font-semibold">
                  DECOMPOSITION & VECTORIZATION
                </span>

                <div className="p-3.5 rounded-xl bg-white/[0.03] border border-white/[0.08] space-y-1">
                  <div className="flex items-center justify-between text-xs font-mono">
                    <span className="text-slate-200 font-semibold">Stage 1: Container Repair & CFR</span>
                    <span className="text-emerald-400">25.0 fps</span>
                  </div>
                  <p className="text-xs text-slate-400 font-light">
                    PySceneDetect detects 410 shot cuts using HSV histogram delta threshold 27.0.
                  </p>
                </div>

                <div className="p-3.5 rounded-xl bg-white/[0.03] border border-white/[0.08] space-y-1">
                  <div className="flex items-center justify-between text-xs font-mono">
                    <span className="text-slate-200 font-semibold">Stage 2: Frame Extraction</span>
                    <span className="text-slate-400">410 JPEGs</span>
                  </div>
                  <p className="text-xs text-slate-400 font-light">
                    Near-lossless FFmpeg midpoint seek captures representative anchors per scene.
                  </p>
                </div>

                <div className="p-3.5 rounded-xl bg-white/[0.03] border border-white/[0.08] space-y-1">
                  <div className="flex items-center justify-between text-xs font-mono">
                    <span className="text-slate-200 font-semibold">Stages 3 & 4: Dual Embeddings</span>
                    <span className="text-electric-cyan font-bold">[N, 512]</span>
                  </div>
                  <p className="text-xs text-slate-400 font-light">
                    OpenCLIP ViT-B-32 (Scene) + InsightFace ArcFace (Identity) in FP16 inference.
                  </p>
                </div>
              </div>

              {/* Right Column: Matching, Restoration & Propagation */}
              <div className="space-y-4 p-5 rounded-2xl bg-white/[0.02] border border-white/[0.06]">
                <span className="text-[10px] font-mono text-violet-glow uppercase tracking-widest block font-semibold">
                  SYNTHESIS & TEMPORAL WARPING
                </span>

                <div className="p-3.5 rounded-xl bg-white/[0.03] border border-white/[0.08] space-y-1">
                  <div className="flex items-center justify-between text-xs font-mono">
                    <span className="text-slate-200 font-semibold">Stage 5: Hybrid Matcher</span>
                    <span className="text-violet-glow">0.7F + 0.3C</span>
                  </div>
                  <p className="text-xs text-slate-400 font-light">
                    Pairs 410 video scenes with corresponding high-resolution ground truth photos.
                  </p>
                </div>

                <div className="p-3.5 rounded-xl bg-white/[0.03] border border-white/[0.08] space-y-1">
                  <div className="flex items-center justify-between text-xs font-mono">
                    <span className="text-slate-200 font-semibold">Stage 6: Face Affine & Real-ESRGAN</span>
                    <span className="text-emerald-400">410 Restored</span>
                  </div>
                  <p className="text-xs text-slate-400 font-light">
                    5-point landmark texture transfer + background super-resolution upscaling.
                  </p>
                </div>

                <div className="p-3.5 rounded-xl bg-white/[0.03] border border-white/[0.08] space-y-1">
                  <div className="flex items-center justify-between text-xs font-mono">
                    <span className="text-slate-200 font-semibold">Stage 7: RAFT-small Optical Flow</span>
                    <span className="text-sky-400">6x Accelerated</span>
                  </div>
                  <p className="text-xs text-slate-400 font-light">
                    Batched GPU propagation of keyframe deltas + rolling Lab de-flicker filter.
                  </p>
                </div>
              </div>
            </div>

            {/* Downward Connector */}
            <div className="flex justify-center">
              <div className="w-0.5 h-6 bg-gradient-to-b from-electric-cyan to-emerald-400" />
            </div>

            {/* Bottom Row: Output Master */}
            <div className="flex justify-center">
              <div className="w-full max-w-md p-4 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 text-center space-y-1 shadow-[0_0_30px_rgba(52,211,153,0.15)]">
                <div className="flex items-center justify-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                  <span className="text-[10px] font-mono text-emerald-400 uppercase tracking-widest font-semibold">
                    STAGE 8 · MASTER OUTPUT
                  </span>
                </div>
                <p className="text-sm font-bold text-white font-display">
                  Restored Master Video (1080p CFR + Lossless AAC Sync)
                </p>
                <p className="text-xs text-slate-400 font-mono">
                  Final Output: output/Restored_Wedding_final.mp4
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
