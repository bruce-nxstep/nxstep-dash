"use client"
import type { Meta, StoryObj } from '@storybook/react';
import { TagInput } from '@/components/cms/tag-input';

const meta = {
    title: 'CMS/TagInput',
    component: TagInput,
    parameters: { layout: 'centered' },
    tags: ['autodocs'],
} satisfies Meta<typeof TagInput>;
export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
    render: () => (
        <div style={{ width: 400 }}>
            <TagInput placeholder="Add tags (Enter or comma)…" />
        </div>
    ),
};

export const WithTags: Story = {
    render: () => (
        <div style={{ width: 400 }}>
            <TagInput defaultTags={['design-system', 'react', 'typescript']} />
        </div>
    ),
};

export const MaxReached: Story = {
    render: () => (
        <div style={{ width: 400 }}>
            <TagInput defaultTags={['tag1', 'tag2', 'tag3']} maxTags={3} />
        </div>
    ),
};

export const Disabled: Story = {
    render: () => (
        <div style={{ width: 400 }}>
            <TagInput defaultTags={['nxstep', 'wealth']} disabled />
        </div>
    ),
};
