from abstract_visualization import Visualization
import pandas as pd
import os
import requests
import datetime
from datetime import date, timedelta
import matplotlib.pyplot as plt
import plotly.graph_objs as go
import plotly.offline as pyo

class Visual1(Visualization):
    """
    This abstract class is the one that all visualizations will be built on.
    """

    def __init__(self, evening_file, morning_file, sensor_latitude, sensor_longitude, sensor_number):
        self.evening_file = evening_file
        self.morning_file = morning_file

        self.sensor_latitude = sensor_latitude
        self.sensor_longitude = sensor_longitude

        self.sensor_number = sensor_number

        self.morning_data, self.evening_data = self._import_files(), \
                                            self._import_files()
        

    
    def _import_files(self):
        """
        This method pulls the relevant sensor data file for the given night 
        and the following morning from Google Drive. 
        """
        folder = "../streamlit/files/"
        file_path_morn = folder + self.morning_file
        file_path_eve = folder + self.evening_file
        
        col_names = ['Time (UTC)','Time (CST)','Temperature','Frequency','Voltage','Sensor']
        df_morn = pd.read_csv(file_path_morn, low_memory=False, sep=";", names=col_names)
        df_eve = pd.read_csv(file_path_eve, low_memory=False, sep=";", names=col_names)

        return df_morn, df_eve
    
    def _parse_data(self, df):
        """
        This method cleans the data files and organizes it 
        with the relevant column names as a dataframe.
        """

        # Assuming the timestamp column is stored in a variable called "timestamp_str"
        timestamp_format = '%Y-%m-%dT%H:%M:%S.%f'  # Define the format of the timestamp

        df['Time (CST)'] = pd.to_datetime(df['Time (CST)'], format='%Y-%m-%dT%H:%M:%S.%f')
        df["Time (UTC)"] = pd.to_datetime(df['Time (UTC)'], format='%Y-%m-%dT%H:%M:%S.%f')

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

    def _call_apis(self):
        """
        This method pulls the relevant weather and moon phase data for each night 
        from external APIs. 
        """
        api_url = f"https://api.open-meteo.com/v1/forecast?latitude={self.sensor_latitude}&longitude={self.sensor_longitude}&hourly=temperature_2m"
        response = requests.get(api_url)
        response.json()

    def create_visual(self, df_morn, df_eve, t_start: datetime, t_end: datetime):
        """
        This method takes the data from the _construct_data function and returns
        a visual object as an HTML file. 
        """

        df_morn_inbounds = df_morn[df_morn["Time (UTC)"] < t_end]
        df_eve_inbounds = df_eve[df_eve["Time (UTC)"] > t_start]

        df = pd.concat([df_eve_inbounds, df_morn_inbounds])

        x = df["Time (UTC)"]
        y = df["Frequency"]

        # creating the line graph using plotly
        trace = go.Scatter(x=x, y=y, mode='lines')
        data = [trace]
        layout = go.Layout(title=f'{df["Date"][0]} Sensor {self.sensor_number} Dark Sky Observation', xaxis=dict(title='Time (UTC)'), yaxis=dict(title='Light Frequency'))
        fig = go.Figure(data=data, layout=layout)
        pyo.plot(fig, filename='line_graph.html')



if __name__ == "__main__":
    vis1 = Visual1("2022-08-27_LENSSTSL0008.txt", "2022-08-28_LENSSTSL0008.txt", 42.57, -88.542, 8)
    vis1.create_visual()

