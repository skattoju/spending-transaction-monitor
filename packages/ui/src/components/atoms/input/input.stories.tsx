import type { Meta, StoryObj } from '@storybook/react';
import { Input } from './input';

const meta = {
  title: 'Atoms/Input',
  component: Input,
  decorators: [
    (Story) => (
      <div className="p-8 bg-background max-w-sm">
        <Story />
      </div>
    ),
  ],
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
} satisfies Meta<typeof Input>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    placeholder: 'Enter your name...',
  },
};

export const Email: Story = {
  args: {
    type: 'email',
    placeholder: 'Enter your email...',
  },
};

export const Password: Story = {
  args: {
    type: 'password',
    placeholder: 'Enter your password...',
  },
};

export const Disabled: Story = {
  args: {
    placeholder: 'Disabled input',
    disabled: true,
  },
};

export const WithValue: Story = {
  args: {
    value: 'Pre-filled value',
    placeholder: 'This has a value',
  },
};

export const Search: Story = {
  args: {
    type: 'search',
    placeholder: 'Search transactions...',
  },
};
