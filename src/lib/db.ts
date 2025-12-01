import mongoose from 'mongoose';

const MONGODB_URI = process.env.MONGODB_URI;

if (!MONGODB_URI) {
    // Only throw if we're not in build mode
    if (process.env.NODE_ENV !== 'production' && typeof window === 'undefined' && process.env.NEXT_PHASE !== 'phase-production-build') {
        console.warn(
            'MONGODB_URI environment variable is not set. Database features will not work.'
        );
    }
}

/**
 * Global is used here to maintain a cached connection across hot reloads
 * in development. This prevents connections growing exponentially
 * during API Route usage.
 */
// @ts-expect-error
let cached = global.mongoose;

if (!cached) {
    // @ts-expect-error
    cached = global.mongoose = { conn: null, promise: null };
}

async function connectDB() {
    if (!MONGODB_URI) {
        throw new Error('MONGODB_URI is not configured');
    }

    if (cached.conn) {
        return cached.conn;
    }

    if (!cached.promise) {
        const opts = {
            bufferCommands: false,
        };

        cached.promise = mongoose.connect(MONGODB_URI!, opts).then((mongoose) => {
            return mongoose;
        });
    }

    try {
        cached.conn = await cached.promise;
    } catch (e) {
        cached.promise = null;
        throw e;
    }

    return cached.conn;
}

export default connectDB;
