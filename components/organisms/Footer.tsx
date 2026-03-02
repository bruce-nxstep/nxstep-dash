import Link from 'next/link';

export function Footer() {
    return (
        <footer className="border-t bg-muted/30 py-12">
            <div className="container mx-auto px-4 max-w-6xl">
                <div className="flex flex-col md:flex-row justify-between items-center gap-8">
                    <div className="text-xl font-bold tracking-tighter">NXSTEP</div>

                    <nav className="flex flex-wrap items-center gap-6 text-sm text-muted-foreground">
                        <Link href="/" className="hover:text-primary transition-colors">Journal</Link>
                        <Link href="/about" className="hover:text-primary transition-colors">À propos</Link>
                        <Link href="/contact" className="hover:text-primary transition-colors">Contact</Link>
                        <Link href="/mentions-legales" className="hover:text-primary transition-colors">Mentions Légales</Link>
                    </nav>

                    <div className="text-sm text-muted-foreground">
                        © {new Date().getFullYear()} NXSTEP. Tous droits réservés.
                    </div>
                </div>
            </div>
        </footer>
    );
}
