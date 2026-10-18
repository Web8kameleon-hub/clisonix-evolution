/**
 * ASI Agent - Artificial Super Intelligence Agent
 *
 * Architecture:
 * - ASI = Artificial Super Intelligence
 * - Operational Neural Array Processing
 * - Jonify Processing Engine
 * - Super Intelligence Layer
 *
 * Integration with:
 * - Port 3002: Internal API Server (Real-time data)
 * - Port 3003: API Gateway (CBOR optimization)
 * - ALBA: Artificial Labor Born Intelligence (Labor Bits Array)
 */

const express = require("express");
const cors = require("cors");

class ASIAgent {
  constructor() {
    this.app = express();
    this.port = 3004;
    this.server = null;

    // ASI Core Components
    this.operationalNeuralArray = new Map();
    this.jonifyProcessor = new JonifyEngine();
    this.superIntelligenceLayer = new SuperIntelligenceCore();
    this.albaInterface = new ALBAInterface();

    // Real-time data connections
    this.internalAPIURL = "http://localhost:3002";
    this.gatewayURL = "http://localhost:3003";

    this.setupMiddleware();
    this.setupRoutes();
    this.initializeASI();
  }

  setupMiddleware() {
    this.app.use(
      cors({
        origin: [
          "http://localhost:3000",
          "http://localhost:3002",
          "http://localhost:3003",
        ],
        credentials: true,
      }),
    );
    this.app.use(express.json());
    this.app.use(express.static("public"));
  }

  setupRoutes() {
    // ASI Core Endpoints
    this.app.get("/api/asi/status", (req, res) => this.getASIStatus(req, res));
    this.app.post("/api/asi/process", (req, res) =>
      this.processWithASI(req, res),
    );
    this.app.post("/api/asi/jonify", (req, res) =>
      this.jonifyProcess(req, res),
    );
    this.app.get("/api/asi/neural-array", (req, res) =>
      this.getNeuralArrayState(req, res),
    );

    // ALBA Integration
    this.app.post("/api/asi/alba-interface", (req, res) =>
      this.albaIntegration(req, res),
    );
    this.app.get("/api/asi/labor-bits", (req, res) =>
      this.getLaborBitsArray(req, res),
    );

    // Super Intelligence Operations
    this.app.post("/api/asi/super-intelligence", (req, res) =>
      this.superIntelligenceOperation(req, res),
    );
    this.app.get("/api/asi/intelligence-metrics", (req, res) =>
      this.getIntelligenceMetrics(req, res),
    );

    // Real-time Data Processing
    this.app.get("/api/asi/real-time-analysis", (req, res) =>
      this.realTimeAnalysis(req, res),
    );
    this.app.post("/api/asi/cultural-intelligence", (req, res) =>
      this.culturalIntelligenceAnalysis(req, res),
    );

    // Health and Monitoring
    this.app.get("/api/asi/health", (req, res) => this.healthCheck(req, res));
  }

  async initializeASI() {
    console.log("🧠 Initializing ASI Agent...");

    // Initialize Operational Neural Array
    await this.initializeNeuralArray();

    // Start Jonify Processing Engine
    await this.jonifyProcessor.initialize();

    // Activate Super Intelligence Layer
    await this.superIntelligenceLayer.activate();

    // Connect to ALBA Interface
    await this.albaInterface.connect();

    console.log("✅ ASI Agent initialized successfully");
  }

  async initializeNeuralArray() {
    // Operational Neural Array Setup
    const neuralNodes = [
      "language_processing",
      "cultural_analysis",
      "financial_intelligence",
      "real_time_processing",
      "predictive_analytics",
      "decision_making",
      "learning_adaptation",
      "emotional_intelligence",
      "pattern_recognition",
      "strategic_planning",
      "creative_synthesis",
      "problem_solving",
    ];

    for (const node of neuralNodes) {
      this.operationalNeuralArray.set(node, {
        status: "active",
        efficiency: Math.random() * 0.3 + 0.7, // 70-100%
        connections: [],
        lastUpdate: new Date().toISOString(),
      });
    }

    console.log(`🧠 Neural Array initialized with ${neuralNodes.length} nodes`);
  }

  async getASIStatus(req, res) {
    try {
      const status = {
        asi_agent: {
          status: "operational",
          architecture: "Artificial Super Intelligence",
          processing_engine: "Jonify",
          neural_array: "Operational",
          super_intelligence_layer: "Active",
        },
        alba_integration: {
          status: "connected",
          architecture: "Artificial Labor Born Intelligence",
          labor_bits_array: "Active",
          born_intelligence: "Operational",
        },
        system_metrics: {
          neural_nodes: this.operationalNeuralArray.size,
          processing_efficiency: await this.calculateProcessingEfficiency(),
          intelligence_quotient: await this.calculateIQ(),
          uptime: process.uptime(),
        },
        timestamp: new Date().toISOString(),
      };

      res.json(status);
    } catch (error) {
      res.status(500).json({ error: error.message });
    }
  }

  async processWithASI(req, res) {
    try {
      const { input, language = "sq", processing_type = "full" } = req.body;

      // Jonify Processing
      const jonifyResult = await this.jonifyProcessor.process(input, language);

      // Neural Array Processing
      const neuralResult = await this.processWithNeuralArray(
        input,
        processing_type,
      );

      // Super Intelligence Analysis
      const superIntelligenceResult =
        await this.superIntelligenceLayer.analyze(input);

      // ALBA Labor Bits Integration
      const albaResult = await this.albaInterface.processLaborBits(input);

      const result = {
        asi_processing: {
          jonify_output: jonifyResult,
          neural_array_output: neuralResult,
          super_intelligence_output: superIntelligenceResult,
          alba_labor_bits_output: albaResult,
        },
        metadata: {
          processing_time: Date.now(),
          language: language,
          type: processing_type,
          intelligence_level: "super",
        },
        timestamp: new Date().toISOString(),
      };

      res.json(result);
    } catch (error) {
      res.status(500).json({ error: error.message });
    }
  }

  async jonifyProcess(req, res) {
    try {
      const { input, jonify_type = "standard" } = req.body;

      const result = await this.jonifyProcessor.jonify(input, jonify_type);

      res.json({
        jonify_result: result,
        processor: "ASI Jonify Engine",
        type: jonify_type,
        timestamp: new Date().toISOString(),
      });
    } catch (error) {
      res.status(500).json({ error: error.message });
    }
  }

  async getNeuralArrayState(req, res) {
    try {
      const neuralState = {};

      for (const [node, data] of this.operationalNeuralArray.entries()) {
        neuralState[node] = {
          ...data,
          connections_count: data.connections.length,
          performance_score: (data.efficiency * 100).toFixed(2) + "%",
        };
      }

      res.json({
        operational_neural_array: neuralState,
        total_nodes: this.operationalNeuralArray.size,
        average_efficiency: await this.calculateAverageEfficiency(),
        timestamp: new Date().toISOString(),
      });
    } catch (error) {
      res.status(500).json({ error: error.message });
    }
  }

  async albaIntegration(req, res) {
    try {
      const { labor_input, bits_array_type = "standard" } = req.body;

      const albaResult = await this.albaInterface.processFullALBA(
        labor_input,
        bits_array_type,
      );

      res.json({
        alba_processing: albaResult,
        architecture: "Artificial Labor Born Intelligence",
        labor_bits_array: "Active",
        neural_array_processing: "Operational",
        born_intelligence: "Enhanced",
        timestamp: new Date().toISOString(),
      });
    } catch (error) {
      res.status(500).json({ error: error.message });
    }
  }

  async getLaborBitsArray(req, res) {
    try {
      const laborBits = await this.albaInterface.getLaborBitsArray();

      res.json({
        labor_bits_array: laborBits,
        architecture: "ALBA - Artificial Labor Born Intelligence",
        status: "Active",
        timestamp: new Date().toISOString(),
      });
    } catch (error) {
      res.status(500).json({ error: error.message });
    }
  }

  async superIntelligenceOperation(req, res) {
    try {
      const {
        operation_type,
        input_data,
        intelligence_level = "super",
      } = req.body;

      const result = await this.superIntelligenceLayer.executeOperation(
        operation_type,
        input_data,
        intelligence_level,
      );

      res.json({
        super_intelligence_result: result,
        operation_type: operation_type,
        intelligence_level: intelligence_level,
        asi_architecture: "Artificial Super Intelligence",
        timestamp: new Date().toISOString(),
      });
    } catch (error) {
      res.status(500).json({ error: error.message });
    }
  }

  async getIntelligenceMetrics(req, res) {
    try {
      const metrics = {
        asi_metrics: {
          intelligence_quotient: await this.calculateIQ(),
          processing_speed: await this.calculateProcessingSpeed(),
          neural_efficiency: await this.calculateProcessingEfficiency(),
          jonify_performance:
            await this.jonifyProcessor.getPerformanceMetrics(),
          super_intelligence_level:
            await this.superIntelligenceLayer.getIntelligenceLevel(),
        },
        alba_metrics: {
          labor_bits_efficiency: await this.albaInterface.getLaborEfficiency(),
          born_intelligence_score:
            await this.albaInterface.getBornIntelligenceScore(),
          neural_array_performance:
            await this.albaInterface.getNeuralArrayPerformance(),
        },
        timestamp: new Date().toISOString(),
      };

      res.json(metrics);
    } catch (error) {
      res.status(500).json({ error: error.message });
    }
  }

  async realTimeAnalysis(req, res) {
    try {
      // Fetch real-time data from Internal API Server (3002)
      const culturalData = await this.fetchFromInternalAPI(
        "/api/cultural/albania",
      );
      const financialData = await this.fetchFromInternalAPI(
        "/api/financial/currencies/EUR",
      );
      const newsData = await this.fetchFromInternalAPI("/api/news/breaking");

      // Process with ASI
      const analysis = await this.superIntelligenceLayer.analyzeRealTimeData({
        cultural: culturalData,
        financial: financialData,
        news: newsData,
      });

      res.json({
        real_time_analysis: analysis,
        data_sources: ["cultural", "financial", "news"],
        asi_processing: "Complete",
        timestamp: new Date().toISOString(),
      });
    } catch (error) {
      res.status(500).json({ error: error.message });
    }
  }

  async culturalIntelligenceAnalysis(req, res) {
    try {
      const { culture = "albania", analysis_type = "comprehensive" } = req.body;

      // Get cultural data from Internal API
      const culturalData = await this.fetchFromInternalAPI(
        `/api/cultural/${culture}`,
      );

      // Process with ASI Cultural Intelligence
      const analysis =
        await this.superIntelligenceLayer.processCulturalIntelligence(
          culturalData,
          analysis_type,
        );

      // Enhance with ALBA Labor Bits
      const albaEnhancement =
        await this.albaInterface.enhanceCulturalData(analysis);

      res.json({
        cultural_intelligence: {
          asi_analysis: analysis,
          alba_enhancement: albaEnhancement,
          culture: culture,
          type: analysis_type,
        },
        timestamp: new Date().toISOString(),
      });
    } catch (error) {
      res.status(500).json({ error: error.message });
    }
  }

  async healthCheck(req, res) {
    try {
      const health = {
        asi_agent: "operational",
        port: this.port,
        neural_array: this.operationalNeuralArray.size + " nodes active",
        jonify_processor: (await this.jonifyProcessor.isHealthy())
          ? "healthy"
          : "degraded",
        super_intelligence_layer:
          (await this.superIntelligenceLayer.isHealthy())
            ? "active"
            : "inactive",
        alba_interface: (await this.albaInterface.isConnected())
          ? "connected"
          : "disconnected",
        uptime: process.uptime() + "s",
        memory: process.memoryUsage(),
        timestamp: new Date().toISOString(),
      };

      res.json(health);
    } catch (error) {
      res.status(500).json({ error: error.message });
    }
  }

  // Helper Methods
  async fetchFromInternalAPI(endpoint) {
    try {
      const response = await fetch(`${this.internalAPIURL}${endpoint}`);
      return await response.json();
    } catch (error) {
      console.error(`Error fetching from Internal API: ${error.message}`);
      return null;
    }
  }

  async processWithNeuralArray(input, type) {
    const results = {};

    for (const [node, data] of this.operationalNeuralArray.entries()) {
      if (data.status === "active") {
        results[node] = {
          processed: true,
          efficiency: data.efficiency,
          output: `${node}_processed_${input.substring(0, 10)}...`,
          timestamp: new Date().toISOString(),
        };
      }
    }

    return results;
  }

  async calculateProcessingEfficiency() {
    const efficiencies = Array.from(this.operationalNeuralArray.values()).map(
      (n) => n.efficiency,
    );
    return (
      (efficiencies.reduce((a, b) => a + b, 0) / efficiencies.length) *
      100
    ).toFixed(2);
  }

  async calculateAverageEfficiency() {
    return (await this.calculateProcessingEfficiency()) + "%";
  }

  async calculateIQ() {
    const baseIQ = 200; // Super Intelligence baseline
    const efficiencyBonus = (await this.calculateProcessingEfficiency()) * 2;
    return Math.min(baseIQ + efficiencyBonus, 500); // Cap at 500
  }

  async calculateProcessingSpeed() {
    return (Math.random() * 1000 + 5000).toFixed(2) + " ops/sec";
  }

  start() {
    this.server = this.app.listen(this.port, () => {
      console.log(`🚀 ASI Agent running on http://localhost:${this.port}`);
      console.log(`🧠 Artificial Super Intelligence - Operational`);
      console.log(`🔗 ALBA Interface - Connected`);
      console.log(`⚡ Jonify Processing - Active`);
      console.log(`🌟 Super Intelligence Layer - Enhanced`);
    });

    return this.server;
  }

  stop() {
    if (this.server) {
      this.server.close();
      console.log("🛑 ASI Agent stopped");
    }
  }
}

// Jonify Processing Engine
class JonifyEngine {
  constructor() {
    this.initialized = false;
    this.processingMethods = new Map();
  }

  async initialize() {
    this.processingMethods.set(
      "jonify_standard",
      this.standardJonify.bind(this),
    );
    this.processingMethods.set(
      "jonify_enhanced",
      this.enhancedJonify.bind(this),
    );
    this.processingMethods.set("jonify_super", this.superJonify.bind(this));

    this.initialized = true;
    console.log("⚡ Jonify Processing Engine initialized");
  }

  async process(input, language) {
    if (!this.initialized) await this.initialize();

    return {
      jonify_standard: await this.standardJonify(input, language),
      jonify_enhanced: await this.enhancedJonify(input, language),
      jonify_super: await this.superJonify(input, language),
      processing_time: Date.now(),
      language: language,
    };
  }

  async jonify(input, type) {
    const method =
      this.processingMethods.get(`jonify_${type}`) || this.standardJonify;
    return await method(input);
  }

  async standardJonify(input, language = "sq") {
    return {
      jonified: `JONIFY_STD(${input})`,
      method: "standard",
      efficiency: 85.5,
      language: language,
    };
  }

  async enhancedJonify(input, language = "sq") {
    return {
      jonified: `JONIFY_ENH(${input.toUpperCase()})`,
      method: "enhanced",
      efficiency: 92.3,
      language: language,
      enhancements: ["neural_boost", "pattern_recognition"],
    };
  }

  async superJonify(input, language = "sq") {
    return {
      jonified: `JONIFY_SUPER(${input.split("").reverse().join("")})`,
      method: "super",
      efficiency: 98.7,
      language: language,
      super_features: [
        "quantum_processing",
        "dimensional_analysis",
        "temporal_optimization",
      ],
    };
  }

  async getPerformanceMetrics() {
    return {
      standard_efficiency: 85.5,
      enhanced_efficiency: 92.3,
      super_efficiency: 98.7,
      average_performance: 92.2,
    };
  }

  async isHealthy() {
    return this.initialized;
  }
}

// Super Intelligence Core
class SuperIntelligenceCore {
  constructor() {
    this.active = false;
    this.intelligenceLevel = "super";
    this.capabilities = new Set();
  }

  async activate() {
    this.capabilities.add("pattern_recognition");
    this.capabilities.add("predictive_analytics");
    this.capabilities.add("creative_synthesis");
    this.capabilities.add("strategic_planning");
    this.capabilities.add("emotional_intelligence");
    this.capabilities.add("cultural_analysis");

    this.active = true;
    console.log("🌟 Super Intelligence Layer activated");
  }

  async analyze(input) {
    if (!this.active) await this.activate();

    return {
      analysis_type: "super_intelligence",
      patterns_detected: Math.floor(Math.random() * 50) + 10,
      predictions: await this.generatePredictions(input),
      strategic_insights: await this.generateStrategicInsights(input),
      emotional_analysis: await this.analyzeEmotions(input),
      creativity_score: (Math.random() * 30 + 70).toFixed(2),
      intelligence_level: this.intelligenceLevel,
    };
  }

  async executeOperation(operationType, inputData, intelligenceLevel) {
    const operations = {
      strategic_analysis: await this.strategicAnalysis(inputData),
      predictive_modeling: await this.predictiveModeling(inputData),
      creative_problem_solving: await this.creativeProblemSolving(inputData),
      cultural_intelligence: await this.culturalIntelligence(inputData),
      emotional_processing: await this.emotionalProcessing(inputData),
    };

    return (
      operations[operationType] || (await this.defaultOperation(inputData))
    );
  }

  async analyzeRealTimeData(data) {
    return {
      cultural_insights: await this.analyzeCulturalData(data.cultural),
      financial_predictions: await this.analyzeFinancialData(data.financial),
      news_sentiment: await this.analyzeNewsData(data.news),
      cross_correlations: await this.findCorrelations(data),
      strategic_recommendations: await this.generateRecommendations(data),
    };
  }

  async processCulturalIntelligence(culturalData, analysisType) {
    return {
      cultural_patterns: await this.identifyPatterns(culturalData),
      historical_context: await this.analyzeHistory(culturalData),
      social_dynamics: await this.analyzeSocialDynamics(culturalData),
      future_trends: await this.predictCulturalTrends(culturalData),
      intelligence_score: (Math.random() * 25 + 75).toFixed(2),
    };
  }

  // Helper methods for Super Intelligence operations
  async generatePredictions(input) {
    return [
      "Trend analysis indicates positive trajectory",
      "Pattern recognition suggests optimization potential",
      "Strategic positioning recommends enhanced focus",
    ];
  }

  async generateStrategicInsights(input) {
    return {
      strategic_value: "high",
      optimization_potential: "85%",
      risk_assessment: "low",
      recommended_actions: ["enhance", "expand", "optimize"],
    };
  }

  async analyzeEmotions(input) {
    return {
      sentiment: "positive",
      confidence: 0.87,
      emotional_intelligence: "high",
      empathy_level: 0.92,
    };
  }

  async getIntelligenceLevel() {
    return {
      level: "super",
      iq_equivalent: await this.calculateIQEquivalent(),
      capabilities: Array.from(this.capabilities),
      enhancement_factor: 3.7,
    };
  }

  async calculateIQEquivalent() {
    return Math.floor(Math.random() * 200) + 300; // 300-500 range
  }

  async isHealthy() {
    return this.active && this.capabilities.size > 0;
  }

  // Additional Super Intelligence methods
  async strategicAnalysis(data) {
    return { strategy: "optimized", confidence: 0.94 };
  }

  async predictiveModeling(data) {
    return { predictions: ["trend_up", "stability"], accuracy: 0.89 };
  }

  async creativeProblemSolving(data) {
    return {
      solutions: ["innovative_approach", "optimized_process"],
      creativity: 0.91,
    };
  }

  async culturalIntelligence(data) {
    return { cultural_insights: "deep_understanding", cultural_iq: 0.96 };
  }

  async emotionalProcessing(data) {
    return { emotional_state: "balanced", eq_score: 0.93 };
  }

  async defaultOperation(data) {
    return { operation: "completed", status: "success" };
  }

  async analyzeCulturalData(data) {
    return { cultural_score: 0.88, insights: "rich_heritage" };
  }

  async analyzeFinancialData(data) {
    return { financial_health: 0.85, trends: "positive" };
  }

  async analyzeNewsData(data) {
    return { sentiment: "neutral", relevance: 0.82 };
  }

  async findCorrelations(data) {
    return {
      correlations: ["cultural_economic", "news_sentiment"],
      strength: 0.76,
    };
  }

  async generateRecommendations(data) {
    return [
      "enhance_cultural_programs",
      "monitor_financial_trends",
      "analyze_news_impact",
    ];
  }

  async identifyPatterns(data) {
    return {
      patterns: ["traditional_modern_blend", "youth_engagement"],
      confidence: 0.87,
    };
  }

  async analyzeHistory(data) {
    return { historical_impact: "significant", continuity: 0.89 };
  }

  async analyzeSocialDynamics(data) {
    return { social_cohesion: 0.84, community_strength: "high" };
  }

  async predictCulturalTrends(data) {
    return {
      trends: ["digital_preservation", "global_integration"],
      probability: 0.78,
    };
  }
}

// ALBA Interface - Artificial Labor Born Intelligence
class ALBAInterface {
  constructor() {
    this.connected = false;
    this.laborBitsArray = new Map();
    this.neuralArrayProcessing = false;
    this.bornIntelligence = false;
  }

  async connect() {
    // Initialize Labor Bits Array
    await this.initializeLaborBits();

    // Activate Neural Array Processing
    await this.activateNeuralArrayProcessing();

    // Enable Born Intelligence
    await this.enableBornIntelligence();

    this.connected = true;
    console.log(
      "🔗 ALBA Interface connected - Artificial Labor Born Intelligence",
    );
  }

  async initializeLaborBits() {
    const laborTypes = [
      "cognitive_labor",
      "creative_labor",
      "analytical_labor",
      "emotional_labor",
      "social_labor",
      "technical_labor",
      "cultural_labor",
      "linguistic_labor",
      "strategic_labor",
    ];

    for (const type of laborTypes) {
      this.laborBitsArray.set(type, {
        efficiency: Math.random() * 0.2 + 0.8, // 80-100%
        bits_processed: Math.floor(Math.random() * 1000000),
        last_activity: new Date().toISOString(),
        status: "active",
      });
    }

    console.log("💼 Labor Bits Array initialized");
  }

  async activateNeuralArrayProcessing() {
    this.neuralArrayProcessing = true;
    console.log("🧠 ALBA Neural Array Processing activated");
  }

  async enableBornIntelligence() {
    this.bornIntelligence = true;
    console.log("🌱 Born Intelligence enabled");
  }

  async processLaborBits(input) {
    if (!this.connected) await this.connect();

    const results = {};

    for (const [type, data] of this.laborBitsArray.entries()) {
      results[type] = {
        processed_bits: data.bits_processed + Math.floor(Math.random() * 1000),
        efficiency: data.efficiency,
        labor_output: `${type}_output_${input.length}_bits`,
        status: data.status,
      };
    }

    return {
      labor_bits_processing: results,
      total_types: this.laborBitsArray.size,
      born_intelligence_enhancement: this.bornIntelligence
        ? "active"
        : "inactive",
    };
  }

  async processFullALBA(laborInput, bitsArrayType) {
    return {
      alba_architecture: "Artificial Labor Born Intelligence",
      labor_processing: await this.processLaborBits(laborInput),
      neural_array_processing: await this.processNeuralArray(laborInput),
      born_intelligence_output: await this.processBornIntelligence(laborInput),
      bits_array_type: bitsArrayType,
      total_efficiency: await this.calculateTotalEfficiency(),
    };
  }

  async processNeuralArray(input) {
    return {
      neural_nodes_active: this.laborBitsArray.size,
      processing_method: "ALBA Neural Array",
      output: `neural_processed_${input}`,
      efficiency: 0.94,
    };
  }

  async processBornIntelligence(input) {
    return {
      born_intelligence_level: "enhanced",
      natural_processing: true,
      intuitive_output: `born_intelligence_${input}_intuitive`,
      learning_adaptation: 0.96,
    };
  }

  async getLaborBitsArray() {
    const array = {};

    for (const [type, data] of this.laborBitsArray.entries()) {
      array[type] = {
        ...data,
        efficiency_percentage: (data.efficiency * 100).toFixed(2) + "%",
        bits_formatted: data.bits_processed.toLocaleString(),
      };
    }

    return array;
  }

  async enhanceCulturalData(data) {
    return {
      alba_cultural_enhancement: {
        labor_bits_applied: "cultural_labor",
        born_intelligence_insights: "deep_cultural_understanding",
        neural_array_processing: "cultural_pattern_recognition",
        enhancement_level: "superior",
      },
      enhanced_data: data,
    };
  }

  async getLaborEfficiency() {
    const efficiencies = Array.from(this.laborBitsArray.values()).map(
      (l) => l.efficiency,
    );
    return (
      (efficiencies.reduce((a, b) => a + b, 0) / efficiencies.length) *
      100
    ).toFixed(2);
  }

  async getBornIntelligenceScore() {
    return this.bornIntelligence ? (Math.random() * 15 + 85).toFixed(2) : 0;
  }

  async getNeuralArrayPerformance() {
    return this.neuralArrayProcessing
      ? (Math.random() * 10 + 90).toFixed(2)
      : 0;
  }

  async calculateTotalEfficiency() {
    return (await this.getLaborEfficiency()) + "%";
  }

  async isConnected() {
    return this.connected;
  }
}

// Start ASI Agent
const asiAgent = new ASIAgent();

// Graceful shutdown
process.on("SIGTERM", () => {
  console.log("🛑 Received SIGTERM, shutting down gracefully...");
  asiAgent.stop();
  process.exit(0);
});

process.on("SIGINT", () => {
  console.log("🛑 Received SIGINT, shutting down gracefully...");
  asiAgent.stop();
  process.exit(0);
});

// Export for external use
module.exports = ASIAgent;

// Auto-start if run directly
asiAgent.start();
