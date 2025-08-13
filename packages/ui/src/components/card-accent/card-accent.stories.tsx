import type { Meta, StoryObj } from '@storybook/react';
import { CardAccent } from './card-accent';

const meta: Meta<typeof CardAccent> = {
  title: 'Components/CardAccent',
  component: CardAccent,
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
};

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {};

export const Dark: Story = {
  parameters: {
    backgrounds: { default: 'dark' },
  },
};