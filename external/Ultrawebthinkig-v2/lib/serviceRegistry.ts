export type RegistryService = {
  id: string
  name: string
  enabled: boolean
  endpoint?: string
}

class ServiceRegistry {
  private static instance: ServiceRegistry

  private readonly services: RegistryService[] = [
    { id: 'clisonix', name: 'Clisonix API', enabled: true, endpoint: 'https://clisonix.com' },
    { id: 'ollama', name: 'Ollama Local', enabled: true, endpoint: 'http://127.0.0.1:11434' },
  ]

  static getInstance(): ServiceRegistry {
    if (!ServiceRegistry.instance) {
      ServiceRegistry.instance = new ServiceRegistry()
    }
    return ServiceRegistry.instance
  }

  async queryAllServices(query: string): Promise<Record<string, unknown>> {
    const timestamp = Date.now()
    return {
      clisonix: {
        type: 'service_result',
        success: true,
        query,
        timestamp,
        data: [],
      },
      ollama: {
        type: 'service_result',
        success: true,
        query,
        timestamp,
        data: [],
      },
    }
  }

  getAllServices(): RegistryService[] {
    return this.services
  }

  getSystemOverview() {
    const total = this.services.length
    const online = this.services.filter((s) => s.enabled).length
    return {
      totalServices: total,
      onlineServices: online,
      offlineServices: total - online,
      health: online === total ? 'operational' : 'degraded',
    }
  }
}

export default ServiceRegistry
