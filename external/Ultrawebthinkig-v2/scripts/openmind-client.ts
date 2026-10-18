export interface ConversationHistory {
  id: string;
  timestamp: string;
  query: string;
  response: string;
  confidence: number;
}

export interface OpenMindResponse {
  success: boolean;
  response: string;
  confidence: number;
  timestamp: string;
  conversationId?: string;
}

class OpenMindClient {
  private baseUrl: string;
  private conversations: ConversationHistory[] = [];

  constructor(baseUrl = 'http://localhost:8080') {
    this.baseUrl = baseUrl;
  }

  async query(message: string): Promise<OpenMindResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/manager/handle`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message, clientId: 'openmind-client' })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      // Store conversation - handle UltraCom manager response format
      const responseText = data.solution || data.message || data.response || 'No response';
      this.conversations.push({
        id: `conv-${Date.now()}`,
        timestamp: new Date().toISOString(),
        query: message,
        response: responseText,
        confidence: data.confidence || 0.85
      });

      return {
        success: data.success || true,
        response: responseText,
        confidence: data.confidence || 0.85,
        timestamp: data.timestamp || new Date().toISOString(),
        conversationId: this.conversations[this.conversations.length - 1]?.id
      };

    } catch (error) {
      console.error('OpenMind Client Error:', error);
      return {
        success: false,
        response: 'Unable to connect to OpenMind service. Using offline mode.',
        confidence: 0.0,
        timestamp: new Date().toISOString()
      };
    }
  }

  getConversations(): ConversationHistory[] {
    return this.conversations;
  }

  clearConversations(): void {
    this.conversations = [];
  }
}

export default OpenMindClient;
export type { OpenMindClient as OpenMindClientType };
