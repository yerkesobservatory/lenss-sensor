# Define and abstract visualization class that loads data, parses it correctly,
# and renders the HTML from it.
# All methods should be @abstractmethods with docstrings underneath them that
# tell you what the function should accomplish.
# Look here for an example: https://github.com/chanteriam/reproductive-rights-data-project/blob/main/reproductive_rights_data_project/visualization/abstract_visualization.py

from abc import ABC, abstractmethod

class Visualization(ABC):
    """
    This abstract class is the one that all visualizations will be built on.
    """

    @abstractmethod
    def _import_files(self):
        """
        This method pulls the relevant sensor data file for the given night 
        and the following morning from Google Drive. 
        """
        pass

    @abstractmethod
    def _parse_data(self):
        """
        This method cleans the data files and organizes it 
        with the relevant column names as a dataframe.
        """
        pass

    @abstractmethod
    def _construct_data(self):
        """
        This method constructs all the information needed for the
        class to render the visualization.
        """
        pass

    @abstractmethod
    def _call_apis(self):
        """
        This method pulls the relevant weather and moon phase data for each night 
        from external APIs. 
        """
        pass

    @abstractmethod
    def create_visual(self):
        """
        This method takes the data from the _construct_data function and returns
        a visual object as an HTML file. 
        """
        pass

