import { NextResponse } from 'next/server';
import { getDb } from '@/lib/db';
import { v4 as uuidv4 } from 'uuid';

// GET /api/pages - Retrieve all pages (for the sidebar tree)
export async function GET() {
    try {
        const db = getDb();
        const pages = db.prepare('SELECT * FROM pages ORDER BY created_at ASC').all();
        return NextResponse.json({ pages });
    } catch (error) {
        console.error('Failed to get pages:', error);
        return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 });
    }
}

// POST /api/pages - Create a new page
export async function POST(request: Request) {
    try {
        const { title, parent_id } = await request.json();
        const db = getDb();
        const newId = uuidv4();

        db.prepare('INSERT INTO pages (id, title, parent_id) VALUES (?, ?, ?)')
            .run(newId, title || 'Untitled', parent_id || null);

        const newPage = db.prepare('SELECT * FROM pages WHERE id = ?').get(newId);
        return NextResponse.json({ page: newPage });
    } catch (error) {
        console.error('Failed to create page:', error);
        return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 });
    }
}
