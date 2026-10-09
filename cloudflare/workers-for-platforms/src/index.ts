export interface Env {
  DISPATCH_NAMESPACE: DispatchNamespace;
  BINDING_NAME: KVNamespace;
  DB: D1Database;
  TEMPLATES_BUCKET: R2Bucket;
  ASSETS_BUCKET: R2Bucket;
  ALLOWED_EMAIL?: string;
  CUSTOM_DOMAIN?: string;
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);

    if (url.pathname === "/health") {
      // Surface only non-sensitive readiness information.
      return Response.json({
        status: "ok",
        service: "clisonix-workers-for-platforms",
        customDomain: env.CUSTOM_DOMAIN ?? null,
        hasDispatchNamespace: Boolean(env.DISPATCH_NAMESPACE),
      });
    }

    if (url.pathname === "/dispatch/check") {
      const scriptName = url.searchParams.get("script");
      if (!scriptName) {
        return Response.json({ error: "Missing script query parameter" }, { status: 422 });
      }

      try {
        const entry = env.DISPATCH_NAMESPACE.get(scriptName);
        return Response.json({
          script: scriptName,
          available: Boolean(entry),
        });
      } catch (error) {
        return Response.json(
          { error: "Dispatch namespace lookup failed", details: String(error) },
          { status: 503 },
        );
      }
    }

    return Response.json({
      message: "Workers for Platforms endpoint",
      routes: ["/health", "/dispatch/check?script=<name>"],
    });
  },
};
