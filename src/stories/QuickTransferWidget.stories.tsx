import type { Meta, StoryObj } from '@storybook/react';
import { QuickTransferWidget } from '@/components/dashboard/QuickTransferWidget';

const meta = {
    title: 'Dashboard/QuickTransferWidget',
    component: QuickTransferWidget,
    parameters: {
        layout: 'padded',
    },
    tags: ['autodocs'],
} satisfies Meta<typeof QuickTransferWidget>;

export default meta;
type Story = StoryObj<typeof meta>;

// The quick transfer form showcasing inputs and gradients
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
