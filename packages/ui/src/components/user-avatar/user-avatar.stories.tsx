import type { Meta, StoryObj } from '@storybook/react';
import { UserAvatar } from './user-avatar';

const meta = {
  title: 'Components/UserAvatar',
  component: UserAvatar,
  decorators: [
    (Story) => (
      <div className="p-8 bg-background">
        <Story />
      </div>
    ),
  ],
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
} satisfies Meta<typeof UserAvatar>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {},
};

export const WithAvatar: Story = {
  args: {
    userName: 'Sarah Johnson',
    userEmail: 'sarah@transactionguard.com',
    avatarUrl: 'https://github.com/shadcn.png',
  },
};

export const LongName: Story = {
  args: {
    userName: 'Christopher Alexander Thompson',
    userEmail: 'christopher.alexander.thompson@very-long-domain-name.com',
  },
};

export const WithHandlers: Story = {
  args: {
    userName: 'Alex Smith',
    userEmail: 'alex@example.com',
    onSettingsClick: () => {
      console.log('Settings clicked');
      alert('Settings clicked!');
    },
    onLogoutClick: () => {
      console.log('Logout clicked');
      alert('Logout clicked!');
    },
  },
};

export const CustomClass: Story = {
  args: {
    className: 'ring-2 ring-primary ring-offset-2',
    userName: 'Demo User',
    userEmail: 'demo@example.com',
  },
};
