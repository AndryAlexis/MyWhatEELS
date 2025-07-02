"""
Example usage of the improved FileDropper class (in-memory version)

This demonstrates the clean, readable interface of the refactored component
that stores files in memory rather than saving them to disk.
"""

from whateels.components import FileDropper


def create_file_upload_demo():
    """Example of using the FileDropper class."""
    
    # Create the file dropper - simple and clean
    file_dropper = FileDropper()
    
    # Access public methods for integration
    filename, content = file_dropper.get_last_uploaded_file()
    print(f"Last uploaded file: {filename} ({len(content)} bytes)")
    
    # Get individual components
    print(f"Filename: {file_dropper.get_filename()}")
    print(f"Content size: {len(file_dropper.get_file_content())} bytes")
    
    # Reset state if needed
    file_dropper.clear_feedback()
    
    return file_dropper


def process_uploaded_file(file_dropper: FileDropper):
    """Example of how to process the uploaded file content."""
    filename, content = file_dropper.get_last_uploaded_file()
    
    if filename and content:
        print(f"Processing {filename}...")
        # Here you would process the file content directly from memory
        # For example: parse DM3/DM4 data, extract metadata, etc.
        return True
    else:
        print("No file uploaded yet")
        return False


if __name__ == "__main__":
    # Demo usage
    dropper = create_file_upload_demo()
    print("FileDropper created successfully!")
    print(f"Valid extensions: {dropper.VALID_EXTENSIONS}")
    print("Files are now stored in memory, not saved to disk")
