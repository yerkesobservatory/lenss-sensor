from abstract_visualization import Visualization
import pandas as pd
import os
import requests
from datetime import datetime
from datetime import date, timedelta, time
import matplotlib.pyplot as plt
import plotly.graph_objs as go
import plotly.offline as pyo
from plotly.subplots import make_subplots

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

        self.morning_data, self.evening_data = self._import_files()
        self._parse_data(self.morning_data)
        self._parse_data(self.evening_data)

        self.evening_day = self.evening_data.loc[0, "Date"]
        self.morning_day = self.morning_data.loc[0, "Date"]
        

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

        df['Time (CST)'] = df['Time (CST)'].apply(lambda x: x.time())
        df["Time (UTC)"] = df["Time (UTC)"].apply(lambda x: x.time())


    def _construct_data(self):
        """
        This method constructs all the information needed for the
        class to render the visualization.
        """
        pass

    def _get_graph_info(self, t_start: time, t_end: time):
        """
        This method will get moon phase, sunrise/sunset times, 
        cloud cover information, etc.
        """
        cloudcover = self._call_apis(t_start, t_end)

        
        return cloudcover

    def _call_apis(self, t_start: time, t_end: time):
        """
        This method pulls the relevant weather for the night 
        from external APIs. 

        Returns: list of hours, cloud cover percentages
        """
        api_url = f"https://archive-api.open-meteo.com/v1/archive?latitude={self.sensor_latitude}&longitude={self.sensor_longitude}&start_date={self.evening_day}&end_date={self.morning_day}&hourly=cloudcover&timezone=America%2FChicago"
        response = requests.get(api_url)
        data = response.json()

        if not data:
            raise Exception("Cloud Data Couldn't be Found")
        

        times = data["hourly"]["time"]
        cloudcover = data["hourly"]["cloudcover"]

        start = datetime.combine(self.evening_day, t_start)
        end = datetime.combine(self.morning_day, t_end)
        
        res = {}
        for i, time in enumerate(times):
            time_obj = datetime.strptime(time, '%Y-%m-%dT%H:%M%f')
            if start <= time_obj <= end:
                res[time_obj] = cloudcover[i]
        
        return res
        

    def create_visual(self, t_start: time, t_end: time):
        """
        This method takes the data from the _construct_data function and returns
        a visual object as an HTML file. 
        """

        df_morn_inbounds = self.morning_data[self.morning_data["Time (CST)"] < t_end]
        df_eve_inbounds = self.evening_data[self.evening_data["Time (CST)"] > t_start]

        df = pd.concat([df_eve_inbounds, df_morn_inbounds])

        cloudcover = self._get_graph_info(t_start, t_end)
        x1 = df["Time (CST)"]
        x2 = [t.time() for t in cloudcover.keys()]

        y1 = df["Frequency"].rolling(5).mean()
        y2 = list(cloudcover.values())

        # creating the line graph using plotly
        # trace = go.Scatter(x=x, y=y, mode='lines')
        # data = [trace]
        # layout = go.Layout(title=f'{self.evening_day} Sensor {self.sensor_number} Dark Sky Observation', xaxis=dict(title='Time (CST)'), yaxis=dict(title='Light Frequency'))
        # fig = go.Figure(data=data, layout=layout)
        # pyo.plot(fig, filename='line_graph.html')

        # Create subplot with two y-axes
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        # Add traces to the subplot
        fig.add_trace(go.Scatter(x=x1, y=y1, name="Trace 1"), secondary_y=False)
        fig.add_trace(go.Scatter(x=x2, y=y2, name="Trace 2"), secondary_y=True)
        # Set axis labels and title
        fig.update_layout(title="Dual Axis Graph")
        fig.update_xaxes(title_text="X Axis")
        fig.update_yaxes(title_text="Y Axis 1", secondary_y=False)
        fig.update_yaxes(title_text="Y Axis 2", secondary_y=True)
        # Show the plot
        pyo.plot(fig, filename='line_graph.html')



if __name__ == "__main__":
    vis1 = Visual1("2022-10-17_LENSSTSL0008.txt", "2022-10-18_LENSSTSL0008.txt", 42.57, -88.542, 8)
    
    t_start = time(22, 0, 0)
    t_end = time(4, 0, 0)
    vis1.create_visual(t_start, t_end)