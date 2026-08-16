import { useState, useEffect } from 'react'
import { PROJECT } from '../data/pipelineData'
import { DegradedFilmSVG, RestoredFilmSVG } from './FrameIllustrations'

export default function HeroSection() {
  const [sliderPos, setSliderPos] = useState(52)
  const [isHovered, setIsHovered] = useState(false)
  const [tick, setTick] = useState(0)
  const [restoringIdx, setRestoringIdx] = useState(0)

  const RESTORING_QUOTES = [
    'Restoring lost faces from 1994 VHS tape...',
    'Restoring wedding ceremony — Scene 042 of 410...',
    'Restoring color gamut via Reinhard transfer...',
    'Restoring 512-D identity embeddings...',
    'Restoring high-frequency texture detail...',
    'Restoring archival footage — 360p → 1080p...',
  ]

  useEffect(() => {
    const timer = setInterval(() => {
      setTick((t) => (t + 1) % 1000)
    }, 1000)
    return () => clearInterval(timer)
  }, [])

  useEffect(() => {
    const timer = setInterval(() => {
      setRestoringIdx(i => (i + 1) % RESTORING_QUOTES.length)
    }, 2800)
    return () => clearInterval(timer)
  }, [])

  return (
    <section className="relative min-h-[92vh] flex items-center justify-center pt-24 pb-16 px-4 sm:px-6 overflow-hidden">
      {/* Background subtle technical grid */}
      <div className="absolute inset-0 tech-grid-bg opacity-30 pointer-events-none" />
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[350px] bg-gradient-to-tr from-electric-cyan/10 via-violet-subtle/10 to-transparent blur-[120px] pointer-events-none" />

      <div className="max-w-7xl mx-auto w-full grid lg:grid-cols-12 gap-12 lg:gap-8 items-center relative z-10">
        {/* Left Column: Editorial Typography */}
        <div className="lg:col-span-7 space-y-6 text-left">
          {/* Status Indicator */}
          <div className="inline-flex items-center gap-2.5 px-3.5 py-1.5 rounded-full bg-white/[0.04] border border-white/[0.1] text-xs font-mono text-slate-300 shadow-sm backdrop-blur-md">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse shadow-[0_0_10px_#34d399]" />
            <span className="tracking-wide">PIPELINE ONLINE</span>
            <span className="text-slate-600">/</span>
            <span className="text-electric-cyan font-medium">RESEARCH-GRADE RESTORATION</span>
          </div>

          {/* Primary Headline */}
          <div className="space-y-2">
            <p className="text-xs sm:text-sm font-mono tracking-[0.28em] uppercase text-electric-cyan">
              COMPUTER VISION × SEMANTIC ANCHORING
            </p>
            <h1 className="heading-gold text-4xl sm:text-6xl xl:text-7xl font-extrabold tracking-tight text-white font-display uppercase leading-[1.05]">
              AI Video<br />
              <span className="bg-gradient-to-r from-white via-slate-200 to-electric-cyan bg-clip-text text-transparent">
                Restoration
              </span><br />
              Pipeline
            </h1>

            {/* Scrolling 'Restoring...' ticker */}
            <div className="overflow-hidden h-6 mt-1">
              <p
                key={restoringIdx}
                className="text-xs font-mono text-slate-500 tracking-wider"
                style={{
                  animation: 'restoring-in 0.5s ease forwards',
                }}
              >
                <span className="text-electric-cyan/60 mr-1">▶</span>
                {RESTORING_QUOTES[restoringIdx]}
              </p>
            </div>
          </div>

          {/* Supporting Text */}
          <p className="text-base sm:text-lg text-slate-300/80 max-w-xl font-light leading-relaxed">
            Recovering lost visual details from degraded archival footage using computer vision, semantic matching and reference-guided AI restoration.
          </p>

          {/* CTA Buttons */}
          <div className="flex flex-wrap items-center gap-4 pt-2">
            <a
              href="#pipeline"
              className="px-6 py-3.5 rounded-xl bg-gradient-to-r from-electric-cyan to-electric-blue text-[#040407] font-semibold text-xs tracking-wider uppercase transition-all duration-200 hover:shadow-cyan-glow hover:scale-[1.02] active:scale-[0.98] flex items-center gap-2.5 font-display"
            >
              <span>Explore Pipeline</span>
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
              </svg>
            </a>

            <a
              href={PROJECT.githubUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="px-6 py-3.5 rounded-xl bg-white/[0.05] hover:bg-white/[0.1] border border-white/[0.12] hover:border-electric-cyan/40 text-slate-200 hover:text-white font-medium text-xs tracking-wider uppercase transition-all duration-200 flex items-center gap-2 font-display"
            >
              <svg className="w-4 h-4 text-slate-300" viewBox="0 0 24 24" fill="currentColor">
                <path fillRule="evenodd" clipRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.53 1.032 1.53 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" />
              </svg>
              <span>View Source</span>
            </a>
          </div>

          {/* Live Telemetry Pill Row */}
          <div className="pt-4 grid grid-cols-3 gap-3 max-w-lg border-t border-white/[0.07]">
            <div className="space-y-0.5">
              <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wider block">Shot Detector</span>
              <span className="text-sm font-semibold text-slate-200 font-mono">410 Scenes</span>
            </div>
            <div className="space-y-0.5">
              <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wider block">Vector Latents</span>
              <span className="text-sm font-semibold text-slate-200 font-mono">512-D Dual</span>
            </div>
            <div className="space-y-0.5">
              <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wider block">VRAM Envelope</span>
              <span className="text-sm font-semibold text-electric-cyan font-mono">4 GB Cap</span>
            </div>
          </div>
        </div>

        {/* Right Column: Large Cinematic Video / Frame Interactive Preview */}
        <div className="lg:col-span-5">
          <div className="relative rounded-2xl p-2 bg-gradient-to-b from-white/[0.08] to-white/[0.02] border border-white/[0.12] shadow-2xl backdrop-blur-2xl">
            {/* Top Frame Status Header */}
            <div className="flex items-center justify-between px-3 py-2 text-[11px] font-mono text-slate-400 border-b border-white/[0.06] mb-2">
              <div className="flex items-center gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-electric-cyan animate-ping" />
                <span className="text-slate-300">SCENE_0042.RAW</span>
              </div>
              <div className="flex items-center gap-3">
                <span>1080p @ 25 CFR</span>
                <span className="text-emerald-400 font-semibold">REC ●</span>
              </div>
            </div>

            {/* Split Screen Media Container */}
            <div
              className="relative aspect-[4/3] rounded-xl overflow-hidden cursor-ew-resize select-none border border-white/[0.08] bg-[#0c0d14]"
              onMouseMove={(e) => {
                const rect = e.currentTarget.getBoundingClientRect()
                const pos = ((e.clientX - rect.left) / rect.width) * 100
                setSliderPos(Math.max(10, Math.min(90, pos)))
              }}
              onTouchMove={(e) => {
                const touch = e.touches[0]
                const rect = e.currentTarget.getBoundingClientRect()
                const pos = ((touch.clientX - rect.left) / rect.width) * 100
                setSliderPos(Math.max(10, Math.min(90, pos)))
              }}
              onMouseEnter={() => setIsHovered(true)}
              onMouseLeave={() => setIsHovered(false)}
            >
              {/* Layer 1: Restored Frame (Full canvas underneath) */}
              <div className="absolute inset-0 bg-[#09101d] overflow-hidden">
                <RestoredFilmSVG className="w-full h-full" />
                <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-black/20" />
                {/* Restored Target Badge */}
                <div className="absolute bottom-3 right-3 px-2.5 py-1 rounded bg-black/70 backdrop-blur-md border border-electric-cyan/40 text-[10px] font-mono text-electric-cyan">
                  AI RESTORED · 1080p
                </div>
              </div>

              {/* Layer 2: Degraded Frame (Clipped to sliderPos width) */}
              <div
                className="absolute inset-y-0 left-0 overflow-hidden border-r border-electric-cyan shadow-[0_0_20px_rgba(0,240,255,0.6)]"
                style={{ width: `${sliderPos}%` }}
              >
                <div className="relative w-full h-full min-w-[320px] sm:min-w-[480px]">
                  <DegradedFilmSVG className="w-full h-full" />
                  <div className="absolute inset-0 film-scanlines pointer-events-none opacity-30" />
                  {/* Degraded Badge */}
                  <div className="absolute bottom-3 left-3 px-2.5 py-1 rounded bg-black/70 backdrop-blur-md border border-amber-500/40 text-[10px] font-mono text-amber-400">
                    DEGRADED ARCHIVE · 360p
                  </div>
                </div>
              </div>

              {/* Central Divider Handle */}
              <div
                className="absolute top-0 bottom-0 -translate-x-1/2 w-0.5 bg-electric-cyan flex items-center justify-center pointer-events-none"
                style={{ left: `${sliderPos}%` }}
              >
                <div className="w-7 h-7 rounded-full bg-[#07090e] border-2 border-electric-cyan shadow-cyan-glow flex items-center justify-center text-electric-cyan text-[10px]">
                  ↔
                </div>
              </div>

              {/* Tech Crosshair Overlays */}
              <div className="absolute top-4 left-4 tech-crosshair pointer-events-none" />
              <div className="absolute top-4 right-4 tech-crosshair pointer-events-none" />
            </div>

            {/* Bottom Interactive Prompt */}
            <div className="mt-2.5 px-3 py-1.5 flex items-center justify-between text-[10px] font-mono text-slate-400">
              <span className="flex items-center gap-1.5">
                <span className="text-electric-cyan">◀ Drag slider ▶</span> to inspect detail recovery
              </span>
              <span className="text-slate-500">
                LPIPS: <span className="text-emerald-400">0.082</span>
              </span>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
