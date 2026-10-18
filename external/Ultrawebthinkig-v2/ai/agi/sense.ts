import { promises as fs } from "node:fs";
import { basename, extname } from "node:path";

type SenseContext = {
	logger: {
		info: (data: unknown, message?: string) => void;
		warn: (data: unknown, message?: string) => void;
	};
	cfg: {
		AGI_DATA_DIR?: string;
	};
};

export type SensedText = {
	tags: string[];
	tokens: number;
	chars: number;
	languageHint: "sq" | "en" | "mixed" | "unknown";
	sentiment: "positive" | "neutral" | "negative";
	keywords: string[];
};

export type SensedFile = {
	modality: "audio" | "signal" | "text" | "json" | "binary";
	tags: string[];
	summary: string;
	meta: {
		path: string;
		name: string;
		ext: string;
		sizeBytes: number;
		modifiedAt: string;
	};
	features: {
		sizeKb: number;
		lineCount?: number;
		keysCount?: number;
		sample?: string;
	};
};

function detectLanguage(text: string): "sq" | "en" | "mixed" | "unknown" {
	const normalized = text.toLowerCase();
	const albanianMarkers = ["është", "çfarë", "për", "faleminderit", "mirë", "shërbim"];
	const englishMarkers = ["the", "what", "service", "model", "system", "data"];

	const albanianHits = albanianMarkers.filter((item) => normalized.includes(item)).length;
	const englishHits = englishMarkers.filter((item) => normalized.includes(item)).length;

	if (albanianHits === 0 && englishHits === 0) return "unknown";
	if (albanianHits > 0 && englishHits > 0) return "mixed";
	return albanianHits > englishHits ? "sq" : "en";
}

function detectSentiment(text: string): "positive" | "neutral" | "negative" {
	const normalized = text.toLowerCase();
	const positiveWords = ["good", "great", "sukses", "mirë", "excellent", "thanks"];
	const negativeWords = ["error", "fail", "problem", "keq", "broken", "timeout"];

	const positiveScore = positiveWords.filter((word) => normalized.includes(word)).length;
	const negativeScore = negativeWords.filter((word) => normalized.includes(word)).length;

	if (positiveScore > negativeScore) return "positive";
	if (negativeScore > positiveScore) return "negative";
	return "neutral";
}

function extractKeywords(text: string, maxCount = 12): string[] {
	const stopWords = new Set([
		"the",
		"and",
		"for",
		"with",
		"that",
		"this",
		"nga",
		"dhe",
		"për",
		"me",
		"është",
		"ne",
		"to",
		"of",
	]);

	const words = text
		.toLowerCase()
		.replace(/[^\p{L}\p{N}\s]/gu, " ")
		.split(/\s+/)
		.filter((word) => word.length > 2 && !stopWords.has(word));

	const frequency = new Map<string, number>();
	for (const word of words) {
		frequency.set(word, (frequency.get(word) ?? 0) + 1);
	}

	return [...frequency.entries()]
		.sort((first, second) => second[1] - first[1])
		.slice(0, maxCount)
		.map(([keyword]) => keyword);
}

export class Sense {
	constructor(private readonly context: SenseContext) {}

	async fromText(text: string): Promise<SensedText> {
		const sanitizedText = text.trim();
		const tokens = sanitizedText.length > 0 ? sanitizedText.split(/\s+/).length : 0;
		const languageHint = detectLanguage(sanitizedText);
		const sentiment = detectSentiment(sanitizedText);
		const keywords = extractKeywords(sanitizedText);
		const tags = ["text", languageHint, sentiment, ...(tokens > 40 ? ["long"] : ["short"]), ...keywords.slice(0, 4)];

		this.context.logger.info({ tokens, languageHint, sentiment }, "sense.fromText completed");

		return {
			tags,
			tokens,
			chars: sanitizedText.length,
			languageHint,
			sentiment,
			keywords,
		};
	}

	async fromFile(filePath: string): Promise<SensedFile> {
		const stat = await fs.stat(filePath);
		const extension = extname(filePath).toLowerCase();
		const fileName = basename(filePath);

		let modality: SensedFile["modality"] = "binary";
		if ([".wav", ".mp3", ".flac", ".ogg"].includes(extension)) modality = "audio";
		else if ([".edf", ".bdf", ".csv"].includes(extension)) modality = "signal";
		else if ([".txt", ".md", ".log"].includes(extension)) modality = "text";
		else if ([".json"].includes(extension)) modality = "json";

		const baseMeta = {
			path: filePath,
			name: fileName,
			ext: extension,
			sizeBytes: stat.size,
			modifiedAt: stat.mtime.toISOString(),
		};

		const features: SensedFile["features"] = {
			sizeKb: Number((stat.size / 1024).toFixed(2)),
		};

		if (modality === "text" || modality === "json") {
			const rawContent = await fs.readFile(filePath, "utf-8");
			features.lineCount = rawContent.split(/\r?\n/).length;
			features.sample = rawContent.slice(0, 180);
			if (modality === "json") {
				try {
					const parsed = JSON.parse(rawContent) as Record<string, unknown>;
					features.keysCount = Object.keys(parsed).length;
				} catch {
					this.context.logger.warn({ filePath }, "sense.fromFile json parse warning");
				}
			}
		}

		const tags = ["file", modality, extension.replace(".", "") || "noext", ...(stat.size > 5_000_000 ? ["large"] : ["small"])];
		const summary = `${fileName} (${modality}) ${features.sizeKb}KB`;

		this.context.logger.info({ filePath, modality, size: stat.size }, "sense.fromFile completed");

		return {
			modality,
			tags,
			summary,
			meta: baseMeta,
			features,
		};
	}
}
