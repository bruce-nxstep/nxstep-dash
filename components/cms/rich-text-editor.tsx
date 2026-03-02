"use client"

import * as React from "react"
import { cn } from "@/lib/utils"
import {
    Bold, Italic, Underline, Strikethrough,
    Heading1, Heading2, List, ListOrdered, Link2, Quote, Undo2, Redo2,
} from "lucide-react"

const TOOLBAR_ACTIONS = [
    { cmd: "undo", icon: <Undo2 className="h-3.5 w-3.5" />, label: "Undo", group: 0 },
    { cmd: "redo", icon: <Redo2 className="h-3.5 w-3.5" />, label: "Redo", group: 0 },
    { cmd: "bold", icon: <Bold className="h-3.5 w-3.5" />, label: "Bold", group: 1 },
    { cmd: "italic", icon: <Italic className="h-3.5 w-3.5" />, label: "Italic", group: 1 },
    { cmd: "underline", icon: <Underline className="h-3.5 w-3.5" />, label: "Underline", group: 1 },
    { cmd: "strikeThrough", icon: <Strikethrough className="h-3.5 w-3.5" />, label: "Strike", group: 1 },
    { cmd: "h1", icon: <Heading1 className="h-3.5 w-3.5" />, label: "H1", group: 2 },
    { cmd: "h2", icon: <Heading2 className="h-3.5 w-3.5" />, label: "H2", group: 2 },
    { cmd: "insertUnorderedList", icon: <List className="h-3.5 w-3.5" />, label: "Bullet list", group: 3 },
    { cmd: "insertOrderedList", icon: <ListOrdered className="h-3.5 w-3.5" />, label: "Numbered list", group: 3 },
    { cmd: "blockquote", icon: <Quote className="h-3.5 w-3.5" />, label: "Quote", group: 3 },
    { cmd: "createLink", icon: <Link2 className="h-3.5 w-3.5" />, label: "Insert link", group: 4 },
] as const

export interface RichTextEditorProps {
    value?: string
    onChange?: (html: string) => void
    placeholder?: string
    readOnly?: boolean
    minHeight?: number
    className?: string
}

function RichTextEditor({
    value,
    onChange,
    placeholder = "Start writing…",
    readOnly = false,
    minHeight = 200,
    className,
}: RichTextEditorProps) {
    const editorRef = React.useRef<HTMLDivElement>(null)
    const [focused, setFocused] = React.useState(false)

    // Sync external value (initial only)
    React.useEffect(() => {
        if (editorRef.current && value !== undefined && editorRef.current.innerHTML !== value) {
            editorRef.current.innerHTML = value
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [])

    const exec = (cmd: string) => {
        if (cmd === "h1" || cmd === "h2") {
            document.execCommand("formatBlock", false, cmd === "h1" ? "H1" : "H2")
        } else if (cmd === "blockquote") {
            document.execCommand("formatBlock", false, "BLOCKQUOTE")
        } else if (cmd === "createLink") {
            const url = window.prompt("Enter URL:")
            if (url) document.execCommand("createLink", false, url)
        } else {
            document.execCommand(cmd, false)
        }
        editorRef.current?.focus()
    }

    let prevGroup = -1
    return (
        <div
            className={cn(
                "flex flex-col rounded-[var(--radius-lg)] border overflow-hidden transition-colors",
                focused ? "border-[var(--color-primary)]/60" : "border-[var(--color-border)]",
                className
            )}
        >
            {/* Toolbar */}
            {!readOnly && (
                <div className="flex items-center flex-wrap gap-0.5 px-2 py-1.5 border-b border-[var(--color-border)] bg-[var(--color-bg-input)]">
                    {TOOLBAR_ACTIONS.map((action) => {
                        const showSep = action.group !== prevGroup && prevGroup !== -1
                        prevGroup = action.group
                        return (
                            <React.Fragment key={action.cmd}>
                                {showSep && <span className="w-px h-4 bg-[var(--color-border)] mx-1" />}
                                <button
                                    type="button"
                                    title={action.label}
                                    aria-label={action.label}
                                    onMouseDown={(e) => { e.preventDefault(); exec(action.cmd) }}
                                    className="p-1.5 rounded-[var(--radius-sm)] text-[var(--color-text-muted)] hover:text-[var(--color-text-primary)] hover:bg-[var(--color-bg-card)] transition-colors"
                                >
                                    {action.icon}
                                </button>
                            </React.Fragment>
                        )
                    })}
                </div>
            )}

            {/* Editor area */}
            <div className="relative flex-1 bg-[var(--color-bg-input)]">
                {/* Placeholder */}
                {!focused && editorRef.current?.innerHTML === "" && (
                    <span
                        className="absolute top-3 left-3 text-sm text-[var(--color-text-muted)] pointer-events-none select-none"
                        aria-hidden="true"
                    >
                        {placeholder}
                    </span>
                )}
                <div
                    ref={editorRef}
                    contentEditable={!readOnly}
                    suppressContentEditableWarning
                    onFocus={() => setFocused(true)}
                    onBlur={() => {
                        setFocused(false)
                        onChange?.(editorRef.current?.innerHTML ?? "")
                    }}
                    className={cn(
                        "outline-none p-3 text-sm text-[var(--color-text-primary)] leading-relaxed",
                        "[&_h1]:text-2xl [&_h1]:font-bold [&_h1]:mt-3 [&_h1]:mb-1",
                        "[&_h2]:text-xl [&_h2]:font-semibold [&_h2]:mt-2 [&_h2]:mb-1",
                        "[&_blockquote]:border-l-2 [&_blockquote]:border-[var(--color-primary)] [&_blockquote]:pl-3 [&_blockquote]:italic [&_blockquote]:text-[var(--color-text-muted)]",
                        "[&_ul]:list-disc [&_ul]:pl-5 [&_ol]:list-decimal [&_ol]:pl-5",
                        "[&_a]:text-[var(--color-primary)] [&_a]:underline",
                        readOnly && "cursor-default"
                    )}
                    style={{ minHeight }}
                />
            </div>
        </div>
    )
}

export { RichTextEditor }
