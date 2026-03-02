"use client";

import React from "react";
import { usePathname } from "next/navigation";

export function NavigationWrapper({
    header,
    footer,
    children
}: {
    header: React.ReactNode;
    footer: React.ReactNode;
    children: React.ReactNode;
}) {
    const pathname = usePathname();
    const isEditor = pathname?.startsWith("/editor");

    if (isEditor) {
        return <>{children}</>;
    }

    return (
        <>
            {header}
            <main className="flex-grow">
                {children}
            </main>
            {footer}
        </>
    );
}
