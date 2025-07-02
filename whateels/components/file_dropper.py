"""
File Dropper Component for EELS Data Upload

This module provides a Panel-based file upload component specifically designed
for DM3/DM4 EELS data files with validation and feedback.

Features:
- Drag-and-drop file upload interface
- File type validation (DM3/DM4 only)
- Visual feedback for upload status
- File content stored in memory for processing
"""

import panel as pn
import os

class FileDropper(pn.WidgetBox):
    """
    A specialized file upload component for EELS data files.
    
    This class extends Panel's WidgetBox to create a complete file upload
    interface with validation, feedback, and in-memory file handling.

    Attributes:
        valid_extensions (tuple): Allowed file extensions for upload
    """

    def __init__(
        self, 
        callback_function,
        valid_extensions: tuple = ('.dm3', '.dm4'),
        reject_message: str = "❌ Rejected:",
        success_message: str = "✅ Processed file:",
        feedback_message: str = "No file uploaded yet."
    ):
        """
        Initialize the FileDropper component.
        
        Creates the complete UI layout including title, file dropper widget,
        and feedback pane, then sets up event handlers for file uploads.
        
        Args:
            callback_function: Required callback function to call after successful upload.
                              Must accept (filename: str, file_content: bytes)
            valid_extensions: Tuple of allowed file extensions (e.g., ('.dm3', '.dm4'))
            reject_message: Message to display when rejecting invalid files
            success_message: Message to display on successful file upload
            feedback_message: Initial message to display before any upload
        """
        # Store configuration parameters
        # This allows easy customization of messages and valid extensions
        self.valid_extensions = valid_extensions
        self.reject_message = reject_message
        self.success_message = success_message
        self.feedback_message = feedback_message
        self.callback_function = callback_function

        # Create UI components in logical order
        self.upload_title = self._create_title()
        self.feedback_pane = self._create_feedback_pane()
        self.file_widget = self._create_file_widget()
        
        # Initialize parent WidgetBox with all components
        super().__init__(
            self.upload_title,
            self.file_widget,
            self.feedback_pane,
        )
        
        # Set up event handling after widget creation
        self._setup_event_handlers()
    
    def _create_title(self) -> pn.pane.HTML:
        """Create the title header for the upload box."""
        return pn.pane.HTML(
            "<h3 class='fdw-box-title'>Upload EELS data file</h3>"
        )
    
    def _create_feedback_pane(self) -> pn.pane.HTML:
        """Create the feedback message pane for status updates."""
        return pn.pane.HTML(
            f"<p class='feedback-message'>{self.feedback_message}</p>", 
            sizing_mode='stretch_width', 
            css_classes=['feedback-message']
        )
    
    def _create_file_widget(self) -> pn.widgets.FileDropper:
        """Create the main file dropper widget."""
        return pn.widgets.FileDropper(
            sizing_mode='stretch_width',
            multiple=False,  # Only allow single file uploads
        )
    
    def _setup_event_handlers(self):
        """Set up event handlers for file upload events."""
        def handle_file_upload(_):
            """
            Handle file upload events with validation and feedback.
            
            This nested function has access to the instance's widgets
            and handles the complete upload workflow.
            
            Args:
                _: Panel parameter change event (unused, but required by Panel)
            """
            
            self.clear_feedback()  # Clear previous feedback
            # Process each uploaded file (though we only allow single uploads)
            for filename, file_content in self.file_widget.value.items():
                if self._is_valid_file_extension(filename):
                    self._process_file_and_show_success(filename, file_content)
                    # Call the required callback function
                    self.callback_function(filename, file_content)
                else:
                    self._reject_file_and_show_error()
        
        # Connect the event handler to the file widget
        self.file_widget.param.watch(handle_file_upload, 'value')

    
    # === File Validation Methods ===
    
    def _is_valid_file_extension(self, filename: str) -> bool:
        """
        Validate file extension against allowed EELS data formats.
        
        Args:
            filename: Name of the file to validate
            
        Returns:
            bool: True if file has valid .dm3 or .dm4 extension, False otherwise
        """
        return filename.lower().endswith(self.valid_extensions)
    
    # === File Processing Methods ===
    
    def _process_file_and_show_success(self, filename: str, file_content: bytes):
        """
        Process uploaded file and display success feedback.
        
        This method handles the complete successful upload workflow:
        1. Store file content in memory for processing
        2. Update feedback pane with success message
        
        Note: The callback function is always called after successful processing
        
        Args:
            filename: Name of the file to process
            file_content: Binary content of the uploaded file
        """
        # Store file content and metadata for later processing
        self._last_uploaded_filename = filename
        self._last_uploaded_content = file_content
        
        # Update UI with success feedback
        success_message = (
            f"<p class='feedback-message success'>"
            f"{self.success_message}"
            f"</p>"
        )
        
        self.feedback_pane.object = success_message

    def _reject_file_and_show_error(self):
        """
        Handle rejection of invalid files and display error feedback.
        
        This method handles the error workflow when files don't meet requirements:
        1. Clear the file widget to remove invalid file
        2. Display error message to user
        """
        # Clear the file widget to remove the invalid file
        self.file_widget.value = {}
        self.file_widget.param.trigger('value')  # Force UI update
                
        # Update UI with error feedback
        error_message = (
            f"<p class='feedback-message error'>"
            f"{self.reject_message}"
            f"</p>"
        )
        self.feedback_pane.object = error_message
        
    # === Public Interface Methods ===
    
    def clear_feedback(self):
        """
        Clear the feedback message and reset to default state.
        
        Useful for programmatically resetting the component state
        or clearing previous upload status messages.
        """
        self.feedback_pane.object = f"<p class='feedback-message'>{self.feedback_message}</p>"
    
    def get_last_uploaded_file(self) -> tuple[str, bytes]:
        """
        Get the filename and content of the most recently uploaded file.
        
        Returns:
            tuple: (filename, file_content) of the last uploaded file, 
                   or ("", b"") if none
        """
        if hasattr(self, '_last_uploaded_filename') and hasattr(self, '_last_uploaded_content'):
            return self._last_uploaded_filename, self._last_uploaded_content
        return "", b""
    
    def get_file_content(self) -> bytes:
        """
        Get the content of the most recently uploaded file.
        
        Returns:
            bytes: Content of the last uploaded file, or empty bytes if none
        """
        if hasattr(self, '_last_uploaded_content'):
            return self._last_uploaded_content
        return b""
    
    def get_filename(self) -> str:
        """
        Get the filename of the most recently uploaded file.
        
        Returns:
            str: Filename of the last uploaded file, or empty string if none
        """
        if hasattr(self, '_last_uploaded_filename'):
            return self._last_uploaded_filename
        return ""