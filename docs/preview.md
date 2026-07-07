# Algorithm Preview Site

Live demo: **https://vivekcyr25.github.io/AI-Video-Restoration-Pipeline/**

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

## Features

- Scroll-driven intro narrative
- Interactive lighting-invariant explainer
- 8-stage pipeline walkthrough
- Before/after asset comparison

