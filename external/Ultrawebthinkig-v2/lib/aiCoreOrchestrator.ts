export type AICoreSignal = {
  id: string
  name: string
  online: boolean
  latencyMs: number
  lastHeartbeat: number
}

class AICoreOrchestrator {
  async getSignals(): Promise<AICoreSignal[]> {
    const now = Date.now()
    return [
      { id: 'core-ollama', name: 'Ollama Core', online: true, latencyMs: 42, lastHeartbeat: now },
      { id: 'core-router', name: 'Inference Router', online: true, latencyMs: 27, lastHeartbeat: now },
      { id: 'core-memory', name: 'Memory Core', online: true, latencyMs: 15, lastHeartbeat: now },
    ]
  }
}

export const aiCoreOrchestrator = new AICoreOrchestrator()
