'use client';

import React, { useEffect, useRef, useState, use } from 'react';
import grapesjs from 'grapesjs';
import 'grapesjs/dist/css/grapes.min.css';
import gjsPresetWebpage from 'grapesjs-preset-webpage';
import { Button } from '@/components/ui/button';
import { Save, Loader2, ArrowLeft } from 'lucide-react';
import { toast } from 'sonner';

interface EditorPageProps {
    params: Promise<{ slug: string }>;
}

export default function EditorPage({ params }: EditorPageProps) {
    const { slug } = use(params);
    const editorRef = useRef<HTMLDivElement>(null);
    const [editor, setEditor] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [pageData, setPageData] = useState<any>(null);

    useEffect(() => {
        async function fetchPage() {
            try {
                const res = await fetch(`/api/cms/pages/${slug}`);
                const data = await res.json();
                setPageData(data);
                setLoading(false);
            } catch (error) {
                console.error('Error fetching page:', error);
                toast.error('Erreur lors du chargement de la page.');
            }
        }
        fetchPage();
    }, [slug]);

    useEffect(() => {
        if (!loading && pageData && editorRef.current && !editor) {
            const gjsEditor = grapesjs.init({
                container: editorRef.current,
                height: 'calc(100vh - 64px)',
                width: 'auto',
                storageManager: false,
                plugins: [gjsPresetWebpage],
                pluginsOpts: {
                    [gjsPresetWebpage]: {},
                },
                canvas: {
                    styles: [
                        'https://cdn.tailwindcss.com?plugins=forms,container-queries',
                        'https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&display=swap',
                        'https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap',
                    ],
                    scripts: [
                        'https://cdn.tailwindcss.com?plugins=forms,container-queries',
                    ]
                }
            });

            // Inject Design System Tokens as requested by user
            gjsEditor.on('canvas:mount', () => {
                const doc = gjsEditor.Canvas.getDocument();
                if (doc) {
                    const style = doc.createElement('style');
                    style.innerHTML = `
                        :root {
                            --color-primary: #7000bb;
                            --color-primary-light: #00d22c;
                            --color-primary-dark: #c815fb;
                            --color-success: #c52222;
                            --color-warning: #f59e0b;
                            --color-danger: #ef4444;
                            --color-info: #a53bf6;
                            --color-text-primary: #ffffff;
                            --color-text-secondary: #a1a1aa;
                            --color-text-muted: #52525b;
                            --color-bg-app: #020202;
                            --color-bg-card: #111118;
                            --color-bg-sidebar: #0d0d12;
                            --color-bg-input: #1a1a24;
                            --font-size-h1: 48px;
                            --font-size-h2: 36px;
                            --font-size-h3: 24px;
                            --color-bg-page: #181818;
                            /* Tailwind compat variables */
                            --background: 240 10% 3.9%;
                            --foreground: 0 0% 98%;
                            --primary: 271 100% 43%;
                            --border: 240 3.7% 15.9%;
                        }
                        .glass-panel {
                            background: rgba(26, 17, 34, 0.6);
                            backdrop-filter: blur(12px);
                            -webkit-backdrop-filter: blur(12px);
                            border: 1px solid rgba(127, 25, 230, 0.2);
                        }
                        .text-gradient {
                            background: linear-gradient(to right, #7f19e6, #c084fc);
                            -webkit-background-clip: text;
                            -webkit-text-fill-color: transparent;
                        }
                        .glow-effect {
                            box-shadow: 0 0 20px rgba(127, 25, 230, 0.3);
                        }
                        body { 
                            font-family: 'Space Grotesk', sans-serif; 
                            background-color: var(--color-bg-page); 
                            color: white; 
                            margin: 0;
                        }
                    `;
                    doc.head.appendChild(style);
                }
            });

            gjsEditor.setComponents(pageData.content);
            setEditor(gjsEditor);
        }
    }, [loading, pageData, editor]);

    const handleSave = async () => {
        if (!editor) return;
        setSaving(true);
        const content = editor.getHtml() + `<style>${editor.getCss()}</style>`;

        try {
            const res = await fetch('/api/cms/save', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ id: pageData.id, content }),
            });

            if (res.ok) {
                toast.success('Page enregistrée avec succès !');
            } else {
                toast.error('Erreur lors de l\'enregistrement.');
            }
        } catch (error) {
            toast.error('Erreur serveur.');
        } finally {
            setSaving(false);
        }
    };

    if (loading) return <div className="flex h-screen items-center justify-center"><Loader2 className="h-8 w-8 animate-spin" /></div>;

    return (
        <div className="flex flex-col h-screen bg-background">
            <header className="h-16 border-b flex items-center justify-between px-6 bg-card z-50">
                <div className="flex items-center gap-4">
                    <Button variant="ghost" size="icon" onClick={() => window.history.back()}>
                        <ArrowLeft className="h-4 w-4" />
                    </Button>
                    <h1 className="font-semibold text-lg">Éditeur Visuel : {pageData?.title}</h1>
                </div>
                <div className="flex items-center gap-2">
                    <Button onClick={handleSave} disabled={saving} className="gap-2">
                        {saving ? <Loader2 className="h-4 w-4 animate-spin" /> : <Save className="h-4 w-4" />}
                        Enregistrer
                    </Button>
                </div>
            </header>
            <div ref={editorRef} />
        </div>
    );
}
