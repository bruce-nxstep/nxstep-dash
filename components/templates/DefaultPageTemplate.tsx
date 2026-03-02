import React from 'react';
import { StitchTheme } from '@/components/organisms/StitchTheme';

interface DefaultPageTemplateProps {
    title: string;
    content: string;
    author?: string;
    date?: string;
    sidebar?: React.ReactNode;
    isAiGenerated?: boolean;
}

export function DefaultPageTemplate({
    title,
    content,
    author,
    date,
    sidebar,
    isAiGenerated = false
}: DefaultPageTemplateProps) {
    return (
        <div className="w-full">
            {/* Design System Tokens & Injections */}
            <StitchTheme />

            <main className="flex-grow">
                {/* 
                   If it's a Stitch/AI design, we let it take the full width 
                   and handle its own spacing to respect the high-fidelity layout.
                */}
                {isAiGenerated ? (
                    <div
                        className="w-full"
                        dangerouslySetInnerHTML={{ __html: content }}
                    />
                ) : (
                    <div className="container mx-auto px-4 py-12 md:py-20 max-w-6xl">
                        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12">

                            {/* Main Content Area */}
                            <article className={sidebar ? "lg:col-span-8" : "lg:col-span-12"}>
                                <header className="mb-10 text-center lg:text-left">
                                    <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight mb-4 gradient-text">
                                        {title}
                                    </h1>
                                    {(author || date) && (
                                        <div className="flex items-center gap-4 text-sm text-muted-foreground">
                                            {author && <span>Par <span className="text-foreground font-medium">{author}</span></span>}
                                            {author && date && <span className="h-1 w-1 rounded-full bg-border" />}
                                            {date && <span>Publié le {new Date(date).toLocaleDateString()}</span>}
                                        </div>
                                    )}
                                </header>

                                <div
                                    className="prose prose-zinc dark:prose-invert max-w-none 
                           prose-h2:text-2xl prose-h2:font-bold prose-h2:mt-12 prose-h2:mb-6
                           prose-p:text-lg prose-p:leading-relaxed prose-p:mb-6 mb-20"
                                    dangerouslySetInnerHTML={{ __html: content }}
                                />
                            </article>

                            {/* Optional Sidebar */}
                            {sidebar && (
                                <aside className="lg:col-span-4 space-y-12">
                                    {sidebar}
                                </aside>
                            )}

                        </div>
                    </div>
                )}
            </main>
        </div>
    );
}
