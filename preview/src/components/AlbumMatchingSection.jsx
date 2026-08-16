import { useState } from 'react'
import { DegradedFrameSVG, RestoredFrameSVG } from './FrameIllustrations'

const MATCH_PAIRS = [
  {
    id: 1,
    title: 'Match Pair #01 · Ceremony Altar Shot',
    videoFrame: './assets/degraded_frame_01.jpg',
    albumPhoto: './assets/album_ref_01.jpg',
    videoTime: '00:12:45 (Scene 42)',
    photoMeta: '20260704_161237.jpg · 4000x3000 Raw',
    faceScore: 0.942,
    clipScore: 0.865,
    hybridScore: 0.919,
    rationale: 'ArcFace biometric embedding locks onto the bride & groom facial structure despite tape motion blur; OpenCLIP confirms church altar lighting and floral backdrop.'
  },
  {
    id: 2,
    title: 'Match Pair #02 · Bridal Portrait & Jewelry',
    videoFrame: './assets/degraded_frame_02.jpg',
    albumPhoto: './assets/album_ref_02.jpg',
    videoTime: '00:34:10 (Scene 100)',
    photoMeta: '20260704_161648.jpg · 4000x3000 Raw',
    faceScore: 0.963,
    clipScore: 0.840,
    hybridScore: 0.926,
    rationale: '5-point landmark detection precisely aligns eye and lip positions, enabling high-frequency texture transfer of skin pores and fabric embroidery.'
  },
  {
    id: 3,
    title: 'Match Pair #03 · Wide Reception & Lighting',
    videoFrame: './assets/degraded_frame_03.jpg',
    albumPhoto: './assets/album_ref_03.jpg',
    videoTime: '01:05:22 (Scene 200)',
    photoMeta: '20260704_162730.jpg · 4000x3000 Raw',
    faceScore: 0.918,
    clipScore: 0.881,
    hybridScore: 0.907,
    rationale: 'Semantic vector matching identifies wide hall ambient illumination, guiding Reinhard color transfer to neutralize tape color degradation.'
  }
]

export default function AlbumMatchingSection() {
  const [activePairIdx, setActivePairIdx] = useState(0)
  const activePair = MATCH_PAIRS[activePairIdx]

  return (
    <section id="matching" className="py-24 px-4 sm:px-6 relative bg-[#05060b] border-t border-white/[0.06] overflow-hidden">
      {/* Glow */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[350px] bg-gradient-to-r from-violet-subtle/10 via-electric-cyan/10 to-transparent blur-[140px] pointer-events-none" />

      <div className="max-w-7xl mx-auto relative z-10">
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-16 space-y-3">
          <p className="text-xs font-mono tracking-[0.25em] uppercase text-violet-glow font-semibold">
            THE CORE DIFFERENTIATOR
          </p>
          <h2 className="text-3xl sm:text-5xl font-extrabold tracking-tight text-white font-display uppercase leading-tight">
            When The Album Remembers<br />
            <span className="bg-gradient-to-r from-white via-slate-200 to-violet-glow bg-clip-text text-transparent">
              What The Video Forgot
            </span>
          </h2>
          <p className="text-sm sm:text-base text-slate-400 font-light leading-relaxed">
            The system generates 512-dimensional visual embeddings for video frames and album photographs, searching for semantically identical visual references that serve as immutable ground-truth anchors.
          </p>

          {/* Pair Selectors */}
          <div className="flex flex-wrap justify-center gap-2 pt-4">
            {MATCH_PAIRS.map((pair, idx) => (
              <button
                key={pair.id}
                onClick={() => setActivePairIdx(idx)}
                className={`px-4 py-2 rounded-xl text-xs font-mono transition-all border ${
                  activePairIdx === idx
                    ? 'bg-violet-subtle/20 border-violet-subtle text-violet-glow shadow-violet-glow'
                    : 'bg-white/[0.03] border-white/10 text-slate-400 hover:text-white hover:bg-white/[0.06]'
                }`}
              >
                {pair.title}
              </button>
            ))}
          </div>
        </div>

        {/* Visual Match Showcase (Video Frame <---> Matched Album Photo) */}
        <div className="max-w-5xl mx-auto rounded-3xl p-6 sm:p-8 bg-gradient-to-b from-white/[0.05] to-white/[0.01] border border-white/[0.12] shadow-2xl backdrop-blur-2xl">
          <div className="grid md:grid-cols-11 gap-6 items-center">
            {/* Left: Degraded Video Frame */}
            <div className="md:col-span-5 space-y-3">
              <div className="flex items-center justify-between text-xs font-mono">
                <span className="text-amber-400 font-semibold flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-amber-400 animate-pulse" />
                  OLD VIDEO FRAME
                </span>
                <span className="text-slate-500">{activePair.videoTime}</span>
              </div>

              <div className="relative aspect-[4/3] rounded-2xl overflow-hidden border border-amber-500/30 bg-[#090b12] group">
                <DegradedFrameSVG className="w-full h-full" />
                <div className="absolute inset-0 film-scanlines pointer-events-none opacity-20" />
              </div>
            </div>

            {/* Center: Dual Vector Similarity Computation */}
            <div className="md:col-span-1 flex flex-col items-center justify-center gap-3 py-4">
              <div className="hidden md:block w-px h-12 bg-gradient-to-b from-transparent via-violet-subtle to-transparent" />
              <div className="w-10 h-10 rounded-full bg-violet-subtle/20 border border-violet-subtle text-violet-glow flex items-center justify-center text-xs font-mono shadow-violet-glow animate-pulse">
                ⇄
              </div>
              <div className="hidden md:block w-px h-12 bg-gradient-to-b from-violet-subtle via-transparent to-transparent" />
            </div>

            {/* Right: High-Resolution Album Photo */}
            <div className="md:col-span-5 space-y-3">
              <div className="flex items-center justify-between text-xs font-mono">
                <span className="text-electric-cyan font-semibold flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-electric-cyan animate-pulse" />
                  MATCHED ALBUM PHOTO
                </span>
                <span className="text-slate-500 truncate max-w-[180px]">{activePair.photoMeta}</span>
              </div>

              <div className="relative aspect-[4/3] rounded-2xl overflow-hidden border border-electric-cyan/40 bg-[#090b12] group">
                <RestoredFrameSVG className="w-full h-full" />
              </div>
            </div>
          </div>

          {/* Similarity Calculation Matrix */}
          <div className="mt-8 pt-6 border-t border-white/[0.08] grid sm:grid-cols-3 gap-4">
            <div className="p-4 rounded-2xl bg-white/[0.02] border border-white/[0.06] text-center">
              <span className="text-[10px] font-mono uppercase tracking-wider text-slate-400 block mb-1">
                ArcFace Biometric (70% Weight)
              </span>
              <p className="text-2xl font-bold font-mono text-electric-cyan">
                {activePair.faceScore.toFixed(3)}
              </p>
              <span className="text-[10px] text-slate-500 font-mono">Pose-Invariant Identity Cosine</span>
            </div>

            <div className="p-4 rounded-2xl bg-white/[0.02] border border-white/[0.06] text-center">
              <span className="text-[10px] font-mono uppercase tracking-wider text-slate-400 block mb-1">
                OpenCLIP Semantics (30% Weight)
              </span>
              <p className="text-2xl font-bold font-mono text-violet-glow">
                {activePair.clipScore.toFixed(3)}
              </p>
              <span className="text-[10px] text-slate-500 font-mono">ViT-B-32 Scene Composition</span>
            </div>

            <div className="p-4 rounded-2xl bg-gradient-to-br from-electric-cyan/10 to-violet-subtle/10 border border-electric-cyan/30 text-center">
              <span className="text-[10px] font-mono uppercase tracking-wider text-white font-semibold block mb-1">
                Composite Match Score
              </span>
              <p className="text-2xl font-bold font-mono text-emerald-400">
                {activePair.hybridScore.toFixed(3)}
              </p>
              <span className="text-[10px] text-slate-400 font-mono">0.70 × Face + 0.30 × CLIP</span>
            </div>
          </div>

          {/* Rationale */}
          <p className="mt-5 text-xs text-slate-300 font-light leading-relaxed px-2 text-center max-w-2xl mx-auto">
            <span className="text-white font-medium">Why Reference Anchoring Matters: </span>
            {activePair.rationale}
          </p>
        </div>
      </div>
    </section>
  )
}
