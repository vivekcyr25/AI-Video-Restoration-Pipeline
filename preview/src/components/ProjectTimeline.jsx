import { PROJECT_TIMELINE } from '../data/pipelineData'

export default function ProjectTimeline() {
  return (
    <section className="py-24 px-4 sm:px-6 relative bg-[#040407] border-t border-white/[0.06]">
      <div className="max-w-6xl mx-auto">
        {/* Section Header */}
        <div className="text-center max-w-2xl mx-auto mb-16 space-y-3">
          <p className="text-xs font-mono tracking-[0.25em] uppercase text-electric-cyan font-semibold">
            PIPELINE EVOLUTION
          </p>
          <h2 className="text-3xl sm:text-5xl font-extrabold tracking-tight text-white font-display uppercase">
            The Engineering Journey
          </h2>
          <p className="text-sm text-slate-400 font-light">
            From initial research concepts to an accelerated, hardware-optimized production system.
          </p>
        </div>

        {/* Timeline Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {PROJECT_TIMELINE.map((item) => (
            <div
              key={item.phase}
              className="p-6 rounded-3xl bg-[#07090e] border border-white/[0.08] hover:border-electric-cyan/40 transition-all duration-300 shadow-xl space-y-3 relative group"
            >
              <div className="flex items-center justify-between pb-3 border-b border-white/[0.06]">
                <span className="text-xs font-mono font-bold text-electric-cyan">
                  PHASE {item.phase}
                </span>
                <span className="w-2 h-2 rounded-full bg-electric-cyan group-hover:scale-125 transition-transform" />
              </div>

              <h3 className="text-base font-bold text-white font-display">
                {item.title}
              </h3>

              <p className="text-xs text-slate-400 font-light leading-relaxed">
                {item.desc}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
