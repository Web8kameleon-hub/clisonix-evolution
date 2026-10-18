type MemoryEntryType = 'document' | 'conversation'

type MemoryEntry = {
  id: string
  title: string
  type: MemoryEntryType
  content: string
  metadata: {
    timestamp: number
    source?: string
    mimeType?: string
    size?: number
    confidence?: number
    responseTime?: number
    servicesUsed?: number
  }
}

export type MemorySearchResult = {
  entry: MemoryEntry
  relevanceScore: number
  matchedFragments: string[]
}

class OpenMindMemory {
  private static instance: OpenMindMemory
  private readonly entries: MemoryEntry[] = []

  static getInstance(): OpenMindMemory {
    if (!OpenMindMemory.instance) {
      OpenMindMemory.instance = new OpenMindMemory()
    }
    return OpenMindMemory.instance
  }

  async storeDocument(file: File): Promise<string> {
    const id = `doc_${Date.now()}_${Math.floor(Math.random() * 10000)}`
    const content = await file.text()
    this.entries.unshift({
      id,
      title: file.name,
      type: 'document',
      content,
      metadata: {
        timestamp: Date.now(),
        source: 'upload',
        mimeType: file.type,
        size: file.size,
      },
    })
    return id
  }

  async storeConversation(
    query: string,
    response: string,
    meta?: { confidence?: number; responseTime?: number; servicesUsed?: number },
  ): Promise<string> {
    const id = `conv_${Date.now()}_${Math.floor(Math.random() * 10000)}`
    this.entries.unshift({
      id,
      title: query.slice(0, 120),
      type: 'conversation',
      content: `Q: ${query}\nA: ${response}`,
      metadata: {
        timestamp: Date.now(),
        source: 'openmind',
        confidence: meta?.confidence,
        responseTime: meta?.responseTime,
        servicesUsed: meta?.servicesUsed,
      },
    })
    return id
  }

  search(query: string, limit = 10): MemorySearchResult[] {
    const needle = query.toLowerCase().trim()
    if (!needle) {
      return this.entries.slice(0, limit).map((entry) => ({ entry, relevanceScore: 0, matchedFragments: [] }))
    }

    const results = this.entries
      .map((entry) => {
        const hay = `${entry.title}\n${entry.content}`.toLowerCase()
        const idx = hay.indexOf(needle)
        const found = idx >= 0
        const relevanceScore = found ? 1 : 0
        const matchedFragments = found
          ? [entry.content.substring(Math.max(0, idx - 80), Math.min(entry.content.length, idx + needle.length + 80))]
          : []
        return { entry, relevanceScore, matchedFragments }
      })
      .filter((r) => r.relevanceScore > 0)
      .slice(0, limit)

    return results
  }

  getMemoryStats() {
    const totalDocuments = this.entries.filter((e) => e.type === 'document').length
    const totalConversations = this.entries.filter((e) => e.type === 'conversation').length

    return {
      totalEntries: this.entries.length,
      totalDocuments,
      totalConversations,
      lastUpdated: this.entries[0]?.metadata.timestamp ?? null,
    }
  }
}

export default OpenMindMemory
