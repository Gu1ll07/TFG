import { app, BrowserWindow, dialog } from "electron";
import { spawn } from "child_process";
import path from "path";
import { fileURLToPath } from "url";
import http from "http";
import fs from "fs";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

let backendProcess = null;
let backendLogPath = "";

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function pingHealth() {
  return new Promise((resolve) => {
    const req = http.get("http://127.0.0.1:8000/health", (res) => {
      const ok = res.statusCode === 200;
      res.resume();
      resolve(ok);
    });

    req.on("error", () => resolve(false));
    req.setTimeout(500, () => {
      req.destroy();
      resolve(false);
    });
  });
}

async function waitForBackend(timeoutMs = 15000) {
  const deadline = Date.now() + timeoutMs;

  while (Date.now() < deadline) {
    const ok = await pingHealth();
    if (ok) return true;
    await sleep(300);
  }

  return false;
}

function logBackend(message) {
  try {
    fs.appendFileSync(backendLogPath, `[${new Date().toISOString()}] ${message}\n`);
  } catch {}
}

function startBackend() {
  if (!app.isPackaged) {
    return;
  }

  const backendExe = path.join(process.resourcesPath, "backend", "backend.exe");
  const backendDir = path.dirname(backendExe);

  backendLogPath = path.join(app.getPath("userData"), "backend-launch.log");
  fs.writeFileSync(backendLogPath, "", "utf8");

  logBackend(`app.isPackaged = ${app.isPackaged}`);
  logBackend(`process.resourcesPath = ${process.resourcesPath}`);
  logBackend(`backendExe = ${backendExe}`);
  logBackend(`backendDir = ${backendDir}`);
  logBackend(`backendExe exists = ${fs.existsSync(backendExe)}`);

  if (!fs.existsSync(backendExe)) {
    dialog.showErrorBox(
      "Backend no encontrado",
      `No existe backend.exe en:\n${backendExe}\n\nLog:\n${backendLogPath}`
    );
    return;
  }

  backendProcess = spawn(backendExe, [], {
    cwd: backendDir,
    windowsHide: false,
    stdio: ["ignore", "pipe", "pipe"]
  });

  logBackend(`spawn launched, pid = ${backendProcess.pid ?? "unknown"}`);

  backendProcess.stdout?.on("data", (data) => {
    logBackend(`STDOUT: ${data.toString()}`);
  });

  backendProcess.stderr?.on("data", (data) => {
    logBackend(`STDERR: ${data.toString()}`);
  });

  backendProcess.on("error", (err) => {
    logBackend(`PROCESS ERROR: ${err.stack || err.message || String(err)}`);
    dialog.showErrorBox(
      "Error arrancando backend",
      `${String(err)}\n\nLog:\n${backendLogPath}`
    );
  });

  backendProcess.on("exit", (code, signal) => {
    logBackend(`PROCESS EXIT: code=${code} signal=${signal}`);
  });
}

function stopBackend() {
  if (backendProcess) {
    try {
      backendProcess.kill();
      logBackend("PROCESS KILLED");
    } catch (err) {
      logBackend(`KILL ERROR: ${err.stack || err.message || String(err)}`);
    }
    backendProcess = null;
  }
}

function createWindow() {
  const win = new BrowserWindow({
    width: 1920,
    height: 1080
  });

  win.webContents.on("did-fail-load", (_event, code, desc, url) => {
    dialog.showErrorBox("Error cargando renderer", `Código: ${code}\nDescripción: ${desc}\nURL: ${url}`);
  });

  win.loadFile(path.join(__dirname, "html", "index.html"));
  win.webContents.openDevTools({ mode: "detach" });
}

app.whenReady().then(async () => {
  startBackend();

  if (app.isPackaged) {
    const ok = await waitForBackend();

    if (!ok) {
      dialog.showErrorBox(
        "Error de arranque",
        `El backend no ha arrancado correctamente en http://127.0.0.1:8000\n\nRevisa el log:\n${backendLogPath}`
      );
      app.quit();
      return;
    }
  }

  createWindow();

  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on("before-quit", () => {
  stopBackend();
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") app.quit();
});