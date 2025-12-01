"use client";

import React, { useState, useEffect } from 'react';
import { cn } from '@/lib/utils';
import { AlertTriangle, Filter, Search, Sparkles, ThumbsUp, ThumbsDown } from 'lucide-react';

export default function ReviewsPage() {
    const [filter, setFilter] = useState<'all' | 'good' | 'bad'>('all');
    const [reviews, setReviews] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [analysis, setAnalysis] = useState<any>(null);

    useEffect(() => {
        fetchReviews();
    }, []);

    const fetchReviews = async () => {
        try {
            const res = await fetch('/api/reviews');
            const data = await res.json();
            if (data.success) {
                setReviews(data.data);
                // Generate summary if we have reviews
                if (data.data.length > 0) {
                    generateAnalysis(data.data);
                }
            }
        } catch (error) {
            console.error('Error fetching reviews:', error);
        } finally {
            setLoading(false);
        }
    };

    const generateAnalysis = async (reviewsData: any[]) => {
        try {
            const res = await fetch('/api/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    reviews: reviewsData.map(r => ({
                        review: r.review,
                        rating: r.rating,
                        mealType: r.mealType
                    }))
                })
            });
            const data = await res.json();
            if (data.success) {
                setAnalysis(data.analysis);
            }
        } catch (error) {
            console.error('Error generating analysis:', error);
        }
    };

    const handleCorrection = async (id: string, correctSentiment: 'good' | 'bad') => {
        try {
            // Optimistic update
            setReviews(prev => prev.map(r =>
                r._id === id ? { ...r, sentiment: correctSentiment } : r
            ));

            const res = await fetch(`/api/reviews/${id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ sentiment: correctSentiment })
            });

            if (!res.ok) {
                throw new Error('Failed to update sentiment');
            }

            // Refresh to ensure sync
            fetchReviews();
        } catch (error) {
            console.error('Error correcting sentiment:', error);
            // Revert on error would go here, but fetchReviews handles sync
            fetchReviews();
        }
    };

    const filteredReviews = reviews.filter(r => {
        if (filter === 'all') return true;
        return r.sentiment === filter;
    });

    if (loading) return (
        <div className="flex items-center justify-center h-96">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
        </div>
    );

    return (
        <div className="space-y-8 animate-fade-in">
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900">Review Management</h1>
                    <p className="text-gray-500 text-sm mt-1">Monitor and analyze student feedback</p>
                </div>

                <div className="flex items-center space-x-3 bg-white p-1 rounded-xl border border-gray-200 shadow-sm">
                    <button
                        onClick={() => setFilter('all')}
                        className={cn(
                            "px-4 py-2 text-sm font-medium rounded-lg transition-all",
                            filter === 'all' ? "bg-gray-100 text-gray-900" : "text-gray-500 hover:text-gray-700"
                        )}
                    >
                        All
                    </button>
                    <button
                        onClick={() => setFilter('good')}
                        className={cn(
                            "px-4 py-2 text-sm font-medium rounded-lg transition-all flex items-center",
                            filter === 'good' ? "bg-green-50 text-green-700" : "text-gray-500 hover:text-gray-700"
                        )}
                    >
                        <ThumbsUp className="w-3 h-3 mr-2" /> Positive
                    </button>
                    <button
                        onClick={() => setFilter('bad')}
                        className={cn(
                            "px-4 py-2 text-sm font-medium rounded-lg transition-all flex items-center",
                            filter === 'bad' ? "bg-red-50 text-red-700" : "text-gray-500 hover:text-gray-700"
                        )}
                    >
                        <ThumbsDown className="w-3 h-3 mr-2" /> Negative
                    </button>
                </div>
            </div>

            {/* AI Insights */}
            {analysis && (
                <div className="bg-gradient-to-r from-indigo-50 to-purple-50 border border-indigo-100 rounded-3xl p-6 relative overflow-hidden">
                    <div className="absolute top-0 right-0 w-32 h-32 bg-indigo-100 rounded-full -mr-10 -mt-10 opacity-50 blur-xl"></div>
                    <div className="flex relative z-10">
                        <div className="flex-shrink-0 p-3 bg-white rounded-2xl shadow-sm h-fit">
                            <Sparkles className="h-6 w-6 text-indigo-600" aria-hidden="true" />
                        </div>
                        <div className="ml-5">
                            <h3 className="text-lg font-bold text-gray-900">AI Analysis Summary</h3>
                            <div className="mt-2 text-gray-700 leading-relaxed">
                                <p>{analysis}</p>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* Reviews Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                {filteredReviews.map((review) => (
                    <div key={review._id} className="bg-white rounded-3xl shadow-sm border border-gray-100 p-6 hover:shadow-md transition-all duration-300 flex flex-col h-full group">
                        <div className="flex justify-between items-start mb-4">
                            <div className="flex items-center space-x-2">
                                <span className={cn(
                                    "px-3 py-1 text-xs font-bold rounded-full uppercase tracking-wide transition-colors",
                                    review.sentiment === 'good' ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"
                                )}>
                                    {review.sentiment}
                                </span>
                                <span className="text-xs text-gray-400 font-medium">
                                    {new Date(review.createdAt).toLocaleDateString()}
                                </span>
                            </div>
                            <div className="flex items-center bg-gray-50 px-2 py-1 rounded-lg">
                                <span className="text-sm font-bold text-gray-900 mr-1">{review.rating}</span>
                                <span className="text-yellow-400 text-sm">★</span>
                            </div>
                        </div>

                        <div className="mb-3">
                            <div className="flex items-center justify-between mb-2">
                                <h4 className="text-sm font-semibold text-gray-900 capitalize">{review.mealType}</h4>
                                {review.studentName && (
                                    <span className="text-xs text-gray-500">{review.studentName}</span>
                                )}
                            </div>

                            {/* Food Items */}
                            {review.foodItems && review.foodItems.length > 0 && (
                                <div className="flex flex-wrap gap-1.5 mb-3">
                                    {review.foodItems.map((item: string, idx: number) => (
                                        <span key={idx} className="text-xs bg-indigo-50 text-indigo-700 px-2 py-1 rounded-full font-medium">
                                            {item}
                                        </span>
                                    ))}
                                </div>
                            )}

                            {/* Review Text */}
                            <p className="text-gray-600 text-sm leading-relaxed line-clamp-3 mb-3">
                                "{review.review}"
                            </p>

                            {/* Image Description */}
                            {review.imageDescription && (
                                <div className="bg-purple-50 border border-purple-100 rounded-lg p-2 mb-3">
                                    <p className="text-xs text-purple-700 font-medium mb-1">📷 Image Description:</p>
                                    <p className="text-xs text-purple-600 italic">"{review.imageDescription}"</p>
                                </div>
                            )}
                        </div>

                        {/* Detailed Ratings */}
                        {review.detailedRatings && (
                            <div className="mb-4 pb-4 border-b border-gray-100">
                                <p className="text-xs font-semibold text-gray-700 mb-2">Detailed Ratings:</p>
                                <div className="grid grid-cols-2 gap-2">
                                    {review.detailedRatings.spice && (
                                        <div className="flex items-center justify-between text-xs bg-gray-50 px-2 py-1.5 rounded-lg">
                                            <span className="text-gray-600">Spice</span>
                                            <span className="font-bold text-indigo-600">{review.detailedRatings.spice}/5</span>
                                        </div>
                                    )}
                                    {review.detailedRatings.taste && (
                                        <div className="flex items-center justify-between text-xs bg-gray-50 px-2 py-1.5 rounded-lg">
                                            <span className="text-gray-600">Taste</span>
                                            <span className={cn(
                                                "font-bold",
                                                review.detailedRatings.taste <= 2 ? "text-red-600" : review.detailedRatings.taste >= 4 ? "text-green-600" : "text-gray-600"
                                            )}>{review.detailedRatings.taste}/5</span>
                                        </div>
                                    )}
                                    {review.detailedRatings.freshness && (
                                        <div className="flex items-center justify-between text-xs bg-gray-50 px-2 py-1.5 rounded-lg">
                                            <span className="text-gray-600">Freshness</span>
                                            <span className={cn(
                                                "font-bold",
                                                review.detailedRatings.freshness <= 2 ? "text-red-600" : review.detailedRatings.freshness >= 4 ? "text-green-600" : "text-gray-600"
                                            )}>{review.detailedRatings.freshness}/5</span>
                                        </div>
                                    )}
                                    {review.detailedRatings.hygiene && (
                                        <div className="flex items-center justify-between text-xs bg-gray-50 px-2 py-1.5 rounded-lg">
                                            <span className="text-gray-600">Hygiene</span>
                                            <span className={cn(
                                                "font-bold",
                                                review.detailedRatings.hygiene <= 2 ? "text-red-600" : review.detailedRatings.hygiene >= 4 ? "text-green-600" : "text-gray-600"
                                            )}>{review.detailedRatings.hygiene}/5</span>
                                        </div>
                                    )}
                                    {review.detailedRatings.staff && (
                                        <div className="flex items-center justify-between text-xs bg-gray-50 px-2 py-1.5 rounded-lg">
                                            <span className="text-gray-600">Staff</span>
                                            <span className={cn(
                                                "font-bold",
                                                review.detailedRatings.staff <= 2 ? "text-red-600" : review.detailedRatings.staff >= 4 ? "text-green-600" : "text-gray-600"
                                            )}>{review.detailedRatings.staff}/5</span>
                                        </div>
                                    )}
                                </div>
                            </div>
                        )}

                        {/* Correction Controls - Visible on Hover/Focus */}
                        <div className="mt-auto pt-4 border-t border-gray-50 flex justify-between items-center opacity-0 group-hover:opacity-100 transition-opacity">
                            <span className="text-xs text-gray-400">Correct if wrong:</span>
                            <div className="flex space-x-2">
                                <button
                                    onClick={() => handleCorrection(review._id, 'good')}
                                    disabled={review.sentiment === 'good'}
                                    className={cn(
                                        "p-1.5 rounded-full transition-colors",
                                        review.sentiment === 'good'
                                            ? "bg-green-100 text-green-600 cursor-default"
                                            : "bg-gray-100 text-gray-400 hover:bg-green-100 hover:text-green-600"
                                    )}
                                    title="Mark as Positive"
                                >
                                    <ThumbsUp className="w-3.5 h-3.5" />
                                </button>
                                <button
                                    onClick={() => handleCorrection(review._id, 'bad')}
                                    disabled={review.sentiment === 'bad'}
                                    className={cn(
                                        "p-1.5 rounded-full transition-colors",
                                        review.sentiment === 'bad'
                                            ? "bg-red-100 text-red-600 cursor-default"
                                            : "bg-gray-100 text-gray-400 hover:bg-red-100 hover:text-red-600"
                                    )}
                                    title="Mark as Negative"
                                >
                                    <ThumbsDown className="w-3.5 h-3.5" />
                                </button>
                            </div>
                        </div>

                        {review.aiAnalysis && (
                            <div className="mt-2">
                                <div className="flex items-start space-x-2">
                                    <Sparkles className="h-3 w-3 text-indigo-400 mt-0.5 flex-shrink-0" />
                                    <p className="text-xs text-indigo-600 italic line-clamp-2">
                                        {review.aiAnalysis}
                                    </p>
                                </div>
                            </div>
                        )}
                    </div>
                ))}
            </div>

            {filteredReviews.length === 0 && (
                <div className="text-center py-20 bg-gray-50 rounded-3xl border border-dashed border-gray-200">
                    <div className="mx-auto h-12 w-12 text-gray-300 mb-4">
                        <Search className="h-full w-full" />
                    </div>
                    <h3 className="text-lg font-medium text-gray-900">No reviews found</h3>
                    <p className="text-gray-500 mt-1">Try adjusting your filters or check back later.</p>
                </div>
            )}
        </div>
    );
}
