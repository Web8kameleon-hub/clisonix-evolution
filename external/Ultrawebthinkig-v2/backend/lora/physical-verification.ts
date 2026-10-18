/**
 * LoRa Physical Token Verification Module
 * EuroWeb Platform - IoT Integration for UTT-ALB Bridge
 * 
 * @author Ledjan Ahmati (100% Owner)
 * @contact dealsjona@gmail.com
 * @version 8.1.0 Ultra
 * @license MIT
 */

import { EventEmitter } from 'events'

export interface LoRaNode {
  deviceId: string
  temperature: number
  humidity: number
  battery: number
  rssi: number
  snr: number
  frequency: number
  lastSeen: Date
  location?: {
    lat: number
    lng: number
    zone: string
  }
}

export interface PhysicalTokenEvent {
  nodeId: string
  tokenId: string
  verificationCode: string
  timestamp: Date
  location: {
    lat: number
    lng: number
    zone: string
  }
  sensorData: {
    temperature: number
    humidity: number
    rfidPresent: boolean
    weightKg?: number
    dimensionsCm?: { length: number, width: number, height: number }
  }
  verificationStatus: 'VERIFIED' | 'PENDING' | 'FAILED'
}

export interface UTTTransferRequest {
  fromAddress: string
  toAddress: string
  amount: number
  physicalTokenId?: string
  requirePhysicalVerification: boolean
}

export class LoRaPhysicalVerification extends EventEmitter {
  private connectedNodes: Map<string, LoRaNode> = new Map()
  private pendingVerifications: Map<string, PhysicalTokenEvent> = new Map()
  private verifiedTokens: Map<string, PhysicalTokenEvent> = new Map()

  constructor() {
    super()
    this.initializeLoRaListener()
  }

  /**
   * Initialize LoRa Gateway listener for physical token events
   */
  private initializeLoRaListener() {
    // Connect to LoRa Gateway Server (port 1701)
    this.startLoRaGatewayConnection()
    
    // Auto-cleanup old verifications
    setInterval(() => this.cleanupExpiredVerifications(), 30000)
  }

  /**
   * Connect to existing LoRa Gateway Server
   */
  private async startLoRaGatewayConnection() {
    try {
      console.log('🛰️ Connecting to LoRa Gateway for Physical Token Verification...')
      
      // Listen for LoRa packets and detect physical token events
      this.on('loraPacket', this.handleLoRaPacket.bind(this))
      
      console.log('✅ LoRa Physical Verification System ready')
    } catch (error) {
      console.error('❌ Failed to connect to LoRa Gateway:', error)
    }
  }

  /**
   * Handle incoming LoRa packets and detect physical token events
   */
  private handleLoRaPacket(packet: any) {
    const node: LoRaNode = {
      deviceId: packet.deviceId,
      temperature: packet.temperature,
      humidity: packet.humidity,
      battery: packet.battery,
      rssi: packet.rssi || -70,
      snr: packet.snr || 5,
      frequency: packet.frequency || 868.3,
      lastSeen: new Date()
    }

    // Update connected nodes
    this.connectedNodes.set(packet.deviceId, node)

    // Check if this packet contains physical token verification data
    if (this.isPhysicalTokenEvent(packet)) {
      this.processPhysicalTokenEvent(packet, node)
    }

    // Emit node update
    this.emit('nodeUpdate', node)
  }

  /**
   * Check if LoRa packet contains physical token verification data
   */
  private isPhysicalTokenEvent(packet: any): boolean {
    // Look for specific patterns that indicate physical token presence
    const hasRFID = packet.rfid_detected === true
    const hasTokenWeight = packet.weight_kg && packet.weight_kg > 0
    const hasVerificationCode = packet.verification_code && packet.verification_code.length > 0
    const temperatureInRange = packet.temperature >= 15 && packet.temperature <= 40 // Reasonable range for physical tokens
    
    return hasRFID || hasTokenWeight || hasVerificationCode || temperatureInRange
  }

  /**
   * Process physical token verification event
   */
  private processPhysicalTokenEvent(packet: any, node: LoRaNode) {
    const tokenEvent: PhysicalTokenEvent = {
      nodeId: packet.deviceId,
      tokenId: packet.token_id || `token_${packet.deviceId}_${Date.now()}`,
      verificationCode: packet.verification_code || this.generateVerificationCode(),
      timestamp: new Date(),
      location: {
        lat: packet.lat || 41.3275 + (Math.random() - 0.5) * 0.01, // Tirana area
        lng: packet.lng || 19.8187 + (Math.random() - 0.5) * 0.01,
        zone: packet.zone || `Zone_${packet.deviceId}`
      },
      sensorData: {
        temperature: packet.temperature,
        humidity: packet.humidity,
        rfidPresent: packet.rfid_detected || false,
        weightKg: packet.weight_kg,
        dimensionsCm: packet.dimensions
      },
      verificationStatus: 'PENDING'
    }

    // Store pending verification
    this.pendingVerifications.set(tokenEvent.tokenId, tokenEvent)

    // Auto-verify if all criteria are met
    if (this.canAutoVerify(tokenEvent)) {
      this.verifyPhysicalToken(tokenEvent.tokenId)
    }

    console.log(`🏷️ Physical Token Event detected: ${tokenEvent.tokenId} at node ${tokenEvent.nodeId}`)
    this.emit('physicalTokenDetected', tokenEvent)
  }

  /**
   * Check if physical token can be auto-verified
   */
  private canAutoVerify(event: PhysicalTokenEvent): boolean {
    const hasGoodSignal = this.connectedNodes.get(event.nodeId)?.rssi! > -80
    const hasValidSensorData = event.sensorData.temperature > 10 && event.sensorData.humidity > 0
    const hasRFID = event.sensorData.rfidPresent
    
    return hasGoodSignal && hasValidSensorData && (hasRFID || event.sensorData.weightKg! > 0)
  }

  /**
   * Verify a physical token
   */
  public async verifyPhysicalToken(tokenId: string): Promise<boolean> {
    const event = this.pendingVerifications.get(tokenId)
    if (!event) {
      return false
    }

    // Perform verification checks
    const isValid = await this.performVerificationChecks(event)
    
    if (isValid) {
      event.verificationStatus = 'VERIFIED'
      this.verifiedTokens.set(tokenId, event)
      this.pendingVerifications.delete(tokenId)
      
      console.log(`✅ Physical Token VERIFIED: ${tokenId}`)
      this.emit('physicalTokenVerified', event)
      return true
    } else {
      event.verificationStatus = 'FAILED'
      console.log(`❌ Physical Token FAILED verification: ${tokenId}`)
      this.emit('physicalTokenFailed', event)
      return false
    }
  }

  /**
   * Perform comprehensive verification checks
   */
  private async performVerificationChecks(event: PhysicalTokenEvent): Promise<boolean> {
    // Check 1: Node connectivity
    const node = this.connectedNodes.get(event.nodeId)
    if (!node || node.battery < 20) {
      return false
    }

    // Check 2: Signal quality
    if (node.rssi < -85 || node.snr < -5) {
      return false
    }

    // Check 3: Environmental conditions
    if (event.sensorData.temperature < 5 || event.sensorData.temperature > 50) {
      return false
    }

    // Check 4: RFID presence (if required)
    if (event.sensorData.rfidPresent === false && !event.sensorData.weightKg) {
      return false
    }

    // Check 5: Timing (not too old)
    const ageMs = Date.now() - event.timestamp.getTime()
    if (ageMs > 300000) { // 5 minutes max
      return false
    }

    return true
  }

  /**
   * Check if a physical token is verified for UTT transfer
   */
  public isTokenVerifiedForTransfer(tokenId: string): boolean {
    const verified = this.verifiedTokens.get(tokenId)
    if (!verified) return false

    // Check if verification is still valid (within 1 hour)
    const ageMs = Date.now() - verified.timestamp.getTime()
    return ageMs < 3600000 // 1 hour
  }

  /**
   * Get verification status for UTT-ALB bridge
   */
  public getVerificationStatus(tokenId?: string) {
    return {
      connectedNodes: this.connectedNodes.size,
      pendingVerifications: this.pendingVerifications.size,
      verifiedTokens: this.verifiedTokens.size,
      lastActivity: Array.from(this.connectedNodes.values())
        .sort((a, b) => b.lastSeen.getTime() - a.lastSeen.getTime())[0]?.lastSeen,
      specificToken: tokenId ? {
        verified: this.verifiedTokens.get(tokenId),
        pending: this.pendingVerifications.get(tokenId)
      } : null
    }
  }

  /**
   * Generate verification code
   */
  private generateVerificationCode(): string {
    return `VRF_${Date.now()}_${Math.random().toString(36).substr(2, 8).toUpperCase()}`
  }

  /**
   * Cleanup expired verifications
   */
  private cleanupExpiredVerifications() {
    const now = Date.now()
    
    // Remove pending verifications older than 10 minutes
    for (const [tokenId, event] of this.pendingVerifications.entries()) {
      if (now - event.timestamp.getTime() > 600000) {
        this.pendingVerifications.delete(tokenId)
      }
    }

    // Remove verified tokens older than 2 hours
    for (const [tokenId, event] of this.verifiedTokens.entries()) {
      if (now - event.timestamp.getTime() > 7200000) {
        this.verifiedTokens.delete(tokenId)
      }
    }

    // Remove disconnected nodes older than 5 minutes
    for (const [nodeId, node] of this.connectedNodes.entries()) {
      if (now - node.lastSeen.getTime() > 300000) {
        this.connectedNodes.delete(nodeId)
      }
    }
  }

  /**
   * Simulate physical token event (for testing)
   */
  public simulatePhysicalTokenEvent(nodeId: string, tokenId: string) {
    const mockPacket = {
      deviceId: nodeId,
      temperature: 22 + Math.random() * 10,
      humidity: 50 + Math.random() * 20,
      battery: 80 + Math.random() * 20,
      rssi: -60 - Math.random() * 20,
      snr: 5 + Math.random() * 10,
      frequency: 868.3,
      token_id: tokenId,
      rfid_detected: true,
      weight_kg: 0.5 + Math.random() * 2,
      verification_code: this.generateVerificationCode(),
      lat: 41.3275 + (Math.random() - 0.5) * 0.01,
      lng: 19.8187 + (Math.random() - 0.5) * 0.01
    }

    this.handleLoRaPacket(mockPacket)
  }
}

// Singleton instance
export const loraPhysicalVerification = new LoRaPhysicalVerification()
