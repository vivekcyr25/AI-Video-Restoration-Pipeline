import { PROJECT } from '../data/pipelineData'

export default function Footer() {
  return (
    <footer className="relative z-20 py-14 px-4 sm:px-6 bg-[#040407] border-t border-white/10 text-slate-300 font-sans">
      <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-6">
        {/* Left: Author & Role */}
        <div className="space-y-1.5 text-center sm:text-left">
          <p className="font-bold text-white font-display text-lg tracking-wider uppercase">
            {PROJECT.author}
          </p>
          <p className="text-slate-300 text-xs tracking-widest uppercase font-medium">
            {PROJECT.role}
          </p>
        </div>

        {/* Center: Quick Links */}
        <div className="flex items-center gap-8 text-xs tracking-widest uppercase font-semibold">
          <a
            href={PROJECT.githubUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="text-slate-300 hover:text-electric-cyan transition-colors"
          >
            GitHub
          </a>
          <a
            href="https://linkedin.com"
            target="_blank"
            rel="noopener noreferrer"
            className="text-slate-300 hover:text-electric-cyan transition-colors"
          >
            LinkedIn
          </a>
          <a
            href="http://localhost:5173/"
            target="_blank"
            rel="noopener noreferrer"
            className="text-slate-300 hover:text-electric-cyan transition-colors"
          >
            Portfolio
          </a>
        </div>

        {/* Right: Project License & Purpose */}
        <div className="text-center sm:text-right text-xs text-slate-300 space-y-1 tracking-wider uppercase font-sans">
          <p className="text-slate-200 font-medium">AI Video Restoration Pipeline · {PROJECT.license}</p>
          <p className="text-slate-400 text-[11px]">Preserving Irreplaceable Historical Media</p>
        </div>
      </div>
    </footer>
  )
}
