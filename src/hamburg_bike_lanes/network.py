import geopandas as gpd
from shapely.geometry import LineString, MultiLineString
from shapely import Geometry
from shapely.ops import linemerge
from typing import List

from hamburg_bike_lanes.helpers import simplify_multilinestring

class BikeLaneNetwork:
    def __init__(
        self,
        file_path:str,
        index_col:str="gml_id",
        projection:str = "EPSG:25832",
        file_engine="pyogrio"  # use "fiona" for geojsons/gpkg containing dicts (nested dicts in particular) as values
    ):
        self.gdf = gpd.read_file(file_path, engine=file_engine)

        self.gdf = self.gdf.set_crs(projection)
        self.gdf = self.gdf.set_index(index_col)

        # set spatial index
        self.spatial_index = self.gdf.sindex

    def join_lines_by_idx(self, indexes: List[int]) -> LineString | MultiLineString:
        """
        merges an array of lines into 1 continuous line if possible.
        otherwise returns MultiLineString with continuous sub linestrings.
        """
        subset = self.gdf.loc[indexes].copy()

        # often times we have multiline strings where they are not needed, 
        # these sometimes are not merged right due to coordinate precision errors
        subset["geometry"] = subset.geometry.apply(simplify_multilinestring)

        # return single continuous linestring if possible, else multilinestring
        return linemerge(subset["geometry"].to_list())
    
    def find_intersecting_rows(self, target_geom: Geometry, ignore_idx=None) -> gpd.GeoDataFrame:
        # Use spatial index to find potential intersections first
        possible_matches_index = list(self.spatial_index.intersection(target_geom.buffer(1).bounds))
        possible_matches = self.gdf.iloc[possible_matches_index]

        if not len(possible_matches):
            return gpd.GeoDataFrame()
        
        if ignore_idx:
            possible_matches = possible_matches[possible_matches.index != ignore_idx]
            if not len(possible_matches):
                return gpd.GeoDataFrame()
        
        # Then perform exact intersection test on the smaller subset
        return possible_matches[possible_matches.geometry.intersects(target_geom.buffer(0.1))].copy()
