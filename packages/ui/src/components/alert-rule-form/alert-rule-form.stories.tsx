import type { Meta, StoryObj } from '@storybook/react';
import { AlertRuleForm } from './alert-rule-form';

const meta = {
  title: 'Components/AlertRuleForm',
  component: AlertRuleForm,
  decorators: [
    (Story) => (
      <div className="p-8 bg-background max-w-4xl">
        <Story />
      </div>
    ),
  ],
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
} satisfies Meta<typeof AlertRuleForm>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    onSubmit: (data) => {
      console.log('Form submitted:', data);
      alert(`Rule created: ${data.rule}`);
    },
  },
};

export const Loading: Story = {
  args: {
    isSubmitting: true,
    onSubmit: (data) => {
      console.log('Form submitted:', data);
    },
  },
};

export const CustomExamples: Story = {
  args: {
    exampleRules: [
      'Alert when spending exceeds $10,000 in one day',
      'Notify me of transactions over $5,000 outside business hours',
      'Alert for more than 10 transactions in 1 hour',
    ],
    onSubmit: (data) => {
      console.log('Form submitted:', data);
      alert(`Custom rule: ${data.rule}`);
    },
  },
};

export const WithError: Story = {
  render: () => {
    const handleSubmit = (data: { rule: string }) => {
      // Simulate validation error by trying to submit an invalid rule
      console.log('Form submitted:', data);
    };

    return (
      <div className="space-y-6">
        <AlertRuleForm onSubmit={handleSubmit} />
        <div className="text-center text-sm text-muted-foreground">
          Try submitting a rule without "alert" or "when" to see validation errors
        </div>
      </div>
    );
  },
};
