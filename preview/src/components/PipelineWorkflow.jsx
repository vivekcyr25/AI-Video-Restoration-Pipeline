import { useState } from 'react'
import { PIPELINE_STAGES } from '../data/pipelineData'

export default function PipelineWorkflow({ onStageClick }) {
  const [hoveredStage, setHoveredStage] = useState(null)
  const [activeTab, setActiveTab] = useState(1)

  const currentStage = PIPELINE_STAGES.find((s) => s.id === activeTab) || PIPELINE_STAGES[0]

  return (
    <section id="pipeline" className="py-24 px-4 sm:px-6 relative bg-[#040407] border-t border-white/[0.06]">
      {/* Background glow */}
      <div className="absolute top-1/3 right-10 w-96 h-96 bg-electric-blue/5 blur-[120px] pointer-events-none" />

      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center max-w-3xl mx-auto mb-16 space-y-3">
          <p className="text-xs font-mono tracking-[0.25em] uppercase text-electric-cyan font-semibold">
            STEP-BY-STEP RECONSTRUCTION FLOW
          </p>
          <h2 className="text-3xl sm:text-5xl font-extrabold tracking-tight text-white font-display uppercase">
            How The Pipeline Works
          </h2>
          <p className="text-sm sm:text-base text-slate-400 font-light leading-relaxed">
            An 8-stage modular architecture converting degraded legacy video footage into high-fidelity, temporally coherent master files.
          </p>
        </div>

        {/* Technical Flow Timeline & Node Grid */}
        <div className="grid lg:grid-cols-12 gap-8 items-start">
          {/* Left Column: Interactive Technical Timeline List (8 Stages) */}
          <div className="lg:col-span-7 space-y-3">
            {PIPELINE_STAGES.map((stage) => {
              const isActive = activeTab === stage.id
              const isHovered = hoveredStage === stage.id

              return (
                <div
                  key={stage.id}
                  onMouseEnter={() => {
                    setHoveredStage(stage.id)
                    setActiveTab(stage.id)
                  }}
                  onMouseLeave={() => setHoveredStage(null)}
                  onClick={() => onStageClick(stage.id)}
                  className={`group relative rounded-2xl p-5 border transition-all duration-300 cursor-pointer ${
                    isActive
                      ? 'bg-gradient-to-r from-white/[0.08] to-white/[0.02] border-electric-cyan/50 shadow-cyan-glow'
                      : 'bg-white/[0.02] border-white/[0.06] hover:border-white/[0.15] hover:bg-white/[0.04]'
                  }`}
                >
                  <div className="flex items-start gap-4">
                    {/* Stage Number & Icon */}
                    <div
                      className={`w-12 h-12 rounded-xl flex items-center justify-center text-xl shrink-0 transition-transform duration-300 border ${
                        isActive
                          ? 'bg-electric-cyan/20 border-electric-cyan text-white scale-105 shadow-inner'
                          : 'bg-white/[0.04] border-white/10 text-slate-300 group-hover:scale-105'
                      }`}
                    >
                      {stage.icon}
                    </div>

                    {/* Stage Details */}
                    <div className="min-w-0 flex-1">
                      <div className="flex items-center justify-between gap-2 mb-1">
                        <div className="flex items-center gap-2">
                          <span className="text-[11px] font-mono font-bold text-electric-cyan tracking-wider">
                            STAGE {stage.number}
                          </span>
                          <span className="text-[10px] px-2 py-0.5 rounded bg-white/[0.06] text-slate-400 font-mono">
                            {stage.tool}
                          </span>
                        </div>
                        <span className="text-[11px] font-mono text-slate-500 group-hover:text-electric-cyan transition-colors">
                          Inspect ↗
                        </span>
                      </div>

                      <h3 className="text-base sm:text-lg font-bold text-white font-display tracking-tight group-hover:text-electric-glow transition-colors">
                        {stage.name}
                      </h3>

                      <p className="text-xs sm:text-sm text-slate-400 font-light mt-1 leading-relaxed">
                        {stage.summary}
                      </p>

                      {/* Output Tag */}
                      <div className="mt-3 flex items-center gap-2 text-[11px] font-mono text-slate-500">
                        <span className="text-slate-600">→</span>
                        <span className="text-slate-300 truncate">{stage.outputs[0]}</span>
                      </div>
                    </div>
                  </div>

                  {/* Flow Connector Line */}
                  {stage.id < PIPELINE_STAGES.length && (
                    <div className="absolute -bottom-3 left-10 w-0.5 h-3 bg-white/10 group-hover:bg-electric-cyan/40 transition-colors z-10" />
                  )}
                </div>
              )
            })}
          </div>

          {/* Right Column: Deep-Dive Stage Preview Card */}
          <div className="lg:col-span-5 lg:sticky lg:top-28 space-y-4">
            <div className="rounded-3xl p-6 sm:p-7 bg-[#07090e] border border-white/[0.12] shadow-2xl backdrop-blur-2xl space-y-6">
              {/* Card Header */}
              <div className="flex items-center justify-between pb-4 border-b border-white/[0.08]">
                <div className="flex items-center gap-3">
                  <span className="text-2xl">{currentStage.icon}</span>
                  <div>
                    <span className="text-[10px] font-mono text-electric-cyan uppercase tracking-widest block font-semibold">
                      ACTIVE STAGE INSPECTION
                    </span>
                    <h4 className="text-lg font-bold text-white font-display">
                      {currentStage.name}
                    </h4>
                  </div>
                </div>
                <span className="px-2.5 py-1 rounded-full bg-electric-cyan/10 border border-electric-cyan/30 text-electric-cyan text-xs font-mono">
                  {currentStage.number} / 08
                </span>
              </div>

              {/* Description */}
              <div className="space-y-2">
                <span className="text-[10px] font-mono uppercase tracking-wider text-slate-500 block">
                  ALGORITHM OVERVIEW
                </span>
                <p className="text-xs sm:text-sm text-slate-300 font-light leading-relaxed">
                  {currentStage.description}
                </p>
              </div>

              {/* Technical Implementations */}
              <div className="p-4 rounded-2xl bg-white/[0.02] border border-white/[0.06] space-y-2">
                <span className="text-[10px] font-mono uppercase tracking-wider text-electric-cyan block font-semibold">
                  STAGE SPECIFICATIONS
                </span>
                <ul className="space-y-2">
                  {currentStage.techDetails.map((detail, idx) => (
                    <li key={idx} className="flex items-start gap-2 text-xs text-slate-300">
                      <span className="text-electric-cyan mt-0.5">▸</span>
                      <span>{detail}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Artifacts */}
              <div className="grid grid-cols-2 gap-3 pt-2">
                <div className="p-3 rounded-xl bg-white/[0.02] border border-white/[0.06]">
                  <span className="text-[9px] font-mono uppercase tracking-wider text-slate-500 block mb-1">
                    Primary Engine
                  </span>
                  <p className="text-xs font-mono text-slate-200 font-medium truncate">
                    {currentStage.tool}
                  </p>
                </div>
                <div className="p-3 rounded-xl bg-white/[0.02] border border-white/[0.06]">
                  <span className="text-[9px] font-mono uppercase tracking-wider text-emerald-500 block mb-1">
                    Key Output
                  </span>
                  <p className="text-xs font-mono text-emerald-400 font-medium truncate">
                    {currentStage.outputs[0]}
                  </p>
                </div>
              </div>

              {/* Click to open full modal */}
              <button
                onClick={() => onStageClick(currentStage.id)}
                className="w-full py-3 rounded-xl bg-white/[0.05] hover:bg-electric-cyan/20 border border-white/[0.1] hover:border-electric-cyan text-slate-200 hover:text-white text-xs font-mono font-medium transition-all flex items-center justify-center gap-2"
              >
                <span>View Complete Stage Parameters & Math</span>
                <span>→</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
