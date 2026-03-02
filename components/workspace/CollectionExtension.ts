import { mergeAttributes, Node } from '@tiptap/core';
import { ReactNodeViewRenderer } from '@tiptap/react';
import { CollectionBlock } from './CollectionBlock';

export const CollectionNode = Node.create({
    name: 'collection',
    group: 'block',
    atom: true, // It's treated as a single selectable block, not editable inline prose

    addAttributes() {
        return {
            title: {
                default: 'Untitled Database',
            },
            dataId: {
                default: null, // this will reference the UUID in our SQLite 'collections' table
            }
        };
    },

    parseHTML() {
        return [
            {
                tag: 'div[data-type="collection"]',
            },
        ];
    },

    renderHTML({ HTMLAttributes }) {
        return ['div', mergeAttributes(HTMLAttributes, { 'data-type': 'collection' })];
    },

    addNodeView() {
        return ReactNodeViewRenderer(CollectionBlock);
    },
});
