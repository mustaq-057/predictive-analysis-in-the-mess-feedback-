import { NextRequest, NextResponse } from 'next/server';
import connectDB from '@/lib/db';
import Review from '@/models/Review';
import { generateReviewSummary, groupReviewsByItem } from '@/lib/custom-ai';

// POST /api/analyze - Generate AI insights from reviews
export async function POST(request: NextRequest) {
    try {
        await connectDB();

        const body = await request.json();
        const { mealType, startDate, endDate, limit } = body;

        // Build query
        const query: any = {};
        if (mealType) query.mealType = mealType;

        if (startDate || endDate) {
            query.createdAt = {};
            if (startDate) query.createdAt.$gte = new Date(startDate);
            if (endDate) query.createdAt.$lte = new Date(endDate);
        }

        // Fetch reviews
        const reviews = await Review.find(query)
            .sort({ createdAt: -1 })
            .limit(limit || 50);

        if (reviews.length === 0) {
            return NextResponse.json({
                success: true,
                message: 'No reviews found for analysis',
                data: {
                    summary: 'No reviews available for the selected criteria.',
                    reviewCount: 0,
                    stats: {
                        totalReviews: 0,
                        averageRating: "0.0",
                        goodReviews: 0,
                        badReviews: 0,
                        mealTypeBreakdown: { breakfast: 0, lunch: 0, dinner: 0 }
                    },
                    foodItemStats: []
                },
            });
        }

        // Prepare data for AI analysis
        const reviewData = reviews.map((r) => ({
            review: r.review,
            rating: r.rating,
            mealType: r.mealType,
            sentiment: r.sentiment as 'good' | 'bad' // Ensure type safety
        }));

        // Generate summary
        const summary = await generateReviewSummary(reviewData);

        // Generate food item stats
        const foodItemStats = groupReviewsByItem(reviewData);

        // Calculate statistics
        const stats = {
            totalReviews: reviews.length,
            averageRating: (
                reviews.reduce((sum, r) => sum + r.rating, 0) / reviews.length
            ).toFixed(1),
            goodReviews: reviews.filter((r) => r.sentiment === 'good').length,
            badReviews: reviews.filter((r) => r.sentiment === 'bad').length,
            mealTypeBreakdown: {
                breakfast: reviews.filter((r) => r.mealType === 'breakfast').length,
                lunch: reviews.filter((r) => r.mealType === 'lunch').length,
                dinner: reviews.filter((r) => r.mealType === 'dinner').length,
            },
        };

        // Calculate Weekly Trends (Last 7 Days)
        const weeklyTrends = [];
        const today = new Date();
        for (let i = 6; i >= 0; i--) {
            const date = new Date(today);
            date.setDate(today.getDate() - i);
            const dateString = date.toLocaleDateString('en-US', { weekday: 'short' }); // Mon, Tue, etc.

            // Filter reviews for this specific day
            // Note: This relies on the fetched 'reviews' array. 
            // If 'limit' is small, this might not be accurate for older days.
            // For accurate trends, we should ideally fetch more data or use a separate aggregation query.
            // But for now, let's use the fetched reviews to keep it simple and fast.
            const dayReviews = reviews.filter(r => {
                const rDate = new Date(r.createdAt);
                return rDate.getDate() === date.getDate() &&
                    rDate.getMonth() === date.getMonth() &&
                    rDate.getFullYear() === date.getFullYear();
            });

            const positive = dayReviews.filter(r => r.sentiment === 'good').length;
            const negative = dayReviews.filter(r => r.sentiment === 'bad').length;

            weeklyTrends.push({
                name: dateString,
                positive,
                negative,
                amt: positive + negative // Total for the day
            });
        }

        return NextResponse.json({
            success: true,
            data: {
                summary,
                stats,
                foodItemStats,
                weeklyTrends
            },
        });
    } catch (error) {
        console.error('POST /api/analyze error:', error);
        return NextResponse.json(
            { success: false, error: 'Failed to generate analysis' },
            { status: 500 }
        );
    }
}
