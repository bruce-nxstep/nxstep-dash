import Database from 'better-sqlite3';
import path from 'path';

const DB_PATH = path.join(process.cwd(), 'wealth_agent', 'data', 'cms.db');

export interface CMSPost {
    id: number;
    title: string;
    slug: string;
    content: string;
    excerpt: string;
    post_type: 'post' | 'page';
    status: 'draft' | 'published' | 'scheduled';
    meta_title: string;
    meta_description: string;
    author: string;
    ai_generated: number;
    featured_image_url: string;
    category_names: string; // From JOIN
    created_at: string;
    updated_at: string;
}

export function getDb() {
    return new Database(DB_PATH, { verbose: console.log });
}

export async function getPageBySlug(slug: string): Promise<CMSPost | null> {
    const db = getDb();
    const query = `
    SELECT p.*, GROUP_CONCAT(c.name) as category_names
    FROM posts p
    LEFT JOIN post_categories pc ON p.id = pc.post_id
    LEFT JOIN categories c ON pc.category_id = c.id
    WHERE p.slug = ? AND p.status = 'published'
    GROUP BY p.id
    LIMIT 1
  `;
    const post = db.prepare(query).get(slug) as CMSPost;
    return post || null;
}

export async function getAllPublishedPages(): Promise<CMSPost[]> {
    const db = getDb();
    const query = `
    SELECT p.*, GROUP_CONCAT(c.name) as category_names
    FROM posts p
    LEFT JOIN post_categories pc ON p.id = pc.post_id
    LEFT JOIN categories c ON pc.category_id = c.id
    WHERE p.post_type = 'page' AND p.status = 'published'
    GROUP BY p.id
    ORDER BY p.title ASC
  `;
    return db.prepare(query).all() as CMSPost[];
}

export async function getNavData() {
    const pages = await getAllPublishedPages();

    // Group by category if we want hierarchical nav
    const grouped: Record<string, CMSPost[]> = {};
    pages.forEach(p => {
        const cats = p.category_names ? p.category_names.split(',') : ['Uncategorized'];
        cats.forEach(cat => {
            if (!grouped[cat]) grouped[cat] = [];
            grouped[cat].push(p);
        });
    });

    return grouped;
}
