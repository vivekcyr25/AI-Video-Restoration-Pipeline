import { PROJECT } from '../data/pipelineData'

export default function GithubCTA() {
  return (
    <section className="py-24 px-4 sm:px-6 relative bg-[#05060b] border-t border-white/[0.06] overflow-hidden">
      {/* Background glow */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[300px] bg-electric-cyan/10 blur-[140px] pointer-events-none" />

      <div className="max-w-4xl mx-auto text-center space-y-6 relative z-10">
        <p className="text-xs font-mono tracking-[0.25em] uppercase text-electric-cyan font-semibold">
          OPEN-SOURCE RESEARCH CODEBASE
        </p>

        <h2 className="text-4xl sm:text-6xl font-extrabold tracking-tight text-white font-display uppercase">
          Explore The Pipeline
        </h2>

        <p className="text-base sm:text-lg text-slate-300 max-w-xl mx-auto font-light leading-relaxed">
          Explore the complete implementation, architecture benchmarks, and engineering decisions behind the AI Video Restoration Pipeline.
        </p>

        <div className="flex flex-wrap items-center justify-center gap-4 pt-4">
          <a
            href={PROJECT.githubUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="px-8 py-4 rounded-xl bg-gradient-to-r from-electric-cyan to-electric-blue text-[#040407] font-semibold text-xs tracking-wider uppercase transition-all duration-200 hover:shadow-cyan-glow hover:scale-[1.02] active:scale-[0.98] flex items-center gap-2.5 font-display"
          >
            <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
              <path fillRule="evenodd" clipRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.53 1.032 1.53 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" />
            </svg>
            <span>View On GitHub</span>
          </a>

          <a
            href={`${PROJECT.githubUrl}#readme`}
            target="_blank"
            rel="noopener noreferrer"
            className="px-8 py-4 rounded-xl bg-white/[0.05] hover:bg-white/[0.1] border border-white/[0.12] hover:border-electric-cyan/40 text-slate-200 hover:text-white font-medium text-xs tracking-wider uppercase transition-all duration-200 font-display"
          >
            Explore Documentation
          </a>
        </div>
      </div>
    </section>
  )
}
