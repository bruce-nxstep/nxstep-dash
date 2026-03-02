"use client";

import React, { useState, useEffect, forwardRef, useImperativeHandle } from 'react';
import { Type, Heading1, Heading2, Heading3, List, CheckSquare, Code, LayoutGrid } from 'lucide-react';
import clsx from 'clsx';

export interface CommandItemProps {
    title: string;
    description: string;
    icon: React.ReactNode;
    command: ({ editor, range }: { editor: any; range: any }) => void;
}

export const getSuggestionItems = ({ query }: { query: string }) => {
    const items: CommandItemProps[] = [
        {
            title: 'Text',
            description: 'Just start typing with plain text.',
            icon: <Type className="w-4 h-4" />,
            command: ({ editor, range }) => {
                editor.chain().focus().deleteRange(range).setNode('paragraph').run();
            },
        },
        {
            title: 'Heading 1',
            description: 'Big section heading.',
            icon: <Heading1 className="w-4 h-4" />,
            command: ({ editor, range }) => {
                editor.chain().focus().deleteRange(range).setNode('heading', { level: 1 }).run();
            },
        },
        {
            title: 'Heading 2',
            description: 'Medium section heading.',
            icon: <Heading2 className="w-4 h-4" />,
            command: ({ editor, range }) => {
                editor.chain().focus().deleteRange(range).setNode('heading', { level: 2 }).run();
            },
        },
        {
            title: 'Heading 3',
            description: 'Small section heading.',
            icon: <Heading3 className="w-4 h-4" />,
            command: ({ editor, range }) => {
                editor.chain().focus().deleteRange(range).setNode('heading', { level: 3 }).run();
            },
        },
        {
            title: 'Bullet List',
            description: 'Create a simple bulleted list.',
            icon: <List className="w-4 h-4" />,
            command: ({ editor, range }) => {
                editor.chain().focus().deleteRange(range).toggleBulletList().run();
            },
        },
        {
            title: 'To-do List',
            description: 'Track tasks with a to-do list.',
            icon: <CheckSquare className="w-4 h-4" />,
            command: ({ editor, range }) => {
                editor.chain().focus().deleteRange(range).toggleTaskList().run();
            },
        },
        {
            title: 'Code Block',
            description: 'Capture a code snippet.',
            icon: <Code className="w-4 h-4" />,
            command: ({ editor, range }) => {
                editor.chain().focus().deleteRange(range).toggleCodeBlock().run();
            },
        },
        {
            title: 'Collection (Database)',
            description: 'Insert a Table or Kanban board.',
            icon: <LayoutGrid className="w-4 h-4" />,
            command: ({ editor, range }) => {
                editor.chain().focus().deleteRange(range).insertContent({
                    type: 'collection',
                    attrs: { title: 'Untitled Database' }
                }).run();
            },
        }
    ];

    return items.filter(item => item.title.toLowerCase().startsWith(query.toLowerCase())).slice(0, 10);
};

export const CommandList = forwardRef((props: { items: CommandItemProps[], command: any }, ref) => {
    const [selectedIndex, setSelectedIndex] = useState(0);

    const selectItem = (index: number) => {
        const item = props.items[index];
        if (item) {
            props.command(item);
        }
    };

    const upHandler = () => {
        setSelectedIndex((selectedIndex + props.items.length - 1) % props.items.length);
    };

    const downHandler = () => {
        setSelectedIndex((selectedIndex + 1) % props.items.length);
    };

    const enterHandler = () => {
        selectItem(selectedIndex);
    };

    useImperativeHandle(ref, () => ({
        onKeyDown: ({ event }: { event: KeyboardEvent }) => {
            if (event.key === 'ArrowUp') {
                upHandler();
                return true;
            }
            if (event.key === 'ArrowDown') {
                downHandler();
                return true;
            }
            if (event.key === 'Enter') {
                enterHandler();
                return true;
            }
            return false;
        },
    }));

    useEffect(() => { setSelectedIndex(0); }, [props.items]);

    if (!props.items.length) {
        return <div className="bg-white rounded-md shadow-lg border border-gray-200 p-2 text-sm text-gray-500">No results</div>;
    }

    return (
        <div className="bg-white rounded-xl shadow-xl border border-gray-100 overflow-hidden w-72 max-h-[330px] overflow-y-auto">
            <div className="px-3 py-2 text-xs font-semibold text-gray-400 uppercase tracking-wider">Basic blocks</div>
            {props.items.map((item, index) => (
                <button
                    key={index}
                    className={clsx(
                        "w-full flex items-center gap-3 px-3 py-2 text-left transition-colors",
                        index === selectedIndex ? "bg-gray-100" : "hover:bg-gray-50"
                    )}
                    onClick={() => selectItem(index)}
                >
                    <div className="flex items-center justify-center w-10 h-10 rounded-md bg-white border border-gray-200 shrink-0 shadow-sm text-gray-700">
                        {item.icon}
                    </div>
                    <div className="flex flex-col">
                        <span className="text-sm font-medium text-gray-900">{item.title}</span>
                        <span className="text-xs text-gray-400">{item.description}</span>
                    </div>
                </button>
            ))}
        </div>
    );
});

CommandList.displayName = 'CommandList';
