export default function ProjectStory() {
  return (
    <section id="story" className="py-24 px-4 sm:px-6 relative bg-[#05060a] border-t border-white/[0.06]">
      <div className="max-w-4xl mx-auto">
        {/* Section Header */}
        <div className="text-center mb-12 space-y-2">
          <p className="text-xs font-mono tracking-[0.25em] uppercase text-electric-cyan font-semibold">
            ENGINEERING PHILOSOPHY
          </p>
          <h2 className="text-3xl sm:text-5xl font-extrabold tracking-tight text-white font-display uppercase">
            Why I Built This
          </h2>
        </div>

        {/* Story Narrative Box */}
        <div className="rounded-3xl p-8 sm:p-12 bg-gradient-to-b from-white/[0.04] to-white/[0.01] border border-white/[0.08] shadow-2xl backdrop-blur-xl space-y-6 text-slate-300 font-light leading-relaxed text-sm sm:text-base">
          <p>
            Old VHS tapes and early digital video recordings lose fidelity over time. Crucial family memories—such as wedding ceremonies, gatherings, and milestone archives—become marred by heavy macroblocking, color washout, and tape noise.
          </p>

          <div className="p-5 rounded-2xl bg-white/[0.02] border-l-2 border-electric-cyan space-y-2 italic text-slate-200">
            <p>
              "Standard generative AI restoration models frequently 'hallucinate' facial features—inventing entirely new facial structures and eye geometries that do not belong to the real individuals."
            </p>
          </div>

          <p>
            I realized that while the video footage was heavily degraded, high-resolution still photographs taken during the exact same event still existed in wedding albums at pristine 12-to-24 megapixel clarity.
          </p>

          <p>
            This insight led to the creation of the <strong>AI Video Restoration Pipeline</strong>: rather than asking a generative model to guess what a face looked like, the pipeline uses <strong>OpenCLIP semantic embeddings</strong> and <strong>InsightFace ArcFace biometric features</strong> to retrieve genuine photograph anchors. It then performs sub-pixel 5-point affine alignment, transfers real skin and iris textures, and propagates the detail coherently across time using <strong>RAFT optical flow</strong>.
          </p>

          <div className="pt-4 flex items-center justify-between border-t border-white/[0.06] text-xs font-mono text-slate-400">
            <span>Built by Vivek Sharma</span>
            <span className="text-electric-cyan">Preserving Irreplaceable Media</span>
          </div>
        </div>
      </div>
    </section>
  )
}
