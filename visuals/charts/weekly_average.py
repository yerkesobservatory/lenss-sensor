from datetime import datetime, timedelta
from dateutil.relativedelta import *

import io
import numpy as np
import pandas as pd
import plotly.graph_objs as go
import plotly.offline as pyo
import requests

from visuals.charts.abstract_visualization import Visualization
from external.google_docs import GoogleDocs

class WeeklyAverage(Visualization):
    """
    This file contains the functions for creating a graph of the average
    frequency of light detected by the sensor each week for the past six months,
    given an end date, overlaid with data on the weekly total snowfall in the area.
    """

    def __init__(
        self,
        end_date,
        sensor_latitude,
        sensor_longitude,
        sensor_number,
    ):
        self.end_date = end_date
        
        sensor_string = "{:02d}".format(sensor_number)
        start_date = datetime.strptime(end_date[:10], '%Y-%m-%d') - relativedelta(months=6)
        self.start_date = datetime.strftime(start_date, '%Y-%m-%d')

        self.sensor_latitude = sensor_latitude
        self.sensor_longitude = sensor_longitude

        self.sensor_number = sensor_number

        self.df = self._import_files()
        self.series = self._construct_data(self.df)
        self.snowfall = self._call_apis()

    def _import_files(self):
        """
        Based on the start and end date, this method pulls the sensor data
        text files for every night in the given range from Google Drive and
        combines the data into one dataframe.
        """
        start = datetime.strptime(self.start_date, "%Y-%m-%d")
        end = datetime.strptime(self.end_date, "%Y-%m-%d")
        delta = timedelta(days=1)
        filepaths = []

        sensor_string = "{:02d}".format(self.sensor_number)

        while start <= end:
            filepaths.append(
                start.strftime("%Y-%m-%d") + "_LENSSTSL00" + sensor_string + ".txt"
            )
            start += delta

        col_names = [
            "Time (UTC)",
            "Time (CST)",
            "Temperature",
            "Frequency",
            "Voltage",
            "Sensor",
        ]
        docs = GoogleDocs()
        first_night = docs.get_file(filepaths[0])
        df = pd.read_csv(
            io.StringIO('\n'.join(first_night)), sep=';', names=col_names
        )
        self._parse_data(df)
        df = df[(df["Time (CST)"].dt.hour >= 22)]

        for path in filepaths[1:-1]:
            docs = GoogleDocs()
            current = docs.get_file(path)
            curr_df = pd.read_csv(
                io.StringIO('\n'.join(current)), sep=';', names=col_names
            )
            self._parse_data(curr_df)
            curr_df = curr_df[
                (curr_df["Time (CST)"].dt.hour >= 22)
                | (curr_df["Time (CST)"].dt.hour < 4)
            ]
            df = pd.concat([df, curr_df])

        last_morning = docs.get_file(filepaths[-1])
        curr_df = pd.read_csv(
            io.StringIO('\n'.join(last_morning)), sep=';', names=col_names
        )
        self._parse_data(curr_df)
        curr_df = curr_df[(curr_df["Time (CST)"].dt.hour < 4)]
        df = pd.concat([df, curr_df])

        return df

    def _parse_data(self, df):
        """
        This method cleans the data files and organizes it with the relevant
        column names as a dataframe.
        """
        timestamp_format = (
            "%Y-%m-%dT%H:%M:%S.%f"  # Define the format of the timestamp
        )

        df["Time (CST)"] = pd.to_datetime(
            df["Time (CST)"], format=timestamp_format
        )
        df["Time (UTC)"] = pd.to_datetime(
            df["Time (UTC)"], format=timestamp_format
        )

        df["Day"] = df["Time (CST)"].dt.day
        df["Month"] = df["Time (CST)"].dt.month
        df["Year"] = df["Time (CST)"].dt.year
        df["Date"] = df["Time (CST)"].apply(lambda x: x.date())

    @staticmethod
    def _construct_data(df):
        """
        This method constructs all the information needed for the class to
        render the visualization.
        """
        df["date_week"] = pd.to_datetime(df["Date"]) - pd.to_timedelta(
            7, unit="d"
        )
        return df.groupby([pd.Grouper(key="date_week", freq="W")])[
            "Frequency"
        ].mean()

    def _call_apis(self):
        """
        This method pulls the relevant weather, moon phase, etc. data for each
        night from external APIs.
        """
        # weekly snowfall sum
        snowfall = []
        weeks = list(self.series.index.to_pydatetime())

        for week in weeks:
            curr_week = week.strftime("%Y-%m-%d")
            next_week = (week + timedelta(days=7)).strftime("%Y-%m-%d")
            api_url = (
                f"https://archive-api.open-meteo.com/v1/archive"
                f"?latitude={self.sensor_latitude}&longitude="
                f"{self.sensor_longitude}&start_date={curr_week}"
                f"&end_date={next_week}&daily=snowfall_sum"
                f"&timezone=America%2FChicago"
            )
            response = requests.get(api_url)
            data = response.json()

            if not data:
                raise Exception("Snowfall Data Couldn't be Found")

            snowfall.append(np.sum(data["daily"]["snowfall_sum"]))

        return snowfall

    def create_visual(self):
        """
        This method takes the data from the _construct_data function and returns
        a visual object as an HTML file.
        """
        # plotting weekly average frequency
        trace1 = go.Scatter(
            x=self.series.index,
            y=self.series,
            name="Frequency",
            mode="lines",
            yaxis="y1",
        )

        # plotting weekly total snowfall
        self._call_apis()
        trace2 = go.Scatter(
            x=self.series.index,
            y=self.snowfall,
            name="Snowfall",
            yaxis="y2",
            line=dict(dash="dash"),
        )

        data = [trace1, trace2]
        layout = go.Layout(
            title=f"{self.start_date} to {self.end_date}: Weekly Average "
            f"Frequency of Sensor {self.sensor_number} Dark Sky "
            f"Observations",
            xaxis=dict(title="Week"),
            yaxis=dict(title="Average Light Frequency", side="left"),
            yaxis2=dict(
                title="Total Snowfall (cm)", side="right", overlaying="y"
            ),
        )

        fig = go.Figure(data=data, layout=layout)

        fig.update_layout(
            legend=dict(yanchor="top", y=0.99, xanchor="right", x=0.99)
        )

        pyo.plot(fig, filename="Weekly_Average.html")
