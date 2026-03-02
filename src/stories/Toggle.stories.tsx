import type { Meta, StoryObj } from '@storybook/react';
import { Toggle } from '@/components/ui/toggle';

const meta = {
    title: 'Atoms/Toggle',
    component: Toggle,
    parameters: { layout: 'centered' },
    tags: ['autodocs'],
    argTypes: {
        size: { control: 'radio', options: ['sm', 'md'] },
    },
} satisfies Meta<typeof Toggle>;
export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = { args: { label: 'Enable feature' } };
export const On: Story = { args: { label: 'Enabled', defaultChecked: true } };
export const Disabled: Story = { args: { label: 'Disabled', disabled: true } };
export const DisabledOn: Story = { args: { label: 'Disabled + On', disabled: true, defaultChecked: true } };
export const Small: Story = { args: { label: 'Small toggle', size: 'sm' } };

export const AllStates: Story = {
    render: () => (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            <Toggle label="Off (default)" />
            <Toggle label="On" defaultChecked />
            <Toggle label="Disabled off" disabled />
            <Toggle label="Disabled on" disabled defaultChecked />
            <Toggle label="Small – Off" size="sm" />
            <Toggle label="Small – On" size="sm" defaultChecked />
        </div>
    ),
};
