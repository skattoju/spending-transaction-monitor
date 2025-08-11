
import { HealthSchema } from '../schemas/health';

export const getHealth = async (): Promise<HealthSchema> => {
  const response = await fetch('/api/health/');
  if (!response.ok) {
    throw new Error('Failed to fetch health');
  }
  const data = await response.json();
  return HealthSchema.parse(data);
};
