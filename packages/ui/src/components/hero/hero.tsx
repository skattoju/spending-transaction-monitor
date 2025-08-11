import { Badge } from "../atoms/badge/badge";
import { AccentGlow } from "../accent-glow/accent-glow";

export function Hero() {
  return (
    <section className="relative overflow-hidden rounded-2xl border bg-card p-6 shadow-sm sm:p-8">
      <AccentGlow />
      <div className="relative z-10 flex flex-col gap-3">
        <h1 className="text-3xl font-bold tracking-tight text-foreground sm:text-4xl">
          Welcome to spending-monitor
        </h1>
        <p className="max-w-2xl text-sm leading-6 text-muted-foreground">
          AI-powered alerts for credit card transactions
        </p>
        <div className="mt-2 flex flex-wrap items-center gap-2">
          <Badge variant="secondary">
            Dark mode ready
          </Badge>
          <Badge variant="secondary">
            Accessible
          </Badge>
          <Badge variant="secondary">
            Production-grade UI
          </Badge>
        </div>
      </div>
    </section>
  );
}