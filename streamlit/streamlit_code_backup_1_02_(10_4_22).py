# -*- coding: utf-8 -*-
"""Streamlit Code Backup 1.02 (10/4/22)

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1gk4FpXHhs5H4v6RYh2-0SUbAfebNSgzy
"""

# In order to connect via another device, http://192.168.7.157:(localhostid)
# localhostid can be found in the search bar once the app is opened on the
# main server computer

# Current Bugs: None! To-do: Automate downloads from the drive Add map of
# roughly where each sensor is located Refine Code (Add loops and such for
# excessive if statements) Use st.select_slider to change the visible parts
# of the graph (Unviable, conflicts with custom_x/y too much and would
# require and entire rework of the code) Add a 'heat map' of where light
# pollution is higher than others Add calendar of what days have data for
# each sensor

# Imports
import pandas
import matplotlib.pyplot as plt
import numpy as np
from numpy import random as r
import csv
import streamlit as st
import plotly.express as px
from datetime import datetime
from datetime import timedelta
from PIL import Image

# Page setup
st.set_page_config(
    page_title="LENSS Sensor Plotting",
    page_icon="🌠",
    initial_sidebar_state="expanded",
)

# Login Page, only allows access once the correct password is entered
with st.form("Login"):
    input_password = st.text_input("Please Input Password", "")
    submitted = st.form_submit_button("Submit")

if input_password == "Y3rke5*":
    st.success("Correct Password!")
else:
    st.stop()

# Page setup that is only visible once the password is entered
st.title("LENSS Sensor Plotting")
st.subheader("Configure the plot")
# Night/Sensor selection
sensor_selection = st.selectbox(
    label="Choose a Sensor", options=("Sensor 5", "Sensor 11", "Sensor 12")
)
st.caption("Listed sensors have all available data from 2022-06-01 to today")
day_selection = st.date_input(
    "Choose a Night", datetime.date(datetime.now() - timedelta(2))
)
# Finds out the current date
morning_selection = day_selection + timedelta(days=1)

# Prepares variable names, depending on selection, for later
# Format of data varies with sensor number 
# Because the sensor saves data on a per day basis, 
# two files need to be opened to gather data for one night
# (evening data for the first and morning for the second).
if sensor_selection == "Sensor 5":
    filename = str(day_selection) + "_LENSSTSL0005"
    filename2 = str(morning_selection) + "_LENSSTSL0005"
    sensornumber = "05"
    filetype = "Old"

if sensor_selection == "Sensor 11":
    filename = str(day_selection) + "_LENSSTSL0011"
    filename2 = filename2 = str(morning_selection) + "_LENSSTSL0011"
    sensornumber = "11"
    filetype = "Old"

if sensor_selection == "Sensor 12":
    filename = str(day_selection) + "_LENSSTSL12"
    filename2 = str(morning_selection) + "_LENSSTSL12"
    sensornumber = "12"
    filetype = "New"

# Imports files
morning_error = False
night_error = False
if filetype == "New":
    try:
        sensor = pandas.read_csv(
            "files/" + filename + ".txt",
            sep=";",
            names=[
                "UTC",
                "CST",
                "Temperature",
                "Frequency",
                "Voltage",
                "Sensor Number",
            ],
        )
    except:
        morning_error = True
    try:
        sensor2 = pandas.read_csv(
            "files/" + filename2 + ".txt",
            sep=";",
            names=[
                "UTC",
                "CST",
                "Temperature",
                "Frequency",
                "Voltage",
                "Sensor Number",
            ],
        )
    except:
        night_error = True
else:
    try:
        sensor = pandas.read_csv(
            "files/" + filename + ".txt",
            names=["Time", "Voltage", "Frequency", "Temperature", "Sensors"],
        )
    except:
        morning_error = True
    try:
        sensor2 = pandas.read_csv(
            "files/" + filename2 + ".txt",
            names=["Time", "Voltage", "Frequency", "Temperature", "Sensors"],
        )
    except:
        night_error = True

    # Feedback/Error messages if file is unavailable
if morning_error:
    st.error("Missing File For The Morning!")
    if night_error:
        st.error("Missing File For The Night!")
        st.stop()
if night_error:
    st.error("Missing File For The Night!")
if night_error or morning_error:
    st.stop()

# Sets up more variable names for later
Frequency = sensor["Frequency"].to_list()
Frequency2 = sensor2["Frequency"].to_list()
Temperature = sensor["Temperature"].to_list()
Temperature2 = sensor2["Temperature"].to_list()

# Finds the last 0 in the first file (for the night)
# Last 0 marks astronomical twilight 
# (last stage of dusk/beginning of night)
last0 = len(Frequency) - 1
while Frequency[last0] != 0:
    last0 = last0 - 1

# In the event that there are zeros elsewhere in the data (ex. S5
# 2022-08-08), moves it back 2 hours (120 minutes) and restarts the process
hours2 = 120
if last0 > len(Frequency[: len(Frequency) - hours2]):
    last0 = len(Frequency) - hours2
    while Frequency[last0] != 0:
        last0 = last0 - 1

Frequency_Night = Frequency[last0 + 1:]

# Finds the first 0 in the second file (for the morning)
# First 0 in the mornining is the beginning of dawn
first0 = 240
while Frequency2[first0] != 0:
    first0 = first0 + 1
Frequency_Morning = Frequency2[0: first0 - 1]

# These three lines limit the amount of downward/upward curve on the
# night/day half of the graph. It does so by finding a mean, and working its
# way forward/backward from there, eliminating any part that is above the mean.

morning_mean = sum(Frequency_Morning[: len(Frequency_Morning) - 60]) / (
        len(Frequency_Morning) - 60
)
while sum(Frequency_Night[:5]) / 5 > morning_mean + 2:
    Frequency_Night = Frequency_Night[5:]
while (
        sum(Frequency_Morning[
            len(Frequency_Morning) - 5:]) / 5 > morning_mean + 2
):
    Frequency_Morning = Frequency_Morning[: len(Frequency_Morning) - 5]

# List of all the useful data for the night
night = Frequency_Night + Frequency_Morning

# Detects which sensor was selected, and then removes it from the list so
# duplicates are not visible on the overlay
sensor_options = ["Sensor 5", "Sensor 11", "Sensor 12"]
for word in [w for w in list(sensor_options) if w in sensor_selection]:
    sensor_options.remove(word)

    # Graph customization, variable names make it self-explanatory
with st.sidebar:
    st.title("Customize Graph")
    timestamps = st.checkbox("Add Timestamps?", value=True)
    hour_labels = st.checkbox("Add Hour Labels?")
    meandisplay = st.checkbox("Add Mean?", value=True)
    trendline = st.checkbox("Add Trendline?")
    goal_line = st.checkbox("Add Goal?")
    overlay_toggle = st.radio(
        "Overlay Other Sensor Data?", ("Deny Overlay", "Allow Overlay")
    )
    if overlay_toggle == "Allow Overlay":
        overlay_options = st.radio("Available Overlays", (sensor_options))

    # Colors!
    with st.expander("Choose Colors", expanded=False):
        option_column1, option_column2 = st.columns(2)
        with option_column1:
            main_color = st.color_picker("Main Color", "#FF0000")
            midnight_color = st.color_picker("Midnight Color", "#0000FF")
            hours_color = st.color_picker("Hours Color", "#000000")
        with option_column2:
            if goal_line:
                goal_color = st.color_picker("Goal Color", "#ff6600")
            if overlay_toggle == "Allow Overlay":
                overlay_color = st.color_picker("Overlay Color", "#008000")
            if trendline:
                trendline_color = st.color_picker("Trendline Color", "#000000")

    # Allows user to select whether the temp should be read in Celsius or
    # Fahrenheit
    c_or_f = st.radio(
        "Read temperatures in Celsius of Fahrenheit?", ("Celsius", "Fahrenheit")
    )

# Lets the user change the X-Axis and Y-Axis to whatever they like, so long
# as it is actually within the graph, defaults to the length of the graph and
# a Y-Axis of 50
with st.expander("Advanced Options", expanded=False):
    custom_x = st.slider(
        "Select the X-Axis values of the graph:", value=(0, len(night))
    )
    custom_y = st.slider("Select the Y-Axis values of the graph:", 0, 100, 50)
    st.caption("Warning: A Y-Axis below 10 is not recommended")

    # Finds the mean of the visible range
custom_night_sum = sum(night[list(custom_x)[0]: list(custom_x)[1]])
custom_length = len(night[list(custom_x)[0]: list(custom_x)[1]])
mean = custom_night_sum / custom_length

# Begins creating the graph
fig, ax = plt.subplots()

# Adds lines to the graph to help the viewer visualize when points on the
# graph actually are
if timestamps:
    plt.plot(
        [len(Frequency_Night), len(Frequency_Night)],
        [-1, sum(Frequency_Night[len(Frequency_Night) - 2:]) / 2],
        color=midnight_color,
        linestyle="solid",
        linewidth=2,
        label="Midnight",
    )

    PM_Plotting_Loop = len(Frequency_Night)
    while PM_Plotting_Loop - 60 > list(custom_x)[0]:
        PM_Plotting_Loop = PM_Plotting_Loop - 60
        plottingloop_X = [PM_Plotting_Loop, PM_Plotting_Loop]
        plottingloop_Y = [
            -1,
            sum(Frequency_Night[PM_Plotting_Loop: PM_Plotting_Loop + 1]),
        ]
        plt.plot(
            plottingloop_X,
            plottingloop_Y,
            color=hours_color,
            linestyle="solid",
            linewidth=2,
        )

    AM_Plotting_Loop = len(Frequency_Night)
    while AM_Plotting_Loop + 60 < list(custom_x)[1]:
        AM_Plotting_Loop = AM_Plotting_Loop + 60
        plottingloop_X = [AM_Plotting_Loop, AM_Plotting_Loop]
        plottingloop_Y = [
            -1,
            sum(night[AM_Plotting_Loop: AM_Plotting_Loop + 1]),
        ]
        plt.plot(
            plottingloop_X,
            plottingloop_Y,
            color=hours_color,
            linestyle="solid",
            linewidth=2,
        )

# When activated, adds a goal line to the graph by doing some totally complex
# math
if goal_line:
    plt.plot(
        range(len([x - (mean - 3) for x in night])),
        [x - (mean - 3) for x in night],
        color=goal_color,
        linestyle="solid",
        linewidth=2,
        label="Goal",
    )

# Sets Y-Axis values for the text in hour_labels to make them easy to view
if hour_labels:
    if custom_y <= 10:
        hour_labels_y = -0.5
    if 30 > custom_y > 10:
        hour_labels_y = -1
    if 30 <= custom_y <= 85:
        hour_labels_y = -3
    if custom_y > 85:
        hour_labels_y = -4

# When toggled on, these loops add labeled hour markers to the bottom of the
# graph, can be buggy when the night is long
if hour_labels:
    if list(custom_x)[0] < len(Frequency_Night) and list(custom_x)[1] > len(
            Frequency_Night
    ):
        plt.text(len(Frequency_Night), hour_labels_y, "\ 12 AM")

    # Variables for future use
Midnight_PM = 12
Midnight_AM = 0

# Loops that 'plot' the text on the graph. They do the same thing as the
# previous two loops, except they add text and are a bit more complex
if hour_labels:
    PM_Label_Loop = len(Frequency_Night)
    while PM_Label_Loop - 60 > list(custom_x)[0]:
        while PM_Label_Loop - 60 > list(custom_x)[1]:
            PM_Label_Loop = PM_Label_Loop - 60
            Midnight_PM = Midnight_PM - 1
        PM_Label_Loop = PM_Label_Loop - 60
        Midnight_PM = Midnight_PM - 1
        if 0 < PM_Label_Loop < list(custom_x)[1]:
            plt.text(
                PM_Label_Loop, hour_labels_y, "\ " + str(Midnight_PM) + " PM"
            )

    AM_Label_Loop = len(Frequency_Night)
    while AM_Label_Loop + 60 < list(custom_x)[1]:
        while AM_Label_Loop + 60 < list(custom_x)[0]:
            AM_Label_Loop = AM_Label_Loop + 60
            Midnight_AM = Midnight_AM + 1
        AM_Label_Loop = AM_Label_Loop + 60
        Midnight_AM = Midnight_AM + 1
        if 0 < AM_Label_Loop < list(custom_x)[1]:
            plt.text(
                AM_Label_Loop, hour_labels_y, "\ " + str(Midnight_AM) + " AM"
            )

# Imports overlay files
if overlay_toggle == "Allow Overlay":
    if overlay_options == "Sensor 5":
        additional_sensor_number = "05"

    if overlay_options == "Sensor 11":
        additional_sensor_number = "11"

    try:
        addition1night = pandas.read_csv(
            "files/"
            + (str(day_selection) + "_LENSSTSL00" + additional_sensor_number)
            + ".txt",
            names=["Time", "Voltage", "Frequency", "Temperature", "Sensors"],
        )
    except:
        night_error = True
    try:
        addition1morning = pandas.read_csv(
            "files/"
            + (
                    str(morning_selection)
                    + "_LENSSTSL00"
                    + additional_sensor_number
            )
            + ".txt",
            names=["Time", "Voltage", "Frequency", "Temperature", "Sensors"],
        )
    except:
        morning_error = True

    if overlay_options == "Sensor 12":
        additional_sensor_number = "12"
        try:
            addition1night = pandas.read_csv(
                "files/" + (str(day_selection) + "_LENSSTSL12") + ".txt",
                sep=";",
                names=[
                    "UTC",
                    "CST",
                    "Temperature",
                    "Frequency",
                    "Voltage",
                    "Sensor Number",
                ],
            )
        except:
            night_error = True
        try:
            addition1morning = pandas.read_csv(
                "files/" + (str(morning_selection) + "_LENSSTSL12") + ".txt",
                sep=";",
                names=[
                    "UTC",
                    "CST",
                    "Temperature",
                    "Frequency",
                    "Voltage",
                    "Sensor Number",
                ],
            )
        except:
            morning_error = True

    # Detects if an overlay file is missing
    if morning_error:
        st.error("Missing File For The Morning Of Overlay!")
        if night_error:
            st.error("Missing File For The Night Of Overlay!")
            st.stop()
    if night_error:
        st.error("Missing File For The Night Of Overlay!")
    if night_error or morning_error:
        st.stop()

    # Basically repeats what happened with the first file earlier, only now
    # with the optional overlay
    if overlay_options == "Sensor 5" or "Sensor 11" or "Sensor 12":
        Frequency_Night_Overlay = addition1night["Frequency"].to_list()
        Frequency_Morning_Overlay = addition1morning["Frequency"].to_list()
        Additional_last0 = len(Frequency_Night_Overlay) - 1
        while Frequency_Night_Overlay[Additional_last0] != 0:
            Additional_last0 = Additional_last0 - 1
        if Additional_last0 > len(
                Frequency_Night_Overlay[: len(Frequency_Night_Overlay) - 120]
        ):
            Additional_last0 = len(Frequency_Night_Overlay) - 120
            while Frequency_Night_Overlay[Additional_last0] != 0:
                Additional_last0 = Additional_last0 - 1

        Frequency_Night_Overlay = Frequency_Night_Overlay[
                                  Additional_last0 + 1:
                                  ]
        Additional_first0 = 240
        while Frequency_Morning_Overlay[Additional_first0] != 0:
            Additional_first0 = Additional_first0 + 1
        Frequency_Morning_Overlay = Frequency_Morning_Overlay[
                                    0: Additional_first0 - 1
                                    ]
        Additional_morningmean = sum(Frequency_Morning_Overlay) / len(
            Frequency_Morning_Overlay
        )
        while sum(Frequency_Night_Overlay[:5]) / 5 > Additional_morningmean + 2:
            Frequency_Night_Overlay = Frequency_Night_Overlay[5:]
        while (
                sum(Frequency_Morning_Overlay[
                    len(Frequency_Morning_Overlay) - 5:])
                / 5
                > Additional_morningmean + 2
        ):
            Frequency_Morning_Overlay = Frequency_Morning_Overlay[
                                        : len(Frequency_Morning_Overlay) - 5
                                        ]
        additional_night = Frequency_Night_Overlay + Frequency_Morning_Overlay

# Adds the overlay plot to the graph, does this before the main line for the
# night gets added in order to have the main line be over this one
if overlay_toggle == "Allow Overlay":
    plt.plot(
        range(
            len(Frequency_Night) - len(Frequency_Night_Overlay),
            len(additional_night)
            + len(Frequency_Night)
            - len(Frequency_Night_Overlay),
        ),
        additional_night,
        linestyle="solid",
        linewidth=3,
        c=overlay_color,
        label=overlay_options,
    )

# Plots the main line for the night
arr = plt.plot(
    range(len(night)),
    night,
    linestyle="solid",
    linewidth=3,
    c=main_color,
    label=sensor_selection,
)

# Sets axis to what was set earlier, defaults to the len(night) and a Y-Axis
# of 50
plt.axis([list(custom_x)[0], list(custom_x)[1], 0, custom_y])

# Adds a legend for the lines so you can tell them apart
plt.legend(loc="upper right")

# Sets a title, and if there is an overlay it will add the overlay to the
# title, if not, no overlay is added to the title
if overlay_toggle == "Allow Overlay":
    plt.title(
        "TSL 00"
        + sensornumber
        + " and TSL 00"
        + additional_sensor_number
        + " Night of "
        + filename[0:10]
    )
if overlay_toggle == "Deny Overlay":
    plt.title("TSL 00" + sensornumber + " Night of " + filename[0:10])

# Plots the trendline
if trendline:
    plt.plot(
        [0, len(night)],
        [sum(Frequency_Night[:20]) / 20, morning_mean],
        color=trendline_color,
        linewidth=1.5,
    )

# Labels the graph, if the hour labels are toggled on the default Time (
# Hours) will be removed. Also adds the Y-Axis label and removes the default
# labels that the graph would have, ex. (1, 2, 3, 4, 5, 6...)
plt.xlabel("Time (Hours)")
if hour_labels:
    plt.xlabel("")
plt.ylabel("Frequency")
plt.xticks([])

# Adds the mean to the top left of the graph
if meandisplay and custom_y > mean + 2:
    plt.text(
        0.1,
        0.9,
        "Mean = " + str(round(mean, 2)),
        ha="center",
        va="center",
        transform=ax.transAxes,
    )

# Saves the file to allow its potential download, may need to be fixed as it
# could cause storage problems
plt.savefig(
    "Images/TSL " + filename[19:] + " Night of " + filename[0:10] + ".png"
)
# Ends graph creation and displays it
st.pyplot(fig)

# Error/Success messages depending on if the mean could be safely displayed
# without interfereing with the important data
if custom_y < mean + 2 and meandisplay:
    st.warning("Unable to safely display the mean!")

if custom_y > mean + 2 and meandisplay:
    st.success("Graph Created Successfully!")

if not meandisplay:
    st.success("Graph Created Successfully!")

# Creates variable names for the temperature to be displayed later
combined_temp = Temperature[last0:] + Temperature2[0: Frequency2.index(0) - 50]
combined_temp = combined_temp[list(custom_x)[0]: list(custom_x)[1]]
temp_unit = "°C"
# Converts Celsius to Fahrenheit if the user selected that
if c_or_f == "Fahrenheit":
    combined_temp = [x * 9 / 5 + 32 for x in combined_temp]
    temp_unit = "°F"

temp_mean = round(sum(combined_temp) / len(combined_temp), 1)
temp_min = min(combined_temp)
temp_max = max(combined_temp)

# Displays the temperature below the graph, showing the difference between
# the mean for the night and the highest/lowest temp
temperature_column1, temperature_column2, temperature_column3 = st.columns(3)
temperature_column1.metric(
    "Mean Temperature", str(round((temp_mean), 1)) + temp_unit
)
temperature_column2.metric(
    "Lowest Temperature",
    str(round((temp_min), 1)) + temp_unit,
    "-" + str(round((temp_mean - temp_min), 1)) + temp_unit,
)
temperature_column3.metric(
    "Highest Temperature",
    str(round((temp_max), 1)) + temp_unit,
    str(round((temp_max - temp_mean), 1)) + temp_unit,
)

# Creates a variable name with the file name (was saved earlier) in order for
# download by the viewer
image_name = (
        "Images/TSL " + filename[19:] + " Night of " + filename[0:10] + ".png"
)

# Creates a download button to download the graph
with open(image_name, "rb") as file:
    st.download_button(label="Download Graph", data=file, file_name=image_name)

# Allows the user to view the raw data for the night, defaults to collapsed
# as to not be annoying
with st.expander("View Raw Data"):
    st.subheader("Raw Data")
    combined_sensor = pandas.concat(
        [sensor[last0 + 20:], sensor2[0: Frequency2.index(0) - 50]],
        ignore_index=True,
        sort=False,
    )
    st.dataframe(data=combined_sensor)

# Creates a map of where the sensors are located, randomizing the location by
# + or - 0.001-9 degrees latitude and longitude ra stands for random, due to
# only being used with random, and oe stands for odd or even. Shortened for
# easier reading
ra = [0.001, 0.002, 0.003, 0.004, 0.005, 0.006, 0.007, 0.008, 0.009]
oe = [-1, 1]
st.header("Where do we have data from?")
# Each of these represent a sensor location
# (42.578 + r.choice(ra)*r.choice(oe), -88.565 + r.choice(ra)*r.choice(oe)),
locations = pandas.DataFrame(
    [
        (42.56, -88.566),  # S1
        (42.55, -88.525),  # S2
        (42.567, -88.543),  # S3
        (42.5535, -88.577),  # S4
        (42.5725, -88.5752),  # S5 X
        (42.5535, -88.573),  # S6
        (42.5743, -88.5732),  # S7 X
        (42.57, -88.542),  # S8
        (42.5731, -88.5753),  # S9 X
        (42.5736, -88.5749),  # S10 X
        (42.5728, -88.5734),  # S11 X
        (42.5734, -88.5739),
    ],  # S12 X
    columns=["lat", "lon"],
)
st.map(locations)

# Description text
st.caption(
    "All sensor locations are not precisely on their true location, and deviate by a noticable amount."
)
