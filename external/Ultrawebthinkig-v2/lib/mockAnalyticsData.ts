/**
 * 📊 ASI Analytics Mock Data Provider
 * Provides sample data for testing analytics components
 */

export const mockAnalyticsData = {
  users: {
    total: 2847,
    active: 2156,
    growth: 12.5,
    chartData: [
      { date: '2025-10-01', total: 2450, active: 1950 },
      { date: '2025-10-02', total: 2465, active: 1968 },
      { date: '2025-10-03', total: 2485, active: 1985 },
      { date: '2025-10-04', total: 2520, active: 2015 },
      { date: '2025-10-05', total: 2560, active: 2048 },
      { date: '2025-10-06', total: 2598, active: 2087 },
      { date: '2025-10-07', total: 2635, active: 2125 },
      { date: '2025-10-08', total: 2678, active: 2145 },
      { date: '2025-10-09', total: 2715, active: 2168 },
      { date: '2025-10-10', total: 2756, active: 2187 },
      { date: '2025-10-11', total: 2789, active: 2205 },
      { date: '2025-10-12', total: 2823, active: 2234 },
      { date: '2025-10-13', total: 2847, active: 2156 }
    ]
  },
  
  revenue: {
    mrr: 42156,
    arr: 505872,
    growth: 5.3,
    chartData: [
      { month: '2025-01', mrr: 35420, arr: 425040 },
      { month: '2025-02', mrr: 36890, arr: 442680 },
      { month: '2025-03', mrr: 38245, arr: 458940 },
      { month: '2025-04', mrr: 39654, arr: 475848 },
      { month: '2025-05', mrr: 40123, arr: 481476 },
      { month: '2025-06', mrr: 41567, arr: 498804 },
      { month: '2025-07', mrr: 42156, arr: 505872 }
    ]
  },
  
  subscriptions: {
    active: 1845,
    churned: 48,
    churnRate: 2.4,
    planDistribution: [
      { plan: 'Basic', count: 856, revenue: 8560 },
      { plan: 'Pro', count: 654, revenue: 32700 },
      { plan: 'Enterprise', count: 335, revenue: 33500 }
    ]
  },
  
  orders: {
    total: 1256,
    revenue: 124592,
    averageOrder: 99.19,
    chartData: [
      { date: '2025-10-01', orders: 89, revenue: 8920 },
      { date: '2025-10-02', orders: 95, revenue: 9456 },
      { date: '2025-10-03', orders: 78, revenue: 7845 },
      { date: '2025-10-04', orders: 112, revenue: 11245 },
      { date: '2025-10-05', orders: 134, revenue: 13456 },
      { date: '2025-10-06', orders: 98, revenue: 9876 },
      { date: '2025-10-07', orders: 87, revenue: 8745 },
      { date: '2025-10-08', orders: 156, revenue: 15678 },
      { date: '2025-10-09', orders: 142, revenue: 14256 },
      { date: '2025-10-10', orders: 167, revenue: 16789 },
      { date: '2025-10-11', orders: 198, revenue: 19856 },
      { date: '2025-10-12', orders: 189, revenue: 18934 },
      { date: '2025-10-13', orders: 211, revenue: 21156 }
    ]
  }
};

/**
 * 🎯 Mock API Functions for Development
 */
export const mockCubeApi = {
  load: async (query: any) => {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Return mock data based on query
    if (query.measures?.includes('Users.count')) {
      return {
        data: mockAnalyticsData.users.chartData.map(item => ({
          'Users.count': item.total,
          'Users.activeCount': item.active,
          'Users.createdAt': item.date
        })),
        chartPivot: () => mockAnalyticsData.users.chartData.map(item => ({
          x: item.date,
          'Users.count': item.total,
          'Users.activeCount': item.active
        }))
      };
    }
    
    if (query.measures?.includes('Subscriptions.mrr')) {
      return {
        data: mockAnalyticsData.revenue.chartData,
        chartPivot: () => mockAnalyticsData.revenue.chartData.map(item => ({
          x: item.month,
          'Subscriptions.mrr': item.mrr,
          'Subscriptions.arr': item.arr
        }))
      };
    }
    
    if (query.measures?.includes('Orders.revenue')) {
      return {
        data: mockAnalyticsData.orders.chartData,
        chartPivot: () => mockAnalyticsData.orders.chartData.map(item => ({
          x: item.date,
          'Orders.revenue': item.revenue,
          'Orders.count': item.orders
        }))
      };
    }
    
    // Default empty response
    return {
      data: [],
      chartPivot: () => []
    };
  }
};

/**
 * 🔄 Real-time Data Generator (for demo purposes)
 */
export const generateRealTimeMetrics = () => {
  const baseMetrics = mockAnalyticsData;
  const variance = 0.05; // 5% variance
  
  return {
    totalRevenue: Math.round(baseMetrics.orders.revenue * (1 + (Math.random() - 0.5) * variance)),
    activeUsers: Math.round(baseMetrics.users.active * (1 + (Math.random() - 0.5) * variance)),
    mrr: Math.round(baseMetrics.revenue.mrr * (1 + (Math.random() - 0.5) * variance)),
    churnRate: Math.round(baseMetrics.subscriptions.churnRate * (1 + (Math.random() - 0.5) * variance) * 10) / 10
  };
};
