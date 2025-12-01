import { NextRequest, NextResponse } from 'next/server';
import connectDB from '@/lib/db';
import Review from '@/models/Review';

// GET /api/reviews/[id] - Get a specific review
export async function GET(
    request: NextRequest,
    { params }: { params: Promise<{ id: string }> }
) {
    try {
        await connectDB();

        const { id } = await params;
        const review = await Review.findById(id);

        if (!review) {
            return NextResponse.json(
                { success: false, error: 'Review not found' },
                { status: 404 }
            );
        }

        return NextResponse.json({
            success: true,
            data: review,
        });
    } catch (error) {
        console.error('GET /api/reviews/[id] error:', error);
        return NextResponse.json(
            { success: false, error: 'Failed to fetch review' },
            { status: 500 }
        );
    }
}

// PUT /api/reviews/[id] - Update a review
export async function PUT(
    request: NextRequest,
    { params }: { params: Promise<{ id: string }> }
) {
    try {
        await connectDB();

        const { id } = await params;
        const body = await request.json();
        const { rating, review, sentiment } = body;

        const updatedReview = await Review.findByIdAndUpdate(
            id,
            { rating, review, sentiment },
            { new: true, runValidators: true }
        );

        if (!updatedReview) {
            return NextResponse.json(
                { success: false, error: 'Review not found' },
                { status: 404 }
            );
        }

        return NextResponse.json({
            success: true,
            data: updatedReview,
        });
    } catch (error) {
        console.error('PUT /api/reviews/[id] error:', error);
        return NextResponse.json(
            { success: false, error: 'Failed to update review' },
            { status: 500 }
        );
    }
}

// DELETE /api/reviews/[id] - Delete a review
export async function DELETE(
    request: NextRequest,
    { params }: { params: Promise<{ id: string }> }
) {
    try {
        await connectDB();

        const { id } = await params;
        const deletedReview = await Review.findByIdAndDelete(id);

        if (!deletedReview) {
            return NextResponse.json(
                { success: false, error: 'Review not found' },
                { status: 404 }
            );
        }

        return NextResponse.json({
            success: true,
            message: 'Review deleted successfully',
        });
    } catch (error) {
        console.error('DELETE /api/reviews/[id] error:', error);
        return NextResponse.json(
            { success: false, error: 'Failed to delete review' },
            { status: 500 }
        );
    }
}
