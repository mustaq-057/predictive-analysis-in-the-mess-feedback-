import { NextRequest, NextResponse } from 'next/server';
import connectDB from '@/lib/db';
import Review from '@/models/Review';
import { uploadImage } from '@/lib/cloudinary';
import { analyzeFoodReview } from '@/lib/custom-ai';

// GET /api/reviews - Fetch all reviews with optional filters
export async function GET(request: NextRequest) {
    try {
        await connectDB();

        const { searchParams } = new URL(request.url);
        const mealType = searchParams.get('mealType');
        const sentiment = searchParams.get('sentiment');
        const limit = parseInt(searchParams.get('limit') || '50');
        const skip = parseInt(searchParams.get('skip') || '0');

        // Build query
        const query: any = {};
        if (mealType) query.mealType = mealType;
        if (sentiment) query.sentiment = sentiment;

        const reviews = await Review.find(query)
            .sort({ createdAt: -1 })
            .limit(limit)
            .skip(skip);

        const total = await Review.countDocuments(query);

        return NextResponse.json({
            success: true,
            data: reviews,
            total,
            limit,
            skip,
        });
    } catch (error) {
        console.error('GET /api/reviews error:', error);
        return NextResponse.json(
            { success: false, error: 'Failed to fetch reviews' },
            { status: 500 }
        );
    }
}

// POST /api/reviews - Create a new review
export async function POST(request: NextRequest) {
    try {
        await connectDB();

        const body = await request.json();
        const { studentName, studentEmail, mealType, rating, review, foodImage, imageDescription, foodItems, detailedRatings } = body;

        // Validate required fields
        if (!studentName || !studentEmail || !mealType || !rating) {
            return NextResponse.json(
                { success: false, error: 'Missing required fields' },
                { status: 400 }
            );
        }

        // Validate: remarks is required UNLESS (image exists AND imageDescription is provided)
        if (foodImage) {
            if ((!review || review.trim().length === 0) && (!imageDescription || imageDescription.trim().length === 0)) {
                return NextResponse.json(
                    { success: false, error: 'Please provide either feedback text or describe the uploaded image' },
                    { status: 400 }
                );
            }
        } else if (!review || review.trim().length === 0) {
            return NextResponse.json(
                { success: false, error: 'Please provide your feedback' },
                { status: 400 }
            );
        }

        // Upload image if provided
        let imageUrl = null;
        if (foodImage) {
            try {
                const uploadResult = await uploadImage(foodImage);
                imageUrl = uploadResult.secure_url;
            } catch (error) {
                console.error('Image upload failed:', error);
                // Continue without image if upload fails
            }
        }

        // Build enriched review context for AI analysis
        let enrichedReview = review || '';

        // Add image description if provided
        if (imageDescription && imageDescription.trim().length > 0) {
            enrichedReview = imageDescription + (enrichedReview ? ` ${enrichedReview}` : '');
        }

        if (foodItems && foodItems.length > 0) {
            enrichedReview = `Food items: ${foodItems.join(', ')}. ${enrichedReview}`;
        }

        // Add low rating context
        if (detailedRatings) {
            const lowRatings = [];
            if (detailedRatings.hygiene && detailedRatings.hygiene <= 2) lowRatings.push(`hygiene: ${detailedRatings.hygiene}/5`);
            if (detailedRatings.taste && detailedRatings.taste <= 2) lowRatings.push(`taste: ${detailedRatings.taste}/5`);
            if (detailedRatings.freshness && detailedRatings.freshness <= 2) lowRatings.push(`freshness: ${detailedRatings.freshness}/5`);

            if (lowRatings.length > 0) {
                enrichedReview += ` [Low ratings - ${lowRatings.join(', ')}]`;
            }
        }

        // Analyze review with custom ML model
        const aiResult = await analyzeFoodReview(enrichedReview, rating);

        // Create review
        const newReview = await Review.create({
            studentName,
            studentEmail,
            mealType,
            rating,
            review: review || '',
            foodImage: imageUrl,
            imageDescription: imageDescription || null,
            foodItems: foodItems || [],
            detailedRatings: detailedRatings || {},
            sentiment: aiResult.sentiment,
            aiAnalysis: aiResult.analysis,
        });

        return NextResponse.json({
            success: true,
            data: newReview,
        }, { status: 201 });
    } catch (error) {
        console.error('POST /api/reviews error:', error);
        return NextResponse.json(
            { success: false, error: error instanceof Error ? error.message : 'Failed to create review' },
            { status: 500 }
        );
    }
}
