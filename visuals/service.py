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
    # `[YYYY-MM-DD]_LENSSTSL0002.txt`
    # Make flag values to indicate if you need to build the chart
    # Verify that all files needed for a given chart exist and update flag
    # Build charts that can be built using google client

    # TODO: Sync with Google Docs
    # TODO: Go through Google Docs directory and pull the appropriate files
    # TODO: Alena and Abraham, make note of teh files needed and coordinate with
    # TODO: Fatimah on which files you'll be using for these visuals. You should
    # TODO: be using the cleaned night files and not the raw data files.

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


def google_client():
    return {}


def verify_file(folder: str, file_name: str):
    return True


def get_file(folder:str, file_name:str):
    return True

if __name__ == "__main__":
    main()
