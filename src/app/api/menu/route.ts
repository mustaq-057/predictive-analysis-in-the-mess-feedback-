import { NextRequest, NextResponse } from 'next/server';
import connectDB from '@/lib/db';
import MenuItem from '@/models/MenuItem';

// GET /api/menu - Fetch menu items with optional filters
export async function GET(request: NextRequest) {
    try {
        await connectDB();

        const { searchParams } = new URL(request.url);
        const mealType = searchParams.get('mealType');
        const messType = searchParams.get('messType');
        const date = searchParams.get('date');
        const isAvailable = searchParams.get('isAvailable');

        // Build query
        const query: any = {};
        if (mealType) query.mealType = mealType;
        if (messType) query.messType = messType;
        if (isAvailable !== null) query.isAvailable = isAvailable === 'true';

        // Filter by date (if provided, get items for that specific date)
        if (date) {
            const targetDate = new Date(date);
            const startOfDay = new Date(targetDate.setUTCHours(0, 0, 0, 0));
            const endOfDay = new Date(targetDate.setUTCHours(23, 59, 59, 999));
            query.date = { $gte: startOfDay, $lte: endOfDay };
        }

        const menuItems = await MenuItem.find(query)
            .sort({ date: -1, mealType: 1 })
            .limit(100)
            .lean();

        return NextResponse.json({
            success: true,
            data: menuItems,
        });
    } catch (error) {
        console.error('GET /api/menu error:', error);
        return NextResponse.json(
            { success: false, error: 'Failed to fetch menu items' },
            { status: 500 }
        );
    }
}

// POST /api/menu - Create a new menu item
export async function POST(request: NextRequest) {
    try {
        await connectDB();

        const body = await request.json();
        const { name, messType, mealType, description, date, isAvailable } = body;

        // Validate required fields
        if (!name || !mealType || !date) {
            return NextResponse.json(
                { success: false, error: 'Missing required fields (name, mealType, date)' },
                { status: 400 }
            );
        }

        const newMenuItem = await MenuItem.create({
            name,
            messType: messType || 'North', // Default to North if not provided
            mealType,
            description,
            date: new Date(date),
            isAvailable: isAvailable !== undefined ? isAvailable : true,
        });

        return NextResponse.json({
            success: true,
            data: newMenuItem,
        }, { status: 201 });
    } catch (error) {
        console.error('POST /api/menu error:', error);
        return NextResponse.json(
            { success: false, error: 'Failed to create menu item' },
            { status: 500 }
        );
    }
}
