import subprocess
import sys, os

def package_pyqt5_app(script_name):
    try:
        # Command to package the PyQt5 app. Adjust the options as necessary.
        # For example, you might want to add '--windowed' if your app is GUI only.
        command = [
            'pyinstaller',
            '--onefile',  # Bundle the app into one file
            '--noconsole',  # Uncomment this line if you do not want a console window to appear on application launch
            script_name
        ]

        # Execute the command
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        print("PyQt5 app packaged successfully.")
    except subprocess.CalledProcessError as e:
        print("Error during packaging:", e)
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)

if __name__ == "__main__":
    # Replace 'your_script.py' with the name of your PyQt5 application script
    # Get the absolute path of the script file
    script_path = os.path.abspath(__file__)
    # Extract the directory path
    script_dir = os.path.dirname(script_path)
    # Change the current working directory to the script directory
    os.chdir(script_dir)
    package_pyqt5_app('CPTDataEditor.py')
