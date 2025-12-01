import mongoose, { Schema, Document } from 'mongoose';

export interface IReview extends Document {
    studentName: string;
    studentEmail: string;
    mealType: 'breakfast' | 'lunch' | 'dinner';
    rating: number;
    review: string;
    foodImage?: string;
    imageDescription?: string;
    foodItems?: string[];
    detailedRatings?: {
        spice?: number;
        taste?: number;
        freshness?: number;
        hygiene?: number;
        staff?: number;
    };
    sentiment: 'good' | 'bad';
    aiAnalysis?: string;
    createdAt: Date;
    updatedAt: Date;
}

const ReviewSchema: Schema = new Schema(
    {
        studentName: {
            type: String,
            required: [true, 'Student name is required'],
            trim: true,
        },
        studentEmail: {
            type: String,
            required: [true, 'Student email is required'],
            lowercase: true,
            trim: true,
        },
        mealType: {
            type: String,
            required: [true, 'Meal type is required'],
            enum: ['breakfast', 'lunch', 'dinner'],
        },
        rating: {
            type: Number,
            required: [true, 'Rating is required'],
            min: 1,
            max: 5,
        },
        review: {
            type: String,
            required: [true, 'Review text is required'],
            trim: true,
        },
        foodImage: {
            type: String,
            default: null,
        },
        imageDescription: {
            type: String,
            default: null,
        },
        foodItems: {
            type: [String],
            default: [],
        },
        detailedRatings: {
            spice: { type: Number, min: 1, max: 5 },
            taste: { type: Number, min: 1, max: 5 },
            freshness: { type: Number, min: 1, max: 5 },
            hygiene: { type: Number, min: 1, max: 5 },
            staff: { type: Number, min: 1, max: 5 },
        },
        sentiment: {
            type: String,
            required: [true, 'Sentiment is required'],
            enum: ['good', 'bad'],
        },
        aiAnalysis: {
            type: String,
            default: null,
        },
    },
    {
        timestamps: true,
    }
);

// Add indexes for faster queries
ReviewSchema.index({ sentiment: 1, createdAt: -1 });
ReviewSchema.index({ mealType: 1, createdAt: -1 });
ReviewSchema.index({ createdAt: -1 });
ReviewSchema.index({ studentEmail: 1 });

const Review = mongoose.models.Review || mongoose.model<IReview>('Review', ReviewSchema);

export default Review;
