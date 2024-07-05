import geopandas as gpd
import pandas as pd
import csv
from shapely.geometry import Point

def load_properties(properties_csv):
    return pd.read_csv(properties_csv, index_col='properties')

def shapefile_to_csv(input_shapefile, properties_csv, output_csv):
    # Read the shapefile
    gdf = gpd.read_file(input_shapefile)
    
    # Ensure the GeoDataFrame has a CRS
    if gdf.crs is None:
        raise ValueError("Input shapefile does not have a defined CRS")
    
    # Load properties
    properties_df = load_properties(properties_csv)
    
    # Open the output CSV file
    with open(output_csv, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        
        # Write the header
        csvwriter.writerow(['XCoordinate', 'YCoordinate', 'class', 'class_name'])
        
        # Iterate through each feature in the GeoDataFrame
        for idx, row in gdf.iterrows():
            # Get the geometry
            geom = row['geometry']
            
            # Check if the geometry is a Point
            if isinstance(geom, Point):
                x, y = geom.x, geom.y
            else:
                # If it's not a Point, use the centroid
                centroid = geom.centroid
                x, y = centroid.x, centroid.y
            
            # Get properties value
            properties_value = row.get('properties', '')
            
            # Look up class and class_name from properties_df
            if properties_value in properties_df.index:
                class_value = properties_df.loc[properties_value, 'class']
                class_name = properties_df.loc[properties_value, 'class_name']
            else:
                class_value = ''
                class_name = ''
            
            # Write the row to CSV
            csvwriter.writerow([x, y, class_value, class_name])
    
    print(f"Conversion complete. Output saved to {output_csv}")
    print(f"CRS of the input shapefile: {gdf.crs}")

# Usage example
input_shapefile = 'path/to/your/input.shp'
properties_csv = 'path/to/your/properties.csv'
output_csv = 'path/to/your/output.csv'
shapefile_to_csv(input_shapefile, properties_csv, output_csv)