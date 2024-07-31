#!/usr/bin/env python3
"""
Image Color Analyzer

This script analyzes an input image and identifies its dominant colors.
It uses K-means clustering to determine the most prominent colors and
provides their values in RGB, HEX, and HSV formats.

Usage:
    python colorchecker.py [-h] -i INPUT_IMAGE [-o OUTPUT_FILE] [-n NUM_COLORS]

Arguments:
    -i, --input     : Path to the input image file.
    -o, --output    : Path to the output text file. If not provided, results will be 
                      printed to the console.
    -n, --num-colors: Number of dominant colors to identify. Default is 5.
    -h, --help      : Show this help message and exit.

Requirements:
    - Python 3.x
    - OpenCV (cv2)
    - NumPy
    - scikit-learn
    - tqdm
"""

import cv2
import numpy as np
from sklearn.cluster import KMeans
import argparse
import os
from tqdm import tqdm

def rgb_to_hex(rgb):
    return '#{:02x}{:02x}{:02x}'.format(rgb[0], rgb[1], rgb[2])

def analyze_image_colors(image_path, num_colors=5):
    # Read the image
    image = cv2.imread(image_path)
    
    if image is None:
        raise ValueError(f"Unable to read image at {image_path}")
    
    # Convert to RGB (OpenCV uses BGR by default)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # Reshape the image to be a list of pixels
    pixels = image.reshape(-1, 3)
    
    # Perform K-means clustering
    print("Performing K-means clustering...")
    kmeans = KMeans(n_clusters=num_colors, n_init=10)
    kmeans.fit(pixels)
    
    # Get the colors
    colors = kmeans.cluster_centers_
    
    # Convert to integer RGB values
    colors = colors.round().astype(int)
    
    return colors

def main():
    parser = argparse.ArgumentParser(description="Analyze dominant colors in an image.")
    parser.add_argument("-i", "--input", required=True, help="Path to the input image file")
    parser.add_argument("-o", "--output", help="Path to the output text file (optional)")
    parser.add_argument("-n", "--num-colors", type=int, default=5, help="Number of dominant colors to identify (default: 5)")
    args = parser.parse_args()

    try:
        # Analyze the image
        print(f"Analyzing image: {args.input}")
        colors = analyze_image_colors(args.input, args.num_colors)

        # Prepare the results
        results = [f"Dominant colors in {args.input}:", "Color | Hex Code | RGB Values | HSV Values", "-" * 50]
        
        for i, color in enumerate(colors, 1):
            rgb = tuple(color)
            hex_code = rgb_to_hex(rgb)
            
            # Convert RGB to HSV
            hsv = cv2.cvtColor(np.uint8([[color]]), cv2.COLOR_RGB2HSV)[0][0]
            
            results.extend([
                f"Color {i}:",
                f"  Hex: {hex_code}",
                f"  RGB: {rgb}",
                f"  HSV: {tuple(hsv)}",
                ""
            ])

        # Output the results
        if args.output:
            with open(args.output, 'w') as f:
                f.write('\n'.join(results))
            print(f"Results saved to {args.output}")
        else:
            print('\n'.join(results))

    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()