import { spawn } from "child_process";
import path from "path";
import { fileURLToPath } from "url";
import fs from "fs";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const PY_DIR = path.join(__dirname, "pybackend");
const PY_ENTRY = path.join(PY_DIR, "app.py");

function pickPythonCmd() {
  if (process.platform === "win32") return "py";
  return "python3";
}

function run(cmd, args, opts = {}) {
  const child = spawn(cmd, args, {
    shell: process.platform === "win32",
    stdio: "inherit",
    ...opts
  });

  child.on("error", (err) => {
    console.error(`[start.js] Error lanzando ${cmd}:`, err);
  });

  return child;
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function startApp() {
  if (!fs.existsSync(PY_ENTRY)) {
    console.error(`[start.js] No se encuentra el backend: ${PY_ENTRY}`);
    process.exit(1);
  }

  let pyCmd = pickPythonCmd();
  let py = run(pyCmd, [PY_ENTRY], { cwd: PY_DIR });

  py.on("exit", (code) => {
    if (code !== 0 && pyCmd === "py") {
      console.error(`[start.js] 'py' salió con código ${code}. Reintentando con 'python'...`);
      py = run("python", [PY_ENTRY], { cwd: PY_DIR });
    }
  });

  await sleep(2000);

  const electronCmd = process.platform === "win32" ? "npx.cmd" : "npx";
  const el = run(electronCmd, ["electron", "."], { cwd: __dirname });

  el.on("close", (code) => {
    try {
      py.kill();
    } catch {}
    process.exit(code ?? 0);
  });
}

startApp();
