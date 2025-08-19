import type { Meta, StoryObj } from '@storybook/react';
import { Label } from './label';

const meta = {
  title: 'Atoms/Label',
  component: Label,
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
} satisfies Meta<typeof Label>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    children: 'Your Name',
  },
};

export const Required: Story = {
  render: () => (
    <Label>
      Email Address <span className="text-destructive">*</span>
    </Label>
  ),
};

export const WithInput: Story = {
  render: () => (
    <div className="space-y-2">
      <Label htmlFor="example">Example Label</Label>
      <input
        id="example"
        type="text"
        placeholder="Enter value..."
        className="w-full px-3 py-2 border border-input rounded-md bg-background text-foreground"
      />
    </div>
  ),
};
