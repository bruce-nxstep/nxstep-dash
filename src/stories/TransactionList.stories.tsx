import type { Meta, StoryObj } from '@storybook/react';
import { TransactionList } from '@/components/dashboard/TransactionList';

const meta = {
    title: 'Dashboard/TransactionList',
    component: TransactionList,
    parameters: {
        layout: 'padded',
    },
    tags: ['autodocs'],
} satisfies Meta<typeof TransactionList>;

export default meta;
type Story = StoryObj<typeof meta>;

// Premium dark mode ledger list
export const Default: Story = {
    args: {},
};
