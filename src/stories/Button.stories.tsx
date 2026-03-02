import type { Meta, StoryObj } from '@storybook/react';
import { Button } from '@/components/ui/button';

const meta = {
    title: 'Atoms/Button',
    component: Button,
    parameters: { layout: 'centered' },
    tags: ['autodocs'],
    argTypes: {
        variant: {
            control: 'select',
            options: ['default', 'destructive', 'outline', 'secondary', 'ghost', 'link'],
        },
        size: {
            control: 'select',
            options: ['xs', 'sm', 'default', 'lg', 'icon'],
        },
        disabled: { control: 'boolean' },
    },
} satisfies Meta<typeof Button>;

export default meta;
type Story = StoryObj<typeof meta>;

// ── Individual variants ──────────────────────────────────────────────────────
export const Primary: Story = { args: { children: 'Primary Action', variant: 'default' } };
export const Secondary: Story = { args: { children: 'Secondary Action', variant: 'secondary' } };
export const Outline: Story = { args: { children: 'Outlined', variant: 'outline' } };
export const Ghost: Story = { args: { children: 'Ghost', variant: 'ghost' } };
export const Danger: Story = { args: { children: 'Delete', variant: 'destructive' } };
export const LinkStyle: Story = { args: { children: 'Learn more →', variant: 'link' } };

// ── States ───────────────────────────────────────────────────────────────────
export const Disabled: Story = { args: { children: 'Disabled', disabled: true } };
export const DisabledDanger: Story = { args: { children: 'Delete', variant: 'destructive', disabled: true } };

// ── Sizes ────────────────────────────────────────────────────────────────────
export const AllSizes: Story = {
    render: () => (
        <div style={{ display: 'flex', gap: 12, alignItems: 'center', flexWrap: 'wrap' }}>
            <Button size="xs">XSmall</Button>
            <Button size="sm">Small</Button>
            <Button size="default">Default</Button>
            <Button size="lg">Large</Button>
        </div>
    ),
};

// ── All variants grid ────────────────────────────────────────────────────────
export const AllVariants: Story = {
    render: () => (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16, padding: 16 }}>
            {/* Normal */}
            <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
                {(['default', 'secondary', 'outline', 'ghost', 'destructive', 'link'] as const).map(v => (
                    <Button key={v} variant={v}>{v}</Button>
                ))}
            </div>
            {/* Disabled */}
            <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
                {(['default', 'secondary', 'outline', 'ghost', 'destructive'] as const).map(v => (
                    <Button key={`${v}-disabled`} variant={v} disabled>{v} (disabled)</Button>
                ))}
            </div>
        </div>
    ),
};
