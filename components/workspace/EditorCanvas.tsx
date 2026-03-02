"use client";

import { useEditor, EditorContent, ReactRenderer } from '@tiptap/react';
import { Extension } from '@tiptap/core';
import StarterKit from '@tiptap/starter-kit';
import Placeholder from '@tiptap/extension-placeholder';
import Suggestion from '@tiptap/suggestion';
import tippy from 'tippy.js';
import { useWorkspaceStore } from "@/lib/store/workspace";
import { useEffect } from 'react';
import { CommandList } from './SlashCommandList';
import { CollectionNode } from './CollectionExtension';

export function EditorCanvas() {
    const { activePageId } = useWorkspaceStore();

    const editor = useEditor({
        immediatelyRender: false,
        extensions: [
            CollectionNode,
            StarterKit.configure({
                heading: { levels: [1, 2, 3] },
            }),
            Placeholder.configure({
                placeholder: "Press '/' for commands",
            }),
            // @ts-ignore (Tiptap types can be complex for suggestions)
            Extension.create({
                name: 'slashcommand',
                addProseMirrorPlugins() {
                    return [
                        Suggestion({
                            editor: this.editor,
                            char: '/',
                            command: ({ editor, range, props }) => {
                                props.command({ editor, range });
                            },
                            items: ({ query }) => {
                                // Dynamic import of items list to avoid circular dependencies
                                const { getSuggestionItems } = require('./SlashCommandList');
                                return getSuggestionItems({ query });
                            },
                            render: () => {
                                let component: ReactRenderer<any>;
                                let popup: any;

                                return {
                                    onStart: (props) => {
                                        component = new ReactRenderer(CommandList, {
                                            props,
                                            editor: props.editor,
                                        });

                                        popup = tippy('body', {
                                            getReferenceClientRect: props.clientRect,
                                            appendTo: () => document.body,
                                            content: component.element,
                                            showOnCreate: true,
                                            interactive: true,
                                            trigger: 'manual',
                                            placement: 'bottom-start',
                                        })[0] as any;
                                    },
                                    onUpdate(props: any) {
                                        component.updateProps(props);
                                        popup.setProps({
                                            getReferenceClientRect: props.clientRect,
                                        });
                                    },
                                    onKeyDown(props: any) {
                                        if (props.event.key === 'Escape') {
                                            popup.hide();
                                            return true;
                                        }
                                        return component.ref?.onKeyDown(props);
                                    },
                                    onExit() {
                                        popup.destroy();
                                        component.destroy();
                                    },
                                };
                            },
                        }),
                    ];
                },
            }),
        ],
        content: "<h1>Welcome to your new page</h1><p>Start typing or press '/' for commands.</p>",
        editorProps: {
            attributes: {
                class: 'prose prose-stone prose-lg max-w-none focus:outline-none min-h-[500px] mt-8',
            },
        },
    });

    // Re-hydrate editor when page changes (placeholder logic until API is fully wired)
    useEffect(() => {
        if (editor && activePageId) {
            editor.commands.setContent(`<h1>Page ${activePageId}</h1><p>Start typing or press '/' for commands.</p>`);
        }
    }, [activePageId, editor]);

    if (!activePageId) {
        return (
            <div className="flex-1 flex items-center justify-center text-gray-400 bg-white">
                <p>Select or create a page in the sidebar.</p>
            </div>
        );
    }

    return (
        <main className="flex-1 bg-white overflow-y-auto">
            <div className="max-w-4xl mx-auto px-12 py-16">

                {/* Breadcrumb Area Mock */}
                <div className="text-sm text-gray-400 mb-8 flex items-center gap-2">
                    <span>Workspace</span>
                    <span>/</span>
                    <span className="text-gray-800 font-medium">Page {activePageId}</span>
                </div>

                {/* Tiptap Canvas */}
                <div className="relative">
                    <EditorContent editor={editor} />
                </div>

            </div>
        </main>
    );
}
