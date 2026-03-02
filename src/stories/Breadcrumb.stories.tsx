import type { Meta, StoryObj } from '@storybook/react';
import { Breadcrumb } from '@/components/molecules/breadcrumb';

const meta = {
    title: 'Molecules/Breadcrumb',
    component: Breadcrumb,
    parameters: { layout: 'centered' },
    tags: ['autodocs'],
} satisfies Meta<typeof Breadcrumb>;
export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
    args: {
        items: [
            { label: 'Home', href: '/' },
            { label: 'Design System', href: '/design' },
            { label: 'Breadcrumb' },
        ],
    },
};

export const TwoLevels: Story = {
    args: {
        items: [
            { label: 'Dashboard', href: '/' },
            { label: 'Settings' },
        ],
    },
};

export const NoHomeIcon: Story = {
    args: {
        homeIcon: false,
        items: [
            { label: 'Products', href: '/products' },
            { label: 'Wealth Tools', href: '/products/wealth' },
            { label: 'Asset Allocation' },
        ],
    },
};
