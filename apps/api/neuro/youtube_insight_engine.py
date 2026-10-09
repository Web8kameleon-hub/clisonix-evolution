"""
YouTube Insight Engine - REAL YouTube API Analysis
Analyzes video metadata, trends, engagement
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class YouTubeInsightEngine:
    """Analyze YouTube videos with REAL metadata"""
    
    def analyze(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze REAL YouTube video metadata
        Input: YouTube API response (snippet, statistics, contentDetails)
        """
        try:
            snippet = metadata.get('snippet', {})
            stats = metadata.get('statistics', {})
            
            # REAL METRICS
            view_count = int(stats.get('viewCount', 0))
            like_count = int(stats.get('likeCount', 0))
            comment_count = int(stats.get('commentCount', 0))
            
            # ENGAGEMENT RATE (real calculation)
            engagement_rate = 0.0
            if view_count > 0:
                engagement_rate = ((like_count + comment_count) / view_count) * 100
            
            # EMOTIONAL TONE (from title/description sentiment)
            title = snippet.get('title', '').lower()
            description = snippet.get('description', '').lower()
            
            positive_words = ['amazing', 'love', 'best', 'great', 'awesome', 'beautiful', 'perfect']
            negative_words = ['hate', 'worst', 'terrible', 'bad', 'awful', 'horrible']
            
            positive_count = sum(1 for word in positive_words if word in title or word in description)
            negative_count = sum(1 for word in negative_words if word in title or word in description)
            
            if positive_count > negative_count:
                emotional_tone = "positive"
                sentiment_score = 0.5 + (positive_count / 10)
            elif negative_count > positive_count:
                emotional_tone = "negative"
                sentiment_score = 0.5 - (negative_count / 10)
            else:
                emotional_tone = "neutral"
                sentiment_score = 0.5
            
            # CORE INSIGHTS
            insights = []
            
            if engagement_rate > 5.0:
                insights.append("High audience engagement - strong community")
            elif engagement_rate < 1.0:
                insights.append("Low engagement - consider more interactive content")
            
            if view_count > 100000:
                insights.append("Viral potential detected")
            
            if like_count > view_count * 0.05:
                insights.append("Strong positive reception")
            
            # TREND POTENTIAL (based on real metrics)
            trend_score = min(100, (
                (view_count / 1000) * 0.3 +
                engagement_rate * 5 +
                (like_count / 100) * 0.2
            ))
            
            # TARGET AUDIENCE (inferred from category and tags)
            category = snippet.get('categoryId', 'Unknown')
            tags = snippet.get('tags', [])
            
            # RECOMMENDED BRAIN-SYNC
            if emotional_tone == "positive" and engagement_rate > 3:
                brain_sync = "motivation"
            elif "relax" in title or "calm" in title:
                brain_sync = "relax"
            elif "focus" in title or "study" in title:
                brain_sync = "focus"
            elif "sleep" in title or "meditation" in title:
                brain_sync = "sleep"
            else:
                brain_sync = "creativity"
            
            return {
                "metadata": {
                    "title": snippet.get('title'),
                    "channel": snippet.get('channelTitle'),
                    "published_at": snippet.get('publishedAt'),
                    "category_id": category
                },
                "real_metrics": {
                    "views": view_count,
                    "likes": like_count,
                    "comments": comment_count,
                    "engagement_rate_percent": round(engagement_rate, 2)
                },
                "emotional_tone": {
                    "tone": emotional_tone,
                    "sentiment_score": round(sentiment_score, 2)
                },
                "core_insights": insights,
                "trend_potential": round(trend_score, 2),
                "target_audience": {
                    "category": category,
                    "tags": tags[:10],
                    "estimated_age_group": "18-34" if engagement_rate > 3 else "all_ages"
                },
                "recommended_brain_sync": brain_sync
            }
            
        except Exception as e:
            logger.error(f"YouTube insight error: {e}")
            return {"error": str(e)}
