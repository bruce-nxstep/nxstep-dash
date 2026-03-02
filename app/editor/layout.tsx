import { Toaster } from "sonner";

export default function EditorLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <div className="min-h-screen bg-background antialiased flex flex-col font-sans">
            {children}
            <Toaster position="top-center" richColors />
        </div>
    );
}
