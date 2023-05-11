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

    # Pseudocode for next step
    # Get previous days date
    # Construct the file names needed for each chart
    # `[YYYY-MM-DD]_LENSSTSL0002.txt` and folder names `[MM]`
    # Make flag values to indicate if you need to build the chart
    # Verify that all files needed for a given chart exist and update flag
    # Build charts that can be built using google client

    make_lenss_plotter = True
    make_two_nights = True
    make_weekly_average = True

    if make_lenss_plotter:
        LENSSPlotter(
            "2022-10-11_LENSSTSL0008.txt",
            "2022-10-12_LENSSTSL0008.txt",
            42.57,
            -88.542,
            8,
        ).create_visual()

    if make_two_nights:
        TwoNights(
            "2022-09-19_LENSSTSL0008.txt",
            "2022-09-20_LENSSTSL0008.txt",
            "2022-12-26_LENSSTSL0008.txt",
            "2022-12-27_LENSSTSL0008.txt",
            42.57,
            -88.542,
            8,
        ).create_visual()

    if make_weekly_average:
        WeeklyAverage(
            "2022-8-23", "2023-1-23", 42.57, -88.542, 8
        ).create_visual()


if __name__ == "__main__":
    main()
