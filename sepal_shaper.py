import geopandas as gpd
import pandas as pd
import csv
from shapely.geometry import Point
import os
import argparse

def load_properties(properties_csv):
    return pd.read_csv(properties_csv, index_col='properties')

def shapefile_to_csv(input_shapefile, properties_csv, output_csv):
    try:
        # Read the shapefile
        gdf = gpd.read_file(input_shapefile)
        
        # Ensure the GeoDataFrame has a CRS
        if gdf.crs is None:
            raise ValueError("Input shapefile does not have a defined CRS")
        
        # Load properties
        properties_df = load_properties(properties_csv)
        
        # Get all column names from properties_df
        property_columns = properties_df.columns.tolist()
        
        # Open the output CSV file
        with open(output_csv, 'w', newline='') as csvfile:
            csvwriter = csv.writer(csvfile)
            
            # Write the header
            header = ['XCoordinate', 'YCoordinate'] + property_columns
            csvwriter.writerow(header)
            
            # Counters for statistics
            total_count = 0
            kept_count = 0
            error_count = 0
            no_match_count = 0
            
            # Iterate through each feature in the GeoDataFrame
            for idx, row in gdf.iterrows():
                total_count += 1
                
                # Get properties value
                properties_value = row.get('properties', '')
                
                # Check if the properties value exists in the properties DataFrame
                if properties_value in properties_df.index:
                    try:
                        # Get all property values
                        property_values = properties_df.loc[properties_value].values.tolist()
                        
                        # Get the geometry
                        geom = row['geometry']
                        
                        # Check if the geometry is valid and not None
                        if geom is not None and geom.is_valid:
                            # Check if the geometry is a Point
                            if isinstance(geom, Point):
                                x, y = geom.x, geom.y
                            else:
                                # If it's not a Point, use the centroid
                                centroid = geom.centroid
                                x, y = centroid.x, centroid.y
                            
                            # Write the row to CSV
                            csvwriter.writerow([x, y] + property_values)
                            kept_count += 1
                        else:
                            print(f"Warning: Invalid or None geometry found for index {idx}. Skipping this entry.")
                            error_count += 1
                    except Exception as e:
                        print(f"Error processing entry at index {idx}: {str(e)}")
                        error_count += 1
                else:
                    no_match_count += 1
        
        print(f"Conversion complete. Output saved to {output_csv}")
        print(f"CRS of the input shapefile: {gdf.crs}")
        print(f"Total entries processed: {total_count}")
        print(f"Entries kept: {kept_count}")
        print(f"Entries dropped due to no property match: {no_match_count}")
        print(f"Entries skipped due to errors: {error_count}")
    
    except Exception as e:
        print(f"An error occurred during processing: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description="Convert shapefile to CSV with all property fields.")
    parser.add_argument("input_shapefile", help="Path to the input shapefile")
    parser.add_argument("properties_csv", help="Path to the properties CSV file")
    parser.add_argument("output_csv", help="Path for the output CSV file")
    args = parser.parse_args()

    # Convert relative paths to absolute paths based on the current working directory
    cwd = os.getcwd()
    input_shapefile = os.path.join(cwd, args.input_shapefile)
    properties_csv = os.path.join(cwd, args.properties_csv)
    output_csv = os.path.join(cwd, args.output_csv)

    shapefile_to_csv(input_shapefile, properties_csv, output_csv)

if __name__ == "__main__":
    main()
