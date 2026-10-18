/**
 * 🧠 NEURAL TYPES - TYPE DEFINITIONS FOR NEURAL SYSTEMS
 * Type definitions për sistemet Neural dhe AI
 * 
 * @author Ledjan Ahmati (100% Owner)
 * @contact dealsjona@gmail.com
 * @version 8.0.0-NEURAL-TYPES
 * @license MIT
 */

/**
 * 🎯 NEURAL CONFIGURATION
 */
export interface NeuralConfig {
  learningRate: number;
  epochs: number;
  batchSize: number;
  hiddenLayers: number[];
  activationFunction: 'relu' | 'sigmoid' | 'tanh' | 'leaky_relu';
  optimizer: 'adam' | 'sgd' | 'rmsprop';
  lossFunction: 'mse' | 'categorical_crossentropy' | 'binary_crossentropy';
  regularization?: {
    l1?: number;
    l2?: number;
    dropout?: number;
  };
  earlyStopping?: {
    patience: number;
    minDelta: number;
    monitor: 'loss' | 'accuracy' | 'val_loss' | 'val_accuracy';
  };
}

/**
 * 🧠 NEURAL NETWORK ARCHITECTURE
 */
export interface NeuralArchitecture {
  id: string;
  name: string;
  type: 'feedforward' | 'cnn' | 'rnn' | 'lstm' | 'transformer';
  layers: NeuralLayer[];
  inputShape: number[];
  outputShape: number[];
  parameters: number;
  flops: number;
  memoryUsage: number;
  createdAt: Date;
  updatedAt: Date;
}

/**
 * 🎛️ NEURAL LAYER
 */
export interface NeuralLayer {
  id: string;
  type: 'dense' | 'conv2d' | 'maxpool2d' | 'dropout' | 'batch_norm' | 'activation';
  name: string;
  inputShape: number[];
  outputShape: number[];
  parameters: number;
  config: Record<string, any>;
  weights?: number[][];
  biases?: number[];
  activation?: string;
  trainable: boolean;
}

/**
 * 📊 TRAINING METRICS
 */
export interface TrainingMetrics {
  epoch: number;
  loss: number;
  accuracy: number;
  valLoss?: number;
  valAccuracy?: number;
  learningRate: number;
  batchSize: number;
  duration: number;
  memoryUsage: number;
  timestamp: Date;
}

/**
 * 🎯 TRAINING SESSION
 */
export interface TrainingSession {
  id: string;
  modelId: string;
  config: NeuralConfig;
  startTime: Date;
  endTime?: Date;
  status: 'pending' | 'training' | 'completed' | 'failed' | 'stopped';
  metrics: TrainingMetrics[];
  bestMetrics: TrainingMetrics;
  totalEpochs: number;
  currentEpoch: number;
  estimatedTimeRemaining?: number;
  error?: string;
}

/**
 * 🧮 NEURAL COMPUTATION
 */
export interface NeuralComputation {
  forward: (input: number[]) => number[];
  backward: (gradient: number[]) => number[];
  updateWeights: (gradients: number[], learningRate: number) => void;
  getWeights: () => number[][];
  setWeights: (weights: number[][]) => void;
  getParameters: () => number;
  clone: () => NeuralComputation;
}

/**
 * 🎨 ACTIVATION FUNCTIONS
 */
export type ActivationFunction = {
  forward: (x: number) => number;
  backward: (x: number) => number;
  name: string;
};

/**
 * 📈 OPTIMIZER STATE
 */
export interface OptimizerState {
  type: 'adam' | 'sgd' | 'rmsprop';
  learningRate: number;
  momentum?: number;
  beta1?: number;
  beta2?: number;
  epsilon?: number;
  decay?: number;
  iterations: number;
  gradients: Record<string, number[]>;
  velocities?: Record<string, number[]>;
  moments?: Record<string, number[]>;
}

/**
 * 📊 MODEL PERFORMANCE
 */
export interface ModelPerformance {
  accuracy: number;
  precision: number;
  recall: number;
  f1Score: number;
  confusionMatrix: number[][];
  roc: {
    fpr: number[];
    tpr: number[];
    auc: number;
  };
  loss: number;
  inferenceTime: number;
  memoryFootprint: number;
  flops: number;
}

/**
 * 🔮 PREDICTION RESULT
 */
export interface PredictionResult {
  predictions: number[];
  probabilities: number[];
  confidence: number;
  uncertainty?: number;
  explanations?: string[];
  metadata: {
    modelId: string;
    timestamp: Date;
    inferenceTime: number;
    batchSize: number;
  };
}

/**
 * 🧠 NEURAL PLANNER INTERFACE
 */
export interface INeuralPlanner {
  id: string;
  name: string;
  version: string;
  architecture: NeuralArchitecture;
  config: NeuralConfig;
  isTraining: boolean;
  isTrained: boolean;
  
  // Core methods
  initialize(): Promise<void>;
  train(data: TrainingData): Promise<TrainingSession>;
  predict(input: number[]): Promise<PredictionResult>;
  evaluate(testData: TestData): Promise<ModelPerformance>;
  
  // Model management
  save(path: string): Promise<void>;
  load(path: string): Promise<void>;
  clone(): INeuralPlanner;
  
  // Configuration
  updateConfig(config: Partial<NeuralConfig>): void;
  getConfig(): NeuralConfig;
  
  // Monitoring
  getMetrics(): TrainingMetrics[];
  getPerformance(): ModelPerformance;
  getStatus(): string;
}

/**
 * 📚 TRAINING DATA
 */
export interface TrainingData {
  inputs: number[][];
  outputs: number[][];
  validation?: {
    inputs: number[][];
    outputs: number[][];
  };
  metadata?: {
    name: string;
    description: string;
    size: number;
    features: string[];
    preprocessing: string[];
  };
}

/**
 * 🧪 TEST DATA
 */
export interface TestData {
  inputs: number[][];
  outputs: number[][];
  metadata?: {
    name: string;
    description: string;
    size: number;
  };
}

/**
 * 🔧 HYPERPARAMETER TUNING
 */
export interface HyperparameterSpace {
  learningRate: {
    min: number;
    max: number;
    scale: 'linear' | 'log';
  };
  batchSize: number[];
  hiddenLayers: number[][];
  dropout: {
    min: number;
    max: number;
  };
  optimizer: ('adam' | 'sgd' | 'rmsprop')[];
  activationFunction: ('relu' | 'sigmoid' | 'tanh')[];
}

/**
 * 🎯 HYPERPARAMETER TRIAL
 */
export interface HyperparameterTrial {
  id: string;
  parameters: Record<string, any>;
  score: number;
  metrics: ModelPerformance;
  duration: number;
  status: 'pending' | 'running' | 'completed' | 'failed';
  startTime: Date;
  endTime?: Date;
  error?: string;
}

/**
 * 🏆 HYPERPARAMETER TUNING RESULT
 */
export interface TuningResult {
  bestTrial: HyperparameterTrial;
  allTrials: HyperparameterTrial[];
  bestParameters: Record<string, any>;
  bestScore: number;
  totalTrials: number;
  completedTrials: number;
  duration: number;
  convergenceHistory: number[];
}

/**
 * 🧠 NEURAL MEMORY
 */
export interface NeuralMemory {
  shortTerm: {
    capacity: number;
    entries: Map<string, any>;
    accessCount: Map<string, number>;
  };
  longTerm: {
    capacity: number;
    entries: Map<string, any>;
    importance: Map<string, number>;
  };
  workingMemory: {
    currentContext: unknown;
    activePatterns: Set<string>;
    attention: Map<string, number>;
  };
}

/**
 * 🔍 ATTENTION MECHANISM
 */
export interface AttentionWeights {
  query: number[];
  key: number[];
  value: number[];
  weights: number[][];
  output: number[];
  heads: number;
  dimensions: number;
}

/**
 * 🌊 NEURAL FLOW STATE
 */
export interface NeuralFlowState {
  id: string;
  timestamp: Date;
  activations: Map<string, number[]>;
  gradients: Map<string, number[]>;
  attention: AttentionWeights[];
  memory: NeuralMemory;
  context: unknown;
  metadata: Record<string, any>;
}

/**
 * 📡 NEURAL COMMUNICATION
 */
export interface NeuralMessage {
  id: string;
  from: string;
  to: string;
  type: 'activation' | 'gradient' | 'weight_update' | 'sync' | 'control';
  payload: unknown;
  priority: 'low' | 'normal' | 'high' | 'critical';
  timestamp: Date;
  metadata?: Record<string, any>;
}

/**
 * 🎮 NEURAL CONTROLLER
 */
export interface NeuralController {
  id: string;
  planners: Map<string, INeuralPlanner>;
  
  // Lifecycle
  initialize(): Promise<void>;
  shutdown(): Promise<void>;
  
  // Planner management
  addPlanner(planner: INeuralPlanner): void;
  removePlanner(id: string): boolean;
  getPlanner(id: string): INeuralPlanner | undefined;
  
  // Coordination
  orchestrate(task: unknown): Promise<any>;
  balance(): Promise<void>;
  sync(): Promise<void>;
  
  // Monitoring
  getStatus(): Record<string, any>;
  getMetrics(): Record<string, any>;
  healthCheck(): Promise<boolean>;
}

/**
 * 🎯 NEURAL EVENTS
 */
export type NeuralEvent = 
  | { type: 'training_started'; data: { sessionId: string; modelId: string } }
  | { type: 'training_completed'; data: { sessionId: string; metrics: ModelPerformance } }
  | { type: 'training_failed'; data: { sessionId: string; error: string } }
  | { type: 'epoch_completed'; data: { sessionId: string; epoch: number; metrics: TrainingMetrics } }
  | { type: 'prediction_made'; data: { modelId: string; result: PredictionResult } }
  | { type: 'model_saved'; data: { modelId: string; path: string } }
  | { type: 'model_loaded'; data: { modelId: string; path: string } }
  | { type: 'weights_updated'; data: { modelId: string; layerId: string } }
  | { type: 'optimization_step'; data: { modelId: string; step: number; loss: number } };

/**
 * 🎭 NEURAL PATTERNS
 */
export interface NeuralPattern {
  id: string;
  name: string;
  description: string;
  type: 'classification' | 'regression' | 'generation' | 'detection' | 'clustering';
  input: {
    shape: number[];
    type: 'image' | 'text' | 'audio' | 'numeric' | 'categorical';
    preprocessing: string[];
  };
  output: {
    shape: number[];
    type: 'classification' | 'regression' | 'generation';
    postprocessing: string[];
  };
  architecture: string;
  complexity: 'simple' | 'medium' | 'complex' | 'very_complex';
  computationalCost: number;
  accuracy: number;
  trainable: boolean;
}

/**
 * 🏗️ NEURAL BUILDER
 */
export interface NeuralBuilder {
  reset(): NeuralBuilder;
  addLayer(layer: Partial<NeuralLayer>): NeuralBuilder;
  setConfig(config: Partial<NeuralConfig>): NeuralBuilder;
  setOptimizer(optimizer: OptimizerState): NeuralBuilder;
  compile(): INeuralPlanner;
  validate(): boolean;
  estimateComplexity(): number;
  getArchitecture(): NeuralArchitecture;
}

/**
 * 📊 NEURAL ANALYTICS
 */
export interface NeuralAnalytics {
  totalModels: number;
  activeSessions: number;
  averageAccuracy: number;
  totalPredictions: number;
  computeUtilization: number;
  memoryUtilization: number;
  errorRate: number;
  performanceTrends: {
    accuracy: number[];
    loss: number[];
    trainingTime: number[];
    timestamps: Date[];
  };
  modelDistribution: Record<string, number>;
  usagePatterns: Record<string, number>;
}
