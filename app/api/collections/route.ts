import { NextResponse } from 'next/server';
import { getDb } from '@/lib/db';
import { v4 as uuidv4 } from 'uuid';

export async function GET(request: Request) {
    try {
        const { searchParams } = new URL(request.url);
        const pageId = searchParams.get('page_id');

        const db = getDb();
        let collections = [];

        if (pageId) {
            collections = db.prepare('SELECT * FROM collections WHERE page_id = ?').all(pageId);
        } else {
            collections = db.prepare('SELECT * FROM collections').all();
        }

        const parsedCollections = collections.map((c: any) => ({
            ...c,
            schema: c.schema ? JSON.parse(c.schema) : null
        }));

        return NextResponse.json({ collections: parsedCollections });
    } catch (error) {
        console.error('Failed to get collections:', error);
        return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 });
    }
}

export async function POST(request: Request) {
    try {
        const { page_id, schema } = await request.json();
        const db = getDb();
        const newId = uuidv4();

        // Schema defines columns like [{ id: 'status', label: 'Status', type: 'select', options: ['A faire', 'En cours'] }]
        db.prepare('INSERT INTO collections (id, page_id, schema) VALUES (?, ?, ?)')
            .run(newId, page_id, JSON.stringify(schema || []));

        const newCollection = db.prepare('SELECT * FROM collections WHERE id = ?').get(newId);
        newCollection.schema = JSON.parse(newCollection.schema);

        return NextResponse.json({ collection: newCollection });
    } catch (error) {
        console.error('Failed to create collection:', error);
        return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 });
    }
}
