import re

from src.components.transcript import TemporalPattern


class TemporalAnalyzer:
    """Extract detailed temporal information"""

    # Day name mappings
    DAY_NAMES = {
        'monday': 'MON', 'tuesday': 'TUE', 'wednesday': 'WED',
        'thursday': 'THU', 'friday': 'FRI', 'saturday': 'SAT', 'sunday': 'SUN',
        'mon': 'MON', 'tue': 'TUE', 'wed': 'WED', 'thu': 'THU',
        'fri': 'FRI', 'sat': 'SAT', 'sun': 'SUN'
    }

    def extract(self, text: str) -> TemporalPattern:
        """Extract complete temporal pattern from text"""

        days = self._extract_days(text)
        times = self._extract_times(text)
        duration = self._extract_duration(text)
        frequency = self._calculate_frequency(times, duration)
        pattern = self._build_pattern(times)

        return TemporalPattern(
            days=days,
            times=times,
            duration=duration,
            frequency=frequency,
            pattern=pattern
        )

    def _extract_days(self, text: str) -> list[str]:
        """Extract day names from text"""
        text_lower = text.lower()
        days = []

        for day_name, day_code in self.DAY_NAMES.items():
            if day_name in text_lower:
                if day_code not in days:
                    days.append(day_code)

        return days

    @staticmethod
    def _extract_times(text: str) -> list[str]:
        """
        Extract times from text

        Patterns:
        - 9am, 9:00am, 9 am
        - 1pm, 1:00pm, 1 pm
        - 6pm, 18:00
        """
        times = []

        # Pattern 1: "9am", "1pm"
        pattern1 = re.finditer(r'\b(\d{1,2})\s?(am|pm)\b', text.lower())
        for match in pattern1:
            hour = match.group(1)
            period = match.group(2)
            times.append(f"{hour}{period}")

        # Pattern 2: "9:00am", "1:30pm"
        pattern2 = re.finditer(r'\b(\d{1,2}):(\d{2})\s?(am|pm)\b', text.lower())
        for match in pattern2:
            hour = match.group(1)
            period = match.group(3)
            times.append(f"{hour}{period}")

        # Pattern 3: "around 9", "around 1", "around 6" (infer from context)
        pattern3 = re.finditer(r'around (\d{1,2})', text.lower())
        for match in pattern3:
            hour = int(match.group(1))
            # Heuristic: if mentioned with work, assume business hours
            if 6 <= hour <= 11:
                times.append(f"{hour}am")
            elif 1 <= hour <= 6:
                times.append(f"{hour}pm")

        # Remove duplicates while preserving order
        seen = set()
        unique_times = []
        for time in times:
            if time not in seen:
                seen.add(time)
                unique_times.append(time)

        return unique_times

    def _extract_duration(self, text: str) -> str:
        """
        Extract duration

        Patterns:
        - "past three days" → "3d"
        - "for 2 weeks" → "2w"
        - "since Monday" → calculate
        """
        text_lower = text.lower()

        # Pattern 1: "X days/weeks/months"
        match = re.search(r'(\d+|one|two|three|four|five|six|seven)\s+(day|week|month)s?', text_lower)
        if match:
            num_str = match.group(1)
            unit = match.group(2)

            # Convert words to numbers
            word_to_num = {
                'one': 1, 'two': 2, 'three': 3, 'four': 4,
                'five': 5, 'six': 6, 'seven': 7
            }
            num = word_to_num.get(num_str, num_str)

            # Convert to compact format
            unit_code = unit[0]  # d, w, m
            return f"{num}{unit_code}"

        # Pattern 2: "past X days"
        match = re.search(r'past (\d+|one|two|three|four|five)\s+days?', text_lower)
        if match:
            num_str = match.group(1)
            word_to_num = {'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5}
            num = word_to_num.get(num_str, num_str)
            return f"{num}d"

        # Pattern 3: "since Monday/Tuesday" (calculate from context)
        days_mentioned = self._extract_days(text)
        if days_mentioned and 'since' in text_lower:
            # Simple heuristic: if multiple days mentioned, it's been that many days
            return f"{len(days_mentioned)}d"

        return None

    @staticmethod
    def _calculate_frequency(times: list[str], duration: str) -> str | None:
        """
        Calculate frequency from times and duration

        Examples:
        - 3 times, 1 day → "3x_daily"
        - 2 times, 1 week → "2x_weekly"
        """
        if not times:
            return None

        num_occurrences = len(times)

        if duration:
            # Extract number from duration (e.g., "3d" → 3)
            match = re.match(r'(\d+)([dwm])', duration)
            if match:
                num_units = int(match.group(1))
                unit = match.group(2)

                if unit == 'd' and num_units == 1:
                    return f"{num_occurrences}x_daily"
                elif unit == 'w' and num_units == 1:
                    return f"{num_occurrences}x_weekly"

        # Default: if we see multiple times mentioned, assume daily
        if num_occurrences >= 2:
            return f"{num_occurrences}x_daily"

        return None

    @staticmethod
    def _build_pattern(times: list[str]) -> str | None:
        """
        Build pattern string from times

        Example: ["9am", "1pm", "6pm"] → "9am+1pm+6pm"
        """
        if not times:
            return None

        return '+'.join(times)