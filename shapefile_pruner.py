import geopandas as gpd
import argparse
from collections import Counter
import os
import sys
import numpy as np

def calculate_stats(counts):
    if not counts:
        return 0, 0, 0, 0  # Return zeros if the list is empty
    return (
        np.mean(counts),
        np.median(counts),
        min(counts),
        max(counts)
    )

def prune_shapefile(input_file, output_file, feature_field, threshold_value):
    try:
        # Read the input shapefile
        gdf = gpd.read_file(input_file)
    except FileNotFoundError:
        print(f"Error: The input file '{input_file}' was not found.")
        sys.exit(1)
    except PermissionError:
        print(f"Error: Permission denied when trying to read '{input_file}'.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: An unexpected error occurred while reading the input file: {str(e)}")
        sys.exit(1)

    # Check if the feature field exists in the shapefile
    if feature_field not in gdf.columns:
        print(f"Error: The specified feature field '{feature_field}' does not exist in the shapefile.")
        print(f"Available fields are: {', '.join(gdf.columns)}")
        sys.exit(1)

    # Count the occurrences of each unique feature
    feature_counts = Counter(gdf[feature_field])

    # Calculate stats for original data
    original_counts = list(feature_counts.values())
    original_avg, original_median, original_min, original_max = calculate_stats(original_counts)

    # Identify features to keep (those with count >= threshold_value)
    features_to_keep = {feature for feature, count in feature_counts.items() if count >= threshold_value}

    # Filter the GeoDataFrame based on the features to keep
    pruned_gdf = gdf[gdf[feature_field].isin(features_to_keep)]

    # Calculate stats for pruned data
    pruned_counts = [count for feature, count in feature_counts.items() if feature in features_to_keep]
    pruned_avg, pruned_median, pruned_min, pruned_max = calculate_stats(pruned_counts)

    # Check if any features remain after pruning
    if len(pruned_gdf) == 0:
        print("Warning: All features have been pruned. The output shapefile will be empty.")

    try:
        # Save the pruned GeoDataFrame to a new shapefile
        pruned_gdf.to_file(output_file)
    except PermissionError:
        print(f"Error: Permission denied when trying to write to '{output_file}'.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: An unexpected error occurred while writing the output file: {str(e)}")
        sys.exit(1)

    print(f"Pruned shapefile saved to {output_file}")
    print(f"Original feature count: {len(gdf)}")
    print(f"Pruned feature count: {len(pruned_gdf)}")
    print(f"Number of unique features in original: {len(feature_counts)}")
    print(f"Number of unique features in pruned: {len(features_to_keep)}")
    print("\nStatistics for feature counts:")
    print(f"Original - Avg: {original_avg:.2f}, Median: {original_median:.2f}, Min: {original_min}, Max: {original_max}")
    print(f"Pruned - Avg: {pruned_avg:.2f}, Median: {pruned_median:.2f}, Min: {pruned_min}, Max: {pruned_max}")

if __name__ == "__main__":
    try:
        # Set the working directory to the script's location
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
    except Exception as e:
        print(f"Error: Unable to set working directory: {str(e)}")
        sys.exit(1)

    parser = argparse.ArgumentParser(description="Prune shapefile features based on unique feature count.")
    parser.add_argument("input_file", help="Name of the input shapefile in the current directory")
    parser.add_argument("output_file", help="Name for the pruned shapefile (will be saved in the current directory)")
    parser.add_argument("feature_field", help="Name of the field containing features to count")
    parser.add_argument("threshold_value", type=int, help="Minimum count to keep features")

    args = parser.parse_args()

    # Print current working directory for user reference
    print(f"Working directory: {os.getcwd()}")

    prune_shapefile(args.input_file, args.output_file, args.feature_field, args.threshold_value)
