'use client';

import { useState, useRef } from 'react';
import Link from 'next/link';
import {
    ArrowLeft,
    Upload,
    FileText,
    Search,
    Trash2,
    Eye,
    X,
    Loader2,
    FolderOpen,
    CheckCircle,
    AlertTriangle,
    HelpCircle,
} from 'lucide-react';

interface Document {
    id: string;
    name: string;
    chunks: number;
    uploadedAt: string;
    size: string;
    status: 'processing' | 'ready' | 'error';
}

export default function DocumentsPage() {
    const [documents, setDocuments] = useState<Document[]>(mockDocuments);
    const [searchQuery, setSearchQuery] = useState('');
    const [isUploading, setIsUploading] = useState(false);
    const [showUploadModal, setShowUploadModal] = useState(false);
    const [deleteConfirm, setDeleteConfirm] = useState<string | null>(null);
    const [previewDoc, setPreviewDoc] = useState<Document | null>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);

    const filteredDocs = documents.filter(doc =>
        doc.name.toLowerCase().includes(searchQuery.toLowerCase())
    );

    // Handle file selection
    const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        const files = e.target.files;
        if (!files || files.length === 0) return;

        setIsUploading(true);
        setShowUploadModal(false);

        // Process each file
        Array.from(files).forEach((file) => {
            // Add document with processing status
            const newDoc: Document = {
                id: Date.now().toString() + Math.random().toString(36).substr(2, 9),
                name: file.name,
                chunks: 0,
                uploadedAt: 'Just now',
                size: formatFileSize(file.size),
                status: 'processing',
            };

            setDocuments(prev => [newDoc, ...prev]);

            // Simulate processing completion
            setTimeout(() => {
                setDocuments(prev =>
                    prev.map(d =>
                        d.id === newDoc.id
                            ? { ...d, status: 'ready', chunks: Math.floor(Math.random() * 50) + 10 }
                            : d
                    )
                );
                setIsUploading(false);
            }, 2000 + Math.random() * 2000);
        });

        // Reset input
        if (fileInputRef.current) {
            fileInputRef.current.value = '';
        }
    };

    // Handle delete
    const handleDelete = (docId: string) => {
        setDocuments(prev => prev.filter(d => d.id !== docId));
        setDeleteConfirm(null);
    };

    // Format file size
    const formatFileSize = (bytes: number): string => {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
    };

    return (
        <div className="min-h-screen">
            {/* Hidden file input */}
            <input
                ref={fileInputRef}
                type="file"
                multiple
                accept=".pdf,.md,.txt,.docx,.doc"
                className="hidden"
                onChange={handleFileSelect}
            />

            {/* Header */}
            <header className="glass border-b border-surface-200/50 dark:border-surface-700/50 sticky top-0 z-40">
                <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
                    <div className="flex items-center gap-4">
                        <Link href="/" className="btn-ghost p-2" title="Go back home">
                            <ArrowLeft className="w-5 h-5" />
                        </Link>
                        <div className="flex items-center gap-3">
                            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center">
                                <FileText className="w-5 h-5 text-white" />
                            </div>
                            <div>
                                <h1 className="text-h4 font-semibold">Your Documents</h1>
                                <p className="text-caption text-surface-500 hidden sm:block">
                                    Upload files for the AI to learn from
                                </p>
                            </div>
                        </div>
                    </div>

                    <button
                        onClick={() => setShowUploadModal(true)}
                        disabled={isUploading}
                        className="btn-primary"
                    >
                        {isUploading ? (
                            <Loader2 className="w-4 h-4 animate-spin" />
                        ) : (
                            <Upload className="w-4 h-4" />
                        )}
                        <span className="hidden sm:inline">Add Files</span>
                        <span className="sm:hidden">Add</span>
                    </button>
                </div>
            </header>

            <main className="max-w-6xl mx-auto px-4 py-8">
                {/* Help tip */}
                <div className="mb-6 p-4 rounded-xl bg-primary-500/5 border border-primary-200/50 dark:border-primary-800/50">
                    <div className="flex items-start gap-3">
                        <HelpCircle className="w-5 h-5 text-primary-500 flex-shrink-0 mt-0.5" />
                        <div>
                            <p className="text-body-sm text-surface-700 dark:text-surface-300">
                                <strong>How it works:</strong> Upload your documents (PDF, Word, Markdown, or text files).
                                Our AI will read and understand them so you can ask questions in the chat.
                            </p>
                        </div>
                    </div>
                </div>

                {/* Search */}
                <div className="mb-6">
                    <div className="relative max-w-md">
                        <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-surface-400" />
                        <input
                            type="text"
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            placeholder="Find a document..."
                            className="input pl-12"
                            aria-label="Search documents"
                        />
                    </div>
                </div>

                {/* Stats - simplified labels */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
                    {[
                        { label: 'Total Files', value: documents.length, icon: FileText },
                        { label: 'Text Sections', value: documents.reduce((acc, d) => acc + d.chunks, 0), icon: CheckCircle },
                        { label: 'Ready to Use', value: documents.filter(d => d.status === 'ready').length, icon: CheckCircle },
                        { label: 'Processing', value: documents.filter(d => d.status === 'processing').length, icon: Loader2 },
                    ].map((stat, i) => (
                        <div key={i} className="card p-4">
                            <div className="flex items-center gap-2 mb-1">
                                <stat.icon className="w-4 h-4 text-surface-400" />
                                <p className="text-caption text-surface-500">{stat.label}</p>
                            </div>
                            <p className="text-h3 gradient-text">{stat.value}</p>
                        </div>
                    ))}
                </div>

                {/* Document List */}
                {filteredDocs.length === 0 ? (
                    <div className="card p-12 text-center">
                        <FolderOpen className="w-12 h-12 text-surface-400 mx-auto mb-4" />
                        <h3 className="text-h4 mb-2">
                            {searchQuery ? 'No matching documents' : 'No documents yet'}
                        </h3>
                        <p className="text-body text-surface-500 mb-6">
                            {searchQuery
                                ? 'Try a different search term'
                                : 'Upload your first file to get started. The AI will learn from it!'}
                        </p>
                        {!searchQuery && (
                            <button onClick={() => setShowUploadModal(true)} className="btn-primary">
                                <Upload className="w-4 h-4" />
                                Upload Your First File
                            </button>
                        )}
                    </div>
                ) : (
                    <div className="space-y-3">
                        {filteredDocs.map((doc) => (
                            <div
                                key={doc.id}
                                className="card-hover p-4 flex items-center justify-between group"
                            >
                                <div className="flex items-center gap-4 min-w-0">
                                    <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-500/10 to-accent-500/10 flex items-center justify-center flex-shrink-0">
                                        <FileText className="w-5 h-5 text-primary-500" />
                                    </div>
                                    <div className="min-w-0">
                                        <h3 className="text-body font-medium truncate">{doc.name}</h3>
                                        <div className="flex items-center gap-3 text-caption text-surface-500">
                                            <span>{doc.chunks} sections</span>
                                            <span>•</span>
                                            <span>{doc.size}</span>
                                            <span className="hidden sm:inline">•</span>
                                            <span className="hidden sm:inline">{doc.uploadedAt}</span>
                                        </div>
                                    </div>
                                </div>

                                <div className="flex items-center gap-2 flex-shrink-0">
                                    {/* Status badge with friendly labels */}
                                    <span className={`px-2.5 py-1 rounded-full text-caption font-medium ${doc.status === 'ready'
                                            ? 'bg-green-500/10 text-green-600 dark:text-green-400'
                                            : doc.status === 'processing'
                                                ? 'bg-yellow-500/10 text-yellow-600 dark:text-yellow-400'
                                                : 'bg-red-500/10 text-red-600 dark:text-red-400'
                                        }`}>
                                        {doc.status === 'ready' && '✓ Ready'}
                                        {doc.status === 'processing' && 'Processing...'}
                                        {doc.status === 'error' && 'Error'}
                                    </span>

                                    {/* Action buttons - always visible on mobile, hover on desktop */}
                                    <div className="flex items-center gap-1 sm:opacity-0 sm:group-hover:opacity-100 transition-opacity">
                                        <button
                                            onClick={() => setPreviewDoc(doc)}
                                            className="btn-ghost p-2"
                                            title="Preview document"
                                            aria-label="Preview document"
                                        >
                                            <Eye className="w-4 h-4" />
                                        </button>
                                        <button
                                            onClick={() => setDeleteConfirm(doc.id)}
                                            className="btn-ghost p-2 text-red-500 hover:bg-red-500/10"
                                            title="Delete document"
                                            aria-label="Delete document"
                                        >
                                            <Trash2 className="w-4 h-4" />
                                        </button>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </main>

            {/* Upload Modal */}
            {showUploadModal && (
                <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
                    <div
                        className="absolute inset-0 bg-surface-950/50 backdrop-blur-sm"
                        onClick={() => setShowUploadModal(false)}
                    />
                    <div className="card p-6 w-full max-w-md relative animate-in z-10">
                        <button
                            onClick={() => setShowUploadModal(false)}
                            className="absolute top-4 right-4 btn-ghost p-2"
                            aria-label="Close"
                        >
                            <X className="w-5 h-5" />
                        </button>

                        <h2 className="text-h3 mb-2">Add Documents</h2>
                        <p className="text-body-sm text-surface-500 mb-6">
                            Upload files for the AI to learn from. We support PDF, Word, Markdown, and text files.
                        </p>

                        {/* Drop zone */}
                        <div
                            onClick={() => fileInputRef.current?.click()}
                            className="border-2 border-dashed border-surface-300 dark:border-surface-600 rounded-2xl p-8 text-center cursor-pointer hover:border-primary-500 hover:bg-primary-500/5 transition-colors"
                        >
                            <Upload className="w-10 h-10 text-surface-400 mx-auto mb-3" />
                            <p className="text-body font-medium mb-1">Click to browse files</p>
                            <p className="text-caption text-surface-500">
                                or drag and drop here
                            </p>
                            <p className="text-caption text-surface-400 mt-3">
                                PDF, DOCX, MD, TXT up to 10MB
                            </p>
                        </div>

                        <div className="mt-6 flex justify-end gap-3">
                            <button onClick={() => setShowUploadModal(false)} className="btn-secondary">
                                Cancel
                            </button>
                            <button onClick={() => fileInputRef.current?.click()} className="btn-primary">
                                <Upload className="w-4 h-4" />
                                Choose Files
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Delete Confirmation Modal */}
            {deleteConfirm && (
                <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
                    <div
                        className="absolute inset-0 bg-surface-950/50 backdrop-blur-sm"
                        onClick={() => setDeleteConfirm(null)}
                    />
                    <div className="card p-6 w-full max-w-sm relative animate-in z-10">
                        <div className="flex items-center gap-3 mb-4">
                            <div className="w-10 h-10 rounded-full bg-red-500/10 flex items-center justify-center">
                                <AlertTriangle className="w-5 h-5 text-red-500" />
                            </div>
                            <div>
                                <h3 className="text-h4">Delete Document?</h3>
                                <p className="text-caption text-surface-500">This can't be undone</p>
                            </div>
                        </div>

                        <p className="text-body text-surface-600 dark:text-surface-400 mb-6">
                            The AI will no longer be able to answer questions from this document.
                        </p>

                        <div className="flex justify-end gap-3">
                            <button onClick={() => setDeleteConfirm(null)} className="btn-secondary">
                                Keep It
                            </button>
                            <button
                                onClick={() => handleDelete(deleteConfirm)}
                                className="btn bg-red-500 hover:bg-red-600 text-white"
                            >
                                <Trash2 className="w-4 h-4" />
                                Delete
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Preview Modal */}
            {previewDoc && (
                <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
                    <div
                        className="absolute inset-0 bg-surface-950/50 backdrop-blur-sm"
                        onClick={() => setPreviewDoc(null)}
                    />
                    <div className="card p-6 w-full max-w-lg relative animate-in z-10">
                        <button
                            onClick={() => setPreviewDoc(null)}
                            className="absolute top-4 right-4 btn-ghost p-2"
                            aria-label="Close"
                        >
                            <X className="w-5 h-5" />
                        </button>

                        <div className="flex items-center gap-4 mb-6">
                            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-primary-500/20 to-accent-500/20 flex items-center justify-center">
                                <FileText className="w-6 h-6 text-primary-500" />
                            </div>
                            <div>
                                <h2 className="text-h4">{previewDoc.name}</h2>
                                <p className="text-caption text-surface-500">
                                    Uploaded {previewDoc.uploadedAt}
                                </p>
                            </div>
                        </div>

                        <div className="space-y-3">
                            <div className="flex justify-between py-2 border-b border-surface-200 dark:border-surface-700">
                                <span className="text-surface-500">File Size</span>
                                <span className="font-medium">{previewDoc.size}</span>
                            </div>
                            <div className="flex justify-between py-2 border-b border-surface-200 dark:border-surface-700">
                                <span className="text-surface-500">Text Sections</span>
                                <span className="font-medium">{previewDoc.chunks} sections</span>
                            </div>
                            <div className="flex justify-between py-2 border-b border-surface-200 dark:border-surface-700">
                                <span className="text-surface-500">Status</span>
                                <span className={`font-medium ${previewDoc.status === 'ready' ? 'text-green-500' :
                                        previewDoc.status === 'processing' ? 'text-yellow-500' : 'text-red-500'
                                    }`}>
                                    {previewDoc.status === 'ready' ? 'Ready to use' :
                                        previewDoc.status === 'processing' ? 'Still processing...' : 'Error occurred'}
                                </span>
                            </div>
                        </div>

                        <div className="mt-6 flex justify-end">
                            <button onClick={() => setPreviewDoc(null)} className="btn-primary">
                                Done
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}

const mockDocuments: Document[] = [
    { id: '1', name: 'langchain_documentation.pdf', chunks: 42, uploadedAt: '2 hours ago', size: '2.4 MB', status: 'ready' },
    { id: '2', name: 'aws_bedrock_guide.md', chunks: 28, uploadedAt: '1 day ago', size: '156 KB', status: 'ready' },
    { id: '3', name: 'langgraph_tutorial.pdf', chunks: 35, uploadedAt: '3 days ago', size: '1.8 MB', status: 'ready' },
    { id: '4', name: 'qdrant_architecture.md', chunks: 0, uploadedAt: 'Just now', size: '89 KB', status: 'processing' },
];
