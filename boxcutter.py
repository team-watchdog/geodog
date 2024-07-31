#!/usr/bin/env python3
"""
boxcutter.py - A tool to split large images into smaller tiles

Usage:
    python boxcutter.py [-i INPUT_IMAGE] [-o OUTPUT_FOLDER] [-s TILE_SIZE]

Arguments:
    -h, --help      : Show this help message and exit
    -i, --image     : Path to the input image file. If not provided, the script will
                      use the first image file found in the current directory.
    -o, --output    : Path to the output folder where tiles will be saved. If not
                      provided, a 'tiles' folder will be created in the current directory.
    -s, --size      : Size of each tile (width and height) in pixels. Default is 256.

Examples:
    python boxcutter.py -i large_image.jpg -o output_tiles -s 512
    python boxcutter.py --image map.png --output map_tiles --size 1024
    python boxcutter.py  # Uses default values

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

def tile_image(image_path=None, output_folder=None, tile_size=256):
    # If image_path is not provided, look for the first image in the current directory
    if image_path is None:
        for file in os.listdir():
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                image_path = file
                break
        if image_path is None:
            raise ValueError("No image file found in the current directory")
    
    # If output_folder is not provided, create a 'tiles' folder in the current directory
    if output_folder is None:
        output_folder = os.path.join(os.getcwd(), 'tiles')
    
    # Open the image
    with Image.open(image_path) as img:
        # Get the image dimensions
        width, height = img.size
        
        # Create the output folder if it doesn't exist
        os.makedirs(output_folder, exist_ok=True)
        
        # Calculate total number of tiles
        total_tiles = ((height - 1) // tile_size + 1) * ((width - 1) // tile_size + 1)
        
        # Create a tqdm progress bar
        with tqdm(total=total_tiles, unit='tile') as pbar:
            # Counter for naming tiles
            tile_count = 0
            
            # Iterate over the image in tile_size x tile_size pixel blocks
            for i in range(0, height, tile_size):
                for j in range(0, width, tile_size):
                    # Define the box for cropping
                    box = (j, i, j + tile_size, i + tile_size)
                    
                    # Crop the image
                    tile = img.crop(box)
                    
                    # If the tile is smaller than tile_size x tile_size, create a new tile_size x tile_size image
                    if tile.size != (tile_size, tile_size):
                        new_tile = Image.new('RGB', (tile_size, tile_size))
                        new_tile.paste(tile, (0, 0))
                        tile = new_tile
                    
                    # Save the tile
                    tile_count += 1
                    tile_name = f"tile_{tile_count:04d}.png"
                    tile_path = os.path.join(output_folder, tile_name)
                    tile.save(tile_path, "PNG")
                    
                    # Update the progress bar
                    pbar.update(1)
        
        print(f"Tiling complete. {tile_count} tiles created in {output_folder}")

def main():
    parser = argparse.ArgumentParser(description="Split an image into tiles.")
    parser.add_argument("-i", "--image", help="Path to the input image file")
    parser.add_argument("-o", "--output", help="Path to the output folder")
    parser.add_argument("-s", "--size", type=int, default=256, help="Tile size (default: 256)")
    
    args = parser.parse_args()
    
    tile_image(args.image, args.output, args.size)

if __name__ == "__main__":
    main()