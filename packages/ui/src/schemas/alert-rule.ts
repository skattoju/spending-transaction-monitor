import { z } from 'zod';

export const CreateAlertRuleSchema = z.object({
  rule: z.string().min(1, 'Rule is required'),
});

export type CreateAlertRuleInput = z.infer<typeof CreateAlertRuleSchema>;
