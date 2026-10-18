type DualMindConversation = {
  albiResponse: string
  jonaResponse: string
  sharedInsight: string
}

class DualMindEngine {
  private static instance: DualMindEngine

  static getInstance(): DualMindEngine {
    if (!DualMindEngine.instance) {
      DualMindEngine.instance = new DualMindEngine()
    }
    return DualMindEngine.instance
  }

  async generateAnthropicConversation(query: string, language: string): Promise<DualMindConversation> {
    const lang = language?.toLowerCase() || 'en'

    const albiResponse =
      lang.startsWith('sq')
        ? `ALBI: Ja analiza ime teknike për pyetjen "${query}" bazuar në kontekstin aktual të sistemit.`
        : `ALBI: Here is my technical analysis for "${query}" based on current system context.`

    const jonaResponse =
      lang.startsWith('sq')
        ? `JONA: Po shtoj perspektivën strategjike dhe praktike që ta bëjmë përgjigjen të përdorshme menjëherë.`
        : `JONA: I add the strategic and practical perspective so the answer is immediately actionable.`

    const sharedInsight =
      lang.startsWith('sq')
        ? 'Insight i përbashkët: kombino qasjen teknike me validim në burime reale dhe vepro hap-pas-hapi.'
        : 'Shared insight: combine technical approach with real-source validation and execute step-by-step.'

    return { albiResponse, jonaResponse, sharedInsight }
  }
}

export default DualMindEngine
