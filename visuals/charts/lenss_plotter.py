from datetime import datetime, time, timedelta

import astropy.units as astro_units
import io
import julian
import pandas as pd
import plotly.graph_objs as go
import plotly.offline as pyo
import requests
from astroplan import Observer
from astropy.time import Time

from visuals.charts.abstract_visualization import Visualization
from external.google_docs import GoogleDocs


class LENSSPlotter(Visualization):
    """
    This file contains the functions for creating a graph of the frequency of
    light detected by a given sensor over the course of one night, along with
    moon illumination. Other info about sunrise/sunset, average cloud cover,
    and average temperature is included.
    """

    def __init__(
        self,
        evening_file,
        sensor_latitude,
        sensor_longitude,
        sensor_number,
    ):
        self.evening_file = evening_file
        sensor_string = "{:02d}".format(sensor_number)
        morn_date = datetime.strptime(evening_file[:10], '%Y-%m-%d') + timedelta(days=1)
        self.morning_file = datetime.strftime(morn_date,'%Y-%m-%d') + "_LENSSTSL00" + sensor_string + ".txt"

        self.sensor_latitude = sensor_latitude
        self.sensor_longitude = sensor_longitude
        self.sensor_location = Observer(
            longitude=self.sensor_longitude * astro_units.deg,
            latitude=self.sensor_latitude * astro_units.deg,
            elevation=879 * astro_units.m,
        )

        self.sensor_number = sensor_number

        self.morning_data, self.evening_data = self._import_files()

        self._parse_data(self.morning_data)
        self._parse_data(self.evening_data)

        self.evening_day = self.evening_data.loc[0, "Date"]
        self.morning_day = self.morning_data.loc[0, "Date"]

    def _import_files(self):
        """
        Given the name of two files as strings, this method pulls the
        relevant sensor data text file for the given night and the following
        morning from Google Drive.
        """
        docs = GoogleDocs()
        mlist = docs.get_file(self.morning_file)
        elist = docs.get_file(self.evening_file)

        col_names = [
            "Time (UTC)",
            "Time (CST)",
            "Temperature",
            "Frequency",
            "Voltage",
            "Sensor",
        ]
        df_morn = pd.read_csv(io.StringIO('\n'.join(mlist)), sep=';', names=col_names)
        df_eve = pd.read_csv(io.StringIO('\n'.join(elist)), sep=';', names=col_names)

        return df_morn, df_eve

    def _parse_data(self, df):
        """
        This method cleans the data files and organizes it
        with the relevant column names as a dataframe.
        """

        # Assuming the timestamp column is stored in a variable called
        # "timestamp_str"
        timestamp_format = (
            "%Y-%m-%dT%H:%M:%S.%f"  # Define the format of the timestamp
        )

        df["Time (CST)"] = pd.to_datetime(
            df["Time (CST)"], format=timestamp_format
        )
        df["Time (UTC)"] = pd.to_datetime(
            df["Time (UTC)"], format=timestamp_format
        )

        df["Day"] = df["Time (UTC)"].dt.day
        df["Month"] = df["Time (UTC)"].dt.month
        df["Year"] = df["Time (UTC)"].dt.year
        df["Date"] = df["Time (UTC)"].apply(lambda x: x.date())

    def _get_moon_info(self, df: pd.DataFrame):
        def get_moon_illum(t: datetime):
            return float(str(self.sensor_location.moon_illumination(str(t))))

        df["moon_illum"] = df["Time (CST)"].apply(lambda t: get_moon_illum(t))

    def _call_weather_api(self, t_start: datetime, t_end: datetime):
        """
        This method pulls the relevant weather for the night
        from external APIs.

        Returns: dictionary of hours, cloud cover percentages
        """
        api_url = (
            f"https://archive-api.open-meteo.com/v1/archive"
            f"?latitude={self.sensor_latitude}&"
            f"longitude={self.sensor_longitude}"
            f"&start_date={self.evening_day}"
            f"&end_date={self.morning_day}&hourly=cloudcover"
            f"&timezone=America%2FChicago"
        )
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
            - 2400000.5  # converting from Julian Date to MJD
            - (6 * (0.5 / 12))
        )
        sunset_standard_time = julian.from_jd(sunset_mjd_time, fmt="mjd")
        sunset_24time = sunset_standard_time.strftime("%H:%M")

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
        sunrise_24time = sunrise_standard_time.strftime("%H:%M")

        return sunset_24time, sunrise_24time

    def create_visual(self):
        """
        This method takes the data from the _construct_data function and returns
        a visual object as an HTML file.
        """
        t_start = datetime.combine(self.evening_day, time(22, 0, 0))
        t_end = datetime.combine(self.morning_day, time(4, 0, 0))

        df = pd.concat([self.evening_data, self.morning_data])

        df = df[(df["Time (CST)"] >= t_start) & (df["Time (CST)"] <= t_end)]

        self._get_moon_info(df)
        cloudcover = self._call_weather_api(t_start, t_end)

        x1 = df["Time (CST)"].apply(lambda x: x.time().replace(microsecond=0))
        y1 = df["Frequency"].rolling(5).mean()
        y2 = df["moon_illum"]

        # Create the first trace object with its own y-axis
        trace1 = go.Scatter(
            x=x1, y=y1, mode="lines", name="Light Frequency", yaxis="y1"
        )

        # Create the second trace object with its own y-axis
        trace2 = go.Scatter(
            x=x1,
            y=y2,
            line=dict(dash="dash"),
            name="Moon Illumination",
            yaxis="y2",
        )

        # Define the layout object with two y-axes
        layout = go.Layout(
            title=f"{self.evening_day} Sensor {self.sensor_number} Dark Sky "
            f"Observation",
            xaxis=dict(title="Time (CST)"),
            yaxis=dict(title="Light Frequency", side="left"),
            yaxis2=dict(
                title="Moon Illumination", side="right", overlaying="y"
            ),
        )

        # Add both traces to the data list
        data = [trace1, trace2]
        # Create the figure object
        fig = go.Figure(data=data, layout=layout)

        # Add an annotation for the sunset/sunrise time
        sunset, sunrise = self._get_sunset_sunrise(t_start, t_end)
        fig.add_annotation(
            text=f"Sunset Time: {sunset}", x=35, y=11, showarrow=False
        )
        fig.add_annotation(
            text=f"Sunrise Time: {sunrise}", x=35, y=10, showarrow=False
        )

        # Add an annotation for the average cloud cover
        avg_cloud_cover = sum(cloudcover.values()) / len(cloudcover)
        fig.add_annotation(
            text=f"Avg. Cloud Cover: {avg_cloud_cover:.1f}%",
            x=35,
            y=9,
            showarrow=False,
        )

        # Add an annotation for the average temperature
        avg_temp = df["Temperature"].mean()
        fig.add_annotation(
            text=f"Avg. Temp (C): {avg_temp:.1f} C", x=35, y=8, showarrow=False
        )

        fig.update_layout(
            legend=dict(yanchor="top", y=0.99, xanchor="right", x=0.99)
        )

        fig.update_xaxes(ticklabelstep=10)

        # Plot the line graph
        pyo.plot(fig, filename="LENSS_Plotter.html")
