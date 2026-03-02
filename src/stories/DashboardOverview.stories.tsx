import React from 'react';
import type { Meta, StoryObj } from '@storybook/react';
import { PortfolioChart } from '@/components/dashboard/PortfolioChart';
import { MetricCard } from '@/components/dashboard/MetricCard';
import { AssetAllocationRing } from '@/components/dashboard/AssetAllocationRing';
import { TransactionList } from '@/components/dashboard/TransactionList';
import { QuickTransferWidget } from '@/components/dashboard/QuickTransferWidget';
import { GoalProgressBar } from '@/components/dashboard/GoalProgressBar';

const DashboardLayout = ({ variant = "purple" }: { variant?: "purple" | "gold" }) => {
    return (
        <div className="min-h-screen text-white p-8 font-sans w-[1200px] max-w-full overflow-hidden relative" style={{ backgroundColor: "var(--color-bg-page)" }}>
            {/* Global Ambient Glow */}
            <div className={`absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[300px] opacity-10 blur-[120px] rounded-full pointer-events-none ${variant === 'purple' ? 'bg-primary' : 'bg-yellow-500'}`}></div>

            <header className="mb-10 animate-fade-in">
                <h1 className="text-4xl font-light tracking-tight text-white m-0">
                    Good morning, <span className="font-semibold text-transparent bg-clip-text bg-gradient-to-r from-gray-200 to-gray-500">Alex</span>
                </h1>
                <p className="text-gray-400 mt-2">Here is what's happening with your wealth today.</p>
            </header>

            {/* Top KPI row */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
                <MetricCard title="Total Net Worth" value="$1,450,000" trend={12.5} variant={variant} />
                <MetricCard title="Monthly Yield" value="+$14,200" trend={4.2} variant={variant} />
                <MetricCard title="Available Cash" value="$125,500" trend={-1.5} variant={variant} />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Main Chart Column (Takes up 2/3) */}
                <div className="lg:col-span-2 space-y-6">
                    <PortfolioChart variant={variant} />

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <AssetAllocationRing />
                        <GoalProgressBar variant={variant} />
                    </div>
                </div>

                {/* Sidebar Column (Takes up 1/3) */}
                <div className="space-y-6">
                    <QuickTransferWidget variant={variant} />
                    <TransactionList />
                </div>
            </div>
        </div>
    );
};

const meta = {
    title: 'Pages/DashboardOverview',
    component: DashboardLayout,
    parameters: {
        layout: 'fullscreen',
    },
    tags: ['autodocs'],
} satisfies Meta<typeof DashboardLayout>;

export default meta;
type Story = StoryObj<typeof meta>;

export const ImperialPurple: Story = {
    args: {
        variant: 'purple',
    },
};

export const LuxuryGoldTheme: Story = {
    args: {
        variant: 'gold',
    },
};
