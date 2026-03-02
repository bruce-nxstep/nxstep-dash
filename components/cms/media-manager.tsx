"use client"

import * as React from "react"
import { Upload, X, ImageIcon } from "lucide-react"
import { cn } from "@/lib/utils"

export interface MediaFile {
    id: string
    src: string
    name?: string
}

export interface MediaManagerProps {
    files?: MediaFile[]
    onAdd?: (files: MediaFile[]) => void
    onDelete?: (id: string) => void
    onSelect?: (file: MediaFile) => void
    selectedId?: string
    maxFiles?: number
    className?: string
}

function MediaManager({
    files = [],
    onAdd,
    onDelete,
    onSelect,
    selectedId,
    maxFiles = 50,
    className,
}: MediaManagerProps) {
    const inputRef = React.useRef<HTMLInputElement>(null)
    const [dragging, setDragging] = React.useState(false)

    const handleFiles = (fileList: FileList | null) => {
        if (!fileList) return
        const newFiles: MediaFile[] = Array.from(fileList)
            .filter((f) => f.type.startsWith("image/"))
            .slice(0, maxFiles - files.length)
            .map((f) => ({
                id: `media-${Date.now()}-${Math.random().toString(36).slice(2)}`,
                src: URL.createObjectURL(f),
                name: f.name,
            }))
        if (newFiles.length > 0) onAdd?.(newFiles)
    }

    return (
        <div className={cn("flex flex-col gap-3", className)}>
            {/* Drop zone */}
            <div
                onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
                onDragLeave={() => setDragging(false)}
                onDrop={(e) => { e.preventDefault(); setDragging(false); handleFiles(e.dataTransfer.files) }}
                onClick={() => inputRef.current?.click()}
                className={cn(
                    "flex flex-col items-center justify-center gap-2 p-6 rounded-[var(--radius-xl)]",
                    "border-2 border-dashed cursor-pointer transition-colors select-none",
                    dragging
                        ? "border-[var(--color-primary)] bg-[var(--color-primary)]/5"
                        : "border-[var(--color-border)] hover:border-[var(--color-primary)]/50 bg-[var(--color-bg-input)]"
                )}
            >
                <Upload className="h-8 w-8 text-[var(--color-text-muted)]" />
                <p className="text-sm font-medium text-[var(--color-text-secondary)]">
                    Drag & drop images or <span className="text-[var(--color-primary)]">browse</span>
                </p>
                <p className="text-xs text-[var(--color-text-muted)]">PNG, JPG, GIF, WEBP</p>
                <input
                    ref={inputRef}
                    type="file"
                    multiple
                    accept="image/*"
                    className="sr-only"
                    onChange={(e) => handleFiles(e.target.files)}
                />
            </div>

            {/* Grid */}
            {files.length > 0 && (
                <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 gap-2">
                    {files.map((file) => (
                        <div
                            key={file.id}
                            onClick={() => onSelect?.(file)}
                            className={cn(
                                "relative group rounded-[var(--radius-lg)] overflow-hidden cursor-pointer",
                                "border-2 transition-all aspect-square",
                                selectedId === file.id
                                    ? "border-[var(--color-primary)] shadow-lg shadow-[var(--color-primary)]/20"
                                    : "border-transparent hover:border-[var(--color-primary)]/40"
                            )}
                        >
                            <img
                                src={file.src}
                                alt={file.name ?? "Media"}
                                className="w-full h-full object-cover"
                                loading="lazy"
                            />
                            {/* Delete button */}
                            {onDelete && (
                                <button
                                    type="button"
                                    aria-label={`Delete ${file.name ?? "image"}`}
                                    onClick={(e) => { e.stopPropagation(); onDelete(file.id) }}
                                    className="absolute top-1 right-1 p-0.5 rounded-full bg-black/60 text-white opacity-0 group-hover:opacity-100 transition-opacity hover:bg-[var(--color-danger)]"
                                >
                                    <X className="h-3 w-3" />
                                </button>
                            )}
                            {/* Selected indicator */}
                            {selectedId === file.id && (
                                <span className="absolute bottom-1 right-1 w-4 h-4 rounded-full bg-[var(--color-primary)] flex items-center justify-center">
                                    <svg viewBox="0 0 10 10" fill="none" className="w-2.5 h-2.5">
                                        <path d="M1.5 5l2.5 2.5 4.5-4.5" stroke="black" strokeWidth="1.8" strokeLinecap="round" />
                                    </svg>
                                </span>
                            )}
                        </div>
                    ))}
                </div>
            )}

            {files.length === 0 && (
                <div className="flex items-center justify-center gap-2 py-4 text-[var(--color-text-muted)] text-sm">
                    <ImageIcon className="h-4 w-4" />
                    No media yet
                </div>
            )}

            <p className="text-xs text-[var(--color-text-muted)] text-right">
                {files.length} / {maxFiles}
            </p>
        </div>
    )
}

export { MediaManager }
