import { EventEmitter } from 'eventemitter3';
import { Observable, Subject, BehaviorSubject } from 'rxjs';
import { z } from 'zod';
import type { 
  AGISheetConfig, 
  CellData, 
  LayerStatus, 
  KameleonModeType,
  OperationalCommand 
} from '../types/index.js';

// Validation schemas
const CellDataSchema = z.object({
  id: z.string(),
  row: z.number(),
  col: z.number(),
  value: z.any(),
  formula: z.string().optional(),
  agiBinding: z.string().optional(),
  layerRef: z.string().optional(),
  timestamp: z.number(),
  metadata: z.record(z.string(), z.any()).optional()
});

const AGISheetConfigSchema = z.object({
  id: z.string(),
  name: z.string(),
  mode: z.enum(['analysis', 'decision', 'planning', 'control', 'task', 'admin', 'industrial']),
  rows: z.number().min(1).max(10000),
  cols: z.number().min(1).max(256),
  realTimeUpdates: z.boolean().default(true),
  agiIntegration: z.boolean().default(true),
  securityLevel: z.enum(['basic', 'standard', 'high', 'military']).default('standard')
});

/**
 * AGISheet Core - Motori kryesor i AGISheet
 * Një Excel me tru AGI që mund të kthehet në çdo gjë
 */
export class AGISheetCore extends EventEmitter {
  private config: AGISheetConfig;
  private cells: Map<string, CellData> = new Map();
  private layers: Map<string, LayerStatus> = new Map();
  private kameleonMode: BehaviorSubject<KameleonModeType>;
  private commandStream: Subject<OperationalCommand> = new Subject();
  private isActive = false;

  constructor(config: Partial<AGISheetConfig> = {}) {
    super();
    
    // Validate and set configuration
    const validatedConfig = AGISheetConfigSchema.parse({
      id: config.id || `agisheet-${Date.now()}`,
      name: config.name || 'AGISheet Kameleon',
      mode: config.mode || 'analysis',
      rows: config.rows || 1000,
      cols: config.cols || 50,
      realTimeUpdates: config.realTimeUpdates ?? true,
      agiIntegration: config.agiIntegration ?? true,
      securityLevel: config.securityLevel || 'standard'
    });

    this.config = validatedConfig;
    this.kameleonMode = new BehaviorSubject(validatedConfig.mode);
    
    this.initializeGrid();
    this.setupEventHandlers();
  }

  /**
   * Inicializimi i grid-it me qeliza të zbrazëta
   */
  private initializeGrid(): void {
    for (let row = 0; row < this.config.rows; row++) {
      for (let col = 0; col < this.config.cols; col++) {
        const cellId = this.getCellId(row, col);
        const cell: CellData = {
          id: cellId,
          row,
          col,
          value: null,
          timestamp: Date.now()
        };
        this.cells.set(cellId, cell);
      }
    }
    
    this.emit('grid:initialized', { 
      rows: this.config.rows, 
      cols: this.config.cols 
    });
  }

  /**
   * Setup event handlers për real-time updates
   */
  private setupEventHandlers(): void {
    // Kameleon mode changes
    this.kameleonMode.subscribe(mode => {
      this.emit('kameleon:modeChanged', { mode, timestamp: Date.now() });
      this.adaptToMode(mode);
    });

    // Command stream processing
    this.commandStream.subscribe(command => {
      this.processCommand(command);
    });
  }

  /**
   * Adaptimi i AGISheet sipas kameleon mode
   */
  private adaptToMode(mode: KameleonModeType): void {
    switch (mode) {
      case 'analysis':
        this.setupAnalysisMode();
        break;
      case 'decision':
        this.setupDecisionMode();
        break;
      case 'planning':
        this.setupPlanningMode();
        break;
      case 'control':
        this.setupControlMode();
        break;
      case 'task':
        this.setupTaskMode();
        break;
      case 'admin':
        this.setupAdminMode();
        break;
      case 'industrial':
        this.setupIndustrialMode();
        break;
    }
  }

  /**
   * Vendosja e vlerës në një qelizë
   */
  setCellValue(row: number, col: number, value: unknown, formula?: string): void {
    const cellId = this.getCellId(row, col);
    const existingCell = this.cells.get(cellId);
    
    if (!existingCell) {
      throw new Error(`Cell ${cellId} does not exist`);
    }

    const updatedCell: CellData = {
      ...existingCell,
      value,
      formula,
      timestamp: Date.now()
    };

    // Validate cell data
    const validatedCell = CellDataSchema.parse(updatedCell);
    this.cells.set(cellId, validatedCell);

    this.emit('cell:updated', { cellId, cell: validatedCell });

    // AGI processing if enabled
    if (this.config.agiIntegration) {
      this.processAGIBinding(validatedCell);
    }
  }

  /**
   * Marrja e vlerës së një qelize
   */
  getCellValue(row: number, col: number): unknown {
    const cellId = this.getCellId(row, col);
    const cell = this.cells.get(cellId);
    return cell?.value || null;
  }

  /**
   * Lidhja e një qelize me AGI layer
   */
  bindCellToAGI(row: number, col: number, layerId: string, binding: string): void {
    const cellId = this.getCellId(row, col);
    const cell = this.cells.get(cellId);
    
    if (!cell) {
      throw new Error(`Cell ${cellId} does not exist`);
    }

    const updatedCell: CellData = {
      ...cell,
      agiBinding: binding,
      layerRef: layerId,
      timestamp: Date.now()
    };

    this.cells.set(cellId, updatedCell);
    this.emit('agi:cellBound', { cellId, layerId, binding });
  }

  /**
   * Ndryshimi i kameleon mode
   */
  switchKameleonMode(mode: KameleonModeType): void {
    this.kameleonMode.next(mode);
  }

  /**
   * Dërgimi i komandës operacionale
   */
  sendCommand(command: OperationalCommand): void {
    this.commandStream.next(command);
  }

  /**
   * Aktivizimi i AGISheet
   */
  activate(): void {
    this.isActive = true;
    this.emit('agisheet:activated', { timestamp: Date.now() });
  }

  /**
   * Çaktivizimi i AGISheet
   */
  deactivate(): void {
    this.isActive = false;
    this.emit('agisheet:deactivated', { timestamp: Date.now() });
  }

  // Private helper methods
  private getCellId(row: number, col: number): string {
    return `${String.fromCharCode(65 + col)}${row + 1}`;
  }

  private processAGIBinding(cell: CellData): void {
    if (cell.agiBinding && cell.layerRef) {
      this.emit('agi:processBinding', {
        cellId: cell.id,
        binding: cell.agiBinding,
        layerId: cell.layerRef,
        value: cell.value
      });
    }
  }

  private processCommand(command: OperationalCommand): void {
    this.emit('command:received', command);
    
    switch (command.type) {
      case 'layer:control':
        this.handleLayerCommand(command);
        break;
      case 'cell:bulk-update':
        this.handleBulkUpdate(command);
        break;
      case 'mode:switch':
        this.switchKameleonMode(command.data.mode);
        break;
      default:
        this.emit('command:unknown', command);
    }
  }

  private handleLayerCommand(command: OperationalCommand): void {
    // Implementation for layer control commands
    this.emit('layer:commandProcessed', command);
  }

  private handleBulkUpdate(command: OperationalCommand): void {
    // Implementation for bulk cell updates
    this.emit('cells:bulkUpdated', command);
  }

  // Kameleon mode setup methods
  private setupAnalysisMode(): void {
    // Configure for data analysis
    this.emit('mode:analysis:setup');
  }

  private setupDecisionMode(): void {
    // Configure for decision making
    this.emit('mode:decision:setup');
  }

  private setupPlanningMode(): void {
    // Configure for planning tasks
    this.emit('mode:planning:setup');
  }

  private setupControlMode(): void {
    // Configure for operational control
    this.emit('mode:control:setup');
  }

  private setupTaskMode(): void {
    // Configure for task management
    this.emit('mode:task:setup');
  }

  private setupAdminMode(): void {
    // Configure for administrative tasks
    this.emit('mode:admin:setup');
  }

  private setupIndustrialMode(): void {
    // Configure for industrial control
    this.emit('mode:industrial:setup');
  }

  // Getters
  get currentMode(): KameleonModeType {
    return this.kameleonMode.value;
  }

  get isActiveSheet(): boolean {
    return this.isActive;
  }

  get cellCount(): number {
    return this.cells.size;
  }

  get configuration(): AGISheetConfig {
    return { ...this.config };
  }
}
