import * as cbor from 'cbor'
import { createHmac } from 'crypto'

export enum NanoGridPayloadType {
  TELEMETRY = 0x01,
  CONFIG = 0x02,
  EVENT = 0x03,
  COMMAND = 0x04,
  CALIBRATION = 0x05,
}

export enum NanoGridModelId {
  ESP32_PRESSURE = 0x10,
  STM32_GAS = 0x20,
  ASIC_MULTI = 0x30,
  RASPBERRY_PI = 0x40,
  CUSTOM_IOT = 0xff,
}

export enum NanoGridSecurityLevel {
  NONE = 0x00,
  STANDARD = 0x01,
  HIGH = 0x02,
  MILITARY = 0x03,
}

export interface NanoGridHeader {
  magic: Buffer
  version: number
  modelId: number
  payloadType: number
  flags: number
  length: number
  timestamp: number
  reserved: number
}

export interface NanoGridPacket {
  header: NanoGridHeader
  payload: Buffer
  mac: Buffer
  raw: Buffer
}

const MAGIC = Buffer.from([0xc1, 0x53])
const VERSION = 0x01
const HEADER_SIZE = 14

export function createNanoGridPacket(
  data: Record<string, unknown>,
  options: {
    modelId?: number
    payloadType?: NanoGridPayloadType
    securityLevel?: NanoGridSecurityLevel
    secret?: string | Buffer
    timestamp?: number
  } = {},
): NanoGridPacket {
  const payload = Buffer.from(cbor.encode(data))
  const securityLevel = options.securityLevel ?? NanoGridSecurityLevel.STANDARD

  const header: NanoGridHeader = {
    magic: MAGIC,
    version: VERSION,
    modelId: options.modelId ?? NanoGridModelId.CUSTOM_IOT,
    payloadType: options.payloadType ?? NanoGridPayloadType.TELEMETRY,
    flags: securityLevel,
    length: payload.length,
    timestamp: options.timestamp ?? Math.floor(Date.now() / 1000),
    reserved: 0,
  }

  const headerBuffer = encodeHeader(header)
  const mac = computeMac(headerBuffer, payload, securityLevel, options.secret)
  const raw = Buffer.concat([headerBuffer, payload, mac])

  return { header, payload, mac, raw }
}

export function parseNanoGridPacket(raw: Buffer): NanoGridPacket {
  if (raw.length < HEADER_SIZE) {
    throw new Error(`Packet too small: ${raw.length}`)
  }

  if (raw[0] !== MAGIC[0] || raw[1] !== MAGIC[1]) {
    throw new Error('Invalid NanoGrid magic bytes')
  }

  const header: NanoGridHeader = {
    magic: raw.subarray(0, 2),
    version: raw[2],
    modelId: raw[3],
    payloadType: raw[4],
    flags: raw[5],
    length: raw.readUInt16BE(6),
    timestamp: raw.readUInt32BE(8),
    reserved: raw.readUInt16BE(12),
  }

  const payloadStart = HEADER_SIZE
  const payloadEnd = payloadStart + header.length
  if (payloadEnd > raw.length) {
    throw new Error('Payload length exceeds packet size')
  }

  const securityLevel = header.flags & 0x0f
  const macSize = securityLevel === NanoGridSecurityLevel.NONE
    ? 2
    : securityLevel === NanoGridSecurityLevel.MILITARY
      ? 32
      : 16

  const mac = raw.subarray(payloadEnd, payloadEnd + macSize)
  const payload = raw.subarray(payloadStart, payloadEnd)

  return { header, payload, mac, raw }
}

export function decodeNanoGridPayload<T = Record<string, unknown>>(packet: NanoGridPacket): T {
  return cbor.decodeFirstSync(packet.payload) as T
}

export function verifyNanoGridPacket(packet: NanoGridPacket, secret?: string | Buffer): boolean {
  const securityLevel = packet.header.flags & 0x0f
  const headerBuffer = encodeHeader(packet.header)
  const expected = computeMac(headerBuffer, packet.payload, securityLevel, secret)
  return expected.equals(packet.mac)
}

export function modelLabel(modelId: number): string {
  switch (modelId) {
    case NanoGridModelId.ESP32_PRESSURE:
      return 'ESP32 Pressure'
    case NanoGridModelId.STM32_GAS:
      return 'STM32 Gas'
    case NanoGridModelId.ASIC_MULTI:
      return 'ASIC Multi'
    case NanoGridModelId.RASPBERRY_PI:
      return 'Raspberry Pi'
    default:
      return 'Custom IoT'
  }
}

function encodeHeader(header: NanoGridHeader): Buffer {
  const buffer = Buffer.alloc(HEADER_SIZE)
  buffer[0] = header.magic[0]
  buffer[1] = header.magic[1]
  buffer[2] = header.version
  buffer[3] = header.modelId
  buffer[4] = header.payloadType
  buffer[5] = header.flags
  buffer.writeUInt16BE(header.length, 6)
  buffer.writeUInt32BE(header.timestamp, 8)
  buffer.writeUInt16BE(header.reserved ?? 0, 12)
  return buffer
}

function computeMac(
  headerBuffer: Buffer,
  payload: Buffer,
  securityLevel: number,
  secret?: string | Buffer,
): Buffer {
  const body = Buffer.concat([headerBuffer, payload])

  if (securityLevel === NanoGridSecurityLevel.NONE) {
    return crc16(body)
  }

  const normalizedSecret = typeof secret === 'string'
    ? Buffer.from(secret, 'utf8')
    : secret ?? Buffer.alloc(32, 0xaa)

  const hmac = createHmac('sha256', normalizedSecret)
  hmac.update(body)
  const digest = hmac.digest()

  if (securityLevel === NanoGridSecurityLevel.MILITARY) {
    return digest
  }

  return digest.subarray(0, 16)
}

function crc16(data: Buffer): Buffer {
  let crc = 0xffff

  for (const byte of data) {
    crc ^= byte << 8
    for (let i = 0; i < 8; i++) {
      if (crc & 0x8000) {
        crc = ((crc << 1) ^ 0x1021) & 0xffff
      } else {
        crc = (crc << 1) & 0xffff
      }
    }
  }

  const result = Buffer.alloc(2)
  result.writeUInt16BE(crc, 0)
  return result
}
