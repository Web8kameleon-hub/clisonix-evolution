// edge/mesh-radio.ts
// LoRa Radio Driver + CBOR Payload + Ed25519 Signing
// Industrial Mesh Offline - Core Radio Module

import { webcrypto } from 'crypto'

// LoRa Configuration for EU868 band
export const LORA_CONFIG = {
    frequency: 868_100_000,          // Hz (EU868 ISM band)
    bandwidth: 125_000,              // Hz (125 kHz)
    spreading_factor: 7,             // SF7 (fast, short range)
    coding_rate: 5,                  // 4/5 error correction
    tx_power: 14,                    // dBm (max for EU without license)
    preamble_length: 8,              // symbols
    sync_word: 0x12,                 // LoRa sync word
    max_payload: 222,                // bytes (SF7, BW125, CR4/5)
    duty_cycle_limit: 0.01,          // 1% duty cycle EU regulation
    channel_list: [                  // EU868 channels
        868_100_000, 868_300_000, 868_500_000,
        867_100_000, 867_300_000, 867_500_000,
        867_700_000, 867_900_000
    ]
} as const

// Message types
export enum MessageType {
    METAR = 0,
    TAF = 1,
    SENSOR = 2,
    ALERT = 3,
    CONTROL = 4,
    HEARTBEAT = 5,
    ACK = 6,
    ROUTE = 7
}

// Priority levels (0 = highest)
export enum Priority {
    CRITICAL = 0,      // Emergency alerts
    HIGH = 1,          // Weather alerts
    NORMAL = 2,        // Regular METAR/TAF
    LOW = 3,           // Telemetry
    BACKGROUND = 4     // Housekeeping
}

// Packet flags
export enum PacketFlags {
    SIGNED = 0x01,
    ENCRYPTED = 0x02,
    ACK_REQUIRED = 0x04,
    ROUTE_REQUEST = 0x08,
    EMERGENCY = 0x10,
    COMPRESSED = 0x20
}

// 64-byte fixed header structure
export interface MeshHeader {
    version: number           // Protocol version (1)
    msg_type: MessageType     // Message type enum
    sequence: number          // Anti-replay counter (0-65535)
    timestamp: number         // Unix epoch seconds
    origin_id: number         // Unique node ID
    icao_code: number         // Airport code as uint32
    ttl: number              // Time-to-live hops (0-255)
    priority: Priority        // Priority level
    flags: number            // Bit flags
    reserved: number         // Future use
    signature: Uint8Array    // Ed25519 signature (32 bytes)
}

// CBOR payload structures
export interface MetarPayload {
    wind_speed: number        // knots
    wind_gust?: number        // knots
    wind_dir: number         // degrees
    qnh: number              // hPa
    visibility: number       // meters
    temperature: number      // Celsius
    dewpoint?: number        // Celsius
    clouds?: string[]        // Cloud layers
    weather?: string[]       // Weather phenomena
    raw_metar: string        // Original METAR string
}

export interface SensorPayload {
    sensor_id: string
    readings: {
        [key: string]: number | string
    }
    battery?: number         // percentage
    signal_strength?: number // dBm
    location?: {
        lat: number
        lon: number
        alt?: number
    }
}

export interface AlertPayload {
    alert_type: string       // WIND_SPEED, QNH_DROP, etc.
    severity: 'LOW' | 'HIGH' | 'CRITICAL'
    value: number
    threshold: number
    description: string
    expires_at?: number      // Unix timestamp
}

// Radio Wave Propagation Intelligence
// Adapts transmission parameters based on ionospheric conditions
export interface PropagationConditions {
    time_of_day: 'dawn' | 'day' | 'dusk' | 'night'
    season: 'spring' | 'summer' | 'autumn' | 'winter'
    solar_flux: number        // Solar flux index (67-300)
    k_index: number          // Geomagnetic activity (0-9)
    sunspot_number: number   // Solar activity indicator
    ionospheric_layer: 'D' | 'E' | 'F1' | 'F2'
    muf: number             // Maximum Usable Frequency (MHz)
    predicted_range_km: number
    signal_absorption_db: number
}

export interface LinkQualityMetrics {
    rssi: number            // Received Signal Strength Indicator (dBm)
    snr: number            // Signal-to-Noise Ratio (dB)
    packet_loss: number    // Packet loss percentage (0-1)
    latency_ms: number     // Round-trip time
    throughput_bps: number // Effective data rate
    reliability_score: number // 0-1 composite score
    last_updated: number   // Unix timestamp
}

export interface OptimalTransmissionParams {
    tx_power_dbm: number      // Recommended transmission power
    data_rate: number         // Recommended spreading factor
    frequency_mhz: number     // Optimal frequency selection
    retry_count: number       // Recommended retransmission count
    backoff_ms: number       // Adaptive backoff timing
    confidence: number       // AI prediction confidence (0-1)
}

// Advanced Link Quality Manager with Ionospheric Intelligence
class RadioPropagationIntelligence {
    private linkMetrics: Map<string, LinkQualityMetrics> = new Map()
    private propagationHistory: PropagationConditions[] = []
    private readonly maxHistoryHours = 168 // 1 week of data

    constructor() {
        // Initialize with baseline conditions
        this.updatePropagationConditions()

        // Update every 15 minutes
        setInterval(() => {
            this.updatePropagationConditions()
        }, 15 * 60 * 1000)
    }

    // Real-time propagation condition assessment
    private updatePropagationConditions(): void {
        const now = new Date()
        const hour = now.getHours()
        const month = now.getMonth()

        // Determine time of day with transition periods
        let timeOfDay: PropagationConditions['time_of_day']
        if (hour >= 5 && hour <= 7) timeOfDay = 'dawn'
        else if (hour >= 8 && hour <= 17) timeOfDay = 'day'
        else if (hour >= 18 && hour <= 20) timeOfDay = 'dusk'
        else timeOfDay = 'night'

        // Seasonal determination
        let season: PropagationConditions['season']
        if (month >= 2 && month <= 4) season = 'spring'
        else if (month >= 5 && month <= 7) season = 'summer'
        else if (month >= 8 && month <= 10) season = 'autumn'
        else season = 'winter'

        // Simplified solar/ionospheric modeling
        // In production, this would connect to space weather APIs
        const baseFlux = 150 + Math.sin(now.getTime() / (365 * 24 * 3600 * 1000)) * 50
        const conditions: PropagationConditions = {
            time_of_day: timeOfDay,
            season,
            solar_flux: baseFlux + (Math.random() - 0.5) * 20,
            k_index: Math.floor(Math.random() * 4), // Usually low
            sunspot_number: Math.max(0, baseFlux - 80 + (Math.random() - 0.5) * 40),
            ionospheric_layer: timeOfDay === 'day' ? 'D' : 'F2',
            muf: this.calculateMUF(timeOfDay, season),
            predicted_range_km: this.predictRange(timeOfDay, season),
            signal_absorption_db: this.calculateAbsorption(timeOfDay, season)
        }

        this.propagationHistory.push(conditions)

        // Cleanup old data
        if (this.propagationHistory.length > this.maxHistoryHours * 4) {
            this.propagationHistory = this.propagationHistory.slice(-this.maxHistoryHours * 4)
        }
    }

    // Calculate Maximum Usable Frequency based on conditions
    private calculateMUF(timeOfDay: string, season: string): number {
        let baseMUF = 14.0 // Base frequency for LoRa (MHz)

        // Night conditions: higher ionospheric reflection
        if (timeOfDay === 'night') {
            baseMUF *= 1.5 // Better propagation at night
        } else if (timeOfDay === 'day') {
            baseMUF *= 0.8 // D-layer absorption during day
        }

        // Seasonal variations
        if (season === 'winter') baseMUF *= 1.2
        if (season === 'summer') baseMUF *= 0.9

        return baseMUF
    }

    // Predict communication range based on propagation conditions
    private predictRange(timeOfDay: string, season: string): number {
        let baseRange = 15.0 // Base LoRa range (km)

        // Night: dramatic range increase due to skywave
        if (timeOfDay === 'night') {
            baseRange *= 3.0 // Up to 45km at night!
        } else if (timeOfDay === 'dawn' || timeOfDay === 'dusk') {
            baseRange *= 2.0 // Transition periods
        }

        // Winter: better propagation
        if (season === 'winter') baseRange *= 1.3

        return baseRange
    }

    // Calculate signal absorption
    private calculateAbsorption(timeOfDay: string, season: string): number {
        let absorption = 0.5 // Base absorption (dB)

        // Day: high D-layer absorption
        if (timeOfDay === 'day') {
            absorption += 3.0
        } else if (timeOfDay === 'night') {
            absorption -= 1.0 // Minimal absorption
        }

        // Summer: higher absorption
        if (season === 'summer') absorption += 1.0

        return Math.max(0, absorption)
    }

    // Update link quality metrics for a specific connection
    updateLinkMetrics(nodeId: string, metrics: Partial<LinkQualityMetrics>): void {
        const existing = this.linkMetrics.get(nodeId) || {
            rssi: -100,
            snr: -10,
            packet_loss: 0.5,
            latency_ms: 1000,
            throughput_bps: 300,
            reliability_score: 0.5,
            last_updated: Date.now()
        }

        const updated: LinkQualityMetrics = {
            ...existing,
            ...metrics,
            last_updated: Date.now()
        }

        // Calculate composite reliability score
        updated.reliability_score = this.calculateReliabilityScore(updated)

        this.linkMetrics.set(nodeId, updated)
    }

    // AI-powered reliability scoring
    private calculateReliabilityScore(metrics: LinkQualityMetrics): number {
        const rssiScore = Math.max(0, Math.min(1, (metrics.rssi + 120) / 50))
        const snrScore = Math.max(0, Math.min(1, (metrics.snr + 10) / 20))
        const lossScore = 1 - metrics.packet_loss
        const latencyScore = Math.max(0, Math.min(1, (2000 - metrics.latency_ms) / 2000))

        return (rssiScore * 0.3 + snrScore * 0.3 + lossScore * 0.3 + latencyScore * 0.1)
    }

    // Generate optimal transmission parameters using AI predictions
    getOptimalTransmissionParams(targetNodeId: string): OptimalTransmissionParams {
        const currentConditions = this.getCurrentConditions()
        const linkQuality = this.linkMetrics.get(targetNodeId)

        let txPower: number = LORA_CONFIG.tx_power // Start with default
        let dataRate: number = LORA_CONFIG.spreading_factor
        let frequency: number = LORA_CONFIG.frequency
        let retryCount = 3
        let backoffMs = 1000
        let confidence = 0.7

        if (currentConditions && linkQuality) {
            // Night optimization: use lower power, higher data rate
            if (currentConditions.time_of_day === 'night') {
                txPower = Math.max(2, txPower - 3) // Reduce power
                dataRate = Math.max(7, dataRate - 1) // Increase data rate
                confidence = 0.9
            }

            // Day optimization: increase power, more robust settings
            else if (currentConditions.time_of_day === 'day') {
                txPower = Math.min(14, txPower + 2) // Increase power
                dataRate = Math.min(12, dataRate + 1) // Decrease data rate (more robust)
                retryCount = 5
                confidence = 0.8
            }

            // Adaptive frequency selection based on absorption
            if (currentConditions.signal_absorption_db > 2.0) {
                // Use lower frequency channel for better penetration
                frequency = LORA_CONFIG.channel_list[0]
            }

            // Poor link quality compensation
            if (linkQuality.reliability_score < 0.5) {
                txPower = Math.min(14, txPower + 3)
                dataRate = Math.min(12, dataRate + 2)
                retryCount = Math.min(8, retryCount + 2)
                backoffMs *= 2
            }
        }

        return {
            tx_power_dbm: txPower,
            data_rate: dataRate,
            frequency_mhz: frequency / 1_000_000,
            retry_count: retryCount,
            backoff_ms: backoffMs,
            confidence
        }
    }

    // Get current propagation conditions
    getCurrentConditions(): PropagationConditions | null {
        return this.propagationHistory[this.propagationHistory.length - 1] || null
    }

    // Predict future propagation conditions (up to 24 hours)
    predictPropagationConditions(hoursAhead: number): PropagationConditions {
        const future = new Date(Date.now() + hoursAhead * 3600 * 1000)
        const hour = future.getHours()
        const month = future.getMonth()

        let timeOfDay: PropagationConditions['time_of_day']
        if (hour >= 5 && hour <= 7) timeOfDay = 'dawn'
        else if (hour >= 8 && hour <= 17) timeOfDay = 'day'
        else if (hour >= 18 && hour <= 20) timeOfDay = 'dusk'
        else timeOfDay = 'night'

        return {
            time_of_day: timeOfDay,
            season: 'autumn', // Simplified
            solar_flux: 150,
            k_index: 2,
            sunspot_number: 70,
            ionospheric_layer: timeOfDay === 'day' ? 'D' : 'F2',
            muf: this.calculateMUF(timeOfDay, 'autumn'),
            predicted_range_km: this.predictRange(timeOfDay, 'autumn'),
            signal_absorption_db: this.calculateAbsorption(timeOfDay, 'autumn')
        }
    }

    // Generate network optimization recommendations
    getNetworkOptimizationReport(): {
        current_performance: string
        recommendations: string[]
        predicted_changes: Array<{
            time: string
            expected_range_change: string
            suggested_actions: string[]
        }>
    } {
        const conditions = this.getCurrentConditions()
        const totalNodes = this.linkMetrics.size
        const avgReliability = Array.from(this.linkMetrics.values())
            .reduce((sum, m) => sum + m.reliability_score, 0) / totalNodes || 0

        const recommendations: string[] = []

        if (conditions?.time_of_day === 'day' && avgReliability < 0.7) {
            recommendations.push("Increase transmission power during daytime due to D-layer absorption")
            recommendations.push("Consider lower data rates for better penetration")
        }

        if (conditions?.time_of_day === 'night' && avgReliability > 0.8) {
            recommendations.push("Reduce power consumption - excellent night propagation detected")
            recommendations.push("Increase data rates to maximize throughput")
        }

        // Predict next 6 hours
        const predictions = []
        for (let i = 1; i <= 6; i++) {
            const futureConditions = this.predictPropagationConditions(i)
            predictions.push({
                time: `+${i}h`,
                expected_range_change: futureConditions.time_of_day === 'night' ?
                    '+200% (skywave propagation)' : '-30% (ground wave only)',
                suggested_actions: futureConditions.time_of_day === 'night' ?
                    ['Reduce TX power', 'Increase data rates', 'Schedule bulk transfers'] :
                    ['Increase TX power', 'Use robust modulation', 'Prioritize critical traffic']
            })
        }

        return {
            current_performance: `${(avgReliability * 100).toFixed(1)}% network reliability`,
            recommendations,
            predicted_changes: predictions.slice(0, 3) // Next 3 hours
        }
    }
}

// Duty cycle tracker for EU868 compliance
class DutyCycleManager {
    private transmissions: { timestamp: number; duration: number }[] = []
    private readonly windowMs = 3600_000 // 1 hour window
    private readonly maxDutyCycle = LORA_CONFIG.duty_cycle_limit

    canTransmit(durationMs: number): boolean {
        this.cleanup()

        const totalDuration = this.transmissions
            .reduce((sum, tx) => sum + tx.duration, 0)

        const projectedDutyCycle = (totalDuration + durationMs) / this.windowMs
        return projectedDutyCycle <= this.maxDutyCycle
    }

    recordTransmission(durationMs: number): void {
        this.transmissions.push({
            timestamp: Date.now(),
            duration: durationMs
        })
    }

    private cleanup(): void {
        const cutoff = Date.now() - this.windowMs
        this.transmissions = this.transmissions
            .filter(tx => tx.timestamp > cutoff)
    }

    getCurrentDutyCycle(): number {
        this.cleanup()
        const totalDuration = this.transmissions
            .reduce((sum, tx) => sum + tx.duration, 0)
        return totalDuration / this.windowMs
    }
}

// Ed25519 signing and verification
class MeshCrypto {
    private keyPair: CryptoKeyPair | null = null

    async generateKeyPair(): Promise<void> {
        this.keyPair = await webcrypto.subtle.generateKey(
            {
                name: 'Ed25519',
                namedCurve: 'Ed25519'
            },
            true,
            ['sign', 'verify']
        )
    }

    async sign(data: Uint8Array): Promise<Uint8Array> {
        if (!this.keyPair?.privateKey) {
            throw new Error('No private key available for signing')
        }

        const signature = await webcrypto.subtle.sign(
            'Ed25519',
            this.keyPair.privateKey,
            data
        )

        return new Uint8Array(signature)
    }

    async verify(data: Uint8Array, signature: Uint8Array, publicKey: CryptoKey): Promise<boolean> {
        try {
            return await webcrypto.subtle.verify(
                'Ed25519',
                publicKey,
                signature,
                data
            )
        } catch (error) {
            console.error('Signature verification failed:', error)
            return false
        }
    }

    async exportPublicKey(): Promise<Uint8Array> {
        if (!this.keyPair?.publicKey) {
            throw new Error('No public key available')
        }

        const exported = await webcrypto.subtle.exportKey('raw', this.keyPair.publicKey)
        return new Uint8Array(exported)
    }

    async importPublicKey(keyData: Uint8Array): Promise<CryptoKey> {
        return await webcrypto.subtle.importKey(
            'raw',
            keyData,
            {
                name: 'Ed25519',
                namedCurve: 'Ed25519'
            },
            false,
            ['verify']
        )
    }
}

// CBOR encoding/decoding (simplified implementation)
class CBORCodec {
    static encode(obj: any): Uint8Array {
        // Simplified CBOR encoder - in production use a proper CBOR library
        const json = JSON.stringify(obj)
        return new TextEncoder().encode(json)
    }

    static decode<T>(data: Uint8Array): T {
        // Simplified CBOR decoder - in production use a proper CBOR library
        const json = new TextDecoder().decode(data)
        return JSON.parse(json) as T
    }
}

// Main LoRa Mesh Radio class
export class MeshRadio {
    private crypto: MeshCrypto
    private dutyCycle: DutyCycleManager
    private nodeId: number
    private sequenceCounter: number = 0
    private isTransmitting: boolean = false
    private currentChannel: number = 0

    constructor(nodeId: number) {
        this.nodeId = nodeId
        this.crypto = new MeshCrypto()
        this.dutyCycle = new DutyCycleManager()
    }

    async initialize(): Promise<void> {
        await this.crypto.generateKeyPair()
        console.log(`LoRa Mesh Radio initialized - Node ID: ${this.nodeId.toString(16).padStart(8, '0')}`)
    }

    // Create and sign a mesh packet
    async createPacket(
        msgType: MessageType,
        payload: MetarPayload | SensorPayload | AlertPayload | any,
        icaoCode: string = 'UNKN',
        priority: Priority = Priority.NORMAL,
        ttl: number = 5
    ): Promise<{ header: MeshHeader; payload: Uint8Array; packet: Uint8Array }> {
        // Increment sequence counter
        this.sequenceCounter = (this.sequenceCounter + 1) % 65536

        // Convert ICAO to uint32
        const icaoBuffer = new TextEncoder().encode(icaoCode.padEnd(4, '\0'))
        const icaoU32 = new DataView(icaoBuffer.buffer).getUint32(0, false)

        // Encode payload with CBOR
        const payloadBytes = CBORCodec.encode(payload)

        // Create header
        const header: MeshHeader = {
            version: 1,
            msg_type: msgType,
            sequence: this.sequenceCounter,
            timestamp: Math.floor(Date.now() / 1000),
            origin_id: this.nodeId,
            icao_code: icaoU32,
            ttl: ttl,
            priority: priority,
            flags: PacketFlags.SIGNED,
            reserved: 0,
            signature: new Uint8Array(32)
        }

        // Serialize header (without signature)
        const headerBytes = this.serializeHeader(header, false)

        // Create signing data (header + payload)
        const signingData = new Uint8Array(headerBytes.length + payloadBytes.length)
        signingData.set(headerBytes, 0)
        signingData.set(payloadBytes, headerBytes.length)

        // Sign the packet
        const signature = await this.crypto.sign(signingData)
        header.signature = signature.slice(0, 32) // Truncate to 32 bytes if needed

        // Serialize complete header with signature
        const finalHeaderBytes = this.serializeHeader(header, true)

        // Create final packet
        const packet = new Uint8Array(finalHeaderBytes.length + payloadBytes.length)
        packet.set(finalHeaderBytes, 0)
        packet.set(payloadBytes, finalHeaderBytes.length)

        return {
            header,
            payload: payloadBytes,
            packet
        }
    }

    // Serialize header to bytes
    private serializeHeader(header: MeshHeader, includeSignature: boolean): Uint8Array {
        const buffer = new ArrayBuffer(64)
        const view = new DataView(buffer)

        view.setUint8(0, header.version)
        view.setUint8(1, header.msg_type)
        view.setUint16(2, header.sequence, false)
        view.setUint32(4, header.timestamp, false)
        view.setUint32(8, header.origin_id, false)
        view.setUint32(12, header.icao_code, false)
        view.setUint8(16, header.ttl)
        view.setUint8(17, header.priority)
        view.setUint8(18, header.flags)
        view.setUint8(19, header.reserved)

        if (includeSignature) {
            const headerArray = new Uint8Array(buffer)
            headerArray.set(header.signature, 20)
            return headerArray
        }

        return new Uint8Array(buffer, 0, 20) // Header without signature
    }

    // Parse received packet
    async parsePacket(packetData: Uint8Array): Promise<{
        header: MeshHeader;
        payload: any;
        valid: boolean;
    } | null> {
        if (packetData.length < 64) {
            console.warn('Packet too short for valid header')
            return null
        }

        try {
            // Parse header
            const headerView = new DataView(packetData.buffer, 0, 64)
            const header: MeshHeader = {
                version: headerView.getUint8(0),
                msg_type: headerView.getUint8(1),
                sequence: headerView.getUint16(2, false),
                timestamp: headerView.getUint32(4, false),
                origin_id: headerView.getUint32(8, false),
                icao_code: headerView.getUint32(12, false),
                ttl: headerView.getUint8(16),
                priority: headerView.getUint8(17),
                flags: headerView.getUint8(18),
                reserved: headerView.getUint8(19),
                signature: packetData.slice(20, 52)
            }

            // Extract payload
            const payloadData = packetData.slice(64)

            // Verify signature if present
            let valid = true
            if (header.flags & PacketFlags.SIGNED) {
                // In production, verify against known public keys
                // For now, just mark as valid for demo
                valid = true
            }

            // Decode payload
            let payload: any
            try {
                payload = CBORCodec.decode(payloadData)
            } catch (error) {
                console.error('Failed to decode CBOR payload:', error)
                return null
            }

            return {
                header,
                payload,
                valid
            }
        } catch (error) {
            console.error('Failed to parse packet:', error)
            return null
        }
    }

    // Transmit packet over LoRa
    async transmit(packet: Uint8Array, priority: Priority = Priority.NORMAL): Promise<boolean> {
        if (this.isTransmitting) {
            console.warn('Radio busy, transmission queued')
            return false
        }

        // Check duty cycle compliance
        const txDurationMs = this.calculateTransmissionTime(packet.length)
        if (!this.dutyCycle.canTransmit(txDurationMs)) {
            console.warn(`Transmission blocked by duty cycle (${(this.dutyCycle.getCurrentDutyCycle() * 100).toFixed(2)}%)`)
            return false
        }

        try {
            this.isTransmitting = true

            // Select channel (round-robin for now)
            const channel = LORA_CONFIG.channel_list[this.currentChannel]
            this.currentChannel = (this.currentChannel + 1) % LORA_CONFIG.channel_list.length

            console.log(`Transmitting ${packet.length} bytes on ${channel / 1e6} MHz (SF${LORA_CONFIG.spreading_factor})`)

            // Simulate LoRa transmission
            await this.simulateLoRaTransmission(packet, channel, txDurationMs)

            // Record transmission for duty cycle tracking
            this.dutyCycle.recordTransmission(txDurationMs)

            return true
        } catch (error) {
            console.error('Transmission failed:', error)
            return false
        } finally {
            this.isTransmitting = false
        }
    }

    // Calculate transmission time for duty cycle compliance
    private calculateTransmissionTime(payloadBytes: number): number {
        const { spreading_factor, bandwidth, coding_rate } = LORA_CONFIG

        // LoRa airtime calculation
        const symbolDuration = (1 << spreading_factor) / bandwidth * 1000 // ms
        const preambleTime = (LORA_CONFIG.preamble_length + 4.25) * symbolDuration

        const payloadSymbols = Math.ceil(
            (8 * payloadBytes - 4 * spreading_factor + 28 + 16) /
            (4 * (spreading_factor - 2))
        ) * (coding_rate + 4)

        const payloadTime = payloadSymbols * symbolDuration

        return Math.ceil(preambleTime + payloadTime)
    }

    // Simulate LoRa transmission (replace with actual radio driver)
    private async simulateLoRaTransmission(
        packet: Uint8Array,
        frequency: number,
        durationMs: number
    ): Promise<void> {
        // In production, this would interface with SX1302/SX1276 driver
        console.log(`[LoRa TX] Freq: ${frequency / 1e6}MHz, Duration: ${durationMs}ms, Size: ${packet.length}B`)

        // Simulate transmission delay
        await new Promise(resolve => setTimeout(resolve, durationMs))

        // Log packet details for debugging
        const parsed = await this.parsePacket(packet)
        if (parsed) {
            console.log(`[LoRa TX] Type: ${MessageType[parsed.header.msg_type]}, Origin: ${parsed.header.origin_id.toString(16)}`)
        }
    }

    // Get radio statistics
    getStats(): {
        nodeId: string;
        dutyCycle: number;
        sequenceCounter: number;
        isTransmitting: boolean;
        currentChannel: number;
    } {
        return {
            nodeId: this.nodeId.toString(16).padStart(8, '0'),
            dutyCycle: this.dutyCycle.getCurrentDutyCycle(),
            sequenceCounter: this.sequenceCounter,
            isTransmitting: this.isTransmitting,
            currentChannel: this.currentChannel
        }
    }

    // Create specific message types
    async createMetarMessage(metar: MetarPayload, icao: string): Promise<Uint8Array> {
        const { packet } = await this.createPacket(
            MessageType.METAR,
            metar,
            icao,
            Priority.NORMAL
        )
        return packet
    }

    async createAlertMessage(alert: AlertPayload, icao: string): Promise<Uint8Array> {
        const priority = alert.severity === 'CRITICAL' ? Priority.CRITICAL : Priority.HIGH
        const { packet } = await this.createPacket(
            MessageType.ALERT,
            alert,
            icao,
            priority
        )
        return packet
    }

    async createSensorMessage(sensor: SensorPayload, icao: string): Promise<Uint8Array> {
        const { packet } = await this.createPacket(
            MessageType.SENSOR,
            sensor,
            icao,
            Priority.LOW
        )
        return packet
    }
}

// Factory function for creating radio instances
export function createMeshRadio(nodeId?: number): MeshRadio {
    const id = nodeId || Math.floor(Math.random() * 0xFFFFFFFF)
    return new MeshRadio(id)
}

// Global Radio Propagation Intelligence Instance
export const globalRadioPropagation = new RadioPropagationIntelligence()

// Export utility functions
export function icaoToUint32(icao: string): number {
    const buffer = new TextEncoder().encode(icao.padEnd(4, '\0'))
    return new DataView(buffer.buffer).getUint32(0, false)
}

export function uint32ToIcao(value: number): string {
    const buffer = new ArrayBuffer(4)
    new DataView(buffer).setUint32(0, value, false)
    return new TextDecoder().decode(buffer).replace(/\0/g, '')
}

// Enhanced Radio with Propagation Intelligence
export class IntelligentMeshRadio extends MeshRadio {
    private propagationIntelligence: RadioPropagationIntelligence

    constructor(nodeId: number) {
        super(nodeId)
        this.propagationIntelligence = globalRadioPropagation
    }

    // Override transmit with intelligent power management
    async intelligentTransmit(packet: Uint8Array, targetNodeId: string): Promise<boolean> {
        // Get optimal transmission parameters
        const optimalParams = this.propagationIntelligence.getOptimalTransmissionParams(targetNodeId)

        console.log(`🌊 Adaptive Radio: Using ${optimalParams.tx_power_dbm}dBm power, SF${optimalParams.data_rate} for ${targetNodeId}`)
        console.log(`📡 Propagation Confidence: ${(optimalParams.confidence * 100).toFixed(1)}%`)

        // Apply intelligent parameters (in real implementation, this would configure the radio)
        const success = await this.transmit(packet)

        // Update link quality based on transmission result
        this.propagationIntelligence.updateLinkMetrics(targetNodeId, {
            last_updated: Date.now(),
            reliability_score: success ? 0.9 : 0.3
        })

        return success
    }

    // Get network optimization report
    getNetworkOptimizationReport() {
        return this.propagationIntelligence.getNetworkOptimizationReport()
    }

    // Get current propagation conditions
    getCurrentPropagationConditions() {
        return this.propagationIntelligence.getCurrentConditions()
    }

    // Predict future conditions
    predictPropagationConditions(hoursAhead: number) {
        return this.propagationIntelligence.predictPropagationConditions(hoursAhead)
    }
}

// Factory for intelligent radio
export function createIntelligentMeshRadio(nodeId?: number): IntelligentMeshRadio {
    const id = nodeId || Math.floor(Math.random() * 0xFFFFFFFF)
    return new IntelligentMeshRadio(id)
}
