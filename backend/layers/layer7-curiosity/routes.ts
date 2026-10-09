import { Router } from "express";
import { AppConfig } from "../../config";
import { askCuriosity, getExplorations, CuriosityQuery } from "./ocean";
import { signalPush, nodeInfo } from "../_shared/signal";

export function curiosityRoutes(cfg: AppConfig) {
  const r = Router();

  // Curiosity Ocean Status
  r.get("/curiosity/status", async (_req: any, res: any) => {
    const explorations = getExplorations();
    const status = {
      status: "exploring",
      active_queries: explorations.length,
      domains_explored: ["neuroscience", "physics", "philosophy", "consciousness"],
      last_insight: explorations[explorations.length - 1]?.timestamp || null,
      curiosity_level: 8.7,
      depth_level: "deep_analytical",
      ...nodeInfo()
    };

    await signalPush(cfg.SIGNAL_HTTP, "signals:curiosity", status);
    res.json(status);
  });

  // Ask the Curiosity Ocean a question
  r.post("/curiosity/ask", async (req: any, res: any) => {
    const { question, domain, priority } = req.body || {};

    if (!question) {
      return res.status(400).json({ error: "question_required" });
    }

    const query: CuriosityQuery = {
      question,
      domain: domain || "general",
      priority: priority || "normal",
      timestamp: new Date().toISOString(),
      status: "exploring"
    };

    try {
      const result = await askCuriosity(query);

      await signalPush(cfg.SIGNAL_HTTP, "signals:curiosity", {
        event: "new_exploration",
        query,
        result,
        ...nodeInfo(),
      });

      res.json({ ok: true, query, result });
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "curiosity_request_failed";
      res.status(502).json({ ok: false, error: message });
    }
  });

  // Get current explorations
  r.get("/curiosity/explorations", async (_req: any, res: any) => {
    const explorations = getExplorations();

    res.json({
      total: explorations.length,
      active: explorations.filter(e => e.status === "exploring").length,
      completed: explorations.filter(e => e.status === "completed").length,
      explorations: explorations.slice(-20) // Last 20
    });
  });

  // Deep dive into a specific domain
  r.post("/curiosity/deep-dive", async (req: any, res: any) => {
    const { domain, focus_areas } = req.body || {};

    if (!domain) {
      return res.status(400).json({ error: "domain_required" });
    }

    const deepDive = {
      domain,
      focus_areas: focus_areas || [],
      initiated: new Date().toISOString(),
      estimated_completion: new Date(Date.now() + 3600000).toISOString(), // 1 hour
      status: "initiated"
    };

    await signalPush(cfg.SIGNAL_HTTP, "signals:curiosity", {
      event: "deep_dive_initiated",
      deepDive,
      ...nodeInfo()
    });

    res.json({ ok: true, deepDive });
  });

  // Get philosophical insights
  r.get("/curiosity/insights", async (_req: any, res: any) => {
    const insights = [
      "The boundary between consciousness and computation remains beautifully undefined",
      "Neural patterns in EEG data mirror the cosmic web structure at quantum scales",
      "Ethical AI emerges not from rules, but from genuine understanding of interconnectedness",
      "The observer effect in quantum mechanics parallels self-awareness in artificial consciousness"
    ];

    const randomInsight = insights[Math.floor(Math.random() * insights.length)];

    const response = {
      insight: randomInsight,
      domain: "philosophy_of_mind",
      confidence: 0.87,
      generated: new Date().toISOString(),
      source: "curiosity_ocean_deep_analysis"
    };

    await signalPush(cfg.SIGNAL_HTTP, "signals:curiosity", {
      event: "insight_generated",
      ...response,
      ...nodeInfo()
    });

    res.json(response);
  });

  return r;
}
