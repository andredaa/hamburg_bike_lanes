# Hamburg Geoportal Bike Data Analysis

This project analyzes bicycle infrastructure data from Hamburg's Geoportal and Transparenzportal. It provides tools to process, analyze, and compare bike network data across different time periods, calculate geometric differences using Fréchet distance, and identify new bike infrastructure.

## Overview

The project focuses on analyzing Hamburg's cycling infrastructure network ("Radverkehrsnetz") using geospatial data. It includes functionality for:

- Processing and cleaning GeoJSON data from different time periods
- Analyzing bike lane network topology and connectivity
- Comparing infrastructure changes between July 2022 and May 2023
- Calculating Fréchet distance between bike path geometries
- Ranking bike infrastructure by quality and type
- Identifying new dedicated bike infrastructure

## Data Sources

### Downloading Data

Download the relevant bicycle infrastructure layers from one of these official sources:

1. **Hamburg Geoportal** (https://geoportal-hamburg.de/)
   - Search for "Radverkehrsnetz" (cycling network)
   - Download layers in GeoJSON or GML format

2. **Hamburg Transparenzportal** (https://transparenz.hamburg.de/)
   - Search for "Radverkehrsnetz Hamburg"
   - Look for datasets containing bicycle infrastructure information
   - Download available formats (GeoJSON, GML, GPKG)

### Required Layers

The following bike infrastructure types should be downloaded:

- **Radweg** - Dedicated bike paths
- **Radfahrstreifen** - Bike lanes (painted lanes on roads)
- **Fahrradstraße** - Bicycle streets
- **Mischverkehr** - Mixed traffic
- **Schutzstreifen** - Advisory bike lanes
- **Grünflächen** - Paths through green spaces
- **Schiebestrecke** - Walking sections
- **Sonstige** - Other types

### Data Organization

Place downloaded data in the following directory structure:

```
radverkehrsnetz_geoportal/
├── july_2022/
│   └── geojson/
│       ├── fahrradstrasse.geojson
│       ├── radweg.geojson
│       ├── radfahrstreifen.geojson
│       ├── mischverkehr.geojson
│       ├── gruenflaechen.geojson
│       ├── schiebestrecke.geojson
│       └── sonstige.geojson
├── may_2023/
│   ├── geojson/
│   │   ├── fahrradstrasse.geojson
│   │   ├── radweg.geojson
│   │   ├── radfahrstreifen.geojson
│   │   ├── mischverkehr.geojson
│   │   ├── gruenflaechen.geojson
│   │   ├── schiebestrecke.geojson
│   │   └── sonstige.geojson
│   └── gml/
│       └── gml_to_geojson.py
└── new_bike_infra_2022_to_2023/
    └── new_bike_infra_2022_to_2023_radfahrstreifen.geojson
```

## Project Structure

### Main Scripts

- **`bike_lane_network.py`** - Core class for analyzing bike lane network topology, finding intersections, and joining connected line segments
- **`create_geojson_all_dedicated_bike_infra.py`** - Combines multiple bike infrastructure types into a single dataset, filters out non-infrastructure elements, and ranks infrastructure quality
- **`frechet_distance.py`** - Calculates Fréchet distance between bike path geometries to identify similar or changed infrastructure
- **`helpers.py`** - Utility functions for geometry processing, bearing calculations, and coordinate transformations

### Key Classes and Functions

#### BikeLaneNetwork
Main class for working with bike infrastructure networks:
- Loads and indexes bike path geodata
- Finds intersecting bike paths
- Joins connected line segments
- Manages spatial indexing for efficient queries

#### Infrastructure Ranking
The project includes a ranking system for bike infrastructure quality (0-3):
- **3**: Protected bike lanes, Copenhagen-style paths, wide paths (≥4m)
- **2**: Bike streets (Fahrradstraße), bike lanes (Radfahrstreifen), paths through green spaces
- **1**: Advisory lanes (Schutzstreifen), bus lanes with bikes, separated paths
- **0**: Mixed paths, paths in median strips, narrow infrastructure

## Installation

### Using uv (Recommended)

This project uses [uv](https://github.com/astral-sh/uv) for fast and reliable dependency management.

1. **Install uv** (if not already installed):
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. **Clone the repository and install dependencies**:
```bash
cd hamburg_geoportal_bike_data
uv sync
```

This will create a virtual environment and install all dependencies specified in `pyproject.toml`.

3. **Activate the virtual environment**:
```bash
source .venv/bin/activate
```

Alternatively, you can run scripts directly with `uv`:
```bash
uv run python create_geojson_all_dedicated_bike_infra.py
```

### Using pip (Alternative)

If you prefer using pip:

```bash
pip install -e .
```

## Requirements

### Python Dependencies

The project requires Python ≥3.10 and the following packages:

- `geopandas>=0.14.0` - Geospatial data manipulation
- `pandas>=2.0.0` - Data processing
- `numpy>=1.24.0` - Numerical operations
- `shapely>=2.0.0` - Geometric operations
- `pyogrio>=0.7.0` - Fast geospatial file I/O (preferred)
- `fiona>=1.9.0` - Alternative geospatial file I/O
- `pretty-errors>=1.2.0` - Enhanced error messages

All dependencies are automatically installed when using `uv sync` or `pip install -e .`

### Coordinate Reference Systems

The project uses the following CRS:
- **EPSG:25832** - ETRS89 / UTM zone 32N (primary working CRS for Hamburg)
- **EPSG:4326** - WGS84 (for data exchange)

## Usage

### 1. Create Combined Bike Infrastructure Dataset

```python
python create_geojson_all_dedicated_bike_infra.py
```

This script:
- Reads individual layer files
- Filters out non-bike-infrastructure elements (pedestrian zones, ferry routes, etc.)
- Ranks infrastructure by quality
- Outputs a combined GeoJSON file

### 2. Analyze Network Topology

```python
from hamburg_bike_lanes.bike_lane_network import BikeLaneNetwork
import geopandas as gpd

# Load bike network
gdf = gpd.read_file("path/to/your/bike_infrastructure.geojson")
network = BikeLaneNetwork(gdf, "path/to/your/bike_infrastructure.geojson")

# Find intersecting segments
target_geom = gdf.iloc[0].geometry
intersecting = network.find_intersecting_rows(target_geom)
```

### 3. Calculate Fréchet Distance

Use `frechet_distance.py` to compare bike path geometries between different time periods or identify similar infrastructure segments.

## Data Processing Notes

### Excluded Infrastructure Types

The following are filtered out as they don't represent actual bike infrastructure:
- Pedestrian zones (Fußgängerzone)
- Pedestrian crossings used as walking sections
- Sidewalks (even with "Fahrrad frei" signs)
- Ferry routes

### Geometry Processing

- MultiLineStrings are simplified where possible to continuous LineStrings
- Spatial indexing is used for efficient intersection queries
- Coordinate precision is handled carefully to avoid merging errors

## Contributing

When adding new data:
1. Download layers from official sources (Geoportal or Transparenzportal)
2. Place in appropriate time-stamped directory
3. Ensure CRS is set correctly (EPSG:25832)
4. Update processing scripts if new categories are added

## License

This project is licensed under the **Creative Commons Attribution 4.0 International License (CC BY 4.0)**.

### Citation

If you use this code or methodology in your research or publications, please cite this repository:

```bibtex
@software{hamburg_bike_data_2025,
  author = {Andre},
  title = {Hamburg Geoportal Bike Data Analysis},
  year = {2025},
  url = {https://github.com/yourusername/hamburg_geoportal_bike_data},
  note = {Analysis tools for Hamburg's bicycle infrastructure data}
}
```

Or in text format:
> Andre (2025). Hamburg Geoportal Bike Data Analysis. https://github.com/yourusername/hamburg_geoportal_bike_data

### Data License

**Important**: The CC BY 4.0 license applies to the code and analysis methods in this repository. The underlying data from Hamburg Geoportal and Transparenzportal is subject to its own licensing terms:

- **Data License Germany – Zero – Version 2.0** (typically used for Hamburg open data)
- Please refer to the Hamburg Geoportal and Transparenzportal terms of use for specific data licensing information

When publishing work using this project, cite both this repository (for the methods) and the Hamburg open data sources (for the data).

## References

- Hamburg Geoportal: https://geoportal-hamburg.de/
- Hamburg Transparenzportal: https://transparenz.hamburg.de/
- Data License Germany – Zero – Version 2.0: https://www.govdata.de/dl-de/zero-2-0
- Creative Commons BY 4.0: https://creativecommons.org/licenses/by/4.0/
