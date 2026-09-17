#!/usr/bin/env node
// uiux-overz — one-command UIUX ENGINE installer.
// Usage: npx uiux-overz init [--dir <path>] [--minimal]
const fs = require("fs");
const path = require("path");

const VERSION = "1.0.0";
const PKG_ROOT = path.resolve(__dirname, "..");
const PAYLOAD_SKILLS = path.join(PKG_ROOT, "payload", "skills");
const TPL = (n) => fs.readFileSync(path.join(PKG_ROOT, "templates", n), "utf8");
const MANAGED_OPEN = "<!-- uiux-engine:managed -->";
const MANAGED_CLOSE = "<!-- /uiux-engine:managed -->";
const MEDIA_ROOT = "INBOX-OverzStyleUIUX";

function help() {
  console.log(`uiux-overz v${VERSION} — UIUX ENGINE one-command install
Usage:
  npx uiux-overz init [--dir <path>] [--minimal]

  init            scaffold into current folder (or --dir)
  --minimal       binder only (.agents/skills/uiux-engine), skip the 46-skill copy
  --dir <path>    target project folder (default: .)
  --help, -h      this text
  --version, -v   version`);
}

function copyDir(src, dest) {
  fs.mkdirSync(dest, { recursive: true });
  for (const e of fs.readdirSync(src, { withFileTypes: true })) {
    const s = path.join(src, e.name), d = path.join(dest, e.name);
    if (e.isDirectory()) copyDir(s, d);
    else if (e.isFile()) fs.copyFileSync(s, d);
  }
}

function dirSize(p) {
  let b = 0;
  for (const e of fs.readdirSync(p, { withFileTypes: true })) {
    const full = path.join(p, e.name);
    b += e.isDirectory() ? dirSize(full) : fs.statSync(full).size;
  }
  return b;
}

function ensureGitignore(project) {
  const gi = path.join(project, ".gitignore");
  const snippet = TPL("gitignore-snippet.txt").trim() + "\n";
  const current = fs.existsSync(gi) ? fs.readFileSync(gi, "utf8") : "";
  if (current.includes(MANAGED_OPEN) || current.includes("uiux-overz managed")) {
    console.log("  [skip] .gitignore already has uiux-overz rules");
    return;
  }
  fs.writeFileSync(gi, (current.replace(/\s*$/, "") + "\n\n" + snippet).replace(/^\n+/, ""));
  console.log("  [OK]   .gitignore media rules appended");
}

function ensureAgentsBlock(project) {
  const block = TPL("agents-block.md").trim() + "\n";
  const ag = path.join(project, "AGENTS.md");
  const name = path.basename(project);
  if (fs.existsSync(ag)) {
    const text = fs.readFileSync(ag, "utf8");
    if (text.includes(MANAGED_OPEN)) { console.log("  [skip] AGENTS.md already bound"); return; }
    fs.writeFileSync(ag, text.replace(/\s*$/, "") + "\n\n" + block);
    console.log("  [OK]   AGENTS.md block appended");
  } else {
    fs.writeFileSync(ag, `# ${name}\n\n${block}`);
    console.log("  [OK]   AGENTS.md created");
  }
}

function init(project, minimal) {
  console.log(`uiux-overz init\n  project: ${project}\n  mode: ${minimal ? "minimal (binder only)" : "full (46 skills)"}`);
  const agentsSkills = path.join(project, ".agents", "skills");
  const claudeBinder = path.join(project, ".claude", "skills", "uiux-engine");
  fs.mkdirSync(claudeBinder, { recursive: true });
  fs.writeFileSync(path.join(claudeBinder, "SKILL.md"), TPL("skill-binder.md"));
  console.log("  [OK]   .claude/skills/uiux-engine/SKILL.md");

  if (!minimal) {
    if (!fs.existsSync(path.join(PAYLOAD_SKILLS, "animate", "SKILL.md"))) {
      console.error("  [FAIL] payload missing — reinstall uiux-overz.");
      process.exit(1);
    }
    copyDir(PAYLOAD_SKILLS, agentsSkills);
    const n = fs.readdirSync(agentsSkills).filter((x) => fs.existsSync(path.join(agentsSkills, x, "SKILL.md"))).length;
    console.log(`  [OK]   .agents/skills/ (${n} skills, ${(dirSize(agentsSkills) / 1024 / 1024).toFixed(2)} MB)`);
  }
  const binderDir = path.join(agentsSkills, "uiux-engine");
  fs.mkdirSync(binderDir, { recursive: true });
  fs.writeFileSync(path.join(binderDir, "SKILL.md"), TPL("skill-binder.md"));
  console.log("  [OK]   .agents/skills/uiux-engine/SKILL.md");

  const kiloDir = path.join(project, ".kilo", "command");
  fs.mkdirSync(kiloDir, { recursive: true });
  fs.writeFileSync(path.join(kiloDir, "uiux.md"), TPL("kilo-uiux.md"));
  console.log("  [OK]   .kilo/command/uiux.md");

  for (const sub of ["images", "videos"]) {
    const d = path.join(project, MEDIA_ROOT, sub);
    fs.mkdirSync(d, { recursive: true });
    const keep = path.join(d, ".gitkeep");
    if (!fs.existsSync(keep)) fs.writeFileSync(keep, "");
  }
  console.log(`  [OK]   ${MEDIA_ROOT}/images/ + videos/`);

  ensureGitignore(project);
  ensureAgentsBlock(project);
  console.log("\n  Done. Open an agent in this project and describe what to design.");
}

function main() {
  const args = process.argv.slice(2);
  if (args.includes("--help") || args.includes("-h") || args.length === 0) { help(); return; }
  if (args.includes("--version") || args.includes("-v")) { console.log(VERSION); return; }
  if (args[0] !== "init") { console.error(`unknown command: ${args[0]}`); help(); process.exit(1); }
  const di = args.indexOf("--dir");
  const project = path.resolve(di !== -1 && args[di + 1] ? args[di + 1] : ".");
  init(project, args.includes("--minimal"));
}

main();
