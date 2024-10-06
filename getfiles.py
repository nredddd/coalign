import os
import glob
from collections import defaultdict
import random

# Specify the directory containing the images
image_folder = 'val_dir'  # Change to your image directory
image_files = glob.glob(os.path.join(image_folder, '*.png'))

# Initialize a defaultdict to hold lists of filenames grouped by the first number
grouped_files = defaultdict(list)

# Loop through each file and group them
for file_path in image_files:
    # Extract the filename and split by underscore
    filename = os.path.basename(file_path)  # e.g., '00003_001.png'
    first_number = filename.split('_')[0]  # Get the first number part
    
    # Append the filename to the list corresponding to the first number
    grouped_files[first_number].append(filename)

# Convert the defaultdict to a list of tuples
result = [(key, value) for key, value in grouped_files.items()]


filt = [row for row in result if len(row[1])>1]

for i in range(10):
    randrow = random.choice(filt)
    s2= random.sample(randrow[1],2)
    print(s2[0],s2[1])


