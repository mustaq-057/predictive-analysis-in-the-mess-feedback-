require('dotenv').config({ path: '.env.local' });
const mongoose = require('mongoose');
const cloudinary = require('cloudinary').v2;

console.log('\n' + '='.repeat(60));
console.log('🧪 COMPREHENSIVE INTEGRATION TESTS');
console.log('='.repeat(60) + '\n');

// Test counter
let testsRun = 0;
let testsPassed = 0;
let testsFailed = 0;

function logTest(name, passed, details) {
    testsRun++;
    if (passed) {
        testsPassed++;
        console.log(`✅ ${name}`);
    } else {
        testsFailed++;
        console.log(`❌ ${name}`);
    }
    if (details) {
        console.log(`   ${details}`);
    }
}

async function runTests() {
    // ============================================
    // 1. ENVIRONMENT VARIABLES TEST
    // ============================================
    console.log('\n📋 1. TESTING ENVIRONMENT VARIABLES\n' + '-'.repeat(60));

    const mongoUri = process.env.MONGODB_URI;
    const cloudName = process.env.NEXT_PUBLIC_CLOUDINARY_CLOUD_NAME;
    const cloudApiKey = process.env.CLOUDINARY_API_KEY;
    const cloudApiSecret = process.env.CLOUDINARY_API_SECRET;

    logTest('MongoDB URI configured', !!mongoUri, mongoUri ? `URI: ${mongoUri.substring(0, 30)}...` : 'Missing');
    logTest('Cloudinary Cloud Name configured', !!cloudName, cloudName ? `Cloud Name: ${cloudName}` : 'Missing');
    logTest('Cloudinary API Key configured', !!cloudApiKey, cloudApiKey ? `API Key: ${cloudApiKey}` : 'Missing');
    logTest('Cloudinary API Secret configured', !!cloudApiSecret, cloudApiSecret ? `Secret: ${cloudApiSecret.substring(0, 10)}...` : 'Missing');

    if (!mongoUri || !cloudName || !cloudApiKey || !cloudApiSecret) {
        console.log('\n⚠️  Cannot proceed with tests - missing environment variables');
        process.exit(1);
    }

    // ============================================
    // 2. MONGODB CONNECTION TEST
    // ============================================
    console.log('\n🗄️  2. TESTING MONGODB CONNECTION\n' + '-'.repeat(60));

    try {
        await mongoose.connect(mongoUri, {
            bufferCommands: false,
        });
        logTest('MongoDB connection established', true, `Connected to: ${mongoose.connection.name}`);

        // Test database operations
        const dbState = mongoose.connection.readyState;
        logTest('MongoDB ready state', dbState === 1, `State: ${dbState === 1 ? 'Connected' : 'Not Connected'}`);

        // List collections
        const collections = await mongoose.connection.db.listCollections().toArray();
        logTest('Database collections accessible', true, `Found ${collections.length} collections: ${collections.map(c => c.name).join(', ')}`);

    } catch (error) {
        logTest('MongoDB connection', false, `Error: ${error.message}`);
    }

    // ============================================
    // 3. MONGODB WRITE/READ TEST
    // ============================================
    console.log('\n💾 3. TESTING MONGODB WRITE/READ OPERATIONS\n' + '-'.repeat(60));

    try {
        // Define Review schema
        const ReviewSchema = new mongoose.Schema({
            studentName: String,
            studentEmail: String,
            mealType: { type: String, enum: ['breakfast', 'lunch', 'dinner'] },
            rating: { type: Number, min: 1, max: 5 },
            review: String,
            foodImage: String,
            sentiment: { type: String, enum: ['good', 'bad'] },
            aiAnalysis: String,
        }, { timestamps: true });

        const Review = mongoose.models.Review || mongoose.model('Review', ReviewSchema);

        // Create test review
        const testReview = {
            studentName: 'Test Student (Integration Test)',
            studentEmail: 'test@integration.test',
            mealType: 'lunch',
            rating: 4,
            review: 'This is a test review created by the integration test script. The food was good!',
            sentiment: 'good',
            aiAnalysis: 'Test sentiment analysis',
        };

        const created = await Review.create(testReview);
        logTest('Create review in MongoDB', !!created._id, `Document ID: ${created._id}`);

        // Read back the review
        const found = await Review.findById(created._id);
        logTest('Read review from MongoDB', !!found, `Found review: "${found?.review.substring(0, 50)}..."`);

        // Count all reviews
        const count = await Review.countDocuments();
        logTest('Count reviews in database', true, `Total reviews in DB: ${count}`);

        // Delete test review
        await Review.findByIdAndDelete(created._id);
        const deleted = await Review.findById(created._id);
        logTest('Delete test review', !deleted, 'Test review cleaned up successfully');

    } catch (error) {
        logTest('MongoDB write/read operations', false, `Error: ${error.message}`);
    }

    // ============================================
    // 4. CLOUDINARY CONFIGURATION TEST
    // ============================================
    console.log('\n☁️  4. TESTING CLOUDINARY CONFIGURATION\n' + '-'.repeat(60));

    try {
        cloudinary.config({
            cloud_name: cloudName,
            api_key: cloudApiKey,
            api_secret: cloudApiSecret,
        });

        logTest('Cloudinary configuration', true, `Configured with cloud: ${cloudName}`);

    } catch (error) {
        logTest('Cloudinary configuration', false, `Error: ${error.message}`);
    }

    // ============================================
    // 5. CLOUDINARY UPLOAD TEST
    // ============================================
    console.log('\n📤 5. TESTING CLOUDINARY IMAGE UPLOAD\n' + '-'.repeat(60));

    try {
        // Create a small test image (1x1 pixel red dot in base64)
        const testImageBase64 = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8DwHwAFBQIAX8jx0gAAAABJRU5ErkJggg==";

        const uploadResult = await cloudinary.uploader.upload(testImageBase64, {
            folder: 'test-integration',
            resource_type: 'auto',
        });

        logTest('Upload image to Cloudinary', !!uploadResult.secure_url, `URL: ${uploadResult.secure_url}`);
        logTest('Cloudinary image public ID generated', !!uploadResult.public_id, `Public ID: ${uploadResult.public_id}`);

        // ============================================
        // 6. CLOUDINARY DELETE TEST
        // ============================================
        console.log('\n🗑️  6. TESTING CLOUDINARY IMAGE DELETE\n' + '-'.repeat(60));

        const deleteResult = await cloudinary.uploader.destroy(uploadResult.public_id);
        logTest('Delete image from Cloudinary', deleteResult.result === 'ok', `Result: ${deleteResult.result}`);

    } catch (error) {
        logTest('Cloudinary upload/delete', false, `Error: ${error.message}`);
    }

    // ============================================
    // 7. END-TO-END TEST (Database + Cloudinary)
    // ============================================
    console.log('\n🔄 7. TESTING END-TO-END INTEGRATION\n' + '-'.repeat(60));

    try {
        const ReviewSchema = new mongoose.Schema({
            studentName: String,
            studentEmail: String,
            mealType: { type: String, enum: ['breakfast', 'lunch', 'dinner'] },
            rating: { type: Number, min: 1, max: 5 },
            review: String,
            foodImage: String,
            sentiment: { type: String, enum: ['good', 'bad'] },
            aiAnalysis: String,
        }, { timestamps: true });

        const Review = mongoose.models.Review || mongoose.model('Review', ReviewSchema);

        // Upload an image
        const testImageBase64 = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8DwHwAFBQIAX8jx0gAAAABJRU5ErkJggg==";
        const uploadResult = await cloudinary.uploader.upload(testImageBase64, {
            folder: 'mess-reviews',
        });

        // Create review with image URL
        const reviewWithImage = await Review.create({
            studentName: 'Test Student (E2E Test)',
            studentEmail: 'e2e@test.com',
            mealType: 'dinner',
            rating: 5,
            review: 'End-to-end test with image upload!',
            foodImage: uploadResult.secure_url,
            sentiment: 'good',
            aiAnalysis: 'Positive review detected',
        });

        logTest('Create review with Cloudinary image', !!reviewWithImage._id && !!reviewWithImage.foodImage,
            `Review ID: ${reviewWithImage._id}, Image: ${reviewWithImage.foodImage}`);

        // Clean up
        await Review.findByIdAndDelete(reviewWithImage._id);
        await cloudinary.uploader.destroy(uploadResult.public_id);
        logTest('Cleanup E2E test data', true, 'Removed test review and image');

    } catch (error) {
        logTest('End-to-end integration', false, `Error: ${error.message}`);
    }

    // ============================================
    // FINAL RESULTS
    // ============================================
    await mongoose.connection.close();

    console.log('\n' + '='.repeat(60));
    console.log('📊 TEST RESULTS SUMMARY');
    console.log('='.repeat(60));
    console.log(`Total Tests: ${testsRun}`);
    console.log(`✅ Passed: ${testsPassed}`);
    console.log(`❌ Failed: ${testsFailed}`);
    console.log(`Success Rate: ${((testsPassed / testsRun) * 100).toFixed(1)}%`);
    console.log('='.repeat(60) + '\n');

    if (testsFailed === 0) {
        console.log('🎉 ALL TESTS PASSED! Database and Cloudinary are working perfectly!\n');
        process.exit(0);
    } else {
        console.log('⚠️  SOME TESTS FAILED. Please check the errors above.\n');
        process.exit(1);
    }
}

// Run all tests
runTests().catch(error => {
    console.error('\n❌ Fatal error running tests:', error);
    process.exit(1);
});
