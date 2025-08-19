import type { Meta, StoryObj } from '@storybook/react';
import { useForm } from '@tanstack/react-form';
import { z } from 'zod';
import {
  Form,
  FormControl,
  FormDescription,
  FormItem,
  FormLabel,
  FormMessage,
} from './form';
import { Input } from '../input/input';
import { Button } from '../button/button';

const ExampleSchema = z.object({
  email: z.string().email('Please enter a valid email address'),
  name: z.string().min(2, 'Name must be at least 2 characters'),
});

const meta = {
  title: 'Atoms/Form',
  component: Form,
  decorators: [
    (Story) => (
      <div className="p-8 bg-background max-w-md">
        <Story />
      </div>
    ),
  ],
  parameters: {
    layout: 'centered',
    docs: {
      description: {
        component:
          'Form components built for TanStack Form with proper validation and accessibility.',
      },
    },
  },
  tags: ['autodocs'],
} satisfies Meta<typeof Form>;

export default meta;
type Story = StoryObj<typeof meta>;

function FormExampleDemo() {
  const form = useForm({
    defaultValues: {
      name: '',
      email: '',
    },
    onSubmit: async ({ value }) => {
      console.log('Form submitted:', value);
      alert(`Submitted: ${JSON.stringify(value, null, 2)}`);
    },
    validators: {
      onChange: ExampleSchema,
    },
  });

  return (
    <Form
      onSubmit={(e) => {
        e.preventDefault();
        e.stopPropagation();
        form.handleSubmit();
      }}
    >
      <form.Field name="name">
        {(field) => (
          <FormItem>
            <FormLabel htmlFor={field.name}>Name</FormLabel>
            <FormControl>
              <Input
                id={field.name}
                name={field.name}
                value={field.state.value}
                onBlur={field.handleBlur}
                onChange={(e) => field.handleChange(e.target.value)}
                placeholder="Enter your name"
              />
            </FormControl>
            <FormDescription>This is your public display name.</FormDescription>
            {field.state.meta.errors.length > 0 && (
              <FormMessage>{field.state.meta.errors[0]?.toString()}</FormMessage>
            )}
          </FormItem>
        )}
      </form.Field>

      <form.Field name="email">
        {(field) => (
          <FormItem>
            <FormLabel htmlFor={field.name}>Email</FormLabel>
            <FormControl>
              <Input
                id={field.name}
                name={field.name}
                type="email"
                value={field.state.value}
                onBlur={field.handleBlur}
                onChange={(e) => field.handleChange(e.target.value)}
                placeholder="Enter your email"
              />
            </FormControl>
            {field.state.meta.errors.length > 0 && (
              <FormMessage>{field.state.meta.errors[0]?.toString()}</FormMessage>
            )}
          </FormItem>
        )}
      </form.Field>

      <Button type="submit" className="w-full">
        Submit
      </Button>
    </Form>
  );
}

export const Example: Story = {
  render: () => <FormExampleDemo />,
};
