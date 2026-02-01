import geopandas
import pandas as pd
from pathlib import Path
import pretty_errors

from hamburg_bike_lanes.ranking import rank_bikepath

not_actually_bike_infra = [
    "nan",
    "Fußgängerzone - zeitlich begrenzt",
    "Fußgängerzone (meist zeitlich begrenzt)",
    "Fußgängerüberweg/-furt (Schiebestrecke)",
    "Gehweg (Schiebestrecke)",
    "Gehweg (Fahrrad frei)",
    "Fußgängerzone - immer befahrbar",
    "Fußgängerzone - zeitlich begrenzt",
    "Gehweg (nur ZZ 1022-10)",
    "Fähre",
]

src_dir = Path(__file__).parent.parent
data_dir = src_dir.parent / "data"
input_geojson_dir = data_dir / "radverkehrsnetz_geoportal/may_2023/geojson/"

gdf = geopandas.GeoDataFrame()

input_gdfs = []

for file in [
    "sonstige.geojson",
    "radweg.geojson",
    "radfahrstreifen.geojson",
    "gruenflaechen.geojson",
    "fahrradstrasse.geojson",
]:
    input_gdfs.append(geopandas.read_file(input_geojson_dir / file))

gdf = pd.concat(input_gdfs, ignore_index=True)

gdf = gdf[~gdf["radweg_art"].isin(not_actually_bike_infra)]
gdf = gdf[gdf["radweg_art"].notnull()]
gdf["radweg_art_ranking"] = gdf.apply(lambda x: rank_bikepath(x), axis=1)

# gdf["lange_meter"] = round(gdf["laenge"])
# gdf = gdf.drop(columns=["laenge"])
# gdf["benutzungspflicht"] = gdf["benutzungspflicht"].apply(lambda x: "Nein" if str(x) == "nicht benutzungspflichtig" else x)
# gdf["radweg_in_mittellage"] = gdf["radweg_in_mittellage"].apply(lambda x: "Nein" if str(x) == "nan" else x)

gdf = gdf.set_crs("EPSG:25832", allow_override=True)

gdf.to_file(input_geojson_dir / "radinfrastruktur_mai2023_ohne_mischverkehr_gml_id.geojson", driver="GeoJSON")
