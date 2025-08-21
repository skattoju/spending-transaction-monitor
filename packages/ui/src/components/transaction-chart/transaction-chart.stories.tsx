import type { Meta, StoryObj } from '@storybook/react';
import { TransactionChart } from './transaction-chart';

const meta = {
  title: 'Components/TransactionChart',
  component: TransactionChart,
  decorators: [
    (Story) => (
      <div className="p-8 bg-background max-w-6xl">
        <Story />
      </div>
    ),
  ],
  parameters: {
    layout: 'centered',
    docs: {
      description: {
        component:
          'Interactive transaction volume chart built with Recharts. Features time range selection, summary statistics, and responsive design.',
      },
    },
  },
  tags: ['autodocs'],
} satisfies Meta<typeof TransactionChart>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {},
  parameters: {
    docs: {
      description: {
        story:
          'Default chart showing transaction volume over the last 7 days with interactive tooltips and time range selection.',
      },
    },
  },
};

export const WithCustomClass: Story = {
  args: {
    className: 'shadow-lg border-2',
  },
  parameters: {
    docs: {
      description: {
        story: 'Chart with custom styling applied via className prop.',
      },
    },
  },
};
