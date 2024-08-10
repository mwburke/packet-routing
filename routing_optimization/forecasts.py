from dataclasses import dataclass

from pandas import read_csv
from scipy.stats import norm


@dataclass
class ForecastGenerator:
    """Class for generating and adjusting packet forecasts"""

    forecast: dict

    def generate_forecast(self) -> None:
        """
        Generate forecast. In a real case, this would either be a
        time-series model or a way to pull existing forecasts from
        a storage bucket or database.
        """
        df = read_csv("./data/forecasts.csv")
        self.forecast = df.to_dict()

    def adjust_forecasts(self, adjustments: dict) -> None:
        """
        Adjust forecast based on the adjustments dictionary.

        adjustments : dict
            Dictionary where keys are the packet types and values are
            the desired percentile of the normal distribution we want to
            adjust the forecast value to.
        """
        for packet_type, percentile in adjustments.items():
            mean = self.forecast[packet_type]["mean"]
            std_dev = self.forecast[packet_type]["std_dev"]
            self.forecast[packet_type] = self._calculate_adjusted_forecast(
                mean, std_dev, percentile
            )

    def _calculate_adjusted_forecast(mean: float, std_dev: float, percentile: float) -> float:
        """
        Calculate the adjusted forecast based on the mean, standard deviation, and
        percentile of the normal distribution. This allows the user to be more or
        less conservative in their forecast adjustments.
        """
        z_score = norm.ppf(percentile)
        adjusted_forecast = mean + (z_score * std_dev)
        return adjusted_forecast
