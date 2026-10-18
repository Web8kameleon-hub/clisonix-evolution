'use client';

import { useState, useEffect } from 'react';
import styles from './radio.module.css';

interface RadioStation {
  id: string;
  name: string;
  frequency: string;
  type: 'AM' | 'FM' | 'SW' | 'DAB';
  power: number;
  coverage: number;
  status: 'broadcasting' | 'offline' | 'maintenance' | 'standby';
  location: string;
  language: string;
  content: string[];
  listeners: number;
  uptime: number;
  lastBroadcast: string;
}

interface BroadcastContent {
  id: string;
  title: string;
  type: 'news' | 'music' | 'talk' | 'propaganda' | 'emergency' | 'education';
  duration: number;
  language: string;
  priority: 'low' | 'medium' | 'high' | 'critical';
  status: 'scheduled' | 'broadcasting' | 'completed' | 'cancelled';
  startTime: string;
  endTime: string;
  stations: string[];
}

interface RadioMetrics {
  totalStations: number;
  activeStations: number;
  totalListeners: number;
  totalCoverage: number;
  averageUptime: number;
  activeBroadcasts: number;
  emergencyCapable: number;
}

export default function RadioPropagandaDashboard() {
  const [stations, setStations] = useState<RadioStation[]>([]);
  const [broadcasts, setBroadcasts] = useState<BroadcastContent[]>([]);
  const [metrics, setMetrics] = useState<RadioMetrics>({
    totalStations: 0,
    activeStations: 0,
    totalListeners: 0,
    totalCoverage: 0,
    averageUptime: 0,
    activeBroadcasts: 0,
    emergencyCapable: 0
  });
  const [selectedStation, setSelectedStation] = useState<RadioStation | null>(null);
  const [filterType, setFilterType] = useState<string>('all');
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    fetchRadioData();
    const interval = setInterval(fetchRadioData, 15000);
    return () => clearInterval(interval);
  }, []);

  const fetchRadioData = async () => {
    setIsLoading(true);
    try {
      // Simulate radio station data
      const mockStations: RadioStation[] = [
        {
          id: 'station-001',
          name: 'National Radio One',
          frequency: '101.5 FM',
          type: 'FM',
          power: 50000,
          coverage: 85,
          status: 'broadcasting',
          location: 'Central Transmitter',
          language: 'English',
          content: ['News', 'Music', 'Talk Shows'],
          listeners: 245000,
          uptime: 99.8,
          lastBroadcast: new Date().toISOString()
        },
        {
          id: 'station-002',
          name: 'Emergency Alert System',
          frequency: '1240 AM',
          type: 'AM',
          power: 25000,
          coverage: 65,
          status: 'standby',
          location: 'Emergency Center',
          language: 'Multiple',
          content: ['Emergency Alerts', 'Public Safety'],
          listeners: 0,
          uptime: 100,
          lastBroadcast: new Date(Date.now() - 3600000).toISOString()
        },
        {
          id: 'station-003',
          name: 'Voice of Freedom',
          frequency: '15.425 SW',
          type: 'SW',
          power: 100000,
          coverage: 95,
          status: 'broadcasting',
          location: 'International Complex',
          language: 'Multiple',
          content: ['International News', 'Cultural Programs', 'Educational'],
          listeners: 1250000,
          uptime: 97.5,
          lastBroadcast: new Date(Date.now() - 30000).toISOString()
        },
        {
          id: 'station-004',
          name: 'City FM',
          frequency: '89.7 FM',
          type: 'FM',
          power: 15000,
          coverage: 45,
          status: 'broadcasting',
          location: 'Urban Center',
          language: 'English',
          content: ['Music', 'Local News', 'Entertainment'],
          listeners: 89000,
          uptime: 98.2,
          lastBroadcast: new Date(Date.now() - 60000).toISOString()
        },
        {
          id: 'station-005',
          name: 'Digital Radio Plus',
          frequency: 'DAB 12C',
          type: 'DAB',
          power: 20000,
          coverage: 55,
          status: 'broadcasting',
          location: 'Digital Hub',
          language: 'English',
          content: ['Digital Content', 'Interactive Shows', 'Podcasts'],
          listeners: 67000,
          uptime: 99.1,
          lastBroadcast: new Date(Date.now() - 120000).toISOString()
        },
        {
          id: 'station-006',
          name: 'Regional AM Network',
          frequency: '540 AM',
          type: 'AM',
          power: 75000,
          coverage: 78,
          status: 'maintenance',
          location: 'Regional Tower',
          language: 'English',
          content: ['Regional News', 'Weather', 'Agriculture'],
          listeners: 0,
          uptime: 95.8,
          lastBroadcast: new Date(Date.now() - 7200000).toISOString()
        }
      ];

      const mockBroadcasts: BroadcastContent[] = [
        {
          id: 'broadcast-001',
          title: 'Morning News Bulletin',
          type: 'news',
          duration: 30,
          language: 'English',
          priority: 'high',
          status: 'broadcasting',
          startTime: new Date(Date.now() - 900000).toISOString(),
          endTime: new Date(Date.now() + 900000).toISOString(),
          stations: ['station-001', 'station-003', 'station-004']
        },
        {
          id: 'broadcast-002',
          title: 'Emergency Weather Alert',
          type: 'emergency',
          duration: 5,
          language: 'Multiple',
          priority: 'critical',
          status: 'scheduled',
          startTime: new Date(Date.now() + 1800000).toISOString(),
          endTime: new Date(Date.now() + 2100000).toISOString(),
          stations: ['station-001', 'station-002', 'station-006']
        },
        {
          id: 'broadcast-003',
          title: 'International Music Hour',
          type: 'music',
          duration: 60,
          language: 'Multiple',
          priority: 'medium',
          status: 'broadcasting',
          startTime: new Date(Date.now() - 1800000).toISOString(),
          endTime: new Date(Date.now() + 1800000).toISOString(),
          stations: ['station-003']
        },
        {
          id: 'broadcast-004',
          title: 'Public Information Campaign',
          type: 'propaganda',
          duration: 15,
          language: 'English',
          priority: 'high',
          status: 'scheduled',
          startTime: new Date(Date.now() + 3600000).toISOString(),
          endTime: new Date(Date.now() + 4500000).toISOString(),
          stations: ['station-001', 'station-004', 'station-005']
        }
      ];

      const activeStations = mockStations.filter(s => s.status === 'broadcasting').length;
      const totalListeners = mockStations.reduce((sum, s) => sum + s.listeners, 0);
      const totalCoverage = Math.max(...mockStations.map(s => s.coverage));
      const avgUptime = mockStations.reduce((sum, s) => sum + s.uptime, 0) / mockStations.length;
      const activeBroadcasts = mockBroadcasts.filter(b => b.status === 'broadcasting').length;
      const emergencyCapable = mockStations.filter(s => s.content.some(c => c.includes('Emergency') || c.includes('Alert'))).length;

      const mockMetrics: RadioMetrics = {
        totalStations: mockStations.length,
        activeStations,
        totalListeners,
        totalCoverage,
        averageUptime: Math.round(avgUptime * 100) / 100,
        activeBroadcasts,
        emergencyCapable
      };

      setStations(mockStations);
      setBroadcasts(mockBroadcasts);
      setMetrics(mockMetrics);
    } catch (error) {
      console.error('Error fetching radio data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'broadcasting': return '#00ff88';
      case 'standby': return '#00d4ff';
      case 'maintenance': return '#ffa502';
      case 'offline': return '#ff6b6b';
      default: return '#6c757d';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical': return '#ff0000';
      case 'high': return '#ff6b6b';
      case 'medium': return '#ffa502';
      case 'low': return '#00d4ff';
      default: return '#6c757d';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'AM': return '📻';
      case 'FM': return '📡';
      case 'SW': return '🌍';
      case 'DAB': return '📺';
      default: return '📢';
    }
  };

  const getContentTypeIcon = (type: string) => {
    switch (type) {
      case 'news': return '📰';
      case 'music': return '🎵';
      case 'talk': return '🎙️';
      case 'propaganda': return '📢';
      case 'emergency': return '🚨';
      case 'education': return '📚';
      default: return '📻';
    }
  };

  const formatDuration = (minutes: number) => {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return hours > 0 ? `${hours}h ${mins}m` : `${mins}m`;
  };

  const formatPower = (watts: number) => {
    if (watts >= 1000) {
      return `${(watts / 1000).toFixed(1)}kW`;
    }
    return `${watts}W`;
  };

  const formatListeners = (count: number) => {
    if (count >= 1000000) {
      return `${(count / 1000000).toFixed(1)}M`;
    }
    if (count >= 1000) {
      return `${(count / 1000).toFixed(1)}K`;
    }
    return count.toString();
  };

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const filteredStations = filterType === 'all' 
    ? stations 
    : stations.filter(station => station.type === filterType);

  return (
    <div className={styles['container']}>
      <div className={styles['header']}>
        <h1 className={styles['title']}>📻 Radio Propaganda Center</h1>
        <p className={styles['subtitle']}>
          Centralized radio broadcasting and content distribution management
        </p>
        <div className={styles['last-updated']}>
          Last updated: {new Date().toLocaleTimeString()}
          {isLoading && <span className={styles['loading']}>⟳</span>}
        </div>
      </div>

      {/* Metrics Overview */}
      <div className={styles['metrics-grid']}>
        <div className={styles['metric-card']}>
          <div className={styles['metric-icon']}>📡</div>
          <div className={styles['metric-data']}>
            <div className={styles['metric-value']}>{metrics.totalStations}</div>
            <div className={styles['metric-label']}>Total Stations</div>
          </div>
        </div>
        <div className={styles['metric-card']}>
          <div className={styles['metric-icon']}>📻</div>
          <div className={styles['metric-data']}>
            <div className={styles['metric-value']}>{metrics.activeStations}</div>
            <div className={styles['metric-label']}>Broadcasting</div>
          </div>
        </div>
        <div className={styles['metric-card']}>
          <div className={styles['metric-icon']}>👥</div>
          <div className={styles['metric-data']}>
            <div className={styles['metric-value']}>{formatListeners(metrics.totalListeners)}</div>
            <div className={styles['metric-label']}>Total Listeners</div>
          </div>
        </div>
        <div className={styles['metric-card']}>
          <div className={styles['metric-icon']}>🌐</div>
          <div className={styles['metric-data']}>
            <div className={styles['metric-value']}>{metrics.totalCoverage}%</div>
            <div className={styles['metric-label']}>Max Coverage</div>
          </div>
        </div>
        <div className={styles['metric-card']}>
          <div className={styles['metric-icon']}>⏱️</div>
          <div className={styles['metric-data']}>
            <div className={styles['metric-value']}>{metrics.averageUptime}%</div>
            <div className={styles['metric-label']}>Avg Uptime</div>
          </div>
        </div>
        <div className={styles['metric-card']}>
          <div className={styles['metric-icon']}>📢</div>
          <div className={styles['metric-data']}>
            <div className={styles['metric-value']}>{metrics.activeBroadcasts}</div>
            <div className={styles['metric-label']}>Live Broadcasts</div>
          </div>
        </div>
        <div className={styles['metric-card']}>
          <div className={styles['metric-icon']}>🚨</div>
          <div className={styles['metric-data']}>
            <div className={styles['metric-value']}>{metrics.emergencyCapable}</div>
            <div className={styles['metric-label']}>Emergency Ready</div>
          </div>
        </div>
      </div>

      {/* Active Broadcasts */}
      <div className={styles['broadcasts-section']}>
        <h2 className={styles['section-title']}>📢 Active Broadcasts</h2>
        <div className={styles['broadcasts-grid']}>
          {broadcasts.filter(b => b.status === 'broadcasting' || b.status === 'scheduled').map((broadcast) => (
            <div key={broadcast.id} className={styles['broadcast-card']}>
              <div className={styles['broadcast-header']}>
                <div className={styles['broadcast-title']}>
                  {getContentTypeIcon(broadcast.type)} {broadcast.title}
                </div>
                <div 
                  className={styles['broadcast-priority']}
                  style={{ color: getPriorityColor(broadcast.priority) }}
                >
                  ● {broadcast.priority.toUpperCase()}
                </div>
              </div>
              
              <div className={styles['broadcast-info']}>
                <div className={styles['broadcast-detail']}>
                  <span>Type:</span>
                  <span>{broadcast.type}</span>
                </div>
                <div className={styles['broadcast-detail']}>
                  <span>Duration:</span>
                  <span>{formatDuration(broadcast.duration)}</span>
                </div>
                <div className={styles['broadcast-detail']}>
                  <span>Language:</span>
                  <span>{broadcast.language}</span>
                </div>
                <div className={styles['broadcast-detail']}>
                  <span>Time:</span>
                  <span>{formatTime(broadcast.startTime)} - {formatTime(broadcast.endTime)}</span>
                </div>
                <div className={styles['broadcast-detail']}>
                  <span>Stations:</span>
                  <span>{broadcast.stations.length} stations</span>
                </div>
              </div>
              
              <div 
                className={styles['broadcast-status']}
                style={{ backgroundColor: broadcast.status === 'broadcasting' ? 'rgba(0, 255, 136, 0.2)' : 'rgba(0, 212, 255, 0.2)' }}
              >
                {broadcast.status === 'broadcasting' ? '🔴 LIVE' : '⏰ SCHEDULED'}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Station Filter */}
      <div className={styles['filter-section']}>
        <h2 className={styles['section-title']}>📡 Radio Stations</h2>
        <div className={styles['station-filters']}>
          <button 
            className={`${styles['filter-button']} ${filterType === 'all' ? styles['active'] : ''}`}
            onClick={() => setFilterType('all')}
          >
            All Stations ({stations.length})
          </button>
          <button 
            className={`${styles['filter-button']} ${filterType === 'FM' ? styles['active'] : ''}`}
            onClick={() => setFilterType('FM')}
          >
            📡 FM ({stations.filter(s => s.type === 'FM').length})
          </button>
          <button 
            className={`${styles['filter-button']} ${filterType === 'AM' ? styles['active'] : ''}`}
            onClick={() => setFilterType('AM')}
          >
            📻 AM ({stations.filter(s => s.type === 'AM').length})
          </button>
          <button 
            className={`${styles['filter-button']} ${filterType === 'SW' ? styles['active'] : ''}`}
            onClick={() => setFilterType('SW')}
          >
            🌍 SW ({stations.filter(s => s.type === 'SW').length})
          </button>
          <button 
            className={`${styles['filter-button']} ${filterType === 'DAB' ? styles['active'] : ''}`}
            onClick={() => setFilterType('DAB')}
          >
            📺 DAB ({stations.filter(s => s.type === 'DAB').length})
          </button>
        </div>
      </div>

      {/* Stations Grid */}
      <div className={styles['stations-section']}>
        <div className={styles['stations-grid']}>
          {filteredStations.map((station) => (
            <div 
              key={station.id} 
              className={styles['station-card']}
              onClick={() => setSelectedStation(station)}
            >
              <div className={styles['station-header']}>
                <div className={styles['station-title']}>
                  {getTypeIcon(station.type)} {station.name}
                </div>
                <div 
                  className={styles['station-status']}
                  style={{ color: getStatusColor(station.status) }}
                >
                  ● {station.status.toUpperCase()}
                </div>
              </div>
              
              <div className={styles['station-frequency']}>{station.frequency}</div>
              <div className={styles['station-location']}>📍 {station.location}</div>
              
              <div className={styles['station-metrics']}>
                <div className={styles['station-metric']}>
                  <span>Power:</span>
                  <span>{formatPower(station.power)}</span>
                </div>
                <div className={styles['station-metric']}>
                  <span>Coverage:</span>
                  <span>{station.coverage}%</span>
                </div>
                <div className={styles['station-metric']}>
                  <span>Listeners:</span>
                  <span>{formatListeners(station.listeners)}</span>
                </div>
                <div className={styles['station-metric']}>
                  <span>Uptime:</span>
                  <span>{station.uptime}%</span>
                </div>
              </div>
              
              <div className={styles['station-content']}>
                <div className={styles['content-label']}>Content:</div>
                <div className={styles['content-tags']}>
                  {station.content.map((content, index) => (
                    <span key={index} className={styles['content-tag']}>
                      {content}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Station Details Modal */}
      {selectedStation && (
        <div className={styles['modal-overlay']} onClick={() => setSelectedStation(null)}>
          <div className={styles['modal-content']} onClick={(e) => e.stopPropagation()}>
            <div className={styles['modal-header']}>
              <h3 className={styles['modal-title']}>
                {getTypeIcon(selectedStation.type)} {selectedStation.name}
              </h3>
              <button 
                className={styles['modal-close']}
                onClick={() => setSelectedStation(null)}
              >
                ✕
              </button>
            </div>
            
            <div className={styles['modal-body']}>
              <div className={styles['station-details']}>
                <div className={styles['detail-section']}>
                  <h4>Station Information</h4>
                  <div className={styles['detail-grid']}>
                    <div className={styles['detail-item']}>
                      <span>Frequency:</span>
                      <span>{selectedStation.frequency}</span>
                    </div>
                    <div className={styles['detail-item']}>
                      <span>Type:</span>
                      <span>{selectedStation.type}</span>
                    </div>
                    <div className={styles['detail-item']}>
                      <span>Status:</span>
                      <span style={{ color: getStatusColor(selectedStation.status) }}>
                        {selectedStation.status}
                      </span>
                    </div>
                    <div className={styles['detail-item']}>
                      <span>Location:</span>
                      <span>{selectedStation.location}</span>
                    </div>
                    <div className={styles['detail-item']}>
                      <span>Language:</span>
                      <span>{selectedStation.language}</span>
                    </div>
                  </div>
                </div>
                
                <div className={styles['detail-section']}>
                  <h4>Technical Specifications</h4>
                  <div className={styles['detail-grid']}>
                    <div className={styles['detail-item']}>
                      <span>Transmitter Power:</span>
                      <span>{formatPower(selectedStation.power)}</span>
                    </div>
                    <div className={styles['detail-item']}>
                      <span>Coverage Area:</span>
                      <span>{selectedStation.coverage}%</span>
                    </div>
                    <div className={styles['detail-item']}>
                      <span>Current Listeners:</span>
                      <span>{selectedStation.listeners.toLocaleString()}</span>
                    </div>
                    <div className={styles['detail-item']}>
                      <span>Uptime:</span>
                      <span>{selectedStation.uptime}%</span>
                    </div>
                    <div className={styles['detail-item']}>
                      <span>Last Broadcast:</span>
                      <span>{new Date(selectedStation.lastBroadcast).toLocaleString()}</span>
                    </div>
                  </div>
                </div>
                
                <div className={styles['detail-section']}>
                  <h4>Programming Content</h4>
                  <div className={styles['content-list']}>
                    {selectedStation.content.map((content, index) => (
                      <div key={index} className={styles['content-item']}>
                        📻 {content}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Controls */}
      <div className={styles['controls']}>
        <button 
          className={styles['refresh-button']}
          onClick={fetchRadioData}
          disabled={isLoading}
        >
          {isLoading ? '⟳ Refreshing...' : '🔄 Refresh Data'}
        </button>
      </div>
    </div>
  );
}
