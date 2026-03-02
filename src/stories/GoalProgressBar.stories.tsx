import type { Meta, StoryObj } from '@storybook/react';
import { GoalProgressBar } from '@/components/dashboard/GoalProgressBar';

const meta = {
    title: 'Dashboard/GoalProgressBar',
    component: GoalProgressBar,
    parameters: {
        layout: 'padded',
    },
    tags: ['autodocs'],
} satisfies Meta<typeof GoalProgressBar>;

export default meta;
type Story = StoryObj<typeof meta>;

// The financial goals tracking component with animations
export const purpleVariant: Story = {
    args: {
        variant: 'purple',
    },
};

export const GoldVariant: Story = {
    args: {
        variant: 'gold',
    },
};
