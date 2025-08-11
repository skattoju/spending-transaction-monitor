import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "../atoms/card/card";
import { Badge } from "../atoms/badge/badge";
import { CircleHelp } from "lucide-react";
import { ServiceList } from "../service-list/service-list";

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

export function StatusPanel({ services, isLoading }: { services: Service[]; isLoading: boolean }) {
  const healthyCount = services.filter((s) => s.status === "healthy").length;

  if (services.length === 0) {
    return (
      <Card className="shadow-sm">
        <CardHeader>
          <CardTitle className="text-lg">Service Health</CardTitle>
          <CardDescription>
            No services configured
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <CircleHelp className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
            <p className="text-muted-foreground">
              Add packages like API or Database to see service health monitoring here.
            </p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="shadow-sm">
      <CardHeader className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <CardTitle className="text-lg">Service Health</CardTitle>
          <CardDescription>
            {isLoading ? "Checking services..." : `${healthyCount} of ${services.length} services healthy`}
          </CardDescription>
        </div>
      </CardHeader>
      <CardContent>
        <ServiceList />
      </CardContent>
    </Card>
  );
}