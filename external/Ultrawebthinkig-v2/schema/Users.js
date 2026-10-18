/**
 * Users Cube Schema - User Analytics & Metrics
 * EuroWeb Platform User Behavior Analysis
 * 
 * @author Ledjan Ahmati
 * @version 8.0.0-CUBE-ANALYTICS
 */

cube(`Users`, {
  sql: `
    SELECT 
      id,
      email,
      username,
      created_at,
      last_login,
      subscription_type,
      tenant_id,
      country,
      device_type,
      browser,
      is_active,
      total_sessions,
      total_revenue
    FROM users
  `,

  // Dimensions
  dimensions: {
    id: {
      sql: `id`,
      type: `string`,
      primaryKey: true
    },

    email: {
      sql: `email`,
      type: `string`,
      shown: false // Hide PII in analytics
    },

    username: {
      sql: `username`,
      type: `string`
    },

    subscriptionType: {
      sql: `subscription_type`,
      type: `string`,
      title: 'Subscription Type'
    },

    tenantId: {
      sql: `tenant_id`,
      type: `string`,
      title: 'Tenant ID'
    },

    country: {
      sql: `country`,
      type: `string`
    },

    deviceType: {
      sql: `device_type`,
      type: `string`,
      title: 'Device Type'
    },

    browser: {
      sql: `browser`,
      type: `string`
    },

    isActive: {
      sql: `is_active`,
      type: `boolean`,
      title: 'Active Status'
    },

    // Time dimensions
    createdAt: {
      sql: `created_at`,
      type: `time`,
      title: 'Registration Date'
    },

    lastLogin: {
      sql: `last_login`,
      type: `time`,
      title: 'Last Login'
    },

    createdAtDate: {
      sql: `DATE(created_at)`,
      type: `time`,
      title: 'Registration Date (Day)'
    },

    createdAtMonth: {
      sql: `DATE_TRUNC('month', created_at)`,
      type: `time`,
      title: 'Registration Month'
    }
  },

  // Measures
  measures: {
    count: {
      type: `count`,
      title: 'Total Users'
    },

    activeUsers: {
      sql: `id`,
      type: `count`,
      title: 'Active Users',
      filters: [
        { sql: `${CUBE}.is_active = true` }
      ]
    },

    newUsers: {
      sql: `id`,
      type: `count`,
      title: 'New Users (Last 30 days)',
      filters: [
        { sql: `${CUBE}.created_at >= NOW() - INTERVAL '30 days'` }
      ]
    },

    premiumUsers: {
      sql: `id`,
      type: `count`,
      title: 'Premium Users',
      filters: [
        { sql: `${CUBE}.subscription_type IN ('premium', 'ultra', 'enterprise')` }
      ]
    },

    totalRevenue: {
      sql: `SUM(total_revenue)`,
      type: `number`,
      title: 'Total Revenue',
      format: 'currency'
    },

    averageRevenue: {
      sql: `AVG(total_revenue)`,
      type: `number`,
      title: 'Average Revenue Per User',
      format: 'currency'
    },

    totalSessions: {
      sql: `SUM(total_sessions)`,
      type: `number`,
      title: 'Total Sessions'
    },

    averageSessions: {
      sql: `AVG(total_sessions)`,
      type: `number`,
      title: 'Average Sessions Per User'
    },

    // Retention metrics
    retentionRate: {
      sql: `
        COUNT(CASE WHEN last_login >= NOW() - INTERVAL '7 days' THEN 1 END) * 100.0 / 
        COUNT(CASE WHEN created_at <= NOW() - INTERVAL '7 days' THEN 1 END)
      `,
      type: `number`,
      title: 'Weekly Retention Rate (%)',
      format: 'percent'
    },

    churnRate: {
      sql: `
        COUNT(CASE WHEN last_login < NOW() - INTERVAL '30 days' AND is_active = false THEN 1 END) * 100.0 / 
        COUNT(*)
      `,
      type: `number`,
      title: 'Churn Rate (%)',
      format: 'percent'
    }
  },

  // Pre-aggregations for performance
  preAggregations: {
    // Daily user counts
    dailyUsers: {
      measures: [
        Users.count,
        Users.newUsers,
        Users.activeUsers
      ],
      dimensions: [
        Users.createdAtDate
      ],
      timeDimension: Users.createdAt,
      granularity: `day`,
      refreshKey: {
        every: `1 hour`
      }
    },

    // Monthly metrics
    monthlyMetrics: {
      measures: [
        Users.count,
        Users.totalRevenue,
        Users.averageRevenue,
        Users.retentionRate
      ],
      dimensions: [
        Users.subscriptionType,
        Users.country
      ],
      timeDimension: Users.createdAt,
      granularity: `month`,
      refreshKey: {
        every: `1 day`
      }
    },

    // Device and browser analytics
    deviceAnalytics: {
      measures: [
        Users.count,
        Users.activeUsers
      ],
      dimensions: [
        Users.deviceType,
        Users.browser,
        Users.country
      ],
      refreshKey: {
        every: `6 hours`
      }
    }
  },

  // Data source
  dataSource: `default`
});
