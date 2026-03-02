import { notFound } from 'next/navigation';
import { getPageBySlug } from '@/lib/cms';
import { DefaultPageTemplate } from '@/components/templates/DefaultPageTemplate';

export const dynamic = 'force-dynamic';

interface PageProps {
    params: Promise<{ slug: string }>;
}

export default async function CMSPage({ params }: PageProps) {
    const { slug } = await params;
    const post = await getPageBySlug(slug);

    if (!post) {
        notFound();
    }

    return (
        <DefaultPageTemplate
            title={post.title}
            content={post.content}
            author={post.author}
            date={post.created_at}
            isAiGenerated={!!post.ai_generated}
        />
    );
}
