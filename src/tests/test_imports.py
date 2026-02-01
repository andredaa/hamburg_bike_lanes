import pytest
from pathlib import Path

from src.hamburg_bike_lanes.helpers import calculate_bearing
from src.hamburg_bike_lanes.network import BikeLaneNetwork
from src.hamburg_bike_lanes.ranking import rank_bikepath

@pytest.fixture
def network():
    root_dir = Path(__file__).parent.parent.parent
    data_dir = root_dir / "data"
    
    input_geojson_dir = data_dir / "radverkehrsnetz_geoportal/may_2023/geojson/"
    geojson_filename = "radinfrastruktur_mai2023_ohne_mischverkehr_gml_id.geojson"
    test_network = BikeLaneNetwork(file_path= input_geojson_dir / geojson_filename)

    return test_network

def test_network(network):
    network.gdf = network.gdf.reset_index()
    test_intersects = network.find_intersecting_rows(target_geom=network.gdf.iloc[0].geometry)
    test_joined_lines = network.join_lines_by_idx([0,1,2,3])


def test_rank_bikepath(network):
    network.gdf["rank"] = network.gdf.apply(lambda x: rank_bikepath(x), axis=1)


def test_helpers(network):
    test_bearing = calculate_bearing(network.gdf.iloc[0].geometry)

