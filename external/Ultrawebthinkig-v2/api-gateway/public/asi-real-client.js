/**
 * 🔴 ASI REAL API CLIENT - Lidhja e Plotë Frontend-Backend
 * Integron të gjitha endpoint-et reale me CBOR optimization
 */

class ASIRealAPIClient {
    constructor() {
        this.baseURL = 'http://localhost:3003';
        this.endpoints = {
            // 🔴 REAL DATA ENDPOINTS
            realNews: '/api/global-news/breaking-news',
            realFinancial: '/api/real-financial',
            realEconomic: '/api/real-economic',
            realCultural: '/api/real-cultural',
            realAnalytics: '/api/real-analytics',
            
            // 📊 CBOR OPTIMIZED ENDPOINTS
            cborPerformance: '/api/analytics/performance-cbor',
            cborCultural: '/api/cultural/sites-cbor',
            
            // 🏛️ LEGACY ENDPOINTS (Mock Data)
            mockNews: '/api/news',
            mockFinancial: '/api/financial',
            mockCountry: '/api/country'
        };
    }

    // 🌐 Generic API caller with error handling
    async call(endpoint, options = {}) {
        try {
            const url = `${this.baseURL}${endpoint}`;
            const response = await fetch(url, {
                method: 'GET',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                    'X-ASI-Client': 'Real-Dashboard-v1.0'
                },
                ...options
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            console.error(`ASI API Error [${endpoint}]:`, error.message);
            throw error;
        }
    }

    // 🔴 REAL DATA METHODS
    async getRealNews(limit = 5) {
        return await this.call(`${this.endpoints.realNews}?limit=${limit}`);
    }

    async getRealFinancial(symbol = 'EUR', type = 'forex') {
        return await this.call(`${this.endpoints.realFinancial}/${symbol}?type=${type}`);
    }

    async getRealEconomic(country = 'WLD', indicator = 'GDP') {
        return await this.call(`${this.endpoints.realEconomic}/${country}?indicator=${indicator}`);
    }

    async getRealCultural(topic = 'Albania', type = 'summary') {
        return await this.call(`${this.endpoints.realCultural}/${topic}?type=${type}`);
    }

    async getAllRealData() {
        return await this.call(this.endpoints.realAnalytics);
    }

    // 📊 CBOR PERFORMANCE METHODS
    async getCBORPerformance() {
        return await this.call(this.endpoints.cborPerformance);
    }

    async getCBORCulturalSites() {
        return await this.call(this.endpoints.cborCultural);
    }

    // 🏛️ LEGACY METHODS (for comparison)
    async getMockNews(topic = 'albania') {
        return await this.call(`${this.endpoints.mockNews}/${topic}`);
    }

    async getMockFinancial(symbol = 'AAPL') {
        return await this.call(`${this.endpoints.mockFinancial}/${symbol}`);
    }

    async getMockCountry(code = 'AL') {
        return await this.call(`${this.endpoints.mockCountry}/${code}`);
    }
}

// 🌍 Global ASI API Client Instance
window.ASI = new ASIRealAPIClient();

// 🔄 Auto-refresh utilities
class DashboardAutoRefresh {
    constructor() {
        this.intervals = new Map();
    }

    start(key, callback, intervalMs = 30000) {
        this.stop(key); // Clear existing
        const interval = setInterval(callback, intervalMs);
        this.intervals.set(key, interval);
        console.log(`🔄 Auto-refresh started for ${key} every ${intervalMs}ms`);
    }

    stop(key) {
        const interval = this.intervals.get(key);
        if (interval) {
            clearInterval(interval);
            this.intervals.delete(key);
            console.log(`⏹️ Auto-refresh stopped for ${key}`);
        }
    }

    stopAll() {
        this.intervals.forEach((interval, key) => this.stop(key));
    }
}

window.ASIRefresh = new DashboardAutoRefresh();

// 🎨 UI Update Utilities
class DashboardUI {
    static updateCard(cardId, title, data, status = 'success') {
        const card = document.getElementById(cardId);
        if (!card) return;

        const statusClass = status === 'error' ? 'error' : status === 'loading' ? 'loading' : 'success';
        const timestamp = new Date().toLocaleString('sq-AL');

        let content = '';
        if (typeof data === 'object' && data !== null) {
            content = Object.entries(data).map(([key, value]) => {
                if (typeof value === 'object') value = JSON.stringify(value);
                return `
                    <div class="data-row">
                        <span class="label">${key.replace(/_/g, ' ')}</span>
                        <span class="value">${value}</span>
                    </div>
                `;
            }).join('');
        } else {
            content = `<div class="data-row"><span class="value">${data}</span></div>`;
        }

        card.innerHTML = `
            <div class="card-header ${statusClass}">
                <h3>${title}</h3>
                <span class="status-badge ${statusClass}">🔴 LIVE</span>
            </div>
            <div class="card-content">
                ${content}
            </div>
            <div class="card-footer">
                <small>Përditësuar: ${timestamp}</small>
            </div>
        `;
    }

    static showLoading(cardId, message = 'Duke ngarkuar...') {
        this.updateCard(cardId, message, '⏳ Ju lutemi prisni...', 'loading');
    }

    static showError(cardId, error) {
        this.updateCard(cardId, 'Gabim', `❌ ${error.message || error}`, 'error');
    }
}

// 📊 Real Dashboard Controllers
class RealDashboardController {
    constructor() {
        this.isInitialized = false;
    }

    async init() {
        if (this.isInitialized) return;
        
        console.log('🚀 Initializing Real Dashboard Controller...');
        
        // Setup event listeners
        this.setupEventListeners();
        
        // Load initial data
        await this.loadInitialData();
        
        // Start auto-refresh
        this.startAutoRefresh();
        
        this.isInitialized = true;
        console.log('✅ Real Dashboard Controller initialized');
    }

    setupEventListeners() {
        // Real data buttons
        document.getElementById('btn-real-news')?.addEventListener('click', () => this.loadRealNews());
        document.getElementById('btn-real-financial')?.addEventListener('click', () => this.loadRealFinancial());
        document.getElementById('btn-real-economic')?.addEventListener('click', () => this.loadRealEconomic());
        document.getElementById('btn-real-cultural')?.addEventListener('click', () => this.loadRealCultural());
        document.getElementById('btn-all-real')?.addEventListener('click', () => this.loadAllRealData());
        
        // CBOR performance
        document.getElementById('btn-cbor-performance')?.addEventListener('click', () => this.loadCBORPerformance());
    }

    async loadInitialData() {
        // Load financial data first (most reliable)
        await this.loadRealFinancial();
    }

    async loadRealNews() {
        try {
            DashboardUI.showLoading('card-news', 'Duke marrë lajme reale...');
            const result = await window.ASI.getRealNews(5);
            
            if (result.data && result.data.error) {
                DashboardUI.updateCard('card-news', 'Real News Status', {
                    'Status': result.data.message,
                    'Available Sources': result.data.available_sources?.join(', ') || 'Multiple',
                    'Note': result.data.asi_note
                });
            } else {
                DashboardUI.updateCard('card-news', 'Real News - Live', result.data || result);
            }
        } catch (error) {
            DashboardUI.showError('card-news', error);
        }
    }

    async loadRealFinancial() {
        try {
            DashboardUI.showLoading('card-financial', 'Duke marrë të dhëna financiare reale...');
            const result = await window.ASI.getRealFinancial('EUR', 'forex');
            
            if (result.data && result.data.rates) {
                const rates = result.data.rates;
                DashboardUI.updateCard('card-financial', 'EUR Exchange Rates - Live', {
                    'EUR → USD': rates.USD,
                    'EUR → GBP': rates.GBP,
                    'EUR → JPY': rates.JPY,
                    'EUR → CHF': rates.CHF,
                    'Last Updated': result.data.date,
                    'Source': result.data.asi_analysis?.data_source || 'Live API'
                });
            } else {
                DashboardUI.updateCard('card-financial', 'Real Financial', result.data || result);
            }
        } catch (error) {
            DashboardUI.showError('card-financial', error);
        }
    }

    async loadRealEconomic() {
        try {
            DashboardUI.showLoading('card-economic', 'Duke marrë të dhëna ekonomike reale...');
            const result = await window.ASI.getRealEconomic('WLD', 'GDP');
            
            if (result.data && result.data.data_points) {
                const latest = result.data.data_points[0];
                DashboardUI.updateCard('card-economic', 'World GDP - Real Data', {
                    'Latest GDP': latest?.formatted_value || 'N/A',
                    'Year': latest?.year || 'N/A',
                    'Country': latest?.country_name || 'World',
                    'Source': result.data.source || 'World Bank',
                    'Authenticity': result.data.asi_analysis?.authenticity || 'Official Data'
                });
            } else {
                DashboardUI.updateCard('card-economic', 'Real Economic', result.data || result);
            }
        } catch (error) {
            DashboardUI.showError('card-economic', error);
        }
    }

    async loadRealCultural() {
        try {
            DashboardUI.showLoading('card-cultural', 'Duke marrë të dhëna kulturore reale...');
            const result = await window.ASI.getRealCultural('Albania', 'summary');
            
            if (result.data) {
                DashboardUI.updateCard('card-cultural', 'Cultural Data - Albania', {
                    'Title': result.data.title || 'Albania',
                    'Description': (result.data.description || 'N/A').substring(0, 100) + '...',
                    'Source': result.data.source || 'Wikipedia',
                    'Page URL': result.data.page_url ? 'Available' : 'N/A'
                });
            } else {
                DashboardUI.updateCard('card-cultural', 'Real Cultural', result.data || result);
            }
        } catch (error) {
            DashboardUI.showError('card-cultural', error);
        }
    }

    async loadAllRealData() {
        try {
            DashboardUI.showLoading('card-all', 'Duke marrë të gjitha të dhënat reale...');
            const result = await window.ASI.getAllRealData();
            
            if (result.data) {
                DashboardUI.updateCard('card-all', 'All Real Data Analytics', {
                    'Data Sources': result.data.asi_real_insights?.api_sources?.join(', ') || 'Multiple',
                    'Authenticity': result.data.asi_real_insights?.data_authenticity || '100% Real',
                    'Mock Data': result.data.asi_real_insights?.no_mock_data ? 'None' : 'Present',
                    'Real Time': result.data.asi_real_insights?.real_time_updates ? 'Active' : 'Inactive',
                    'Status': result.asi_status || 'Active'
                });
            } else {
                DashboardUI.updateCard('card-all', 'Real Analytics', result);
            }
        } catch (error) {
            DashboardUI.showError('card-all', error);
        }
    }

    async loadCBORPerformance() {
        try {
            DashboardUI.showLoading('card-cbor', 'Duke marrë performancën CBOR...');
            const result = await window.ASI.getCBORPerformance();
            
            if (result.cbor_performance) {
                const perf = result.cbor_performance;
                DashboardUI.updateCard('card-cbor', 'CBOR Performance - Real Metrics', {
                    'Size Reduction': `${perf.size_reduction}%`,
                    'Speed Improvement': `${perf.speed_improvement}x`,
                    'Compression Ratio': perf.compression_ratio,
                    'Memory Usage': `${perf.memory_usage}%`,
                    'ASI Enhancement': result.asi_cbor_note || 'Active'
                });
            } else {
                DashboardUI.updateCard('card-cbor', 'CBOR Performance', result);
            }
        } catch (error) {
            DashboardUI.showError('card-cbor', error);
        }
    }

    startAutoRefresh() {
        // Refresh financial data every 60 seconds
        window.ASIRefresh.start('financial', () => this.loadRealFinancial(), 60000);
        
        // Refresh news every 5 minutes
        window.ASIRefresh.start('news', () => this.loadRealNews(), 300000);
        
        // Refresh economic data every 30 minutes
        window.ASIRefresh.start('economic', () => this.loadRealEconomic(), 1800000);
    }

    destroy() {
        window.ASIRefresh.stopAll();
        this.isInitialized = false;
    }
}

// 🌍 Global Dashboard Controller
window.DashboardController = new RealDashboardController();

// 🚀 Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.DashboardController.init();
});

console.log('🔴 ASI Real API Client loaded successfully!');
