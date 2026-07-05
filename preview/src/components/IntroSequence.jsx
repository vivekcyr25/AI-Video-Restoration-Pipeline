import { useRef, useEffect } from 'react'
import { INTRO_BEATS } from '../data/pipeline'
import { useScrollProgress, getBeatStyles, getIntroExitOpacity } from '../hooks/useScroll'
import InteractiveInvariant from './InteractiveInvariant'

function ScrollHint({ visible }) {
  return (
    <div
      className="absolute bottom-10 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2 transition-opacity duration-500 pointer-events-none"
      style={{ opacity: visible ? 1 : 0 }}
    >
      <span className="text-[11px] text-white/40 tracking-widest uppercase">Scroll to explore</span>
      <div className="w-5 h-8 rounded-full border border-white/20 flex justify-center pt-1.5">
        <div className="w-1 h-1.5 rounded-full bg-white/50 animate-bounce" />
      </div>
    </div>
  )
}

export default function IntroSequence({ onProgress }) {
  const containerRef = useRef(null)
  const progress = useScrollProgress(containerRef)
  const exitOpacity = getIntroExitOpacity(progress)

  useEffect(() => {
    onProgress?.(progress)
  }, [progress, onProgress])

  const lastBeatVisible = progress > 0.75

  return (
    <section
      ref={containerRef}
      className="relative z-20"
      style={{ height: `${INTRO_BEATS.length * 100}vh` }}
    >
      <div
        className="sticky top-0 h-screen flex items-center justify-center overflow-hidden bg-[#050508]"
        style={{ opacity: exitOpacity }}
      >
        <div className="relative w-full max-w-4xl mx-auto px-6 h-full max-h-[720px]">
          {INTRO_BEATS.map((beat, i) => {
            const { visible, ...cssStyle } = getBeatStyles(progress, i, INTRO_BEATS.length)
            const isSolution = beat.id === 'solution'
            const isVintage = beat.tone === 'vintage'

            return (
              <div
                key={beat.id}
                className="absolute inset-0 flex flex-col items-center justify-center px-2"
                style={cssStyle}
                aria-hidden={!visible}
              >
                {beat.eyebrow && (
                  <p
                    className={`text-xs font-medium tracking-[0.25em] uppercase mb-5 ${
                      isSolution ? 'text-cyber-glow' : isVintage ? 'text-amber-500/70' : 'text-white/50'
                    }`}
                  >
                    {beat.eyebrow}
                  </p>
                )}

                {beat.interactive ? (
                  <InteractiveInvariant />
                ) : (
                  <h1
                    className={`text-4xl sm:text-5xl md:text-6xl font-semibold tracking-tight leading-[1.1] whitespace-pre-line mb-5 ${
                      isVintage ? 'text-amber-100/90' : 'text-white'
                    }`}
                  >
                    {beat.headline}
                  </h1>
                )}

                {!beat.interactive && (
                  <p className="text-base sm:text-lg max-w-xl mx-auto leading-relaxed font-light text-white/45">
                    {beat.sub}
                  </p>
                )}

                {isSolution && (
                  <>
                    <p className="text-sm sm:text-base max-w-lg mx-auto leading-relaxed font-light text-white/55 mt-4">
                      {beat.sub}
                    </p>
                    <div className="mt-8 flex items-center gap-3">
                      <div className="h-px w-12 bg-gradient-to-r from-transparent to-cyber-blue/60" />
                      <span className="text-sm font-medium text-cyber-glow tracking-wide">
                        Here is the solution
                      </span>
                      <div className="h-px w-12 bg-gradient-to-l from-transparent to-cyber-blue/60" />
                    </div>
                  </>
                )}
              </div>
            )
          })}
        </div>

        <ScrollHint visible={!lastBeatVisible && progress < 0.12} />
      </div>
    </section>
  )
}
