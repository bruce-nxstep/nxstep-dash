import type { Meta, StoryObj } from '@storybook/react';
import { PortfolioChart } from '@/components/dashboard/PortfolioChart';

const meta = {
    title: 'Dashboard/PortfolioChart',
    component: PortfolioChart,
    parameters: {
        layout: 'padded',
    },
    tags: ['autodocs'],
} satisfies Meta<typeof PortfolioChart>;

export default meta;
type Story = StoryObj<typeof meta>;

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
