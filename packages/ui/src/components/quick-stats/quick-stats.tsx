import { StatCard } from "../stat-card/stat-card";

type Service = {
  id: string;
  name: string;
  description: string;
  icon: React.ReactNode;
  status: "healthy" | "degraded" | "down" | "unknown";
  region?: string;
  endpoint?: string;
  port?: number;
  lastCheck?: Date;
  error?: string;
};

export function QuickStats({ services }: { services: Service[] }) {
  const healthyCount = services.filter(s => s.status === "healthy").length;
  const totalServices = services.length;
  const overallStatus = healthyCount === totalServices ? "Operational" : 
                       healthyCount > totalServices / 2 ? "Degraded" : "Down";
  const statusTone = healthyCount === totalServices ? "emerald" : 
                    healthyCount > totalServices / 2 ? "sky" : "violet";
  
  return (
    <section className="mt-6 grid gap-4 sm:grid-cols-3">
      <StatCard label="Overall Health" value={overallStatus} tone={statusTone} />
      <StatCard label="Services" value={`${totalServices} total`} tone="sky" />
      <StatCard label="Healthy" value={`${healthyCount}/${totalServices}`} tone="emerald" />
    </section>
  );
}