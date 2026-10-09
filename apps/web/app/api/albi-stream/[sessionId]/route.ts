import { NextRequest } from "next/server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const encoder = new TextEncoder();

function toSseChunk(payload: unknown, event?: string): Uint8Array {
  const body = `${event ? `event: ${event}\n` : ""}data: ${JSON.stringify(payload)}\n\n`;
  return encoder.encode(body);
}

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ sessionId: string }> },
) {
  const { sessionId } = await params;
  const origin = request.nextUrl.origin;

  let interval: NodeJS.Timeout | null = null;

  const stream = new ReadableStream<Uint8Array>({
    start(controller) {
      let closed = false;

      const safeClose = () => {
        if (closed) return;
        closed = true;
        if (interval) {
          clearInterval(interval);
          interval = null;
        }
        try {
          controller.close();
        } catch {
          // Stream may already be closed
        }
      };

      request.signal.addEventListener("abort", safeClose);

      const pump = async () => {
        if (closed) return;

        try {
          const response = await fetch(
            `${origin}/api/albi-user/session/${sessionId}/metrics`,
            {
              method: "GET",
              cache: "no-store",
              headers: { Accept: "application/json" },
            },
          );

          if (!response.ok) {
            controller.enqueue(
              toSseChunk(
                {
                  status: response.status,
                  error: `metrics_endpoint_failed_${response.status}`,
                },
                "error",
              ),
            );
            return;
          }

          const payload = await response.json();
          controller.enqueue(toSseChunk(payload, "metrics"));
        } catch (error) {
          const message =
            error instanceof Error ? error.message : "stream_error";
          controller.enqueue(toSseChunk({ error: message }, "error"));
        }
      };

      void pump();
      interval = setInterval(() => {
        void pump();
      }, 2000);
    },

    cancel() {
      if (interval) {
        clearInterval(interval);
        interval = null;
      }
    },
  });

  return new Response(stream, {
    headers: {
      "Content-Type": "text/event-stream",
      "Cache-Control": "no-cache, no-transform",
      Connection: "keep-alive",
      "X-Accel-Buffering": "no",
    },
  });
}
