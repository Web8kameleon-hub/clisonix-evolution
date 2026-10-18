/**
 * 🌊 FLUID TYPES - TYPE DEFINITIONS FOR FLUID ARCHITECTURE
 * Type definitions për Fluid Architecture Systems
 * 
 * @author Ledjan Ahmati (100% Owner)
 * @contact dealsjona@gmail.com
 * @version 8.0.0-FLUID-TYPES
 * @license MIT
 */

/**
 * 🌊 FLUID CONFIGURATION
 */
export interface FluidConfig {
  adaptiveThreshold: number;
  responsiveBreakpoints: {
    mobile: number;
    tablet: number;
    desktop: number;
    wide: number;
  };
  fluidScaling: {
    minScale: number;
    maxScale: number;
    baseSize: number;
  };
  performanceTargets: {
    renderTime: number;
    layoutShift: number;
    interactionDelay: number;
  };
  enableOptimizations: boolean;
  enableExperiments: boolean;
}

/**
 * 🎯 FLUID COMPONENT
 */
export interface FluidComponent {
  id: string;
  name: string;
  type: 'container' | 'content' | 'navigation' | 'interactive' | 'media';
  responsive: boolean;
  adaptive: boolean;
  fluid: boolean;
  constraints: {
    minWidth?: number;
    maxWidth?: number;
    minHeight?: number;
    maxHeight?: number;
    aspectRatio?: number;
  };
  breakpoints: Record<string, FluidStyles>;
  animations: FluidAnimation[];
  interactions: FluidInteraction[];
  metadata: Record<string, any>;
}

/**
 * 🎨 FLUID STYLES
 */
export interface FluidStyles {
  layout: {
    display?: string;
    position?: string;
    flexDirection?: string;
    justifyContent?: string;
    alignItems?: string;
    gridTemplate?: string;
  };
  spacing: {
    margin?: string | number;
    padding?: string | number;
    gap?: string | number;
  };
  typography: {
    fontSize?: string | number;
    lineHeight?: string | number;
    fontWeight?: string | number;
    letterSpacing?: string | number;
  };
  colors: {
    background?: string;
    color?: string;
    border?: string;
  };
  effects: {
    shadow?: string;
    blur?: string;
    opacity?: number;
    transform?: string;
  };
  custom: Record<string, any>;
}

/**
 * 🎭 FLUID ANIMATION
 */
export interface FluidAnimation {
  id: string;
  name: string;
  type: 'transition' | 'keyframes' | 'spring' | 'physics';
  trigger: 'hover' | 'focus' | 'scroll' | 'resize' | 'load' | 'manual';
  duration: number;
  delay?: number;
  easing: string;
  properties: string[];
  keyframes?: Record<string, FluidStyles>;
  springConfig?: {
    tension: number;
    friction: number;
    mass: number;
  };
  conditions?: {
    mediaQuery?: string;
    device?: string;
    performance?: 'high' | 'medium' | 'low';
  };
}

/**
 * 🖱️ FLUID INTERACTION
 */
export interface FluidInteraction {
  id: string;
  type: 'click' | 'hover' | 'focus' | 'scroll' | 'drag' | 'swipe' | 'pinch';
  target: string;
  action: string;
  feedback: {
    visual?: FluidAnimation;
    haptic?: 'light' | 'medium' | 'heavy';
    audio?: string;
  };
  adaptive: boolean;
  accessibility: {
    label: string;
    description: string;
    keyboardShortcut?: string;
  };
}

/**
 * 📱 FLUID VIEWPORT
 */
export interface FluidViewport {
  width: number;
  height: number;
  pixelRatio: number;
  orientation: 'portrait' | 'landscape';
  breakpoint: 'mobile' | 'tablet' | 'desktop' | 'wide';
  safeAreas: {
    top: number;
    right: number;
    bottom: number;
    left: number;
  };
  capabilities: {
    touch: boolean;
    hover: boolean;
    pointerFine: boolean;
    reducedMotion: boolean;
    highContrast: boolean;
  };
}

/**
 * 🎮 FLUID CONTROLLER
 */
export interface FluidController {
  id: string;
  viewport: FluidViewport;
  components: Map<string, FluidComponent>;
  
  // Lifecycle
  initialize(): Promise<void>;
  destroy(): Promise<void>;
  
  // Component management
  addComponent(component: FluidComponent): void;
  removeComponent(id: string): boolean;
  updateComponent(id: string, updates: Partial<FluidComponent>): void;
  
  // Responsive behavior
  handleResize(viewport: FluidViewport): void;
  handleOrientationChange(orientation: 'portrait' | 'landscape'): void;
  adaptToDevice(capabilities: Partial<FluidViewport['capabilities']>): void;
  
  // Performance
  optimize(): Promise<void>;
  measure(): Promise<FluidMetrics>;
  
  // State
  getState(): FluidState;
  setState(state: Partial<FluidState>): void;
}

/**
 * 📊 FLUID METRICS
 */
export interface FluidMetrics {
  performance: {
    renderTime: number;
    layoutTime: number;
    paintTime: number;
    scriptTime: number;
    totalTime: number;
    frameRate: number;
    memoryUsage: number;
  };
  responsiveness: {
    breakpointTransitions: number;
    adaptiveChanges: number;
    resizeEvents: number;
    orientationChanges: number;
  };
  interactions: {
    clickRate: number;
    hoverRate: number;
    scrollDistance: number;
    gestureCount: number;
  };
  accessibility: {
    keyboardNavigation: number;
    screenReaderUsage: number;
    highContrastUsage: number;
    reducedMotionUsage: number;
  };
  errors: {
    layoutShifts: number;
    renderErrors: number;
    interactionFailures: number;
  };
}

/**
 * 🌊 FLUID STATE
 */
export interface FluidState {
  currentBreakpoint: string;
  viewport: FluidViewport;
  activeComponents: Set<string>;
  runningAnimations: Set<string>;
  performanceMode: 'high' | 'medium' | 'low';
  adaptiveFeatures: {
    enabled: boolean;
    threshold: number;
    adjustments: Record<string, any>;
  };
  experiments: {
    active: Set<string>;
    results: Record<string, any>;
  };
  cache: {
    computedStyles: Map<string, FluidStyles>;
    measurements: Map<string, DOMRect>;
    media: Map<string, boolean>;
  };
}

/**
 * 🔄 FLUID ADAPTATION
 */
export interface FluidAdaptation {
  id: string;
  trigger: 'viewport' | 'performance' | 'network' | 'user' | 'content';
  condition: (state: FluidState) => boolean;
  action: (component: FluidComponent, state: FluidState) => FluidComponent;
  priority: number;
  reversible: boolean;
  metadata: {
    description: string;
    impact: 'low' | 'medium' | 'high';
    compatibility: string[];
  };
}

/**
 * 🧪 FLUID EXPERIMENT
 */
export interface FluidExperiment {
  id: string;
  name: string;
  description: string;
  hypothesis: string;
  variants: {
    id: string;
    name: string;
    changes: Partial<FluidComponent>[];
    weight: number;
  }[];
  metrics: string[];
  duration: number;
  sampleSize: number;
  status: 'draft' | 'running' | 'completed' | 'paused' | 'cancelled';
  results?: {
    variant: string;
    significance: number;
    improvement: number;
    confidence: number;
  };
}

/**
 * 🎯 FLUID OPTIMIZATION
 */
export interface FluidOptimization {
  type: 'layout' | 'animation' | 'interaction' | 'loading' | 'rendering';
  target: string;
  description: string;
  impact: {
    performance: number;
    memory: number;
    bandwidth: number;
    battery: number;
  };
  conditions: string[];
  implementation: (component: FluidComponent) => FluidComponent;
  validation: (metrics: FluidMetrics) => boolean;
}

/**
 * 📱 FLUID DEVICE PROFILE
 */
export interface FluidDeviceProfile {
  id: string;
  name: string;
  category: 'mobile' | 'tablet' | 'desktop' | 'tv' | 'watch' | 'embedded';
  capabilities: {
    screen: {
      width: number;
      height: number;
      pixelRatio: number;
      colorDepth: number;
      refreshRate: number;
    };
    input: {
      touch: boolean;
      mouse: boolean;
      keyboard: boolean;
      stylus: boolean;
      voice: boolean;
    };
    sensors: {
      accelerometer: boolean;
      gyroscope: boolean;
      magnetometer: boolean;
      proximity: boolean;
      light: boolean;
    };
    connectivity: {
      wifi: boolean;
      cellular: boolean;
      bluetooth: boolean;
      nfc: boolean;
    };
    performance: {
      cpu: 'low' | 'medium' | 'high';
      gpu: 'low' | 'medium' | 'high';
      memory: number;
      storage: number;
    };
  };
  adaptations: FluidAdaptation[];
  optimizations: FluidOptimization[];
}

/**
 * 🎨 FLUID THEME
 */
export interface FluidTheme {
  id: string;
  name: string;
  mode: 'light' | 'dark' | 'auto';
  colors: {
    primary: string[];
    secondary: string[];
    neutral: string[];
    success: string[];
    warning: string[];
    error: string[];
  };
  typography: {
    families: string[];
    scales: number[];
    weights: number[];
  };
  spacing: {
    scale: number;
    units: number[];
  };
  shadows: string[];
  borders: {
    radii: number[];
    widths: number[];
  };
  animations: {
    durations: number[];
    easings: string[];
  };
  breakpoints: Record<string, number>;
  fluidScaling: {
    enabled: boolean;
    minScale: number;
    maxScale: number;
  };
}

/**
 * 🌐 FLUID CONTEXT
 */
export interface FluidContext {
  theme: FluidTheme;
  viewport: FluidViewport;
  device: FluidDeviceProfile;
  user: {
    preferences: {
      reducedMotion: boolean;
      highContrast: boolean;
      fontSize: 'small' | 'medium' | 'large';
      theme: 'light' | 'dark' | 'auto';
    };
    accessibility: {
      screenReader: boolean;
      keyboardOnly: boolean;
      voiceControl: boolean;
    };
    behavior: {
      interactionPatterns: string[];
      preferredInputs: string[];
      sessionDuration: number;
    };
  };
  environment: {
    network: {
      type: '2g' | '3g' | '4g' | '5g' | 'wifi' | 'ethernet';
      speed: 'slow' | 'medium' | 'fast';
      saveData: boolean;
    };
    battery: {
      level: number;
      charging: boolean;
      savingMode: boolean;
    };
    location: {
      timeZone: string;
      locale: string;
      region: string;
    };
  };
}

/**
 * 🔌 FLUID PLUGIN
 */
export interface FluidPlugin {
  id: string;
  name: string;
  version: string;
  description: string;
  author: string;
  dependencies: string[];
  
  // Hooks
  onInitialize?: (controller: FluidController) => void;
  onComponentAdd?: (component: FluidComponent) => FluidComponent;
  onComponentUpdate?: (component: FluidComponent) => FluidComponent;
  onViewportChange?: (viewport: FluidViewport) => void;
  onThemeChange?: (theme: FluidTheme) => void;
  onOptimize?: (metrics: FluidMetrics) => FluidOptimization[];
  onDestroy?: () => void;
  
  // Configuration
  config?: Record<string, any>;
  schema?: Record<string, any>;
}

/**
 * 📊 FLUID ANALYTICS
 */
export interface FluidAnalytics {
  sessions: {
    total: number;
    unique: number;
    duration: number;
    bounceRate: number;
  };
  devices: Record<string, number>;
  breakpoints: Record<string, number>;
  interactions: Record<string, number>;
  performance: {
    averageLoadTime: number;
    averageRenderTime: number;
    errorRate: number;
    optimizationImpact: number;
  };
  accessibility: {
    screenReaderUsage: number;
    keyboardNavigation: number;
    highContrastUsage: number;
    reducedMotionUsage: number;
  };
  experiments: Record<string, {
    participants: number;
    conversionRate: number;
    significance: number;
  }>;
}

/**
 * 🎬 FLUID EVENTS
 */
export type FluidEvent = 
  | { type: 'viewport_changed'; data: { viewport: FluidViewport } }
  | { type: 'breakpoint_changed'; data: { from: string; to: string } }
  | { type: 'component_added'; data: { component: FluidComponent } }
  | { type: 'component_removed'; data: { id: string } }
  | { type: 'component_updated'; data: { id: string; changes: Partial<FluidComponent> } }
  | { type: 'animation_started'; data: { id: string; component: string } }
  | { type: 'animation_completed'; data: { id: string; component: string } }
  | { type: 'interaction_triggered'; data: { type: string; component: string } }
  | { type: 'adaptation_applied'; data: { adaptation: FluidAdaptation; component: string } }
  | { type: 'optimization_applied'; data: { optimization: FluidOptimization; component: string } }
  | { type: 'experiment_started'; data: { experiment: FluidExperiment } }
  | { type: 'experiment_completed'; data: { experiment: FluidExperiment; results: unknown } }
  | { type: 'performance_measured'; data: { metrics: FluidMetrics } }
  | { type: 'error_occurred'; data: { error: string; component?: string } };

/**
 * 🏗️ FLUID BUILDER
 */
export interface FluidBuilder {
  reset(): FluidBuilder;
  setConfig(config: Partial<FluidConfig>): FluidBuilder;
  addComponent(component: Partial<FluidComponent>): FluidBuilder;
  setTheme(theme: FluidTheme): FluidBuilder;
  addAdaptation(adaptation: FluidAdaptation): FluidBuilder;
  addOptimization(optimization: FluidOptimization): FluidBuilder;
  addPlugin(plugin: FluidPlugin): FluidBuilder;
  build(): FluidController;
  validate(): boolean;
  preview(): FluidState;
}
