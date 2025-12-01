const fetch = require('node-fetch');

async function testMenuApi() {
    try {
        // Get today's date in YYYY-MM-DD format (UTC)
        const today = new Date().toISOString().split('T')[0];
        console.log(`Testing API for date: ${today}`);

        const baseUrl = 'http://localhost:3005/api/menu';

        // Test North Lunch
        const northUrl = `${baseUrl}?date=${today}&mealType=Lunch&messType=North&isAvailable=true`;
        console.log(`Fetching: ${northUrl}`);
        const resNorth = await fetch(northUrl);
        const dataNorth = await resNorth.json();
        console.log('North Lunch Items:', dataNorth.data ? dataNorth.data.length : dataNorth);
        if (dataNorth.data && dataNorth.data.length > 0) {
            dataNorth.data.forEach(item => console.log(` - ${item.name} (${item.messType})`));
        }

        // Test South Lunch
        const southUrl = `${baseUrl}?date=${today}&mealType=Lunch&messType=South&isAvailable=true`;
        console.log(`Fetching: ${southUrl}`);
        const resSouth = await fetch(southUrl);
        const dataSouth = await resSouth.json();
        console.log('South Lunch Items:', dataSouth.data ? dataSouth.data.length : dataSouth);
        if (dataSouth.data && dataSouth.data.length > 0) {
            dataSouth.data.forEach(item => console.log(` - ${item.name} (${item.messType})`));
        }

    } catch (error) {
        console.error('Error testing API:', error);
    }
}

testMenuApi();
