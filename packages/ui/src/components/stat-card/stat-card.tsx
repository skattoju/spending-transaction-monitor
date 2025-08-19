import { ReactNode } from 'react';
import { Card } from '../atoms/card/card';
import { cn } from '../../lib/utils';

export interface StatCardProps {
  className?: string;
  title: string;
  value: string | number;
  variant?: 'default' | 'compact';
  tone?: 'emerald' | 'sky' | 'violet';
  icon?: ReactNode;
  action?: ReactNode;
  description?: string;
}

export function StatCard({
  className,
  title,
  value,
  variant = 'default',
  tone,
  icon,
  action,
  description,
}: StatCardProps) {
  const line =
    tone === 'emerald'
      ? 'from-emerald-500/0 via-emerald-500/60 to-emerald-500/0'
      : tone === 'sky'
        ? 'from-sky-500/0 via-sky-500/60 to-sky-500/0'
        : tone === 'violet'
          ? 'from-violet-500/0 via-violet-500/60 to-violet-500/0'
          : null;

  if (variant === 'compact') {
    return (
      <Card className={cn('p-4', className)}>
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-muted-foreground">{title}</p>
            <p className="text-xl font-semibold text-foreground">{value}</p>
          </div>
          {icon && !action && icon}
          {action && <div>{action}</div>}
        </div>
      </Card>
    );
  }

  // Default variant
  return (
    <Card className={cn('relative overflow-hidden', className)}>
      {line && (
        <div className={`absolute inset-x-0 top-0 h-0.5 bg-gradient-to-r ${line}`} />
      )}
      <div className="p-6">
        <div className="flex items-center justify-between mb-4">
          <p className="text-sm font-medium text-muted-foreground">{title}</p>
          {icon ? icon : <div className="h-2 w-2 rounded-full bg-muted" />}
        </div>
        <div className="space-y-1">
          <p className="text-2xl font-bold text-foreground">{value}</p>
          {description && (
            <p className="text-xs text-muted-foreground">{description}</p>
          )}
        </div>
        {action && <div className="mt-4">{action}</div>}
      </div>
    </Card>
  );
}
