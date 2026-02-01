import math
from shapely import Geometry
from shapely.geometry import LineString, MultiLineString, Point
from shapely.ops import linemerge


def calculate_bearing(linestring, distance_along_path=None, start_at_intersection_with: Geometry=None):
    """Return bearing (degrees 0–360) of a LineString or MultiLineString.

    For MultiLineString the first coordinate of the first component and the last
    coordinate of the last component are used.

    distance_along_path = bearing between the start and a point at distance along the path
    start_at_intersection_with = (roughly) start at the intersection point with another geom
    """
    linestring = simplify_multilinestring(linestring)

    # get startpoint
    if start_at_intersection_with and linestring.intersects(start_at_intersection_with.buffer(1)):
        linestring_start = linestring.intersection(start_at_intersection_with.buffer(1))
    else:
        linestring_start = linestring

    if isinstance(linestring_start, MultiLineString):
        start_point = linestring_start.geoms[0].coords[0]
    else:  # Assume LineString-like
        start_point = linestring_start.coords[0]

    # get endpoint
    if isinstance(linestring, MultiLineString):
        end_point = linestring.geoms[-1].coords[-1]  # fallback is last point of line
        if distance_along_path and distance_along_path > linestring.length:
            total_len = 0
            end_point = None
            for geom in linestring.geoms:
                # normal interpolation of multiline strings often doesnt work.
                if total_len + geom.length >= distance_along_path:
                    end_point = geom.interpolate(distance_along_path-total_len).coords[0]
                    break
                total_len += geom.length
    else:  # Assume LineString-like
        if distance_along_path:
            end_point = linestring.interpolate(distance_along_path).coords[0]
        else:
            end_point = linestring.coords[-1]

    # calculate bearing
    start_x, start_y = start_point[0], start_point[1]
    end_x, end_y = end_point[0], end_point[1]

    # Guard zero-length
    if start_x == end_x and start_y == end_y:
        return 0.0

    angle = math.atan2(end_y - start_y, end_x - start_x)
    bearing = math.degrees(angle)
    if bearing < 0:
        bearing += 360
    return bearing




# Define a function to simplify MultiLineStrings to LineStrings when possible
def simplify_multilinestring(geom, precision=4):
    """
    Convert MultiLineString to LineString when possible, and reduce coordinate precision.
    
    Args:
        geom: The geometry to simplify
        precision: Number of decimal places to round coordinates to
    
    Returns:
        Simplified geometry (LineString when possible, or original geometry)
    """
    from shapely.geometry import LineString, MultiLineString
    
    # Round coordinates to specified precision to eliminate tiny gaps
    def round_coords(coords, prec):
        return [(round(x, prec), round(y, prec)) for x, y in coords]
    
    if geom.geom_type == 'LineString':
        return geom
    
    elif geom.geom_type == 'MultiLineString':
        # If it has only one component, convert to LineString
        if len(geom.geoms) == 1:
            rounded_coords = round_coords(list(geom.geoms[0].coords), precision)
            return LineString(rounded_coords)
        
        # Try to merge into a single LineString by concatenating coordinates
        try:
            # Extract all coordinates from all line segments with reduced precision
            all_coords = []
            for line in geom.geoms:
                all_coords.extend(round_coords(list(line.coords), precision))
            
            # Create a new LineString with all coordinates
            if all_coords:
                return LineString(all_coords)
            
        except Exception as e:
            print(f"Failed to convert MultiLineString to LineString: {e}")
            # If failed to create a LineString, keep as MultiLineString but with rounded coords
            parts = [LineString(round_coords(list(line.coords), precision)) for line in geom.geoms]
            return MultiLineString(parts)
    


def get_last_point_of_line(linestring: LineString|MultiLineString) -> Point:
    """Return the last point of a LineString or MultiLineString.

    For MultiLineString we take the last coordinate of the last component.
    (Assumes the MultiLineString represents a chained path; if not merged,
    order is preserved as stored.)
    """
    if isinstance(linestring, MultiLineString):
        return Point(linestring.geoms[-1].coords[-1])
    return Point(linestring.coords[-1])


def get_first_point_of_line(linestring: LineString|MultiLineString) -> Point:
    """Return the first point of a linear geometry (LineString or MultiLineString)."""
    if isinstance(linestring, MultiLineString):
        return Point(linestring.geoms[0].coords[0])
    return Point(linestring.coords[0])


def normalize_linear(geom):
    """If a MultiLineString can be merged into a single LineString, do so.

    linemerge will merge only if components are properly noded/connected.
    """
    if geom.geom_type == "MultiLineString":
        merged = linemerge(geom)
        return merged
    return geom


def full_reverse(geom: LineString|MultiLineString):
    """Reverse a LineString or MultiLineString preserving path continuity.

    Shapely's .reverse() on a MultiLineString reverses each component's
    coordinate order but keeps the component order the same. For chained
    paths that are stored as sequences of 2‑point segments this breaks the
    logical continuity. This helper reverses both the coordinates within
    each component AND the order of the components.
    """
    if isinstance(geom, LineString):
        return LineString(list(geom.coords)[::-1])
    if isinstance(geom, MultiLineString):
        # geom.geoms is a GeometrySequence; slicing with [::-1] returns a new
        # MultiLineString (not an iterable of components). Use reversed() or
        # index iteration instead of slicing.
        reversed_components = [
            LineString(list(geom.geoms[i].coords)[::-1])
            for i in range(len(geom.geoms)-1, -1, -1)
        ]
        return MultiLineString(reversed_components)
    raise TypeError(f"Unsupported geometry type for full_reverse: {geom.geom_type}")



def split_by_distance(linestring, max_length):
    """Split LineString into segments of max_length using segmentize."""
    from shapely.geometry import LineString
    
    if linestring.length <= max_length:
        return [linestring]
    
    # Use segmentize to add vertices at max_length intervals
    segmentized = linestring.segmentize(max_length)
    
    # Convert to individual segments between consecutive vertices
    coords = list(segmentized.coords)
    segments = []
    
    for i in range(len(coords) - 1):
        segment = LineString([coords[i], coords[i + 1]])
        segments.append(segment)
    
    return segments
