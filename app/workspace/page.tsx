import { Sidebar } from "@/components/workspace/Sidebar";
import { EditorCanvas } from "@/components/workspace/EditorCanvas";

export default function WorkspacePage() {
    return (
        <div className="flex h-screen w-full bg-white text-gray-900 overflow-hidden font-sans">
            <Sidebar />
            <EditorCanvas />
        </div>
    );
}
