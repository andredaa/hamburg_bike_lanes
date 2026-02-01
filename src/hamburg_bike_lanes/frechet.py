import geopandas as gpd
import numpy as np
from pathlib import Path

from hamburg_bike_lanes.helpers import calculate_bearing, simplify_multilinestring, split_by_distance


this_dir = Path(__file__).parent
data_dir = this_dir.parent.parent / "data"
bike_paths_dir = data_dir / "radverkehrsnetz_geoportal/may_2023/geojson"
accidents_data_dir = data_dir / "unfaelle"


def load_mixed_traffic_bike_paths():
    gdf = gpd.read_file(bike_paths_dir / "mischverkehr.geojson", engine="pyogrio")
    gdf = gdf.set_crs("EPSG:25832", allow_override=True)
    
    # Filter out invalid geometries
    gdf = gdf[gdf.geometry.is_valid].copy()
    
    gdf["fid"] = range(len(gdf))

    gdf = explode_gdf_to_segments(gdf)

    return gdf

def load_bike_paths():
    gdf = gpd.read_file(bike_paths_dir / "radinfrastruktur_mai2023_ohne_mischverkehr.geojson", engine="pyogrio")
    gdf = gdf.set_crs("EPSG:4326")
    gdf = gdf.to_crs("EPSG:25832")

    gdf = gdf[gdf.geometry.is_valid].copy()

    gdf["fid"] = range(len(gdf))

    gdf = explode_gdf_to_segments(gdf)

    return gdf


def explode_gdf_to_segments(gdf, max_segment_length=5):
    """
    Explode a GeoDataFrame of LineStrings into segments of maximum length.
    
    Parameters:
    -----------
    gdf : geopandas.GeoDataFrame
        GeoDataFrame containing LineString geometries
    max_segment_length : float
        Maximum length of each segment in the same units as the geometry
    
    Returns:
    --------
    geopandas.GeoDataFrame
        New GeoDataFrame with segmented geometries
    """
    
    rows = []
    
    for row in gdf.itertuples(index=False):
        segments = split_by_distance(row.geometry, max_segment_length)
        
        for i, segment in enumerate(segments):
            new_row = row._asdict()
            new_row['geometry'] = segment
            new_row["segment_id"] = i
            rows.append(new_row)        
    
    result_gdf = gpd.GeoDataFrame(rows, crs=gdf.crs)
    return result_gdf




def find_min_frechet_dist_for_most_similar_bike_path(mixed_traffic_line_geom):
    # Check if input geometry is valid
    if not mixed_traffic_line_geom.is_valid or mixed_traffic_line_geom.is_empty:
        return None
    
    mixed_traffic_line_bearing = calculate_bearing(mixed_traffic_line_geom)
    
    try:
        global bike_paths_gdf
        global bike_paths_gdf_sindex

        nearby_bike_infra_indexes = list(bike_paths_gdf_sindex.intersection(mixed_traffic_line_geom.buffer(20).bounds))
        nearby_bike_infra = bike_paths_gdf.iloc[nearby_bike_infra_indexes].copy()
        
        # Filter out any invalid geometries from nearby paths
        nearby_bike_infra = nearby_bike_infra[nearby_bike_infra.geometry.is_valid]
        nearby_bike_infra  = nearby_bike_infra[nearby_bike_infra.distance(mixed_traffic_line_geom) <= 25]
        
        if len(nearby_bike_infra) == 0:
            return None
        

        # only bike paths that go roughly into the same direction
        nearby_bike_infra["bearing"] = nearby_bike_infra.geometry.apply(lambda geom: calculate_bearing(geom))
        nearby_bike_infra = nearby_bike_infra[abs(
            nearby_bike_infra["bearing"]
            - mixed_traffic_line_bearing
        ) <= 90]

        if len(nearby_bike_infra) == 0:
            return None
        
        distances = nearby_bike_infra.geometry.frechet_distance(mixed_traffic_line_geom, densify=0.5)
        # Filter out any NaN values that might have occurred
        valid_distances = distances[~np.isnan(distances)]
        
        if len(valid_distances) == 0:
            return None
            
        return round(valid_distances.min(), 2)
    
    except Exception as e:
        print(f"Error calculating Fréchet distance: {e}")
        return None





def export_mixed_traffic_bike_paths_with_frechet_distance_to_dedicated_bike_infra():
    """
    iterates over all on mixed traffic biking paths (streets with no dedicated bike infra)
    The geoportal adds mixed traffic bike path on almost all streets, even if a dedicated bike path exits on that street.
    This function segments all  mixed traffic linestrings 
    for each segment: finds the dedicated bike path with the minimum frechet distance (most parallel, most close)
    Then exports the original mixed traffic line strings with a new property: the mean() minimum frechet distance of all its segments
    This property allows quiet reliably to determine, wether a parallel dedicated bike path exists next to this mixed traffic linestring
    """

    
    mixed_traffic_biking_gdf = load_mixed_traffic_bike_paths()
    print("loaded on street")

    global bike_paths_gdf
    bike_paths_gdf = load_bike_paths()
    print("loaded bike paths")

    global bike_paths_gdf_sindex
    bike_paths_gdf_sindex = bike_paths_gdf.sindex

    print("calculating frechet distances")

    mixed_traffic_biking_gdf["min_frechet_distance"] = mixed_traffic_biking_gdf["geometry"].apply(
        lambda geom: find_min_frechet_dist_for_most_similar_bike_path(geom)
    )

    # Create aggregation dictionary for all columns
    agg_dict = {}
    # Use 'first' for all other columns except for min_frechet_distance and geometry
    for col in mixed_traffic_biking_gdf.columns:
        if col not in ['geometry', 'min_frechet_distance', 'fid', 'segment_id']:
            agg_dict[col] = 'first'

    # Add mean aggregation for min_frechet_distance
    agg_dict['min_frechet_distance'] = 'mean'

    # Dissolve with the aggregation dictionary
    mixed_traffic_biking_gdf = mixed_traffic_biking_gdf.dissolve(by="fid", aggfunc=agg_dict)

    # Apply simplification to convert MultiLineStrings to LineStrings when possible
    mixed_traffic_biking_gdf.geometry = mixed_traffic_biking_gdf.geometry.apply(simplify_multilinestring)

    print(mixed_traffic_biking_gdf["min_frechet_distance"].head())

    

    # Export to both GeoJSON and GeoPackage formats
    output_base = bike_paths_dir / "mischverkehr_frechet_new"
    # Export to GeoJSON
    mixed_traffic_biking_gdf.to_file(f"{output_base}.geojson", driver="GeoJSON")
    # Export to GeoPackage with keep_geom_type to avoid MultiLineStrings
    mixed_traffic_biking_gdf.to_file(f"{output_base}.gpkg", driver="GPKG", keep_geom_type=True)





if __name__ == "__main__":

    export_mixed_traffic_bike_paths_with_frechet_distance_to_dedicated_bike_infra()