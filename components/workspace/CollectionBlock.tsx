"use client";

import { NodeViewWrapper } from '@tiptap/react';
import React, { useState } from 'react';
import { Table, LayoutDashboard, ListFilter, Plus, GripVertical, Trash2 } from 'lucide-react';

export function CollectionBlock(props: any) {
    const [activeView, setActiveView] = useState('kanban');

    const deleteNode = () => {
        props.deleteNode();
    };

    return (
        <NodeViewWrapper className="my-8 relative group">
            {/* Hover Actions (Drag Handle & Delete) */}
            <div className="absolute -left-12 top-2 opacity-0 group-hover:opacity-100 transition-opacity flex items-center gap-1">
                <div
                    className="p-1 cursor-grab hover:bg-gray-100 rounded text-gray-400 drag-handle"
                    contentEditable={false}
                    draggable
                    data-drag-handle
                >
                    <GripVertical className="h-4 w-4" />
                </div>
                <button
                    onClick={deleteNode}
                    className="p-1 cursor-pointer hover:bg-red-50 hover:text-red-500 rounded text-gray-400 transition-colors"
                    contentEditable={false}
                >
                    <Trash2 className="h-4 w-4" />
                </button>
            </div>

            {/* Collection Container */}
            <div className="border border-gray-200 rounded-xl bg-white shadow-sm overflow-hidden" contentEditable={false}>

                {/* Header / View Switcher */}
                <div className="flex items-center justify-between px-4 py-3 border-b border-gray-100 bg-gray-50/50">
                    <div className="flex items-center gap-2">
                        <input
                            type="text"
                            placeholder="Untitled Database"
                            className="bg-transparent border-none focus:outline-none font-semibold text-gray-800 placeholder-gray-400 w-48"
                            defaultValue={props.node.attrs.title}
                            onBlur={(e) => props.updateAttributes({ title: e.target.value })}
                        />

                        <div className="h-4 w-px bg-gray-200 mx-2" />

                        {/* View Tabs */}
                        <div className="flex space-x-1">
                            <button
                                onClick={() => setActiveView('table')}
                                className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded-md text-xs font-medium transition-colors ${activeView === 'table' ? 'bg-white shadow-sm text-gray-900 border border-gray-200/60' : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'
                                    }`}
                            >
                                <Table className="h-3.5 w-3.5" /> Table
                            </button>
                            <button
                                onClick={() => setActiveView('kanban')}
                                className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded-md text-xs font-medium transition-colors ${activeView === 'kanban' ? 'bg-white shadow-sm text-gray-900 border border-gray-200/60' : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'
                                    }`}
                            >
                                <LayoutDashboard className="h-3.5 w-3.5" /> Kanban
                            </button>
                        </div>
                    </div>

                    {/* Actions */}
                    <div className="flex items-center gap-2">
                        <button className="p-1.5 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-md transition-colors">
                            <ListFilter className="h-4 w-4" />
                        </button>
                        <button className="flex items-center gap-1.5 px-3 py-1.5 bg-primary text-white text-xs font-medium rounded-md hover:bg-primary/90 transition-colors shadow-sm">
                            <Plus className="h-3.5 w-3.5" /> New Item
                        </button>
                    </div>
                </div>

                {/* Content Area Rendering (Placeholder for actual Data Views) */}
                <div className="p-4 bg-gray-50/30 min-h-[200px]">
                    {activeView === 'table' && (
                        <div className="flex items-center justify-center h-48 border-2 border-dashed border-gray-200 rounded-lg bg-white/50">
                            <p className="text-sm text-gray-400">Spreadsheet View Component mounting here...</p>
                        </div>
                    )}

                    {activeView === 'kanban' && (
                        <div className="flex items-center justify-center h-48 border-2 border-dashed border-gray-200 rounded-lg bg-white/50">
                            <p className="text-sm text-gray-400">Kanban Board Component mounting here...</p>
                        </div>
                    )}
                </div>

            </div>
        </NodeViewWrapper>
    );
}
