#!/usr/bin/env python3
"""
Color Remapper

This script remaps the colors in an input image to a set of visually distinct colors
using K-means clustering. It reduces the number of unique colors in the image to
a maximum of 20, making the image more visually striking and easier to distinguish
different areas.

Usage:
    python color_remapper.py [-h] -i INPUT_IMAGE [-o OUTPUT_IMAGE] [-n NUM_COLORS]

Arguments:
    -i, --input     : Path to the input image file.
    -o, --output    : Path to the output image file. If not provided, it will be
                      derived from the input filename with '_remapped' appended.
    -n, --num-colors: Maximum number of colors to use in the remapped image. 
                      Default is 20.
    -h, --help      : Show this help message and exit.

Requirements:
    - Python 3.x
    - NumPy
    - Pillow (PIL Fork)
    - scikit-learn
    - tqdm
"""

import argparse
import os
import numpy as np
from PIL import Image
from sklearn.cluster import KMeans
from tqdm import tqdm

def count_unique_colors(img_array):
    pixels = img_array.reshape(-1, 3)
    unique_colors = np.unique(pixels, axis=0)
    return len(unique_colors)

def generate_distinct_colors(n):
    hues = np.linspace(0, 1, n, endpoint=False)
    hsv_colors = np.column_stack((hues, np.ones(n), np.ones(n)))
    rgb_colors = np.array([np.array(Image.new("HSV", (1, 1), tuple(map(lambda x: int(x * 255), hsv))).convert("RGB").getpixel((0, 0))) for hsv in hsv_colors])
    return rgb_colors

def remap_colors(image_path, max_colors=20):
    # Open the image
    img = Image.open(image_path)
    
    # Convert to RGB if it's not already
    img = img.convert('RGB')
    
    # Convert image to numpy array
    img_array = np.array(img)
    
    # Count unique colors
    unique_color_count = count_unique_colors(img_array)
    
    # Determine the number of clusters
    n_colors = min(unique_color_count, max_colors)
    
    # Reshape the array to 2D for KMeans
    pixels = img_array.reshape(-1, 3)
    
    print("Performing K-means clustering...")
    # Perform K-means clustering
    kmeans = KMeans(n_clusters=n_colors, random_state=42, n_init=10)
    labels = kmeans.fit_predict(pixels)
    
    # Get the colors
    colors = kmeans.cluster_centers_.astype(int)
    
    # Create a visually distinct color palette
    distinct_colors = generate_distinct_colors(n_colors)
    
    # Create a mapping from cluster labels to distinct colors
    color_map = {i: tuple(color) for i, color in enumerate(distinct_colors)}
    
    print("Remapping colors...")
    # Apply the color mapping to the image
    remapped_pixels = np.array([color_map[label] for label in tqdm(labels, desc="Remapping pixels", unit="pixel")])
    
    # Reshape back to original image shape
    remapped_img_array = remapped_pixels.reshape(img_array.shape)
    
    # Convert back to PIL Image
    remapped_img = Image.fromarray(remapped_img_array.astype('uint8'), 'RGB')
    
    return remapped_img

def main():
    parser = argparse.ArgumentParser(description="Remap colors in an image to a set of visually distinct colors.")
    parser.add_argument("-i", "--input", required=True, help="Path to the input image file")
    parser.add_argument("-o", "--output", help="Path to the output image file (default: derived from input filename)")
    parser.add_argument("-n", "--num-colors", type=int, default=20, help="Maximum number of colors to use (default: 20)")
    args = parser.parse_args()

    # Derive output filename if not provided
    if args.output is None:
        base_name = os.path.splitext(os.path.basename(args.input))[0]
        args.output = f"{base_name}_remapped.jpg"

    try:
        print(f"Processing image: {args.input}")
        remapped_image = remap_colors(args.input, args.num_colors)
        remapped_image.save(args.output)
        print(f"Remapped image saved as: {args.output}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()