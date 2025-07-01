"""
File Dropper Component for EELS Data Upload

This module provides a Panel-based file upload component specifically designed
for DM3/DM4 EELS data files with validation and feedback.
"""

import os
import panel as pn

pn.extension()


def file_dropper():
    """
    Create a file dropper component for uploading DM3/DM4 EELS data files.
    
    Returns
    -------
    tuple
        A tuple containing (container_widget, feedback_pane) for the file dropper interface
    """
    # Create title for the upload box
    upload_title = pn.pane.HTML(
        "<h3 class='fdw-box-title'>Upload an image</h3>"
    )

    # Create feedback message pane (initialized first to avoid reference errors)
    feedback_message_pane = pn.pane.HTML(
        "<p class='feedback-message'>No file uploaded yet.</p>", 
        sizing_mode='stretch_width', 
        css_classes=['feedback-message']
    )

    # Create the file dropper widget
    file_dropper_widget = pn.widgets.FileDropper(
        sizing_mode='stretch_width',  # Stretch to available width
        multiple=False,  # Allow only single file upload
    )

    # Container to hold all components
    upload_container = pn.WidgetBox(
        upload_title, 
        file_dropper_widget, 
        feedback_message_pane,
    )

    def handle_file_upload(event):
        """
        Handle file upload events with validation and feedback.
        
        Args:
            event: Panel parameter change event containing file data
        """
        # Ensure uploads directory exists
        _ensure_uploads_directory()
        
        # Process each uploaded file
        for filename, file_content in file_dropper_widget.value.items():
            if _is_valid_file_extension(filename):
                _save_file_and_show_success(filename, file_content, feedback_message_pane)
            else:
                _reject_file_and_show_error(filename, file_dropper_widget, feedback_message_pane)

    def _ensure_uploads_directory():
        """Ensure the uploads directory exists."""
        uploads_directory = "uploads"
        os.makedirs(uploads_directory, exist_ok=True)

    def _is_valid_file_extension(filename: str) -> bool:
        """
        Check if the file has a valid DM3 or DM4 extension.
        
        Args:
            filename: Name of the file to validate
            
        Returns:
            bool: True if file extension is valid, False otherwise
        """
        return filename.lower().endswith(('.dm3', '.dm4'))

    def _reject_file_and_show_error(filename: str, file_dropper_widget, feedback_pane):
        """
        Handle rejection of invalid files.
        
        Args:
            filename: Name of the rejected file
            file_dropper_widget: Widget to reset
            feedback_pane: Pane to update with error message
        """
        # Reset the FileDropper widget
        file_dropper_widget.value = {}
        file_dropper_widget.param.trigger('value')  # Force UI update
        
        # Show error feedback
        current_path = os.path.join(os.getcwd(), filename)
        print(f"Rejected file: {current_path} (not .dm3 or .dm4)")
        
        error_message = (
            f"<p class='feedback-message error'>"
            f"❌ Rejected file: {filename} (not .dm3 or .dm4)"
            f"</p>"
        )
        feedback_pane.object = error_message

    def _save_file_and_show_success(filename: str, file_content: bytes, feedback_pane):
        """
        Save uploaded file and show success feedback.
        
        Args:
            filename: Name of the file to save
            file_content: Binary content of the file
            feedback_pane: Pane to update with success message
        """
        # Save file to uploads directory
        uploads_directory = "uploads"
        file_path = os.path.join(uploads_directory, filename)
        
        with open(file_path, "wb") as file_handle:
            file_handle.write(file_content)
        
        # Show success feedback
        file_size = len(file_content) if file_content else 0
        print(f"File uploaded successfully: {filename}, Size: {file_size} bytes")
        
        success_message = (
            f"<p class='feedback-message success'>"
            f"✅ Uploaded file: {filename} ({file_size} bytes)"
            f"</p>"
        )
        feedback_pane.object = success_message

    # Watch for file upload events
    file_dropper_widget.param.watch(handle_file_upload, 'value')
    
    return upload_container