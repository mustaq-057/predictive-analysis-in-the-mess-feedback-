"use client";

import React, { useEffect, useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, AreaChart, Area } from 'recharts';
import { Users, Star, AlertCircle, TrendingUp, TrendingDown, Utensils, ThumbsUp, ThumbsDown, Sparkles } from 'lucide-react';
import { cn } from '@/lib/utils';

interface FoodItemStat {
    item: string;
    good: number;
    bad: number;
    reviews: string[];
}

interface WeeklyTrend {
    name: string;
    positive: number;
    negative: number;
    amt: number;
}

interface AnalyticsData {
    summary: string;
    stats: {
        totalReviews: number;
        averageRating: string;
        goodReviews: number;
        badReviews: number;
        mealTypeBreakdown: {
            breakfast: number;
            lunch: number;
            dinner: number;
        };
    };
    foodItemStats: FoodItemStat[];
    weeklyTrends: WeeklyTrend[];
}

export default function AdminDashboard() {
    const [data, setData] = useState<AnalyticsData | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const res = await fetch('/api/analyze', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ limit: 100 }) // Analyze last 100 reviews
                });
                const json = await res.json();
                if (json.success) {
                    setData(json.data);
                }
            } catch (error) {
                console.error('Failed to fetch analytics:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, []);

    if (loading) {
        return <div className="p-8 text-center text-gray-500">Loading analytics...</div>;
    }

    const criticalItems = data?.foodItemStats.filter(i => i.bad > i.good).slice(0, 5) || [];
    const goodItems = data?.foodItemStats.filter(i => i.good >= i.bad).slice(0, 5) || [];
    const chartData = data?.weeklyTrends || [];

    return (
        <div className="space-y-8 animate-fade-in">
            <div className="flex justify-between items-center">
                <h1 className="text-2xl font-bold text-gray-900">Analytics Dashboard</h1>
                <div className="text-sm text-gray-500">Last updated: Just now</div>
            </div>

            {/* Stats Overview */}
            <div className="grid grid-cols-1 gap-6 sm:grid-cols-3">
                <StatsCard
                    title="Total Reviews"
                    value={data?.stats?.totalReviews?.toString() || "0"}
                    change=""
                    trend="neutral"
                    icon={<Users className="h-6 w-6 text-indigo-600" />}
                    color="indigo"
                />
                <StatsCard
                    title="Avg. Rating"
                    value={data?.stats?.averageRating || "0.0"}
                    change=""
                    trend="neutral"
                    icon={<Star className="h-6 w-6 text-yellow-600" />}
                    color="yellow"
                />
                <StatsCard
                    title="Critical Issues"
                    value={criticalItems.length.toString()}
                    change=""
                    trend="neutral"
                    icon={<AlertCircle className="h-6 w-6 text-red-600" />}
                    color="red"
                />
            </div>

            {/* AI Insights Section */}
            <div className="bg-gradient-to-r from-indigo-50 to-purple-50 rounded-3xl p-8 border border-indigo-100 shadow-sm">
                <div className="flex items-start gap-4">
                    <div className="p-3 bg-white rounded-2xl shadow-sm">
                        <Sparkles className="h-6 w-6 text-indigo-600" />
                    </div>
                    <div className="space-y-2">
                        <h3 className="text-lg font-bold text-gray-900">AI Summary & Suggestions</h3>
                        <div className="text-gray-700 whitespace-pre-line leading-relaxed">
                            {data?.summary || "No enough data to generate summary."}
                        </div>
                    </div>
                </div>
            </div>

            {/* Food Item Analysis */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Critical Issues */}
                <div className="bg-white shadow-sm border border-red-100 rounded-3xl p-8">
                    <div className="flex items-center gap-3 mb-6">
                        <div className="p-2 bg-red-50 rounded-xl">
                            <ThumbsDown className="h-5 w-5 text-red-600" />
                        </div>
                        <h3 className="text-lg font-bold text-gray-900">Critical Issues (Fix Immediately)</h3>
                    </div>
                    <div className="space-y-4">
                        {criticalItems.length > 0 ? (
                            criticalItems.map((item) => (
                                <div key={item.item} className="p-4 bg-red-50/50 rounded-2xl border border-red-100">
                                    <div className="flex justify-between items-center mb-2">
                                        <span className="font-bold text-gray-900 capitalize">{item.item}</span>
                                        <span className="text-sm font-medium text-red-600">{item.bad} Complaints</span>
                                    </div>
                                    <div className="text-sm text-gray-600 italic truncate">
                                        {item.reviews[0]}
                                    </div>
                                </div>
                            ))
                        ) : (
                            <div className="text-center text-gray-500 py-8">No critical issues found! 🎉</div>
                        )}
                    </div>
                </div>

                {/* Doing Well */}
                <div className="bg-white shadow-sm border border-green-100 rounded-3xl p-8">
                    <div className="flex items-center gap-3 mb-6">
                        <div className="p-2 bg-green-50 rounded-xl">
                            <ThumbsUp className="h-5 w-5 text-green-600" />
                        </div>
                        <h3 className="text-lg font-bold text-gray-900">Doing Well (Keep it up)</h3>
                    </div>
                    <div className="space-y-4">
                        {goodItems.length > 0 ? (
                            goodItems.map((item) => (
                                <div key={item.item} className="p-4 bg-green-50/50 rounded-2xl border border-green-100">
                                    <div className="flex justify-between items-center mb-2">
                                        <span className="font-bold text-gray-900 capitalize">{item.item}</span>
                                        <span className="text-sm font-medium text-green-600">{item.good} Likes</span>
                                    </div>
                                    <div className="w-full bg-gray-100 rounded-full h-2">
                                        <div
                                            className="bg-green-500 h-2 rounded-full"
                                            style={{ width: `${(item.good / (item.good + item.bad)) * 100}%` }}
                                        />
                                    </div>
                                </div>
                            ))
                        ) : (
                            <div className="text-center text-gray-500 py-8">No data available yet.</div>
                        )}
                    </div>
                </div>
            </div>

            {/* Charts */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                <div className="bg-white shadow-sm border border-gray-100 rounded-3xl p-8 hover:shadow-md transition-shadow">
                    <h3 className="text-lg font-bold text-gray-900 mb-6">Weekly Feedback Trends</h3>
                    <div className="h-80">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={chartData} margin={{ top: 5, right: 10, left: -20, bottom: 5 }}>
                                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                                <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fill: '#64748b', fontSize: 12 }} dy={10} />
                                <YAxis axisLine={false} tickLine={false} tick={{ fill: '#64748b', fontSize: 12 }} />
                                <Tooltip contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }} cursor={{ fill: '#f8fafc' }} />
                                <Legend wrapperStyle={{ paddingTop: '20px' }} />
                                <Bar dataKey="positive" fill="#6366f1" name="Positive" radius={[4, 4, 0, 0]} barSize={30} />
                                <Bar dataKey="negative" fill="#ef4444" name="Negative" radius={[4, 4, 0, 0]} barSize={30} />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                <div className="bg-white shadow-sm border border-gray-100 rounded-3xl p-8 hover:shadow-md transition-shadow">
                    <h3 className="text-lg font-bold text-gray-900 mb-6">Rating Distribution</h3>
                    <div className="h-80">
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={chartData} margin={{ top: 5, right: 10, left: -20, bottom: 5 }}>
                                <defs>
                                    <linearGradient id="colorPositive" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.3} />
                                        <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0} />
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                                <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fill: '#64748b', fontSize: 12 }} dy={10} />
                                <YAxis axisLine={false} tickLine={false} tick={{ fill: '#64748b', fontSize: 12 }} />
                                <Tooltip contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }} />
                                <Legend wrapperStyle={{ paddingTop: '20px' }} />
                                <Area type="monotone" dataKey="positive" stroke="#8b5cf6" strokeWidth={3} fillOpacity={1} fill="url(#colorPositive)" name="Satisfaction Score" />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            </div>
        </div>
    );
}

function StatsCard({ title, value, change, trend, icon, color }: { title: string, value: string, change: string, trend: 'up' | 'down' | 'neutral', icon: React.ReactNode, color: string }) {
    const colorStyles = {
        indigo: "bg-indigo-50 text-indigo-600",
        yellow: "bg-yellow-50 text-yellow-600",
        red: "bg-red-50 text-red-600",
    };

    return (
        <div className="bg-white overflow-hidden shadow-sm border border-gray-100 rounded-3xl p-6 hover:shadow-md transition-all duration-300">
            <div className="flex items-center">
                <div className={cn("p-3 rounded-2xl", colorStyles[color as keyof typeof colorStyles])}>
                    {icon}
                </div>
                <div className="ml-5 w-0 flex-1">
                    <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">{title}</dt>
                        <dd>
                            <div className="flex items-baseline">
                                <div className="text-2xl font-bold text-gray-900">{value}</div>
                                {change && (
                                    <div className={cn(
                                        "ml-2 flex items-baseline text-sm font-semibold",
                                        trend === 'up' ? "text-green-600" : trend === 'down' ? "text-red-600" : "text-gray-500"
                                    )}>
                                        {trend === 'up' && <TrendingUp className="self-center flex-shrink-0 h-4 w-4 text-green-500" aria-hidden="true" />}
                                        {trend === 'down' && <TrendingDown className="self-center flex-shrink-0 h-4 w-4 text-red-500" aria-hidden="true" />}
                                        <span className="sr-only">{trend === 'up' ? 'Increased' : trend === 'down' ? 'Decreased' : 'Change'} by</span>
                                        {change}
                                    </div>
                                )}
                            </div>
                        </dd>
                    </dl>
                </div>
            </div>
        </div>
    );
}
