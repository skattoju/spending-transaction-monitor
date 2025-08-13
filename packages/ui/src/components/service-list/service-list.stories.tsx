import type { Meta, StoryObj } from '@storybook/react';
import { ServiceList } from './service-list';

const meta: Meta<typeof ServiceList> = {
  title: 'Components/ServiceList',
  component: ServiceList,
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
      { name: 'Service 1', status: 'healthy', message: 'Service is running normally', version: '1.0.0' },
      { name: 'Service 2', status: 'degraded', message: 'Service experiencing issues', version: '1.2.1' },
      { name: 'Service 3', status: 'down', message: 'Service is offline', version: '0.9.5' },
    ],
    isLoading: false,
  },
};

export const Dark: Story = {
  parameters: {
    backgrounds: { default: 'dark' },
  },
  args: {
    services: [
      { name: 'Service 1', status: 'healthy', message: 'Service is running normally', version: '1.0.0' },
      { name: 'Service 2', status: 'degraded', message: 'Service experiencing issues', version: '1.2.1' },
      { name: 'Service 3', status: 'down', message: 'Service is offline', version: '0.9.5' },
    ],
    isLoading: false,
  },
};