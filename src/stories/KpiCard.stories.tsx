import type { Meta, StoryObj } from '@storybook/react';
import { KpiCard } from '@/components/dashboard/kpi-card';
import { DollarSign, Users, TrendingUp, ShoppingCart } from 'lucide-react';

const SPARKLINE = [42, 38, 55, 47, 60, 58, 70, 65, 80, 75, 90, 88];

const meta = {
    title: 'Dashboard/KpiCard',
    component: KpiCard,
    parameters: { layout: 'centered' },
    tags: ['autodocs'],
} satisfies Meta<typeof KpiCard>;
export default meta;
type Story = StoryObj<typeof meta>;

export const Revenue: Story = {
    args: {
        label: 'Monthly Revenue',
        value: '24,500',
        unit: '€',
        trend: 'up',
        trendValue: '+12.4%',
        trendLabel: 'vs last month',
        sparkline: SPARKLINE,
        icon: <DollarSign className="h-4 w-4" />,
    },
};

export const Users_: Story = {
    name: 'Users',
    args: {
        label: 'Active Users',
        value: '1,284',
        trend: 'up',
        trendValue: '+5.2%',
        sparkline: [30, 45, 35, 50, 40, 60, 55, 70],
        icon: <Users className="h-4 w-4" />,
    },
};

export const Conversion: Story = {
    args: {
        label: 'Conversion Rate',
        value: '3.2',
        unit: '%',
        trend: 'down',
        trendValue: '-0.8%',
        trendLabel: 'vs last week',
        sparkline: [5, 4.8, 4.2, 3.9, 3.5, 3.2],
        icon: <TrendingUp className="h-4 w-4" />,
    },
};

export const Neutral: Story = {
    args: {
        label: 'Avg. Order Value',
        value: '128',
        unit: '€',
        trend: 'neutral',
        trendValue: '0%',
        sparkline: [120, 125, 122, 128, 126, 128],
        icon: <ShoppingCart className="h-4 w-4" />,
    },
};

export const AllVariants: Story = {
    render: () => (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 280px)', gap: 16 }}>
            <KpiCard label="Revenue" value="24,500" unit="€" trend="up" trendValue="+12.4%" sparkline={SPARKLINE} />
            <KpiCard label="Users" value="1,284" trend="up" trendValue="+5%" sparkline={[30, 45, 35, 50, 60]} />
            <KpiCard label="Conversion" value="3.2" unit="%" trend="down" trendValue="-0.8%" sparkline={[5, 4, 3.5, 3.2]} />
            <KpiCard label="Orders" value="892" trend="neutral" trendValue="0%" sparkline={[88, 90, 88, 89, 92]} />
        </div>
    ),
};
