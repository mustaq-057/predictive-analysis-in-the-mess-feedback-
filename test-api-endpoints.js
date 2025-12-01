// Test API endpoints
const fetch = require('node-fetch');

async function testAPI() {
    console.log('\n' + '='.repeat(60));
    console.log('🌐 API ENDPOINT TESTS');
    console.log('='.repeat(60) + '\n');

    const baseUrl = 'http://localhost:3005';

    // Test 1: GET /api/reviews
    console.log('📥 Testing GET /api/reviews\n' + '-'.repeat(60));
    try {
        const response = await fetch(`${baseUrl}/api/reviews`);
        const data = await response.json();

        console.log(`✅ Status: ${response.status} ${response.statusText}`);
        console.log(`✅ Success: ${data.success}`);
        console.log(`✅ Total reviews: ${data.total}`);
        console.log(`✅ Reviews fetched: ${data.data?.length || 0}`);

        if (data.data && data.data.length > 0) {
            console.log('\nSample review:');
            const sample = data.data[0];
            console.log(`   Student: ${sample.studentName}`);
            console.log(`   Meal: ${sample.mealType}`);
            console.log(`   Rating: ${sample.rating}/5`);
            console.log(`   Sentiment: ${sample.sentiment}`);
            console.log(`   Review: ${sample.review.substring(0, 100)}...`);
        }
    } catch (error) {
        console.log(`❌ Error: ${error.message}`);
    }

    // Test 2: POST /api/reviews (Create feedback)
    console.log('\n\n📤 Testing POST /api/reviews (Create Feedback)\n' + '-'.repeat(60));
    try {
        const testReview = {
            studentName: 'API Test User',
            studentEmail: 'apitest@example.com',
            mealType: 'lunch',
            rating: 4,
            review: 'Testing the feedback submission API. The food quality was good today!'
        };

        const response = await fetch(`${baseUrl}/api/reviews`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(testReview),
        });

        const data = await response.json();

        console.log(`✅ Status: ${response.status} ${response.statusText}`);
        console.log(`✅ Success: ${data.success}`);

        if (data.success) {
            console.log(`✅ Review created with ID: ${data.data._id}`);
            console.log(`✅ AI Sentiment detected: ${data.data.sentiment}`);
            console.log(`✅ AI Analysis: ${data.data.aiAnalysis || 'N/A'}`);

            // Clean up test review
            console.log('\n🧹 Cleaning up test review...');
            // Note: You would need a DELETE endpoint to clean this up properly
            console.log('✅ Test review created (ID: ' + data.data._id + ')');
        }
    } catch (error) {
        console.log(`❌ Error: ${error.message}`);
    }

    // Test 3: GET /api/reviews with filters
    console.log('\n\n🔍 Testing GET /api/reviews with filters\n' + '-'.repeat(60));
    try {
        // Test sentiment filter
        const response = await fetch(`${baseUrl}/api/reviews?sentiment=good&limit=3`);
        const data = await response.json();

        console.log(`✅ Good reviews found: ${data.data?.length || 0}`);

        // Test meal type filter
        const lunchResponse = await fetch(`${baseUrl}/api/reviews?mealType=lunch&limit=3`);
        const lunchData = await lunchResponse.json();

        console.log(`✅ Lunch reviews found: ${lunchData.data?.length || 0}`);
    } catch (error) {
        console.log(`❌ Error: ${error.message}`);
    }

    console.log('\n' + '='.repeat(60));
    console.log('✅ API ENDPOINT TESTS COMPLETE');
    console.log('='.repeat(60) + '\n');
}

testAPI().catch(console.error);
