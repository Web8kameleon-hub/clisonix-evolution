import { execFile } from "node:child_process";
import { promisify } from "node:util";

const execFileAsync = promisify(execFile);

type CommanderContext = {
	logger: {
		info: (data: unknown, message?: string) => void;
		warn: (data: unknown, message?: string) => void;
	};
	cfg: {
		AGI_COMMAND_WHITELIST: string;
		AGI_NET_TIMEOUT_MS: number;
		AGI_DISABLE_NETWORK: "0" | "1";
	};
};

type CommandInput = {
	type: string;
	params?: Record<string, unknown>;
};

type CommandResult = {
	ok: boolean;
	type: string;
	stdout?: string;
	stderr?: string;
	statusCode?: number;
	data?: unknown;
	error?: string;
};

function parseWhitelist(value: string): Set<string> {
	return new Set(
		value
			.split(",")
			.map((item) => item.trim())
			.filter(Boolean)
	);
}

export class Commander {
	private readonly commandWhitelist: Set<string>;

	constructor(private readonly context: CommanderContext) {
		this.commandWhitelist = parseWhitelist(context.cfg.AGI_COMMAND_WHITELIST);
	}

	async execute(command: CommandInput): Promise<CommandResult> {
		if (command.type === "shell") {
			return this.executeShell(command.params ?? {});
		}
		if (command.type === "fetch") {
			return this.executeFetch(command.params ?? {});
		}

		return {
			ok: false,
			type: command.type,
			error: `Unsupported command type: ${command.type}`,
		};
	}

	private async executeShell(params: Record<string, unknown>): Promise<CommandResult> {
		const executable = String(params.executable ?? "").trim();
		const args = Array.isArray(params.args)
			? params.args.map((item) => String(item))
			: [];

		if (!executable) {
			return { ok: false, type: "shell", error: "Missing executable" };
		}

		if (!this.commandWhitelist.has(executable)) {
			return { ok: false, type: "shell", error: `Executable not allowed: ${executable}` };
		}

		try {
			const { stdout, stderr } = await execFileAsync(executable, args, {
				timeout: this.context.cfg.AGI_NET_TIMEOUT_MS,
				windowsHide: true,
			});

			this.context.logger.info({ executable, argsCount: args.length }, "commander.executeShell success");

			return {
				ok: true,
				type: "shell",
				stdout: stdout?.toString() ?? "",
				stderr: stderr?.toString() ?? "",
			};
		} catch (error) {
			const message = error instanceof Error ? error.message : String(error);
			this.context.logger.warn({ executable, message }, "commander.executeShell failed");
			return { ok: false, type: "shell", error: message };
		}
	}

	private async executeFetch(params: Record<string, unknown>): Promise<CommandResult> {
		if (this.context.cfg.AGI_DISABLE_NETWORK === "1") {
			return { ok: false, type: "fetch", error: "Network is disabled by AGI_DISABLE_NETWORK=1" };
		}

		const url = String(params.url ?? "").trim();
		if (!url) {
			return { ok: false, type: "fetch", error: "Missing url" };
		}

		const method = String(params.method ?? "GET").toUpperCase();
		const headers = (params.headers as Record<string, string> | undefined) ?? {};
		const body = params.body;

		try {
			const controller = new AbortController();
			const timeout = setTimeout(() => controller.abort(), this.context.cfg.AGI_NET_TIMEOUT_MS);

			const response = await fetch(url, {
				method,
				headers,
				body: body === undefined ? undefined : JSON.stringify(body),
				signal: controller.signal,
			});

			clearTimeout(timeout);

			const contentType = response.headers.get("content-type") ?? "";
			const data = contentType.includes("application/json")
				? await response.json()
				: await response.text();

			this.context.logger.info({ method, url, status: response.status }, "commander.executeFetch success");

			return {
				ok: response.ok,
				type: "fetch",
				statusCode: response.status,
				data,
			};
		} catch (error) {
			const message = error instanceof Error ? error.message : String(error);
			this.context.logger.warn({ url, message }, "commander.executeFetch failed");
			return {
				ok: false,
				type: "fetch",
				error: message,
			};
		}
	}
}
