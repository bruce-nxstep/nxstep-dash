'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';

interface NavLinkProps {
    href: string;
    children: React.ReactNode;
    className?: string;
}

export function NavLink({ href, children, className }: NavLinkProps) {
    const pathname = usePathname();
    const isActive = pathname === href;

    return (
        <Link
            href={href}
            className={cn(
                "px-4 py-2 text-sm font-medium transition-colors hover:text-primary",
                isActive
                    ? "text-primary border-b-2 border-primary"
                    : "text-muted-foreground",
                className
            )}
        >
            {children}
        </Link>
    );
}
