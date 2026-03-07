import { NextResponse } from 'next/server';
import { getDb } from '@/lib/db';

// PATCH /api/content-plan/[id] — Update a content plan item
export async function PATCH(
    request: Request,
    { params }: { params: Promise<{ id: string }> }
) {
    try {
        const { id } = await params;
        const body = await request.json();
        const db = getDb();

        // Build dynamic SET clause
        const allowedFields = ['title', 'post_idea', 'post_type', 'content', 'media_files', 'scheduled_at', 'status'];
        const updates: string[] = [];
        const values: unknown[] = [];

        for (const field of allowedFields) {
            if (body[field] !== undefined) {
                updates.push(`${field} = ?`);
                values.push(body[field]);
            }
        }

        if (updates.length === 0) {
            return NextResponse.json({ error: 'No valid fields to update' }, { status: 400 });
        }

        updates.push('updated_at = CURRENT_TIMESTAMP');
        values.push(id);

        db.prepare(`UPDATE content_plan SET ${updates.join(', ')} WHERE id = ?`).run(...values);

        const updated = db.prepare('SELECT * FROM content_plan WHERE id = ?').get(id);
        return NextResponse.json({ item: updated });
    } catch (error) {
        console.error('Failed to update content plan item:', error);
        return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 });
    }
}
