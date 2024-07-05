import cv2
import numpy as np
import json
import os
import geopandas as gpd
from shapely.geometry import Polygon
from rasterio.transform import from_bounds
from sklearn.cluster import KMeans
import argparse

def rgb_to_hex(r, g, b):
    return '#{:02x}{:02x}{:02x}'.format(r, g, b)

def get_dominant_color(img_section):
    colors = img_section.reshape(-1, 3)
    return np.mean(colors, axis=0).astype(int)

def image_to_geojson_grid(image_path, output_geojson_path, shapefile_path, grid_size=5, x_offset=0, y_offset=0, n_clusters=10):
    if not os.path.exists(image_path):
        print(f"Error: The file {image_path} does not exist.")
        return

    img = cv2.imread(image_path)
    
    if img is None:
        print(f"Error: Unable to read the image file {image_path}. Make sure it's a valid image file.")
        return

    height, width = img.shape[:2]
    
    # Read the shapefile
    gdf = gpd.read_file(shapefile_path)
    
    # Get the bounds of the shapefile
    minx, miny, maxx, maxy = gdf.total_bounds
    
    # Create a transform to convert from pixel coordinates to geographic coordinates
    transform = from_bounds(minx, miny, maxx, maxy, width, height)
    
    # Prepare color data for k-means
    color_data = []
    grid_cells = []
    
    # Create a buffer around the shapefile geometries
    buffered_geometry = gdf.geometry.buffer(grid_size * max(maxx - minx, maxy - miny) / max(width, height))
    
    for y in range(0, height, grid_size):
        for x in range(0, width, grid_size):
            img_section = img[y:y+grid_size, x:x+grid_size]
            dominant_color = get_dominant_color(img_section)
            
            # Convert pixel coordinates to geographic coordinates
            x1, y1 = transform * (x + x_offset, y + y_offset)
            x2, y2 = transform * (x + grid_size + x_offset, y + grid_size + y_offset)
            
            # Create a polygon from the grid cell
            poly = Polygon([(x1, y1), (x2, y1), (x2, y2), (x1, y2)])
            
            # Check if the polygon intersects with the buffered shapefile
            if buffered_geometry.intersects(poly).any():
                color_data.append(dominant_color)
                grid_cells.append((poly, dominant_color))

    # Perform k-means clustering
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    kmeans.fit(color_data)
    
    # Get cluster centers and convert to hex
    cluster_centers = kmeans.cluster_centers_.astype(int)
    cluster_hex_colors = [rgb_to_hex(*color) for color in cluster_centers]
    
    # Create GeoJSON features
    features = []
    for poly, color in grid_cells:
        cluster = kmeans.predict([color])[0]
        
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [list(poly.exterior.coords)]
            },
            "properties": {
                "color": cluster_hex_colors[cluster],
                "cluster": f"Cluster_{cluster}"
            }
        }
        features.append(feature)

    geojson = {
        "type": "FeatureCollection",
        "features": features
    }

    with open(output_geojson_path, 'w') as f:
        json.dump(geojson, f)

    print(f"GeoJSON file created: {output_geojson_path}")
    print(f"Number of grid cells included: {len(features)}")
    print(f"Number of clusters: {n_clusters}")
    print("Cluster colors:")
    for i, color in enumerate(cluster_hex_colors):
        print(f"  Cluster_{i}: {color}")

def main():
    parser = argparse.ArgumentParser(description="Convert an image to a color-clustered GeoJSON grid.")
    parser.add_argument("image_path", help="Path to the input image file")
    parser.add_argument("output_geojson_path", help="Path for the output GeoJSON file")
    parser.add_argument("shapefile_path", help="Path to the shapefile defining the area of interest")
    parser.add_argument("--grid_size", type=int, default=10, help="Size of the grid cells in pixels (default: 10)")
    parser.add_argument("--x_offset", type=int, default=0, help="X offset in pixels (default: 0)")
    parser.add_argument("--y_offset", type=int, default=0, help="Y offset in pixels (default: 0)")
    parser.add_argument("--n_clusters", type=int, default=10, help="Number of color clusters (default: 10)")

    args = parser.parse_args()

    image_to_geojson_grid(
        args.image_path,
        args.output_geojson_path,
        args.shapefile_path,
        args.grid_size,
        args.x_offset,
        args.y_offset,
        args.n_clusters
    )

if __name__ == "__main__":
    main()