import { NextResponse } from 'next/server';
import { getPageBySlug } from '@/lib/cms';

interface PageProps {
    params: Promise<{ slug: string }>;
}

export async function GET(request: Request, { params }: PageProps) {
    try {
        const { slug } = await params;
        const post = await getPageBySlug(slug);

        if (!post) {
            return NextResponse.json({ error: 'Page not found' }, { status: 404 });
        }

        return NextResponse.json(post);
    } catch (error) {
        console.error('Error fetching CMS page:', error);
        return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 });
    }
}
