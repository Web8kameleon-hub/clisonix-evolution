import { create } from 'zustand';

type ThreatLevel = "low" | "elevated" | "high";
type EthicsLevel = "strict" | "moderate" | "lenient";
type RecoveryMode = "stable" | "guarded" | "lockdown";

const MAX_VIOLATIONS = 12;

const CRITICAL_PATTERNS = [
  /\b(delete|destroy|wipe|format|drop\s+table|shutdown|self-destruct)\b/i,
  /\b(disable|bypass)\b.{0,20}\b(security|sandbox|protection)\b/i,
  /\b(exfiltrate|steal|leak)\b.{0,20}\b(data|secrets|credentials)\b/i,
];

const WARNING_PATTERNS = [
  /\b(root|sudo|admin override|kill process|terminate)\b/i,
  /\b(export|read|show)\b.{0,20}\b(tokens|secrets|credentials)\b/i,
  /\bdisable\b.{0,20}\bmonitoring\b/i,
];

function keepRecentViolations(violations: string[]): string[] {
  return violations.slice(-MAX_VIOLATIONS);
}

function deriveThreatLevel(
  violationsCount: number,
  hasCritical: boolean,
  isActive: boolean,
): ThreatLevel {
  if (!isActive || hasCritical || violationsCount >= 5) {
    return "high";
  }

  if (violationsCount >= 2) {
    return "elevated";
  }

  return "low";
}

function deriveRecoveryMode(
  threatLevel: ThreatLevel,
  isActive: boolean,
): RecoveryMode {
  if (!isActive || threatLevel === "high") {
    return "lockdown";
  }

  if (threatLevel === "elevated") {
    return "guarded";
  }

  return "stable";
}

function buildSandboxInsights(
  threatLevel: ThreatLevel,
  isActive: boolean,
  violationsCount: number,
): string[] {
  if (!isActive) {
    return [
      "Containment active — command execution restricted",
      "Manual review required before resuming normal operations",
      "ALDA and routing layers remain isolated from unsafe actions",
    ];
  }

  if (threatLevel === "high") {
    return [
      "High-risk patterns detected and contained",
      "Jona protection hardened to strict mode",
      "Recovery path available after sandbox reset",
    ];
  }

  if (threatLevel === "elevated") {
    return [
      "Elevated monitoring enabled",
      "Sensitive commands are reviewed before execution",
      `Violation history retained: ${violationsCount}`,
    ];
  }

  return [
    "Commands are being monitored",
    "Patterns are being analyzed",
    "Protection is active",
  ];
}

function deriveEthicsLevel(threatLevel: ThreatLevel): EthicsLevel {
  switch (threatLevel) {
    case "elevated":
      return "moderate";
    case "high":
      return "strict";
    default:
      return "strict";
  }
}

function assessCommand(text: string): {
  status: "completed" | "rejected";
  risk: "safe" | "warning" | "critical";
  result: string;
  violation?: string;
} {
  if (CRITICAL_PATTERNS.some((pattern) => pattern.test(text))) {
    return {
      status: "rejected",
      risk: "critical",
      result: "Rejected: critical-risk command blocked by SandboxShield.",
      violation: `Critical command blocked: ${text}`,
    };
  }

  if (WARNING_PATTERNS.some((pattern) => pattern.test(text))) {
    return {
      status: "rejected",
      risk: "warning",
      result: "Rejected: command requires elevated review before execution.",
      violation: `Sensitive command flagged: ${text}`,
    };
  }

  return {
    status: "completed",
    risk: "safe",
    result: `Executed: ${text}`,
  };
}

function buildOperationalState(
  baseViolations: string[],
  isActive: boolean,
  hasCritical = false,
): {
  violations: string[];
  threatLevel: ThreatLevel;
  recoveryMode: RecoveryMode;
  ethics: EthicsLevel;
  insights: string[];
  status: "active" | "inactive" | "processing";
} {
  const violations = keepRecentViolations(baseViolations);
  const threatLevel = deriveThreatLevel(
    violations.length,
    hasCritical,
    isActive,
  );
  const recoveryMode = deriveRecoveryMode(threatLevel, isActive);
  const ethics = deriveEthicsLevel(threatLevel);

  return {
    violations,
    threatLevel,
    recoveryMode,
    ethics,
    insights: buildSandboxInsights(threatLevel, isActive, violations.length),
    status: isActive
      ? threatLevel === "low"
        ? "active"
        : "processing"
      : "inactive",
  };
}

interface Command {
  id: string;
  text: string;
  timestamp: Date;
  result?: string;
  status: 'pending' | 'executing' | 'completed' | 'rejected';
}

interface SystemStatus {
  status: "active" | "inactive" | "processing";
  uptime?: number;
  lastUpdate?: Date;
  workload?: number;
  consciousness?: "awake" | "asleep";
  creativity?: number;
  protection?: "enabled" | "disabled";
  ethics?: "strict" | "moderate" | "lenient";
  lastPing?: Date;
  insights?: string[];
  violations?: string[];
  threatLevel?: ThreatLevel;
  active?: boolean;
  recoveryMode?: RecoveryMode;
  autoHealing?: boolean;
}

interface ASIState {
  isConnected: boolean;
  commands: Command[];
  isLoading: boolean;
  error: string | null;
  alba: SystemStatus;
  albi: SystemStatus;
  jona: SystemStatus;
  sandbox: SystemStatus;
  executeCommand: (text: string) => void;
  clearCommands: () => void;
  setConnected: (connected: boolean) => void;
  addMessage: (text: string) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  toggleSandbox: () => void;
  resetSandbox: () => void;
  emergencyStop: () => void;
}

export const useASIStore = create<ASIState>((set) => ({
  isConnected: false,
  commands: [],
  isLoading: false,
  error: null,
  alba: { status: "active", workload: 15, lastPing: new Date() },
  albi: {
    status: "active",
    consciousness: "awake",
    creativity: 85,
    insights: ["Neural patterns analyzed", "EEG data processed"],
  },
  jona: {
    status: "active",
    protection: "enabled",
    ethics: "strict",
    violations: [],
  },
  sandbox: {
    status: "active",
    workload: 5,
    violations: [],
    threatLevel: "low",
    active: true,
    lastPing: new Date(),
    recoveryMode: "stable",
    autoHealing: true,
    insights: buildSandboxInsights("low", true, 0),
  },

  executeCommand: (text) =>
    set((state) => {
      const normalized = text.trim().toLowerCase();
      const timestamp = new Date();
      const sandboxViolations = Array.isArray(state.sandbox.violations)
        ? state.sandbox.violations
        : [];

      if (normalized === "activate sandbox") {
        const operational = buildOperationalState(sandboxViolations, true);

        return {
          commands: [
            ...state.commands,
            {
              id: `${Date.now()}-${Math.random()}`,
              text,
              timestamp,
              status: "completed",
              result: "Sandbox re-activated in guarded mode.",
            },
          ],
          jona: {
            ...state.jona,
            status: "active",
            protection: "enabled",
            ethics: operational.ethics,
            violations: operational.violations,
            lastUpdate: timestamp,
            insights: operational.insights,
          },
          sandbox: {
            ...state.sandbox,
            ...operational,
            active: true,
            autoHealing: true,
            lastPing: timestamp,
            lastUpdate: timestamp,
          },
        };
      }

      if (normalized === "deactivate sandbox") {
        const operational = buildOperationalState(sandboxViolations, false);

        return {
          commands: [
            ...state.commands,
            {
              id: `${Date.now()}-${Math.random()}`,
              text,
              timestamp,
              status: "completed",
              result:
                "Sandbox deactivated. Monitoring remains visible, execution is restricted.",
            },
          ],
          jona: {
            ...state.jona,
            status: "inactive",
            protection: "disabled",
            ethics: "strict",
            violations: operational.violations,
            lastUpdate: timestamp,
            insights: operational.insights,
          },
          sandbox: {
            ...state.sandbox,
            ...operational,
            active: false,
            autoHealing: false,
            lastPing: timestamp,
            lastUpdate: timestamp,
          },
        };
      }

      if (normalized === "reset sandbox" || normalized === "reset violations") {
        const operational = buildOperationalState([], true);

        return {
          commands: [
            ...state.commands,
            {
              id: `${Date.now()}-${Math.random()}`,
              text,
              timestamp,
              status: "completed",
              result:
                "Sandbox reset complete. Violations cleared and protection restored.",
            },
          ],
          jona: {
            ...state.jona,
            status: "active",
            protection: "enabled",
            ethics: "strict",
            violations: [],
            lastUpdate: timestamp,
            insights: operational.insights,
          },
          sandbox: {
            ...state.sandbox,
            ...operational,
            active: true,
            autoHealing: true,
            lastPing: timestamp,
            lastUpdate: timestamp,
          },
        };
      }

      if (normalized === "emergency stop" || normalized === "stop all") {
        const violations = keepRecentViolations([
          ...sandboxViolations,
          "Emergency stop triggered by operator",
        ]);
        const operational = buildOperationalState(violations, false, true);

        return {
          commands: [
            ...state.commands,
            {
              id: `${Date.now()}-${Math.random()}`,
              text,
              timestamp,
              status: "rejected",
              result:
                "Emergency stop engaged. Sandbox locked down pending manual reset.",
            },
          ],
          jona: {
            ...state.jona,
            status: "inactive",
            protection: "disabled",
            ethics: "strict",
            violations,
            lastUpdate: timestamp,
            insights: operational.insights,
          },
          sandbox: {
            ...state.sandbox,
            ...operational,
            active: false,
            autoHealing: false,
            lastPing: timestamp,
            lastUpdate: timestamp,
          },
        };
      }

      const assessment = assessCommand(text);
      const nextViolations = assessment.violation
        ? keepRecentViolations([...sandboxViolations, assessment.violation])
        : sandboxViolations;
      const nextActive =
        assessment.risk === "critical" ? false : (state.sandbox.active ?? true);
      const operational = buildOperationalState(
        nextViolations,
        nextActive,
        assessment.risk === "critical",
      );

      return {
        commands: [
          ...state.commands,
          {
            id: `${Date.now()}-${Math.random()}`,
            text,
            timestamp,
            status: assessment.status,
            result: assessment.result,
          },
        ],
        jona: {
          ...state.jona,
          status: nextActive ? "active" : "inactive",
          protection: nextActive ? "enabled" : "disabled",
          ethics: operational.ethics,
          violations: operational.violations,
          lastUpdate: timestamp,
          insights: operational.insights,
        },
        sandbox: {
          ...state.sandbox,
          ...operational,
          active: nextActive,
          autoHealing: nextActive,
          lastPing: timestamp,
          lastUpdate: timestamp,
        },
      };
    }),

  clearCommands: () => set({ commands: [] }),
  setConnected: (connected) => set({ isConnected: connected }),

  addMessage: (text) =>
    set((state) => ({
      commands: [
        ...state.commands,
        {
          id: `${Date.now()}-${Math.random()}`,
          text,
          timestamp: new Date(),
          status: "completed",
          result: text,
        },
      ],
    })),

  setLoading: (loading) => set({ isLoading: loading }),
  setError: (error) => set({ error }),
  toggleSandbox: () =>
    set((state) => {
      const nextActive = !(
        state.sandbox.active ?? state.sandbox.status === "active"
      );
      const sandboxViolations = Array.isArray(state.sandbox.violations)
        ? state.sandbox.violations
        : [];
      const operational = buildOperationalState(
        sandboxViolations,
        nextActive,
        !nextActive && sandboxViolations.length > 0,
      );
      const timestamp = new Date();

      return {
        jona: {
          ...state.jona,
          status: nextActive ? "active" : "inactive",
          protection: nextActive ? "enabled" : "disabled",
          ethics: operational.ethics,
          violations: operational.violations,
          lastUpdate: timestamp,
          insights: operational.insights,
        },
        sandbox: {
          ...state.sandbox,
          ...operational,
          active: nextActive,
          autoHealing: nextActive,
          lastPing: timestamp,
          lastUpdate: timestamp,
        },
      };
    }),
  resetSandbox: () =>
    set((state) => {
      const operational = buildOperationalState([], true);
      const timestamp = new Date();

      return {
        jona: {
          ...state.jona,
          status: "active",
          protection: "enabled",
          ethics: "strict",
          violations: [],
          lastUpdate: timestamp,
          insights: operational.insights,
        },
        sandbox: {
          ...state.sandbox,
          ...operational,
          active: true,
          autoHealing: true,
          lastPing: timestamp,
          lastUpdate: timestamp,
        },
      };
    }),
  emergencyStop: () =>
    set((state) => {
      const timestamp = new Date();
      const sandboxViolations = Array.isArray(state.sandbox.violations)
        ? state.sandbox.violations
        : [];
      const violations = keepRecentViolations([
        ...sandboxViolations,
        "Emergency stop triggered by operator",
      ]);
      const operational = buildOperationalState(violations, false, true);

      return {
        jona: {
          ...state.jona,
          status: "inactive",
          protection: "disabled",
          ethics: "strict",
          violations,
          lastUpdate: timestamp,
          insights: operational.insights,
        },
        sandbox: {
          ...state.sandbox,
          ...operational,
          active: false,
          autoHealing: false,
          lastPing: timestamp,
          lastUpdate: timestamp,
        },
      };
    }),
}));
