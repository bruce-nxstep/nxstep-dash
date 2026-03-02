"use client"
import type { Meta, StoryObj } from '@storybook/react';
import { Sidebar } from '@/components/organisms/sidebar';
import { Topbar } from '@/components/organisms/topbar';
import { KpiCard } from '@/components/dashboard/kpi-card';
import { ActivityWidget } from '@/components/dashboard/activity-widget';
import { DataTable } from '@/components/molecules/data-table';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Breadcrumb } from '@/components/molecules/breadcrumb';
import { Toaster, toast } from '@/components/ui/toast';
import {
    LayoutDashboard, Users, FileText, Settings, BarChart2,
    DollarSign, TrendingUp, ShoppingCart,
} from 'lucide-react';
import { Avatar } from '@/components/ui/avatar';

const meta = {
    title: 'Dashboard/DashboardFull',
    parameters: { layout: 'fullscreen' },
} satisfies Meta;
export default meta;
type Story = StoryObj;

// ── Sample data ──────────────────────────────────────────────────────────────
const SIDEBAR_SECTIONS = [
    {
        title: 'Main',
        items: [
            { icon: <LayoutDashboard className="h-4 w-4" />, label: 'Dashboard', href: '#', active: true },
            { icon: <Users className="h-4 w-4" />, label: 'Leads', href: '#', badge: 12 },
            { icon: <BarChart2 className="h-4 w-4" />, label: 'Analytics', href: '#' },
        ],
    },
    {
        title: 'CMS',
        items: [
            { icon: <FileText className="h-4 w-4" />, label: 'Articles', href: '#' },
            { icon: <Settings className="h-4 w-4" />, label: 'Settings', href: '#' },
        ],
    },
];

const SPARKLINE = [42, 38, 55, 47, 60, 58, 70, 65, 80, 75, 90, 88];

type Lead = { id: string; name: string; company: string; status: string; score: number };
const TABLE_DATA: Lead[] = [
    { id: '1', name: 'Jean Dupont', company: 'LVMH', status: 'Enrichi', score: 92 },
    { id: '2', name: 'Sophie Martin', company: 'BNP Paribas', status: 'Contacté', score: 78 },
    { id: '3', name: 'Luc Bernard', company: 'AXA', status: 'Converti', score: 95 },
    { id: '4', name: 'Emma Moreau', company: 'Total', status: 'Scrapé', score: 61 },
    { id: '5', name: 'Noah Leroy', company: 'Société Générale', status: 'En attente', score: 45 },
];
const COLUMNS = [
    { key: 'name', header: 'Name', sortable: true },
    { key: 'company', header: 'Company', sortable: true },
    {
        key: 'status', header: 'Status', sortable: true,
        render: (r: Lead) => {
            const v = ({ Scrapé: 'default', Enrichi: 'primary', Contacté: 'warning', Converti: 'success', 'En attente': 'secondary' } as Record<string, any>)[r.status] ?? 'default';
            return <Badge variant={v}>{r.status}</Badge>;
        }
    },
    { key: 'score', header: 'Score', sortable: true, render: (r: Lead) => `${r.score}%` },
];

const ACTIVITY = [
    { id: '1', title: 'Lead Sophie Martin enriched', timestamp: '2m ago', variant: 'success' as const },
    { id: '2', title: 'Email sent to LVMH', description: 'Outreach campaign #4', timestamp: '15m ago', variant: 'default' as const },
    { id: '3', title: 'Article published: Design System', timestamp: '1h ago', variant: 'success' as const },
    { id: '4', title: 'Failed to scrape AXA', description: 'HTTP 403', timestamp: '2h ago', variant: 'danger' as const },
    { id: '5', title: 'New lead imported from CSV', timestamp: '3h ago', variant: 'default' as const },
];

// ── Story ────────────────────────────────────────────────────────────────────
export const Default: Story = {
    render: () => (
        <div style={{ display: 'flex', height: '100vh', background: 'var(--color-bg-app)', overflow: 'hidden' }}>
            <Toaster />

            {/* Sidebar */}
            <Sidebar
                sections={SIDEBAR_SECTIONS}
                bottomSlot={
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <Avatar initials="JL" size="sm" />
                        <span style={{ fontSize: 13, color: 'var(--color-text-secondary)' }}>Jean-Luc</span>
                    </div>
                }
            />

            {/* Main area */}
            <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
                {/* Topbar */}
                <Topbar
                    user={{ name: 'Jean-Luc', initials: 'JL', email: 'jl@nxstep.fr' }}
                    notificationCount={3}
                    breadcrumbSlot={
                        <Breadcrumb items={[
                            { label: 'Home', href: '#' },
                            { label: 'Dashboard' },
                        ]} />
                    }
                    actionsSlot={
                        <Button size="sm" onClick={() => toast.success('Scraped!', '12 new leads found.')}>
                            + Scrape leads
                        </Button>
                    }
                />

                {/* Content */}
                <main style={{ flex: 1, overflowY: 'auto', padding: 24, display: 'flex', flexDirection: 'column', gap: 24 }}>
                    {/* KPI row */}
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 16 }}>
                        <KpiCard label="Monthly Revenue" value="24,500" unit="€" trend="up" trendValue="+12.4%" sparkline={SPARKLINE} icon={<DollarSign className="h-4 w-4" />} />
                        <KpiCard label="Active Leads" value="1,284" trend="up" trendValue="+5.2%" sparkline={[30, 45, 35, 50, 60]} icon={<Users className="h-4 w-4" />} />
                        <KpiCard label="Conversion" value="3.2" unit="%" trend="down" trendValue="-0.8%" sparkline={[5, 4.8, 4.2, 3.9, 3.5, 3.2]} icon={<TrendingUp className="h-4 w-4" />} />
                        <KpiCard label="Avg. Order" value="128" unit="€" trend="neutral" trendValue="0%" sparkline={[120, 125, 122, 128, 126]} icon={<ShoppingCart className="h-4 w-4" />} />
                    </div>

                    {/* Table + Activity */}
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 320px', gap: 16, alignItems: 'start' }}>
                        <div style={{ background: 'var(--color-bg-card)', borderRadius: 'var(--radius-xl)', padding: 20, border: '1px solid var(--color-border)' }}>
                            <h2 style={{ fontSize: 14, fontWeight: 600, color: 'var(--color-text-primary)', marginBottom: 16 }}>Recent Leads</h2>
                            <DataTable columns={COLUMNS} data={TABLE_DATA} rowKey="id" pageSize={5} />
                        </div>
                        <ActivityWidget items={ACTIVITY} />
                    </div>
                </main>
            </div>
        </div>
    ),
};
