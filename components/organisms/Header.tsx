import Link from 'next/link';
import { getNavData } from '@/lib/cms';
import { NavLink } from '@/components/molecules/NavLink';
import { Menu, X, ChevronDown } from 'lucide-react';
import { Button } from '@/components/ui/button';

export async function Header() {
    const navData = await getNavData();
    const categories = Object.keys(navData);

    return (
        <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
            <div className="container mx-auto px-4 flex h-20 items-center justify-between">

                {/* Logo */}
                <Link href="/" className="flex items-center space-x-2">
                    <span className="text-2xl font-black tracking-tighter gradient-text">NXSTEP</span>
                </Link>

                {/* Desktop Navigation */}
                <nav className="hidden md:flex items-center space-x-2">
                    <NavLink href="/">Journal</NavLink>

                    {categories.map(cat => (
                        <div key={cat} className="relative group">
                            <button className="flex items-center px-4 py-2 text-sm font-medium text-muted-foreground transition-colors hover:text-primary group">
                                {cat}
                                <ChevronDown className="ml-1 h-4 w-4 transition-transform group-hover:rotate-180" />
                            </button>

                            {/* Dropdown Menu (Hierarchy) */}
                            <div className="absolute left-0 mt-0 w-56 origin-top-left rounded-xl border bg-popover p-2 shadow-xl opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200">
                                {navData[cat].map(page => (
                                    <Link
                                        key={page.id}
                                        href={`/${page.slug}`}
                                        className="block rounded-lg px-3 py-2 text-sm transition-colors hover:bg-accent hover:text-accent-foreground"
                                    >
                                        {page.title}
                                    </Link>
                                ))}
                            </div>
                        </div>
                    ))}
                </nav>

                {/* Mobile Actions */}
                <div className="flex items-center space-x-4">
                    <Button variant="outline" className="hidden sm:flex rounded-full px-6">
                        Espace Client
                    </Button>
                    <Button variant="ghost" size="icon" className="md:hidden">
                        <Menu className="h-6 w-6" />
                    </Button>
                </div>

            </div>
        </header>
    );
}
