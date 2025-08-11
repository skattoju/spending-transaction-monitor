
import { useQuery, UseQueryResult } from '@tanstack/react-query';
import { getHealth } from '../services/health';
import { HealthSchema } from '../schemas/health';

export const useHealth = (): UseQueryResult<HealthSchema, Error> => {
  return useQuery({
    queryKey: ['health'],
    queryFn: getHealth,
  });
};
