/**
 * EuroWeb AGI Types - Type definitions për arkitekturën modulare
 * @module AGI-Types
 * @author EuroWeb Development Team
 * @version 8.0.0 Industrial
 */

// Core AGI Module Types
export interface AGIModule {
  id: string;
  name: string;
  type: 'mind' | 'sense' | 'planner' | 'response' | 'monitor' | 'orchestrator';
  status: 'active' | 'inactive' | 'processing' | 'error' | 'optimizing' | 'learning';
  execute: (params: AGIExecutionParams) => Promise<AGIExecutionResult>;
  validate: () => boolean;
  getMetrics: () => AGIModuleMetrics;
}

export interface AGIExecutionParams {
  route?: string;
  params?: Record<string, any>;
  timestamp: number;
  layer?: number;
  context?: IntelliContext;
}

export interface AGIExecutionResult {
  success: boolean;
  result?: any;
  error?: string;
  duration: number;
  timestamp: number;
}

export interface AGIModuleMetrics {
  load: number;
  connections: number;
  processed: number;
  errors: number;
  lastUpdate: number;
}

// EuroWeb Specific Types
export interface EuroWebConfig {
  web8Mode: boolean;
  agiEnabled: boolean;
  moduleCount: number;
  securityLevel: 'standard' | 'high' | 'military' | 'post-quantum';
  realTimeUpdates: boolean;
  meshNetworking: boolean;
  ddosProtection: boolean;
}

export interface Web8NavigationParams {
  url: string;
  layer: number;
  method: 'agi-guided' | 'traditional' | 'mesh-assisted';
  security: boolean;
  trace: SignalTrace;
}

// Signal Trace System
export class SignalTrace {
  public id: string;
  public steps: SignalStep[] = [];
  public startTime: number;
  public endTime?: number;

  constructor(id: string) {
    this.id = id;
    this.startTime = Date.now();
  }

  public addStep(action: string, data?: any): void {
    this.steps.push({
      action,
      data,
      timestamp: Date.now(),
      duration: Date.now() - this.startTime
    });
  }

  public complete(): void {
    this.endTime = Date.now();
  }

  public getDuration(): number {
    return (this.endTime || Date.now()) - this.startTime;
  }
}

export interface SignalStep {
  action: string;
  data?: any;
  timestamp: number;
  duration: number;
}

// Intelligence Context
export class IntelliContext {
  private traces: Map<string, SignalTrace> = new Map();
  private memory: Map<string, any> = new Map();
  private startTime: number = Date.now();

  public addTrace(trace: SignalTrace): void {
    this.traces.set(trace.id, trace);
  }

  public getTrace(id: string): SignalTrace | undefined {
    return this.traces.get(id);
  }

  public store(key: string, value: any): void {
    this.memory.set(key, {
      value,
      timestamp: Date.now()
    });
  }

  public retrieve(key: string): any {
    const item = this.memory.get(key);
    return item ? item.value : undefined;
  }

  public getMetrics(): IntelliContextMetrics {
    return {
      traces: this.traces.size,
      memoryItems: this.memory.size,
      uptime: Date.now() - this.startTime,
      lastActivity: Math.max(...Array.from(this.traces.values()).map(t => t.startTime))
    };
  }
}

export interface IntelliContextMetrics {
  traces: number;
  memoryItems: number;
  uptime: number;
  lastActivity: number;
}

// Memory Layer
export class MemoryLayer {
  private shortTerm: Map<string, MemoryItem> = new Map();
  private longTerm: Map<string, MemoryItem> = new Map();
  private maxShortTerm = 1000;
  private maxLongTerm = 10000;

  public store(key: string, value: any, persistent = false): void {
    const item: MemoryItem = {
      value,
      timestamp: Date.now(),
      accessCount: 0,
      persistent
    };

    if (persistent) {
      this.longTerm.set(key, item);
      this.cleanupLongTerm();
    } else {
      this.shortTerm.set(key, item);
      this.cleanupShortTerm();
    }
  }

  public retrieve(key: string): any {
    const item = this.shortTerm.get(key) || this.longTerm.get(key);
    if (item) {
      item.accessCount++;
      item.lastAccess = Date.now();
      return item.value;
    }
    return undefined;
  }

  public getMetrics(): MemoryLayerMetrics {
    return {
      shortTermCount: this.shortTerm.size,
      longTermCount: this.longTerm.size,
      totalMemory: this.shortTerm.size + this.longTerm.size,
      maxShortTerm: this.maxShortTerm,
      maxLongTerm: this.maxLongTerm
    };
  }

  private cleanupShortTerm(): void {
    if (this.shortTerm.size > this.maxShortTerm) {
      const entries = Array.from(this.shortTerm.entries());
      entries.sort((a, b) => a[1].timestamp - b[1].timestamp);
      const toRemove = entries.slice(0, entries.length - this.maxShortTerm);
      toRemove.forEach(([key]) => this.shortTerm.delete(key));
    }
  }

  private cleanupLongTerm(): void {
    if (this.longTerm.size > this.maxLongTerm) {
      const entries = Array.from(this.longTerm.entries());
      entries.sort((a, b) => (a[1].lastAccess || 0) - (b[1].lastAccess || 0));
      const toRemove = entries.slice(0, entries.length - this.maxLongTerm);
      toRemove.forEach(([key]) => this.longTerm.delete(key));
    }
  }
}

export interface MemoryItem {
  value: any;
  timestamp: number;
  accessCount: number;
  lastAccess?: number;
  persistent: boolean;
}

export interface MemoryLayerMetrics {
  shortTermCount: number;
  longTermCount: number;
  totalMemory: number;
  maxShortTerm: number;
  maxLongTerm: number;
}

// Orchestrated Routing Types
export interface OrchestrationParams {
  route: string;
  method: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
  params: Record<string, any>;
  headers?: Record<string, string>;
  metadata?: Record<string, any>;
  agiGuided?: boolean;
  layer?: number;
}

export interface OrchestrationResult {
  success: boolean;
  data?: any;
  error?: string;
  duration: number;
  route: string;
  timestamp: number;
  trace?: SignalTrace;
}

// Layer Control Types
export interface LayerControl {
  id: string;
  name: string;
  active: boolean;
  load: number;
  connections: number;
  type: 'perception' | 'processing' | 'decision' | 'execution' | 'learning' | 'memory' | 'integration';
  modules: AGIModule[];
}

// All types are already exported above
