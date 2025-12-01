"use client";

import React, { useState, useEffect } from 'react';
import { cn } from '@/lib/utils';
import { Clock, ThumbsUp, ThumbsDown, MessageSquare, Loader2 } from 'lucide-react';

export default function HistoryPage() {
    const [reviews, setReviews] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchReviews();
    }, []);

    const fetchReviews = async () => {
        try {
            const res = await fetch('/api/reviews');
            const data = await res.json();
            if (data.success) {
                setReviews(data.data);
            }
        } catch (error) {
            console.error('Error fetching reviews:', error);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-96">
                <Loader2 className="h-8 w-8 animate-spin text-indigo-600" />
            </div>
        );
    }

    return (
        <div className="space-y-6">
            <div className="bg-white shadow rounded-lg p-6">
                <h1 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
                    <Clock className="mr-2 h-6 w-6 text-indigo-600" />
                    Your Feedback History
                </h1>

                {reviews.length === 0 ? (
                    <div className="text-center py-12">
                        <p className="text-gray-500">No feedback submitted yet.</p>
                    </div>
                ) : (
                    <div className="flow-root">
                        <ul className="-my-5 divide-y divide-gray-200">
                            {reviews.map((item) => (
                                <li key={item._id} className="py-5">
                                    <div className="relative focus-within:ring-2 focus-within:ring-indigo-500">
                                        <h3 className="text-sm font-semibold text-gray-800">
                                            <span className="absolute inset-0" aria-hidden="true" />
                                            {item.mealType}
                                        </h3>
                                        <p className="text-sm text-gray-600 line-clamp-2 mt-1">
                                            {item.review}
                                        </p>
                                        <div className="mt-2 flex items-center space-x-4">
                                            <div className="flex items-center text-sm text-gray-500">
                                                <span className="font-medium mr-1">Rating:</span>
                                                <span className={cn(
                                                    "font-bold",
                                                    item.rating >= 4 ? "text-green-600" : item.rating >= 3 ? "text-yellow-600" : "text-red-600"
                                                )}>
                                                    {item.rating}/5
                                                </span>
                                            </div>
                                            <div className="flex items-center text-sm">
                                                {/* Sentiment hidden for students */}
                                            </div>
                                        </div>
                                        <div className="mt-2 flex items-center justify-between">
                                            <div className="text-xs text-gray-400">
                                                {new Date(item.createdAt).toLocaleDateString()}
                                            </div>
                                        </div>
                                    </div>
                                </li>
                            ))}
                        </ul>
                    </div>
                )}
            </div>
        </div>
    );
}
