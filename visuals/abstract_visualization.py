from abc import ABC, abstractmethod


class Visualization(ABC):
    """
    This abstract class is the one that all visualizations will be built on.
    """

    @abstractmethod
    def _import_files(self):
        """
        This method pulls the relevant sensor data file(s) for the given night
        and the following morning from Google Drive.
        """
        pass

    @abstractmethod
    def _parse_data(self, df):
        """
        This method cleans the data files and organizes it with the relevant
        column names as a dataframe.
        """
        pass

    @abstractmethod
    def create_visual(self):
        """
        This method takes the data from the _construct_data function and returns
        a visual object as an HTML file.
        """
        pass
