import { spawn } from "child_process";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const PY_ENTRY = path.join(__dirname, "pybackend", "app.py");

// --- Helpers para Windows ---
function pickPythonCmd() {
  if (process.platform !== "win32") return "python3";
  return "py"; // intenta primero el launcher de Windows
}

function run(cmd, args, opts = {}) {
  const child = spawn(cmd, args, { shell: process.platform === "win32", stdio: "inherit", ...opts });
  child.on("error", (e) => console.error(`[start.js] Error lanzando ${cmd}:`, e));
  return child;
}

// 1) Backend FastAPI
let pyCmd = pickPythonCmd();
let py = run(pyCmd, [PY_ENTRY], { cwd: path.join(__dirname, "pybackend") });
py.on("exit", (code) => {
  if (code !== 0) {
    console.error(`[start.js] ${pyCmd} salió con código ${code}. Reintentando con 'python'...`);
    py = run("python", [PY_ENTRY], { cwd: path.join(__dirname, "pybackend") });
  }
});

// 2) Electron tras un pequeño delay
const wait = (ms) => new Promise((r) => setTimeout(r, ms));
(async () => {
  await wait(1500);
  const el = run("npx", ["electron", "."]);
  el.on("close", (code) => { try { py.kill(); } catch {} ; process.exit(code ?? 0); });
})();
