import type { Meta, StoryObj } from '@storybook/react';
import { Navbar } from '@/components/organisms/navbar';
import { Button } from '@/components/ui/button';
import { Avatar } from '@/components/ui/avatar';

const meta = {
    title: 'Organisms/Navbar',
    component: Navbar,
    parameters: { layout: 'fullscreen' },
    tags: ['autodocs'],
} satisfies Meta<typeof Navbar>;
export default meta;
type Story = StoryObj<typeof meta>;

const LINKS = [
    { label: 'Dashboard', href: '#', active: true },
    { label: 'Prospecting', href: '#' },
    { label: 'Kanban', href: '#' },
    { label: 'Design System', href: '#' },
];

export const Default: Story = {
    args: {
        links: LINKS,
        cta: <Button size="sm">Get started</Button>,
        userSlot: <Avatar initials="JL" size="sm" />,
    },
};

export const NoUser: Story = {
    args: {
        links: LINKS,
        cta: <Button size="sm">Sign in</Button>,
    },
};

export const MinimalLogo: Story = {
    args: {
        logo: <span style={{ color: 'var(--color-primary)', fontWeight: 700 }}>◆ NXSTEP</span>,
        links: LINKS,
    },
};
