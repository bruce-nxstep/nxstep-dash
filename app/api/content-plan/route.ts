import { NextResponse } from 'next/server';
import { getDb } from '@/lib/db';

// GET /api/content-plan — List all content plan items
export async function GET() {
    try {
        const db = getDb();
        const items = db.prepare('SELECT * FROM content_plan ORDER BY scheduled_at ASC').all();
        return NextResponse.json({ items });
    } catch (error) {
        console.error('Failed to get content plan:', error);
        return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 });
    }
}

// POST /api/content-plan — Create a new content plan item
export async function POST(request: Request) {
    try {
        const body = await request.json();
        const db = getDb();

        const stmt = db.prepare(`
            INSERT INTO content_plan (title, post_idea, post_type, content, media_files, scheduled_at, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        `);

        const result = stmt.run(
            body.title || 'Nouveau post',
            body.post_idea || '',
            body.post_type || 'Post',
            body.content || '',
            body.media_files || '[]',
            body.scheduled_at || null,
            body.status || 'Brouillon'
        );

        const newItem = db.prepare('SELECT * FROM content_plan WHERE id = ?').get(result.lastInsertRowid);
        return NextResponse.json({ item: newItem });
    } catch (error) {
        console.error('Failed to create content plan item:', error);
        return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 });
    }
}

// DELETE /api/content-plan?id=123 — Delete a content plan item
export async function DELETE(request: Request) {
    try {
        const { searchParams } = new URL(request.url);
        const id = searchParams.get('id');
        if (!id) {
            return NextResponse.json({ error: 'Missing id parameter' }, { status: 400 });
        }

        const db = getDb();
        db.prepare('DELETE FROM content_plan WHERE id = ?').run(id);
        return NextResponse.json({ success: true });
    } catch (error) {
        console.error('Failed to delete content plan item:', error);
        return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 });
    }
}
