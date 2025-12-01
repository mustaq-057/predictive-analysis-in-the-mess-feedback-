import React from 'react';
import Link from 'next/link';
import { LayoutDashboard, MessageSquare, Menu as MenuIcon, Settings } from 'lucide-react';

export default function AdminLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <div className="min-h-screen bg-gray-100 flex">
            {/* Sidebar */}
            <div className="hidden md:flex md:w-64 md:flex-col md:fixed md:inset-y-0 bg-gray-900 text-white">
                <div className="flex-1 flex flex-col min-h-0">
                    <div className="flex items-center h-16 flex-shrink-0 px-4 bg-gray-900 font-bold text-xl">
                        Mess Admin
                    </div>
                    <div className="flex-1 flex flex-col overflow-y-auto">
                        <nav className="flex-1 px-2 py-4 space-y-1">
                            <Link href="/admin" className="group flex items-center px-2 py-2 text-sm font-medium rounded-md text-white hover:bg-gray-700">
                                <LayoutDashboard className="mr-3 h-6 w-6 text-gray-300" />
                                Dashboard
                            </Link>
                            <Link href="/admin/reviews" className="group flex items-center px-2 py-2 text-sm font-medium rounded-md text-gray-300 hover:bg-gray-700 hover:text-white">
                                <MessageSquare className="mr-3 h-6 w-6 text-gray-400 group-hover:text-gray-300" />
                                Reviews
                            </Link>
                            <Link href="/admin/menu" className="group flex items-center px-2 py-2 text-sm font-medium rounded-md text-gray-300 hover:bg-gray-700 hover:text-white">
                                <MenuIcon className="mr-3 h-6 w-6 text-gray-400 group-hover:text-gray-300" />
                                Menu Manager
                            </Link>
                        </nav>
                    </div>
                </div>
            </div>

            {/* Main content */}
            <div className="md:pl-64 flex flex-col flex-1">
                <main className="flex-1">
                    <div className="py-6">
                        <div className="max-w-7xl mx-auto px-4 sm:px-6 md:px-8">
                            {children}
                        </div>
                    </div>
                </main>
            </div>
        </div>
    );
}
