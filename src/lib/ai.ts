import { GoogleGenerativeAI } from '@google/generative-ai';

const apiKey = process.env.GOOGLE_API_KEY;

if (!apiKey) {
    // Warn but don't throw during build
    if (process.env.NODE_ENV !== 'production' && typeof window === 'undefined' && process.env.NEXT_PHASE !== 'phase-production-build') {
        console.warn('GOOGLE_API_KEY environment variable is not set. AI features will not work.');
    }
}

const genAI = apiKey ? new GoogleGenerativeAI(apiKey) : null;

/**
 * Analyze food review using Google Gemini AI
 * @param review - The review text to analyze
 * @param rating - The rating (1-5) given by the student
 * @param imageUrl - Optional URL of the food image
 * @returns AI analysis result with sentiment and insights
 */
export async function analyzeFoodReview(
    review: string,
    rating: number,
    imageUrl?: string
): Promise<{ sentiment: 'good' | 'bad'; analysis: string }> {
    try {
        if (!genAI) {
            throw new Error('AI service not configured');
        }

        const model = genAI.getGenerativeModel({ model: 'gemini-1.5-flash' });

        const prompt = `
You are an AI assistant analyzing mess food reviews for a college dining service. 

Review Text: "${review}"
Rating: ${rating}/5

${imageUrl ? `Food Image URL: ${imageUrl}` : 'No image provided.'}

Please provide:
1. Sentiment classification: 'good' or 'bad' (based on the rating and review)
2. A brief analysis (2-3 sentences) highlighting:
   - Key concerns or praise mentioned
   - Specific food quality issues or strengths
   - Actionable insights for the mess management

Format your response as JSON:
{
  "sentiment": "good" or "bad",
  "analysis": "your analysis here"
}
`;

        const result = await model.generateContent(prompt);
        const response = await result.response;
        const text = response.text();

        // Parse JSON response
        const jsonMatch = text.match(/\{[\s\S]*\}/);
        if (!jsonMatch) {
            throw new Error('Invalid AI response format');
        }

        const parsed = JSON.parse(jsonMatch[0]);

        // Validate sentiment
        if (parsed.sentiment !== 'good' && parsed.sentiment !== 'bad') {
            // Fallback based on rating
            parsed.sentiment = rating >= 3 ? 'good' : 'bad';
        }

        return {
            sentiment: parsed.sentiment,
            analysis: parsed.analysis || 'No specific insights available.',
        };
    } catch (error) {
        console.error('AI analysis error:', error);

        // Fallback sentiment based on rating
        const fallbackSentiment = rating >= 3 ? 'good' : 'bad';

        return {
            sentiment: fallbackSentiment,
            analysis: 'AI analysis unavailable. Sentiment determined by rating.',
        };
    }
}

/**
 * Generate summary insights from multiple reviews
 * @param reviews - Array of review objects
 * @returns Summary insights with trends and recommendations
 */
export async function generateReviewSummary(
    reviews: Array<{ review: string; rating: number; mealType: string }>
): Promise<string> {
    try {
        if (!genAI) {
            throw new Error('AI service not configured');
        }

        const model = genAI.getGenerativeModel({ model: 'gemini-1.5-flash' });

        const reviewsText = reviews
            .map((r, i) => `Review ${i + 1} (${r.mealType}, ${r.rating}/5): ${r.review}`)
            .join('\n');

        const prompt = `
You are analyzing a batch of mess food reviews for college dining management.

Reviews:
${reviewsText}

Please provide a concise summary (3-4 sentences) including:
1. Overall sentiment trend
2. Most common complaints or praises
3. Specific recommendations for improvement

Be specific and actionable.
`;

        const result = await model.generateContent(prompt);
        const response = await result.response;
        return response.text();
    } catch (error) {
        console.error('Summary generation error:', error);
        return 'Unable to generate summary at this time.';
    }
}

export default genAI;
