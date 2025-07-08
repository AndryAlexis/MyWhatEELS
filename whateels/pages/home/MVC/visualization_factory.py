"""
Factory for creating EELS visualizations based on dataset type.

This is a true Factory Pattern implementation that:
- Takes dataset type as input
- Returns different visualization objects based on type
- Hides the object creation logic from clients
"""

from .visualizations import SingleSpectrumVisualizer, SpectrumLineVisualizer, SpectrumImageVisualizer

class EELSVisualizationFactory:
    """Factory for creating appropriate EELS visualizations"""
    
    def __init__(self, model):
        self.model = model
        self.current_visualizer = None  # Store reference to current visualizer
        self._visualizers = {
            model.Constants.SINGLE_SPECTRUM: SingleSpectrumVisualizer,
            model.Constants.SPECTRUM_LINE: SpectrumLineVisualizer,
            model.Constants.SPECTRUM_IMAGE: SpectrumImageVisualizer
        }
    
    def create_visualization(self, dataset_type: str):
        """
        Create EELS visualization based on dataset type
        
        Args:
            dataset_type: Type of dataset (SSp, SLi, or SIm)
            
        Returns:
            Panel component with the appropriate visualization
        """
        try:
            visualizer_class = self._visualizers.get(dataset_type)
            if visualizer_class:
                self.current_visualizer = visualizer_class(self.model)
                return self.current_visualizer.create_layout()
            else:
                self.current_visualizer = None
                return self._create_error_placeholder(f"Unknown dataset type: {dataset_type}")
        except Exception as e:
            print(f"Error creating visualization: {e}")
            self.current_visualizer = None
            return self._create_error_placeholder(str(e))
    
    def _create_error_placeholder(self, error_msg: str):
        """Create error placeholder"""
        import panel as pn
        return pn.pane.HTML(
            f"""
            <div style='width:100%; height:100%; background-color:#ffe6e6; 
                        display:flex; align-items:center; justify-content:center;
                        border:2px solid #ff9999; border-radius:8px; min-height:400px;'>
                <div style='text-align:center; color:#cc0000;'>
                    <h3>Visualization Error</h3>
                    <p>{error_msg}</p>
                </div>
            </div>
            """,
            sizing_mode='stretch_both'
        )
