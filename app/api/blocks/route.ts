import { NextResponse } from 'next/server';
import { getDb } from '@/lib/db';
import { v4 as uuidv4 } from 'uuid';

// GET /api/blocks?page_id=xxx
export async function GET(request: Request) {
    try {
        const { searchParams } = new URL(request.url);
        const pageId = searchParams.get('page_id');

        if (!pageId) {
            return NextResponse.json({ error: 'page_id is required' }, { status: 400 });
        }

        const db = getDb();
        const blocks = db.prepare('SELECT * FROM blocks WHERE page_id = ? ORDER BY order_index ASC').all(pageId);

        // Parse JSON
        const parsedBlocks = blocks.map((b: any) => ({
            ...b,
            content: b.content ? JSON.parse(b.content) : null,
            properties: b.properties ? JSON.parse(b.properties) : null
        }));

        return NextResponse.json({ blocks: parsedBlocks });
    } catch (error) {
        console.error('Failed to get blocks:', error);
        return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 });
    }
}

// POST /api/blocks - Bulk update/insert blocks for auto-save
export async function POST(request: Request) {
    try {
        const { page_id, blocks } = await request.json();

        if (!page_id || !Array.isArray(blocks)) {
            return NextResponse.json({ error: 'Invalid payload' }, { status: 400 });
        }

        const db = getDb();

        // Use a transaction for bulk save
        const transaction = db.transaction((blocksToSave: any[]) => {
            // For simplicity in this iteration: Delete existing and re-insert 
            // (In production, a true diff sync like Yjs or CRDT is better)
            db.prepare('DELETE FROM blocks WHERE page_id = ?').run(page_id);

            const insert = db.prepare(`
        INSERT INTO blocks (id, page_id, type, content, properties, order_index, parent_block_id) 
        VALUES (?, ?, ?, ?, ?, ?, ?)
      `);

            for (const [index, block] of blocksToSave.entries()) {
                insert.run(
                    block.id || uuidv4(),
                    page_id,
                    block.type,
                    block.content ? JSON.stringify(block.content) : null,
                    block.properties ? JSON.stringify(block.properties) : null,
                    index,
                    block.parent_block_id || null
                );
            }
        });

        transaction(blocks);

        return NextResponse.json({ success: true });
    } catch (error) {
        console.error('Failed to save blocks:', error);
        return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 });
    }
}
