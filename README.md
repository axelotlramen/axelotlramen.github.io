# axelotlramen's Gacha Dashboard

Public frontend for my (axelotlramen's) personal gacha stats dashboard: Genshin Impact, Honkai: Star Rail, and Arknights: Endfield. The data pipeline that produces `data/stats.json` and `data/endgame_history.csv` lives in the private `gacha-stats-backend` repo (included here as a submodule at `backend/`) and isn't public, since it hand-rolls auth against undocumented APIs.

Built with Vite, React, TypeScript, Tailwind CSS, and shadcn/ui.

## Running locally

```bash
npm install --prefix app
npm run dev --prefix app
```

This serves the site at `http://localhost:5173` using whatever data is at `app/public/data/`. That folder isn't tracked in git, since it's just a local copy of the backend's output, so copy it in yourself before running:

```bash
cp backend/data/stats.json backend/data/endgame_history.csv app/public/data/
```

(`git submodule update --init --remote` first if `backend/` is empty.)

## Editing your profile info

The intro card on the home page (username, bio, social links, latest video) is plain data, not something baked into a component. Edit it directly in `app/src/content/profile.ts`. Drop a real photo at `app/public/pfp.jpg` to replace the initials placeholder.

## Deployment

`.github/workflows/deploy.yml` builds the app (`npm run build` in `app/`) and deploys `app/dist` to GitHub Pages. It runs automatically on every push to `main`, and whenever the backend repo dispatches a `data-updated` event after a fresh scrape.

## Disclaimer

This is a personal fan-made project and isn't affiliated with HoYoverse or Arknights: Endfield's publishers. All assets belong to their respective owners.
