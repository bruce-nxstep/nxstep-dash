"use client"
import type { Meta, StoryObj } from '@storybook/react';
import { Modal } from '@/components/molecules/modal';
import { Button } from '@/components/ui/button';
import { useState } from 'react';

const meta = {
    title: 'Molecules/Modal',
    component: Modal,
    parameters: { layout: 'fullscreen' },
    tags: ['autodocs'],
} satisfies Meta<typeof Modal>;
export default meta;
type Story = StoryObj<typeof meta>;

const ModalDemo = ({ size }: { size?: 'sm' | 'md' | 'lg' | 'full' }) => {
    const [open, setOpen] = useState(false);
    return (
        <div style={{ padding: 32 }}>
            <Button onClick={() => setOpen(true)}>Open {size ?? 'md'} modal</Button>
            <Modal
                open={open}
                onClose={() => setOpen(false)}
                title="Confirm action"
                size={size}
                footer={
                    <>
                        <Button variant="ghost" onClick={() => setOpen(false)}>Cancel</Button>
                        <Button onClick={() => setOpen(false)}>Confirm</Button>
                    </>
                }
            >
                <p style={{ color: 'var(--color-text-secondary)' }}>
                    Are you sure you want to proceed? This action cannot be undone.
                </p>
            </Modal>
        </div>
    );
};

export const Default: Story = { render: () => <ModalDemo /> };
export const Small: Story = { render: () => <ModalDemo size="sm" /> };
export const Large: Story = { render: () => <ModalDemo size="lg" /> };
