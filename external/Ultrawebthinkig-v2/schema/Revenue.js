/**
 * Revenue Cube Schema - Financial Analytics
 * EuroWeb Platform Revenue & Financial Metrics
 * 
 * @author Ledjan Ahmati
 * @version 8.0.0-CUBE-ANALYTICS
 */

cube(`Revenue`, {
  sql: `
    SELECT 
      id,
      user_id,
      transaction_date,
      amount,
      currency,
      subscription_type,
      payment_method,
      status,
      country,
      tax_amount,
      discount_amount,
      net_amount,
      recurring,
      billing_cycle,
      affiliate_id,
      campaign_id,
      refund_date,
      chargeback_date
    FROM revenue_transactions
  `,

  // Joins
  joins: {
    Users: {
      sql: `${CUBE}.user_id = ${Users}.id`,
      relationship: `belongsTo`
    }
  },

  // Dimensions
  dimensions: {
    id: {
      sql: `id`,
      type: `string`,
      primaryKey: true
    },

    userId: {
      sql: `user_id`,
      type: `string`,
      title: 'User ID'
    },

    subscriptionType: {
      sql: `subscription_type`,
      type: `string`,
      title: 'Subscription Type'
    },

    currency: {
      sql: `currency`,
      type: `string`
    },

    paymentMethod: {
      sql: `payment_method`,
      type: `string`,
      title: 'Payment Method'
    },

    status: {
      sql: `status`,
      type: `string`,
      title: 'Transaction Status'
    },

    country: {
      sql: `country`,
      type: `string`
    },

    billingCycle: {
      sql: `billing_cycle`,
      type: `string`,
      title: 'Billing Cycle'
    },

    isRecurring: {
      sql: `recurring`,
      type: `boolean`,
      title: 'Recurring Payment'
    },

    affiliateId: {
      sql: `affiliate_id`,
      type: `string`,
      title: 'Affiliate ID'
    },

    campaignId: {
      sql: `campaign_id`,
      type: `string`,
      title: 'Campaign ID'
    },

    // Time dimensions
    transactionDate: {
      sql: `transaction_date`,
      type: `time`,
      title: 'Transaction Date'
    },

    transactionMonth: {
      sql: `DATE_TRUNC('month', transaction_date)`,
      type: `time`,
      title: 'Transaction Month'
    },

    transactionQuarter: {
      sql: `DATE_TRUNC('quarter', transaction_date)`,
      type: `time`,
      title: 'Transaction Quarter'
    },

    transactionYear: {
      sql: `DATE_TRUNC('year', transaction_date)`,
      type: `time`,
      title: 'Transaction Year'
    },

    refundDate: {
      sql: `refund_date`,
      type: `time`,
      title: 'Refund Date'
    },

    // Revenue categories
    revenueCategory: {
      sql: `
        CASE 
          WHEN amount < 10 THEN 'Micro'
          WHEN amount < 50 THEN 'Small'
          WHEN amount < 200 THEN 'Medium'
          WHEN amount < 1000 THEN 'Large'
          ELSE 'Enterprise'
        END
      `,
      type: `string`,
      title: 'Revenue Category'
    },

    customerType: {
      sql: `
        CASE 
          WHEN recurring = true THEN 'Subscription'
          ELSE 'One-time'
        END
      `,
      type: `string`,
      title: 'Customer Type'
    }
  },

  // Measures
  measures: {
    count: {
      type: `count`,
      title: 'Total Transactions'
    },

    // Revenue Measures
    totalRevenue: {
      sql: `SUM(amount)`,
      type: `number`,
      title: 'Total Revenue',
      format: 'currency'
    },

    netRevenue: {
      sql: `SUM(net_amount)`,
      type: `number`,
      title: 'Net Revenue',
      format: 'currency'
    },

    averageRevenue: {
      sql: `AVG(amount)`,
      type: `number`,
      title: 'Average Transaction Value',
      format: 'currency'
    },

    medianRevenue: {
      sql: `PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY amount)`,
      type: `number`,
      title: 'Median Transaction Value',
      format: 'currency'
    },

    // Recurring Revenue
    mrr: {
      sql: `
        SUM(CASE 
          WHEN recurring = true AND billing_cycle = 'monthly' THEN amount
          WHEN recurring = true AND billing_cycle = 'yearly' THEN amount / 12
          WHEN recurring = true AND billing_cycle = 'quarterly' THEN amount / 3
          ELSE 0
        END)
      `,
      type: `number`,
      title: 'Monthly Recurring Revenue (MRR)',
      format: 'currency'
    },

    arr: {
      sql: `
        SUM(CASE 
          WHEN recurring = true AND billing_cycle = 'yearly' THEN amount
          WHEN recurring = true AND billing_cycle = 'monthly' THEN amount * 12
          WHEN recurring = true AND billing_cycle = 'quarterly' THEN amount * 4
          ELSE 0
        END)
      `,
      type: `number`,
      title: 'Annual Recurring Revenue (ARR)',
      format: 'currency'
    },

    recurringRevenue: {
      sql: `SUM(amount)`,
      type: `number`,
      title: 'Recurring Revenue',
      format: 'currency',
      filters: [
        { sql: `${CUBE}.recurring = true` }
      ]
    },

    oneTimeRevenue: {
      sql: `SUM(amount)`,
      type: `number`,
      title: 'One-time Revenue',
      format: 'currency',
      filters: [
        { sql: `${CUBE}.recurring = false` }
      ]
    },

    // Taxes and Fees
    totalTax: {
      sql: `SUM(tax_amount)`,
      type: `number`,
      title: 'Total Tax Amount',
      format: 'currency'
    },

    totalDiscounts: {
      sql: `SUM(discount_amount)`,
      type: `number`,
      title: 'Total Discounts',
      format: 'currency'
    },

    // Success Metrics
    successfulTransactions: {
      sql: `COUNT(*)`,
      type: `count`,
      title: 'Successful Transactions',
      filters: [
        { sql: `${CUBE}.status = 'completed'` }
      ]
    },

    failedTransactions: {
      sql: `COUNT(*)`,
      type: `count`,
      title: 'Failed Transactions',
      filters: [
        { sql: `${CUBE}.status IN ('failed', 'declined', 'cancelled')` }
      ]
    },

    successRate: {
      sql: `
        COUNT(CASE WHEN status = 'completed' THEN 1 END) * 100.0 / COUNT(*)
      `,
      type: `number`,
      title: 'Transaction Success Rate (%)',
      format: 'percent'
    },

    // Refunds and Chargebacks
    refundCount: {
      sql: `COUNT(*)`,
      type: `count`,
      title: 'Refund Count',
      filters: [
        { sql: `${CUBE}.refund_date IS NOT NULL` }
      ]
    },

    refundAmount: {
      sql: `SUM(amount)`,
      type: `number`,
      title: 'Refund Amount',
      format: 'currency',
      filters: [
        { sql: `${CUBE}.refund_date IS NOT NULL` }
      ]
    },

    chargebackCount: {
      sql: `COUNT(*)`,
      type: `count`,
      title: 'Chargeback Count',
      filters: [
        { sql: `${CUBE}.chargeback_date IS NOT NULL` }
      ]
    },

    refundRate: {
      sql: `
        COUNT(CASE WHEN refund_date IS NOT NULL THEN 1 END) * 100.0 / COUNT(*)
      `,
      type: `number`,
      title: 'Refund Rate (%)',
      format: 'percent'
    },

    // Customer Metrics
    uniqueCustomers: {
      sql: `user_id`,
      type: `countDistinct`,
      title: 'Unique Customers'
    },

    newCustomers: {
      sql: `user_id`,
      type: `countDistinct`,
      title: 'New Customers',
      filters: [
        { sql: `${CUBE}.transaction_date >= ${Users}.created_at AND ${CUBE}.transaction_date <= ${Users}.created_at + INTERVAL '7 days'` }
      ]
    },

    customerLifetimeValue: {
      sql: `SUM(amount) / COUNT(DISTINCT user_id)`,
      type: `number`,
      title: 'Customer Lifetime Value (CLV)',
      format: 'currency'
    },

    // Growth Metrics
    revenueGrowth: {
      sql: `
        (SUM(CASE WHEN transaction_date >= DATE_TRUNC('month', CURRENT_DATE) THEN amount ELSE 0 END) -
         SUM(CASE WHEN transaction_date >= DATE_TRUNC('month', CURRENT_DATE - INTERVAL '1 month') 
                   AND transaction_date < DATE_TRUNC('month', CURRENT_DATE) THEN amount ELSE 0 END)) * 100.0 /
        NULLIF(SUM(CASE WHEN transaction_date >= DATE_TRUNC('month', CURRENT_DATE - INTERVAL '1 month') 
                        AND transaction_date < DATE_TRUNC('month', CURRENT_DATE) THEN amount ELSE 0 END), 0)
      `,
      type: `number`,
      title: 'Monthly Revenue Growth (%)',
      format: 'percent'
    }
  },

  // Pre-aggregations
  preAggregations: {
    // Daily revenue
    dailyRevenue: {
      measures: [
        Revenue.totalRevenue,
        Revenue.netRevenue,
        Revenue.count,
        Revenue.successRate
      ],
      dimensions: [
        Revenue.subscriptionType,
        Revenue.paymentMethod,
        Revenue.country
      ],
      timeDimension: Revenue.transactionDate,
      granularity: `day`,
      refreshKey: {
        every: `1 hour`
      }
    },

    // Monthly financial summary
    monthlyFinancials: {
      measures: [
        Revenue.totalRevenue,
        Revenue.mrr,
        Revenue.arr,
        Revenue.uniqueCustomers,
        Revenue.customerLifetimeValue,
        Revenue.refundRate
      ],
      dimensions: [
        Revenue.subscriptionType,
        Revenue.country,
        Revenue.customerType
      ],
      timeDimension: Revenue.transactionDate,
      granularity: `month`,
      refreshKey: {
        every: `1 day`
      }
    },

    // Real-time revenue tracking
    realtimeRevenue: {
      measures: [
        Revenue.totalRevenue,
        Revenue.count,
        Revenue.averageRevenue
      ],
      dimensions: [
        Revenue.paymentMethod,
        Revenue.status
      ],
      timeDimension: Revenue.transactionDate,
      granularity: `hour`,
      refreshKey: {
        every: `5 minutes`
      },
      buildRangeStart: {
        sql: `SELECT NOW() - INTERVAL '7 days'`
      },
      buildRangeEnd: {
        sql: `SELECT NOW()`
      }
    }
  },

  // Data source
  dataSource: `financial`
});
