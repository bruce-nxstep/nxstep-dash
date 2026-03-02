import type { Meta, StoryObj } from '@storybook/react';
import { FormField } from '@/components/molecules/form-field';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';

const meta = {
    title: 'Molecules/FormField',
    component: FormField,
    parameters: { layout: 'centered' },
    tags: ['autodocs'],
} satisfies Meta<typeof FormField>;
export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
    render: () => (
        <div style={{ width: 320 }}>
            <FormField label="Email" htmlFor="email" helper="We'll never share your email.">
                <Input id="email" type="email" placeholder="you@example.com" />
            </FormField>
        </div>
    ),
};

export const WithError: Story = {
    render: () => (
        <div style={{ width: 320 }}>
            <FormField label="Username" htmlFor="username" error="Username already taken." required>
                <Input id="username" placeholder="Choose a username" aria-invalid />
            </FormField>
        </div>
    ),
};

export const TextareaField: Story = {
    render: () => (
        <div style={{ width: 320 }}>
            <FormField label="Message" htmlFor="msg" helper="Max 500 characters." required>
                <Textarea id="msg" placeholder="Your message…" rows={4} />
            </FormField>
        </div>
    ),
};
