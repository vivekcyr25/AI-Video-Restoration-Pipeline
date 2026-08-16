/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: [
          'Barlow Condensed',
          'Barlow Semi Condensed',
          '-apple-system',
          'BlinkMacSystemFont',
          'Segoe UI',
          'system-ui',
          'sans-serif',
        ],
        mono: ['JetBrains Mono', 'SF Mono', 'Menlo', 'Consolas', 'monospace'],
        display: ['Barlow Condensed', 'Barlow Semi Condensed', '-apple-system', 'sans-serif'],
      },
      colors: {
        obsidian: {
          950: '#030305',
          900: '#06070a',
          850: '#090b10',
          800: '#0d1017',
          700: '#141824',
        },
        electric: {
          cyan: '#00f0ff',
          blue: '#38bdf8',
          sky: '#0284c7',
          glow: '#67e8f9',
          deep: '#0369a1',
        },
        violet: {
          subtle: '#a855f7',
          glow: '#c084fc',
          deep: '#581c87',
        },
        vintage: {
          amber: '#d97706',
          sepia: '#92400e',
          crt: '#1c140a',
        },
        // Keep legacy cyber colors for backward compat with existing ShaderBackground etc
        cyber: {
          cyan: '#5eead4',
          blue: '#0071e3',
          glow: '#64d2ff',
        },
      },
      animation: {
        'pulse-soft': 'pulse-soft 3s ease-in-out infinite',
        'pulse-glow': 'pulse-glow 2.5s ease-in-out infinite',
        'scan': 'scan 4s linear infinite',
        'beam': 'beam 3s ease-in-out infinite',
        'flow': 'flow 4s ease-in-out infinite',
      },
      keyframes: {
        'pulse-soft': {
          '0%, 100%': { opacity: '0.6' },
          '50%': { opacity: '1' },
        },
        'pulse-glow': {
          '0%, 100%': { opacity: '0.4', transform: 'scale(1)' },
          '50%': { opacity: '0.8', transform: 'scale(1.03)' },
        },
        scan: {
          '0%': { transform: 'translateY(-100%)' },
          '100%': { transform: 'translateY(1000%)' },
        },
        beam: {
          '0%, 100%': { transform: 'translateX(-100%)' },
          '50%': { transform: 'translateX(200%)' },
        },
        flow: {
          '0%, 100%': { transform: 'translateX(0)' },
          '50%': { transform: 'translateX(8px)' },
        },
      },
      // Custom box shadows available via Tailwind's boxShadow scale
      boxShadow: {
        'cyan-glow': '0 0 35px -5px rgba(0, 240, 255, 0.25)',
        'blue-glow': '0 0 35px -5px rgba(56, 189, 248, 0.25)',
        'violet-glow': '0 0 35px -5px rgba(168, 85, 247, 0.25)',
        'glass-card': '0 8px 32px 0 rgba(0, 0, 0, 0.37)',
      },
    },
  },
  plugins: [],
}
