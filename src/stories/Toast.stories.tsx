"use client"
import type { Meta, StoryObj } from '@storybook/react';
import { toast, Toaster } from '@/components/ui/toast';
import { Button } from '@/components/ui/button';

const meta = {
    title: 'Feedback/Toast',
    parameters: { layout: 'centered' },
} satisfies Meta;
export default meta;
type Story = StoryObj;

export const AllVariants: Story = {
    render: () => (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            <Toaster />
            <Button onClick={() => toast.success('Saved!', 'Your article has been saved successfully.')}>
                ✅ Success toast
            </Button>
            <Button variant="destructive" onClick={() => toast.error('Error', 'Failed to delete. Please try again.')}>
                ❌ Error toast
            </Button>
            <Button variant="outline" onClick={() => toast.warning('Warning', 'This will overwrite existing data.')}>
                ⚠️ Warning toast
            </Button>
            <Button variant="secondary" onClick={() => toast.info('FYI', 'Your session expires in 10 minutes.')}>
                ℹ️ Info toast
            </Button>
            <Button variant="ghost" onClick={() => toast.success('Sticky!', 'This will not auto-dismiss.', 0)}>
                📌 Sticky (no auto-dismiss)
            </Button>
        </div>
    ),
};
