"use client"
import type { Meta, StoryObj } from '@storybook/react';
import { SearchInput } from '@/components/molecules/search-input';
import { useState } from 'react';

const meta = {
    title: 'Molecules/SearchInput',
    component: SearchInput,
    parameters: { layout: 'centered' },
    tags: ['autodocs'],
} satisfies Meta<typeof SearchInput>;
export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
    render: () => {
        const [val, setVal] = useState('');
        return (
            <div style={{ width: 320 }}>
                <SearchInput
                    value={val}
                    onChange={e => setVal(e.target.value)}
                    onClear={() => setVal('')}
                    placeholder="Search leads…"
                />
            </div>
        );
    },
};

export const Loading: Story = {
    args: { placeholder: 'Searching…', loading: true, value: 'nxstep' },
};

export const Disabled: Story = {
    args: { placeholder: 'Disabled search', disabled: true },
};
