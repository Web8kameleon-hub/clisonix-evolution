// core/engines/chat-engine.ts
import { UltraMessage, ChatSession, AIProvider, ThinkingConfig } from '../types/chat';
import { SecurityGuard } from '../security/guardian';
import { PerformanceMonitor } from '../monitoring/performance';
import { AGIEngine } from './agi-engine';
import { ReasoningEngine } from './reasoning-engine';

export class ChatEngine {
    private securityGuard: SecurityGuard;
    private performanceMonitor: PerformanceMonitor;
    private agiEngine: AGIEngine;
    private reasoningEngine: ReasoningEngine;

    constructor() {
        this.securityGuard = new SecurityGuard();
        this.performanceMonitor = new PerformanceMonitor();
        this.agiEngine = new AGIEngine();
        this.reasoningEngine = new ReasoningEngine();
    }

    async generateResponse(
        session: ChatSession,
        provider: AIProvider,
        signal?: AbortSignal
    ): Promise<{
        content: string;
        tokens: number;
        confidence: number;
        reasoning: string[];
        metadata: any;
    }> {
        const startTime = Date.now();

        try {
            // Resolve last message safely
            const lastMessage = session.messages[session.messages.length - 1] as UltraMessage | undefined;
            if (!lastMessage?.content) {
                throw new Error('Invalid chat session: missing last message content.');
            }

            // Apply thinking depth and strategy
            const enhancedPrompt = this.enhancePrompt(
                lastMessage.content,
                session.context
            );

            // Generate response using AGI engine
            const agiResponse = await this.agiEngine.process(
                enhancedPrompt,
                provider,
                session.context,
                signal
            );

            // Apply reasoning chain
            const reasonedResponse = await this.reasoningEngine.process(
                agiResponse.content,
                session.context.depth,
                session.context.strategy
            );

            const processingTime = Date.now() - startTime;

            return {
                content: reasonedResponse.content,
                tokens: agiResponse.tokens + reasonedResponse.tokens,
                confidence: agiResponse.confidence * reasonedResponse.confidence,
                reasoning: reasonedResponse.chain,
                metadata: {
                    processingTime,
                    provider,
                    model: agiResponse.model,
                    cost: this.calculateCost(agiResponse.tokens, provider)
                }
            };

        } catch (error) {
            this.performanceMonitor.recordError('chat_engine', error);
            throw error;
        }
    }

    private enhancePrompt(content: string, context: ChatSession['context']): string {
        let enhanced = content;

        // Apply depth modifiers
        switch (context.depth) {
            case 'deep':
                enhanced = `[DEEP ANALYSIS REQUIRED] ${enhanced}\n\nPlease provide comprehensive analysis with multiple perspectives.`;
                break;
            case 'ultra-deep':
                enhanced = `[ULTRA-DEEP ANALYSIS] ${enhanced}\n\nExhaustive analysis required. Consider all possible angles, edge cases, and long-term implications.`;
                break;
        }

        // Apply strategy modifiers
        switch (context.strategy) {
            case 'creative':
                enhanced = `[CREATIVE THINKING] ${enhanced}\n\nThink outside the box. Generate innovative ideas and unconventional solutions.`;
                break;
            case 'critical':
                enhanced = `[CRITICAL ANALYSIS] ${enhanced}\n\nIdentify assumptions, challenge premises, and evaluate evidence rigorously.`;
                break;
            case 'strategic':
                enhanced = `[STRATEGIC THINKING] ${enhanced}\n\nConsider long-term implications, resource allocation, and competitive landscape.`;
                break;
        }

        // Add constraints
        if (context.constraints.length > 0) {
            enhanced += `\n\nCONSTRAINTS:\n- ${context.constraints.join('\n- ')}`;
        }

        return enhanced;
    }

    private calculateCost(tokens: number, provider: AIProvider): number {
        const costRates = {
            openmind: 0.00002,
            anthropic: 0.000025,
            openai: 0.00003,
            local: 0
        };
        return tokens * (costRates[provider] || 0);
    }

    async streamResponse(
        session: ChatSession,
        provider: AIProvider,
        onChunk: (chunk: string) => void,
        signal?: AbortSignal
    ): Promise<void> {
        // Implementation for streaming responses
        const response = await this.generateResponse(session, provider, signal);

        // Simulate streaming
        const words = response.content.split(' ');
        for (const word of words) {
            if (signal?.aborted) break;
            onChunk(word + ' ');
            await new Promise(resolve => setTimeout(resolve, 50));
        }
    }
}