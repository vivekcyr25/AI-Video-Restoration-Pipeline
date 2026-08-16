import { TECH_STACK } from '../data/pipelineData'

export default function TechStackSection() {
  return (
    <section id="stack" className="py-24 px-4 sm:px-6 relative bg-[#040407] border-t border-white/[0.06]">
      <div className="max-w-6xl mx-auto">
        {/* Section Header */}
        <div className="text-center max-w-2xl mx-auto mb-16 space-y-3">
          <p className="text-xs font-mono tracking-[0.25em] uppercase text-electric-cyan font-semibold">
            ENGINEERING DEPENDENCIES
          </p>
          <h2 className="text-3xl sm:text-5xl font-extrabold tracking-tight text-white font-display uppercase">
            Technical Stack
          </h2>
          <p className="text-sm text-slate-400 font-light">
            Strictly verifying and employing modern computer vision, deep learning, and multimedia libraries.
          </p>
        </div>

        {/* 3 Discipline Categories Grid */}
        <div className="grid md:grid-cols-3 gap-6">
          {TECH_STACK.map((category) => (
            <div
              key={category.category}
              className="rounded-3xl p-6 sm:p-7 bg-[#07090e] border border-white/[0.08] hover:border-white/[0.16] transition-all duration-300 shadow-xl space-y-6 flex flex-col justify-between"
            >
              <div className="space-y-4">
                <div className="pb-3 border-b border-white/[0.08]">
                  <span className="text-[10px] font-mono text-electric-cyan uppercase tracking-widest block font-semibold">
                    DISCIPLINE
                  </span>
                  <h3 className="text-base font-bold text-white font-display mt-0.5">
                    {category.category}
                  </h3>
                </div>

                <div className="space-y-3">
                  {category.items.map((item) => (
                    <div
                      key={item.name}
                      className="p-3.5 rounded-xl bg-white/[0.02] border border-white/[0.04] hover:border-electric-cyan/30 hover:bg-white/[0.04] transition-all group"
                    >
                      <p className="text-xs sm:text-sm font-semibold font-mono text-slate-200 group-hover:text-electric-cyan transition-colors">
                        {item.name}
                      </p>
                      <p className="text-xs text-slate-400 font-light mt-1 leading-snug">
                        {item.role}
                      </p>
                    </div>
                  ))}
                </div>
              </div>

              <div className="pt-3 border-t border-white/[0.04] flex items-center justify-between text-[10px] font-mono text-slate-500">
                <span>Verified in requirements.txt</span>
                <span className="text-emerald-400">● Active</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
