import type { Meta, StoryObj } from '@storybook/react';
import { AssetAllocationRing } from '@/components/dashboard/AssetAllocationRing';

const meta = {
    title: 'Dashboard/AssetAllocationRing',
    component: AssetAllocationRing,
    parameters: {
        layout: 'padded',
    },
    tags: ['autodocs'],
} satisfies Meta<typeof AssetAllocationRing>;

export default meta;
type Story = StoryObj<typeof meta>;

// The animated donut chart showcasing the premium glassmorphic container and glowing interactions
export const Default: Story = {
    args: {},
};
