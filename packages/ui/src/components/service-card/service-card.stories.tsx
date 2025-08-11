import type { Meta, StoryObj } from '@storybook/react';
import { ServiceCard } from './service-card';
import { Database, Server, Globe, Lock } from 'lucide-react';

const meta: Meta<typeof ServiceCard> = {
  title: 'Components/ServiceCard',
  component: ServiceCard,
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
};

export default meta;
type Story = StoryObj<typeof meta>;

export const Healthy: Story = {
  args: {
    service: {
      name: 'Database',
      description: 'Primary database',
      icon: <Database />,
      status: 'healthy',
      region: 'us-east-1',
      lastCheck: new Date(),
    },
    isLoading: false,
  },
};

export const AllStatuses: Story = {
  render: () => (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-4xl">
      <ServiceCard
        service={{
          name: 'Database',
          description: 'Primary PostgreSQL database',
          icon: <Database />,
          status: 'healthy',
          region: 'us-east-1',
          lastCheck: new Date(),
        }}
        isLoading={false}
      />
      <ServiceCard
        service={{
          name: 'API Gateway',
          description: 'Main API endpoint',
          icon: <Server />,
          status: 'degraded',
          region: 'us-west-2',
          lastCheck: new Date(Date.now() - 60000),
        }}
        isLoading={false}
      />
      <ServiceCard
        service={{
          name: 'CDN',
          description: 'Content delivery network',
          icon: <Globe />,
          status: 'down',
          region: 'global',
          lastCheck: new Date(Date.now() - 300000),
        }}
        isLoading={false}
      />
      <ServiceCard
        service={{
          name: 'Auth Service',
          description: 'User authentication',
          icon: <Lock />,
          status: 'healthy',
          region: 'eu-west-1',
          lastCheck: new Date(Date.now() - 30000),
        }}
        isLoading={false}
      />
    </div>
  ),
};

export const Loading: Story = {
  args: {
    service: {
      name: 'Loading Service',
      description: 'Checking status...',
      icon: <Server />,
      status: 'healthy',
      region: 'us-east-1',
      lastCheck: new Date(),
    },
    isLoading: true,
  },
};