/**
 * AGISheet Type Definitions
 * Të gjitha tipet për AGISheet Kameleon
 */

export type KameleonModeType = 
  | 'analysis'     // Analiza e të dhënave
  | 'decision'     // Vendimmarrje
  | 'planning'     // Planifikim
  | 'control'      // Kontroll operacional
  | 'task'         // Menaxhim detyrash
  | 'admin'        // Administrativ
  | 'industrial'   // Kontroll industrial

export type SecurityLevel = 'basic' | 'standard' | 'high' | 'military'

export interface AGISheetConfig {
  id: string
  name: string
  mode: KameleonModeType
  rows: number
  cols: number
  realTimeUpdates: boolean
  agiIntegration: boolean
  securityLevel: SecurityLevel
}

export interface CellData {
  id: string
  row: number
  col: number
  value: unknown
  formula?: string
  agiBinding?: string
  layerRef?: string
  timestamp: number
  metadata?: Record<string, any>
}

export interface LayerStatus {
  id: string
  name: string
  status: 'active' | 'inactive' | 'processing' | 'error' | 'optimizing' | 'learning'
  load: number
  connections: number
  lastUpdate: number
  errors: string[]
  commands: OperationalCommand[]
}

export interface AGIBindingConfig {
  cellId: string
  layerId: string
  binding: string
  bidirectional: boolean
  autoUpdate: boolean
  transformFunction?: string
}

export interface OperationalCommand {
  id: string
  type: 'layer:control' | 'cell:update' | 'cell:bulk-update' | 'mode:switch' | 'agi:execute'
  source: string
  target: string
  data: Record<string, any>
  timestamp: number
  priority: 'low' | 'normal' | 'high' | 'critical'
}

export interface DecisionChainNode {
  id: string
  layerId: string
  condition: string
  action: string
  nextNode?: string
  metadata: Record<string, any>
}

export interface IndustrialSensor {
  id: string
  type: 'lora' | 'wifi' | 'ethernet' | 'serial'
  location: string
  value: number
  unit: string
  status: 'online' | 'offline' | 'error'
  lastReading: number
}

export interface DashboardWidget {
  id: string
  type: 'chart' | 'gauge' | 'table' | 'map' | 'log' | 'control'
  title: string
  position: { x: number; y: number; width: number; height: number }
  dataSource: string
  config: Record<string, any>
}

export interface AGISheetEvent {
  type: string
  source: string
  data: unknown
  timestamp: number
}

// AGI Integration Types
export interface AGIModule {
  id: string
  name: string
  type: 'mind' | 'sense' | 'planner' | 'response' | 'monitor'
  status: 'active' | 'inactive' | 'error'
  bindable: boolean
  methods: string[]
}

export interface AGIResponse {
  success: boolean
  data: unknown
  error?: string
  timestamp: number
  executionTime: number
}

// Real-time Communication
export interface SocketMessage {
  event: string
  data: unknown
  timestamp: number
  source: string
}

// Export utility types
export type CellAddress = `${string}${number}`;
export type LayerReference = `LAYER_${number}`;
export type CommandPriority = OperationalCommand['priority']
export type ModuleType = AGIModule['type']
