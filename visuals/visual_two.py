import os
from datetime import date, datetime, time, timedelta

import astropy.units as astro_units
import julian
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.graph_objs as go
import plotly.offline as pyo
import requests
from astroplan import Observer
from astropy.time import Time
from plotly.subplots import make_subplots

from abstract_visualization import Visualization


class Visual2(Visualization):
    """
    This abstract class is the one that all visualizations will be built on.
    """

    def __init__(
        self,
        evening_file1,
        morning_file1,
        evening_file2,
        morning_file2,
        sensor_latitude,
        sensor_longitude,
        sensor_number,
    ):
        self.evening_file1 = evening_file1
        self.morning_file1 = morning_file1

        self.evening_file2 = evening_file2
        self.morning_file2 = morning_file2

        self.sensor_latitude = sensor_latitude
        self.sensor_longitude = sensor_longitude
        self.sensor_location = Observer(
            longitude=self.sensor_longitude * astro_units.deg,
            latitude=self.sensor_latitude * astro_units.deg,
            elevation=879 * astro_units.m,
        )

        self.sensor_number = sensor_number

        self.m1, self.e1, self.m2, self.e2 = self._import_files()

        self._parse_data(self.m1)
        self._parse_data(self.e1)

        self._parse_data(self.m2)
        self._parse_data(self.e2)

        self.evening_day1 = self.e1.loc[0, "Date"]
        self.morning_day1 = self.m1.loc[0, "Date"]

        self.evening_day2 = self.e2.loc[0, "Date"]
        self.morning_day2 = self.m2.loc[0, "Date"]

    def _import_files(self):
        """
        This method pulls the relevant sensor data file for the given night
        and the following morning from Google Drive.
        """
        folder = "../streamlit/files/"
        file_path_morn1 = folder + self.morning_file1
        file_path_eve1 = folder + self.evening_file1

        file_path_morn2 = folder + self.morning_file2
        file_path_eve2 = folder + self.evening_file2

        col_names = [
            "Time (UTC)",
            "Time (CST)",
            "Temperature",
            "Frequency",
            "Voltage",
            "Sensor",
        ]
        df_morn1 = pd.read_csv(
            file_path_morn1, low_memory=False, sep=";", names=col_names
        )
        df_eve1 = pd.read_csv(
            file_path_eve1, low_memory=False, sep=";", names=col_names
        )

        df_morn2 = pd.read_csv(
            file_path_morn2, low_memory=False, sep=";", names=col_names
        )
        df_eve2 = pd.read_csv(
            file_path_eve2, low_memory=False, sep=";", names=col_names
        )

        return df_morn1, df_eve1, df_morn2, df_eve2

    def _parse_data(self, df):
        """
        This method cleans the data files and organizes it
        with the relevant column names as a dataframe.
        """

        # Assuming the timestamp column is stored in a variable called "timestamp_str"
        timestamp_format = (
            "%Y-%m-%dT%H:%M:%S.%f"  # Define the format of the timestamp
        )

        df["Time (CST)"] = pd.to_datetime(
            df["Time (CST)"], format="%Y-%m-%dT%H:%M:%S.%f"
        )
        df["Time (UTC)"] = pd.to_datetime(
            df["Time (UTC)"], format="%Y-%m-%dT%H:%M:%S.%f"
        )

        df["Day"] = df["Time (UTC)"].dt.day
        df["Month"] = df["Time (UTC)"].dt.month
        df["Year"] = df["Time (UTC)"].dt.year
        df["Date"] = df["Time (UTC)"].apply(lambda x: x.date())

    def _construct_data(self):
        """
        This method constructs all the information needed for the
        class to render the visualization.
        """
        pass

    def _get_moon_info(self, df: pd.DataFrame):
        def get_moon_illum(t: datetime):
            return float(str(self.sensor_location.moon_illumination(str(t))))

        df["moon_illum"] = df["Time (CST)"].apply(lambda t: get_moon_illum(t))

    def _call_apis(self):
        return super()._call_apis()

    def _call_weather_api(self, t_start: datetime, t_end: datetime):
        """
        This method pulls the relevant weather for the night
        from external APIs.

        Returns: dictionary of hours, cloud cover percentages
        """
        api_url = f"https://archive-api.open-meteo.com/v1/archive?latitude={self.sensor_latitude}&longitude={self.sensor_longitude}&start_date={t_start.date()}&end_date={t_end.date()}&hourly=cloudcover&timezone=America%2FChicago"
        response = requests.get(api_url)
        data = response.json()

        if not data:
            raise Exception("Cloud Data Couldn't be Found")

        times = [
            datetime.strptime(time, "%Y-%m-%dT%H:%M%f")
            for time in data["hourly"]["time"]
        ]
        cloudcover = data["hourly"]["cloudcover"]

        cloud_dict = dict(zip(times, cloudcover))
        return {x: cloud_dict[x] for x in cloud_dict if t_start <= x <= t_end}

    def _get_sunset_sunrise(self, t_start: datetime, t_end: datetime):
        sunset_mjd_time = (
            float(
                str(
                    self.sensor_location.sun_set_time(
                        Time(str(t_start)), which="nearest"
                    )
                )
            )
            - 2400000.5
            - (6 * (0.5 / 12))
        )
        sunset_standard_time = julian.from_jd(sunset_mjd_time, fmt="mjd")
        sunset_24time = sunset_standard_time.strftime(("%H:%M"))

        sunrise_mjd_time = (
            float(
                str(
                    self.sensor_location.sun_rise_time(
                        Time(str(t_end)), which="nearest"
                    )
                )
            )
            - 2400000.5
            - (6 * (0.5 / 12))
        )
        sunrise_standard_time = julian.from_jd(sunrise_mjd_time, fmt="mjd")
        sunrise_24time = sunrise_standard_time.strftime(("%H:%M"))

        return sunset_24time, sunrise_24time

    def create_visual(
        self,
        t_start1: datetime,
        t_end1: datetime,
        t_start2: datetime,
        t_end2: datetime,
    ):
        """
        This method takes the data from the _construct_data function and returns
        a visual object as an HTML file.
        """

        df1 = pd.concat([self.e1, self.m1])
        df2 = pd.concat([self.e2, self.m2])

        df1 = df1[
            (df1["Time (CST)"] >= t_start1) & (df1["Time (CST)"] <= t_end1)
        ]
        df2 = df2[
            (df2["Time (CST)"] >= t_start2) & (df2["Time (CST)"] <= t_end2)
        ]

        x1 = df1["Time (CST)"].apply(lambda x: x.time().replace(microsecond=0))
        y1 = df1["Frequency"].rolling(5).mean()
        y2 = df2["Frequency"].rolling(5).mean()

        y3 = df1["Temperature"]
        y4 = df2["Temperature"]

        # Create the first trace object with its own y-axis
        trace1 = go.Scatter(
            x=x1,
            y=y1,
            mode="lines",
            name=f"{self.evening_day1} Light Frequency",
            yaxis="y1",
        )

        # Create the second trace object with its own y-axis
        trace2 = go.Scatter(
            x=x1,
            y=y2,
            mode="lines",
            name=f"{self.evening_day2} Light Frequency",
            yaxis="y1",
        )

        # Create the first trace object with its own y-axis
        trace3 = go.Scatter(
            x=x1,
            y=y3,
            line=dict(dash="dash"),
            name=f"{self.evening_day1} Temp",
            yaxis="y2",
        )

        # Create the second trace object with its own y-axis
        trace4 = go.Scatter(
            x=x1,
            y=y4,
            line=dict(dash="dash"),
            name=f"{self.evening_day2} Temp",
            yaxis="y2",
        )

        # Define the layout object with two y-axes
        layout = go.Layout(
            title=f"{self.evening_day1} and {self.evening_day2} Sensor {self.sensor_number} Dark Sky Observation",
            xaxis=dict(title="Time (CST)"),
            yaxis=dict(title="Light Frequency", side="left"),
            yaxis2=dict(title="Temperature", side="right", overlaying="y"),
        )

        # Add both traces to the data list
        data = [trace1, trace2, trace3, trace4]
        # Create the figure object
        fig = go.Figure(data=data, layout=layout)

        fig.update_layout(
            legend=dict(yanchor="top", y=0.99, xanchor="right", x=0.99)
        )

        self._get_moon_info(df1)
        self._get_moon_info(df2)

        fig.add_annotation(
            text=f'{self.evening_day1} Avg. Moon Illum: {df1["moon_illum"].mean():.1f}',
            x=60,
            y=0.9,
            showarrow=False,
        )
        fig.add_annotation(
            text=f'{self.evening_day2} Avg. Moon Illum: {df2["moon_illum"].mean():.1f}',
            x=60,
            y=0.86,
            showarrow=False,
        )

        cloudcover1 = self._call_weather_api(t_start1, t_end1)
        avg_cloud_cover1 = sum(cloudcover1.values()) / len(cloudcover1)
        fig.add_annotation(
            text=f"{self.evening_day1} Avg. Cloud Cover: {avg_cloud_cover1:.1f}%",
            x=60,
            y=0.82,
            showarrow=False,
        )

        cloudcover2 = self._call_weather_api(t_start2, t_end2)
        avg_cloud_cover2 = sum(cloudcover2.values()) / len(cloudcover2)
        fig.add_annotation(
            text=f"{self.evening_day2} Avg. Cloud Cover: {avg_cloud_cover2:.1f}%",
            x=60,
            y=0.78,
            showarrow=False,
        )

        fig.update_xaxes(ticklabelstep=10)

        # Plot the line graph
        pyo.plot(fig, filename="vis2.html")


if __name__ == "__main__":
    vis1 = Visual2(
        "2022-09-19_LENSSTSL0008.txt",
        "2022-09-20_LENSSTSL0008.txt",
        "2022-12-26_LENSSTSL0008.txt",
        "2022-12-27_LENSSTSL0008.txt",
        42.57,
        -88.542,
        8,
    )

    t_start1 = datetime.combine(vis1.evening_day1, time(22, 0, 0))
    t_end1 = datetime.combine(vis1.morning_day1, time(4, 0, 0))

    t_start2 = datetime.combine(vis1.evening_day2, time(22, 0, 0))
    t_end2 = datetime.combine(vis1.morning_day2, time(4, 0, 0))

    vis1.create_visual(t_start1, t_end1, t_start2, t_end2)
