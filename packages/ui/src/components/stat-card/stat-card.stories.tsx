import type { Meta, StoryObj } from '@storybook/react';
import { StatCard } from './stat-card';
import { TrendingUp, Calendar, DollarSign } from 'lucide-react';
import { Button } from '../atoms/button/button';

const meta = {
  title: 'Components/StatCard',
  component: StatCard,
  decorators: [
    (Story) => (
      <div className="p-8 bg-background max-w-sm">
        <Story />
      </div>
    ),
  ],
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
} satisfies Meta<typeof StatCard>;

export default meta;
type Story = StoryObj<typeof meta>;

// Default variant stories
export const Default: Story = {
  args: {
    title: 'Total Revenue',
    value: '$1,234,567',
  },
};

export const WithTone: Story = {
  args: {
    title: 'Active Users',
    value: '12,847',
    tone: 'emerald',
  },
};

export const WithDescription: Story = {
  args: {
    title: 'Transaction Volume',
    value: '$2.4M',
    description: 'total volume processed',
    tone: 'sky',
  },
};

export const WithIcon: Story = {
  args: {
    title: 'Total Transactions',
    value: '12,847',
    description: 'transactions this period',
    icon: <DollarSign className="h-4 w-4 text-muted-foreground" />,
  },
};

export const WithAction: Story = {
  args: {
    title: 'Active Alerts',
    value: '23',
    description: 'alerts requiring attention',
    action: (
      <div className="flex items-center gap-1">
        <TrendingUp className="h-3 w-3 text-success" />
        <span className="text-xs font-medium text-success">-15.3%</span>
        <span className="text-xs text-muted-foreground">from last period</span>
      </div>
    ),
  },
};

// Compact variant stories
export const Compact: Story = {
  args: {
    title: 'Total Revenue',
    value: '$12,345',
    variant: 'compact',
  },
};

export const CompactWithIcon: Story = {
  args: {
    title: "Today's Volume",
    value: '$5,250',
    variant: 'compact',
    icon: <TrendingUp className="h-8 w-8 text-success" />,
  },
};

export const CompactWithAction: Story = {
  args: {
    title: 'Flagged',
    value: '23',
    variant: 'compact',
    action: (
      <Button variant="destructive" size="sm">
        Review
      </Button>
    ),
  },
};

// Grid examples
export const DefaultGrid: Story = {
  decorators: [
    (Story) => (
      <div className="p-8 bg-background">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Story />
          <StatCard
            title="Transaction Volume"
            value="$2.4M"
            description="total volume processed"
            tone="sky"
          />
          <StatCard
            title="Active Alerts"
            value="23"
            description="alerts requiring attention"
            tone="violet"
          />
          <StatCard
            title="Avg. Processing Time"
            value="1.2s"
            description="average transaction time"
          />
        </div>
      </div>
    ),
  ],
  args: {
    title: 'Total Transactions',
    value: '12,847',
    description: 'transactions this period',
    tone: 'emerald',
  },
};

export const CompactGrid: Story = {
  decorators: [
    (Story) => (
      <div className="p-8 bg-background">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <Story />
          <StatCard
            title="Total Transactions"
            value="1,234"
            variant="compact"
            icon={<Calendar className="h-8 w-8 text-primary" />}
          />
          <StatCard
            title="Flagged"
            value="15"
            variant="compact"
            action={
              <Button variant="destructive" size="sm">
                Review
              </Button>
            }
          />
          <StatCard
            title="Success Rate"
            value="98.5%"
            variant="compact"
            icon={<TrendingUp className="h-8 w-8 text-success" />}
          />
        </div>
      </div>
    ),
  ],
  args: {
    title: "Today's Volume",
    value: '$25,000',
    variant: 'compact',
    icon: <DollarSign className="h-8 w-8 text-success" />,
  },
};
