/**
 * 📡 ALBA System - Advanced IoT Network
 * Rrjeti i avancuar i sensorëve dhe pajisjeve IoT
 * 
 * @version 1.0.0 ALBA SYSTEM 
 * @author UltraWebThinking Team
 */

export interface SensorData {
  id: string;
  type: 'temperature' | 'humidity' | 'pressure' | 'motion' | 'co2' | 'energy';
  location: string;
  value: number;
  unit: string;
  status: 'normal' | 'warning' | 'critical' | 'offline';
  lastUpdate: string;
}

export interface DeviceStatus {
  id: string;
  name: string;
  type: 'sensor' | 'controller' | 'actuator' | 'gateway';
  location: string;
  status: 'online' | 'offline' | 'maintenance';
  batteryLevel?: number;
  signalStrength: number;
}

export interface LocationData {
  name: string;
  status: 'operational' | 'warning' | 'critical' | 'maintenance';
  efficiency: number;
  activeSensors: number;
  totalDevices: number;
  temperature: number;
  lastMaintenance: string;
}

export class ALBASystem {
  private static instance: ALBASystem;
  private sensors: Map<string, SensorData> = new Map();
  private devices: Map<string, DeviceStatus> = new Map();
  private criticalMonitoring = false;

  static getInstance(): ALBASystem {
    if (!ALBASystem.instance) {
      ALBASystem.instance = new ALBASystem();
      ALBASystem.instance.initializeSensors();
    }
    return ALBASystem.instance;
  }

  /**
   * 🔧 Initialize demo sensor data
   */
  private initializeSensors(): void {
    console.log('[ALBA System] Initializing IoT network...');

    // Gamma Sector sensors
    this.sensors.set('gamma-temp-01', {
      id: 'gamma-temp-01',
      type: 'temperature',
      location: 'Gamma Sector',
      value: 23.5 + (Math.random() - 0.5) * 2,
      unit: '°C',
      status: 'normal',
      lastUpdate: new Date().toISOString()
    });

    this.sensors.set('gamma-humid-01', {
      id: 'gamma-humid-01', 
      type: 'humidity',
      location: 'Gamma Sector',
      value: 68 + (Math.random() - 0.5) * 10,
      unit: '%',
      status: 'normal',
      lastUpdate: new Date().toISOString()
    });

    // Alpha Sector sensors
    this.sensors.set('alpha-temp-01', {
      id: 'alpha-temp-01',
      type: 'temperature', 
      location: 'Alpha Sector',
      value: 22.1 + (Math.random() - 0.5) * 2,
      unit: '°C',
      status: 'normal',
      lastUpdate: new Date().toISOString()
    });

    this.sensors.set('alpha-co2-01', {
      id: 'alpha-co2-01',
      type: 'co2',
      location: 'Alpha Sector', 
      value: 420 + Math.floor(Math.random() * 50),
      unit: 'ppm',
      status: 'normal',
      lastUpdate: new Date().toISOString()
    });

    // Beta Sector sensors
    this.sensors.set('beta-energy-01', {
      id: 'beta-energy-01',
      type: 'energy',
      location: 'Beta Sector',
      value: 45.7 + (Math.random() - 0.5) * 5,
      unit: 'kW',
      status: 'normal', 
      lastUpdate: new Date().toISOString()
    });

    // Initialize devices
    this.devices.set('gateway-main', {
      id: 'gateway-main',
      name: 'Main IoT Gateway',
      type: 'gateway',
      location: 'Central Hub',
      status: 'online',
      signalStrength: 98
    });

    this.devices.set('controller-gamma', {
      id: 'controller-gamma',
      name: 'Gamma Controller',
      type: 'controller',
      location: 'Gamma Sector',
      status: 'online',
      batteryLevel: 87,
      signalStrength: 92
    });

    console.log(`[ALBA System] ✅ ${this.sensors.size} sensors and ${this.devices.size} devices online`);
  }

  /**
   * 📊 Get all sensor data
   */
  async getAllSensorData(): Promise<SensorData[]> {
    // Simulate real-time updates
    this.updateSensorValues();
    return Array.from(this.sensors.values());
  }

  /**
   * 📱 Get device status
   */
  async getDeviceStatus(): Promise<DeviceStatus[]> {
    return Array.from(this.devices.values());
  }

  /**
   * 🏭 Get location-specific data
   */
  async getLocationData(location: string): Promise<LocationData> {
    const locationSensors = Array.from(this.sensors.values())
      .filter(s => s.location.toLowerCase().includes(location.toLowerCase()));
    
    const avgTemp = locationSensors
      .filter(s => s.type === 'temperature')
      .reduce((acc, s) => acc + s.value, 0) / locationSensors.filter(s => s.type === 'temperature').length || 22;

    const activeSensors = locationSensors.filter(s => s.status !== 'offline').length;
    const efficiency = Math.min(100, 85 + Math.floor(Math.random() * 15));

    return {
      name: `${location.charAt(0).toUpperCase() + location.slice(1)} Sector`,
      status: efficiency > 90 ? 'operational' : efficiency > 70 ? 'warning' : 'critical',
      efficiency,
      activeSensors,
      totalDevices: locationSensors.length,
      temperature: Math.round(avgTemp * 10) / 10,
      lastMaintenance: '2025-10-15'
    };
  }

  /**
   * 🚨 Enable critical monitoring
   */
  async enableCriticalMonitoring(): Promise<void> {
    console.log('[ALBA System] 🚨 CRITICAL MONITORING ENABLED');
    this.criticalMonitoring = true;
    
    // Increase monitoring frequency
    setInterval(() => {
      if (this.criticalMonitoring) {
        this.updateSensorValues();
        this.checkCriticalThresholds();
      }
    }, 5000); // Update every 5 seconds in critical mode
  }

  /**
   * 🛡️ Get critical system status
   */
  async getCriticalSystemStatus() {
    const criticalSystems = [
      {
        name: 'Main Power Grid',
        status: 'operational',
        level: 98
      },
      {
        name: 'Network Infrastructure', 
        status: 'optimal',
        level: 99
      },
      {
        name: 'Environmental Controls',
        status: 'stable',
        level: 94
      },
      {
        name: 'Security Systems',
        status: 'active',
        level: 100
      }
    ];

    return criticalSystems;
  }

  /**
   * 📊 Get health status for manager
   */
  async getHealthStatus() {
    const onlineDevices = Array.from(this.devices.values())
      .filter(d => d.status === 'online').length;
    
    return {
      status: onlineDevices > 0 ? 'online' : 'offline',
      devices: onlineDevices,
      lastUpdate: new Date().toISOString()
    };
  }

  /**
   * 🔄 Update sensor values (simulate real-time data)
   */
  private updateSensorValues(): void {
    for (const [id, sensor] of this.sensors) {
      let newValue = sensor.value;
      
      // Simulate realistic sensor fluctuations
      switch (sensor.type) {
        case 'temperature':
          newValue += (Math.random() - 0.5) * 0.5; // ±0.25°C variation
          break;
        case 'humidity':
          newValue += (Math.random() - 0.5) * 2; // ±1% variation  
          break;
        case 'co2':
          newValue += (Math.random() - 0.5) * 10; // ±5ppm variation
          break;
        case 'energy':
          newValue += (Math.random() - 0.5) * 1; // ±0.5kW variation
          break;
      }

      // Update sensor data
      this.sensors.set(id, {
        ...sensor,
        value: Math.round(newValue * 10) / 10,
        lastUpdate: new Date().toISOString()
      });
    }
  }

  /**
   * ⚠️ Check critical thresholds
   */
  private checkCriticalThresholds(): void {
    for (const [id, sensor] of this.sensors) {
      let status: SensorData['status'] = 'normal';
      
      // Define critical thresholds
      switch (sensor.type) {
        case 'temperature':
          if (sensor.value > 30 || sensor.value < 15) status = 'critical';
          else if (sensor.value > 27 || sensor.value < 18) status = 'warning';
          break;
        case 'humidity':
          if (sensor.value > 85 || sensor.value < 30) status = 'critical';
          else if (sensor.value > 80 || sensor.value < 40) status = 'warning';
          break;
        case 'co2':
          if (sensor.value > 1000) status = 'critical';
          else if (sensor.value > 800) status = 'warning';
          break;
      }

      if (status !== sensor.status) {
        console.log(`[ALBA System] ⚠️ Sensor ${id} status changed to: ${status}`);
        this.sensors.set(id, { ...sensor, status });
      }
    }
  }
}

console.log('📡 ALBA System - INITIALIZED');
console.log('🌐 IoT Network: OPERATIONAL');
console.log('📊 Real-time monitoring: ACTIVE');
