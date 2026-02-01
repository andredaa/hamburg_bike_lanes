import geopandas
import fiona
import pandas

fp = "mai_2023.gml"
gml_layers = []


for layer in fiona.listlayers(fp):
    print(layer)
    gdf = geopandas.read_file(fp, driver="GML", layer=layer)
    gml_layers.append(gdf)


all_layers_gdf = pandas.concat(gml_layers)

print(list(all_layers_gdf.columns))

cols_to_keep = [
    "gml_id",
    "radweg_art",
    "fuehrungsart",
    "benutzungspflicht",
    "radweg_in_mittellage",
    "oberflaeche",
    "breite",
    "radrouten",
    "zweirichtung",
    "geometry"
]

cols_to_del = list(set(all_layers_gdf.columns) - set(cols_to_keep))

all_layers_gdf = all_layers_gdf.drop(columns=cols_to_del)

all_layers_gdf = all_layers_gdf.set_crs("EPSG:25832", allow_override=True)
all_layers_gdf = all_layers_gdf.to_crs("EPSG:4326")

all_layers_gdf.to_file("radinfrastruktur_mai2023.geojson")