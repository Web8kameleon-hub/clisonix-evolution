/**
 * 🔮 ASI Predictive Forecasting Engine
 * Advanced revenue and growth prediction with confidence intervals
 * 
 * @version 2.0.0
 * @author Ledjan Ahmati <dealsjona@gmail.com>
 */

export interface ForecastPoint {
  date: string;
  value: number;
  confidence: number;
  upperBound: number;
  lowerBound: number;
  isProjected: boolean;
}

export interface ForecastResult {
  forecasted: ForecastPoint[];
  summary: string;
  confidence: number;
  methodology: string;
  insights: string[];
  alerts: string[];
}

/**
 * 🚀 Advanced Revenue Forecasting
 */
export function forecastRevenue(
  historicalData: { x: string; value: number }[],
  daysAhead = 90
): ForecastResult {
  if (!historicalData || historicalData.length < 7) {
    return {
      forecasted: [],
      summary: "Insufficient historical data for forecasting",
      confidence: 0,
      methodology: "No prediction possible",
      insights: ["Need at least 7 data points for reliable forecasting"],
      alerts: ["Increase data collection period"]
    };
  }

  const values = historicalData.map(d => d.value);
  const dates = historicalData.map(d => new Date(d.x));
  
  // Multiple forecasting methods
  const linearForecast = linearRegression(values, daysAhead);
  const exponentialForecast = exponentialSmoothing(values, daysAhead);
  const seasonalForecast = seasonalDecomposition(values, daysAhead);
  
  // Ensemble prediction (weighted average)
  const ensemble = combineForecasts([
    { forecast: linearForecast, weight: 0.3 },
    { forecast: exponentialForecast, weight: 0.4 },
    { forecast: seasonalForecast, weight: 0.3 }
  ]);

  const forecasted = generateForecastPoints(dates, ensemble, daysAhead);
  const confidence = calculateForecastConfidence(values, ensemble);
  
  return {
    forecasted,
    summary: generateForecastSummary(forecasted, confidence),
    confidence,
    methodology: "Ensemble: Linear Regression + Exponential Smoothing + Seasonal Decomposition",
    insights: generateForecastInsights(forecasted, historicalData),
    alerts: generateForecastAlerts(forecasted, confidence)
  };
}

/**
 * 📈 Specialized Growth Forecasting
 */
export function forecastUserGrowth(
  userData: { x: string; value: number }[],
  daysAhead = 90
): ForecastResult {
  // User growth typically follows S-curve patterns
  const logisticForecast = logisticGrowth(userData.map(d => d.value), daysAhead);
  const exponentialForecast = exponentialSmoothing(userData.map(d => d.value), daysAhead);
  
  const ensemble = combineForecasts([
    { forecast: logisticForecast, weight: 0.6 },
    { forecast: exponentialForecast, weight: 0.4 }
  ]);

  const dates = userData.map(d => new Date(d.x));
  const forecasted = generateForecastPoints(dates, ensemble, daysAhead);
  
  return {
    forecasted,
    summary: `User growth projected to reach ${Math.round(forecasted[forecasted.length - 1]?.value || 0)} users in ${daysAhead} days`,
    confidence: calculateForecastConfidence(userData.map(d => d.value), ensemble),
    methodology: "Logistic Growth Model + Exponential Smoothing",
    insights: ["User growth typically slows as market saturation increases"],
    alerts: forecasted[forecasted.length - 1]?.value > userData[userData.length - 1]?.value * 2 ? 
      ["Aggressive growth projection - ensure infrastructure scaling"] : []
  };
}

// =================== FORECASTING ALGORITHMS ===================

function linearRegression(values: number[], periods: number): number[] {
  const n = values.length;
  const x = Array.from({ length: n }, (_, i) => i);
  const y = values;
  
  // Calculate slope and intercept
  const sumX = x.reduce((a, b) => a + b, 0);
  const sumY = y.reduce((a, b) => a + b, 0);
  const sumXY = x.reduce((acc, xi, i) => acc + xi * y[i], 0);
  const sumX2 = x.reduce((acc, xi) => acc + xi * xi, 0);
  
  const slope = (n * sumXY - sumX * sumY) / (n * sumX2 - sumX * sumX);
  const intercept = (sumY - slope * sumX) / n;
  
  // Generate predictions
  return Array.from({ length: periods }, (_, i) => 
    intercept + slope * (n + i)
  );
}

function exponentialSmoothing(values: number[], periods: number, alpha = 0.3): number[] {
  if (values.length === 0) return [];
  
  let smoothed = values[0];
  const smoothedValues = [smoothed];
  
  // Apply exponential smoothing to historical data
  for (let i = 1; i < values.length; i++) {
    smoothed = alpha * values[i] + (1 - alpha) * smoothed;
    smoothedValues.push(smoothed);
  }
  
  // Project future values
  const trend = (smoothedValues[smoothedValues.length - 1] - smoothedValues[smoothedValues.length - 2]) || 0;
  
  return Array.from({ length: periods }, (_, i) => 
    smoothed + trend * (i + 1)
  );
}

function seasonalDecomposition(values: number[], periods: number): number[] {
  if (values.length < 12) return exponentialSmoothing(values, periods);
  
  // Simple seasonal pattern detection (monthly cycles)
  const seasonLength = Math.min(12, Math.floor(values.length / 3));
  const seasons: number[] = [];
  
  // Calculate seasonal indices
  for (let i = 0; i < seasonLength; i++) {
    const seasonalValues: number[] = [];
    for (let j = i; j < values.length; j += seasonLength) {
      seasonalValues.push(values[j]);
    }
    seasons[i] = seasonalValues.reduce((a, b) => a + b, 0) / seasonalValues.length;
  }
  
  // Deseasonalize data
  const deseasonalized = values.map((val, idx) => 
    val / (seasons[idx % seasonLength] || 1)
  );
  
  // Apply trend forecast to deseasonalized data
  const trendForecast = exponentialSmoothing(deseasonalized, periods);
  
  // Reseasonalize predictions
  return trendForecast.map((val, idx) => 
    val * (seasons[idx % seasonLength] || 1)
  );
}

function logisticGrowth(values: number[], periods: number): number[] {
  if (values.length < 5) return exponentialSmoothing(values, periods);
  
  // Estimate logistic growth parameters
  const maxValue = Math.max(...values) * 1.5; // Assume some growth capacity
  const r = calculateGrowthRate(values) / 100;
  const currentValue = values[values.length - 1];
  
  return Array.from({ length: periods }, (_, i) => {
    const t = i + 1;
    return maxValue / (1 + ((maxValue - currentValue) / currentValue) * Math.exp(-r * t));
  });
}

function combineForecasts(forecasts: { forecast: number[]; weight: number }[]): number[] {
  if (forecasts.length === 0) return [];
  
  const length = Math.max(...forecasts.map(f => f.forecast.length));
  const combined: number[] = [];
  
  for (let i = 0; i < length; i++) {
    let weightedSum = 0;
    let totalWeight = 0;
    
    forecasts.forEach(({ forecast, weight }) => {
      if (i < forecast.length) {
        weightedSum += forecast[i] * weight;
        totalWeight += weight;
      }
    });
    
    combined[i] = totalWeight > 0 ? weightedSum / totalWeight : 0;
  }
  
  return combined;
}

function generateForecastPoints(
  historicalDates: Date[],
  forecast: number[],
  daysAhead: number
): ForecastPoint[] {
  const points: ForecastPoint[] = [];
  const lastDate = historicalDates[historicalDates.length - 1];
  const volatility = calculateVolatility(forecast);
  
  for (let i = 0; i < daysAhead; i++) {
    const date = new Date(lastDate);
    date.setDate(date.getDate() + i + 1);
    
    const value = forecast[i] || 0;
    const confidenceDecay = Math.max(0.3, 1 - (i / daysAhead) * 0.7); // Confidence decreases over time
    const margin = value * (volatility / 100) * (1 + i * 0.1); // Uncertainty increases over time
    
    points.push({
      date: date.toISOString().split('T')[0],
      value,
      confidence: confidenceDecay * 100,
      upperBound: value + margin,
      lowerBound: Math.max(0, value - margin),
      isProjected: true
    });
  }
  
  return points;
}

function calculateForecastConfidence(historical: number[], forecast: number[]): number {
  const volatility = calculateVolatility(historical);
  const trendConsistency = calculateTrendConsistency(historical);
  
  // Base confidence on data quality and trend consistency
  let confidence = 90 - volatility; // Start high, reduce for volatility
  confidence = Math.max(20, confidence); // Minimum confidence
  confidence *= trendConsistency; // Multiply by trend consistency
  
  return Math.min(95, confidence); // Cap at 95%
}

function generateForecastSummary(forecasted: ForecastPoint[], confidence: number): string {
  if (forecasted.length === 0) return "No forecast available";
  
  const firstValue = forecasted[0]?.value || 0;
  const lastValue = forecasted[forecasted.length - 1]?.value || 0;
  const growth = ((lastValue - firstValue) / firstValue) * 100;
  
  return `Forecast shows ${growth > 0 ? 'growth' : 'decline'} of ${Math.abs(growth).toFixed(1)}% with ${confidence.toFixed(0)}% confidence.`;
}

function generateForecastInsights(forecasted: ForecastPoint[], historical: any[]): string[] {
  const insights: string[] = [];
  
  if (forecasted.length === 0) return insights;
  
  const projectedGrowth = calculateProjectedGrowth(forecasted);
  
  if (projectedGrowth > 50) {
    insights.push("🚀 Exceptional growth projected - ensure scalability planning");
  } else if (projectedGrowth > 20) {
    insights.push("📈 Strong growth expected - monitor resource allocation");
  } else if (projectedGrowth < -10) {
    insights.push("⚠️ Decline projected - consider intervention strategies");
  }
  
  // Confidence-based insights
  const avgConfidence = forecasted.reduce((acc, p) => acc + p.confidence, 0) / forecasted.length;
  if (avgConfidence < 60) {
    insights.push("🔍 High uncertainty - increase data collection frequency");
  }
  
  return insights;
}

function generateForecastAlerts(forecasted: ForecastPoint[], confidence: number): string[] {
  const alerts: string[] = [];
  
  if (confidence < 50) {
    alerts.push("Low confidence forecast - use with caution");
  }
  
  if (forecasted.some(p => p.value < 0)) {
    alerts.push("Negative values projected - review model assumptions");
  }
  
  return alerts;
}

// =================== HELPER FUNCTIONS ===================

function calculateGrowthRate(values: number[]): number {
  if (values.length < 2) return 0;
  
  const recent = values[values.length - 1];
  const previous = values[Math.floor(values.length / 2)];
  
  return previous === 0 ? 0 : ((recent - previous) / previous) * 100;
}

function calculateVolatility(values: number[]): number {
  if (values.length < 2) return 0;
  
  const mean = values.reduce((a, b) => a + b, 0) / values.length;
  const variance = values.reduce((acc, val) => acc + Math.pow(val - mean, 2), 0) / values.length;
  const stdDev = Math.sqrt(variance);
  
  return mean === 0 ? 0 : (stdDev / mean) * 100;
}

function calculateTrendConsistency(values: number[]): number {
  if (values.length < 3) return 0.5;
  
  let consistentDirectionCount = 0;
  let totalChanges = 0;
  
  for (let i = 2; i < values.length; i++) {
    const change1 = values[i - 1] - values[i - 2];
    const change2 = values[i] - values[i - 1];
    
    if ((change1 > 0 && change2 > 0) || (change1 < 0 && change2 < 0) || (change1 === 0 && change2 === 0)) {
      consistentDirectionCount++;
    }
    totalChanges++;
  }
  
  return totalChanges === 0 ? 0.5 : consistentDirectionCount / totalChanges;
}

function calculateProjectedGrowth(forecasted: ForecastPoint[]): number {
  if (forecasted.length === 0) return 0;
  
  const firstValue = forecasted[0].value;
  const lastValue = forecasted[forecasted.length - 1].value;
  
  return firstValue === 0 ? 0 : ((lastValue - firstValue) / firstValue) * 100;
}
