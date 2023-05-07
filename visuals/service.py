"""
This file serves as the central runner for data-visualizations for the
Spring '23 Metcalf Clinic LENSS project.
"""

from visuals.lenss_plotter import LENSSPlotter
from visuals.two_nights import TwoNights
from visuals.weekly_average import WeeklyAverage


def main():
    """
    This function serves as the main function that will render all the visuals.
    """
    print("Doing things.")


if __name__ == "__main__":
    LENSSPlotter(
        "2022-10-11_LENSSTSL0008.txt",
        "2022-10-12_LENSSTSL0008.txt",
        42.57,
        -88.542,
        8,
    ).create_visual()

    TwoNights(
        "2022-09-19_LENSSTSL0008.txt",
        "2022-09-20_LENSSTSL0008.txt",
        "2022-12-26_LENSSTSL0008.txt",
        "2022-12-27_LENSSTSL0008.txt",
        42.57,
        -88.542,
        8,
    ).create_visual()

    WeeklyAverage("2022-8-23", "2023-1-23", 42.57, -88.542, 8).create_visual()
