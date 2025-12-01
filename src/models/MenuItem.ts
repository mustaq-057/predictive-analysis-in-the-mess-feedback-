import mongoose, { Schema, Document } from 'mongoose';

export interface IMenuItem extends Document {
    name: string;
    messType: 'North' | 'South';
    mealType: 'breakfast' | 'lunch' | 'dinner';
    description?: string;
    date: Date;
    isAvailable: boolean;
    createdAt: Date;
    updatedAt: Date;
}

const MenuItemSchema: Schema = new Schema(
    {
        name: {
            type: String,
            required: [true, 'Menu item name is required'],
            trim: true,
        },
        messType: {
            type: String,
            required: [true, 'Mess type is required'],
            enum: ['North', 'South'],
            default: 'North'
        },
        mealType: {
            type: String,
            required: [true, 'Meal type is required'],
            enum: ['breakfast', 'lunch', 'dinner'],
        },
        description: {
            type: String,
            trim: true,
            default: null,
        },
        date: {
            type: Date,
            required: [true, 'Date is required'],
        },
        isAvailable: {
            type: Boolean,
            default: true,
        },
    },
    {
        timestamps: true,
    }
);

// Indexes for better query performance
MenuItemSchema.index({ date: -1, messType: 1, mealType: 1 });
MenuItemSchema.index({ isAvailable: 1 });

export default mongoose.models.MenuItem || mongoose.model<IMenuItem>('MenuItem', MenuItemSchema);
