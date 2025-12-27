import re
from datetime import datetime
import spacy
from spacy.matcher import Matcher

try:
    import dateparser
except ImportError:
    dateparser = None

from .._schemas import TemporalPattern
from clm_core.dictionary.en.patterns import DAY_NAMES, WORD_TO_NUM


class TemporalAnalyzer:
    """Temporal extractor with natural date, range, and frequency inference."""

    def __init__(self):
        # TODO: receive nlp as argument instead of loading here
        self._nlp = spacy.load("en_core_web_sm", disable=["ner", "parser", "textcat"])
        self._nlp.add_pipe("sentencizer")
        self.matcher = Matcher(self._nlp.vocab)
        self._init_matchers()

    def _init_matchers(self):
        """Define token-level temporal patterns
        Args:
            None
        Returns:
            None
        Examples:
            >>> analyzer = TemporalAnalyzer()
            >>> analyzer._init_matchers()
            >>> analyzer.matcher
            Matcher(...)
        """
        self.matcher.add(
            "RECURRING",
            [
                [{"LOWER": {"IN": ["every", "each"]}}, {"IS_ALPHA": True}],
            ],
        )
        self.matcher.add(
            "DURATION",
            [
                [
                    {
                        "LOWER": {"IN": ["for", "past", "last", "over", "around"]},
                        "OP": "?",
                    },
                    {
                        "LOWER": {
                            "IN": list(WORD_TO_NUM.keys())
                            + [str(i) for i in range(1, 10)]
                        }
                    },
                    {
                        "LOWER": {
                            "IN": ["day", "days", "week", "weeks", "month", "months"]
                        }
                    },
                ]
            ],
        )
        self.matcher.add(
            "DATE_RANGE",
            [
                [
                    {"LOWER": {"IN": ["from", "between"]}},
                    {"IS_ALPHA": True, "OP": "+"},
                    {"LOWER": {"IN": ["to", "and"]}},
                    {"IS_ALPHA": True, "OP": "+"},
                ]
            ],
        )

    def extract(self, text: str) -> TemporalPattern:
        """Extract temporal information from a given text.

        Args:
            text (str): The text to extract temporal information from.

        Returns:
            TemporalPattern: The extracted temporal information.
        Examples:
            >>> analyzer = TemporalAnalyzer()
            >>> analyzer.extract("from Monday to Friday")
            TemporalPattern(days=['MON', 'TUE', 'WED', 'THU', 'FRI'], times=None, duration=None, frequency=None, pattern=None)
        """
        doc = self._nlp(text)

        days = self._extract_days(text)
        times = self._extract_times(text)
        duration = self._extract_duration(doc, text)
        range_duration = self._extract_date_range(doc, text)
        if not duration and range_duration:
            duration = range_duration

        natural_dates = self._extract_natural_dates(text)
        frequency = self._calculate_frequency(times, duration, text)
        pattern = self._build_pattern(times)

        return TemporalPattern(
            days=days or natural_dates.get("days"),
            times=times or natural_dates.get("times"),
            duration=duration or natural_dates.get("duration"),
            frequency=frequency,
            pattern=pattern,
        )

    def _extract_days(self, text: str) -> list[str]:
        """Extract days from a given text.

        Args:
            text (str): The text to extract days from.

        Returns:
            list[str]: The extracted days.
        Examples:
            >>> _extract_days("Monday")
            ['MON']
            >>> _extract_days("Monday, Tuesday")
            ['MON', 'TUE']
        """
        found = []
        text_lower = text.lower()
        for name, code in DAY_NAMES.items():
            if name in text_lower and code not in found:
                found.append(code)
        return found

    @staticmethod
    def _extract_times(text: str) -> list[str]:
        """Extract times from a given text.

        Args:
            text (str): The text to extract times from.

        Returns:
            list[str]: The extracted times.
        Examples:
            >>> _extract_times("10:30 am")
            ['10:30']
            >>> _extract_times("10:30 am, 2:45 pm")
            ['10:30', '14:45']
        """
        text_lower = text.lower()
        times = []
        for match in re.finditer(r"\b(\d{1,2})(?::(\d{2}))?\s?(am|pm)?\b", text_lower):
            hour = int(match.group(1))
            minute = int(match.group(2)) if match.group(2) else 0
            period = match.group(3)
            if period:
                if period == "pm" and hour < 12:
                    hour += 12
                elif period == "am" and hour == 12:
                    hour = 0
            times.append(f"{hour:02d}:{minute:02d}")
        return sorted(set(times))

    def _extract_duration(self, doc, text: str) -> str | None:
        """Extract duration from text.

        Args:
            doc (Doc): The spaCy document.
            text (str): The text to extract duration from.

        Returns:
            str | None: The extracted duration in the format "XhYmZs".
        Examples:
            >>> _extract_duration(None, "for 2 hours")
            '2h'
            >>> _extract_duration(None, "past 3 days")
            '3d'
            >>> _extract_duration(None, "last 4 weeks")
            '4w'
            >>> _extract_duration(None, "over 5 months")
            '5m'
            >>> _extract_duration(None, "around 6 years")
            '6y'
        """
        text_lower = text.lower()
        regex = r"(?:for|past|last|over|around)?\s*(\d+|one|two|three|four|five|six|seven|couple)\s+(day|week|month)s?"
        match = re.search(regex, text_lower)
        if match:
            num = WORD_TO_NUM.get(match.group(1), match.group(1))
            unit = match.group(2)[0]
            return f"{num}{unit}"

        matches = self.matcher(doc)
        for match_id, start, end in matches:
            rule_name = self._nlp.vocab.strings[match_id]
            if rule_name == "DURATION":
                span = doc[start:end]
                match = re.search(regex, span.text.lower())
                if match:
                    num = WORD_TO_NUM.get(match.group(1), match.group(1))
                    unit = match.group(2)[0]
                    return f"{num}{unit}"

        if "since" in text_lower:
            days_mentioned = self._extract_days(text)
            if days_mentioned:
                return f"{len(days_mentioned)}d"
        return None

    def _extract_date_range(self, doc, text: str) -> str | None:
        """Extracts a date range from the given text.

        Args:
            doc (Doc): The spaCy document.
            text (str): The text to extract the date range from.

        Returns:
            str | None: The extracted date range in the format "Xd".
        Example:
            >>> _extract_date_range(doc, "from Monday to Friday")
            "5d"
        """
        matches = self.matcher(doc)
        for match_id, start, end in matches:
            rule_name = self._nlp.vocab.strings[match_id]
            if rule_name == "DATE_RANGE":
                span_text = doc[start:end].text.lower()

                day_matches = [d for d in DAY_NAMES if d in span_text]
                if len(day_matches) >= 2:
                    first = DAY_NAMES[day_matches[0]]
                    second = DAY_NAMES[day_matches[1]]
                    duration_days = self._day_range_length(first, second)
                    return f"{duration_days}d"

                time_matches = re.findall(
                    r"(\d{1,2})(?::(\d{2}))?\s?(am|pm)?", span_text
                )
                if len(time_matches) >= 2:
                    start_t = self._to_24h(time_matches[0])
                    end_t = self._to_24h(time_matches[1])
                    if start_t and end_t:
                        duration_hours = max(0, end_t - start_t)
                        return f"{duration_hours}h"
        return None

    def _extract_natural_dates(self, text: str) -> dict:
        """Natural Date Understanding
        Parse relative/natural date expressions like:
        - 'next Friday', 'this weekend', 'tomorrow at 9', 'last month'
        Args:
            text (str): The input text to parse.

        Returns:
            dict: A dictionary containing parsed information.
        Examples:
            >>> _extract_natural_dates("next Friday")
            {'day': 'Friday', 'duration': '1d'}
            >>> _extract_natural_dates("this weekend")
            {'day': 'weekend', 'duration': '2d'}
            >>> _extract_natural_dates("tomorrow at 9")
            {'day': 'tomorrow', 'time': '09:00', 'duration': '1d'}
            >>> _extract_natural_dates("last month")
            {'month': 'last', 'duration': '1m'}
        """
        if not dateparser:
            return {}

        now = datetime.now()
        parsed = dateparser.parse(text, settings={"RELATIVE_BASE": now})
        if not parsed:
            return {}

        diff = parsed - now
        duration = None
        if abs(diff.days) == 1:
            duration = "1d"
        elif 2 <= abs(diff.days) <= 7:
            duration = f"{abs(diff.days)}d"
        elif abs(diff.days) > 7:
            duration = f"{abs(diff.days) // 7}w"

        day_code = DAY_NAMES.get(parsed.strftime("%A").lower())

        time_str = parsed.strftime("%H:%M") if parsed else None

        return {
            "days": [day_code] if day_code else None,
            "times": [time_str] if time_str and time_str != "00:00" else None,
            "duration": duration,
        }

    @staticmethod
    def _day_range_length(start_day: str, end_day: str) -> int:
        """Calculate the length of a day range.

        Args:
            start_day (str): The start day of the range.
            end_day (str): The end day of the range.

        Returns:
            int: The length of the day range.
        Examples:
            >>> _day_range_length("MON", "FRI")
            5
            >>> _day_range_length("FRI", "MON")
            3
        """
        days = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
        start_idx, end_idx = days.index(start_day), days.index(end_day)
        delta = end_idx - start_idx
        if delta < 0:
            delta += 7
        return delta + 1

    @staticmethod
    def _to_24h(time_tuple) -> float | None:
        """Convert a time tuple to a 24-hour format.

        Args:
            time_tuple (tuple): A tuple containing the hour, minute, and period.

        Returns:
            float | None: The time in 24-hour format or None if the input is invalid.
        Examples:
            >>> _to_24h(("12", "30", "pm"))
            12.5
            >>> _to_24h(("12", "30", "am"))
            0.5
            >>> _to_24h(("12", "30", "pm"))
            12.5
            >>> _to_24h(("12", "30", "am"))
            0.5
        """
        if not time_tuple:
            return None
        hour = int(time_tuple[0])
        minute = int(time_tuple[1]) if time_tuple[1] else 0
        period = time_tuple[2]
        if period == "pm" and hour < 12:
            hour += 12
        elif period == "am" and hour == 12:
            hour = 0
        return hour + minute / 60

    @staticmethod
    def _calculate_frequency(times, duration, text: str) -> str | None:
        """Calculate the frequency of a given time pattern.

        Args:
            times (list[str]): A list of time patterns.
            duration (str): The duration of the time pattern.
            text (str): The text containing the time pattern.

        Returns:
            str | None: The frequency of the time pattern or None if the input is invalid.
        Examples:
            >>> _calculate_frequency(["12:30pm", "12:30am"], "1d", "twice daily")
            '2x_daily'
            >>> _calculate_frequency(["12:30pm", "12:30am"], "1w", "every day")
            '1x_daily'
            >>> _calculate_frequency(["12:30pm", "12:30am"], "1d", "twice daily")
            '2x_daily'
            >>> _calculate_frequency(["12:30pm", "12:30am"], "1w", "every day")
            '1x_daily'
        """
        num_occurrences = len(times)
        text_lower = text.lower()

        if "twice" in text_lower:
            return "2x_daily"
        if "every" in text_lower or "each" in text_lower:
            return "1x_daily"

        if duration:
            m = re.match(r"(\d+)([dwmh])", duration)
            if m:
                num, unit = int(m.group(1)), m.group(2)
                if unit == "d" and num == 1:
                    return f"{num_occurrences}x_daily"
                elif unit == "w" and num == 1:
                    return f"{num_occurrences}x_weekly"

        if num_occurrences >= 2:
            return f"{num_occurrences}x_daily"

        return None

    @staticmethod
    def _build_pattern(times: list[str]) -> str | None:
        return "+".join(times) if times else None
