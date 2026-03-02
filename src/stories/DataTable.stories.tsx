import type { Meta, StoryObj } from '@storybook/react';
import { DataTable } from '@/components/molecules/data-table';
import { Badge } from '@/components/ui/badge';

const meta = {
    title: 'Molecules/DataTable',
    component: DataTable,
    parameters: { layout: 'padded' },
    tags: ['autodocs'],
} satisfies Meta<typeof DataTable>;
export default meta;
type Story = StoryObj<typeof meta>;

type Lead = { id: string; name: string; company: string; status: string; score: number };

const SAMPLE_DATA: Lead[] = Array.from({ length: 15 }, (_, i) => ({
    id: `lead-${i + 1}`,
    name: ['Jean Dupont', 'Sophie Martin', 'Luc Bernard', 'Emma Moreau', 'Noah Leroy'][i % 5],
    company: ['LVMH', 'BNP Paribas', 'Société Générale', 'AXA', 'Total'][i % 5],
    status: ['Scrapé', 'Enrichi', 'Contacté', 'Converti', 'En attente'][i % 5],
    score: Math.floor(60 + Math.random() * 40),
}));

const COLUMNS = [
    { key: 'name', header: 'Name', sortable: true },
    { key: 'company', header: 'Company', sortable: true },
    {
        key: 'status', header: 'Status', sortable: true,
        render: (row: Lead) => {
            const v = { Scrapé: 'default', Enrichi: 'primary', Contacté: 'warning', Converti: 'success', 'En attente': 'secondary' }[row.status] ?? 'default';
            return <Badge variant={v as any}>{row.status}</Badge>;
        }
    },
    {
        key: 'score', header: 'Score', sortable: true,
        render: (row: Lead) => `${row.score}%`
    },
];

export const Default: Story = {
    render: () => (
        <div style={{ background: 'var(--color-bg-app)', padding: 24, borderRadius: 16, minWidth: 640 }}>
            <DataTable columns={COLUMNS} data={SAMPLE_DATA} rowKey="id" pageSize={5} />
        </div>
    ),
};

export const Empty: Story = {
    render: () => (
        <div style={{ background: 'var(--color-bg-app)', padding: 24, borderRadius: 16, minWidth: 500 }}>
            <DataTable columns={COLUMNS} data={[]} emptyMessage="No leads found. Start scraping!" />
        </div>
    ),
};
