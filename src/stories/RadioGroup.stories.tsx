import type { Meta, StoryObj } from '@storybook/react';
import { RadioGroup } from '@/components/ui/radio-group';

const OPTIONS = [
    { value: 'option-a', label: 'Option A', description: 'The first choice' },
    { value: 'option-b', label: 'Option B', description: 'The second choice' },
    { value: 'option-c', label: 'Option C', description: 'Disabled', disabled: true },
];

const meta = {
    title: 'Atoms/RadioGroup',
    component: RadioGroup,
    parameters: { layout: 'centered' },
    tags: ['autodocs'],
} satisfies Meta<typeof RadioGroup>;
export default meta;
type Story = StoryObj<typeof meta>;

export const Vertical: Story = { args: { options: OPTIONS, defaultValue: 'option-a' } };
export const Horizontal: Story = { args: { options: OPTIONS, orientation: 'horizontal', defaultValue: 'option-b' } };
export const WithDisabled: Story = { args: { options: OPTIONS, defaultValue: 'option-a' } };
