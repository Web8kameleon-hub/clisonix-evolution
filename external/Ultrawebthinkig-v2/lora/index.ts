/**
 * Lora Module - Long Range IoT Communication
 * EuroWeb Platform v8.0.0
 * 
 * @author Ledjan Ahmati
 * @version 8.0.0
 */

export interface LoRaConfig {
  frequency: number;
  spreadingFactor: number;
  bandwidth: number;
  power: number;
  range: string;
}

export interface LoRaDevice {
  id: string;
  name: string;
  type: 'sensor' | 'gateway' | 'node';
  config: LoRaConfig;
  status: 'online' | 'offline' | 'sleep';
  lastSeen: Date;
  data?: any;
}

export interface LoRaNetwork {
  id: string;
  name: string;
  devices: LoRaDevice[];
  coverage: number;
  activeNodes: number;
}

export const LoRaManager = {
  // Static implementation for industrial architecture
  networks: [] as LoRaNetwork[],
  
  createNetwork: (name: string): LoRaNetwork => {
    const network: LoRaNetwork = {
      id: `lora_${Date.now()}`,
      name,
      devices: [],
      coverage: 0,
      activeNodes: 0
    };
    LoRaManager.networks.push(network);
    return network;
  },
  
  addDevice: (networkId: string, device: Omit<LoRaDevice, 'id'>): LoRaDevice => {
    const newDevice: LoRaDevice = {
      ...device,
      id: `device_${Date.now()}`,
      lastSeen: new Date()
    };
    
    const network = LoRaManager.networks.find(n => n.id === networkId);
    if (network) {
      network.devices.push(newDevice);
      network.activeNodes = network.devices.filter(d => d.status === 'online').length;
    }
    
    return newDevice;
  },
  
  getNetworkStatus: (networkId: string) => {
    const network = LoRaManager.networks.find(n => n.id === networkId);
    if (!network) return null;
    
    return {
      totalDevices: network.devices.length,
      onlineDevices: network.devices.filter(d => d.status === 'online').length,
      offlineDevices: network.devices.filter(d => d.status === 'offline').length,
      sleepingDevices: network.devices.filter(d => d.status === 'sleep').length,
      coverage: network.coverage
    };
  }
};

export default LoRaManager;
