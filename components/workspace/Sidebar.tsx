"use client";

import { useWorkspaceStore } from "@/lib/store/workspace";
import { ChevronRight, ChevronDown, FileText, Plus, MoreHorizontal } from "lucide-react";
import { useState } from "react";
import clsx from "clsx";

// Mock Data for initial dev phase (Will be connected to TanStack Query later)
const MOCK_PAGES = [
    { id: "1", title: "Welcome to NXSTech Notion", parentId: null },
    { id: "2", title: "Projects", parentId: null },
    { id: "3", title: "2026 Strategy", parentId: "2" },
    { id: "4", title: "Q1 Campaign", parentId: "3" },
];

export function Sidebar() {
    const { isSidebarOpen } = useWorkspaceStore();

    if (!isSidebarOpen) return null;

    return (
        <aside className="w-64 h-screen bg-[#F7F7F5] border-r border-[#EFEFEF] flex flex-col shrink-0 text-sm overflow-y-auto">
            {/* Sidebar Header */}
            <div className="flex items-center justify-between p-4 hover:bg-black/5 cursor-pointer transition-colors group">
                <div className="flex items-center gap-2 font-medium text-gray-800">
                    <div className="w-5 h-5 bg-[#8200db]-500 text-white rounded-[4px] flex items-center justify-center text-xs">J</div>
                    Jean-Luc's Workspace
                </div>
                <MoreHorizontal className="w-4 h-4 text-gray-400 opacity-0 group-hover:opacity-100 transition-opacity" />
            </div>

            {/* Pages Section */}
            <div className="flex-1 py-2">
                <div className="px-4 py-1 text-xs font-semibold text-gray-400 mb-1">
                    Private
                </div>

                {/* Render Root Pages */}
                {MOCK_PAGES.filter(p => p.parentId === null).map((page) => (
                    <PageTreeItem key={page.id} page={page} allPages={MOCK_PAGES} level={0} />
                ))}
            </div>
        </aside>
    );
}

function PageTreeItem({ page, allPages, level }: { page: any, allPages: any[], level: number }) {
    const [isExpanded, setIsExpanded] = useState(level === 0);
    const { activePageId, setActivePageId } = useWorkspaceStore();

    const children = allPages.filter(p => p.parentId === page.id);
    const hasChildren = children.length > 0;
    const isActive = activePageId === page.id;

    return (
        <div>
            <div
                className={clsx(
                    "flex items-center justify-between py-1 pr-3 cursor-pointer group hover:bg-black/5 transition-colors",
                    isActive ? "bg-black/5 font-medium" : "text-gray-700"
                )}
                style={{ paddingLeft: `${(level * 12) + 16}px` }}
                onClick={() => setActivePageId(page.id)}
            >
                <div className="flex items-center gap-1.5 flex-1 min-w-0">
                    {/* Toggle Chevron */}
                    <div
                        className="w-4 h-4 rounded-sm hover:bg-black/10 flex items-center justify-center -ml-1 text-gray-400"
                        onClick={(e) => {
                            e.stopPropagation();
                            if (hasChildren) setIsExpanded(!isExpanded);
                        }}
                    >
                        {hasChildren && (
                            isExpanded ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronRight className="w-3.5 h-3.5" />
                        )}
                    </div>

                    <FileText className="w-4 h-4 text-gray-400 shrink-0" />
                    <span className="truncate">{page.title}</span>
                </div>

                {/* Action Icons (Hover only) */}
                <div className="opacity-0 group-hover:opacity-100 flex items-center text-gray-400">
                    <div className="w-5 h-5 rounded-sm hover:bg-black/10 flex items-center justify-center">
                        <MoreHorizontal className="w-3.5 h-3.5" />
                    </div>
                    <div className="w-5 h-5 rounded-sm hover:bg-black/10 flex items-center justify-center">
                        <Plus className="w-3.5 h-3.5" />
                    </div>
                </div>
            </div>

            {/* Render Nested Children */}
            {isExpanded && children.length > 0 && (
                <div className="flex flex-col">
                    {children.map(child => (
                        <PageTreeItem key={child.id} page={child} allPages={allPages} level={level + 1} />
                    ))}
                </div>
            )}
        </div>
    );
}
