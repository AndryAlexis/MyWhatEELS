from abc import ABC, abstractmethod

class AbstractEELSVisualizer(ABC):
    """
    Abstract base class for EELS visualizers.
    This class defines the interface for EELS visualizers,
    including methods for creating plots and handling dataset information.
    """
    
    @abstractmethod
    def create_plots(self):
        """
        Create the main layout for the EELS visualizer.
        
        This method should be implemented by subclasses to define how the plots
        and other UI components are arranged.
        """
        pass

    @abstractmethod
    def create_dataset_info(self):
        """
        Create dataset information pane for the sidebar.
        
        This method should be implemented by subclasses to provide details about
        the dataset being visualized.
        """
        pass