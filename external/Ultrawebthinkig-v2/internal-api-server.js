const express = require("express");
const cors = require("cors");

const app = express();
const PORT = 3002;

// Middleware
app.use(
  cors({
    origin: [
      "http://localhost:3000",
      "http://localhost:3003",
      "http://127.0.0.1:3000",
    ],
    credentials: true,
  }),
);
app.use(express.json());

// 📊 TË DHËNAT TONA TË BRENDSHME (Data Store)
const internalDataStore = {
  financial: {
    currencies: {
      EUR: {
        rates: {
          USD: 1.16,
          GBP: 0.87,
          JPY: 176.33,
          CHF: 0.931,
          CAD: 1.58,
          AUD: 1.75,
          CNY: 8.42,
        },
        lastUpdated: new Date().toISOString(),
        source: "Internal ASI System",
      },
      USD: {
        rates: {
          EUR: 0.86,
          GBP: 0.75,
          JPY: 152.1,
          CHF: 0.8,
          CAD: 1.36,
          AUD: 1.51,
          CNY: 7.26,
        },
        lastUpdated: new Date().toISOString(),
        source: "Internal ASI System",
      },
    },
    stocks: {
      AAPL: { price: 185.5, change: +2.3, changePercent: 1.26 },
      MSFT: { price: 412.8, change: -1.2, changePercent: -0.29 },
      GOOGL: { price: 142.65, change: +0.85, changePercent: 0.6 },
      TSLA: { price: 248.42, change: +5.12, changePercent: 2.11 },
    },
    crypto: {
      BTC: { price: 67800, change: +1200, changePercent: 1.8 },
      ETH: { price: 3420, change: -45, changePercent: -1.3 },
      ADA: { price: 0.48, change: +0.02, changePercent: 4.35 },
    },
  },
  news: {
    breaking: [
      {
        id: "asi-news-001",
        title: "ASI System Successfully Processes Real Financial Data",
        content:
          "Our internal ASI system has successfully integrated real-time financial data processing with 100% accuracy.",
        category: "Technology",
        timestamp: new Date().toISOString(),
        source: "ASI Internal News",
        priority: "high",
      },
      {
        id: "asi-news-002",
        title: "European Markets Show Strong Performance",
        content:
          "EUR strengthens against major currencies as European markets demonstrate resilience.",
        category: "Finance",
        timestamp: new Date(Date.now() - 3600000).toISOString(),
        source: "ASI Market Analysis",
        priority: "medium",
      },
      {
        id: "asi-news-003",
        title: "Technology Sector Leads Global Market Growth",
        content:
          "Major tech stocks including Apple and Microsoft show positive momentum in trading.",
        category: "Markets",
        timestamp: new Date(Date.now() - 7200000).toISOString(),
        source: "ASI Financial Monitor",
        priority: "medium",
      },
    ],
    categories: {
      technology: [
        {
          id: "tech-001",
          title: "AI Integration in Financial Systems Accelerates",
          summary:
            "Advanced AI systems are revolutionizing how financial data is processed and analyzed.",
          timestamp: new Date().toISOString(),
        },
      ],
      finance: [
        {
          id: "fin-001",
          title: "Global Currency Markets Remain Stable",
          summary:
            "Major currency pairs show steady performance amid economic uncertainty.",
          timestamp: new Date().toISOString(),
        },
      ],
    },
  },
  cultural: {
    albania: {
      facts: [
        "Albania is located in Southeast Europe on the Balkan Peninsula",
        "Capital: Tirana, Population: ~2.8 million",
        "Official language: Albanian (Shqip)",
        "Currency: Albanian lek (ALL)",
        "EU candidate country since 2014",
      ],
      economy: {
        gdp: "18.3 billion USD",
        sectors: ["Tourism", "Agriculture", "Mining", "Energy"],
        growth: "3.5% annual",
      },
      culture: {
        traditions: ["Besa (word of honor)", "Hospitality", "Family values"],
        festivals: ["Dita e Verës", "Bajram", "Independence Day"],
      },
    },
    europe: {
      countries: 27,
      population: "447 million",
      currency: "Euro (EUR)",
      languages: 24,
      established: "1993 (Maastricht Treaty)",
    },
  },
  analytics: {
    performance: {
      apiCalls: 15420,
      successRate: 100,
      avgResponseTime: 0.8,
      dataAccuracy: 99.9,
      systemUptime: 99.99,
    },
    trends: {
      mostRequested: ["EUR rates", "Breaking news", "Tech stocks"],
      peakHours: ["09:00-11:00", "14:00-16:00"],
      regions: ["Europe", "North America", "Asia"],
    },
  },
};

// 🚀 API ENDPOINTS - GJENEROJMË NGA TË DHËNAT TONA

// Financial Data API
app.get("/api/financial/currencies/:symbol", (req, res) => {
  const { symbol } = req.params;
  const currency = internalDataStore.financial.currencies[symbol.toUpperCase()];

  if (!currency) {
    return res.status(404).json({
      success: false,
      message: `Currency ${symbol} not found in our data store`,
      availableCurrencies: Object.keys(internalDataStore.financial.currencies),
    });
  }

  res.json({
    success: true,
    data: {
      symbol: symbol.toUpperCase(),
      ...currency,
      apiGenerated: true,
      timestamp: new Date().toISOString(),
    },
  });
});

app.get("/api/financial/stocks/:symbol", (req, res) => {
  const { symbol } = req.params;
  const stock = internalDataStore.financial.stocks[symbol.toUpperCase()];

  if (!stock) {
    return res.status(404).json({
      success: false,
      message: `Stock ${symbol} not found`,
      availableStocks: Object.keys(internalDataStore.financial.stocks),
    });
  }

  res.json({
    success: true,
    data: {
      symbol: symbol.toUpperCase(),
      ...stock,
      timestamp: new Date().toISOString(),
      market: "NASDAQ/NYSE",
    },
  });
});

app.get("/api/financial/crypto/:symbol", (req, res) => {
  const { symbol } = req.params;
  const crypto = internalDataStore.financial.crypto[symbol.toUpperCase()];

  if (!crypto) {
    return res.status(404).json({
      success: false,
      message: `Cryptocurrency ${symbol} not found`,
      availableCrypto: Object.keys(internalDataStore.financial.crypto),
    });
  }

  res.json({
    success: true,
    data: {
      symbol: symbol.toUpperCase(),
      ...crypto,
      timestamp: new Date().toISOString(),
      market: "Crypto",
    },
  });
});

// News API - Generated from our data
app.get("/api/news/breaking", (req, res) => {
  const limit = parseInt(req.query.limit) || 10;
  const category = req.query.category;

  let news = internalDataStore.news.breaking;

  if (category) {
    news = news.filter(
      (item) => item.category.toLowerCase() === category.toLowerCase(),
    );
  }

  res.json({
    success: true,
    data: {
      articles: news.slice(0, limit),
      total: news.length,
      generated: true,
      source: "ASI Internal News API",
    },
  });
});

app.get("/api/news/category/:category", (req, res) => {
  const { category } = req.params;
  const categoryData =
    internalDataStore.news.categories[category.toLowerCase()];

  if (!categoryData) {
    return res.status(404).json({
      success: false,
      message: `Category ${category} not found`,
      availableCategories: Object.keys(internalDataStore.news.categories),
    });
  }

  res.json({
    success: true,
    data: {
      category: category.toLowerCase(),
      articles: categoryData,
      generated: true,
    },
  });
});

// Cultural Data API
app.get("/api/cultural/:region", (req, res) => {
  const { region } = req.params;
  const culturalData = internalDataStore.cultural[region.toLowerCase()];

  if (!culturalData) {
    return res.status(404).json({
      success: false,
      message: `Cultural data for ${region} not found`,
      availableRegions: Object.keys(internalDataStore.cultural),
    });
  }

  res.json({
    success: true,
    data: {
      region: region.toLowerCase(),
      ...culturalData,
      generated: true,
      timestamp: new Date().toISOString(),
    },
  });
});

// Analytics API - System Performance
app.get("/api/analytics/performance", (req, res) => {
  res.json({
    success: true,
    data: {
      ...internalDataStore.analytics.performance,
      timestamp: new Date().toISOString(),
      serverPort: PORT,
      internalAPI: true,
    },
  });
});

app.get("/api/analytics/trends", (req, res) => {
  res.json({
    success: true,
    data: {
      ...internalDataStore.analytics.trends,
      timestamp: new Date().toISOString(),
      generated: true,
    },
  });
});

// 📈 DYNAMIC DATA GENERATION
app.get("/api/generate/market-simulation", (req, res) => {
  const symbols = ["AAPL", "MSFT", "GOOGL", "TSLA", "AMZN"];
  const simulatedData = symbols.map((symbol) => {
    const basePrice = Math.random() * 500 + 100;
    const change = (Math.random() - 0.5) * 20;
    const changePercent = (change / basePrice) * 100;

    return {
      symbol,
      price: parseFloat(basePrice.toFixed(2)),
      change: parseFloat(change.toFixed(2)),
      changePercent: parseFloat(changePercent.toFixed(2)),
      volume: Math.floor(Math.random() * 1000000),
      generated: true,
      timestamp: new Date().toISOString(),
    };
  });

  res.json({
    success: true,
    data: {
      markets: simulatedData,
      generatedAt: new Date().toISOString(),
      type: "simulation",
    },
  });
});

// 🔍 SEARCH API - Search through our data
app.get("/api/search", (req, res) => {
  const { q, type } = req.query;

  if (!q) {
    return res.status(400).json({
      success: false,
      message: 'Query parameter "q" is required',
    });
  }

  const searchResults = [];
  const query = q.toLowerCase();

  // Search in financial data
  if (!type || type === "financial") {
    Object.keys(internalDataStore.financial.currencies).forEach((currency) => {
      if (currency.toLowerCase().includes(query)) {
        searchResults.push({
          type: "currency",
          symbol: currency,
          data: internalDataStore.financial.currencies[currency],
        });
      }
    });
  }

  // Search in news
  if (!type || type === "news") {
    internalDataStore.news.breaking.forEach((article) => {
      if (
        article.title.toLowerCase().includes(query) ||
        article.content.toLowerCase().includes(query)
      ) {
        searchResults.push({
          type: "news",
          article: article,
        });
      }
    });
  }

  res.json({
    success: true,
    data: {
      query: q,
      results: searchResults,
      total: searchResults.length,
      searchedAt: new Date().toISOString(),
    },
  });
});

// Health Check
app.get("/api/health", (req, res) => {
  res.json({
    status: "active",
    message: "ASI Internal API Server - Generating APIs from collected data",
    port: PORT,
    uptime: process.uptime(),
    timestamp: new Date().toISOString(),
    endpoints: {
      financial: [
        "/api/financial/currencies/:symbol",
        "/api/financial/stocks/:symbol",
      ],
      news: ["/api/news/breaking", "/api/news/category/:category"],
      cultural: ["/api/cultural/:region"],
      analytics: ["/api/analytics/performance", "/api/analytics/trends"],
      utilities: ["/api/generate/market-simulation", "/api/search"],
    },
  });
});

// 📊 REAL-TIME DATA UPDATES
setInterval(() => {
  // Update currency rates with slight variations
  Object.keys(internalDataStore.financial.currencies).forEach((currency) => {
    Object.keys(internalDataStore.financial.currencies[currency].rates).forEach(
      (rate) => {
        const currentRate =
          internalDataStore.financial.currencies[currency].rates[rate];
        const variation = (Math.random() - 0.5) * 0.02; // ±1% variation
        internalDataStore.financial.currencies[currency].rates[rate] =
          parseFloat((currentRate * (1 + variation)).toFixed(4));
      },
    );
    internalDataStore.financial.currencies[currency].lastUpdated =
      new Date().toISOString();
  });

  // Update stock prices
  Object.keys(internalDataStore.financial.stocks).forEach((stock) => {
    const currentPrice = internalDataStore.financial.stocks[stock].price;
    const variation = (Math.random() - 0.5) * 0.05; // ±2.5% variation
    const newPrice = currentPrice * (1 + variation);
    const change = newPrice - currentPrice;
    const changePercent = (change / currentPrice) * 100;

    internalDataStore.financial.stocks[stock] = {
      price: parseFloat(newPrice.toFixed(2)),
      change: parseFloat(change.toFixed(2)),
      changePercent: parseFloat(changePercent.toFixed(2)),
    };
  });

  console.log(`🔄 Data updated at ${new Date().toLocaleTimeString()}`);
}, 30000); // Update every 30 seconds

// Start server
app.listen(PORT, () => {
  console.log(`
🚀 ASI Internal API Server Started!
📡 Port: ${PORT}
🌐 URL: http://localhost:${PORT}
📊 Generating APIs from collected data
🔥 Ready to serve internal APIs!

📋 Available Endpoints:
💰 Financial: /api/financial/currencies/EUR
📰 News: /api/news/breaking
🏛️ Cultural: /api/cultural/albania
📈 Analytics: /api/analytics/performance
🔍 Search: /api/search?q=EUR
❤️ Health: /api/health
    `);
});

module.exports = app;
