import type { SensedText } from "./sense";

type MindContext = {
	logger: {
		info: (data: unknown, message?: string) => void;
	};
	cfg: {
		AGI_DISABLE_NETWORK?: "0" | "1";
	};
};

type PlanStep = {
	id: string;
	action: string;
	reason: string;
	priority: "low" | "medium" | "high";
};

export type MindPlan = {
	intent: "inform" | "analyze" | "execute" | "diagnose";
	confidence: number;
	steps: PlanStep[];
	constraints: string[];
	networkAllowed: boolean;
};

type PlanInput = SensedText & {
	modality?: string;
};

function detectIntentFromKeywords(keywords: string[]): MindPlan["intent"] {
	const keywordSet = new Set(keywords);
	if (["run", "execute", "command", "deploy", "start"].some((item) => keywordSet.has(item))) {
		return "execute";
	}
	if (["error", "bug", "issue", "debug", "fix"].some((item) => keywordSet.has(item))) {
		return "diagnose";
	}
	if (["analyze", "metrics", "report", "audit", "review"].some((item) => keywordSet.has(item))) {
		return "analyze";
	}
	return "inform";
}

function buildPlanSteps(intent: MindPlan["intent"], input: PlanInput): PlanStep[] {
	const baseline: PlanStep[] = [
		{
			id: "step-1",
			action: "extract-context",
			reason: "Capture user intent and constraints from real input",
			priority: "high",
		},
	];

	if (intent === "execute") {
		baseline.push(
			{
				id: "step-2",
				action: "prepare-command",
				reason: "Validate command against whitelist and permissions",
				priority: "high",
			},
			{
				id: "step-3",
				action: "execute-command",
				reason: "Run real operation and collect stdout/stderr",
				priority: "high",
			}
		);
	} else if (intent === "diagnose") {
		baseline.push(
			{
				id: "step-2",
				action: "collect-signals",
				reason: "Inspect logs, errors, and runtime traces",
				priority: "high",
			},
			{
				id: "step-3",
				action: "propose-fix",
				reason: "Generate actionable remediation based on actual findings",
				priority: "medium",
			}
		);
	} else if (intent === "analyze") {
		baseline.push(
			{
				id: "step-2",
				action: "aggregate-data",
				reason: "Combine metrics/signals from relevant modules",
				priority: "medium",
			},
			{
				id: "step-3",
				action: "summarize-insights",
				reason: "Return concise, useful analysis",
				priority: "medium",
			}
		);
	} else {
		baseline.push({
			id: "step-2",
			action: "respond-clearly",
			reason: "Provide concise and user-friendly information",
			priority: "medium",
		});
	}

	if (input.modality && input.modality !== "text") {
		baseline.push({
			id: "step-extra-modality",
			action: "normalize-modality",
			reason: `Adapt reasoning flow for ${input.modality} input`,
			priority: "medium",
		});
	}

	return baseline;
}

export class Mind {
	constructor(private readonly context: MindContext) {}

	async plan(input: PlanInput): Promise<MindPlan> {
		const intent = detectIntentFromKeywords(input.keywords ?? []);
		const networkAllowed = this.context.cfg.AGI_DISABLE_NETWORK !== "1";
		const steps = buildPlanSteps(intent, input);
		const confidenceBase = 0.55 + Math.min((input.tokens ?? 0) / 200, 0.35);
		const confidence = Number(Math.max(0.5, Math.min(confidenceBase, 0.95)).toFixed(2));
		const constraints = [
			"No mock/fake data",
			"Use real services and verifiable outputs",
			...(networkAllowed ? [] : ["Network operations disabled by config"]),
		];

		const result: MindPlan = {
			intent,
			confidence,
			steps,
			constraints,
			networkAllowed,
		};

		this.context.logger.info({ intent, confidence, stepCount: steps.length }, "mind.plan completed");
		return result;
	}
}
