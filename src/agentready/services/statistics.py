"""Statistics calculator for benchmarking."""

import math
from typing import List

from ..models.benchmark import Statistics


class StatisticsCalculator:
    """Calculate statistical summaries for benchmarking."""

    def calculate_statistics(self, values: List[float]) -> Statistics:
        """Calculate comprehensive statistics for a list of values.

        Args:
            values: List of numeric values

        Returns:
            Statistics object with mean, median, std_dev, min, max, percentiles

        Raises:
            ValueError: If values list is empty
        """
        if not values:
            raise ValueError("Cannot calculate statistics for empty list")

        # Sort values for percentile calculations
        sorted_values = sorted(values)
        n = len(sorted_values)

        # Calculate basic statistics
        mean = sum(sorted_values) / n
        median = self._calculate_percentile(sorted_values, 50)
        
        # Standard deviation
        variance = sum((x - mean) ** 2 for x in sorted_values) / n
        std_dev = math.sqrt(variance)

        # Min/Max
        min_val = sorted_values[0]
        max_val = sorted_values[-1]

        # Percentiles
        percentiles = {
            "p25": self._calculate_percentile(sorted_values, 25),
            "p50": self._calculate_percentile(sorted_values, 50),
            "p75": self._calculate_percentile(sorted_values, 75),
            "p90": self._calculate_percentile(sorted_values, 90),
            "p95": self._calculate_percentile(sorted_values, 95),
        }

        return Statistics(
            mean=mean,
            median=median,
            std_dev=std_dev,
            min=min_val,
            max=max_val,
            percentiles=percentiles,
        )

    def _calculate_percentile(self, sorted_values: List[float], percentile: float) -> float:
        """Calculate a specific percentile.

        Args:
            sorted_values: Pre-sorted list of values
            percentile: Percentile to calculate (0-100)

        Returns:
            Value at the specified percentile
        """
        if not sorted_values:
            return 0.0

        if percentile <= 0:
            return sorted_values[0]
        if percentile >= 100:
            return sorted_values[-1]

        # Linear interpolation method
        n = len(sorted_values)
        index = (percentile / 100) * (n - 1)
        lower = int(math.floor(index))
        upper = int(math.ceil(index))

        if lower == upper:
            return sorted_values[lower]

        # Interpolate between lower and upper
        weight = index - lower
        return sorted_values[lower] * (1 - weight) + sorted_values[upper] * weight

    def calculate_percentile_rank(self, value: float, all_values: List[float]) -> float:
        """Calculate percentile rank of a value within a distribution.

        Args:
            value: Value to rank
            all_values: All values in the distribution

        Returns:
            Percentile rank (0-100, higher is better)
        """
        if not all_values:
            return 50.0

        # Count how many values are less than or equal to the target
        count_below = sum(1 for v in all_values if v < value)
        count_equal = sum(1 for v in all_values if v == value)

        # Percentile rank formula
        percentile = ((count_below + 0.5 * count_equal) / len(all_values)) * 100

        return percentile

    def calculate_rank(self, value: float, all_values: List[float], higher_is_better: bool = True) -> int:
        """Calculate rank of a value (1 = best).

        Args:
            value: Value to rank
            all_values: All values in the distribution
            higher_is_better: True if higher values are better (default)

        Returns:
            Rank (1-based, 1 is best)
        """
        if not all_values:
            return 1

        sorted_values = sorted(all_values, reverse=higher_is_better)
        
        try:
            # Find position in sorted list
            rank = sorted_values.index(value) + 1
            return rank
        except ValueError:
            # Value not in list, return last rank
            return len(all_values)
