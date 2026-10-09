export type ModuleGuide = {
  id: string;
  name: string;
  href: string;
  summary: string;
  howTo: [string, string, string];
};

export const moduleGuides: ModuleGuide[] = [
  {
    id: "zurich",
    name: "Zürich Engine",
    href: "/zurich",
    summary:
      "Deterministic 9-stage reasoning for structured decision workflows.",
    howTo: [
      "Open the module",
      "Enter a precise prompt or problem",
      "Review the staged output and export the result",
    ],
  },
  {
    id: "debate",
    name: "Trinity Debate",
    href: "/debate",
    summary: "Multi-perspective AI debate for deep analysis of one topic.",
    howTo: [
      "Open the module",
      "Submit one topic or question",
      "Compare viewpoints and capture final synthesis",
    ],
  },
  {
    id: "curiosity-ocean",
    name: "Curiosity Ocean",
    href: "/modules/curiosity-ocean",
    summary: "AI research chat for fast exploration and synthesis.",
    howTo: [
      "Open chat interface",
      "Ask focused domain questions",
      "Refine with follow-up prompts and save outputs",
    ],
  },
  {
    id: "web-reader",
    name: "Web Reader",
    href: "/modules/web-reader",
    summary: "Read and analyze web pages with AI assistance.",
    howTo: [
      "Paste URL",
      "Run page extraction",
      "Ask questions directly on extracted content",
    ],
  },
  {
    id: "archive",
    name: "Archive & Research",
    href: "/modules/archive",
    summary: "Multi-source academic and knowledge retrieval workflows.",
    howTo: [
      "Set a research keyword",
      "Choose sources and filters",
      "Export findings or continue in another module",
    ],
  },
  {
    id: "social-intelligence",
    name: "Social Intelligence",
    href: "/modules/social-intelligence",
    summary: "Cross-platform content discovery and trend monitoring.",
    howTo: [
      "Define a topic or entity",
      "Run social search",
      "Compare media signals and preserve evidence",
    ],
  },
  {
    id: "specialized-chat",
    name: "Specialized Expert Chat",
    href: "/modules/specialized-chat",
    summary: "Domain-focused assistant for high-precision responses.",
    howTo: [
      "Select specialist context",
      "Provide concise requirements",
      "Use iterative prompts for accuracy",
    ],
  },
  {
    id: "aviation-weather",
    name: "Aviation Weather",
    href: "/modules/aviation-weather",
    summary: "Operational METAR/TAF and aviation weather interpretation.",
    howTo: [
      "Search airport/ICAO",
      "Inspect live weather blocks",
      "Use insights for planning decisions",
    ],
  },
  {
    id: "eeg-analysis",
    name: "EEG Analysis",
    href: "/modules/eeg-analysis",
    summary: "Brainwave metrics and cognitive pattern exploration.",
    howTo: [
      "Load or stream EEG data",
      "Run analysis pipeline",
      "Review charts and interpretation panels",
    ],
  },
  {
    id: "neural-synthesis",
    name: "Neural Synthesis",
    href: "/modules/neural-synthesis",
    summary: "Neural-to-audio synthesis sessions and frequency control.",
    howTo: [
      "Start synthesis session",
      "Tune waveform and target frequency",
      "Preview/export generated audio",
    ],
  },
  {
    id: "nanogrid-zeiss",
    name: "NanoGrid + ZEISS",
    href: "/modules/nanogrid-zeiss",
    summary:
      "Limit-mode launch surface for ZEISS Vision Ultra neural workflows.",
    howTo: [
      "Open NanoGrid base module",
      "Choose one preset workflow",
      "Run analysis in Curiosity Ocean with auto language",
    ],
  },
  {
    id: "kloud-bridge",
    name: "Kloud Bridge",
    href: "/modules/kloud-bridge",
    summary:
      "Clean live-service view for bridge health, connectivity readiness, and verified synchronization.",
    howTo: [
      "Open the Kloud Bridge module",
      "Refresh bridge health and upstream visibility",
      "Check real synchronization readiness from the live service view",
    ],
  },
  {
    id: "weather-dashboard",
    name: "Weather & Cognitive",
    href: "/modules/weather-dashboard",
    summary: "Correlation between weather conditions and cognitive state.",
    howTo: [
      "Select location and period",
      "Inspect weather + cognitive panels",
      "Track pattern changes over time",
    ],
  },
  {
    id: "account",
    name: "Account & Billing",
    href: "/modules/account",
    summary: "Subscription, billing, and profile management.",
    howTo: [
      "Open account settings",
      "Verify billing/subscription details",
      "Update profile and payment info",
    ],
  },
  {
    id: "my-data-dashboard",
    name: "My Data Dashboard",
    href: "/modules/my-data-dashboard",
    summary: "Data source and integration overview for user pipelines.",
    howTo: [
      "Connect data source",
      "Validate ingestion status",
      "Use dashboard widgets for monitoring",
    ],
  },
  {
    id: "mymirror-now",
    name: "MyMirror Now",
    href: "/modules/mymirror-now",
    summary: "Real-time operational portal with live system metrics.",
    howTo: [
      "Open live panel",
      "Check service cards and alerts",
      "Act on anomalies through linked tools",
    ],
  },
  {
    id: "developer-docs",
    name: "Developer Documentation",
    href: "/developers",
    summary: "API reference, endpoint playground, and SDK examples.",
    howTo: [
      "Open developer portal",
      "Test endpoints from playground",
      "Implement examples in your stack",
    ],
  },
];

export function getModuleGuideById(moduleId: string): ModuleGuide | undefined {
  return moduleGuides.find((moduleGuide) => moduleGuide.id === moduleId);
}

export function getModuleGuideByHref(href: string): ModuleGuide | undefined {
  return moduleGuides.find((moduleGuide) => moduleGuide.href === href);
}
