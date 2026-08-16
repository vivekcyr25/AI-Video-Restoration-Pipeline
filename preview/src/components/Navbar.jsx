import { useState, useEffect } from 'react'
import { PROJECT } from '../data/pipelineData'

export default function Navbar({ onOpenStage }) {
  const [scrolled, setScrolled] = useState(false)
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 30)
    }
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  const navLinks = [
    { label: 'Comparison', href: '#comparison' },
    { label: 'Pipeline', href: '#pipeline' },
    { label: 'Album Match', href: '#matching' },
    { label: 'Restoration', href: '#restoration' },
    { label: 'Architecture', href: '#architecture' },
    { label: 'Terminal', href: '#terminal' },
    { label: 'Constraints', href: '#constraints' },
    { label: 'Tests', href: '#testing' },
  ]

  return (
    <header
      className={`fixed top-0 inset-x-0 z-50 transition-all duration-300 ${
        scrolled
          ? 'bg-[#040407]/85 backdrop-blur-xl border-b border-white/[0.08] shadow-lg shadow-black/40 py-3'
          : 'bg-transparent border-b border-transparent py-5'
      }`}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 flex items-center justify-between">
        {/* Brand / Logo */}
        <a href="#" className="flex items-center gap-3 group">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-electric-cyan/20 to-violet-subtle/20 border border-electric-cyan/40 flex items-center justify-center text-electric-cyan text-sm font-mono font-bold shadow-cyan-glow group-hover:scale-105 transition-transform">
            AI
          </div>
          <div className="flex flex-col">
            <span className="text-xs sm:text-sm font-semibold tracking-wider text-slate-100 uppercase font-display group-hover:text-electric-cyan transition-colors">
              Video Restoration
            </span>
            <span className="text-[10px] font-mono text-slate-400">
              Pipeline Architecture
            </span>
          </div>
        </a>



        {/* Desktop Nav Links */}
        <nav className="hidden md:flex items-center gap-6 text-xs font-medium text-slate-400">
          {navLinks.map((link) => (
            <a
              key={link.label}
              href={link.href}
              className="hover:text-slate-100 hover:text-electric-cyan transition-colors py-1 relative group"
            >
              {link.label}
              <span className="absolute bottom-0 left-0 w-0 h-0.5 bg-electric-cyan transition-all duration-300 group-hover:w-full" />
            </a>
          ))}
        </nav>

        {/* Action button */}
        <div className="flex items-center gap-3">
          <a
            href={PROJECT.githubUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 px-3.5 py-1.5 rounded-lg bg-white/[0.06] hover:bg-white/[0.12] border border-white/[0.12] hover:border-electric-cyan/40 text-xs font-medium text-slate-200 hover:text-white transition-all shadow-sm group"
          >
            <svg
              className="w-4 h-4 text-slate-300 group-hover:text-electric-cyan transition-colors"
              viewBox="0 0 24 24"
              fill="currentColor"
            >
              <path
                fillRule="evenodd"
                clipRule="evenodd"
                d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.53 1.032 1.53 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"
              />
            </svg>
            <span>GitHub</span>
          </a>

          {/* Mobile menu toggle */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="md:hidden p-2 rounded-lg bg-white/[0.05] border border-white/10 text-slate-300"
            aria-label="Toggle menu"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              {mobileMenuOpen ? (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              ) : (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              )}
            </svg>
          </button>
        </div>
      </div>

      {/* Mobile dropdown */}
      {mobileMenuOpen && (
        <div className="md:hidden bg-[#07090e]/95 backdrop-blur-2xl border-b border-white/10 px-4 py-4 mt-2 space-y-2">
          {navLinks.map((link) => (
            <a
              key={link.label}
              href={link.href}
              onClick={() => setMobileMenuOpen(false)}
              className="block py-2 px-3 rounded-lg text-sm text-slate-300 hover:text-electric-cyan hover:bg-white/[0.04]"
            >
              {link.label}
            </a>
          ))}

        </div>
      )}
    </header>
  )
}
