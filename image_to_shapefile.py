import cv2
import numpy as np
import geopandas as gpd
from shapely.geometry import Polygon, MultiPolygon
import matplotlib.colors as mcolors

def image_to_shapefile(image_path, output_shapefile):
    # Read the image
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Failed to read image at {image_path}")
    
    # Convert to RGB (OpenCV uses BGR by default)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # Get image dimensions
    height, width = img_rgb.shape[:2]
    
    # Get unique colors
    unique_colors = np.unique(img_rgb.reshape(-1, img_rgb.shape[-1]), axis=0)
    
    features = []
    
    for color in unique_colors:
        # Create a mask for the current color
        mask = cv2.inRange(img_rgb, color, color)
        
        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            # Ensure contour has at least 3 points
            if len(contour) < 3:
                continue
            
            # Reshape contour to remove single-dimensional entries
            contour = contour.reshape(-1, 2)
            
            # Flip the y-coordinates
            contour[:, 1] = height - contour[:, 1]
            
            try:
                # Convert contour to polygon
                polygon = Polygon(contour)
                
                # Ensure the polygon is valid
                if not polygon.is_valid:
                    polygon = polygon.buffer(0)
                
                # Get color hex code
                hex_color = mcolors.rgb2hex(color / 255.0)
                
                # Add feature
                features.append({
                    'geometry': polygon,
                    'properties': {'color': hex_color}
                })
            except ValueError as e:
                print(f"Skipping invalid contour: {e}")
    
    if not features:
        raise ValueError("No valid features found in the image")
    
    # Create GeoDataFrame
    gdf = gpd.GeoDataFrame(features, crs="EPSG:3857")  # Web Mercator projection
    
    # Save to shapefile
    gdf.to_file(output_shapefile)

# Usage
image_path = 'sri_lanka_map.jpg'
output_shapefile = 'shapefile2.shp'

try:
    image_to_shapefile(image_path, output_shapefile)
    print(f"Shapefile successfully created at {output_shapefile}")
except Exception as e:
    print(f"An error occurred: {e}")