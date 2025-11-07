from typing import Optional

from src.components.transcript import SentimentTrajectory, Turn


class SentimentAnalyzer:
    """Context-aware sentiment analysis"""

    EMOTION_KEYWORDS = {
        "FRUSTRATED": {
            "keywords": [
                "frustrating",
                "frustrated",
                "annoying",
                "annoyed",
                "irritated",
                "fed up",
                "tired of this",
                "sick of",
                "can’t deal",
                "bothered",
            ],
            "intensity": 0.7,
        },
        "ANGRY": {
            "keywords": [
                "angry",
                "furious",
                "mad",
                "outraged",
                "livid",
                "enraged",
                "infuriated",
                "hate this",
                "unacceptable",
                "ridiculous",
                "furious about",
            ],
            "intensity": 0.9,
        },
        "DISAPPOINTED": {
            "keywords": [
                "disappointed",
                "let down",
                "expected better",
                "not happy",
                "unsatisfied",
                "underwhelmed",
                "bummed",
                "disheartening",
                "poor experience",
            ],
            "intensity": 0.7,
        },
        "WORRIED": {
            "keywords": [
                "worried",
                "concerned",
                "anxious",
                "nervous",
                "uneasy",
                "afraid",
                "scared",
                "fearful",
                "uncertain",
                "unsure",
                "stressed about",
            ],
            "intensity": 0.6,
        },
        "CONFUSED": {
            "keywords": [
                "confused",
                "unclear",
                "don’t understand",
                "not sure",
                "lost",
                "bewildered",
                "unsure",
                "don’t get it",
                "need clarification",
                "mixed up",
            ],
            "intensity": 0.5,
        },
        "GRATEFUL": {
            "keywords": [
                "thank",
                "thanks",
                "thankful",
                "appreciate",
                "grateful",
                "means a lot",
                "really helpful",
                "much obliged",
                "so kind",
                "great support",
            ],
            "intensity": 0.6,
        },
        "SATISFIED": {
            "keywords": [
                "satisfied",
                "happy",
                "pleased",
                "great",
                "perfect",
                "wonderful",
                "excellent",
                "awesome",
                "amazing",
                "fantastic",
                "love it",
                "delighted",
            ],
            "intensity": 0.8,
        },
        "RELIEVED": {
            "keywords": [
                "relieved",
                "finally",
                "good to know",
                "glad it’s fixed",
                "that helps",
                "phew",
                "thank goodness",
                "much better now",
            ],
            "intensity": 0.6,
        },
        "IMPATIENT": {
            "keywords": [
                "waiting too long",
                "still waiting",
                "hurry up",
                "been waiting",
                "slow response",
                "why is this taking",
                "taking forever",
                "long time",
            ],
            "intensity": 0.65,
        },
        "HOPEFUL": {
            "keywords": [
                "hopeful",
                "optimistic",
                "looking forward",
                "expecting",
                "believe it’ll work",
                "trust it’ll be fine",
                "can’t wait",
                "excited to see",
            ],
            "intensity": 0.5,
        },
        "CALM": {
            "keywords": [
                "calm",
                "relaxed",
                "fine",
                "no rush",
                "take your time",
                "no worries",
                "it’s okay",
                "that’s alright",
            ],
            "intensity": 0.4,
        },
        "APOLOGETIC": {
            "keywords": [
                "sorry",
                "apologize",
                "my bad",
                "forgive me",
                "I didn’t mean to",
                "regret that",
                "please excuse",
                "didn’t realize",
                "won’t happen again",
            ],
            "intensity": 0.5,
        },
        "GRATEFUL_POSITIVE": {
            "keywords": [
                "thank you so much",
                "really appreciate it",
                "you’ve been amazing",
                "incredible help",
                "couldn’t have done it without you",
            ],
            "intensity": 0.7,
        },
        "RESENTFUL": {
            "keywords": [
                "resent",
                "fed up with",
                "done with this",
                "sick of dealing with",
                "can’t stand",
                "this always happens",
                "same issue again",
                "every time",
            ],
            "intensity": 0.75,
        },
        "SURPRISED": {
            "keywords": [
                "surprised",
                "shocked",
                "didn’t expect",
                "wow",
                "unbelievable",
                "didn’t think that would happen",
            ],
            "intensity": 0.6,
        },
        "APATHETIC": {
            "keywords": [
                "whatever",
                "doesn’t matter",
                "I don’t care",
                "meh",
                "it’s fine",
                "not a big deal",
                "whatever you say",
            ],
            "intensity": 0.3,
        },
    }

    def analyze_turn(self, text: str, speaker: str) -> tuple[Optional[str], float]:
        """
        Analyze sentiment of a turn

        Returns:
            (sentiment, confidence)
        """
        text_lower = text.lower()

        # Check for emotion keywords
        detected_emotions = []
        for emotion, config in self.EMOTION_KEYWORDS.items():
            for keyword in config["keywords"]:
                if keyword in text_lower:
                    detected_emotions.append((emotion, config["intensity"]))
                    break

        if not detected_emotions:
            return "NEUTRAL", 0.5

        # Return strongest emotion
        detected_emotions.sort(key=lambda x: x[1], reverse=True)
        return detected_emotions[0]

    def track_trajectory(self, turns: list[Turn]) -> SentimentTrajectory:
        """Track sentiment changes across conversation"""

        # Focus on customer turns
        customer_turns = [t for t in turns if t.speaker == "customer"]

        if not customer_turns:
            return SentimentTrajectory(start="NEUTRAL", end="NEUTRAL")

        # Analyze first and last customer turns
        start_sentiment, _ = self.analyze_turn(customer_turns[0].text, "customer")
        end_sentiment, _ = self.analyze_turn(customer_turns[-1].text, "customer")

        # Track all sentiment changes
        sentiments = []
        for i, turn in enumerate(customer_turns):
            sentiment, confidence = self.analyze_turn(turn.text, "customer")
            if sentiment != "NEUTRAL":
                sentiments.append((i, sentiment, confidence))

        # Detect turning points
        turning_points = []
        for i in range(1, len(sentiments)):
            prev_sentiment = sentiments[i - 1][1]
            curr_sentiment = sentiments[i][1]
            if prev_sentiment != curr_sentiment:
                turning_points.append((sentiments[i][0], curr_sentiment))

        return SentimentTrajectory(
            start=start_sentiment, end=end_sentiment, turning_points=turning_points
        )
