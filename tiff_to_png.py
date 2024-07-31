#!/usr/bin/env python3
"""
TIFF to PNG Converter

This script converts large TIFF images to PNG format. It processes the image
in tiles to manage memory usage efficiently, making it suitable for very
large images. The script maintains the original image dimensions and uses
a progress bar to show conversion status.

Usage:
    python tiff_to_png.py [-h] [-i INPUT_FILE] [-o OUTPUT_FOLDER] [-s SIZE]

Arguments:
    -h, --help      : Show this help message and exit
    -i, --image     : Path to the input image file. If not provided, the script will
                      will look for it in the current working directory.
    -o, --output    : Path to the output folder where tiles will be saved. If not
                      provided, a 'tiles' folder will be created in the current directory.
    -s, --size      : Size of each tile (width and height) in pixels. Default is 256.

Requirements:
    - Python 3.x
    - Pillow (PIL Fork)
    - tqdm

"""

import os
import argparse
from PIL import Image
from tqdm import tqdm

Image.MAX_IMAGE_PIXELS = None  # Remove image size limit

def find_first_image():
    for file in os.listdir():
        if file.lower().endswith(('.tiff', '.tif', '.png', '.jpg', '.jpeg')):
            return file
    raise FileNotFoundError("No image file found in the current directory.")

def convert_image_to_tiles(input_path, output_folder, tile_size):
    try:
        with Image.open(input_path) as img:
            # Get the original width and height
            width, height = img.size
            
            # Calculate total number of tiles
            total_tiles = ((width + tile_size - 1) // tile_size) * ((height + tile_size - 1) // tile_size)
            
            # Create progress bar
            with tqdm(total=total_tiles, desc="Converting", unit="tile") as pbar:
                # Process the image in tiles
                for y in range(0, height, tile_size):
                    for x in range(0, width, tile_size):
                        # Define the box
                        box = (x, y, min(x + tile_size, width), min(y + tile_size, height))
                        
                        # Get the tile
                        tile = img.crop(box)
                        
                        # Save the tile
                        tile_filename = f"tile_{x}_{y}.png"
                        tile_path = os.path.join(output_folder, tile_filename)
                        tile.save(tile_path, "PNG")
                        
                        # Update progress bar
                        pbar.update(1)
        
        print(f"Successfully converted {input_path} to tiles in {output_folder}")
        print(f"Original image dimensions: {width}x{height}")
        print(f"Tile size: {tile_size}x{tile_size}")
        print(f"Total tiles created: {total_tiles}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description='Convert images to PNG tiles.')
    parser.add_argument('-i', '--image', help='Path to the input image file')
    parser.add_argument('-o', '--output', help='Path to the output folder for tiles')
    parser.add_argument('-s', '--size', type=int, default=256, help='Size of each tile (width and height) in pixels')
    args = parser.parse_args()

    # Get the current working directory
    cwd = os.getcwd()
    
    # If input_file is not provided, find the first image in the current directory
    if not args.image:
        input_file = find_first_image()
        print(f"Using {input_file} as input")
    else:
        input_file = args.image

    # If input_file doesn't have a directory, assume it's in the current working directory
    if not os.path.dirname(input_file):
        input_path = os.path.join(cwd, input_file)
    else:
        input_path = input_file
    
    # If output_folder is not provided, create a 'tiles' folder in the current directory
    if not args.output:
        output_folder = os.path.join(cwd, 'tiles')
        print(f"Saving tiles to {output_folder}")
    else:
        output_folder = args.output
    
    # Ensure the output directory exists
    os.makedirs(output_folder, exist_ok=True)
    
    convert_image_to_tiles(input_path, output_folder, args.size)

if __name__ == "__main__":
    main()