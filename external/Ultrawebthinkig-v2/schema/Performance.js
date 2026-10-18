/**
 * Performance Cube Schema - System Performance Metrics
 * EuroWeb Platform Performance Analytics
 * 
 * @author Ledjan Ahmati
 * @version 8.0.0-CUBE-ANALYTICS
 */

cube(`Performance`, {
  sql: `
    SELECT 
      id,
      timestamp,
      service_name,
      endpoint,
      response_time_ms,
      memory_usage_mb,
      cpu_usage_percent,
      error_rate,
      throughput_rps,
      status_code,
      user_agent,
      ip_address,
      country,
      server_region,
      cache_hit_ratio,
      database_query_time_ms,
      network_latency_ms
    FROM performance_logs
  `,

  // Dimensions
  dimensions: {
    id: {
      sql: `id`,
      type: `string`,
      primaryKey: true
    },

    serviceName: {
      sql: `service_name`,
      type: `string`,
      title: 'Service Name'
    },

    endpoint: {
      sql: `endpoint`,
      type: `string`
    },

    statusCode: {
      sql: `status_code`,
      type: `string`,
      title: 'HTTP Status Code'
    },

    country: {
      sql: `country`,
      type: `string`
    },

    serverRegion: {
      sql: `server_region`,
      type: `string`,
      title: 'Server Region'
    },

    userAgent: {
      sql: `user_agent`,
      type: `string`,
      title: 'User Agent',
      shown: false // Hide detailed user agent
    },

    // Time dimensions
    timestamp: {
      sql: `timestamp`,
      type: `time`
    },

    timestampHour: {
      sql: `DATE_TRUNC('hour', timestamp)`,
      type: `time`,
      title: 'Hour'
    },

    timestampDay: {
      sql: `DATE_TRUNC('day', timestamp)`,
      type: `time`,
      title: 'Day'
    },

    // Performance categories
    performanceCategory: {
      sql: `
        CASE 
          WHEN response_time_ms < 100 THEN 'Excellent'
          WHEN response_time_ms < 300 THEN 'Good'
          WHEN response_time_ms < 1000 THEN 'Fair'
          ELSE 'Poor'
        END
      `,
      type: `string`,
      title: 'Performance Category'
    },

    errorCategory: {
      sql: `
        CASE 
          WHEN status_code LIKE '2%' THEN 'Success'
          WHEN status_code LIKE '3%' THEN 'Redirect'
          WHEN status_code LIKE '4%' THEN 'Client Error'
          WHEN status_code LIKE '5%' THEN 'Server Error'
          ELSE 'Unknown'
        END
      `,
      type: `string`,
      title: 'Response Category'
    }
  },

  // Measures
  measures: {
    count: {
      type: `count`,
      title: 'Total Requests'
    },

    // Response Time Metrics
    averageResponseTime: {
      sql: `AVG(response_time_ms)`,
      type: `number`,
      title: 'Average Response Time (ms)',
      format: '#,##0.00'
    },

    medianResponseTime: {
      sql: `PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY response_time_ms)`,
      type: `number`,
      title: 'Median Response Time (ms)',
      format: '#,##0.00'
    },

    p95ResponseTime: {
      sql: `PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY response_time_ms)`,
      type: `number`,
      title: '95th Percentile Response Time (ms)',
      format: '#,##0.00'
    },

    p99ResponseTime: {
      sql: `PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY response_time_ms)`,
      type: `number`,
      title: '99th Percentile Response Time (ms)',
      format: '#,##0.00'
    },

    maxResponseTime: {
      sql: `MAX(response_time_ms)`,
      type: `number`,
      title: 'Max Response Time (ms)',
      format: '#,##0.00'
    },

    minResponseTime: {
      sql: `MIN(response_time_ms)`,
      type: `number`,
      title: 'Min Response Time (ms)',
      format: '#,##0.00'
    },

    // Memory Usage
    averageMemoryUsage: {
      sql: `AVG(memory_usage_mb)`,
      type: `number`,
      title: 'Average Memory Usage (MB)',
      format: '#,##0.00'
    },

    maxMemoryUsage: {
      sql: `MAX(memory_usage_mb)`,
      type: `number`,
      title: 'Peak Memory Usage (MB)',
      format: '#,##0.00'
    },

    // CPU Usage
    averageCpuUsage: {
      sql: `AVG(cpu_usage_percent)`,
      type: `number`,
      title: 'Average CPU Usage (%)',
      format: '#,##0.00'
    },

    maxCpuUsage: {
      sql: `MAX(cpu_usage_percent)`,
      type: `number`,
      title: 'Peak CPU Usage (%)',
      format: '#,##0.00'
    },

    // Error Rates
    errorRate: {
      sql: `AVG(error_rate) * 100`,
      type: `number`,
      title: 'Error Rate (%)',
      format: '#,##0.000'
    },

    errorCount: {
      sql: `COUNT(*)`,
      type: `count`,
      title: 'Error Count',
      filters: [
        { sql: `${CUBE}.status_code NOT LIKE '2%'` }
      ]
    },

    successRate: {
      sql: `
        COUNT(CASE WHEN status_code LIKE '2%' THEN 1 END) * 100.0 / COUNT(*)
      `,
      type: `number`,
      title: 'Success Rate (%)',
      format: '#,##0.00'
    },

    // Throughput
    averageThroughput: {
      sql: `AVG(throughput_rps)`,
      type: `number`,
      title: 'Average Throughput (RPS)',
      format: '#,##0.00'
    },

    maxThroughput: {
      sql: `MAX(throughput_rps)`,
      type: `number`,
      title: 'Peak Throughput (RPS)',
      format: '#,##0.00'
    },

    totalRequests: {
      sql: `SUM(throughput_rps)`,
      type: `number`,
      title: 'Total Requests Processed',
      format: '#,##0'
    },

    // Cache Performance
    averageCacheHitRatio: {
      sql: `AVG(cache_hit_ratio) * 100`,
      type: `number`,
      title: 'Average Cache Hit Ratio (%)',
      format: '#,##0.00'
    },

    // Database Performance
    averageDbQueryTime: {
      sql: `AVG(database_query_time_ms)`,
      type: `number`,
      title: 'Average DB Query Time (ms)',
      format: '#,##0.00'
    },

    // Network Performance
    averageNetworkLatency: {
      sql: `AVG(network_latency_ms)`,
      type: `number`,
      title: 'Average Network Latency (ms)',
      format: '#,##0.00'
    },

    // Availability
    uptime: {
      sql: `
        COUNT(CASE WHEN status_code LIKE '2%' OR status_code LIKE '3%' THEN 1 END) * 100.0 / COUNT(*)
      `,
      type: `number`,
      title: 'Uptime (%)',
      format: '#,##0.000'
    },

    // Performance Score (custom metric)
    performanceScore: {
      sql: `
        AVG(
          CASE 
            WHEN response_time_ms < 100 AND error_rate < 0.01 THEN 100
            WHEN response_time_ms < 300 AND error_rate < 0.05 THEN 80
            WHEN response_time_ms < 1000 AND error_rate < 0.1 THEN 60
            WHEN response_time_ms < 3000 AND error_rate < 0.2 THEN 40
            ELSE 20
          END
        )
      `,
      type: `number`,
      title: 'Performance Score (0-100)',
      format: '#,##0.0'
    }
  },

  // Pre-aggregations for high-performance analytics
  preAggregations: {
    // Hourly performance metrics
    hourlyPerformance: {
      measures: [
        Performance.count,
        Performance.averageResponseTime,
        Performance.errorRate,
        Performance.averageThroughput,
        Performance.performanceScore
      ],
      dimensions: [
        Performance.serviceName,
        Performance.endpoint
      ],
      timeDimension: Performance.timestamp,
      granularity: `hour`,
      refreshKey: {
        every: `10 minutes`
      }
    },

    // Daily performance summary
    dailyPerformance: {
      measures: [
        Performance.count,
        Performance.averageResponseTime,
        Performance.p95ResponseTime,
        Performance.errorRate,
        Performance.successRate,
        Performance.maxThroughput,
        Performance.uptime
      ],
      dimensions: [
        Performance.serviceName,
        Performance.country,
        Performance.serverRegion
      ],
      timeDimension: Performance.timestamp,
      granularity: `day`,
      refreshKey: {
        every: `1 hour`
      }
    },

    // Real-time monitoring (last 24 hours)
    realtimeMetrics: {
      measures: [
        Performance.count,
        Performance.averageResponseTime,
        Performance.errorCount,
        Performance.averageThroughput
      ],
      dimensions: [
        Performance.serviceName,
        Performance.performanceCategory
      ],
      timeDimension: Performance.timestamp,
      granularity: `minute`,
      refreshKey: {
        every: `1 minute`
      },
      buildRangeStart: {
        sql: `SELECT NOW() - INTERVAL '24 hours'`
      },
      buildRangeEnd: {
        sql: `SELECT NOW()`
      }
    }
  },

  // Data source
  dataSource: `default`
});
