/**
 * EuroWeb Ultra - Radio Propagation Intelligence API
 * 
 * Advanced API for radio wave propagation optimization
 * Adapts transmission parameters based on ionospheric conditions
 * 
 * @author GitHub Copilot & EuroWeb Ultra Team
 * @version 1.0.0 - Radio Intelligence Module
 */

import { globalRadioPropagation } from '@/lib/edge/mesh-radio'
import { NextRequest, NextResponse } from 'next/server'

export async function GET(request: NextRequest) {
    try {
        const { searchParams } = new URL(request.url)
        const action = searchParams.get('action') || 'status'
        const nodeId = searchParams.get('node') || 'gateway-001'
        const hoursAhead = parseInt(searchParams.get('hours') || '6')

        switch (action) {
            case 'status': {
                const currentConditions = globalRadioPropagation.getCurrentConditions()
                const optimizationReport = globalRadioPropagation.getNetworkOptimizationReport()

                return NextResponse.json({
                    success: true,
                    timestamp: new Date().toISOString(),
                    propagation_conditions: currentConditions,
                    network_optimization: optimizationReport,
                    api_version: '1.0.0'
                })
            }

            case 'optimize': {
                const optimalParams = globalRadioPropagation.getOptimalTransmissionParams(nodeId)
                const currentConditions = globalRadioPropagation.getCurrentConditions()

                return NextResponse.json({
                    success: true,
                    target_node: nodeId,
                    current_conditions: currentConditions,
                    optimal_parameters: optimalParams,
                    recommendations: {
                        power_adjustment: optimalParams.tx_power_dbm !== 14 ?
                            `Adjust power to ${optimalParams.tx_power_dbm}dBm` : 'Use default power',
                        data_rate_adjustment: optimalParams.data_rate !== 7 ?
                            `Use SF${optimalParams.data_rate} for optimal balance` : 'Use default SF7',
                        frequency_recommendation: `Optimal frequency: ${optimalParams.frequency_mhz.toFixed(3)}MHz`,
                        confidence_level: `${(optimalParams.confidence * 100).toFixed(1)}% prediction confidence`
                    }
                })
            }

            case 'predict': {
                const predictions = []
                for (let i = 1; i <= Math.min(24, hoursAhead); i++) {
                    const futureConditions = globalRadioPropagation.predictPropagationConditions(i)
                    predictions.push({
                        hours_ahead: i,
                        time: new Date(Date.now() + i * 3600 * 1000).toISOString(),
                        conditions: futureConditions,
                        expected_performance: {
                            range_multiplier: futureConditions.time_of_day === 'night' ? 3.0 : 1.0,
                            signal_absorption: `${futureConditions.signal_absorption_db.toFixed(1)}dB`,
                            optimal_strategy: futureConditions.time_of_day === 'night' ?
                                'Low power, high data rate' : 'High power, robust modulation'
                        }
                    })
                }

                return NextResponse.json({
                    success: true,
                    prediction_horizon_hours: hoursAhead,
                    predictions
                })
            }

            case 'ionosphere': {
                const currentConditions = globalRadioPropagation.getCurrentConditions()

                if (!currentConditions) {
                    return NextResponse.json({
                        success: false,
                        error: 'No propagation data available'
                    }, { status: 503 })
                }

                return NextResponse.json({
                    success: true,
                    ionospheric_data: {
                        dominant_layer: currentConditions.ionospheric_layer,
                        maximum_usable_frequency: `${currentConditions.muf.toFixed(1)} MHz`,
                        predicted_range: `${currentConditions.predicted_range_km.toFixed(1)} km`,
                        signal_absorption: `${currentConditions.signal_absorption_db.toFixed(1)} dB`,
                        solar_activity: {
                            solar_flux: currentConditions.solar_flux,
                            k_index: currentConditions.k_index,
                            sunspot_number: currentConditions.sunspot_number
                        },
                        propagation_summary: {
                            time_of_day: currentConditions.time_of_day,
                            season: currentConditions.season,
                            overall_quality: currentConditions.time_of_day === 'night' ? 'Excellent' :
                                currentConditions.time_of_day === 'day' ? 'Good' : 'Very Good'
                        }
                    }
                })
            }

            case 'update_metrics': {
                // This would be called by mesh nodes to report link quality
                const rssi = parseFloat(searchParams.get('rssi') || '-80')
                const snr = parseFloat(searchParams.get('snr') || '5')
                const packetLoss = parseFloat(searchParams.get('packet_loss') || '0.01')
                const latency = parseFloat(searchParams.get('latency') || '100')

                globalRadioPropagation.updateLinkMetrics(nodeId, {
                    rssi,
                    snr,
                    packet_loss: packetLoss,
                    latency_ms: latency,
                    throughput_bps: 1000, // Example
                    last_updated: Date.now()
                })

                return NextResponse.json({
                    success: true,
                    message: `Updated metrics for node ${nodeId}`,
                    updated_metrics: { rssi, snr, packet_loss: packetLoss, latency }
                })
            }

            default:
                return NextResponse.json({
                    success: false,
                    error: 'Invalid action',
                    available_actions: ['status', 'optimize', 'predict', 'ionosphere', 'update_metrics']
                }, { status: 400 })
        }

    } catch (error) {
        console.error('Radio Propagation API Error:', error)
        return NextResponse.json({
            success: false,
            error: 'Internal server error',
            message: error instanceof Error ? error.message : 'Unknown error'
        }, { status: 500 })
    }
}

export async function POST(request: NextRequest) {
    try {
        const body = await request.json()
        const { action, node_id, metrics } = body

        if (action === 'bulk_update' && metrics) {
            // Bulk update metrics for multiple nodes
            const updates = []
            for (const [nodeId, nodeMetrics] of Object.entries(metrics)) {
                globalRadioPropagation.updateLinkMetrics(nodeId, nodeMetrics as any)
                updates.push(nodeId)
            }

            return NextResponse.json({
                success: true,
                message: `Bulk updated metrics for ${updates.length} nodes`,
                updated_nodes: updates
            })
        }

        if (action === 'network_scan' && node_id) {
            // Simulate a network scan result
            const optimalParams = globalRadioPropagation.getOptimalTransmissionParams(node_id)
            const report = globalRadioPropagation.getNetworkOptimizationReport()

            return NextResponse.json({
                success: true,
                scan_result: {
                    target_node: node_id,
                    optimal_parameters: optimalParams,
                    network_health: report.current_performance,
                    recommendations: report.recommendations,
                    next_optimization_window: '15 minutes'
                }
            })
        }

        return NextResponse.json({
            success: false,
            error: 'Invalid POST action',
            available_actions: ['bulk_update', 'network_scan']
        }, { status: 400 })

    } catch (error) {
        console.error('Radio Propagation POST Error:', error)
        return NextResponse.json({
            success: false,
            error: 'Internal server error',
            message: error instanceof Error ? error.message : 'Unknown error'
        }, { status: 500 })
    }
}
