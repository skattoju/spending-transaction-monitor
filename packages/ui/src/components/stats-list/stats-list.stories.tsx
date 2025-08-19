import type { Meta, StoryObj } from '@storybook/react';
import { StatsList } from './stats-list';
import {
  TrendingUp,
  Calendar,
  AlertTriangle,
  Download,
  DollarSign,
  Server,
  Database,
  Users,
} from 'lucide-react';
import { Button } from '../atoms/button/button';

const meta = {
  title: 'Components/StatsList',
  component: StatsList,
  decorators: [
    (Story) => (
      <div className="p-8 bg-background max-w-6xl">
        <Story />
      </div>
    ),
  ],
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
} satisfies Meta<typeof StatsList>;

export default meta;
type Story = StoryObj<typeof meta>;

const defaultStats = [
  {
    id: '1',
    title: 'Overall Health',
    value: 'Operational',
    tone: 'emerald' as const,
  },
  {
    id: '2',
    title: 'Services',
    value: '2 total',
    tone: 'sky' as const,
  },
  {
    id: '3',
    title: 'Healthy',
    value: '2/2',
    tone: 'emerald' as const,
  },
];

const compactStats = [
  {
    id: '1',
    title: "Today's Volume",
    value: '$25,000',
    icon: <TrendingUp className="h-8 w-8 text-success" />,
  },
  {
    id: '2',
    title: 'Total Transactions',
    value: '1,234',
    icon: <Calendar className="h-8 w-8 text-primary" />,
  },
  {
    id: '3',
    title: 'Flagged',
    value: '15',
    action: (
      <Button variant="destructive" size="sm">
        Review
      </Button>
    ),
  },
  {
    id: '4',
    title: 'Success Rate',
    value: '98.5%',
    icon: <TrendingUp className="h-8 w-8 text-success" />,
  },
];

const detailedStats = [
  {
    id: '1',
    title: 'Total Transactions',
    value: '12,847',
    description: 'transactions this period',
    icon: <DollarSign className="h-4 w-4 text-muted-foreground" />,
  },
  {
    id: '2',
    title: 'Transaction Volume',
    value: '$2.4M',
    description: 'total volume processed',
    icon: <TrendingUp className="h-4 w-4 text-muted-foreground" />,
  },
  {
    id: '3',
    title: 'Active Alerts',
    value: '23',
    description: 'alerts requiring attention',
    icon: <AlertTriangle className="h-4 w-4 text-muted-foreground" />,
  },
  {
    id: '4',
    title: 'Avg. Processing Time',
    value: '1.2s',
    description: 'average transaction time',
    icon: <Download className="h-4 w-4 text-muted-foreground" />,
  },
];

export const Default: Story = {
  args: {
    stats: defaultStats,
    columns: 3,
  },
};

export const DefaultWithTones: Story = {
  args: {
    stats: defaultStats,
    variant: 'default',
    columns: 3,
  },
};

export const Compact: Story = {
  args: {
    stats: compactStats,
    variant: 'compact',
    columns: 4,
  },
};

export const Detailed: Story = {
  args: {
    stats: detailedStats,
    variant: 'default',
    columns: 4,
  },
};

export const TwoColumns: Story = {
  args: {
    stats: compactStats.slice(0, 2),
    variant: 'compact',
    columns: 2,
  },
};

export const FiveColumns: Story = {
  args: {
    stats: [
      ...compactStats,
      {
        id: '5',
        title: 'Active Users',
        value: '1,205',
        icon: <Users className="h-8 w-8 text-info" />,
      },
    ],
    variant: 'compact',
    columns: 5,
  },
};

export const MixedContent: Story = {
  args: {
    stats: [
      {
        id: '1',
        title: 'API Status',
        value: 'Online',
        tone: 'emerald',
        icon: <Server className="h-8 w-8 text-success" />,
      },
      {
        id: '2',
        title: 'Database',
        value: 'Connected',
        tone: 'sky',
        icon: <Database className="h-8 w-8 text-info" />,
      },
      {
        id: '3',
        title: 'Critical Issues',
        value: '2',
        action: (
          <Button variant="destructive" size="sm">
            Fix Now
          </Button>
        ),
      },
    ],
    variant: 'compact',
    columns: 3,
  },
};
