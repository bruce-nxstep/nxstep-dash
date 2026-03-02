"use client"
import type { Meta, StoryObj } from '@storybook/react';
import { ContentToolbar } from '@/components/cms/content-toolbar';
import { toast, Toaster } from '@/components/ui/toast';
import { useState } from 'react';

const meta = {
    title: 'CMS/ContentToolbar',
    component: ContentToolbar,
    parameters: { layout: 'padded' },
    tags: ['autodocs'],
} satisfies Meta<typeof ContentToolbar>;
export default meta;
type Story = StoryObj<typeof meta>;

export const Draft: Story = {
    render: () => {
        const [status, setStatus] = useState<'draft' | 'published' | 'scheduled'>('draft');
        return (
            <>
                <Toaster />
                <ContentToolbar
                    status={status}
                    lastSaved="2 min ago"
                    onPublish={() => { setStatus('published'); toast.success('Published!', 'Your article is now live.'); }}
                    onSchedule={() => { setStatus('scheduled'); toast.info('Scheduled', 'Will publish at midnight.'); }}
                    onDelete={() => toast.error('Deleted', 'Article moved to trash.')}
                />
            </>
        );
    },
};

export const Published: Story = {
    render: () => (
        <>
            <Toaster />
            <ContentToolbar
                status="published"
                lastSaved="just now"
                onDraft={() => toast.info('Set to Draft')}
                onDelete={() => toast.error('Deleted')}
            />
        </>
    ),
};

export const Saving: Story = {
    args: { status: 'draft', saving: true },
};
