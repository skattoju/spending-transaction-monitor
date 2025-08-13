import type { Meta, StoryObj } from '@storybook/react';
import { AccentGlow } from './accent-glow';

const meta: Meta<typeof AccentGlow> = {
  title: 'Components/AccentGlow',
  component: AccentGlow,
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
};

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {};

export const InCard: Story = {
  render: () => (
    <div className="relative overflow-hidden rounded-lg border bg-card p-6 shadow-sm">
      <AccentGlow />
      <div className="relative z-10">
        <h3 className="text-lg font-semibold">Featured Content</h3>
        <p className="text-sm text-muted-foreground mt-1">
          This card has an accent glow effect in the background.
        </p>
      </div>
    </div>
  ),
};