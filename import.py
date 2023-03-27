import os
import shutil

main_folder = 'gh'

# Loop through each subfolder in the main folder
for subfolder in os.listdir(main_folder):
    # Construct the full path of the subfolder
    subfolder_path = os.path.join(main_folder, subfolder)
    
    # Check if the subfolder is a directory
    if os.path.isdir(subfolder_path):
        # Loop through each file in the subfolder
        for file in os.listdir(subfolder_path):
            # Construct the full path of the file
            file_path = os.path.join(subfolder_path, file)
            
            # Move the file to the main folder
            shutil.move(file_path, main_folder)
"""


#main_folder = 'data-bull/lindsey-vonn/transcripts'
text_files = [f for f in os.listdir(main_folder) if f.endswith('.txt')]

for file_name in text_files:
    # Construct the full path of the file
    file_path = os.path.join(main_folder, file_name)
    
    # Open the file in read mode and read the contents
    with open(file_path, 'r') as f:
        contents = f.read()
    
    # Add the desired string to the beginning of the contents
    new_contents = 'From a video featuring Max Verstappen:\n' + contents
    
    # Open the file in write mode and write the new contents
    with open(file_path, 'w') as f:
        f.write(new_contents)
"""