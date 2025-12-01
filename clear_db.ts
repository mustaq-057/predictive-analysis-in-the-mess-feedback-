import { MongoClient } from 'mongodb';
import dotenv from 'dotenv';
import path from 'path';

// Load the secret passwords from the .env file
dotenv.config({ path: path.resolve(process.cwd(), '.env.local') });

const MONGODB_URI = process.env.MONGODB_URI;

// Stop if we don't have the database connection string
if (!MONGODB_URI) {
    console.error('❌ MONGODB_URI is not defined in .env.local');
    process.exit(1);
}

// This function deletes all data from the database
async function clearDatabase() {
    console.log('🚀 Connecting to MongoDB...');
    const client = new MongoClient(MONGODB_URI);

    try {
        // Connect to the database server
        await client.connect();
        console.log('✓ Connected successfully');

        const db = client.db();
        const collection = db.collection('reviews');

        // Check how many reviews we have
        const count = await collection.countDocuments();
        console.log(`📊 Found ${count} reviews in the database.`);

        if (count > 0) {
            console.log('🗑️  Deleting all reviews...');
            // Delete everything in the reviews collection
            const result = await collection.deleteMany({});
            console.log(`✅ Deleted ${result.deletedCount} reviews.`);
        } else {
            console.log('✓ Database is already empty.');
        }

    } catch (error) {
        console.error('❌ Error clearing database:', error);
    } finally {
        // Always close the connection when done
        await client.close();
        console.log('👋 Connection closed');
    }
}

// Run the function
clearDatabase();
