'use client';

import { useState, useEffect } from 'react';
import styles from './iot.module.css';

interface IoTDevice {
  id: string;
  name: string;
  type: 'sensor' | 'actuator' | 'gateway' | 'camera' | 'controller';
  category: 'environmental' | 'security' | 'automation' | 'monitoring' | 'industrial';
  status: 'online' | 'offline' | 'error' | 'maintenance';
  location: string;
  ipAddress: string;
  macAddress: string;
  firmware: string;
  battery?: number;
  lastSeen: string;
  temperature?: number;
  humidity?: number;
  signal: number;
  dataUsage: number;
  alerts: number;
}

interface IoTMetrics {
  totalDevices: number;
  onlineDevices: number;
  offlineDevices: number;
  errorDevices: number;
  averageSignal: number;
  totalDataUsage: number;
  activeAlerts: number;
  uptime: number;
}

export default function IoTDashboard() {
  const [devices, setDevices] = useState<IoTDevice[]>([]);
  const [metrics, setMetrics] = useState<IoTMetrics>({
    totalDevices: 0,
    onlineDevices: 0,
    offlineDevices: 0,
    errorDevices: 0,
    averageSignal: 0,
    totalDataUsage: 0,
    activeAlerts: 0,
    uptime: 0
  });
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [selectedDevice, setSelectedDevice] = useState<IoTDevice | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    fetchIoTData();
    const interval = setInterval(fetchIoTData, 8000);
    return () => clearInterval(interval);
  }, []);

  const fetchIoTData = async () => {
    setIsLoading(true);
    try {
      // Simulate IoT device data
      const mockDevices: IoTDevice[] = [
        {
          id: 'temp-001',
          name: 'Temperature Sensor A1',
          type: 'sensor',
          category: 'environmental',
          status: 'online',
          location: 'Building A - Floor 1',
          ipAddress: '192.168.1.101',
          macAddress: '00:1B:44:11:3A:B7',
          firmware: 'v2.1.4',
          battery: 87,
          lastSeen: new Date().toISOString(),
          temperature: 23.5,
          humidity: 45,
          signal: 85,
          dataUsage: 2.4,
          alerts: 0
        },
        {
          id: 'humid-002',
          name: 'Humidity Monitor B2',
          type: 'sensor',
          category: 'environmental',
          status: 'online',
          location: 'Building B - Floor 2',
          ipAddress: '192.168.1.102',
          macAddress: '00:1B:44:11:3A:B8',
          firmware: 'v2.1.4',
          battery: 62,
          lastSeen: new Date(Date.now() - 120000).toISOString(),
          temperature: 24.1,
          humidity: 52,
          signal: 78,
          dataUsage: 1.8,
          alerts: 1
        },
        {
          id: 'cam-003',
          name: 'Security Camera Main',
          type: 'camera',
          category: 'security',
          status: 'online',
          location: 'Main Entrance',
          ipAddress: '192.168.1.103',
          macAddress: '00:1B:44:11:3A:B9',
          firmware: 'v3.2.1',
          lastSeen: new Date(Date.now() - 30000).toISOString(),
          signal: 92,
          dataUsage: 145.6,
          alerts: 0
        },
        {
          id: 'motion-004',
          name: 'Motion Detector Alpha',
          type: 'sensor',
          category: 'security',
          status: 'error',
          location: 'Building A - Corridor',
          ipAddress: '192.168.1.104',
          macAddress: '00:1B:44:11:3A:BA',
          firmware: 'v1.8.2',
          battery: 23,
          lastSeen: new Date(Date.now() - 1800000).toISOString(),
          signal: 34,
          dataUsage: 0.5,
          alerts: 3
        },
        {
          id: 'light-005',
          name: 'Smart Light Controller',
          type: 'actuator',
          category: 'automation',
          status: 'online',
          location: 'Building C - Office',
          ipAddress: '192.168.1.105',
          macAddress: '00:1B:44:11:3A:BB',
          firmware: 'v2.3.0',
          lastSeen: new Date(Date.now() - 60000).toISOString(),
          signal: 91,
          dataUsage: 3.2,
          alerts: 0
        },
        {
          id: 'hvac-006',
          name: 'HVAC Controller Main',
          type: 'controller',
          category: 'automation',
          status: 'online',
          location: 'Building A - Mechanical Room',
          ipAddress: '192.168.1.106',
          macAddress: '00:1B:44:11:3A:BC',
          firmware: 'v4.1.2',
          lastSeen: new Date(Date.now() - 45000).toISOString(),
          temperature: 19.8,
          signal: 88,
          dataUsage: 12.4,
          alerts: 0
        },
        {
          id: 'gateway-007',
          name: 'IoT Gateway Primary',
          type: 'gateway',
          category: 'industrial',
          status: 'online',
          location: 'Server Room',
          ipAddress: '192.168.1.107',
          macAddress: '00:1B:44:11:3A:BD',
          firmware: 'v5.0.1',
          lastSeen: new Date(Date.now() - 15000).toISOString(),
          signal: 95,
          dataUsage: 234.7,
          alerts: 0
        },
        {
          id: 'air-008',
          name: 'Air Quality Monitor',
          type: 'sensor',
          category: 'environmental',
          status: 'maintenance',
          location: 'Building B - Lobby',
          ipAddress: '192.168.1.108',
          macAddress: '00:1B:44:11:3A:BE',
          firmware: 'v2.0.8',
          battery: 91,
          lastSeen: new Date(Date.now() - 300000).toISOString(),
          temperature: 22.3,
          humidity: 38,
          signal: 72,
          dataUsage: 4.1,
          alerts: 1
        },
        {
          id: 'smoke-009',
          name: 'Smoke Detector Beta',
          type: 'sensor',
          category: 'security',
          status: 'offline',
          location: 'Building C - Kitchen',
          ipAddress: '192.168.1.109',
          macAddress: '00:1B:44:11:3A:BF',
          firmware: 'v1.9.3',
          battery: 0,
          lastSeen: new Date(Date.now() - 3600000).toISOString(),
          signal: 0,
          dataUsage: 0,
          alerts: 2
        }
      ];

      const onlineDevices = mockDevices.filter(d => d.status === 'online').length;
      const offlineDevices = mockDevices.filter(d => d.status === 'offline').length;
      const errorDevices = mockDevices.filter(d => d.status === 'error').length;
      const totalAlerts = mockDevices.reduce((sum, d) => sum + d.alerts, 0);
      const avgSignal = Math.round(mockDevices.reduce((sum, d) => sum + d.signal, 0) / mockDevices.length);
      const totalData = mockDevices.reduce((sum, d) => sum + d.dataUsage, 0);

      const mockMetrics: IoTMetrics = {
        totalDevices: mockDevices.length,
        onlineDevices,
        offlineDevices,
        errorDevices,
        averageSignal: avgSignal,
        totalDataUsage: Math.round(totalData * 100) / 100,
        activeAlerts: totalAlerts,
        uptime: 99.2
      };

      setDevices(mockDevices);
      setMetrics(mockMetrics);
    } catch (error) {
      console.error('Error fetching IoT data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'online': return '#00ff88';
      case 'maintenance': return '#ffa502';
      case 'error': return '#ff6b6b';
      case 'offline': return '#6c757d';
      default: return '#94a3b8';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'sensor': return '📊';
      case 'actuator': return '⚙️';
      case 'gateway': return '🌐';
      case 'camera': return '📹';
      case 'controller': return '🎛️';
      default: return '📱';
    }
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'environmental': return '🌡️';
      case 'security': return '🔒';
      case 'automation': return '🤖';
      case 'monitoring': return '👁️';
      case 'industrial': return '🏭';
      default: return '📱';
    }
  };

  const getBatteryLevel = (battery?: number) => {
    if (!battery) return 'N/A';
    if (battery > 80) return '🟢';
    if (battery > 50) return '🟡';
    if (battery > 20) return '🟠';
    return '🔴';
  };

  const formatLastSeen = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours}h ago`;
    return date.toLocaleDateString();
  };

  const filteredDevices = selectedCategory === 'all' 
    ? devices 
    : devices.filter(device => device.category === selectedCategory);

  return (
    <div className={styles['container']}>
      <div className={styles['header']}>
        <h1 className={styles['title']}>🏠 IoT Device Manager</h1>
        <p className={styles['subtitle']}>
          Comprehensive IoT device monitoring and management platform
        </p>
        <div className={styles['last-updated']}>
          Last updated: {new Date().toLocaleTimeString()}
          {isLoading && <span className={styles['loading']}>⟳</span>}
        </div>
      </div>

      {/* Metrics Overview */}
      <div className={styles['metrics-grid']}>
        <div className={styles['metric-card']}>
          <div className={styles['metric-icon']}>📱</div>
          <div className={styles['metric-data']}>
            <div className={styles['metric-value']}>{metrics.totalDevices}</div>
            <div className={styles['metric-label']}>Total Devices</div>
          </div>
        </div>
        <div className={styles['metric-card']}>
          <div className={styles['metric-icon']}>✅</div>
          <div className={styles['metric-data']}>
            <div className={styles['metric-value']}>{metrics.onlineDevices}</div>
            <div className={styles['metric-label']}>Online</div>
          </div>
        </div>
        <div className={styles['metric-card']}>
          <div className={styles['metric-icon']}>❌</div>
          <div className={styles['metric-data']}>
            <div className={styles['metric-value']}>{metrics.offlineDevices}</div>
            <div className={styles['metric-label']}>Offline</div>
          </div>
        </div>
        <div className={styles['metric-card']}>
          <div className={styles['metric-icon']}>⚠️</div>
          <div className={styles['metric-data']}>
            <div className={styles['metric-value']}>{metrics.errorDevices}</div>
            <div className={styles['metric-label']}>Errors</div>
          </div>
        </div>
        <div className={styles['metric-card']}>
          <div className={styles['metric-icon']}>📶</div>
          <div className={styles['metric-data']}>
            <div className={styles['metric-value']}>{metrics.averageSignal}%</div>
            <div className={styles['metric-label']}>Avg Signal</div>
          </div>
        </div>
        <div className={styles['metric-card']}>
          <div className={styles['metric-icon']}>📊</div>
          <div className={styles['metric-data']}>
            <div className={styles['metric-value']}>{metrics.totalDataUsage} GB</div>
            <div className={styles['metric-label']}>Data Usage</div>
          </div>
        </div>
        <div className={styles['metric-card']}>
          <div className={styles['metric-icon']}>🚨</div>
          <div className={styles['metric-data']}>
            <div className={styles['metric-value']}>{metrics.activeAlerts}</div>
            <div className={styles['metric-label']}>Active Alerts</div>
          </div>
        </div>
        <div className={styles['metric-card']}>
          <div className={styles['metric-icon']}>⏱️</div>
          <div className={styles['metric-data']}>
            <div className={styles['metric-value']}>{metrics.uptime}%</div>
            <div className={styles['metric-label']}>Uptime</div>
          </div>
        </div>
      </div>

      {/* Category Filter */}
      <div className={styles['filter-section']}>
        <h2 className={styles['section-title']}>📂 Device Categories</h2>
        <div className={styles['category-filters']}>
          <button 
            className={`${styles['category-button']} ${selectedCategory === 'all' ? styles['active'] : ''}`}
            onClick={() => setSelectedCategory('all')}
          >
            🌐 All Devices ({devices.length})
          </button>
          <button 
            className={`${styles['category-button']} ${selectedCategory === 'environmental' ? styles['active'] : ''}`}
            onClick={() => setSelectedCategory('environmental')}
          >
            🌡️ Environmental ({devices.filter(d => d.category === 'environmental').length})
          </button>
          <button 
            className={`${styles['category-button']} ${selectedCategory === 'security' ? styles['active'] : ''}`}
            onClick={() => setSelectedCategory('security')}
          >
            🔒 Security ({devices.filter(d => d.category === 'security').length})
          </button>
          <button 
            className={`${styles['category-button']} ${selectedCategory === 'automation' ? styles['active'] : ''}`}
            onClick={() => setSelectedCategory('automation')}
          >
            🤖 Automation ({devices.filter(d => d.category === 'automation').length})
          </button>
          <button 
            className={`${styles['category-button']} ${selectedCategory === 'industrial' ? styles['active'] : ''}`}
            onClick={() => setSelectedCategory('industrial')}
          >
            🏭 Industrial ({devices.filter(d => d.category === 'industrial').length})
          </button>
        </div>
      </div>

      {/* Device Grid */}
      <div className={styles['devices-section']}>
        <h2 className={styles['section-title']}>
          📱 Devices ({filteredDevices.length})
        </h2>
        <div className={styles['devices-grid']}>
          {filteredDevices.map((device) => (
            <div 
              key={device.id} 
              className={styles['device-card']}
              onClick={() => setSelectedDevice(device)}
            >
              <div className={styles['device-header']}>
                <div className={styles['device-icons']}>
                  <span>{getTypeIcon(device.type)}</span>
                  <span>{getCategoryIcon(device.category)}</span>
                </div>
                <div 
                  className={styles['device-status']}
                  style={{ color: getStatusColor(device.status) }}
                >
                  ● {device.status.toUpperCase()}
                </div>
              </div>
              
              <div className={styles['device-name']}>{device.name}</div>
              <div className={styles['device-location']}>📍 {device.location}</div>
              
              <div className={styles['device-metrics']}>
                <div className={styles['device-metric']}>
                  <span>Signal:</span>
                  <span>{device.signal}%</span>
                </div>
                {device.battery && (
                  <div className={styles['device-metric']}>
                    <span>Battery:</span>
                    <span>{getBatteryLevel(device.battery)} {device.battery}%</span>
                  </div>
                )}
                {device.temperature && (
                  <div className={styles['device-metric']}>
                    <span>Temp:</span>
                    <span>{device.temperature}°C</span>
                  </div>
                )}
                <div className={styles['device-metric']}>
                  <span>Data:</span>
                  <span>{device.dataUsage} GB</span>
                </div>
                <div className={styles['device-metric']}>
                  <span>Last Seen:</span>
                  <span>{formatLastSeen(device.lastSeen)}</span>
                </div>
              </div>
              
              {device.alerts > 0 && (
                <div className={styles['device-alerts']}>
                  🚨 {device.alerts} Alert{device.alerts > 1 ? 's' : ''}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Device Details Modal */}
      {selectedDevice && (
        <div className={styles['modal-overlay']} onClick={() => setSelectedDevice(null)}>
          <div className={styles['modal-content']} onClick={(e) => e.stopPropagation()}>
            <div className={styles['modal-header']}>
              <h3 className={styles['modal-title']}>
                {getTypeIcon(selectedDevice.type)} {selectedDevice.name}
              </h3>
              <button 
                className={styles['modal-close']}
                onClick={() => setSelectedDevice(null)}
              >
                ✕
              </button>
            </div>
            
            <div className={styles['modal-body']}>
              <div className={styles['device-details']}>
                <div className={styles['detail-group']}>
                  <h4>Basic Information</h4>
                  <div className={styles['detail-item']}>
                    <span>Type:</span>
                    <span>{selectedDevice.type}</span>
                  </div>
                  <div className={styles['detail-item']}>
                    <span>Category:</span>
                    <span>{selectedDevice.category}</span>
                  </div>
                  <div className={styles['detail-item']}>
                    <span>Status:</span>
                    <span style={{ color: getStatusColor(selectedDevice.status) }}>
                      {selectedDevice.status}
                    </span>
                  </div>
                  <div className={styles['detail-item']}>
                    <span>Location:</span>
                    <span>{selectedDevice.location}</span>
                  </div>
                </div>
                
                <div className={styles['detail-group']}>
                  <h4>Network Information</h4>
                  <div className={styles['detail-item']}>
                    <span>IP Address:</span>
                    <span>{selectedDevice.ipAddress}</span>
                  </div>
                  <div className={styles['detail-item']}>
                    <span>MAC Address:</span>
                    <span>{selectedDevice.macAddress}</span>
                  </div>
                  <div className={styles['detail-item']}>
                    <span>Signal Strength:</span>
                    <span>{selectedDevice.signal}%</span>
                  </div>
                  <div className={styles['detail-item']}>
                    <span>Data Usage:</span>
                    <span>{selectedDevice.dataUsage} GB</span>
                  </div>
                </div>
                
                <div className={styles['detail-group']}>
                  <h4>System Information</h4>
                  <div className={styles['detail-item']}>
                    <span>Firmware:</span>
                    <span>{selectedDevice.firmware}</span>
                  </div>
                  {selectedDevice.battery && (
                    <div className={styles['detail-item']}>
                      <span>Battery:</span>
                      <span>{selectedDevice.battery}%</span>
                    </div>
                  )}
                  <div className={styles['detail-item']}>
                    <span>Last Seen:</span>
                    <span>{formatLastSeen(selectedDevice.lastSeen)}</span>
                  </div>
                  <div className={styles['detail-item']}>
                    <span>Alerts:</span>
                    <span>{selectedDevice.alerts}</span>
                  </div>
                </div>
                
                {(selectedDevice.temperature || selectedDevice.humidity) && (
                  <div className={styles['detail-group']}>
                    <h4>Sensor Data</h4>
                    {selectedDevice.temperature && (
                      <div className={styles['detail-item']}>
                        <span>Temperature:</span>
                        <span>{selectedDevice.temperature}°C</span>
                      </div>
                    )}
                    {selectedDevice.humidity && (
                      <div className={styles['detail-item']}>
                        <span>Humidity:</span>
                        <span>{selectedDevice.humidity}%</span>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Controls */}
      <div className={styles['controls']}>
        <button 
          className={styles['refresh-button']}
          onClick={fetchIoTData}
          disabled={isLoading}
        >
          {isLoading ? '⟳ Refreshing...' : '🔄 Refresh Devices'}
        </button>
      </div>
    </div>
  );
}
