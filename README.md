# Birthday FM

A responsive, static birthday-radio experience for GitHub Pages. The landing page is public and shows a live countdown to 19 September at midnight IST; the broadcast screens sit behind a simple client-side password gate.

## Quick start

1. Edit `content.json` with her name, songs, wishes, and personal notes, or update the built-in preview content in `app.js`.
2. Add your recording as `audio/final-broadcast.mp3` (create the folder if needed).
3. The default password is `starlight`. Change `DEMO_PASSWORD` in `app.js` before sharing.

Optional: if you later want the messages hidden from casual source inspection too, use the included client-side encryption helper after installing Node:

```bash
node tools/encrypt-content.mjs content.json YOUR_PASSWORD
```

This writes an encrypted payload to `content.enc.js`. Remove `content.json` before pushing if it contains private text; keep the encrypted `content.enc.js`.

The simple password is intended to stop random visitors, not determined reverse-engineering. GitHub Pages itself remains publicly reachable.

## GitHub Pages

Push the contents of this folder to a GitHub repository, then choose **Settings → Pages → Deploy from branch → main → /(root)**. The site has no build step and uses relative paths, so it works in a repository subdirectory.

## Notes

GitHub Pages is static hosting. The password gate protects the content from casual source inspection, but it is not server-side authentication. For strict access control, host a Go API/server separately.
