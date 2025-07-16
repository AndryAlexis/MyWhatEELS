"""
Factory for creating EELS plots based on dataset type.

Implements the Factory Pattern to:
- Create appropriate visualizers based on dataset type
- Centralize object creation logic
- Provide a consistent interface for visualization components
- Handle errors in a single location
"""

from .eels_plots import DM4Plots, DM3Plots

class EELSPlotFactory:
    """Factory for creating appropriate EELS plots and visualizations
    
    I'm using the Factory Pattern because it decouples visualization creation
    from the View and makes adding new visualizer types easier.
    """
    
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.current_plot_renderer = None  # Store reference to active plotter
        self._all_plots = {
            model.constants.SPECTRUM_LINE: DM4Plots,
            model.constants.SPECTRUM_IMAGE: DM3Plots
        }
    
    def create_plots(self, dataset_type: str):
        """Create EELS plots based on dataset type
        
        Args:
            dataset_type: Type of dataset (SSp, SLi, or SIm)
            
        Returns:
            Panel component with the appropriate plot visualization, or None if there was an error
            (in which case the View will have been updated to show an error display)
        """
        try:
            visualizer_class = self._all_plots.get(dataset_type)
            if visualizer_class:
                self.current_plot_renderer = visualizer_class(self.model)
                return self.current_plot_renderer.create_layout()
            else:
                self.current_plot_renderer = None
                # Just log the error, View will handle showing it
                print(f"Unknown dataset type: {dataset_type}")
                # We don't return anything as the View will update itself
                self.view.show_error()
                return None
        except Exception as e:
            print(f"Error creating plot: {e}")
            self.current_plot_renderer = None
            # Just log the error, View will handle showing it
            self.view.show_error()
            return None