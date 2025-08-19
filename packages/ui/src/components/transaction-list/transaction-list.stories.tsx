import type { Meta, StoryObj } from '@storybook/react';
import { TransactionList } from './transaction-list';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
      refetchOnWindowFocus: false,
    },
  },
});

const meta = {
  title: 'Components/TransactionList',
  component: TransactionList,
  decorators: [
    (Story) => (
      <QueryClientProvider client={queryClient}>
        <div className="p-8 bg-background max-w-4xl">
          <Story />
        </div>
      </QueryClientProvider>
    ),
  ],
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
} satisfies Meta<typeof TransactionList>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {},
  parameters: {
    docs: {
      description: {
        story:
          'A clean transaction list component that displays transaction cards and pagination. Search functionality should be handled by the parent component.',
      },
    },
  },
};

export const WithClickHandler: Story = {
  args: {
    onTransactionClick: (transaction) => {
      console.log('Transaction clicked:', transaction);
      alert(`Transaction ${transaction.id} clicked!`);
    },
  },
};

export const FiveItemsPerPage: Story = {
  args: {
    itemsPerPage: 5,
  },
};

export const TwentyItemsPerPage: Story = {
  args: {
    itemsPerPage: 20,
  },
};

export const WithSearch: Story = {
  args: {
    searchQuery: 'amazon',
  },
  parameters: {
    docs: {
      description: {
        story:
          'Example showing search results when a search query is provided by the parent component.',
      },
    },
  },
};

export const Loading: Story = {
  decorators: [
    (Story) => {
      // Create a new query client that never resolves queries to show loading state
      const loadingQueryClient = new QueryClient({
        defaultOptions: {
          queries: {
            retry: false,
            refetchOnWindowFocus: false,
            queryFn: () => new Promise(() => {}), // Never resolves
          },
        },
      });

      return (
        <QueryClientProvider client={loadingQueryClient}>
          <div className="p-8 bg-background max-w-4xl">
            <Story />
          </div>
        </QueryClientProvider>
      );
    },
  ],
  args: {},
};
