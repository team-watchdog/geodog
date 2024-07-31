#!/usr/bin/env python3
"""
Blue-White Gradient Image Converter

This script converts an input image to a blue-white gradient using tiling for efficient
processing of large images. It also provides options for contrast adjustment and scaling.

Usage:
    python blueconverter.py [-h] [--tile-size TILE_SIZE] [--contrast CONTRAST] [--scale SCALE]
                            [input] [output]

Arguments:
    input           : Path to the input image file. If not provided, defaults to 'input.png'
                      in the current directory.
    output          : Path to the output image file. If not provided, defaults to 'output.png'
                      in the current directory.
    --tile-size     : Size of each tile (width and height) in pixels. Default is 1024.
    --contrast      : Contrast adjustment percentage. Default is 100 (no change).
    --scale         : Scaling percentage. Default is 100 (no change).
    -h, --help      : Show this help message and exit.

Requirements:
    - Python 3.x
    - NumPy
    - Pillow (PIL Fork)
    - tqdm


"""

import argparse
import os
from PIL import Image, ImageEnhance
import numpy as np
from tqdm import tqdm

Image.MAX_IMAGE_PIXELS = None  # Remove image size limit

def adjust_contrast(img, contrast_factor):
    enhancer = ImageEnhance.Contrast(img)
    return enhancer.enhance(contrast_factor)

def scale_image(img, scale_factor):
    new_size = (int(img.width * scale_factor), int(img.height * scale_factor))
    return img.resize(new_size, Image.LANCZOS)

def convert_tile_to_blue_white(tile):
    # Convert tile to numpy array
    tile_array = np.array(tile)
    
    # Calculate the luminance
    luminance = np.dot(tile_array[..., :3], [0.2989, 0.5870, 0.1140])
    
    # Normalize the luminance to 0-1 range
    luminance = luminance / 255.0
    
    # Create the blue channel (darkest blue is 0, 0, 50)
    blue_channel = np.interp(luminance, [0, 1], [50, 255]).astype(np.uint8)
    
    # Create the new tile array
    new_tile_array = np.zeros_like(tile_array)
    new_tile_array[..., 0] = np.interp(luminance, [0, 1], [0, 255]).astype(np.uint8)  # Red channel
    new_tile_array[..., 1] = np.interp(luminance, [0, 1], [0, 255]).astype(np.uint8)  # Green channel
    new_tile_array[..., 2] = blue_channel  # Blue channel
    
    # Create a new tile from the array
    return Image.fromarray(new_tile_array)

def convert_to_blue_white(input_path, output_path, tile_size=1024, contrast=100, scale=100):
    # Open the image
    with Image.open(input_path) as img:
        # Convert to RGB if it's not already
        img = img.convert('RGB')
        
        # Apply contrast adjustment
        contrast_factor = contrast / 100
        img = adjust_contrast(img, contrast_factor)
        
        # Apply scaling
        scale_factor = scale / 100
        img = scale_image(img, scale_factor)
        
        # Get image dimensions
        width, height = img.size
        
        # Create a new image for the output
        new_img = Image.new('RGB', (width, height))
        
        # Calculate total number of tiles
        total_tiles = ((width - 1) // tile_size + 1) * ((height - 1) // tile_size + 1)
        
        # Process the image in tiles with a progress bar
        with tqdm(total=total_tiles, desc="Converting image", unit="tile") as pbar:
            for y in range(0, height, tile_size):
                for x in range(0, width, tile_size):
                    # Define the tile boundaries
                    box = (x, y, min(x + tile_size, width), min(y + tile_size, height))
                    
                    # Extract the tile
                    tile = img.crop(box)
                    
                    # Process the tile
                    new_tile = convert_tile_to_blue_white(tile)
                    
                    # Place the processed tile back
                    new_img.paste(new_tile, box)
                    
                    # Update progress bar
                    pbar.update(1)
                    pbar.set_postfix({"Processed": f"{x+tile_size}x{y+tile_size}", "Remaining": f"{width-x-tile_size}x{height-y-tile_size}"})
        
        # Save the new image
        new_img.save(output_path)
        print(f"\nConverted image saved as {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Convert an image to blue-white gradient using tiling, with options for contrast and scaling.")
    parser.add_argument("input", nargs="?", default="input.png", help="Input image file (default: input.png in current directory)")
    parser.add_argument("output", nargs="?", default="output.png", help="Output image file (default: output.png in current directory)")
    parser.add_argument("--tile-size", type=int, default=1024, help="Tile size for processing (default: 1024)")
    parser.add_argument("--contrast", type=float, default=100, help="Contrast adjustment percentage (default: 100)")
    parser.add_argument("--scale", type=float, default=100, help="Scaling percentage (default: 100)")
    args = parser.parse_args()

    # Use absolute paths
    input_path = os.path.abspath(args.input)
    output_path = os.path.abspath(args.output)

    if not os.path.exists(input_path):
        print(f"Error: Input file '{input_path}' does not exist.")
        return

    try:
        convert_to_blue_white(input_path, output_path, args.tile_size, args.contrast, args.scale)
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()