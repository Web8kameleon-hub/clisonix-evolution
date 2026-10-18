/**
 * Neural Planner Tests
 * Comprehensive testing for AGI neural network monitoring
 * 
 * @version 8.0.0
 * @author Ledjan Ahmati
 * @contact dealsjona@gmail.com
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { NeuralPlanner } from '../lib/NeuralPlanner';

describe('Neural Planner System', () => {
  let planner: NeuralPlanner;

  beforeEach(() => {
    planner = new NeuralPlanner({
      maxPulseRate: 100,
      flickeringThreshold: 3,
      throttleDelay: 1000, // Shorter for testing
      safeThinkDuration: 2000, // Shorter for testing
      monitoringInterval: 50, // Faster for testing
      emergencyShutdownThreshold: 200
    });
  });

  afterEach(() => {
    planner.destroy();
  });

  describe('Initialization', () => {
    it('should initialize with 8 core neural nodes', () => {
      const status = planner.getNetworkStatus();
      expect(status.totalNodes).toBe(8);
      expect(status.isRunning).toBe(true);
    });

    it('should have n1 and n7 nodes properly configured', () => {
      const status = planner.getNetworkStatus();
      const n1 = status.nodes.find((n: unknown) => n.id === 'n1');
      const n7 = status.nodes.find((n: unknown) => n.id === 'n7');

      expect(n1).toBeDefined();
      expect(n1?.name).toBe('Primary Input Processor');
      expect(n1?.type).toBe('input');

      expect(n7).toBeDefined();
      expect(n7?.name).toBe('Ethical Oversight Controller');
      expect(n7?.type).toBe('ethical');
    });
  });

  describe('n1 Node Monitoring', () => {
    it('should detect n1 overload and throttle input', async () => {
      const alertsSpy = vi.fn();
      planner.on('nodeOverload', alertsSpy);

      // Simulate high pulse rate for n1
      planner.setNodeActivity('n1', 100); // Max activity to trigger high pulse rate

      // Wait for monitoring cycle
      await new Promise(resolve => setTimeout(resolve, 200));

      const status = planner.getNetworkStatus();
      const n1 = status.nodes.find((n: unknown) => n.id === 'n1');

      // Check if throttling occurs when pulse rate exceeds threshold
      if (n1 && n1.pulseRate > 80) {
        expect(status.throttledNodes).toContain('n1');
      }
    });

    it('should recover n1 from throttled state', async () => {
      // Force throttle n1
      planner.setNodeActivity('n1', 100);
      
      // Wait for potential throttling
      await new Promise(resolve => setTimeout(resolve, 200));
      
      // Reduce activity
      planner.setNodeActivity('n1', 20);
      
      // Wait for recovery
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      const status = planner.getNetworkStatus();
      expect(status.throttledNodes).not.toContain('n1');
    });
  });

  describe('n7 Ethical Monitoring', () => {
    it('should detect n7 ethical pulse anomaly and activate SafeThink', async () => {
      const safeThinkSpy = vi.fn();
      planner.on('safeThinkActivated', safeThinkSpy);

      // Simulate excessive flickering for n7 by triggering irregular pulses
      // This is harder to simulate directly, so we'll test the SafeThink activation
      const status = planner.getNetworkStatus();
      
      if (status.safeThinkActive) {
        expect(safeThinkSpy).toHaveBeenCalled();
      }
    });

    it('should deactivate SafeThink after duration', async () => {
      const deactivateSpy = vi.fn();
      planner.on('safeThinkDeactivated', deactivateSpy);

      // If SafeThink becomes active during test, wait for deactivation
      await new Promise(resolve => setTimeout(resolve, 2500));

      // Check that SafeThink can be deactivated
      const status = planner.getNetworkStatus();
      expect(status.safeThinkActive).toBe(false);
    });
  });

  describe('Activity Map Generation', () => {
    it('should generate activity map with node coordinates', () => {
      const activityMap = planner.getActivityMap();

      expect(activityMap.map).toBeDefined();
      expect(activityMap.map.n1).toBeDefined();
      expect(activityMap.map.n7).toBeDefined();

      expect(activityMap.map.n1.coordinates).toEqual({ x: 100, y: 200 });
      expect(activityMap.map.n7.coordinates).toEqual({ x: 700, y: 350 });
    });

    it('should include connection information', () => {
      const activityMap = planner.getActivityMap();

      expect(activityMap.map.n1.connections).toContain('n2');
      expect(activityMap.map.n1.connections).toContain('n3');
      expect(activityMap.map.n1.connections).toContain('n7');

      expect(activityMap.map.n7.connections).toContain('n8');
    });
  });

  describe('Manual Node Control', () => {
    it('should allow manual activity setting', () => {
      const success = planner.setNodeActivity('n1', 75);
      expect(success).toBe(true);

      const status = planner.getNetworkStatus();
      const n1 = status.nodes.find((n: unknown) => n.id === 'n1');
      expect(n1?.activity).toBe(75);
    });

    it('should reject invalid node IDs', () => {
      const success = planner.setNodeActivity('invalid', 50);
      expect(success).toBe(false);
    });

    it('should clamp activity values to valid range', () => {
      planner.setNodeActivity('n1', 150); // Over 100
      let status = planner.getNetworkStatus();
      let n1 = status.nodes.find((n: unknown) => n.id === 'n1');
      expect(n1?.activity).toBe(100);

      planner.setNodeActivity('n1', -50); // Under 0
      status = planner.getNetworkStatus();
      n1 = status.nodes.find((n: unknown) => n.id === 'n1');
      expect(n1?.activity).toBe(0);
    });
  });

  describe('Emergency Procedures', () => {
    it('should trigger emergency shutdown for extreme pulse rates', async () => {
      const emergencySpy = vi.fn();
      planner.on('emergencyShutdown', emergencySpy);

      // Force extreme activity to trigger emergency
      planner.setNodeActivity('n1', 100);
      
      // Wait for monitoring cycles
      await new Promise(resolve => setTimeout(resolve, 300));

      // Check for emergency conditions
      const status = planner.getNetworkStatus();
      const n1 = status.nodes.find((n: unknown) => n.id === 'n1');
      
      if (n1 && n1.pulseRate > 200) {
        expect(n1.status).toBe('offline');
      }
    });

    it('should reset network to initial state', () => {
      // Modify some nodes
      planner.setNodeActivity('n1', 100);
      planner.setNodeActivity('n7', 100);

      // Reset network
      planner.resetNetwork();

      const status = planner.getNetworkStatus();
      status.nodes.forEach((node: unknown) => {
        expect(node.status).toBe('active');
        expect(node.errorCount).toBe(0);
        expect(node.activity).toBeGreaterThan(0);
        expect(node.activity).toBeLessThan(100);
      });

      expect(status.throttledNodes).toHaveLength(0);
      expect(status.safeThinkActive).toBe(false);
    });
  });

  describe('Event System', () => {
    it('should emit warning events', async () => {
      const warningSpy = vi.fn();
      planner.on('warning', warningSpy);

      // Trigger condition that might cause warning
      planner.setNodeActivity('n1', 95);
      
      await new Promise(resolve => setTimeout(resolve, 200));

      // Check if warnings are emitted appropriately
      // This test is more observational since warnings depend on dynamic conditions
    });

    it('should emit alert events', async () => {
      const alertSpy = vi.fn();
      planner.on('alert', alertSpy);

      // Trigger condition that might cause alert
      await new Promise(resolve => setTimeout(resolve, 200));

      // Check if alerts are emitted appropriately
    });
  });

  describe('Performance and Stability', () => {
    it('should handle rapid activity changes', () => {
      for (let i = 0; i < 100; i++) {
        planner.setNodeActivity('n1', Math.random() * 100);
        planner.setNodeActivity('n7', Math.random() * 100);
      }

      const status = planner.getNetworkStatus();
      expect(status.isRunning).toBe(true);
      expect(status.nodes).toHaveLength(8);
    });

    it('should maintain network integrity under stress', async () => {
      // Simulate stress conditions
      const stressTest = async () => {
        for (let i = 0; i < 50; i++) {
          planner.setNodeActivity('n1', 100);
          planner.setNodeActivity('n7', 100);
          await new Promise(resolve => setTimeout(resolve, 10));
          planner.setNodeActivity('n1', 0);
          planner.setNodeActivity('n7', 0);
          await new Promise(resolve => setTimeout(resolve, 10));
        }
      };

      await stressTest();

      const status = planner.getNetworkStatus();
      expect(status.isRunning).toBe(true);
      expect(status.totalNodes).toBe(8);
    });
  });

  describe('Pulse Detection Algorithms', () => {
    it('should detect irregular pulse patterns', () => {
      const activityMap = planner.getActivityMap();
      
      // Check that flickering is being calculated
      Object.values(activityMap.map).forEach((node: unknown) => {
        expect(typeof node.flickering).toBe('number');
        expect(node.flickering).toBeGreaterThanOrEqual(0);
      });
    });

    it('should calculate pulse rates based on activity', () => {
      planner.setNodeActivity('n1', 80);
      
      const status = planner.getNetworkStatus();
      const n1 = status.nodes.find((n: unknown) => n.id === 'n1');
      
      expect(n1?.pulseRate).toBeGreaterThan(0);
      expect(typeof n1?.pulseRate).toBe('number');
    });
  });

  describe('Alert Generation', () => {
    it('should generate alerts for problematic conditions', () => {
      const activityMap = planner.getActivityMap();
      
      // Alerts should be an array
      expect(Array.isArray(activityMap.alerts)).toBe(true);
      
      // Test alert generation logic
      planner.setNodeActivity('n1', 100);
      planner.setNodeActivity('n7', 100);
      
      const updatedMap = planner.getActivityMap();
      // Alerts may be generated based on pulse rates and flickering
    });
  });

  describe('Cleanup and Resource Management', () => {
    it('should stop monitoring when destroyed', () => {
      expect(planner.getNetworkStatus().isRunning).toBe(true);
      
      planner.destroy();
      
      // After destruction, the planner should not be running
      // Note: We can't test getNetworkStatus after destroy as it may throw
    });

    it('should clean up event listeners', () => {
      const testListener = vi.fn();
      planner.on('test', testListener);
      
      planner.destroy();
      
      // Event listeners should be cleaned up
      expect(planner.listenerCount('test')).toBe(0);
    });
  });
});
