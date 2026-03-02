import { NextResponse } from 'next/server';
import Database from 'better-sqlite3';
import path from 'path';

const DB_PATH = path.join(process.cwd(), 'wealth_agent', 'data', 'cms.db');

export async function POST(request: Request) {
    try {
        const { id, content } = await request.json();

        if (!id || content === undefined) {
            return NextResponse.json({ error: 'Missing id or content' }, { status: 400 });
        }

        const db = new Database(DB_PATH);

        const stmt = db.prepare('UPDATE posts SET content = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?');
        const result = stmt.run(content, id);

        if (result.changes === 0) {
            return NextResponse.json({ error: 'Page not found' }, { status: 404 });
        }

        return NextResponse.json({ success: true });
    } catch (error) {
        console.error('Error saving CMS page:', error);
        return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 });
    }
}
