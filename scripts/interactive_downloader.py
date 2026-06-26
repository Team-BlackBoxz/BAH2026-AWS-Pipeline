import ipywidgets as widgets
from IPython.display import display
import subprocess

print("🌍 Landsat 9 AWS Downloader (Interactive)")

# 1. Create the interactive input boxes
path_input = widgets.Text(value='137', description='WRS Path:')
row_input = widgets.Text(value='042', description='WRS Row:')
start_date = widgets.Text(value='2023-01-01', description='Start Date:')
end_date = widgets.Text(value='2023-12-31', description='End Date:')
button = widgets.Button(description="🚀 Start Download", button_style='success')
output = widgets.Output()

# Show the boxes on the screen
display(path_input, row_input, start_date, end_date, button, output)

# 2. What happens when you click the button
def on_button_clicked(b):
    with output:
        output.clear_output()
        print("Starting download... This might take a few minutes for 1GB of data!")
        
        # Construct the fake product ID so the python script can extract the Path/Row from it
        product_id = f"LC09_L2SP_{path_input.value}{row_input.value}_00000000_00000000_02_T1"
        
        # Build the command
        command = [
            "python", "scripts/download_aws.py", 
            product_id, "SR_B2,SR_B3,SR_B4,ST_B10", 
            start_date.value, end_date.value, 
            f"./input/{product_id}"
        ]
        
        # Run the script and print the logs live
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in process.stdout:
            print(line.strip())
        print("✅ Download Complete! You can now run driver.py")

button.on_click(on_button_clicked)
