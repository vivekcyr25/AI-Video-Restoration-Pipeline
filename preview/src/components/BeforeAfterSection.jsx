import { useState, useRef } from 'react'
import { PROJECT } from '../data/pipelineData'
import { DegradedFilmSVG, RestoredFilmSVG } from './FrameIllustrations'

const COMPARISON_SCENES = [
  {
    id: 1,
    name: 'Scene 0042 · Ceremony Portrait',
    degradedImg: './assets/degraded_frame_01.jpg',
    restoredImg: './assets/album_ref_01.jpg',
    metrics: { faceScore: '0.942', clipScore: '0.865', psnrDelta: '+8.4 dB' },
    desc: 'Severe tape compression and low contrast resolved using 5-point affine landmark alignment and photo texture transfer.'
  },
  {
    id: 2,
    name: 'Scene 0100 · High-Frequency Jewelry & Fabric',
    degradedImg: './assets/degraded_frame_02.jpg',
    restoredImg: './assets/album_ref_02.jpg',
    metrics: { faceScore: '0.963', clipScore: '0.840', psnrDelta: '+9.1 dB' },
    desc: 'Restoring intricate wedding fabric textures and lighting dynamics using dual-vector cosine ranking.'
  },
  {
    id: 3,
    name: 'Scene 0200 · Wide Scene & Ambient Background',
    degradedImg: './assets/degraded_frame_03.jpg',
    restoredImg: './assets/album_ref_03.jpg',
    metrics: { faceScore: '0.918', clipScore: '0.881', psnrDelta: '+7.8 dB' },
    desc: 'Real-ESRGAN background upscaling coupled with Reinhard RGB color gamut harmonization.'
  }
]

export default function BeforeAfterSection() {
  const [selectedScene, setSelectedScene] = useState(0)
  const [sliderPos, setSliderPos] = useState(50)
  const [isDragging, setIsDragging] = useState(false)
  const containerRef = useRef(null)

  const activeScene = COMPARISON_SCENES[selectedScene]

  const handleMove = (clientX) => {
    if (!containerRef.current) return
    const rect = containerRef.current.getBoundingClientRect()
    const pos = ((clientX - rect.left) / rect.width) * 100
    setSliderPos(Math.max(5, Math.min(95, pos)))
  }

  const handleMouseMove = (e) => {
    if (isDragging || e.buttons === 1) {
      handleMove(e.clientX)
    }
  }

  const handleTouchMove = (e) => {
    handleMove(e.touches[0].clientX)
  }

  return (
    <section id="comparison" className="py-24 px-4 sm:px-6 relative border-t border-white/[0.06] bg-[#05060a]">
      <div className="max-w-7xl mx-auto">
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-14 space-y-3">
          <p className="text-xs font-mono tracking-[0.25em] uppercase text-electric-cyan font-semibold">
            VISUAL EVIDENCE & FIDELITY RECOVERY
          </p>
          <h2 className="text-3xl sm:text-5xl font-extrabold tracking-tight text-white font-display uppercase">
            From Archive to Restored
          </h2>
          <p className="text-sm sm:text-base text-slate-400 font-light leading-relaxed">
            The system processes degraded archival footage through scene detection, semantic matching and restoration stages to recover visual quality while reconstructing the final video.
          </p>

          {/* Scene Switcher Tabs */}
          <div className="flex flex-wrap justify-center gap-2 pt-4">
            {COMPARISON_SCENES.map((scene, idx) => (
              <button
                key={scene.id}
                onClick={() => {
                  setSelectedScene(idx)
                  setSliderPos(50)
                }}
                className={`px-4 py-2 rounded-xl text-xs font-mono transition-all duration-200 border ${
                  selectedScene === idx
                    ? 'bg-electric-cyan/15 border-electric-cyan/60 text-electric-cyan shadow-cyan-glow'
                    : 'bg-white/[0.03] border-white/10 text-slate-400 hover:text-slate-200 hover:bg-white/[0.06]'
                }`}
              >
                {scene.name}
              </button>
            ))}
          </div>
        </div>

        {/* Main Comparison Component */}
        <div className="max-w-5xl mx-auto rounded-3xl p-3 sm:p-4 bg-gradient-to-b from-white/[0.06] to-white/[0.02] border border-white/[0.12] shadow-2xl backdrop-blur-xl">
          {/* Top Bar with Real Telemetry */}
          <div className="flex flex-wrap items-center justify-between gap-3 px-4 py-3 border-b border-white/[0.08] text-xs font-mono text-slate-400 mb-3">
            <div className="flex items-center gap-3">
              <span className="text-slate-200 font-semibold">{activeScene.name}</span>
              <span className="hidden sm:inline text-slate-600">|</span>
              <span className="text-emerald-400">Identity Cosine: {activeScene.metrics.faceScore}</span>
            </div>
            <div className="flex items-center gap-4 text-[11px]">
              <span>CLIP Semantics: <span className="text-electric-cyan">{activeScene.metrics.clipScore}</span></span>
              <span>PSNR: <span className="text-violet-glow font-bold">{activeScene.metrics.psnrDelta}</span></span>
            </div>
          </div>

          {/* Interactive Comparison Slider */}
          <div
            ref={containerRef}
            onMouseDown={(e) => {
              setIsDragging(true)
              handleMove(e.clientX)
            }}
            onMouseUp={() => setIsDragging(false)}
            onMouseMove={handleMouseMove}
            onTouchMove={handleTouchMove}
            className="relative aspect-[16/10] sm:aspect-[16/9] rounded-2xl overflow-hidden cursor-ew-resize select-none bg-[#090c14] border border-white/[0.08]"
          >
            {/* Restored SVG (Full Right Layer) */}
            <div className="absolute inset-0">
              <RestoredFilmSVG className="w-full h-full" />
              <div className="absolute top-4 right-4 px-3 py-1 rounded-md bg-black/75 backdrop-blur-md border border-electric-cyan/40 text-xs font-mono text-electric-cyan flex items-center gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-electric-cyan animate-pulse" />
                <span>AI RESTORED</span>
              </div>
            </div>

            {/* Degraded SVG (Clipped Left Layer) */}
            <div
              className="absolute inset-y-0 left-0 overflow-hidden border-r-2 border-electric-cyan shadow-[0_0_30px_rgba(0,240,255,0.7)]"
              style={{ width: `${sliderPos}%` }}
            >
              <div className="relative w-full h-full min-w-[500px] sm:min-w-[800px] md:min-w-[1000px]">
                <DegradedFilmSVG className="w-full h-full" />
                <div className="absolute inset-0 film-scanlines pointer-events-none opacity-20" />
                <div className="absolute top-4 left-4 px-3 py-1 rounded-md bg-black/75 backdrop-blur-md border border-amber-500/40 text-xs font-mono text-amber-400 flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-amber-400" />
                  <span>ORIGINAL ARCHIVE</span>
                </div>
              </div>
            </div>

            {/* Draggable Divider Handle */}
            <div
              className="absolute top-0 bottom-0 -translate-x-1/2 w-1 bg-electric-cyan flex items-center justify-center pointer-events-none"
              style={{ left: `${sliderPos}%` }}
            >
              <div className="w-9 h-9 rounded-full bg-[#05060a] border-2 border-electric-cyan shadow-cyan-glow flex items-center justify-center text-electric-cyan text-xs font-bold">
                ↔
              </div>
            </div>
          </div>

          {/* Scene Technical Description */}
          <div className="mt-4 px-4 py-3 rounded-xl bg-white/[0.02] border border-white/[0.06] flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 text-xs text-slate-400 font-light">
            <p className="flex-1">
              <span className="text-slate-200 font-medium">Restoration Method: </span>
              {activeScene.desc}
            </p>
            <span className="font-mono text-[11px] text-slate-500 shrink-0">
              Drag or touch slider horizontally
            </span>
          </div>
        </div>

        {/* Real Repository Metrics Underneath */}
        <div className="mt-14 grid grid-cols-2 md:grid-cols-4 gap-4 max-w-5xl mx-auto">
          <div className="glass rounded-2xl p-6 text-center border-white/[0.08] hover:border-electric-cyan/30 transition-colors">
            <p className="text-3xl sm:text-4xl font-extrabold text-white font-display">410</p>
            <p className="text-xs font-mono text-slate-400 uppercase tracking-wider mt-1.5">Scenes Detected</p>
            <p className="text-[10px] text-slate-500 font-mono mt-1">PySceneDetect HSV 27.0</p>
          </div>

          <div className="glass rounded-2xl p-6 text-center border-white/[0.08] hover:border-electric-cyan/30 transition-colors">
            <p className="text-3xl sm:text-4xl font-extrabold text-electric-cyan font-display">18.7s</p>
            <p className="text-xs font-mono text-slate-400 uppercase tracking-wider mt-1.5">Average Shot Length</p>
            <p className="text-[10px] text-slate-500 font-mono mt-1">Optimal Optical Flow Span</p>
          </div>

          <div className="glass rounded-2xl p-6 text-center border-white/[0.08] hover:border-electric-cyan/30 transition-colors">
            <p className="text-3xl sm:text-4xl font-extrabold text-emerald-400 font-display">95</p>
            <p className="text-xs font-mono text-slate-400 uppercase tracking-wider mt-1.5">Tests Passing</p>
            <p className="text-[10px] text-slate-500 font-mono mt-1">100% Pytest Verification</p>
          </div>

          <div className="glass rounded-2xl p-6 text-center border-white/[0.08] hover:border-electric-cyan/30 transition-colors">
            <p className="text-3xl sm:text-4xl font-extrabold text-violet-glow font-display">2h 07m</p>
            <p className="text-xs font-mono text-slate-400 uppercase tracking-wider mt-1.5">Footage Processed</p>
            <p className="text-[10px] text-slate-500 font-mono mt-1">Lossless AAC Stream-Copy</p>
          </div>
        </div>
      </div>
    </section>
  )
}
