import type { Meta, StoryObj } from '@storybook/react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

const meta = {
    title: 'UI/Card',
    component: Card,
    parameters: {
        layout: 'centered',
    },
    tags: ['autodocs'],
} satisfies Meta<typeof Card>;

export default meta;
type Story = StoryObj<typeof meta>;

// Basic Card structure
export const Default: Story = {
    render: () => (
        <Card className="w-[350px]">
            <CardHeader>
                <CardTitle>Portfolio Performance</CardTitle>
                <CardDescription>Metrics over the last 30 days.</CardDescription>
            </CardHeader>
            <CardContent>
                <p className="text-3xl font-bold tracking-tight">$12,450.00</p>
                <p className="text-sm text-green-500 mt-2">+12.5% vs last month</p>
            </CardContent>
            <CardFooter className="flex justify-between">
                <Button variant="outline">Deposit</Button>
                <Button>Invest Now</Button>
            </CardFooter>
        </Card>
    ),
};

// Premium Floating Card Example
export const PremiumDark: Story = {
    render: () => (
        <Card className="w-[400px] border-none bg-black/40 backdrop-blur-xl shadow-2xl shadow-cyan-900/20 text-white">
            <CardHeader>
                <CardTitle className="tracking-widest uppercase text-xs text-gray-400">Total Net Worth</CardTitle>
                <CardDescription className="text-gray-500">Includes all liquid assets and investments.</CardDescription>
            </CardHeader>
            <CardContent>
                <h2 className="text-5xl font-light text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-500">
                    $1.42M
                </h2>
            </CardContent>
            <CardFooter className="pt-6">
                <Button className="w-full bg-cyan-500 hover:bg-cyan-400 text-black font-semibold shadow-[0_0_15px_rgba(0,240,255,0.4)] transition-all">
                    View Detail Analysis
                </Button>
            </CardFooter>
        </Card>
    ),
};
