// Builds NPM/payload/ from the engine repo. Run via `npm run build`
// (also runs automatically on `prepack`, so `npm publish` always ships fresh skills).
// Payload = methodology skills only. Media (INBOX/REFERENCES/INDEX) is NEVER packed.
const fs = require("fs");
const path = require("path");

const NPM_DIR = path.resolve(__dirname, "..");
const REPO_ROOT = path.resolve(NPM_DIR, "..");
const SRC_SKILLS = path.join(REPO_ROOT, ".agents", "skills");
const OUT = path.join(NPM_DIR, "payload", "skills");

if (!fs.existsSync(path.join(SRC_SKILLS, "animate", "SKILL.md"))) {
  console.error(`[uiux-overz] skills not found at ${SRC_SKILLS} — run from the UIUX_ENGINE repo.`);
  process.exit(1);
}

fs.rmSync(OUT, { recursive: true, force: true });
fs.mkdirSync(OUT, { recursive: true });
fs.cpSync(SRC_SKILLS, OUT, { recursive: true });

const names = fs.readdirSync(OUT).filter((n) => fs.existsSync(path.join(OUT, n, "SKILL.md")));
let bytes = 0;
for (const f of fs.readdirSync(OUT, { recursive: true, withFileTypes: true })) {
  if (f.isFile()) bytes += fs.statSync(path.join(f.parentPath || f.path, f.name)).size;
}
console.log(`[uiux-overz] payload built: ${names.length} skills, ${(bytes / 1024 / 1024).toFixed(2)} MB -> ${OUT}`);
