import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import graphviz
import os
import argparse  # Import the argparse module

class DotFileHandler(FileSystemEventHandler):
    """Handles file system events, specifically for the dot file."""

    def __init__(self, dot_file_path, output_png_path):
        self.dot_file_path = dot_file_path
        self.output_png_path = output_png_path
        self.last_rendered_content = None  # Track last rendered content

    def on_modified(self, event):
        if event.is_directory:
            return None

        if event.event_type == 'modified':
            if event.src_path.lower() == self.dot_file_path.lower():  # Case-insensitive comparison
                print(f"Dot file '{self.dot_file_path}' modified. Rendering PNG...")
                self.render_dot_to_png()

    def render_dot_to_png(self):
        try:
            with open(self.dot_file_path, 'r') as f:
                dot_content = f.read()

            if dot_content == self.last_rendered_content:
                print("Dot file content is the same as last render, skipping PNG generation.")
                return # Skip rendering if content is the same

            dot = graphviz.Source(dot_content)
            dot.render(self.output_png_path, format='png', engine='dot') # Or 'neato', 'fdp', 'sfdp', 'circo'
            print(f"PNG rendered to '{self.output_png_path}.png'")
            self.last_rendered_content = dot_content # Update last rendered content

        except Exception as e:
            print(f"Error rendering PNG: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Watch a dot file for changes and render a PNG.")
    parser.add_argument("dot_file", help="Path to the dot file to watch.")
    parser.add_argument("-o", "--output", help="Optional output filename for the PNG (without extension). "
                        "Defaults to the dot filename without extension.", required=False)

    args = parser.parse_args()

    dot_file = args.dot_file
    output_file_base = args.output

    if not output_file_base:
        # Default output filename is the dot file name without extension
        output_file_base = os.path.splitext(os.path.basename(dot_file))[0]

    watch_path = os.path.dirname(os.path.abspath(dot_file)) or '.' # Watch the directory of the dot file or current dir if dot_file is just a name
    output_file = output_file_base # No need to change this now

    event_handler = DotFileHandler(os.path.abspath(dot_file), output_file)
    observer = Observer()
    observer.schedule(event_handler, watch_path, recursive=False)
    observer.start()

    print(f"Watching for changes in '{dot_file}'. Output PNG will be '{output_file}.png' (in the same directory). Press Ctrl+C to stop.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()