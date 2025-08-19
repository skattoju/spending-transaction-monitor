import type { Meta, StoryObj } from '@storybook/react';
import { DashboardHeader } from './dashboard-header';

const meta = {
  title: 'Components/DashboardHeader',
  component: DashboardHeader,
  decorators: [
    (Story) => (
      <div className="min-h-screen bg-background">
        <Story />
      </div>
    ),
  ],
  parameters: {
    layout: 'fullscreen',
  },
  tags: ['autodocs'],
} satisfies Meta<typeof DashboardHeader>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {},
};

export const WithMenuHandler: Story = {
  args: {
    onMenuClick: () => {
      console.log('Menu clicked');
      alert('Menu button clicked!');
    },
  },
};
