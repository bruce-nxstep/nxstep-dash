import type { Meta, StoryObj } from '@storybook/react';
import { Input } from '@/components/ui/input';

const meta = {
    title: 'UI/Input',
    component: Input,
    parameters: {
        layout: 'centered',
    },
    tags: ['autodocs'],
} satisfies Meta<typeof Input>;

export default meta;
type Story = StoryObj<typeof meta>;

// Basic dark mode input
export const Default: Story = {
    args: {
        type: 'text',
        placeholder: 'Enter your email...',
    },
};

export const Disabled: Story = {
    args: {
        disabled: true,
        placeholder: 'Not available',
    },
};

export const Password: Story = {
    args: {
        type: 'password',
        placeholder: 'Enter your password...',
    },
};

// Example showing minimal border/background configuration suitable for premium UI
export const DarkModeMinimal: Story = {
    args: {
        placeholder: 'Search investments...',
        className: 'bg-black/40 border-white/10 text-white placeholder:text-gray-500 focus-visible:ring-cyan-500',
    },
};
