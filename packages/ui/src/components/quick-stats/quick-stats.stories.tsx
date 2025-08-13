import type { Meta, StoryObj } from '@storybook/react';
import { QuickStats } from './quick-stats';

const meta: Meta<typeof QuickStats> = {
  title: 'Components/QuickStats',
  component: QuickStats,
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
      { id: '1', name: 'Service 1', status: 'healthy', description: '', icon: null },
      { id: '2', name: 'Service 2', status: 'healthy', description: '', icon: null },
      { id: '3', name: 'Service 3', status: 'degraded', description: '', icon: null },
    ],
  },
};

export const Dark: Story = {
  parameters: {
    backgrounds: { default: 'dark' },
  },
  args: {
    services: [
      { id: '1', name: 'Service 1', status: 'healthy', description: '', icon: null },
      { id: '2', name: 'Service 2', status: 'healthy', description: '', icon: null },
      { id: '3', name: 'Service 3', status: 'degraded', description: '', icon: null },
    ],
  },
};