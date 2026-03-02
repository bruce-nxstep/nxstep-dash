import type { Meta, StoryObj } from '@storybook/react';
import { Badge } from '@/components/ui/badge';

const meta = {
    title: 'Atoms/Badge',
    component: Badge,
    parameters: { layout: 'centered' },
    tags: ['autodocs'],
    argTypes: {
        variant: { control: 'select', options: ['default', 'primary', 'secondary', 'success', 'warning', 'danger', 'outline'] },
        size: { control: 'select', options: ['sm', 'md'] },
    },
} satisfies Meta<typeof Badge>;
export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = { args: { children: 'Default' } };
export const Primary: Story = { args: { children: 'Primary', variant: 'primary' } };
export const Secondary: Story = { args: { children: 'Secondary', variant: 'secondary' } };
export const Success: Story = { args: { children: 'Success', variant: 'success' } };
export const Warning: Story = { args: { children: 'Warning', variant: 'warning' } };
export const Danger: Story = { args: { children: 'Danger', variant: 'danger' } };
export const Outline: Story = { args: { children: 'Outline', variant: 'outline' } };

export const AllVariants: Story = {
    render: () => (
        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', padding: 16 }}>
            {(['default', 'primary', 'secondary', 'success', 'warning', 'danger', 'outline'] as const).map(v => (
                <Badge key={v} variant={v}>{v}</Badge>
            ))}
        </div>
    ),
};

export const Sizes: Story = {
    render: () => (
        <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
            <Badge size="sm" variant="primary">Small</Badge>
            <Badge size="md" variant="primary">Medium</Badge>
        </div>
    ),
};
