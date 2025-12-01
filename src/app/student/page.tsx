"use client";

import React, { useState, useEffect } from 'react';
import { cn } from '@/lib/utils';
import { Calendar, MapPin, Utensils, Coffee, Sun, Moon, Clock } from 'lucide-react';

const DAYS = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
const MESS_TYPES = ['North', 'South'];

export default function MenuPage() {
    const [selectedMess, setSelectedMess] = useState('North');
    // Default to today's day name in IST
    const [selectedDay, setSelectedDay] = useState(() => {
        return new Date().toLocaleDateString('en-US', { weekday: 'long', timeZone: 'Asia/Kolkata' });
    });

    const [menuItems, setMenuItems] = useState<{ breakfast: string[], lunch: string[], dinner: string[] }>({
        breakfast: [],
        lunch: [],
        dinner: []
    });
    const [loading, setLoading] = useState(false);

    // Simple cache to avoid redundant API calls
    const cacheRef = React.useRef<{ [key: string]: { breakfast: string[], lunch: string[], dinner: string[] } }>({});

    // Helper to get date for a specific day of the current week
    const getDateForDay = (dayName: string) => {
        const today = new Date();
        const currentDayIndex = today.getDay(); // 0 = Sunday, 1 = Monday, etc.
        const targetDayIndex = DAYS.indexOf(dayName);

        // Calculate difference. 
        // If we want "this week's" Monday and today is Wednesday, we go back.
        // If we want "this week's" Friday and today is Wednesday, we go forward.
        // For simplicity, let's just get the date relative to today.
        const diff = targetDayIndex - currentDayIndex;

        const targetDate = new Date(today);
        targetDate.setDate(today.getDate() + diff);

        return `${targetDate.getFullYear()}-${String(targetDate.getMonth() + 1).padStart(2, '0')}-${String(targetDate.getDate()).padStart(2, '0')}`;
    };

    useEffect(() => {
        const fetchMenu = async () => {
            const cacheKey = `${selectedMess}-${selectedDay}`;

            // Check cache first
            if (cacheRef.current[cacheKey]) {
                setMenuItems(cacheRef.current[cacheKey]);
                return;
            }

            setLoading(true);
            try {
                const date = getDateForDay(selectedDay);

                // OPTIMIZED: Single API call to fetch all meals at once
                const queryParams = new URLSearchParams({
                    date,
                    messType: selectedMess,
                    isAvailable: 'true'
                });

                const res = await fetch(`/api/menu?${queryParams}`);
                const data = await res.json();

                // Filter items by meal type client-side
                const newMenu = { breakfast: [] as string[], lunch: [] as string[], dinner: [] as string[] };

                if (data.success && data.data) {
                    data.data.forEach((item: any) => {
                        const mealType = item.mealType?.toLowerCase();
                        if (mealType === 'breakfast') newMenu.breakfast.push(item.name);
                        else if (mealType === 'lunch') newMenu.lunch.push(item.name);
                        else if (mealType === 'dinner') newMenu.dinner.push(item.name);
                    });
                }

                setMenuItems(newMenu);
                cacheRef.current[cacheKey] = newMenu; // Cache the result

            } catch (error) {
                console.error('Error fetching menu:', error);
                setMenuItems({ breakfast: [], lunch: [], dinner: [] });
            } finally {
                setLoading(false);
            }
        };

        fetchMenu();
    }, [selectedMess, selectedDay]);

    return (
        <div className="space-y-8 animate-fade-in">
            {/* Header Section */}
            <div className="bg-white rounded-3xl shadow-sm border border-gray-100 p-8 relative overflow-hidden">
                <div className="absolute top-0 right-0 w-64 h-64 bg-indigo-50 rounded-full -mr-16 -mt-16 opacity-50"></div>

                <div className="relative z-10">
                    <h1 className="text-3xl font-bold text-gray-900 mb-2 flex items-center">
                        <Utensils className="mr-3 h-8 w-8 text-indigo-600" />
                        Weekly Menu
                    </h1>
                    <p className="text-gray-500 max-w-2xl">
                        Check out what's cooking in the mess today. Plan your meals and never miss your favorites.
                    </p>
                </div>

                {/* Mess Selection Tabs */}
                <div className="mt-8 flex space-x-2 bg-gray-100/50 p-1 rounded-xl inline-flex">
                    {MESS_TYPES.map((mess) => (
                        <button
                            key={mess}
                            onClick={() => setSelectedMess(mess)}
                            className={cn(
                                "px-6 py-2.5 text-sm font-semibold rounded-lg transition-all duration-200",
                                selectedMess === mess
                                    ? "bg-white text-indigo-600 shadow-sm"
                                    : "text-gray-500 hover:text-gray-700 hover:bg-gray-200/50"
                            )}
                        >
                            {mess} Mess
                        </button>
                    ))}
                </div>
            </div>

            {/* Day Selection */}
            <div className="flex overflow-x-auto space-x-3 pb-4 scrollbar-hide -mx-4 px-4 sm:mx-0 sm:px-0">
                {DAYS.map((day) => (
                    <button
                        key={day}
                        onClick={() => setSelectedDay(day)}
                        className={cn(
                            "px-5 py-2.5 rounded-xl text-sm font-medium whitespace-nowrap transition-all duration-200 border",
                            selectedDay === day
                                ? "bg-indigo-600 text-white border-indigo-600 shadow-md shadow-indigo-200"
                                : "bg-white text-gray-600 border-gray-200 hover:border-indigo-300 hover:bg-indigo-50"
                        )}
                    >
                        {day}
                    </button>
                ))}
            </div>

            {/* Menu Display */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <MealCard
                    title="Breakfast"
                    items={menuItems.breakfast}
                    time="7:30 AM - 9:30 AM"
                    icon={<Coffee className="h-6 w-6 text-orange-500" />}
                    color="orange"
                    loading={loading}
                />
                <MealCard
                    title="Lunch"
                    items={menuItems.lunch}
                    time="12:30 PM - 2:30 PM"
                    icon={<Sun className="h-6 w-6 text-yellow-500" />}
                    color="yellow"
                    loading={loading}
                />
                <MealCard
                    title="Dinner"
                    items={menuItems.dinner}
                    time="7:30 PM - 9:30 PM"
                    icon={<Moon className="h-6 w-6 text-indigo-500" />}
                    color="indigo"
                    loading={loading}
                />
            </div>
        </div>
    );
}

function MealCard({ title, items, time, icon, color, loading }: { title: string, items: string[], time: string, icon: React.ReactNode, color: string, loading: boolean }) {
    const colorStyles = {
        orange: "bg-orange-50 border-orange-100 hover:border-orange-200",
        yellow: "bg-yellow-50 border-yellow-100 hover:border-yellow-200",
        indigo: "bg-indigo-50 border-indigo-100 hover:border-indigo-200",
    };

    const dotColors = {
        orange: "bg-orange-400",
        yellow: "bg-yellow-400",
        indigo: "bg-indigo-400",
    };

    return (
        <div className={cn(
            "rounded-3xl p-6 border transition-all duration-300 hover:shadow-lg hover:-translate-y-1",
            colorStyles[color as keyof typeof colorStyles] || "bg-white border-gray-100"
        )}>
            <div className="flex justify-between items-start mb-6">
                <div className="flex items-center space-x-3">
                    <div className="p-2.5 bg-white rounded-xl shadow-sm">
                        {icon}
                    </div>
                    <div>
                        <h3 className="text-lg font-bold text-gray-900">{title}</h3>
                        <div className="flex items-center text-xs font-medium text-gray-500 mt-0.5">
                            <Clock className="h-3 w-3 mr-1" />
                            {time}
                        </div>
                    </div>
                </div>
            </div>

            <div className="bg-white/60 rounded-2xl p-4 backdrop-blur-sm min-h-[120px]">
                {loading ? (
                    <div className="space-y-3 animate-pulse">
                        <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                        <div className="h-4 bg-gray-200 rounded w-1/2"></div>
                        <div className="h-4 bg-gray-200 rounded w-2/3"></div>
                    </div>
                ) : items.length > 0 ? (
                    <ul className="space-y-3">
                        {items.map((item, index) => (
                            <li key={index} className="flex items-center text-gray-700 font-medium">
                                <div className={cn("h-2 w-2 rounded-full mr-3", dotColors[color as keyof typeof dotColors])} />
                                {item}
                            </li>
                        ))}
                    </ul>
                ) : (
                    <p className="text-sm text-gray-400 italic text-center py-4">No items available</p>
                )}
            </div>
        </div>
    );
}
