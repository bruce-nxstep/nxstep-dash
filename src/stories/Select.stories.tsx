import type { Meta, StoryObj } from '@storybook/react';
import { Select } from '@/components/ui/select';

const OPTIONS = [
    { value: 'fr', label: 'France' },
    { value: 'de', label: 'Germany' },
    { value: 'gb', label: 'United Kingdom', disabled: true },
    { value: 'us', label: 'United States' },
];

const meta = {
    title: 'Atoms/Select',
    component: Select,
    parameters: { layout: 'centered' },
    tags: ['autodocs'],
} satisfies Meta<typeof Select>;
export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = { args: { options: OPTIONS, placeholder: 'Choose a country' } };
export const WithValue: Story = { args: { options: OPTIONS, defaultValue: 'fr' } };
export const Disabled: Story = { args: { options: OPTIONS, disabled: true, placeholder: 'Disabled select' } };
