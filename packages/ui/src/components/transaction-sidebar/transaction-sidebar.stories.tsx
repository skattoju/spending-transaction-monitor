import type { Meta, StoryObj } from '@storybook/react';
import { TransactionSidebar } from './transaction-sidebar';
import type { Transaction } from '../../schemas/transaction';

const mockTransaction: Transaction = {
  id: 'TXN-0042',
  amount: 1234.56,
  merchant: 'Amazon Web Services',
  status: 'completed',
  time: '2024-01-15T14:30:00.000Z',
  type: 'subscription',
  currency: 'USD',
  category: 'Cloud Services',
  description:
    'Monthly subscription for AWS hosting services including EC2, S3, and CloudFront usage.',
};

const flaggedTransaction: Transaction = {
  id: 'TXN-0043',
  amount: 2500.0,
  merchant: 'Wire Transfer',
  status: 'flagged',
  time: '2024-01-15T09:15:00.000Z',
  type: 'transfer',
  currency: 'USD',
  category: 'Transfer',
  description:
    'Large wire transfer flagged for manual review due to amount exceeding daily limit.',
};

const meta = {
  title: 'Components/TransactionSidebar',
  component: TransactionSidebar,
  decorators: [
    (Story) => (
      <div className="flex h-screen bg-background">
        <div className="flex-1 bg-muted/20 flex items-center justify-center">
          <p className="text-muted-foreground">Main content area</p>
        </div>
        <Story />
      </div>
    ),
  ],
  parameters: {
    layout: 'fullscreen',
  },
  tags: ['autodocs'],
} satisfies Meta<typeof TransactionSidebar>;

export default meta;
type Story = StoryObj<typeof meta>;

export const WithTransaction: Story = {
  args: {
    transaction: mockTransaction,
    onClose: () => console.log('Close clicked'),
  },
};

export const WithFlaggedTransaction: Story = {
  args: {
    transaction: flaggedTransaction,
    onClose: () => console.log('Close clicked'),
  },
};

export const Empty: Story = {
  args: {
    transaction: null,
  },
};
