import type { Meta, StoryObj } from '@storybook/react';
import { Sidebar } from '@/components/organisms/sidebar';
import { LayoutDashboard, Users, FileText, Settings, BarChart2 } from 'lucide-react';
import { Avatar } from '@/components/ui/avatar';

const SECTIONS = [
    {
        title: 'Main',
        items: [
            { icon: <LayoutDashboard />, label: 'Dashboard', href: '#', active: true },
            { icon: <Users />, label: 'Leads', href: '#', badge: 12 },
            { icon: <BarChart2 />, label: 'Analytics', href: '#' },
        ],
    },
    {
        title: 'CMS',
        items: [
            { icon: <FileText />, label: 'Articles', href: '#' },
            { icon: <Settings />, label: 'Settings', href: '#' },
        ],
    },
];

const USER_SLOT = (
    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        <Avatar initials="JL" size="sm" />
        <span style={{ fontSize: 13, color: 'var(--color-text-secondary)' }}>Jean-Luc</span>
    </div>
);

const meta = {
    title: 'Organisms/Sidebar',
    component: Sidebar,
    parameters: { layout: 'fullscreen' },
    tags: ['autodocs'],
} satisfies Meta<typeof Sidebar>;
export default meta;
type Story = StoryObj<typeof meta>;

export const Expanded: Story = {
    render: () => (
        <div style={{ display: 'flex', height: '100vh', background: 'var(--color-bg-app)' }}>
            <Sidebar sections={SECTIONS} bottomSlot={USER_SLOT} defaultCollapsed={false} />
        </div>
    ),
};

export const Collapsed: Story = {
    render: () => (
        <div style={{ display: 'flex', height: '100vh', background: 'var(--color-bg-app)' }}>
            <Sidebar sections={SECTIONS} bottomSlot={USER_SLOT} defaultCollapsed={true} />
        </div>
    ),
};
