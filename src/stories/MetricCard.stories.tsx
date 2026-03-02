import type { Meta, StoryObj } from '@storybook/react';
import { MetricCard } from '@/components/dashboard/MetricCard';

const meta = {
    title: 'Dashboard/MetricCard',
    component: MetricCard,
    parameters: {
        layout: 'padded',
    },
    tags: ['autodocs'],
} satisfies Meta<typeof MetricCard>;

export default meta;
type Story = StoryObj<typeof meta>;

export const purplePositive: Story = {
    args: {
        title: 'Total Balance',
        value: '$1,450,000',
        trend: 12.5,
        variant: 'purple',
    },
};

export const GoldNegative: Story = {
    args: {
        title: 'Monthly Spending',
        value: '$24,500',
        trend: -3.2,
        variant: 'gold',
    },
};
