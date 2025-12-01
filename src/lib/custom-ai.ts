import { spawn } from 'child_process';
import path from 'path';



// Structure of what the ML model returns
interface AnalysisResult {
    sentiment: 'good' | 'bad';
    confidence: number;
    keywords: string[];
    analysis: string;
}

export async function analyzeFoodReview(
    review: string,
    rating: number
): Promise<{ sentiment: 'good' | 'bad'; analysis: string }> {
    try {
        // Try to use the ML model with a 5-second timeout
        // Why timeout? If Python hangs or crashes, we don't want to wait forever
        const result = await Promise.race([
            runPythonPrediction(review, rating),
            new Promise<never>((_, reject) =>
                setTimeout(() => reject(new Error('ML model took too long to respond')), 5000)
            )
        ]);

        // Success! Return the ML model's prediction
        return {
            sentiment: result.sentiment,
            analysis: result.analysis || 'Analysis unavailable.',
        };
    } catch (error) {
        // If ML model fails (Python error, model not found, timeout, etc.)
        // We fall back to simple keyword-based analysis so the app keeps working
        console.error('ML analysis failed, using fallback:', error);
        return fallbackAnalysis(review, rating);
    }
}

/**
 * Run the Python ML prediction script
 * 
 * This is the bridge between Node.js and Python:
 * 1. We spawn a Python process
 * 2. Pass the review text and rating as arguments
 * 3. Python runs the ML model
 * 4. We capture the JSON output
 * 5. Return the results
 * 
 * If anything goes wrong (Python not installed, model missing, etc.),
 * we throw an error and the fallback kicks in.
 */
function runPythonPrediction(review: string, rating: number): Promise<AnalysisResult> {
    return new Promise((resolve, reject) => {
        // Find the Python script in the ml folder
        const scriptPath = path.join(process.cwd(), 'ml', 'predict.py');

        // Start Python process: python ml/predict.py "review text" 5
        const pythonProcess = spawn('python', [scriptPath, review, rating.toString()]);

        let stdout = '';
        let stderr = '';

        pythonProcess.stdout.on('data', (data) => {
            stdout += data.toString();
        });

        pythonProcess.stderr.on('data', (data) => {
            stderr += data.toString();
        });

        pythonProcess.on('close', (code) => {
            if (code !== 0) {
                reject(new Error(`Python script failed: ${stderr}`));
                return;
            }

            try {
                const result = JSON.parse(stdout);
                if (!result.success) {
                    reject(new Error(result.error || 'Prediction failed'));
                    return;
                }
                resolve(result);
            } catch (error) {
                reject(new Error(`Failed to parse Python output: ${error}`));
            }
        });

        pythonProcess.on('error', (error) => {
            reject(new Error(`Failed to start Python process: ${error.message}`));
        });
    });
}

/**
 * Fallback analysis: Simple keyword-based sentiment detection
 * 
 * This is our backup plan if the ML model fails.
 * It's not as smart as the trained model, but it works!
 * 
 * How it works:
 * 1. Check the rating: 3+ stars = good, below 3 = bad
 * 2. Search for positive words (delicious, fresh, great, etc.)
 * 3. Search for negative words (cold, stale, terrible, etc.)
 * 4. Build a simple analysis message
 * 
 * Example:
 *   "The food was cold and tasteless" with rating 2
 *   → sentiment: bad
 *   → analysis: "Negative feedback. Issues: cold, tasteless. Needs attention."
 */
function fallbackAnalysis(
    review: string,
    rating: number
): { sentiment: 'good' | 'bad'; analysis: string } {
    // First, check the rating to determine basic sentiment
    const sentiment = rating >= 3 ? 'good' : 'bad';
    const reviewLower = review.toLowerCase();

    // List of negative keywords to search for
    const negativeKeywords = [
        'cold', 'stale', 'bad', 'tasteless', 'unhygienic',
        'terrible', 'worst', 'poor', 'late', 'dirty'
    ];

    // List of positive keywords to search for
    const positiveKeywords = [
        'good', 'great', 'excellent', 'delicious', 'fresh',
        'tasty', 'amazing', 'loved', 'perfect', 'fantastic'
    ];

    // Find which keywords appear in the review
    const foundNegative = negativeKeywords.filter(kw => reviewLower.includes(kw));
    const foundPositive = positiveKeywords.filter(kw => reviewLower.includes(kw));

    // Build the analysis message based on what we found
    let analysis = sentiment === 'good'
        ? 'Positive feedback received.'
        : 'Negative feedback indicating issues.';

    // Add specific issues if we found negative keywords
    if (foundNegative.length > 0) {
        analysis += ` Issues mentioned: ${foundNegative.join(', ')}.`;
        analysis += ' Recommend addressing these concerns promptly.';
    }

    // Add positive highlights if it's a good review
    if (foundPositive.length > 0 && sentiment === 'good') {
        analysis += ` Positive aspects: ${foundPositive.join(', ')}.`;
    }

    // If we didn't find any keywords, say so
    if (foundNegative.length === 0 && foundPositive.length === 0) {
        analysis += ' No specific issues or praises identified.';
    }

    return { sentiment, analysis };
}

// Common dishes to look for in reviews
const COMMON_DISHES = [
    'biryani', 'dal', 'rice', 'roti', 'paratha', 'idli', 'dosa', 'sambar',
    'chole', 'rajma', 'paneer', 'chicken', 'sabzi', 'upma', 'poha', 'khichdi',
    'curd', 'salad', 'soup', 'dessert', 'chapati', 'vada', 'uttapam',
    'pulao', 'curry', 'pickle', 'chutney', 'raita', 'coffee', 'tea', 'milk'
];

/**
 * Extract mentioned food items from a review
 */
export function extractFoodItems(text: string): string[] {
    const lowerText = text.toLowerCase();
    return COMMON_DISHES.filter(dish => lowerText.includes(dish));
}

export interface FoodItemStat {
    item: string;
    good: number;
    bad: number;
    reviews: string[];
}

/**
 * Group reviews by food item and calculate sentiment stats
 */
export function groupReviewsByItem(
    reviews: Array<{ review: string; sentiment: 'good' | 'bad' }>
): FoodItemStat[] {
    const stats: Record<string, FoodItemStat> = {};

    reviews.forEach(r => {
        const items = extractFoodItems(r.review);
        items.forEach(item => {
            if (!stats[item]) {
                stats[item] = { item, good: 0, bad: 0, reviews: [] };
            }
            if (r.sentiment === 'good') stats[item].good++;
            else stats[item].bad++;

            // Keep only relevant snippets or full review? Full review for context.
            // Limit to last 5 reviews to save space
            if (stats[item].reviews.length < 5) {
                stats[item].reviews.push(r.review);
            }
        });
    });

    return Object.values(stats).sort((a, b) => b.bad - a.bad); // Sort by most negative first
}

/**
 * Generate summary insights from multiple reviews
 * @param reviews - Array of review objects
 * @returns Summary insights with trends and recommendations
 */
export async function generateReviewSummary(
    reviews: Array<{ review: string; rating: number; mealType: string; sentiment: 'good' | 'bad' }>
): Promise<string> {
    try {
        // Analyze sentiment distribution
        const goodCount = reviews.filter(r => r.sentiment === 'good').length;
        const badCount = reviews.length - goodCount;

        // Group by item
        const itemStats = groupReviewsByItem(reviews);
        const criticalItems = itemStats.filter(i => i.bad > i.good);
        const goodItems = itemStats.filter(i => i.good > i.bad);

        // Build summary
        let summary = `Analysis of ${reviews.length} reviews: ${goodCount} positive, ${badCount} negative.`;

        // 1. Brief Overview
        if (goodCount > badCount) {
            summary += ` Overall performance is good (${Math.round((goodCount / reviews.length) * 100)}% positive).`;
        } else {
            summary += ` Overall performance needs improvement (${Math.round((badCount / reviews.length) * 100)}% negative).`;
        }

        // 2. What's Happening (Critical Issues)
        if (criticalItems.length > 0) {
            summary += `\n\n🔴 Critical Issues (Action Required):`;
            criticalItems.slice(0, 5).forEach(item => {
                // Simple keyword extraction for "What's happening"
                // This is a basic heuristic since we don't have a full LLM here for summarization
                const commonComplaints = item.reviews
                    .join(' ').toLowerCase()
                    .match(/(cold|salty|raw|tasteless|bad|worst|late|dirty|stale|hard|spicy|oily)/g);

                const uniqueComplaints = [...new Set(commonComplaints || [])].slice(0, 3).join(', ');
                const issueDesc = uniqueComplaints ? `Issues: ${uniqueComplaints}` : `"${item.reviews[0].substring(0, 40)}..."`;

                summary += `\n- ${item.item.toUpperCase()}: ${item.bad} bad vs ${item.good} good. ${issueDesc}`;
            });
            summary += `\n👉 Recommendation: Prioritize fixing ${criticalItems.map(i => i.item).slice(0, 3).join(', ')}.`;
        } else {
            summary += "\n\n✅ No critical issues found. Keep up the good work!";
        }

        // 3. Best Doing (Concise)
        if (goodItems.length > 0) {
            summary += `\n\n🌟 Best Doing: ${goodItems.slice(0, 5).map(i => i.item).join(', ')}.`;
        }

        return summary;
    } catch (error) {
        console.error('Summary generation error:', error);
        return 'Unable to generate summary at this time.';
    }
}

export default { analyzeFoodReview, generateReviewSummary, extractFoodItems, groupReviewsByItem };
