import type {
  Transaction,
  TransactionStats,
  Alert,
  AlertRule,
} from '../schemas/transaction';

// Mock data generators
const generateTransactions = (count: number): Transaction[] => {
  const merchants = [
    'Amazon Web Services',
    'Stripe Payment',
    'Google Cloud',
    'Shopify',
    'Netflix',
    'Adobe Creative Suite',
    'Microsoft Azure',
    'GitHub',
    'Slack',
    'Zoom',
    'Dropbox',
    'Coffee Shop',
    'Restaurant',
    'Wire Transfer',
    'International Transfer',
    'PayPal',
  ];

  const statuses: Transaction['status'][] = [
    'completed',
    'pending',
    'flagged',
    'failed',
  ];
  const types: Transaction['type'][] = [
    'subscription',
    'payment',
    'transfer',
    'purchase',
    'refund',
  ];

  const now = Date.now();

  return Array.from({ length: count }, (_, i) => ({
    id: `TXN-${String(i + 1).padStart(4, '0')}`,
    amount: Math.random() * 5000 + 10,
    merchant: merchants[Math.floor(Math.random() * merchants.length)],
    status: statuses[Math.floor(Math.random() * statuses.length)],
    time: new Date(now - Math.random() * 86400000).toISOString(), // Random time in last 24h
    type: types[Math.floor(Math.random() * types.length)],
    currency: 'USD',
    category: ['Software', 'Cloud Services', 'Food & Dining', 'Business', 'Transfer'][
      Math.floor(Math.random() * 5)
    ],
    description: `Transaction for ${merchants[Math.floor(Math.random() * merchants.length)]}`,
  }));
};

const mockTransactions = generateTransactions(50);

// Mock service functions
export const transactionService = {
  // Get recent transactions with pagination
  async getRecentTransactions(
    page = 1,
    limit = 10,
  ): Promise<{
    transactions: Transaction[];
    total: number;
    page: number;
    totalPages: number;
  }> {
    // Simulate API delay
    await new Promise((resolve) => setTimeout(resolve, 500));

    const start = (page - 1) * limit;
    const end = start + limit;
    const transactions = mockTransactions
      .sort((a, b) => new Date(b.time).getTime() - new Date(a.time).getTime())
      .slice(start, end);

    return {
      transactions,
      total: mockTransactions.length,
      page,
      totalPages: Math.ceil(mockTransactions.length / limit),
    };
  },

  // Get transaction by ID
  async getTransactionById(id: string): Promise<Transaction | null> {
    await new Promise((resolve) => setTimeout(resolve, 300));
    return mockTransactions.find((t) => t.id === id) || null;
  },

  // Get transaction statistics
  async getTransactionStats(): Promise<TransactionStats> {
    await new Promise((resolve) => setTimeout(resolve, 400));

    const totalTransactions = mockTransactions.length;
    const totalVolume = mockTransactions.reduce((sum, t) => sum + t.amount, 0);
    const flaggedCount = mockTransactions.filter((t) => t.status === 'flagged').length;

    return {
      totalTransactions,
      totalVolume,
      activeAlerts: flaggedCount,
      avgProcessingTime: 1.2,
      previousPeriod: {
        totalTransactions: Math.floor(totalTransactions * 0.88),
        totalVolume: totalVolume * 0.92,
        activeAlerts: Math.floor(flaggedCount * 1.15),
        avgProcessingTime: 1.27,
      },
    };
  },

  // Search transactions
  async searchTransactions(query: string): Promise<Transaction[]> {
    await new Promise((resolve) => setTimeout(resolve, 400));

    const lowercaseQuery = query.toLowerCase();
    return mockTransactions.filter(
      (t) =>
        t.merchant.toLowerCase().includes(lowercaseQuery) ||
        t.id.toLowerCase().includes(lowercaseQuery) ||
        t.type.includes(lowercaseQuery) ||
        t.category?.toLowerCase().includes(lowercaseQuery),
    );
  },

  // Get chart data for transaction volume over time
  async getTransactionChartData(timeRange: '7d' | '30d' | '90d' | '1y'): Promise<
    Array<{
      date: string;
      volume: number;
      transactions: number;
      formattedDate: string;
    }>
  > {
    await new Promise((resolve) => setTimeout(resolve, 300));

    const days =
      timeRange === '7d'
        ? 7
        : timeRange === '30d'
          ? 30
          : timeRange === '90d'
            ? 90
            : 365;
    const data = [];

    for (let i = days - 1; i >= 0; i--) {
      const date = new Date();
      date.setDate(date.getDate() - i);

      // Generate realistic-looking data with some trends
      const baseVolume = 25000;
      const trend = Math.sin((i / days) * Math.PI * 2) * 5000;
      const randomVariation = (Math.random() - 0.5) * 10000;
      const volume = Math.max(5000, baseVolume + trend + randomVariation);

      const transactions = Math.floor(volume / 200) + Math.floor(Math.random() * 50);

      data.push({
        date: date.toISOString().split('T')[0],
        volume: Math.floor(volume),
        transactions,
        formattedDate: date.toLocaleDateString('en-US', {
          month: 'short',
          day: 'numeric',
        }),
      });
    }

    return data;
  },
};

// Alert service
export const alertService = {
  // Get active alerts
  async getAlerts(): Promise<Alert[]> {
    await new Promise((resolve) => setTimeout(resolve, 300));

    const alerts: Alert[] = [
      {
        id: 'ALT-001',
        title: 'Large Transaction Detected',
        description: 'Transaction of $2,500 exceeds your daily limit',
        severity: 'high',
        timestamp: new Date(Date.now() - 1800000).toISOString(),
        transactionId: 'TXN-0003',
        resolved: false,
      },
      {
        id: 'ALT-002',
        title: 'Unusual Activity Pattern',
        description: 'Multiple transactions from new location',
        severity: 'medium',
        timestamp: new Date(Date.now() - 3600000).toISOString(),
        resolved: false,
      },
      {
        id: 'ALT-003',
        title: 'Failed Transaction',
        description: 'Payment to Stripe failed due to insufficient funds',
        severity: 'low',
        timestamp: new Date(Date.now() - 7200000).toISOString(),
        resolved: true,
      },
    ];

    return alerts;
  },

  // Get alert rules
  async getAlertRules(): Promise<AlertRule[]> {
    await new Promise((resolve) => setTimeout(resolve, 300));

    const rules: AlertRule[] = [
      {
        id: 'RULE-001',
        rule: 'Alert me when transactions exceed $10,000',
        status: 'active',
        triggered: 3,
        lastTriggered: '2 hours ago',
        createdAt: new Date(Date.now() - 86400000 * 30).toISOString(),
      },
      {
        id: 'RULE-002',
        rule: 'Notify me of suspicious login attempts',
        status: 'active',
        triggered: 0,
        lastTriggered: 'Never',
        createdAt: new Date(Date.now() - 86400000 * 15).toISOString(),
      },
      {
        id: 'RULE-003',
        rule: 'Alert for transactions from new countries',
        status: 'active',
        triggered: 12,
        lastTriggered: '1 day ago',
        createdAt: new Date(Date.now() - 86400000 * 60).toISOString(),
      },
      {
        id: 'RULE-004',
        rule: 'Notify when daily spending exceeds $5,000',
        status: 'paused',
        triggered: 8,
        lastTriggered: '5 days ago',
        createdAt: new Date(Date.now() - 86400000 * 45).toISOString(),
      },
    ];

    return rules;
  },

  // Create new alert rule
  async createAlertRule(rule: string): Promise<AlertRule> {
    await new Promise((resolve) => setTimeout(resolve, 500));

    const newRule: AlertRule = {
      id: `RULE-${Date.now()}`,
      rule,
      status: 'active',
      triggered: 0,
      lastTriggered: 'Never',
      createdAt: new Date().toISOString(),
    };

    return newRule;
  },

  // Toggle alert rule status
  async toggleAlertRule(id: string): Promise<AlertRule | null> {
    await new Promise((resolve) => setTimeout(resolve, 300));

    // In a real app, this would update the database
    const rules = await alertService.getAlertRules();
    const rule = rules.find((r) => r.id === id);

    if (rule) {
      rule.status = rule.status === 'active' ? 'paused' : 'active';
      return rule;
    }

    return null;
  },
};
