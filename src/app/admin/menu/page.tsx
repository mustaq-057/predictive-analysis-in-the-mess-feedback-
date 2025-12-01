"use client";

import React, { useState, useEffect } from 'react';
import { Plus, Save, Trash2, Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';

interface MenuItem {
    _id?: string;
    name: string;
    messType: string;
    mealType: string;
    description?: string;
    date: string;
    isAvailable: boolean;
}

interface GroupedMenu {
    [day: string]: {
        [mealType: string]: MenuItem[];
    };
}

const DAYS = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
const MEALS = ['breakfast', 'lunch', 'dinner'];

export default function MenuManagerPage() {
    const [selectedMess, setSelectedMess] = useState<'North' | 'South'>('North');
    const [menu, setMenu] = useState<GroupedMenu>({});
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [weekStart, setWeekStart] = useState<Date>(getWeekStart(new Date()));

    // Cache to avoid redundant API calls
    const cacheRef = React.useRef<{ [key: string]: GroupedMenu }>({});

    useEffect(() => {
        fetchMenuItems();
    }, [selectedMess, weekStart]);

    function getWeekStart(date: Date): Date {
        // Get current IST date
        const istDateStr = new Date().toLocaleDateString('en-CA', { timeZone: 'Asia/Kolkata' });
        const istDate = new Date(istDateStr);
        const day = istDate.getDay(); // 0 = Sunday, 6 = Saturday
        const diff = istDate.getDate() - day; // Calculate Sunday's date
        return new Date(istDate.setDate(diff));
    }

    function getWeekDates(): Date[] {
        const dates: Date[] = [];
        for (let i = 0; i < 7; i++) {
            const date = new Date(weekStart);
            date.setDate(weekStart.getDate() + i);
            dates.push(date);
        }
        return dates;
    }

    function formatDate(date: Date): string {
        return date.toLocaleDateString('en-CA', { timeZone: 'Asia/Kolkata' });
    }

    async function fetchMenuItems() {
        const cacheKey = `${selectedMess}-${formatDate(weekStart)}`;

        // Check cache first
        if (cacheRef.current[cacheKey]) {
            setMenu(cacheRef.current[cacheKey]);
            setLoading(false);
            return;
        }

        setLoading(true);
        try {
            const weekDates = getWeekDates();
            const grouped: GroupedMenu = {};

            // Initialize structure
            DAYS.forEach((day, index) => {
                grouped[day] = {
                    breakfast: [],
                    lunch: [],
                    dinner: []
                };
            });

            // OPTIMIZED: Single API call to fetch all items for the week
            // Fetch without date filter to get all items, then filter client-side
            const startDate = formatDate(weekDates[0]);
            const endDate = formatDate(weekDates[6]);

            const queryParams = new URLSearchParams({
                messType: selectedMess,
            });

            const res = await fetch(`/api/menu?${queryParams}`);
            const data = await res.json();

            if (data.success && data.data) {
                // Filter items to only this week and group them
                data.data.forEach((item: MenuItem) => {
                    const itemDate = new Date(item.date);
                    const itemDateStr = formatDate(itemDate);

                    // Check if item is within our week range
                    const dayIndex = weekDates.findIndex(d => formatDate(d) === itemDateStr);
                    if (dayIndex >= 0) {
                        const day = DAYS[dayIndex];
                        const meal = item.mealType.toLowerCase();
                        if (grouped[day] && grouped[day][meal]) {
                            grouped[day][meal].push(item);
                        }
                    }
                });
            }

            setMenu(grouped);
            cacheRef.current[cacheKey] = grouped; // Cache the result
        } catch (error) {
            console.error('Error fetching menu:', error);
        } finally {
            setLoading(false);
        }
    }

    function addItem(day: string, mealType: string) {
        setMenu(prev => ({
            ...prev,
            [day]: {
                ...prev[day],
                [mealType]: [
                    ...prev[day][mealType],
                    {
                        name: '',
                        messType: selectedMess,
                        mealType: mealType,
                        description: '',
                        date: formatDate(getWeekDates()[DAYS.indexOf(day)]),
                        isAvailable: true
                    }
                ]
            }
        }));
    }

    function updateItem(day: string, mealType: string, index: number, field: keyof MenuItem, value: any) {
        setMenu(prev => ({
            ...prev,
            [day]: {
                ...prev[day],
                [mealType]: prev[day][mealType].map((item, i) =>
                    i === index ? { ...item, [field]: value } : item
                )
            }
        }));
    }

    function removeItem(day: string, mealType: string, index: number) {
        setMenu(prev => ({
            ...prev,
            [day]: {
                ...prev[day],
                [mealType]: prev[day][mealType].filter((_, i) => i !== index)
            }
        }));
    }

    async function saveChanges() {
        setSaving(true);
        try {
            const allItems: MenuItem[] = [];

            // Collect all items
            Object.entries(menu).forEach(([day, meals]) => {
                Object.entries(meals).forEach(([mealType, items]) => {
                    allItems.push(...items);
                });
            });

            // Delete all existing items for this week and mess
            const weekDates = getWeekDates();
            for (const date of weekDates) {
                const queryParams = new URLSearchParams({
                    date: formatDate(date),
                    messType: selectedMess,
                });
                const res = await fetch(`/api/menu?${queryParams}`);
                const data = await res.json();

                if (data.success && data.data) {
                    for (const item of data.data) {
                        await fetch(`/api/menu/${item._id}`, { method: 'DELETE' });
                    }
                }
            }

            // Create all new items
            for (const item of allItems) {
                if (item.name.trim()) {
                    await fetch('/api/menu', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            name: item.name,
                            messType: item.messType,
                            mealType: item.mealType,
                            description: item.description || '',
                            date: item.date,
                            isAvailable: item.isAvailable
                        })
                    });
                }
            }

            alert('Menu saved successfully!');
            await fetchMenuItems(); // Reload
        } catch (error) {
            console.error('Error saving menu:', error);
            alert('Failed to save menu. Please try again.');
        } finally {
            setSaving(false);
        }
    }

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <Loader2 className="h-8 w-8 animate-spin text-indigo-600" />
            </div>
        );
    }

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <h1 className="text-2xl font-bold text-gray-900">Menu Manager</h1>
                <button
                    onClick={saveChanges}
                    disabled={saving}
                    className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50"
                >
                    {saving ? (
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    ) : (
                        <Save className="mr-2 h-4 w-4" />
                    )}
                    {saving ? 'Saving...' : 'Save Changes'}
                </button>
            </div>

            <div className="bg-white shadow rounded-lg p-6">
                <div className="mb-6 flex gap-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Mess Type</label>
                        <select
                            value={selectedMess}
                            onChange={(e) => setSelectedMess(e.target.value as 'North' | 'South')}
                            className="rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm border p-2"
                        >
                            <option value="North">North Mess</option>
                            <option value="South">South Mess</option>
                        </select>
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Week Starting</label>
                        <input
                            type="date"
                            value={formatDate(weekStart)}
                            onChange={(e) => setWeekStart(new Date(e.target.value))}
                            className="rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm border p-2"
                        />
                    </div>
                </div>

                <div className="space-y-8">
                    {DAYS.map((day, dayIndex) => (
                        <div key={day} className="border-b border-gray-200 pb-6 last:border-0">
                            <h3 className="text-lg font-medium text-gray-900 mb-4">
                                {day} - {formatDate(getWeekDates()[dayIndex])}
                            </h3>

                            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                                {MEALS.map(meal => (
                                    <div key={meal} className="space-y-3">
                                        <div className="flex items-center justify-between">
                                            <h4 className="text-sm font-semibold text-gray-700 capitalize">{meal}</h4>
                                            <button
                                                onClick={() => addItem(day, meal)}
                                                className="text-indigo-600 hover:text-indigo-800"
                                            >
                                                <Plus className="h-4 w-4" />
                                            </button>
                                        </div>

                                        <div className="space-y-2">
                                            {menu[day]?.[meal]?.map((item, index) => (
                                                <div key={index} className="flex gap-2 items-center">
                                                    <input
                                                        type="text"
                                                        placeholder="Item name"
                                                        value={item.name}
                                                        onChange={(e) => updateItem(day, meal, index, 'name', e.target.value)}
                                                        className="flex-1 text-sm border-gray-300 rounded-md shadow-sm focus:border-indigo-500 focus:ring-indigo-500 border p-2"
                                                    />
                                                    <button
                                                        onClick={() => removeItem(day, meal, index)}
                                                        className="text-red-600 hover:text-red-800"
                                                    >
                                                        <Trash2 className="h-4 w-4" />
                                                    </button>
                                                </div>
                                            ))}

                                            {menu[day]?.[meal]?.length === 0 && (
                                                <p className="text-xs text-gray-400 italic">No items</p>
                                            )}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
