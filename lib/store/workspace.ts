import { create } from 'zustand';

export type BlockType = 'h1' | 'h2' | 'h3' | 'paragraph' | 'bullet_list' | 'checklist' | 'callout' | 'code' | 'collection';

export interface Block {
    id: string;
    type: BlockType;
    content: any; // JSON standard for Tiptap
    properties?: any; // e.g. checked, language
}

interface WorkspaceState {
    // Sidebar visibility
    isSidebarOpen: boolean;
    toggleSidebar: () => void;

    // Current Page Data
    activePageId: string | null;
    setActivePageId: (id: string | null) => void;

    // Real-time Editor Blocks (Local State before saving to DB)
    blocks: Block[];
    setBlocks: (blocks: Block[]) => void;
    updateBlockContent: (id: string, content: any) => void;
    addBlock: (index: number, block: Block) => void;
    removeBlock: (id: string) => void;
    reorderBlocks: (startIndex: number, endIndex: number) => void;
}

export const useWorkspaceStore = create<WorkspaceState>((set) => ({
    isSidebarOpen: true,
    toggleSidebar: () => set((state) => ({ isSidebarOpen: !state.isSidebarOpen })),

    activePageId: null,
    setActivePageId: (id) => set({ activePageId: id, blocks: [] }), // Reset blocks on page change

    blocks: [],
    setBlocks: (blocks) => set({ blocks }),

    updateBlockContent: (id, content) => set((state) => ({
        blocks: state.blocks.map(b => b.id === id ? { ...b, content } : b)
    })),

    addBlock: (index, block) => set((state) => {
        const newBlocks = [...state.blocks];
        newBlocks.splice(index + 1, 0, block);
        return { blocks: newBlocks };
    }),

    removeBlock: (id) => set((state) => ({
        blocks: state.blocks.filter(b => b.id !== id)
    })),

    reorderBlocks: (startIndex, endIndex) => set((state) => {
        const result = Array.from(state.blocks);
        const [removed] = result.splice(startIndex, 1);
        result.splice(endIndex, 0, removed);
        return { blocks: result };
    })
}));
