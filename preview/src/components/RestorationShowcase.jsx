import { useState } from 'react'

const RESTORATION_PHASES = [
  {
    step: '01',
    name: 'Degraded Frame Ingest',
    tool: 'FFmpeg & OpenCV',
    desc: 'Input anchor frame suffers from blocky compression artifacts, tape noise, and faded RGB saturation.',
    metrics: 'Resolution: 360p / Sub-optimal SNR',
    icon: '📼',
    color: 'from-amber-600/30 to-amber-900/10'
  },
  {
    step: '02',
    name: '5-Point Affine Warp & Color Gamut Align',
    tool: 'InsightFace & Reinhard Transfer',
    desc: 'Locks facial landmark points (eyes, nose, mouth) to the matched high-resolution album photo. Harmonizes color distribution in Lab color space.',
    metrics: 'Landmark Error: < 0.8px Sub-pixel',
    icon: '🎯',
    color: 'from-blue-600/30 to-indigo-900/10'
  },
  {
    step: '03',
    name: 'High-Frequency Texture Transfer',
    tool: 'Frequency Band Decomposition',
    desc: 'Separates low-frequency luminance from high-frequency facial textures (pores, hair, iris reflections). Transfers sharp details using soft confidence masks.',
    metrics: 'Confidence Weight: 0.85 Soft-Alpha',
    icon: '✨',
    color: 'from-emerald-600/30 to-teal-900/10'
  },
  {
    step: '04',
    name: 'Real-ESRGAN Background Upscale',
    tool: 'Real-ESRGAN & PyTorch FP16',
    desc: 'Upscales architectural background, clothing drapery, and ambient scenery while maintaining strict identity preservation on foreground subjects.',
    metrics: 'Final Target: 1080p Master Frame',
    icon: '🚀',
    color: 'from-violet-600/30 to-purple-900/10'
  }
]

export default function RestorationShowcase() {
  const [activeStep, setActiveStep] = useState(0)

  return (
    <section id="restoration" className="py-24 px-4 sm:px-6 relative bg-[#040407] border-t border-white/[0.06]">
      <div className="max-w-7xl mx-auto">
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-16 space-y-3">
          <p className="text-xs font-mono tracking-[0.25em] uppercase text-emerald-400 font-semibold">
            DEEP LEARNING DETAIL SYNTHESIS
          </p>
          <h2 className="text-3xl sm:text-5xl font-extrabold tracking-tight text-white font-display uppercase">
            Restoring The Details
          </h2>
          <p className="text-sm sm:text-base text-slate-400 font-light leading-relaxed">
            Multi-stage frequency decomposition and affine landmark guidance that restores micro-detail without generative hallucination.
          </p>
        </div>

        {/* 4-Step Technical Workflow Grid */}
        <div className="grid md:grid-cols-4 gap-4 mb-12">
          {RESTORATION_PHASES.map((phase, idx) => (
            <div
              key={phase.step}
              onClick={() => setActiveStep(idx)}
              className={`rounded-2xl p-6 border transition-all duration-300 cursor-pointer space-y-3 ${
                activeStep === idx
                  ? 'bg-gradient-to-b from-white/[0.08] to-white/[0.02] border-emerald-400/50 shadow-[0_0_30px_rgba(52,211,153,0.15)] scale-[1.02]'
                  : 'bg-white/[0.02] border-white/[0.06] hover:border-white/[0.12] hover:bg-white/[0.04]'
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="text-xs font-mono font-bold text-emerald-400">
                  STEP {phase.step}
                </span>
                <span className="text-xl">{phase.icon}</span>
              </div>

              <h3 className="text-base font-bold text-white font-display">
                {phase.name}
              </h3>

              <p className="text-xs font-mono text-slate-400">
                {phase.tool}
              </p>

              <p className="text-xs text-slate-400 font-light leading-relaxed pt-1">
                {phase.desc}
              </p>

              <div className="pt-2 border-t border-white/[0.06] text-[10px] font-mono text-emerald-300">
                {phase.metrics}
              </div>
            </div>
          ))}
        </div>

        {/* Technology Highlights Row */}
        <div className="max-w-4xl mx-auto rounded-2xl p-6 bg-white/[0.02] border border-white/[0.08] backdrop-blur-xl">
          <div className="text-center mb-4">
            <span className="text-[10px] font-mono text-slate-400 uppercase tracking-widest">
              DEPLOYED COMPUTER VISION LIBRARIES
            </span>
          </div>
          <div className="flex flex-wrap items-center justify-center gap-6 sm:gap-10 text-xs font-mono text-slate-300">
            <div className="flex items-center gap-2 hover:text-emerald-400 transition-colors">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
              <span>Real-ESRGAN (x4plus)</span>
            </div>
            <div className="flex items-center gap-2 hover:text-emerald-400 transition-colors">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
              <span>OpenCV 4.x (Affine & CLAHE)</span>
            </div>
            <div className="flex items-center gap-2 hover:text-emerald-400 transition-colors">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
              <span>PyTorch 2.x (CUDA FP16)</span>
            </div>
            <div className="flex items-center gap-2 hover:text-emerald-400 transition-colors">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
              <span>InsightFace (ArcFace & RetinaFace)</span>
            </div>
            <div className="flex items-center gap-2 hover:text-emerald-400 transition-colors">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
              <span>ONNX Runtime (CUDA Engine)</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
