/**
 * 🧠 ASI Analytics AI Analyzer
 * Converts raw data into human-readable business insights
 * 
 * @version 2.0.0
 * @author Ledjan Ahmati <dealsjona@gmail.com>
 */

export interface TrendAnalysis {
  summary: string;
  insights: string[];
  alerts: Alert[];
  confidence: number;
  trend: 'increasing' | 'decreasing' | 'stable' | 'volatile';
  growth: number;
  predictions: string[];
}

export interface Alert {
  type: 'warning' | 'critical' | 'info' | 'success';
  message: string;
  action?: string;
}

export interface DataPoint {
  x: string;
  [key: string]: any;
}

/**
 * 🚀 Smart Trend Analyzer - Kryesor
 */
export function analyzeTrends(data: DataPoint[], metric = 'value'): TrendAnalysis {
  if (!data || data.length < 2) {
    return {
      summary: "Insufficient data for analysis",
      insights: ["Need more data points for meaningful analysis"],
      alerts: [],
      confidence: 0,
      trend: 'stable',
      growth: 0,
      predictions: []
    };
  }

  const values = data.map(d => parseFloat(d[metric]) || 0);
  const growth = calculateGrowthRate(values);
  const trend = determineTrend(values);
  const volatility = calculateVolatility(values);
  
  return {
    summary: generateSummary(growth, trend, volatility, values),
    insights: generateInsights(data, values, growth, trend),
    alerts: generateAlerts(growth, trend, volatility, values),
    confidence: calculateConfidence(values),
    trend,
    growth,
    predictions: generatePredictions(values, trend, growth)
  };
}

/**
 * 📊 Revenue-Specific Analysis
 */
export function analyzeRevenue(data: DataPoint[]): TrendAnalysis {
  const analysis = analyzeTrends(data, 'Subscriptions.mrr');
  
  // Revenue-specific enhancements
  if (analysis.growth > 15) {
    analysis.insights.push("🚀 Exceptional revenue growth! Consider scaling operations.");
  }
  
  if (analysis.growth < -5) {
    analysis.alerts.push({
      type: 'warning',
      message: 'Revenue decline detected',
      action: 'Review customer retention strategies'
    });
  }

  return analysis;
}

/**
 * 👥 User Growth Analysis
 */
export function analyzeUserGrowth(data: DataPoint[]): TrendAnalysis {
  const analysis = analyzeTrends(data, 'Users.count');
  
  // User-specific insights
  if (analysis.growth > 20) {
    analysis.insights.push("📈 Strong user acquisition! Monitor server capacity.");
  }
  
  return analysis;
}

/**
 * 💰 Churn Rate Analysis
 */
export function analyzeChurnRate(data: DataPoint[]): TrendAnalysis {
  const analysis = analyzeTrends(data, 'Subscriptions.churnRate');
  
  // Invert logic for churn (lower is better)
  const invertedGrowth = -analysis.growth;
  
  return {
    ...analysis,
    growth: invertedGrowth,
    summary: generateChurnSummary(analysis.growth, analysis.trend),
    insights: generateChurnInsights(analysis.growth, data)
  };
}

// =================== HELPER FUNCTIONS ===================

function calculateGrowthRate(values: number[]): number {
  if (values.length < 2) return 0;
  
  const recent = values.slice(-3).reduce((a, b) => a + b, 0) / Math.min(3, values.length);
  const previous = values.slice(0, -3).reduce((a, b) => a + b, 0) / Math.max(1, values.length - 3);
  
  return previous === 0 ? 0 : ((recent - previous) / previous) * 100;
}

function determineTrend(values: number[]): 'increasing' | 'decreasing' | 'stable' | 'volatile' {
  if (values.length < 3) return 'stable';
  
  const volatility = calculateVolatility(values);
  if (volatility > 30) return 'volatile';
  
  const growth = calculateGrowthRate(values);
  if (growth > 5) return 'increasing';
  if (growth < -5) return 'decreasing';
  return 'stable';
}

function calculateVolatility(values: number[]): number {
  if (values.length < 2) return 0;
  
  const mean = values.reduce((a, b) => a + b, 0) / values.length;
  const variance = values.reduce((acc, val) => acc + Math.pow(val - mean, 2), 0) / values.length;
  const stdDev = Math.sqrt(variance);
  
  return mean === 0 ? 0 : (stdDev / mean) * 100;
}

function calculateConfidence(values: number[]): number {
  const length = values.length;
  const volatility = calculateVolatility(values);
  
  // Higher confidence with more data points and lower volatility
  let confidence = Math.min(90, length * 10); // Base on data points
  confidence -= Math.min(40, volatility); // Reduce for volatility
  
  return Math.max(10, confidence);
}

function generateSummary(growth: number, trend: string, volatility: number, values: number[]): string {
  const currentValue = values[values.length - 1];
  const period = values.length > 7 ? 'month' : 'week';
  
  if (trend === 'volatile') {
    return `Highly volatile performance with ${volatility.toFixed(1)}% fluctuation. Current: ${formatCurrency(currentValue)}.`;
  }
  
  const direction = growth > 0 ? 'increased' : 'decreased';
  return `Revenue ${direction} ${Math.abs(growth).toFixed(1)}% over the ${period}. Current: ${formatCurrency(currentValue)}.`;
}

function generateInsights(data: DataPoint[], values: number[], growth: number, trend: string): string[] {
  const insights: string[] = [];
  
  // Performance insights
  if (growth > 10) {
    insights.push("💡 Strong growth momentum detected. Consider expanding marketing budget.");
  } else if (growth > 5) {
    insights.push("📈 Steady positive growth. Maintain current strategies.");
  } else if (growth < -10) {
    insights.push("⚠️ Significant decline. Immediate action required.");
  }
  
  // Seasonal patterns
  if (detectSeasonality(values)) {
    insights.push("🌊 Seasonal pattern detected. Plan for cyclical variations.");
  }
  
  // Peak performance
  const maxValue = Math.max(...values);
  const currentValue = values[values.length - 1];
  if (currentValue === maxValue) {
    insights.push("🏆 Currently at all-time high performance!");
  }
  
  return insights;
}

function generateAlerts(growth: number, trend: string, volatility: number, values: number[]): Alert[] {
  const alerts: Alert[] = [];
  
  // Critical decline
  if (growth < -15) {
    alerts.push({
      type: 'critical',
      message: 'Critical revenue decline detected',
      action: 'Immediate management review required'
    });
  }
  
  // High volatility
  if (volatility > 40) {
    alerts.push({
      type: 'warning',
      message: 'High volatility in performance metrics',
      action: 'Investigate underlying causes'
    });
  }
  
  // Stagnation
  if (Math.abs(growth) < 1 && values.length > 10) {
    alerts.push({
      type: 'info',
      message: 'Performance has plateaued',
      action: 'Consider new growth strategies'
    });
  }
  
  return alerts;
}

function generatePredictions(values: number[], trend: string, growth: number): string[] {
  const predictions: string[] = [];
  const currentValue = values[values.length - 1];
  
  // Simple linear projection
  const monthlyGrowth = growth / 100;
  const month1 = currentValue * (1 + monthlyGrowth);
  const month3 = currentValue * Math.pow(1 + monthlyGrowth, 3);
  
  predictions.push(`Next month projection: ${formatCurrency(month1)}`);
  predictions.push(`3-month projection: ${formatCurrency(month3)}`);
  
  // Confidence intervals
  if (trend === 'volatile') {
    predictions.push("⚠️ High uncertainty due to volatility");
  } else if (trend === 'stable') {
    predictions.push("✅ High confidence in projections");
  }
  
  return predictions;
}

function generateChurnSummary(growth: number, trend: string): string {
  const direction = growth > 0 ? 'increased' : 'decreased';
  return `Churn rate ${direction} ${Math.abs(growth).toFixed(1)}%. ${trend === 'decreasing' ? '✅ Improving retention' : '⚠️ Monitor closely'}.`;
}

function generateChurnInsights(growth: number, data: DataPoint[]): string[] {
  const insights: string[] = [];
  
  if (growth < -5) {
    insights.push("🎉 Churn rate improving! Customer satisfaction initiatives working.");
  } else if (growth > 5) {
    insights.push("🚨 Churn rate increasing. Review customer experience and pricing.");
  }
  
  return insights;
}

function detectSeasonality(values: number[]): boolean {
  // Simple seasonality detection - look for repeating patterns
  if (values.length < 12) return false;
  
  // Calculate correlation with lagged values
  const lag12 = calculateCorrelation(values.slice(0, -12), values.slice(12));
  return lag12 > 0.7; // Strong correlation suggests seasonality
}

function calculateCorrelation(x: number[], y: number[]): number {
  if (x.length !== y.length || x.length === 0) return 0;
  
  const n = x.length;
  const sumX = x.reduce((a, b) => a + b, 0);
  const sumY = y.reduce((a, b) => a + b, 0);
  const sumXY = x.reduce((acc, xi, i) => acc + xi * y[i], 0);
  const sumX2 = x.reduce((acc, xi) => acc + xi * xi, 0);
  const sumY2 = y.reduce((acc, yi) => acc + yi * yi, 0);
  
  const numerator = n * sumXY - sumX * sumY;
  const denominator = Math.sqrt((n * sumX2 - sumX * sumX) * (n * sumY2 - sumY * sumY));
  
  return denominator === 0 ? 0 : numerator / denominator;
}

function formatCurrency(value: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(value);
}
