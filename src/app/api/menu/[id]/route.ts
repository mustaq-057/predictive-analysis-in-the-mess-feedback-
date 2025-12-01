import { NextRequest, NextResponse } from 'next/server';
import connectDB from '@/lib/db';
import MenuItem from '@/models/MenuItem';

// GET /api/menu/[id] - Get a specific menu item
export async function GET(
    request: NextRequest,
    { params }: { params: Promise<{ id: string }> }
) {
    try {
        await connectDB();

        const { id } = await params;
        const menuItem = await MenuItem.findById(id);

        if (!menuItem) {
            return NextResponse.json(
                { success: false, error: 'Menu item not found' },
                { status: 404 }
            );
        }

        return NextResponse.json({
            success: true,
            data: menuItem,
        });
    } catch (error) {
        console.error('GET /api/menu/[id] error:', error);
        return NextResponse.json(
            { success: false, error: 'Failed to fetch menu item' },
            { status: 500 }
        );
    }
}

// PUT /api/menu/[id] - Update a menu item
export async function PUT(
    request: NextRequest,
    { params }: { params: Promise<{ id: string }> }
) {
    try {
        await connectDB();

        const { id } = await params;
        const body = await request.json();
        const { name, mealType, description, date, isAvailable } = body;

        const updateData: any = {};
        if (name !== undefined) updateData.name = name;
        if (mealType !== undefined) updateData.mealType = mealType;
        if (description !== undefined) updateData.description = description;
        if (date !== undefined) updateData.date = new Date(date);
        if (isAvailable !== undefined) updateData.isAvailable = isAvailable;

        const updatedMenuItem = await MenuItem.findByIdAndUpdate(
            id,
            updateData,
            { new: true, runValidators: true }
        );

        if (!updatedMenuItem) {
            return NextResponse.json(
                { success: false, error: 'Menu item not found' },
                { status: 404 }
            );
        }

        return NextResponse.json({
            success: true,
            data: updatedMenuItem,
        });
    } catch (error) {
        console.error('PUT /api/menu/[id] error:', error);
        return NextResponse.json(
            { success: false, error: 'Failed to update menu item' },
            { status: 500 }
        );
    }
}

// DELETE /api/menu/[id] - Delete a menu item
export async function DELETE(
    request: NextRequest,
    { params }: { params: Promise<{ id: string }> }
) {
    try {
        await connectDB();

        const { id } = await params;
        const deletedMenuItem = await MenuItem.findByIdAndDelete(id);

        if (!deletedMenuItem) {
            return NextResponse.json(
                { success: false, error: 'Menu item not found' },
                { status: 404 }
            );
        }

        return NextResponse.json({
            success: true,
            message: 'Menu item deleted successfully',
        });
    } catch (error) {
        console.error('DELETE /api/menu/[id] error:', error);
        return NextResponse.json(
            { success: false, error: 'Failed to delete menu item' },
            { status: 500 }
        );
    }
}
