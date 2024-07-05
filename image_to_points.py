import cv2
import numpy as np
import csv
from collections import defaultdict
import os

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

def image_to_geo_csv_hex_filtered_with_id(image_path, output_csv_path, sample_rate=10, color_threshold=30):
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
    
    nw_lat, nw_lon = 9.83, 79.65
    se_lat, se_lon = 5.92, 81.88
    
    color_to_id = {}
    next_id = 1

    # First pass: identify unique colors
    for y in range(0, height, sample_rate):
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
        for y in range(0, height, sample_rate):
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

# Usage
image_path = 'sri_lanka_map.jpg'
output_csv_path = 'sri_lanka_land_use_geo_colors_hex_filtered_with_id.csv'
sample_rate = 10
color_threshold = 12  # Adjust this to control how similar colors need to be to be considered the same

image_to_geo_csv_hex_filtered_with_id(image_path, output_csv_path, sample_rate, color_threshold)