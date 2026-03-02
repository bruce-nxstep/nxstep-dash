import { NextResponse } from 'next/server';
import { getPageBySlugAnyStatus } from '@/lib/cms';

export const dynamic = 'force-dynamic';

interface PageProps {
    params: Promise<{ slug: string }>;
}

export async function GET(request: Request, { params }: PageProps) {
    try {
        const { slug } = await params;
        const post = await getPageBySlugAnyStatus(slug);

        if (!post) {
            return NextResponse.json({ error: 'Page not found' }, { status: 404 });
        }

        return NextResponse.json(post);
    } catch (error) {
        console.error('Error fetching CMS page:', error);
        return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 });
    }
}
