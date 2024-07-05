import geopandas as gpd
import argparse
from collections import Counter
import os

def prune_shapefile(input_file, output_file, feature_field, threshold_value):
    # Read the input shapefile
    gdf = gpd.read_file(input_file)

    # Count the occurrences of each unique feature
    feature_counts = Counter(gdf[feature_field])

    # Identify features to keep (those with count >= threshold_value)
    features_to_keep = {feature for feature, count in feature_counts.items() if count >= threshold_value}

    # Filter the GeoDataFrame based on the features to keep
    pruned_gdf = gdf[gdf[feature_field].isin(features_to_keep)]

    # Save the pruned GeoDataFrame to a new shapefile
    pruned_gdf.to_file(output_file)

    print(f"Pruned shapefile saved to {output_file}")
    print(f"Original feature count: {len(gdf)}")
    print(f"Pruned feature count: {len(pruned_gdf)}")
    print(f"Number of unique features in original: {len(feature_counts)}")
    print(f"Number of unique features in pruned: {len(features_to_keep)}")

if __name__ == "__main__":
    # Set the working directory to the script's location
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    parser = argparse.ArgumentParser(description="Prune shapefile features based on unique feature count.")
    parser.add_argument("input_file", help="Name of the input shapefile in the current directory")
    parser.add_argument("output_file", help="Name for the pruned shapefile (will be saved in the current directory)")
    parser.add_argument("feature_field", help="Name of the field containing features to count")
    parser.add_argument("threshold_value", type=int, help="Minimum count to keep features")

    args = parser.parse_args()

    # Print current working directory for user reference
    print(f"Working directory: {os.getcwd()}")

    prune_shapefile(args.input_file, args.output_file, args.feature_field, args.threshold_value)