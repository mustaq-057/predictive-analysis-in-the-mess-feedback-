"use client";

import React, { useState, ChangeEvent, useEffect } from 'react';
import { cn } from '@/lib/utils';
import { Star, Upload, Send, AlertCircle, MessageSquare, Image as ImageIcon, X } from 'lucide-react';

const MESS_TYPES = ['North', 'South'];
const MEAL_TYPES = ['Breakfast', 'Lunch', 'Dinner'];

export default function FeedbackPage() {
    const [mess, setMess] = useState('North');
    const [meal, setMeal] = useState('Lunch');
    const [selectedItems, setSelectedItems] = useState<string[]>([]);
    const [availableItems, setAvailableItems] = useState<any[]>([]);
    const [loadingItems, setLoadingItems] = useState(false);
    const [ratings, setRatings] = useState({
        spice: 3,
        taste: 3,
        freshness: 3,
        hygiene: 3,
        staff: 3,
        overall: 3
    });
    const [feedbackText, setFeedbackText] = useState('');
    const [image, setImage] = useState<string | null>(null);
    const [imageDescription, setImageDescription] = useState('');
    const [isAnonymous, setIsAnonymous] = useState(false);
    const [submitted, setSubmitted] = useState(false);
    const [isDragging, setIsDragging] = useState(false);
    const [error, setError] = useState<string | null>(null);

    // Simple cache to avoid redundant API calls
    const cacheRef = React.useRef<{ [key: string]: any[] }>({});

    useEffect(() => {
        const fetchItems = async () => {
            const cacheKey = `${mess}-${meal}`;

            // Check cache first
            if (cacheRef.current[cacheKey]) {
                setAvailableItems(cacheRef.current[cacheKey]);
                return;
            }

            setLoadingItems(true);
            try {
                // Use IST date explicitly
                const date = new Date().toLocaleDateString('en-CA', { timeZone: 'Asia/Kolkata' });

                const queryParams = new URLSearchParams({
                    date,
                    mealType: meal.toLowerCase(),
                    messType: mess,
                    isAvailable: 'true'
                });

                const res = await fetch(`/api/menu?${queryParams}`);
                const data = await res.json();

                if (data.success && data.data) {
                    setAvailableItems(data.data);
                    cacheRef.current[cacheKey] = data.data; // Cache the result
                } else {
                    setAvailableItems([]);
                }
            } catch (error) {
                console.error('Error fetching menu items:', error);
                setAvailableItems([]);
            } finally {
                setLoadingItems(false);
            }
        };

        fetchItems();
    }, [meal, mess]);

    const handleImageUpload = (e: ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (file) {
            const reader = new FileReader();
            reader.onloadend = () => {
                setImage(reader.result as string);
            };
            reader.readAsDataURL(file);
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError(null);

        // Validate: remarks is required UNLESS (image exists AND imageDescription is provided)
        if (image) {
            // If image exists, must have either remarks OR image description
            if ((!feedbackText || feedbackText.trim().length === 0) && (!imageDescription || imageDescription.trim().length === 0)) {
                setError('Please provide either feedback text or describe the uploaded image.');
                return;
            }
        } else {
            // If no image, remarks is required
            if (!feedbackText || feedbackText.trim().length === 0) {
                setError('Please provide your feedback.');
                return;
            }
        }

        try {
            const res = await fetch('/api/reviews', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    studentName: isAnonymous ? 'Anonymous' : 'Student',
                    studentEmail: isAnonymous ? 'anonymous@example.com' : 'student@example.com',
                    mealType: meal.toLowerCase(),
                    rating: ratings.overall,
                    review: feedbackText,
                    foodImage: image,
                    imageDescription: imageDescription || null,
                    foodItems: selectedItems,
                    detailedRatings: {
                        spice: ratings.spice,
                        taste: ratings.taste,
                        freshness: ratings.freshness,
                        hygiene: ratings.hygiene,
                        staff: ratings.staff
                    },
                    isAnonymous
                })
            });

            const data = await res.json();

            if (res.ok) {
                setSubmitted(true);
                setFeedbackText('');
                setImage(null);
                setImageDescription('');
                setSelectedItems([]);
                setRatings({ spice: 3, taste: 3, freshness: 3, hygiene: 3, staff: 3, overall: 3 });
                setTimeout(() => setSubmitted(false), 3000);
            } else {
                setError(data.error || 'Failed to submit feedback');
            }
        } catch (error) {
            console.error('Error submitting review:', error);
            setError('An unexpected error occurred. Please try again.');
        }
    };

    const toggleItem = (item: string) => {
        setSelectedItems(prev =>
            prev.includes(item) ? prev.filter(i => i !== item) : [...prev, item]
        );
    };

    const handleSelectAll = () => {
        if (selectedItems.length === availableItems.length) {
            setSelectedItems([]);
        } else {
            setSelectedItems(availableItems.map(item => item.name));
        }
    };

    return (
        <div className="max-w-3xl mx-auto animate-fade-in">
            <div className="bg-white shadow-2xl shadow-indigo-200/50 rounded-3xl overflow-hidden border border-indigo-100/50">
                {/* Header */}
                <div className="bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-500 px-8 py-10 text-white relative overflow-hidden">
                    <div className="absolute top-0 right-0 w-96 h-96 bg-white opacity-10 rounded-full -mr-32 -mt-32 blur-3xl animate-pulse"></div>
                    <div className="absolute bottom-0 left-0 w-64 h-64 bg-yellow-300 opacity-10 rounded-full -ml-16 -mb-16 blur-2xl"></div>
                    <div className="relative z-10">
                        <h1 className="text-3xl font-bold mb-2 tracking-tight">Submit Your Feedback</h1>
                        <p className="text-indigo-50 text-lg">Help us improve your dining experience with your valuable insights.</p>
                    </div>
                </div>

                <form onSubmit={handleSubmit} className="p-10 space-y-10">
                    {error && (
                        <div className="bg-red-50 border-2 border-red-200 text-red-700 px-5 py-4 rounded-2xl flex items-center shadow-sm animate-shake">
                            <AlertCircle className="h-5 w-5 mr-2" />
                            {error}
                        </div>
                    )}

                    {/* Mess & Meal Selection */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div className="space-y-2">
                            <label className="text-sm font-semibold text-gray-700">Select Mess</label>
                            <div className="flex bg-gray-50 p-1.5 rounded-xl border border-gray-200">
                                {MESS_TYPES.map(type => (
                                    <button
                                        key={type}
                                        type="button"
                                        onClick={() => setMess(type)}
                                        className={cn(
                                            "flex-1 py-2.5 text-sm font-medium rounded-lg transition-all duration-200",
                                            mess === type
                                                ? "bg-white shadow-sm text-indigo-600 ring-1 ring-black/5"
                                                : "text-gray-500 hover:text-gray-700 hover:bg-gray-100"
                                        )}
                                    >
                                        {type}
                                    </button>
                                ))}
                            </div>
                        </div>
                        <div className="space-y-2">
                            <label className="text-sm font-semibold text-gray-700">Select Meal</label>
                            <div className="relative">
                                <select
                                    value={meal}
                                    onChange={(e) => setMeal(e.target.value)}
                                    className="block w-full rounded-xl border-gray-200 bg-gray-50 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm py-3 px-4 appearance-none"
                                >
                                    {MEAL_TYPES.map(m => <option key={m} value={m}>{m}</option>)}
                                </select>
                                <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-4 text-gray-500">
                                    <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"></path></svg>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Food Items Selection */}
                    <div className="space-y-3">
                        <div className="flex items-center justify-between">
                            <label className="text-sm font-semibold text-gray-700">What did you eat?</label>
                            {availableItems.length > 0 && (
                                <button
                                    type="button"
                                    onClick={handleSelectAll}
                                    className="text-xs font-medium text-indigo-600 hover:text-indigo-700 underline"
                                >
                                    {selectedItems.length === availableItems.length ? 'Deselect All' : 'Select All'}
                                </button>
                            )}
                        </div>
                        {loadingItems ? (
                            <div className="flex space-x-2 animate-pulse">
                                <div className="h-8 w-20 bg-gray-200 rounded-full"></div>
                                <div className="h-8 w-24 bg-gray-200 rounded-full"></div>
                                <div className="h-8 w-16 bg-gray-200 rounded-full"></div>
                            </div>
                        ) : availableItems.length > 0 ? (
                            <div className="flex flex-wrap gap-2">
                                {availableItems.map((item) => (
                                    <button
                                        key={item._id}
                                        type="button"
                                        onClick={() => toggleItem(item.name)}
                                        className={cn(
                                            "px-4 py-2 rounded-full text-sm font-medium border transition-all duration-200",
                                            selectedItems.includes(item.name)
                                                ? "bg-indigo-50 border-indigo-200 text-indigo-700 shadow-sm"
                                                : "bg-white border-gray-200 text-gray-600 hover:border-gray-300 hover:bg-gray-50"
                                        )}
                                    >
                                        {item.name}
                                    </button>
                                ))}
                            </div>
                        ) : (
                            <p className="text-sm text-gray-500 italic">No menu items found for today's {meal}.</p>
                        )}
                    </div>

                    {/* Ratings */}
                    <div className="space-y-6 bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50 p-8 rounded-3xl border-2 border-indigo-100 shadow-lg hover:shadow-xl transition-shadow duration-300">
                        <div className="flex items-center gap-3">
                            <div className="w-1 h-6 bg-gradient-to-b from-indigo-500 to-purple-500 rounded-full"></div>
                            <h3 className="text-base font-bold text-gray-900 uppercase tracking-wide">Rate Your Experience</h3>
                        </div>
                        <div className="space-y-6">
                            <SpiceLevelSlider value={ratings.spice} onChange={(v) => setRatings({ ...ratings, spice: v })} />
                            <RatingRow label="Taste" value={ratings.taste} onChange={(v) => setRatings({ ...ratings, taste: v })} emoji={['🤢', '😣', '😐', '😊', '🤩']} />
                            <RatingRow label="Freshness" value={ratings.freshness} onChange={(v) => setRatings({ ...ratings, freshness: v })} emoji={['🤢', '😷', '😐', '😌', '😄']} />
                            <RatingRow label="Hygiene" value={ratings.hygiene} onChange={(v) => setRatings({ ...ratings, hygiene: v })} emoji={['🤮', '😰', '😐', '😊', '😁']} />
                            <RatingRow label="Staff Behavior" value={ratings.staff} onChange={(v) => setRatings({ ...ratings, staff: v })} emoji={['😡', '😠', '😐', '😊', '🥰']} />

                            <div className="pt-4 border-t border-indigo-100">
                                <RatingRow label="Overall Rating" value={ratings.overall} onChange={(v) => setRatings({ ...ratings, overall: v })} emoji={['😞', '😕', '😐', '🙂', '😍']} size="lg" />
                            </div>
                        </div>
                    </div>

                    {/* Image Upload */}
                    <div className="space-y-2">
                        <label className="text-sm font-semibold text-gray-700">Upload Photo (Optional)</label>
                        <div
                            className={cn(
                                "mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-dashed rounded-2xl transition-all duration-200 relative group",
                                isDragging ? "border-indigo-500 bg-indigo-50" : "border-gray-300 hover:border-indigo-400 hover:bg-gray-50"
                            )}
                            onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
                            onDragLeave={() => setIsDragging(false)}
                            onDrop={(e) => {
                                e.preventDefault();
                                setIsDragging(false);
                                const file = e.dataTransfer.files[0];
                                if (file) {
                                    const reader = new FileReader();
                                    reader.onloadend = () => setImage(reader.result as string);
                                    reader.readAsDataURL(file);
                                }
                            }}
                        >
                            <div className="space-y-2 text-center">
                                {image ? (
                                    <div className="relative inline-block">
                                        <img src={image} alt="Preview" className="h-48 rounded-lg shadow-md object-cover" />
                                        <button
                                            type="button"
                                            onClick={(e) => { e.stopPropagation(); setImage(null); setImageDescription(''); }}
                                            className="absolute -top-3 -right-3 bg-white text-red-500 rounded-full p-1.5 shadow-lg hover:bg-red-50 border border-gray-100 transition-colors"
                                        >
                                            <X size={16} />
                                        </button>
                                    </div>
                                ) : (
                                    <>
                                        <div className="mx-auto h-12 w-12 text-gray-400 group-hover:text-indigo-500 transition-colors">
                                            <ImageIcon className="h-full w-full" />
                                        </div>
                                        <div className="flex text-sm text-gray-600 justify-center">
                                            <label htmlFor="file-upload" className="relative cursor-pointer rounded-md font-medium text-indigo-600 hover:text-indigo-500 focus-within:outline-none">
                                                <span>Upload a file</span>
                                                <input id="file-upload" name="file-upload" type="file" className="sr-only" accept="image/*" onChange={handleImageUpload} />
                                            </label>
                                            <p className="pl-1">or drag and drop</p>
                                        </div>
                                        <p className="text-xs text-gray-500">PNG, JPG, GIF up to 10MB</p>
                                    </>
                                )}
                            </div>
                        </div>

                        {/* Image Description Field - appears when image is uploaded */}
                        {image && (
                            <div className="mt-3 space-y-2 animate-fade-in">
                                <label className="text-sm font-semibold text-indigo-700">Describe this image</label>
                                <textarea
                                    rows={3}
                                    className="block w-full rounded-xl border-indigo-200 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-4 border resize-none bg-indigo-50/30"
                                    placeholder="What's in the picture? Describe the food appearance, portion size, presentation, etc."
                                    value={imageDescription}
                                    onChange={(e) => setImageDescription(e.target.value)}
                                />
                                <p className="text-xs text-gray-500 flex items-center gap-1">
                                    <AlertCircle className="h-3 w-3" />
                                    Provide either this description OR feedback text below.
                                </p>
                            </div>
                        )}
                    </div>

                    {/* Text Feedback */}
                    <div className="space-y-2">
                        <div className="flex items-center justify-between">
                            <label className="text-sm font-semibold text-gray-700">Your Feedback</label>
                            {!image && (
                                <span className="text-xs font-medium text-red-600">* Required</span>
                            )}
                        </div>
                        <div className="relative">
                            <textarea
                                rows={4}
                                required={!image}
                                className="block w-full rounded-xl border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-4 border resize-none"
                                placeholder="Tell us more about the food quality, taste, or any suggestions..."
                                value={feedbackText}
                                onChange={(e) => setFeedbackText(e.target.value)}
                            />
                            <MessageSquare className="absolute top-4 right-4 h-5 w-5 text-gray-400 pointer-events-none" />
                        </div>
                        {image && (
                            <p className="text-xs text-gray-500 flex items-center gap-1">
                                <AlertCircle className="h-3 w-3" />
                                Optional if you described the image above.
                            </p>
                        )}
                    </div>

                    {/* Anonymous Toggle & Submit */}
                    <div className="flex items-center justify-between pt-8 border-t-2 border-indigo-100">
                        <div className="flex items-center group">
                            <div className="relative flex items-start">
                                <div className="flex items-center h-5">
                                    <input
                                        id="anonymous"
                                        type="checkbox"
                                        checked={isAnonymous}
                                        onChange={(e) => setIsAnonymous(e.target.checked)}
                                        className="h-5 w-5 text-indigo-600 border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 cursor-pointer transition-all"
                                    />
                                </div>
                                <div className="ml-3 text-sm">
                                    <label htmlFor="anonymous" className="font-semibold text-gray-800 cursor-pointer group-hover:text-indigo-600 transition-colors">Submit Anonymously</label>
                                    <p className="text-gray-500 text-xs mt-0.5">Your identity won't be shown to admins</p>
                                </div>
                            </div>
                        </div>
                        <button
                            type="submit"
                            disabled={submitted}
                            className={cn(
                                "inline-flex items-center px-10 py-4 border border-transparent text-base font-bold rounded-2xl shadow-xl text-white transition-all duration-300 focus:outline-none focus:ring-4 focus:ring-offset-2 focus:ring-indigo-300 transform hover:scale-105 active:scale-95",
                                submitted
                                    ? "bg-gradient-to-r from-green-500 to-emerald-600 shadow-green-300 cursor-default animate-pulse"
                                    : "bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 hover:from-indigo-700 hover:via-purple-700 hover:to-pink-700 shadow-indigo-300 hover:shadow-2xl"
                            )}
                        >
                            {submitted ? (
                                <>
                                    <span className="mr-2">✓</span> Submitted!
                                </>
                            ) : (
                                <>
                                    <Send className="mr-2 h-5 w-5" />
                                    Submit Feedback
                                </>
                            )}
                        </button>
                    </div>
                </form>
            </div >
        </div >
    );
}

function SpiceLevelSlider({ value, onChange }: { value: number, onChange: (v: number) => void }) {
    return (
        <div className="space-y-2">
            <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-gray-700">Spice Level</span>
                <span className="text-sm font-bold text-indigo-600">{value}</span>
            </div>
            <div className="relative">
                <input
                    type="range"
                    min="1"
                    max="5"
                    step="1"
                    value={value}
                    onChange={(e) => onChange(parseInt(e.target.value))}
                    className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-indigo-600"
                    style={{
                        background: `linear-gradient(to right, #4f46e5 0%, #4f46e5 ${((value - 1) / 4) * 100}%, #e5e7eb ${((value - 1) / 4) * 100}%, #e5e7eb 100%)`
                    }}
                />
                <div className="flex justify-between text-xs text-gray-500 mt-1 px-0.5">
                    <span>1</span>
                    <span>2</span>
                    <span>3</span>
                    <span>4</span>
                    <span>5</span>
                </div>
            </div>
        </div>
    );
}

function RatingRow({ label, value, onChange, emoji, size = "md" }: { label: string, value: number, onChange: (v: number) => void, emoji: string[], size?: "md" | "lg" }) {
    return (
        <div className="flex items-center justify-between group">
            <span className={cn("text-gray-700 font-medium", size === "lg" ? "text-base" : "text-sm")}>{label}</span>
            <div className="flex space-x-1 sm:space-x-3 bg-white rounded-full px-2 py-1 shadow-sm border border-gray-100">
                {[1, 2, 3, 4, 5].map((rating) => (
                    <button
                        key={rating}
                        type="button"
                        onClick={() => onChange(rating)}
                        className={cn(
                            "transition-all duration-200 focus:outline-none transform hover:scale-125",
                            size === "lg" ? "text-2xl p-1" : "text-xl p-0.5",
                            value === rating ? "opacity-100 scale-110" : "opacity-30 grayscale hover:grayscale-0 hover:opacity-70"
                        )}
                        title={`${rating} stars`}
                    >
                        {emoji[rating - 1]}
                    </button>
                ))}
            </div>
        </div>
    );
}
