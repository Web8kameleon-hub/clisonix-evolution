/**
 * Web8Memory - Global Memory Management System
 * Pure TypeScript Memory Engine for Web8 Architecture
 * 
 * @author Ledjan Ahmati (100% Owner)
 * @version 8.0.1 Industrial
 * @license MIT
 */

interface Web8Store {
  sessionData: Record<string, any>;
  globalData: Record<string, any>;
  temporaryData: Record<string, any>;
  lastUpdate: number;
}

/**
 * Web8Memory - Core Memory Management
 */
export class Web8Memory {
  private static store: Web8Store = {
    sessionData: {},
    globalData: {},
    temporaryData: {},
    lastUpdate: Date.now()
  };

  /**
   * Get the entire memory store
   */
  static getStore(): Web8Store {
    return this.store;
  }

  /**
   * Set a value in session data
   */
  static setSessionValue(key: string, value: any): void {
    this.store.sessionData[key] = value;
    this.store.lastUpdate = Date.now();
  }

  /**
   * Get a value from session data
   */
  static getSessionValue(key: string): any {
    return this.store.sessionData[key];
  }

  /**
   * Set a value in global data
   */
  static setGlobalValue(key: string, value: any): void {
    this.store.globalData[key] = value;
    this.store.lastUpdate = Date.now();
  }

  /**
   * Get a value from global data
   */
  static getGlobalValue(key: string): any {
    return this.store.globalData[key];
  }

  /**
   * Clear all memory
   */
  static clear(): void {
    this.store = {
      sessionData: {},
      globalData: {},
      temporaryData: {},
      lastUpdate: Date.now()
    };
  }

  /**
   * Update last access timestamp
   */
  static touch(): void {
    this.store.lastUpdate = Date.now();
  }
}

/**
 * Web8GlobalMemory - Advanced Global Memory Operations
 */
export class Web8GlobalMemory {
  /**
   * Set any value in the global memory store
   */
  static setValue(key: keyof Web8Store, value: any): void {
    (Web8Memory.getStore() as any)[key] = value;
    Web8Memory.touch();
  }

  /**
   * Get any value from the global memory store
   */
  static getValue(key: keyof Web8Store): any {
    return Web8Memory.getStore()[key];
  }

  /**
   * Merge data into session data
   */
  static mergeSessionData(data: Record<string, any>): void {
    const store = Web8Memory.getStore();
    store.sessionData = { ...store.sessionData, ...data };
    Web8Memory.touch();
  }

  /**
   * Get memory usage statistics
   */
  static getStats(): {
    sessionKeys: number;
    globalKeys: number;
    temporaryKeys: number;
    lastUpdate: number;
  } {
    const store = Web8Memory.getStore();
    return {
      sessionKeys: Object.keys(store.sessionData).length,
      globalKeys: Object.keys(store.globalData).length,
      temporaryKeys: Object.keys(store.temporaryData).length,
      lastUpdate: store.lastUpdate
    };
  }
}

// Initialize global memory
Web8Memory.clear();

// Default export
export default Web8Memory;
