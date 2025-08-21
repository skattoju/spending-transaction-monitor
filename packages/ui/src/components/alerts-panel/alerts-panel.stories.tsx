import type { Meta, StoryObj } from '@storybook/react';
import { AlertsPanel } from './alerts-panel';
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
  title: 'Components/AlertsPanel',
  component: AlertsPanel,
  decorators: [
    (Story) => (
      <QueryClientProvider client={queryClient}>
        <div className="p-8 bg-background max-w-md">
          <Story />
        </div>
      </QueryClientProvider>
    ),
  ],
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
} satisfies Meta<typeof AlertsPanel>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {},
};

export const WithClickHandler: Story = {
  args: {
    onAlertClick: (alert) => {
      console.log('Alert clicked:', alert);
      window.alert(`Alert ${alert.id} clicked!`);
    },
  },
};

export const Loading: Story = {
  decorators: [
    (Story) => {
      const loadingQueryClient = new QueryClient({
        defaultOptions: {
          queries: {
            retry: false,
            refetchOnWindowFocus: false,
            queryFn: () => new Promise(() => {}),
          },
        },
      });

      return (
        <QueryClientProvider client={loadingQueryClient}>
          <div className="p-8 bg-background max-w-md">
            <Story />
          </div>
        </QueryClientProvider>
      );
    },
  ],
  args: {},
};

export const NoAlerts: Story = {
  decorators: [
    (Story) => {
      const emptyQueryClient = new QueryClient({
        defaultOptions: {
          queries: {
            retry: false,
            refetchOnWindowFocus: false,
            queryFn: () => Promise.resolve([]),
          },
        },
      });

      return (
        <QueryClientProvider client={emptyQueryClient}>
          <div className="p-8 bg-background max-w-md">
            <Story />
          </div>
        </QueryClientProvider>
      );
    },
  ],
  args: {},
};
