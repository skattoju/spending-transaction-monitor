import { z } from 'zod';

export const TransactionSchema = z.object({
  id: z.string(),
  amount: z.number(),
  merchant: z.string(),
  status: z.enum(['completed', 'pending', 'flagged', 'failed']),
  time: z.string(),
  type: z.enum(['subscription', 'payment', 'transfer', 'purchase', 'refund']),
  currency: z.string().default('USD'),
  category: z.string().optional(),
  description: z.string().optional(),
});

export const TransactionStatsSchema = z.object({
  totalTransactions: z.number(),
  totalVolume: z.number(),
  activeAlerts: z.number(),
  avgProcessingTime: z.number(),
  previousPeriod: z.object({
    totalTransactions: z.number(),
    totalVolume: z.number(),
    activeAlerts: z.number(),
    avgProcessingTime: z.number(),
  }),
});

export const AlertRuleSchema = z.object({
  id: z.string(),
  rule: z.string(),
  status: z.enum(['active', 'inactive', 'paused']),
  triggered: z.number(),
  lastTriggered: z.string(),
  createdAt: z.string(),
});

export const AlertSchema = z.object({
  id: z.string(),
  title: z.string(),
  description: z.string(),
  severity: z.enum(['low', 'medium', 'high', 'critical']),
  timestamp: z.string(),
  transactionId: z.string().optional(),
  resolved: z.boolean().default(false),
});

export type Transaction = z.infer<typeof TransactionSchema>;
export type TransactionStats = z.infer<typeof TransactionStatsSchema>;
export type AlertRule = z.infer<typeof AlertRuleSchema>;
export type Alert = z.infer<typeof AlertSchema>;
