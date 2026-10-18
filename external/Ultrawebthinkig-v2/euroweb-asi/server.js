import express from "express";
import helmet from "helmet";
import dotenv from "dotenv";
import client from "prom-client";
import { ASIcycle } from "./agi/core.js";
import { log } from "./lib/log.js";

dotenv.config();

const app = express();
app.use(express.json());
app.use(helmet({ crossOriginResourcePolicy: { policy: "cross-origin" } }));

const PORT = process.env.PORT || 8088;
const HOST = process.env.HOST || "0.0.0.0";
const CYCLE = parseInt(process.env.CYCLE_MS || "5000", 10);

// Prometheus metrics (ASI-level)
const registry = new client.Registry();
client.collectDefaultMetrics({
  prefix: "asi_",
  register: registry,
  timeout: 5000,
});

const g_cpu_last = new client.Gauge({
  name: "asi_cpu_last",
  help: "CPU load last",
  registers: [registry],
});
const g_cpu_ewma = new client.Gauge({
  name: "asi_cpu_ewma",
  help: "CPU EWMA",
  registers: [registry],
});
const g_mem_last = new client.Gauge({
  name: "asi_mem_last_gb",
  help: "Mem last GB",
  registers: [registry],
});
const g_mem_ewma = new client.Gauge({
  name: "asi_mem_ewma_gb",
  help: "Mem EWMA GB",
  registers: [registry],
});
const g_evloop_p99 = new client.Gauge({
  name: "asi_evloop_p99",
  help: "Event loop p99 seconds",
  registers: [registry],
});
const c_alerts = new client.Counter({
  name: "asi_alerts_total",
  help: "Total alerts fired",
  registers: [registry],
  labelNames: ["type", "what"],
});

let lastFrame = { t: null, bits: null, analysis: null, decision: null };

// scheduler
async function tick() {
  try {
    const frame = await ASIcycle();
    lastFrame = frame;

    // export Prometheus values
    g_cpu_last.set(frame.analysis.cpu.last || 0);
    g_cpu_ewma.set(frame.analysis.cpu.ewma || 0);
    g_mem_last.set(frame.analysis.memGB.last || 0);
    g_mem_ewma.set(frame.analysis.memGB.ewma || 0);
    g_evloop_p99.set(Number(frame.decision?.evloop_p99 || 0));

    (frame.decision?.actions || []).forEach((a) => {
      if (a.type === "ALERT" || a.type === "THROTTLE")
        c_alerts.labels(a.type, a.what).inc();
    });
  } catch (e) {
    log.error("ASI tick error:", e.message);
  }
}
setInterval(tick, CYCLE);
tick(); // start now

// API
app.get("/api/asi/frame", (req, res) => res.json(lastFrame));
app.get("/api/asi/analysis", (req, res) => res.json(lastFrame.analysis || {}));
app.get("/api/asi/decision", (req, res) => res.json(lastFrame.decision || {}));
// Health endpoints
app.get("/api/health", (req, res) =>
  res.json({
    ok: true,
    service: "JOAN ASI",
    status: "healthy",
    uptime: process.uptime(),
    memory: process.memoryUsage(),
    t: new Date().toISOString(),
    message: "💝 Jona protects Earth with love",
  }),
);

app.get("/health", (req, res) =>
  res.json({
    ok: true,
    service: "JOAN ASI",
    status: "healthy",
    uptime: process.uptime(),
    t: new Date().toISOString(),
    message: "🌍 JOAN ASI - Protecting Earth with Love",
  }),
);

app.get("/metrics", async (req, res) => {
  res.set("Content-Type", registry.contentType);
  res.end(await registry.metrics());
});

app.listen(PORT, HOST, () => {
  log.info(`✅ EuroWeb • ASI online at http://${HOST}:${PORT}`);
  log.info(`• Prometheus: /metrics`);
  log.info(`• Frame:      /api/asi/frame`);
});
