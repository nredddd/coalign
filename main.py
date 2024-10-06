import SimpleITK as sitk
import pygame
import numpy as np
import os
import glob
from collections import defaultdict
import random


def gettwofiles():
    # Specify the directory containing the images
    image_folder = 'val_dir'  # Change to your image directory
    img_dir = image_folder
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

    randrow = random.choice(filt)
    s2= random.sample(randrow[1],2)


    filename1, filename2 = os.path.join(img_dir,s2[0]),os.path.join(img_dir,s2[1])

    return filename1, filename2


# Function to convert SimpleITK image to Pygame surface
def sitk_to_pygame(img):
    img_array = sitk.GetArrayFromImage(img)
    img_array = np.clip(img_array, 0, 255).astype(np.uint8)  # Ensure the pixel values are in uint8
    img_array = np.stack([img_array] * 3, axis=-1)  # Convert grayscale to RGB by stacking
    img_array = np.transpose(img_array, (1, 0, 2))  # Transpose to (width, height, channels)
    img_surface = pygame.surfarray.make_surface(img_array)
    return img_surface

# Function to scale images while maintaining aspect ratio
def scale_image(surface, max_dimension):
    width, height = surface.get_size()
    if max(width, height) > max_dimension:
        scale_factor = max_dimension / max(width, height)
        new_size = (int(width * scale_factor), int(height * scale_factor))
        return pygame.transform.scale(surface, new_size)
    return surface


# Function to render text
def render_text(text, font_size, color):
    font = pygame.font.SysFont('Arial', font_size)
    return font.render(text, True, color)



# Event loop to keep the window open
running = True
while running:

    # Initialize Pygame
    pygame.init()
    screen_width = 768 #max(img2_aligned.GetWidth(),img2.GetWidth())
    screen_height = 768 #img1.GetHeight()
    screen = pygame.display.set_mode((screen_width * 2, screen_height))
    pygame.display.set_caption("Image Alignment")


    filename1, filename2 = gettwofiles()

    # Load images using SimpleITK
    img1 = sitk.ReadImage(filename1, sitk.sitkFloat32)
    img2 = sitk.ReadImage(filename2, sitk.sitkFloat32)

    # Preprocess images (optional)
    # For example, you could apply histogram equalization or smoothing here

    # Perform registration
    registration_method = sitk.ImageRegistrationMethod()
    registration_method.SetMetricAsMattesMutualInformation(numberOfHistogramBins=50)

    # Choose a more robust optimizer
    registration_method.SetOptimizerAsGradientDescent(learningRate=1.0, numberOfIterations=100)
    registration_method.SetOptimizerScalesFromPhysicalShift()  # This can help if images are at different scales

    # Multi-resolution strategy
    registration_method.SetShrinkFactorsPerLevel([4, 2, 1])  # Example levels
    registration_method.SetSmoothingSigmasPerLevel([2, 1, 0])  # Smoothing


    # Use affine transform for more flexibility
    initial_transform = sitk.Transform(2, sitk.sitkAffine)
    registration_method.SetInitialTransform(initial_transform)

    # Execute registration
    final_transform = registration_method.Execute(img1, img2)

    # Apply the final transform to the moving image (img2)
    img2_aligned = sitk.Resample(img2, img1, final_transform, sitk.sitkLinear, 0.0)



    # Convert images to Pygame surfaces
    img1_surface = sitk_to_pygame(img1)
    img2_surface = sitk_to_pygame(img2)
    img2_aligned_surface = sitk_to_pygame(img2_aligned)


    # Scale images to fit within the maximum dimension
    max_dimension = 768
    img1_surface = scale_image(img1_surface, max_dimension)
    img2_surface = scale_image(img2_surface, max_dimension)
    img2_aligned_surface = scale_image(img2_aligned_surface, max_dimension)

    # Set transparency for overlay
    transparency = 128  # Adjust transparency level
    img2_surface.set_alpha(transparency)  # Set alpha for aligned img2
    img2_aligned_surface.set_alpha(transparency)  # Set alpha for aligned img2

    # Render text labels
    label1 = render_text(filename1, 30, (255, 255, 255))  # White text
    label2 = render_text(filename2, 30, (255, 255, 255))  # White text
    label2_aligned = render_text("Aligned Image 2", 30, (255, 255, 255))  # White text


    running2 = True
    # Function to alternate display in Pygame
    while running2:
        # clock = pygame.time.Clock()
        screen.fill((0, 0, 0))  # Clear the screen
        
        # Left side: Display img1 and img2
        screen.blit(img1_surface, (0, 0))  # Display img1
        screen.blit(img2_surface, (0, 0))  # Overlay img2 on img1

        # Right side: Overlay img1 with aligned img2
        screen.blit(img1_surface, (max_dimension, 0))  # Display img1 on the right
        screen.blit(img2_aligned_surface, (max_dimension, 0))  # Overlay aligned img2

        # Draw labels
        screen.blit(label1, (10, 10))  # Draw label for img1
        screen.blit(label2, (10, 40))  # Draw label for img2

        pygame.display.flip()  # Update the display

        # Event loop to check for quitting
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    pygame.quit()
                    running = False  # Exit the function                
                if event.key == pygame.K_n:
                    filename1, filename2 = gettwofiles()
                    running2 = False

    pygame.quit()
