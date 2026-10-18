/**
 * EuroWeb Ultra - Radio Propagation Intelligence Dashboard
 * 
 * Real-time visualization of radio wave propagation conditions
 * Displays ionospheric conditions, optimal transmission parameters, and AI predictions
 * 
 * @author GitHub Copilot & EuroWeb Ultra Team
 * @version 1.0.0 - Propagation Intelligence UI
 */

'use client';

import {
    Activity,
    BarChart3,
    CheckCircle,
    Clock,
    Globe,
    Moon,
    Radio,
    Settings,
    Signal,
    Sun,
    Sunrise,
    Sunset,
    Target,
    TrendingUp,
    Wifi,
    Zap
} from 'lucide-react';
import React, { useEffect, useState } from 'react';

interface PropagationConditions {
    time_of_day: 'dawn' | 'day' | 'dusk' | 'night';
    season: 'spring' | 'summer' | 'autumn' | 'winter';
    solar_flux: number;
    k_index: number;
    sunspot_number: number;
    ionospheric_layer: 'D' | 'E' | 'F1' | 'F2';
    muf: number;
    predicted_range_km: number;
    signal_absorption_db: number;
}

interface OptimalParams {
    tx_power_dbm: number;
    data_rate: number;
    frequency_mhz: number;
    retry_count: number;
    backoff_ms: number;
    confidence: number;
}

interface PropagationPrediction {
    hours_ahead: number;
    time: string;
    conditions: PropagationConditions;
    expected_performance: {
        range_multiplier: number;
        signal_absorption: string;
        optimal_strategy: string;
    };
}

const RadioPropagationDashboard: React.FC = () => {
    const [currentConditions, setCurrentConditions] = useState<PropagationConditions | null>(null);
    const [optimalParams, setOptimalParams] = useState<OptimalParams | null>(null);
    const [predictions, setPredictions] = useState<PropagationPrediction[]>([]);
    const [networkReport, setNetworkReport] = useState<any>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [selectedNode, setSelectedNode] = useState('gateway-001');
    const [autoRefresh, setAutoRefresh] = useState(true);

    // Fetch propagation data
    const fetchPropagationData = async () => {
        try {
            setIsLoading(true);

            // Fetch current status
            const statusResponse = await fetch('/api/radio-propagation?action=status');
            const statusData = await statusResponse.json();

            if (statusData.success) {
                setCurrentConditions(statusData.propagation_conditions);
                setNetworkReport(statusData.network_optimization);
            }

            // Fetch optimal parameters for selected node
            const optimizeResponse = await fetch(`/api/radio-propagation?action=optimize&node=${selectedNode}`);
            const optimizeData = await optimizeResponse.json();

            if (optimizeData.success) {
                setOptimalParams(optimizeData.optimal_parameters);
            }

            // Fetch predictions
            const predictResponse = await fetch('/api/radio-propagation?action=predict&hours=12');
            const predictData = await predictResponse.json();

            if (predictData.success) {
                setPredictions(predictData.predictions.slice(0, 6)); // Next 6 hours
            }

        } catch (error) {
            console.error('Failed to fetch propagation data:', error);
        } finally {
            setIsLoading(false);
        }
    };

    // Auto-refresh effect
    useEffect(() => {
        fetchPropagationData();

        if (autoRefresh) {
            const interval = setInterval(fetchPropagationData, 5 * 60 * 1000); // Every 5 minutes
            return () => clearInterval(interval);
        }
    }, [selectedNode, autoRefresh]);

    // Get time of day icon
    const getTimeIcon = (timeOfDay: string) => {
        switch (timeOfDay) {
            case 'dawn': return <Sunrise className="w-5 h-5" />;
            case 'day': return <Sun className="w-5 h-5" />;
            case 'dusk': return <Sunset className="w-5 h-5" />;
            case 'night': return <Moon className="w-5 h-5" />;
            default: return <Clock className="w-5 h-5" />;
        }
    };

    // Get propagation quality color
    const getPropagationQuality = (conditions: PropagationConditions) => {
        if (conditions.time_of_day === 'night') return { color: 'text-green-400', label: 'Excellent', bg: 'bg-green-900/20' };
        if (conditions.time_of_day === 'day') return { color: 'text-yellow-400', label: 'Good', bg: 'bg-yellow-900/20' };
        return { color: 'text-blue-400', label: 'Very Good', bg: 'bg-blue-900/20' };
    };

    // Get confidence level color
    const getConfidenceColor = (confidence: number) => {
        if (confidence >= 0.8) return 'text-green-400';
        if (confidence >= 0.6) return 'text-yellow-400';
        return 'text-red-400';
    };

    if (isLoading) {
        return (
            <div className="w-full max-w-7xl mx-auto p-6 bg-gray-900 text-white">
                <div className="flex items-center justify-center h-64">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-400"></div>
                    <span className="ml-3 text-lg">Loading propagation intelligence...</span>
                </div>
            </div>
        );
    }

    return (
        <div className="w-full max-w-7xl mx-auto p-6 space-y-6 bg-gray-900 text-white">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                    <div className="flex items-center gap-3">
                        <Radio className="w-8 h-8 text-purple-400" />
                        <div>
                            <h1 className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-blue-600">
                                Radio Propagation Intelligence
                            </h1>
                            <p className="text-gray-400 mt-1">
                                AI-powered ionospheric analysis and transmission optimization
                            </p>
                        </div>
                    </div>
                </div>

                <div className="flex items-center gap-4">
                    <select
                        value={selectedNode}
                        onChange={(e) => setSelectedNode(e.target.value)}
                        className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white"
                    >
                        <option value="gateway-001">Gateway 001</option>
                        <option value="relay-001">Relay 001</option>
                        <option value="relay-002">Relay 002</option>
                        <option value="bridge-001">Bridge 001</option>
                    </select>

                    <button
                        onClick={() => setAutoRefresh(!autoRefresh)}
                        className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${autoRefresh
                                ? 'bg-green-600 hover:bg-green-700'
                                : 'bg-gray-600 hover:bg-gray-700'
                            }`}
                    >
                        <Activity className={`w-4 h-4 ${autoRefresh ? 'animate-pulse' : ''}`} />
                        {autoRefresh ? 'Live' : 'Manual'}
                    </button>
                </div>
            </div>

            {/* Current Conditions */}
            {currentConditions && (
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Ionospheric Conditions */}
                    <div className="lg:col-span-2 bg-gray-800 rounded-xl border border-gray-700 p-6">
                        <div className="flex items-center gap-3 mb-6">
                            <Globe className="w-6 h-6 text-blue-400" />
                            <h3 className="text-xl font-semibold">Ionospheric Conditions</h3>
                            <div className={`flex items-center gap-2 px-3 py-1 rounded-full ${getPropagationQuality(currentConditions).bg}`}>
                                {getTimeIcon(currentConditions.time_of_day)}
                                <span className={`text-sm font-medium ${getPropagationQuality(currentConditions).color}`}>
                                    {getPropagationQuality(currentConditions).label}
                                </span>
                            </div>
                        </div>

                        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                            <div className="bg-gray-900/50 rounded-lg p-4">
                                <div className="text-sm text-gray-400 mb-1">Time Period</div>
                                <div className="flex items-center gap-2">
                                    {getTimeIcon(currentConditions.time_of_day)}
                                    <span className="font-semibold capitalize">{currentConditions.time_of_day}</span>
                                </div>
                            </div>

                            <div className="bg-gray-900/50 rounded-lg p-4">
                                <div className="text-sm text-gray-400 mb-1">Dominant Layer</div>
                                <div className="text-xl font-bold text-blue-400">{currentConditions.ionospheric_layer}</div>
                            </div>

                            <div className="bg-gray-900/50 rounded-lg p-4">
                                <div className="text-sm text-gray-400 mb-1">MUF</div>
                                <div className="text-xl font-bold text-green-400">{currentConditions.muf.toFixed(1)} MHz</div>
                            </div>

                            <div className="bg-gray-900/50 rounded-lg p-4">
                                <div className="text-sm text-gray-400 mb-1">Range</div>
                                <div className="text-xl font-bold text-purple-400">{currentConditions.predicted_range_km.toFixed(1)} km</div>
                            </div>

                            <div className="bg-gray-900/50 rounded-lg p-4">
                                <div className="text-sm text-gray-400 mb-1">Solar Flux</div>
                                <div className="text-lg font-semibold">{currentConditions.solar_flux.toFixed(0)}</div>
                            </div>

                            <div className="bg-gray-900/50 rounded-lg p-4">
                                <div className="text-sm text-gray-400 mb-1">K-Index</div>
                                <div className={`text-lg font-semibold ${currentConditions.k_index <= 3 ? 'text-green-400' : 'text-yellow-400'}`}>
                                    {currentConditions.k_index}
                                </div>
                            </div>

                            <div className="bg-gray-900/50 rounded-lg p-4">
                                <div className="text-sm text-gray-400 mb-1">Absorption</div>
                                <div className="text-lg font-semibold text-red-400">{currentConditions.signal_absorption_db.toFixed(1)} dB</div>
                            </div>

                            <div className="bg-gray-900/50 rounded-lg p-4">
                                <div className="text-sm text-gray-400 mb-1">Sunspots</div>
                                <div className="text-lg font-semibold">{currentConditions.sunspot_number.toFixed(0)}</div>
                            </div>
                        </div>
                    </div>

                    {/* Optimal Parameters */}
                    <div className="bg-gray-800 rounded-xl border border-gray-700 p-6">
                        <div className="flex items-center gap-3 mb-6">
                            <Settings className="w-6 h-6 text-green-400" />
                            <h3 className="text-xl font-semibold">Optimal Parameters</h3>
                        </div>

                        {optimalParams && (
                            <div className="space-y-4">
                                <div className="bg-gray-900/50 rounded-lg p-4">
                                    <div className="text-sm text-gray-400 mb-1">TX Power</div>
                                    <div className="flex items-center gap-2">
                                        <Zap className="w-4 h-4 text-yellow-400" />
                                        <span className="text-xl font-bold">{optimalParams.tx_power_dbm} dBm</span>
                                    </div>
                                </div>

                                <div className="bg-gray-900/50 rounded-lg p-4">
                                    <div className="text-sm text-gray-400 mb-1">Data Rate</div>
                                    <div className="flex items-center gap-2">
                                        <Signal className="w-4 h-4 text-blue-400" />
                                        <span className="text-xl font-bold">SF{optimalParams.data_rate}</span>
                                    </div>
                                </div>

                                <div className="bg-gray-900/50 rounded-lg p-4">
                                    <div className="text-sm text-gray-400 mb-1">Frequency</div>
                                    <div className="flex items-center gap-2">
                                        <Wifi className="w-4 h-4 text-purple-400" />
                                        <span className="text-lg font-bold">{optimalParams.frequency_mhz.toFixed(3)} MHz</span>
                                    </div>
                                </div>

                                <div className="bg-gray-900/50 rounded-lg p-4">
                                    <div className="text-sm text-gray-400 mb-1">AI Confidence</div>
                                    <div className="flex items-center gap-2">
                                        <Target className="w-4 h-4 text-green-400" />
                                        <span className={`text-lg font-bold ${getConfidenceColor(optimalParams.confidence)}`}>
                                            {(optimalParams.confidence * 100).toFixed(1)}%
                                        </span>
                                    </div>
                                </div>

                                <div className="bg-gray-900/50 rounded-lg p-4">
                                    <div className="text-sm text-gray-400 mb-1">Retry Strategy</div>
                                    <div className="text-sm">
                                        <div>Count: {optimalParams.retry_count}</div>
                                        <div>Backoff: {optimalParams.backoff_ms}ms</div>
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            )}

            {/* Predictions */}
            <div className="bg-gray-800 rounded-xl border border-gray-700 p-6">
                <div className="flex items-center gap-3 mb-6">
                    <BarChart3 className="w-6 h-6 text-orange-400" />
                    <h3 className="text-xl font-semibold">6-Hour Propagation Forecast</h3>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {predictions.map((prediction, index) => (
                        <div key={index} className="bg-gray-900/50 rounded-lg p-4">
                            <div className="flex items-center justify-between mb-3">
                                <div className="flex items-center gap-2">
                                    {getTimeIcon(prediction.conditions.time_of_day)}
                                    <span className="font-medium">+{prediction.hours_ahead}h</span>
                                </div>
                                <div className="text-xs text-gray-400">
                                    {new Date(prediction.time).toLocaleTimeString()}
                                </div>
                            </div>

                            <div className="space-y-2 text-sm">
                                <div className="flex justify-between">
                                    <span className="text-gray-400">Range:</span>
                                    <span className={`font-medium ${prediction.expected_performance.range_multiplier > 2 ? 'text-green-400' : 'text-yellow-400'
                                        }`}>
                                        {(prediction.expected_performance.range_multiplier * 100).toFixed(0)}%
                                    </span>
                                </div>

                                <div className="flex justify-between">
                                    <span className="text-gray-400">Absorption:</span>
                                    <span className="font-medium text-red-400">
                                        {prediction.expected_performance.signal_absorption}
                                    </span>
                                </div>

                                <div className="mt-2 p-2 bg-gray-800 rounded text-xs text-center">
                                    {prediction.expected_performance.optimal_strategy}
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* Network Optimization Report */}
            {networkReport && (
                <div className="bg-gray-800 rounded-xl border border-gray-700 p-6">
                    <div className="flex items-center gap-3 mb-6">
                        <TrendingUp className="w-6 h-6 text-blue-400" />
                        <h3 className="text-xl font-semibold">Network Optimization Report</h3>
                    </div>

                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        <div>
                            <div className="text-sm text-gray-400 mb-2">Current Performance</div>
                            <div className="text-2xl font-bold text-green-400 mb-4">{networkReport.current_performance}</div>

                            <div className="text-sm text-gray-400 mb-2">Recommendations</div>
                            <div className="space-y-2">
                                {networkReport.recommendations.map((rec: string, index: number) => (
                                    <div key={index} className="flex items-start gap-2 text-sm">
                                        <CheckCircle className="w-4 h-4 text-green-400 mt-0.5 flex-shrink-0" />
                                        <span>{rec}</span>
                                    </div>
                                ))}
                            </div>
                        </div>

                        <div>
                            <div className="text-sm text-gray-400 mb-2">Predicted Changes (Next 3 Hours)</div>
                            <div className="space-y-3">
                                {networkReport.predicted_changes.map((change: any, index: number) => (
                                    <div key={index} className="bg-gray-900/50 rounded-lg p-3">
                                        <div className="flex items-center justify-between mb-2">
                                            <span className="font-medium">{change.time}</span>
                                            <span className={`text-sm ${change.expected_range_change.includes('+') ? 'text-green-400' : 'text-yellow-400'
                                                }`}>
                                                {change.expected_range_change}
                                            </span>
                                        </div>
                                        <div className="text-xs text-gray-400">
                                            {change.suggested_actions.join(' • ')}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default RadioPropagationDashboard;
