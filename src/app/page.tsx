import Link from 'next/link';
import { GraduationCap, ShieldCheck, UtensilsCrossed, ChefHat } from 'lucide-react';

export default function Home() {
    return (
        <div className="min-h-screen bg-gradient-to-br from-indigo-50 to-purple-50 flex flex-col relative overflow-hidden">
            {/* Background Decoration */}
            <div className="absolute top-0 left-0 w-full h-full overflow-hidden z-0 pointer-events-none">
                <div className="absolute -top-24 -left-24 w-96 h-96 bg-indigo-200 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-blob"></div>
                <div className="absolute top-0 -right-4 w-96 h-96 bg-purple-200 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-blob animate-delay-200"></div>
                <div className="absolute -bottom-8 left-20 w-96 h-96 bg-pink-200 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-blob animate-delay-400"></div>
            </div>

            <main className="flex-1 flex flex-col items-center justify-center p-6 relative z-10">
                <div className="text-center mb-16 animate-fade-in">
                    <div className="inline-flex items-center justify-center p-3 bg-white rounded-2xl shadow-lg mb-6 transform rotate-3 hover:rotate-0 transition-transform duration-300">
                        <UtensilsCrossed className="h-10 w-10 text-indigo-600" />
                    </div>
                    <h1 className="text-5xl md:text-7xl font-extrabold text-gray-900 tracking-tight mb-4">
                        Mess <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-purple-600">Feedback</span>
                    </h1>
                    <p className="text-xl text-gray-600 max-w-2xl mx-auto leading-relaxed">
                        Experience dining reimagined. View menus, share your thoughts, and help us create the perfect meal for everyone.
                    </p>
                </div>

                <div className="max-w-5xl w-full grid grid-cols-1 md:grid-cols-2 gap-8 px-4">
                    {/* Student Portal Card */}
                    <Link href="/student" className="group">
                        <div className="bg-white/80 backdrop-blur-lg rounded-3xl shadow-xl border border-white/50 p-8 h-full transform transition-all duration-300 hover:-translate-y-2 hover:shadow-2xl hover:border-indigo-200 flex flex-col items-center text-center cursor-pointer relative overflow-hidden">
                            <div className="absolute inset-0 bg-gradient-to-br from-indigo-50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>

                            <div className="h-24 w-24 bg-indigo-100 rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300 shadow-inner">
                                <GraduationCap className="h-12 w-12 text-indigo-600" />
                            </div>

                            <h2 className="text-3xl font-bold text-gray-900 mb-3 relative">Student Portal</h2>
                            <p className="text-gray-600 mb-8 relative z-10">
                                Check today's menu, rate your meals, and track your feedback history.
                            </p>

                            <span className="mt-auto inline-flex items-center px-8 py-3 border border-transparent text-base font-medium rounded-xl text-white bg-indigo-600 shadow-lg shadow-indigo-200 group-hover:bg-indigo-700 group-hover:shadow-indigo-300 transition-all duration-300 relative z-10">
                                Enter Dashboard
                            </span>
                        </div>
                    </Link>

                    {/* Admin Portal Card */}
                    <Link href="/admin" className="group">
                        <div className="bg-white/80 backdrop-blur-lg rounded-3xl shadow-xl border border-white/50 p-8 h-full transform transition-all duration-300 hover:-translate-y-2 hover:shadow-2xl hover:border-purple-200 flex flex-col items-center text-center cursor-pointer relative overflow-hidden">
                            <div className="absolute inset-0 bg-gradient-to-br from-purple-50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>

                            <div className="h-24 w-24 bg-purple-100 rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300 shadow-inner">
                                <ShieldCheck className="h-12 w-12 text-purple-600" />
                            </div>

                            <h2 className="text-3xl font-bold text-gray-900 mb-3 relative">Admin Portal</h2>
                            <p className="text-gray-600 mb-8 relative z-10">
                                Analyze feedback trends, manage daily menus, and monitor quality.
                            </p>

                            <span className="mt-auto inline-flex items-center px-8 py-3 border border-transparent text-base font-medium rounded-xl text-white bg-purple-600 shadow-lg shadow-purple-200 group-hover:bg-purple-700 group-hover:shadow-purple-300 transition-all duration-300 relative z-10">
                                Access Admin Panel
                            </span>
                        </div>
                    </Link>
                </div>
            </main>

            <footer className="py-6 text-center text-gray-400 text-sm relative z-10">
                <p>2024 Mess Feedback System. Crafted with ❤️ for better food.</p>
            </footer>
        </div>
    );
}
