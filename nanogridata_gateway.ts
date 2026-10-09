/**
 * NANOGRIDATA GATEWAY - System Integration
 * Lightweight service that routes embedded device packets to ALBA collector
 */

import { createServer, Socket } from 'net';
import { EventEmitter } from 'events';
import * as cbor from 'cbor';
import { createHmac, timingSafeEqual } from 'crypto';
import axios from 'axios';

// Logger
const log = (level: string, msg: string, data = '') => {
  console.log(`[${level}] ${msg} ${data}`);
};

// Constants
const NANOGRIDATA_PORT = parseInt(process.env.NANOGRIDATA_PORT || '5678');
const ALBA_ENDPOINT = process.env.ALBA_ENDPOINT || 'http://localhost:5555';
const NANOGRIDATA_MAGIC = [0xC1, 0x53];
const NANOGRIDATA_VERSION = 0x01;
const HEADER_SIZE = 14;
const CBOR_MAX_SIZE = 1024;
const CBOR_MAX_STR_LENGTH = 256;
const CBOR_MAX_ARRAY_LENGTH = 64;

// Enums
enum PayloadType {
  TELEMETRY = 0x01,
  CONFIG = 0x02,
  EVENT = 0x03,
  COMMAND = 0x04,
  CALIBRATION = 0x05,
}

enum ModelID {
  ESP32_PRESSURE = 0x10,
  STM32_GAS = 0x20,
  ASIC_MULTI = 0x30,
  RASPBERRY_PI = 0x40,
  CUSTOM_IOT = 0xFF,
}

enum SecurityLevel {
  NONE = 0x00,
  STANDARD = 0x01,
  HIGH = 0x02,
  MILITARY = 0x03,
}

// Types
interface NanogridataHeader {
  magic: number[];
  version: number;
  modelId: number;
  payloadType: number;
  flags: number;
  length: number;
  timestamp: number;
  reserved: number;
}

interface NanogridataPacket {
  header: NanogridataHeader | null;
  payload: Buffer;
  mac: Buffer;
  valid: boolean;
  error?: string;
}

/**
 * Nanogridata Decoder
 */
class NanogridataDecoder extends EventEmitter {
  private replayCache = new Map<string, number>();
  private deviceSecrets = new Map<string, Buffer>();
  private stats = { received: 0, decoded: 0, rejected: 0, bytes: 0 };

  constructor() {
    super();
    this.loadSecrets();
    this.startCleanup();
  }

  private loadSecrets() {
    const esp32Secret = process.env.NANOGRIDATA_ESP32_SECRET;
    const stm32Secret = process.env.NANOGRIDATA_STM32_SECRET;

    if (esp32Secret) {
      this.deviceSecrets.set('16', Buffer.from(esp32Secret, 'hex'));
    }
    if (stm32Secret) {
      this.deviceSecrets.set('32', Buffer.from(stm32Secret, 'hex'));
    }

    log('INFO', 'Device secrets loaded', `count=${this.deviceSecrets.size}`);
  }

  private decodeHeader(buffer: Buffer): NanogridataHeader | null {
    if (buffer.length < HEADER_SIZE) return null;

    const magic = [buffer[0], buffer[1]];
    if (magic[0] !== NANOGRIDATA_MAGIC[0] || magic[1] !== NANOGRIDATA_MAGIC[1]) {
      return null;
    }

    if (buffer[2] !== NANOGRIDATA_VERSION) return null;

    return {
      magic,
      version: buffer[2],
      modelId: buffer[3],
      payloadType: buffer[4],
      flags: buffer[5],
      length: buffer.readUInt16BE(6),
      timestamp: buffer.readUInt32BE(8),
      reserved: buffer.readUInt16BE(12),
    };
  }

  private validateTimestamp(ts: number): boolean {
    const now = Math.floor(Date.now() / 1000);
    const diff = Math.abs(now - ts);
    return diff <= 3600;
  }

  private checkReplay(modelId: number, ts: number): boolean {
    const key = `${modelId}:${ts}`;
    if (this.replayCache.has(key)) {
      log('WARN', 'Replay attack detected', key);
      return true;
    }
    this.replayCache.set(key, Date.now() + 300000);
    return false;
  }

  private verifyMac(packet: Buffer, mac: Buffer, modelId: number): boolean {
    const secret = this.deviceSecrets.get(modelId.toString());
    if (!secret) {
      log('ERROR', 'No secret for model', `${modelId}`);
      return false;
    }

    try {
      const hmac = createHmac('sha256', secret);
      hmac.update(packet.subarray(0, packet.length - mac.length));
      const computed = hmac.digest();
      return timingSafeEqual(computed.subarray(0, mac.length), mac);
    } catch {
      return false;
    }
  }

  decodeCBOR(buffer: Buffer): any {
    try {
      if (buffer.length > CBOR_MAX_SIZE) throw new Error('CBOR too large');
      return cbor.decodeFirstSync(buffer, {
        maxStrLength: CBOR_MAX_STR_LENGTH,
        maxArrayLength: CBOR_MAX_ARRAY_LENGTH,
      } as any);
    } catch (err) {
      log('ERROR', 'CBOR decode failed', String(err));
      return null;
    }
  }

  private startCleanup() {
    setInterval(() => {
      const now = Date.now();
      let cleaned = 0;
      for (const [key, expiry] of this.replayCache.entries()) {
        if (expiry < now) {
          this.replayCache.delete(key);
          cleaned++;
        }
      }
      if (cleaned > 0) {
        log('DEBUG', 'Cache cleanup', `cleaned=${cleaned}`);
      }
    }, 60000);
  }

  deserialize(buffer: Buffer): NanogridataPacket {
    this.stats.received++;
    this.stats.bytes += buffer.length;

    const header = this.decodeHeader(buffer);
    if (!header) {
      this.stats.rejected++;
      return { header: null, payload: Buffer.alloc(0), mac: Buffer.alloc(0), valid: false, error: 'Invalid header' };
    }

    if (!this.validateTimestamp(header.timestamp)) {
      this.stats.rejected++;
      return { header, payload: Buffer.alloc(0), mac: Buffer.alloc(0), valid: false, error: 'Timestamp invalid' };
    }

    if (this.checkReplay(header.modelId, header.timestamp)) {
      this.stats.rejected++;
      return { header, payload: Buffer.alloc(0), mac: Buffer.alloc(0), valid: false, error: 'Replay detected' };
    }

    const payloadStart = HEADER_SIZE;
    const payloadEnd = HEADER_SIZE + header.length;

    if (payloadEnd > buffer.length) {
      this.stats.rejected++;
      return { header, payload: Buffer.alloc(0), mac: Buffer.alloc(0), valid: false, error: 'Payload overflow' };
    }

    const payload = buffer.subarray(payloadStart, payloadEnd);
    const macSize = (header.flags & 0x0F) === SecurityLevel.STANDARD ? 16 : 2;
    const macStart = payloadEnd;
    const macEnd = macStart + macSize;

    if (macEnd > buffer.length) {
      this.stats.rejected++;
      return { header, payload, mac: Buffer.alloc(0), valid: false, error: 'MAC overflow' };
    }

    const mac = buffer.subarray(macStart, macEnd);

    if ((header.flags & 0x0F) !== SecurityLevel.NONE) {
      if (!this.verifyMac(buffer, mac, header.modelId)) {
        this.stats.rejected++;
        return { header, payload, mac, valid: false, error: 'MAC failed' };
      }
    }

    this.stats.decoded++;
    return { header, payload, mac, valid: true };
  }

  getStats() {
    return { ...this.stats };
  }
}

/**
 * Gateway Server
 */
class NanogridataGateway {
  private decoder: NanogridataDecoder;
  private server: any;
  private connections = 0;

  constructor() {
    this.decoder = new NanogridataDecoder();
  }

  start() {
    this.server = createServer((socket: Socket) => {
      this.connections++;
      const clientId = `${socket.remoteAddress}:${socket.remotePort}`;
      log('INFO', 'Client connected', clientId);

      let buffer = Buffer.alloc(0);

      socket.on('data', (chunk: Buffer) => {
        buffer = Buffer.concat([buffer, chunk]);

        while (buffer.length >= 14) {
          const payloadLength = buffer.readUInt16BE(6);
          const macLength = (buffer[5] & 0x0F) === SecurityLevel.STANDARD ? 16 : 2;
          const totalLength = 14 + payloadLength + macLength;

          if (buffer.length < totalLength) break;

          const packetBuf = buffer.subarray(0, totalLength);
          const packet = this.decoder.deserialize(packetBuf);
          this.routePacket(packet);

          buffer = buffer.subarray(totalLength);
        }
      });

      socket.on('end', () => {
        this.connections--;
        log('INFO', 'Client disconnected', clientId);
      });

      socket.on('error', (err: any) => {
        this.connections--;
        log('ERROR', 'Socket error', String(err));
      });
    });

    this.server.listen(NANOGRIDATA_PORT, '0.0.0.0', () => {
      log('INFO', `Gateway listening on port ${NANOGRIDATA_PORT}`);
    });
  }

  private async routePacket(packet: NanogridataPacket) {
    if (!packet.valid || !packet.header) {
      log('WARN', 'Invalid packet', packet.error);
      return;
    }

    const payload = this.decoder.decodeCBOR(packet.payload);
    if (!payload) return;

    const data = {
      source: `nanogridata_${packet.header.modelId.toString(16)}`,
      type: this.getPayloadTypeName(packet.header.payloadType),
      payload,
      timestamp: new Date(packet.header.timestamp * 1000).toISOString(),
      modelId: packet.header.modelId,
    };

    try {
      await axios.post(`${ALBA_ENDPOINT}/telemetry/ingest`, data, {
        timeout: 2000,
        headers: { 'Content-Type': 'application/json' },
      });
      log('INFO', 'Routed to ALBA', `model=0x${packet.header.modelId.toString(16)}`);
    } catch (err) {
      log('ERROR', 'Route failed', String(err));
    }
  }

  private getPayloadTypeName(type: number): string {
    const names: Record<number, string> = {
      [PayloadType.TELEMETRY]: 'telemetry',
      [PayloadType.CONFIG]: 'config',
      [PayloadType.EVENT]: 'event',
      [PayloadType.COMMAND]: 'command',
      [PayloadType.CALIBRATION]: 'calibration',
    };
    return names[type] || 'unknown';
  }

  getStats() {
    return {
      connections: this.connections,
      packets: this.decoder.getStats(),
    };
  }

  stop() {
    if (this.server) this.server.close();
    log('INFO', 'Gateway stopped');
  }
}

/**
 * Express Monitoring
 */
import express from 'express';

const app = express();
const gateway = new NanogridataGateway();

app.get('/health', (req, res) => {
  res.json({ ok: true });
});

app.get('/stats', (req, res) => {
  res.json(gateway.getStats());
});

app.get('/metrics', (req, res) => {
  const stats = gateway.getStats();
  res.set('Content-Type', 'text/plain');
  const output = `
nanogridata_packets_received ${stats.packets.received}
nanogridata_packets_decoded ${stats.packets.decoded}
nanogridata_packets_rejected ${stats.packets.rejected}
nanogridata_bytes_received ${stats.packets.bytes}
nanogridata_active_connections ${stats.connections}
  `;
  res.send(output);
});

// Start
gateway.start();

const PORT = parseInt(process.env.METRICS_PORT || '5679');
app.listen(PORT, () => {
  log('INFO', `Metrics on port ${PORT}`);
});

// Graceful shutdown
process.on('SIGTERM', () => {
  log('INFO', 'Shutting down');
  gateway.stop();
  process.exit(0);
});

export { NanogridataGateway, NanogridataDecoder };
