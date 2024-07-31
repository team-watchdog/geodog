#!/usr/bin/env python3
"""
Image to Geo-Points Converter with Adjustable Bounding Box

This script converts an input image to a CSV file containing geo-referenced points.
Each point represents a pixel in the image, with its color and assigned color ID.
The geographic bounding box can be adjusted via command-line arguments.

Usage:
    python image_to_points.py [-h] -i INPUT_IMAGE [-s SAMPLE_RATE] [-c COLOR_THRESHOLD]
                              [-o OUTPUT] [--nw-lat NW_LAT] [--nw-lon NW_LON]
                              [--se-lat SE_LAT] [--se-lon SE_LON]

Arguments:
    -i, --input            : Path to the input image file.
    -s, --sample-rate      : Sample rate for pixel processing. Default is 10 (process every 10th pixel).
    -c, --color-threshold  : Threshold for color similarity. Default is 12.
    -o, --output           : Path to the output CSV file. If not provided, it will be derived from the input filename.
    --nw-lat               : Northwest corner latitude. Default is 9.83 (Sri Lanka).
    --nw-lon               : Northwest corner longitude. Default is 79.65 (Sri Lanka).
    --se-lat               : Southeast corner latitude. Default is 5.92 (Sri Lanka).
    --se-lon               : Southeast corner longitude. Default is 81.88 (Sri Lanka).
    -h, --help             : Show this help message and exit.

Requirements:
    - Python 3.x
    - OpenCV (cv2)
    - NumPy
    - tqdm

Note:
    The default geographic bounding box is set for Sri Lanka. Adjust these values
    using the command-line arguments if processing a different area.
"""

import cv2
import numpy as np
import csv
from collections import defaultdict
import os
import argparse
from tqdm import tqdm

def pixel_to_geo(x, y, width, height, nw_lat, nw_lon, se_lat, se_lon):
    lon = nw_lon + (se_lon - nw_lon) * (x / width)
    lat = nw_lat - (nw_lat - se_lat) * (y / height)
    return lat, lon

def rgb_to_hex(r, g, b):
    return '#{:02x}{:02x}{:02x}'.format(r, g, b)

def is_color_valid(r, g, b):
    return (r, g, b) != (255, 255, 255)

def color_distance(color1, color2):
    return sum((a - b) ** 2 for a, b in zip(color1, color2)) ** 0.5

def find_closest_color(color, color_list, threshold):
    for existing_color, _ in color_list:
        if color_distance(color, existing_color) < threshold:
            return existing_color
    return None

def image_to_geo_csv_hex_filtered_with_id(image_path, output_csv_path, sample_rate=10, color_threshold=30, 
                                          nw_lat=9.83, nw_lon=79.65, se_lat=5.92, se_lon=81.88):
    # Check if the file exists
    if not os.path.exists(image_path):
        print(f"Error: The file {image_path} does not exist.")
        return

    # Read the image
    img = cv2.imread(image_path)
    
    # Check if the image was read successfully
    if img is None:
        print(f"Error: Unable to read the image file {image_path}. Make sure it's a valid image file.")
        return

    height, width = img.shape[:2]
    
    color_to_id = {}
    next_id = 1

    # First pass: identify unique colors
    print("Identifying unique colors...")
    for y in tqdm(range(0, height, sample_rate), desc="Processing rows", unit="row"):
        for x in range(0, width, sample_rate):
            b, g, r = img[y, x]
            if is_color_valid(r, g, b):
                color = (r, g, b)
                closest_color = find_closest_color(color, color_to_id.items(), color_threshold)
                if closest_color is None:
                    color_to_id[color] = next_id
                    next_id += 1

    # Open CSV file for writing
    with open(output_csv_path, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['latitude', 'longitude', 'color', 'color_id'])
        
        # Second pass: write data to CSV
        print("Writing data to CSV...")
        for y in tqdm(range(0, height, sample_rate), desc="Processing rows", unit="row"):
            for x in range(0, width, sample_rate):
                b, g, r = img[y, x]
                if is_color_valid(r, g, b):
                    lat, lon = pixel_to_geo(x, y, width, height, nw_lat, nw_lon, se_lat, se_lon)
                    color = (r, g, b)
                    closest_color = find_closest_color(color, color_to_id.items(), color_threshold)
                    if closest_color is None:
                        closest_color = color
                    hex_color = rgb_to_hex(*closest_color)
                    color_id = color_to_id[closest_color]
                    csvwriter.writerow([lat, lon, hex_color, color_id])

    print(f"CSV file created: {output_csv_path}")
    print(f"Number of unique colors: {len(color_to_id)}")

def main():
    parser = argparse.ArgumentParser(description="Convert an image to geo-referenced points in a CSV file.")
    parser.add_argument("-i", "--input", required=True, help="Path to the input image file")
    parser.add_argument("-s", "--sample-rate", type=int, default=10, help="Sample rate for pixel processing (default: 10)")
    parser.add_argument("-c", "--color-threshold", type=int, default=12, help="Threshold for color similarity (default: 12)")
    parser.add_argument("-o", "--output", help="Path to the output CSV file (default: derived from input filename)")
    parser.add_argument("--nw-lat", type=float, default=9.83, help="Northwest corner latitude (default: 9.83)")
    parser.add_argument("--nw-lon", type=float, default=79.65, help="Northwest corner longitude (default: 79.65)")
    parser.add_argument("--se-lat", type=float, default=5.92, help="Southeast corner latitude (default: 5.92)")
    parser.add_argument("--se-lon", type=float, default=81.88, help="Southeast corner longitude (default: 81.88)")
    args = parser.parse_args()

    # Derive output filename if not provided
    if args.output is None:
        base_name = os.path.splitext(os.path.basename(args.input))[0]
        args.output = f"{base_name}_geo_colors_hex_filtered_with_id.csv"

    image_to_geo_csv_hex_filtered_with_id(args.input, args.output, args.sample_rate, args.color_threshold,
                                          args.nw_lat, args.nw_lon, args.se_lat, args.se_lon)

if __name__ == "__main__":
    main()