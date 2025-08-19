import { useQuery, UseQueryResult } from '@tanstack/react-query';
import { getHealth } from '../services/health';
import { Health } from '../schemas/health';

export const useHealth = (): UseQueryResult<Health, Error> => {
  return useQuery({
    queryKey: ['health'],
    queryFn: getHealth,
  });
};
