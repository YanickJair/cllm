from typing import Optional

from .._schemas import SentimentTrajectory, Turn
from src.dictionary.en.patterns import EMOTION_KEYWORDS

class SentimentAnalyzer:
    """Context-aware sentiment analysis"""
    def analyze_turn(self, text: str, speaker: str) -> tuple[Optional[str], float]:
        """
        Analyze sentiment of a turn

        Returns:
            (sentiment, confidence)
        Example:
            >>> analyzer = SentimentAnalyzer()
            >>> analyzer.analyze_turn("I'm feeling great", "customer")
            ("POSITIVE", 0.9)
        """
        text_lower = text.lower()

        detected_emotions = []
        for emotion, config in EMOTION_KEYWORDS.items():
            for keyword in config["keywords"]:
                if keyword in text_lower:
                    detected_emotions.append((emotion, config["intensity"]))
                    break

        if not detected_emotions:
            return "NEUTRAL", 0.5

        detected_emotions.sort(key=lambda x: x[1], reverse=True)
        return detected_emotions[0]

    def track_trajectory(self, turns: list[Turn]) -> SentimentTrajectory:
        """Track sentiment changes across conversation
        Args:
            turns (list[Turn]): List of turns in the conversation
        Returns:
            SentimentTrajectory: Sentiment trajectory across the conversation
        Examples:
            >>> analyzer = SentimentAnalyzer()
            >>> turns = [Turn("customer", "I'm feeling great"), Turn("agent", "That's great to hear!"), Turn("customer", "I'm not so sure")]
            >>> analyzer.track_trajectory(turns)
            SentimentTrajectory(start="POSITIVE", end="NEGATIVE")
        """
        customer_turns = [t for t in turns if t.speaker == "customer"]

        if not customer_turns:
            return SentimentTrajectory(start="NEUTRAL", end="NEUTRAL")

        start_sentiment, _ = self.analyze_turn(customer_turns[0].text, "customer")
        end_sentiment, _ = self.analyze_turn(customer_turns[-1].text, "customer")

        sentiments = []
        for i, turn in enumerate(customer_turns):
            sentiment, confidence = self.analyze_turn(turn.text, "customer")
            if sentiment != "NEUTRAL":
                sentiments.append((i, sentiment, confidence))

        turning_points = []
        for i in range(1, len(sentiments)):
            prev_sentiment = sentiments[i - 1][1]
            curr_sentiment = sentiments[i][1]
            if prev_sentiment != curr_sentiment:
                turning_points.append((sentiments[i][0], curr_sentiment))

        return SentimentTrajectory(
            start=start_sentiment, end=end_sentiment, turning_points=turning_points
        )
