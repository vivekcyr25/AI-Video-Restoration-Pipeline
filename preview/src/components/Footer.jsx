import { PROJECT } from '../data/pipelineData'

export default function Footer() {
  return (
    <footer className="py-12 px-4 sm:px-6 bg-[#030305] border-t border-white/[0.06] text-xs text-slate-400 font-sans">
      <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-6">
        <div className="space-y-1 text-center sm:text-left">
          <p className="font-bold text-slate-100 font-display text-base tracking-wider uppercase">
            {PROJECT.author}
          </p>
          <p className="text-slate-400 text-xs tracking-widest uppercase font-sans">
            {PROJECT.role}
          </p>
        </div>

        <div className="flex items-center gap-8 text-xs tracking-widest uppercase font-medium">
          <a
            href={PROJECT.githubUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="text-slate-400 hover:text-electric-cyan transition-colors"
          >
            GitHub
          </a>
          <a
            href="https://linkedin.com"
            target="_blank"
            rel="noopener noreferrer"
            className="text-slate-400 hover:text-electric-cyan transition-colors"
          >
            LinkedIn
          </a>
          <a
            href="http://localhost:5173/"
            target="_blank"
            rel="noopener noreferrer"
            className="text-slate-400 hover:text-electric-cyan transition-colors"
          >
            Portfolio
          </a>
        </div>

        <div className="text-center sm:text-right text-xs text-slate-400 space-y-0.5 tracking-wider uppercase font-sans">
          <p>AI Video Restoration Pipeline · {PROJECT.license}</p>
          <p className="text-slate-500">Preserving Irreplaceable Historical Media</p>
        </div>
      </div>
    </footer>
  )
}
