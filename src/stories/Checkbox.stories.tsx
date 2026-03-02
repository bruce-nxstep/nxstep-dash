import type { Meta, StoryObj } from '@storybook/react';
import { Checkbox } from '@/components/ui/checkbox';

const meta = {
    title: 'Atoms/Checkbox',
    component: Checkbox,
    parameters: { layout: 'centered' },
    tags: ['autodocs'],
} satisfies Meta<typeof Checkbox>;
export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = { args: { label: 'Accept terms' } };
export const Checked: Story = { args: { label: 'Checked', defaultChecked: true } };
export const Indeterminate: Story = { args: { label: 'Indeterminate', indeterminate: true } };
export const Disabled: Story = { args: { label: 'Disabled', disabled: true } };
export const DisabledChecked: Story = { args: { label: 'Disabled checked', disabled: true, defaultChecked: true } };

export const AllStates: Story = {
    render: () => (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            <Checkbox label="Default (unchecked)" />
            <Checkbox label="Checked" defaultChecked />
            <Checkbox label="Indeterminate" indeterminate />
            <Checkbox label="Disabled" disabled />
            <Checkbox label="Disabled + Checked" disabled defaultChecked />
        </div>
    ),
};
