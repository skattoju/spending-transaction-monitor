import type { Meta, StoryObj } from '@storybook/react';
import { StatusPanel } from './status-panel';

const meta: Meta<typeof StatusPanel> = {
  title: 'Components/StatusPanel',
  component: StatusPanel,
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
};

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    services: [
      { name: 'Service 1', status: 'healthy', description: 'desc', icon: null },
      { name: 'Service 2', status: 'degraded', description: 'desc', icon: null },
      { name: 'Service 3', status: 'down', description: 'desc', icon: null },
    ],
    isLoading: false,
  },
};

export const Loading: Story = {
  args: {
    services: [
      { name: 'Service 1', status: 'healthy', description: 'Loading status...', icon: null },
      { name: 'Service 2', status: 'degraded', description: 'Checking health...', icon: null },
      { name: 'Service 3', status: 'down', description: 'Connecting...', icon: null },
    ],
    isLoading: true,
  },
};

export const Empty: Story = {
  args: {
    services: [],
    isLoading: false,
  },
};