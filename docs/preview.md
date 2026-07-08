# Algorithm Preview Site

Live demo: **https://vivekcyr25.github.io/AI-Video-Restoration-Pipeline/**

## Requirements

- Node.js 20+
- npm 10+
- Modern browser with WebGL enabled

## Local Development

```bash
cd preview
npm install
npm run dev
```

## Build

```bash
cd preview
npm run build
```

Output is written to `preview/dist/` and deployed automatically via GitHub Actions on push to `main`.

## Stack

- React 18 + Vite 6
- Tailwind CSS 3
- WebGL fragment shaders (background)
- GitHub Pages (Actions deploy)

## Browser Support

The preview is optimized for current Chromium, Firefox, and Safari releases with WebGL enabled.

## Audio note
Background music may require a first scroll/click to start due to browser autoplay rules. Use the mute button to control it.

## Troubleshooting

- If music does not start, click once anywhere on the page or use the speaker button.
- If development changes do not appear, restart `npm run dev` to refresh Vite state.

## Features

- Scroll-driven intro narrative
- Interactive lighting-invariant explainer
- 8-stage pipeline walkthrough
- Before/after asset comparison

## Deployment

Pushes to `main` that touch `preview/` trigger the GitHub Actions Pages workflow automatically.

