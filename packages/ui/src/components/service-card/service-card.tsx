import { Badge } from "../atoms/badge/badge";
import { Separator } from "../atoms/separator/separator";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "../atoms/tooltip/tooltip";
import { CardAccent } from "../card-accent/card-accent";
import {
  CheckCircle2,
  CircleHelp,
  AlertTriangle,
} from "lucide-react";
import type { Service } from "../../schemas/health";
import { getUptime, formatTime } from "../../lib/utils";
import { useState, useEffect } from "react";

const STATUS_META: Record<
  Service["status"],
  { label: string; color: string; dot: string; icon: React.ReactNode }
> = {
  healthy: {
    label: "Healthy",
    color:
      "bg-emerald-100 text-emerald-700 dark:bg-emerald-950/40 dark:text-emerald-300",
    dot: "bg-emerald-500",
    icon: <CheckCircle2 className="h-4 w-4 text-emerald-500" />,
  },
  degraded: {
    label: "Degraded",
    color:
      "bg-amber-100 text-amber-700 dark:bg-amber-950/40 dark:text-amber-300",
    dot: "bg-amber-500",
    icon: <AlertTriangle className="h-4 w-4 text-amber-500" />,
  },
  down: {
    label: "Down",
    color:
      "bg-rose-100 text-rose-700 dark:bg-rose-950/40 dark:text-rose-300",
    dot: "bg-rose-500",
    icon: <AlertTriangle className="h-4 w-4 text-rose-500" />,
  },
  unknown: {
    label: "Unknown",
    color:
      "bg-slate-100 text-slate-700 dark:bg-slate-900/60 dark:text-slate-300",
    dot: "bg-slate-400",
    icon: <CircleHelp className="h-4 w-4 text-slate-400" />,
  },
};

export function ServiceCard({ 
  service, 
  isLoading, 
  error 
}: { 
  service: Service; 
  isLoading: boolean;
  error?: Error | null;
}) {
  const meta = STATUS_META[service.status];
  const [uptime, setUptime] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setUptime(getUptime(new Date(service.start_time)));
    }, 1000);
    return () => clearInterval(interval);
  }, [service.start_time]);

  const uptimeString = formatTime(uptime);

  return (
    <div className="group relative overflow-hidden rounded-xl border bg-card p-4 transition-all duration-300 hover:-translate-y-0.5 hover:shadow-md">
      <CardAccent />
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-3">
          <div className="grid h-10 w-10 place-items-center rounded-lg bg-muted ring-1 ring-border">
            {isLoading ? (
              <div className="animate-spin h-5 w-5 border-2 border-primary border-t-transparent rounded-full" />
            ) : (
              STATUS_META[service.status].icon
            )}
          </div>
          <div className="flex flex-col">
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium text-foreground">
                {service.name}
              </span>
              <span className="rounded-md text-sm bg-muted px-1.5 py-0.5">
                v{service.version}
              </span>
              {isLoading ? (
                <span className="inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[10px] font-medium bg-muted text-muted-foreground">
                  <div className="h-1.5 w-1.5 rounded-full bg-muted-foreground animate-pulse"></div>
                  Checking...
                </span>
              ) : (
                <span
                  className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[10px] font-medium ${meta.color}`}
                >
                  <span
                    className={`h-1.5 w-1.5 rounded-full ${meta.dot}`}
                  ></span>
                  {meta.label}
                </span>
              )}
            </div>
            <span className="text-xs text-muted-foreground">
              {service.message}
            </span>
            {error && !isLoading && (
              <span className="text-xs text-destructive mt-1">
                {error.message}
              </span>
            )}
            <span className="text-xs text-muted-foreground">
              {uptimeString}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}