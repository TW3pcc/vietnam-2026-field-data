"""
Vietnam 2026 Field Data Processor
==================================
Author  : Theron W. Wells III
Date    : 2026
Purpose : Processes ArcGIS Field Maps export (Vietnam_2026_0.csv) into:
            - Validated, region-tagged records
            - GeoJSON feature collection (importable to ArcGIS Online, QGIS, GitHub)
            - Markdown field report with statistics
            - (Optional) ArcGIS feature class via arcpy

Workflow:
    ArcGIS Field Maps --> Hosted Feature Layer --> CSV Export
        --> This Script --> GeoJSON + Report --> GitHub / ArcGIS Online

Dependencies:
    - Python 3.x (standard library only for core functions)
    - arcpy (optional -- only needed for feature class export block)

Run from ArcGIS Pro Python environment OR any Python 3 interpreter.
"""

import csv
import json
import os
import math
from datetime import datetime
from collections import defaultdict

# -----------------------------------------------------------------
# CONFIGURATION
# -----------------------------------------------------------------

INPUT_CSV  = r"C:\Users\Theron\Desktop\Vietnam Travel\Vietnam_Stops_2026\Vietnam_2026_0.csv"
OUTPUT_DIR = r"C:\Users\Theron\Desktop\Vietnam Travel\Vietnam_Stops_2026"

GEOJSON_OUT = os.path.join(OUTPUT_DIR, "Vietnam_2026_Stops.geojson")
REPORT_OUT  = os.path.join(OUTPUT_DIR, "Vietnam_2026_Field_Report.md")

# Optional arcpy output (set to None to skip)
ARCPY_GDB     = None   # e.g. r"C:\GIS\Vietnam.gdb"
ARCPY_FC_NAME = "Vietnam_2026_Stops"

# -----------------------------------------------------------------
# REGION DEFINITIONS
# Bounding boxes derived from field data coordinate ranges.
# Format: (lon_min, lon_max, lat_min, lat_max)
# -----------------------------------------------------------------

REGIONS = {
    "Hanoi": {
        "bounds": (105.820, 105.870, 21.020, 21.055),
        "chapter": 1,
        "description": "Capital city; Old Quarter, temples, food culture",
        "layer_view": "Hanoi_Layer_View"
    },
    "Tam Coc": {
        "bounds": (105.880, 105.950, 20.190, 20.260),
        "chapter": 2,
        "description": "Karst landscape; Trang An UNESCO site, Hang Mua, Thung Nham",
        "layer_view": "Tam_Coc_Layer_View"
    },
    "Sapa": {
        "bounds": (103.830, 103.890, 22.295, 22.345),
        "chapter": 3,
        "description": "Northern highlands; H'Mong culture, terraced agriculture, trekking",
        "layer_view": "Sapa_Layer_View"
    },
    "Phong Nha": {
        "bounds": (106.250, 106.610, 17.500, 17.640),
        "chapter": 4,
        "description": "Karst cave systems; Phong Nha-Ke Bang NP, Son River",
        "layer_view": "Phong_Nha_Layer_View"
    },
    "Hue": {
        "bounds": (107.530, 107.660, 16.380, 16.480),
        "chapter": 5,
        "description": "Imperial capital; Nguyen Dynasty tombs, Perfume River, UNESCO sites",
        "layer_view": "Hue_Layer_View"
    },
    "Hoi An": {
        "bounds": (108.190, 108.380, 15.870, 16.210),
        "chapter": 6,
        "description": "Ancient trading port; coastal ecology, Old Town, artisan culture",
        "layer_view": "Hoi_An_Layer_View"
    },
}

VALID_TYPES = {"Culture", "Ecology", "Logistics", "Reflective", ""}


# -----------------------------------------------------------------
# HELPER FUNCTIONS
# -----------------------------------------------------------------

def assign_region(lon, lat):
    """Assigns region name via coordinate bounding box. Returns 'Unclassified' if no match."""
    for region, meta in REGIONS.items():
        lon_min, lon_max, lat_min, lat_max = meta["bounds"]
        if lon_min <= lon <= lon_max and lat_min <= lat <= lat_max:
            return region
    return "Unclassified"


def validate_coordinates(lon, lat, objectid):
    """Validates coordinate plausibility for Vietnam extent (lon 102-110, lat 8-24)."""
    if not (-180 <= lon <= 180 and -90 <= lat <= 90):
        return False, f"OID {objectid}: Out-of-range coordinates ({lon}, {lat})"
    if not (102.0 <= lon <= 110.0 and 8.0 <= lat <= 24.0):
        return False, f"OID {objectid}: Coordinates outside Vietnam extent ({lon}, {lat})"
    return True, "OK"


def haversine_km(lon1, lat1, lon2, lat2):
    """Great-circle distance between two WGS84 points, in kilometers."""
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def parse_date(date_str):
    """Attempts multiple date format parses. Returns datetime or None."""
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except ValueError:
            continue
    return None


# -----------------------------------------------------------------
# MAIN PROCESSING
# -----------------------------------------------------------------

def load_and_validate(csv_path):
    """
    Reads the Field Maps CSV export, validates coordinates and types,
    assigns regions. Returns (records list, warnings list).
    """
    records = []
    warnings = []

    with open(csv_path, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)

        expected_cols = {"OBJECTID", "GlobalID", "Place", "Type of Place",
                         "Reflection", "Date", "Environment Observation", "x", "y"}
        missing = expected_cols - set(reader.fieldnames)
        if missing:
            raise ValueError(f"CSV missing expected columns: {missing}")

        for row in reader:
            oid = row["OBJECTID"].strip()

            if not row["Place"].strip():
                warnings.append(f"OID {oid}: Empty Place name -- skipped")
                continue

            try:
                lon = float(row["x"])
                lat = float(row["y"])
            except (ValueError, KeyError):
                warnings.append(f"OID {oid} ({row['Place']}): Could not parse coordinates -- skipped")
                continue

            is_valid, msg = validate_coordinates(lon, lat, oid)
            if not is_valid:
                warnings.append(msg + " -- skipped")
                continue

            rec_type = row.get("Type of Place", "").strip()
            if rec_type not in VALID_TYPES:
                warnings.append(
                    f"OID {oid} ({row['Place']}): Non-standard Type '{rec_type}' -- retained but flagged"
                )

            region = assign_region(lon, lat)
            if region == "Unclassified":
                warnings.append(
                    f"OID {oid} ({row['Place']}): ({lon:.4f}, {lat:.4f}) outside defined regions"
                )

            date_obj = parse_date(row.get("Date", ""))
            if not date_obj and row.get("Date", "").strip():
                warnings.append(f"OID {oid} ({row['Place']}): Could not parse date '{row['Date']}'")

            records.append({
                "objectid"  : oid,
                "global_id" : row.get("GlobalID", "").strip(),
                "place"     : row["Place"].strip(),
                "type"      : rec_type if rec_type else "Unclassified",
                "reflection": row.get("Reflection", "").strip(),
                "date_str"  : row.get("Date", "").strip(),
                "date_obj"  : date_obj,
                "photo_ref" : row.get("Photo Referrence", "").strip(),
                "env_obs"   : row.get("Environment Observation", "").strip(),
                "lon"       : lon,
                "lat"       : lat,
                "region"    : region,
                "chapter"   : REGIONS.get(region, {}).get("chapter", 0),
            })

    return records, warnings


def build_geojson(records):
    """
    Builds GeoJSON FeatureCollection from validated records.
    Compatible with ArcGIS Online, QGIS, Mapbox, Leaflet, GitHub map preview.
    """
    features = []
    for r in records:
        features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [r["lon"], r["lat"]]},
            "properties": {
                "OBJECTID"          : r["objectid"],
                "GlobalID"          : r["global_id"],
                "Place"             : r["place"],
                "Type"              : r["type"],
                "Region"            : r["region"],
                "StoryMap_Chapter"  : r["chapter"],
                "Date"              : r["date_str"],
                "Reflection"        : r["reflection"],
                "Environment_Obs"   : r["env_obs"],
                "Photo_Reference"   : r["photo_ref"],
            }
        })

    return {
        "type": "FeatureCollection",
        "name": "Vietnam_2026_Stops",
        "crs": {
            "type": "name",
            "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}
        },
        "features": features
    }


def compute_statistics(records):
    """Computes summary statistics grouped by region and type."""
    stats = {
        "total_stops"       : len(records),
        "by_region"         : defaultdict(lambda: {"count": 0, "types": defaultdict(int), "dates": []}),
        "by_type"           : defaultdict(int),
        "date_range"        : {"earliest": None, "latest": None},
        "total_distance_km" : 0.0,
        "unclassified"      : 0,
    }

    for r in records:
        region = r["region"]
        rtype  = r["type"]
        stats["by_region"][region]["count"] += 1
        stats["by_region"][region]["types"][rtype] += 1
        stats["by_type"][rtype] += 1
        if r["date_obj"]:
            stats["by_region"][region]["dates"].append(r["date_obj"])
            if not stats["date_range"]["earliest"] or r["date_obj"] < stats["date_range"]["earliest"]:
                stats["date_range"]["earliest"] = r["date_obj"]
            if not stats["date_range"]["latest"] or r["date_obj"] > stats["date_range"]["latest"]:
                stats["date_range"]["latest"] = r["date_obj"]
        if region == "Unclassified":
            stats["unclassified"] += 1

    # Approximate route distance -- inter-region legs only (>5 km apart)
    sorted_records = sorted(
        records, key=lambda x: (x["chapter"], x["date_obj"] or datetime.min)
    )
    for i in range(1, len(sorted_records)):
        dist = haversine_km(
            sorted_records[i - 1]["lon"], sorted_records[i - 1]["lat"],
            sorted_records[i]["lon"],     sorted_records[i]["lat"]
        )
        if dist > 5:
            stats["total_distance_km"] += dist

    return stats


def generate_report(records, stats, warnings):
    """Generates portfolio-quality Markdown field report for GitHub."""
    now      = datetime.now().strftime("%Y-%m-%d")
    earliest = stats["date_range"]["earliest"]
    latest   = stats["date_range"]["latest"]
    date_range_str = (
        f"{earliest.strftime('%B %d')} - {latest.strftime('%B %d, %Y')}"
        if earliest and latest else "Dates not fully parsed"
    )

    lines = [
        "# Vietnam 2026 -- GIS Field Data Report",
        f"**Generated:** {now}  ",
        f"**Collector:** Theron W. Wells III  ",
        f"**Platform:** ArcGIS Field Maps -> Hosted Feature Layer -> CSV Export  ",
        "",
        "---",
        "",
        "## Project Summary",
        "",
        "Personal GIS field data collection project documenting a 20-day expedition "
        "through Vietnam, May-June 2026. Data collected in real time using ArcGIS Field "
        "Maps; processed and exported via this script for GitHub hosting, GeoJSON "
        "distribution, and StoryMaps integration.",
        "",
        "**Workflow:**",
        "```",
        "ArcGIS Field Maps (mobile) --> Hosted Feature Layer (ArcGIS Online)",
        "    --> 6 Hosted Layer Views (one per region)",
        "        --> 6 Map Tour chapters (StoryMaps)",
        "        --> CSV Export --> Python Processing --> GeoJSON + Report (GitHub)",
        "```",
        "",
        "---",
        "",
        "## Collection Statistics",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| **Total Field Points** | {stats['total_stops']} |",
        f"| **Date Range** | {date_range_str} |",
        f"| **Trip Duration** | 20 days |",
        f"| **Regions / Layer Views** | {len([r for r in stats['by_region'] if r != 'Unclassified'])} |",
        f"| **Approx. Route Distance** | {stats['total_distance_km']:.0f} km (inter-region legs) |",
        f"| **Coordinate System** | WGS 1984 (EPSG:4326) |",
        "",
        "---",
        "",
        "## Stops by Region",
        "",
        "| Chapter | Region | Stops | Description |",
        "|---------|--------|-------|-------------|",
    ]

    for region_name, meta in sorted(REGIONS.items(), key=lambda x: x[1]["chapter"]):
        count = stats["by_region"][region_name]["count"]
        lines.append(f"| {meta['chapter']} | **{region_name}** | {count} | {meta['description']} |")
    if stats["unclassified"] > 0:
        lines.append(f"| -- | *Unclassified* | {stats['unclassified']} | Outside defined bounding boxes |")

    lines += [
        "",
        "---",
        "",
        "## Stops by Category",
        "",
        "| Type | Count | % of Total | Notes |",
        "|------|-------|-----------|-------|",
    ]

    type_notes = {
        "Culture"      : "Restaurants, temples, markets, historical sites, artisan stops",
        "Ecology"      : "Natural areas, beaches, rivers, karst formations, protected zones",
        "Logistics"    : "Hotels, transport hubs, transfer points",
        "Reflective"   : "Personal significance; emotional or contemplative stops",
        "Unclassified" : "Type field empty or non-standard at collection time",
    }
    total = stats["total_stops"]
    for t in ["Culture", "Ecology", "Logistics", "Reflective", "Unclassified"]:
        count = stats["by_type"].get(t, 0)
        if count > 0:
            pct = f"{(count / total * 100):.1f}%"
            lines.append(f"| **{t}** | {count} | {pct} | {type_notes.get(t, '')} |")

    lines += ["", "---", "", "## Regional Breakdown by Category", ""]
    for region_name, meta in sorted(REGIONS.items(), key=lambda x: x[1]["chapter"]):
        r_stats = stats["by_region"][region_name]
        if r_stats["count"] == 0:
            continue
        lines += [
            f"### Chapter {meta['chapter']}: {region_name}",
            f"**Total stops:** {r_stats['count']}  ",
            f"**Layer View:** `{meta['layer_view']}`  ",
            "",
            "| Type | Count |",
            "|------|-------|",
        ]
        for t, c in sorted(r_stats["types"].items()):
            lines.append(f"| {t} | {c} |")
        lines.append("")

    lines += [
        "---", "",
        "## Data Schema", "",
        "| Field | Type | Description |",
        "|-------|------|-------------|",
        "| `OBJECTID` | Integer | Auto-generated unique ID |",
        "| `GlobalID` | GUID | Links to photo attachments in hosted layer |",
        "| `Place` | String | Stop name |",
        "| `Type of Place` | String (Domain) | Culture / Ecology / Logistics / Reflective |",
        "| `Reflection` | String | Field observation at collection time |",
        "| `Date` | Date | Collection date |",
        "| `Photo Reference` | String | Photo description or filename |",
        "| `Environment Observation` | String | Ecological/environmental conditions |",
        "| `x` | Double | Longitude (WGS 1984) |",
        "| `y` | Double | Latitude (WGS 1984) |",
        "| `Region` *(derived)* | String | Assigned by processor via bounding box |",
        "| `StoryMap_Chapter` *(derived)* | Integer | StoryMap chapter number |",
        "",
        "---", "",
        "## Tools & Workflow", "",
        "| Tool | Role |",
        "|------|------|",
        "| ArcGIS Field Maps | Mobile field data collection |",
        "| ArcGIS Online | Hosted Feature Layer & Layer View management |",
        "| ArcGIS StoryMaps | Public narrative presentation |",
        "| Python 3 (stdlib) | Validation, GeoJSON export, report generation |",
        "| arcpy *(optional)* | Feature class export to geodatabase |",
        "| GitHub | Version control, GeoJSON map preview, portfolio hosting |",
        "",
    ]

    if warnings:
        lines += [
            "---", "",
            "## Validation Log", "",
            f"*{len(warnings)} issue(s) flagged during processing:*", "",
        ]
        for w in warnings:
            lines.append(f"- {w}")
        lines.append("")

    lines += [
        "---", "",
        "## Links", "",
        "- 📖 [Vietnam 2026 StoryMap](#) *(add your ArcGIS StoryMaps URL)*",
        "- 🗺️ [ArcGIS Online Web Map](#) *(add your web map URL)*",
        "- 👤 [Portfolio / LinkedIn](#) *(add your URL)*",
        "",
        "---",
        "",
        "*Data collected in the field. Processed at home. The map was always the plan.*",
        "",
        f"*Report generated by `vietnam_field_processor.py` -- {now}*",
    ]

    return "\n".join(lines)


# -----------------------------------------------------------------
# OPTIONAL: ARCPY FEATURE CLASS EXPORT
# Set ARCPY_GDB path above and run from ArcGIS Pro Python env.
# -----------------------------------------------------------------

def export_to_feature_class(records, gdb_path, fc_name):
    """Exports records to ArcGIS feature class. Requires arcpy."""
    try:
        import arcpy
    except ImportError:
        print("  [SKIP] arcpy not available -- run from ArcGIS Pro Python environment")
        return

    sr = arcpy.SpatialReference(4326)
    fc_path = os.path.join(gdb_path, fc_name)

    if arcpy.Exists(fc_path):
        arcpy.management.Delete(fc_path)

    arcpy.management.CreateFeatureclass(gdb_path, fc_name, "POINT", spatial_reference=sr)

    field_defs = [
        ("OBJECTID_orig", "LONG",  "",    "Original OBJECTID"),
        ("GlobalID_orig", "TEXT",  "38",  "Original GlobalID"),
        ("Place",         "TEXT",  "255", "Stop name"),
        ("Type",          "TEXT",  "50",  "Category"),
        ("Region",        "TEXT",  "50",  "Assigned region"),
        ("Chapter",       "SHORT", "",    "StoryMap chapter"),
        ("Date_Str",      "TEXT",  "20",  "Collection date"),
        ("Reflection",    "TEXT",  "2000","Field reflection"),
        ("Env_Obs",       "TEXT",  "2000","Environment observation"),
        ("Photo_Ref",     "TEXT",  "255", "Photo reference"),
    ]
    for fname, ftype, flength, falias in field_defs:
        kwargs = {"field_alias": falias}
        if ftype == "TEXT" and flength:
            kwargs["field_length"] = int(flength)
        arcpy.management.AddField(fc_path, fname, ftype, **kwargs)

    fields = [
        "SHAPE@XY", "OBJECTID_orig", "GlobalID_orig", "Place", "Type",
        "Region", "Chapter", "Date_Str", "Reflection", "Env_Obs", "Photo_Ref"
    ]

    with arcpy.da.InsertCursor(fc_path, fields) as cursor:
        for r in records:
            cursor.insertRow([
                (r["lon"], r["lat"]), int(r["objectid"]), r["global_id"],
                r["place"], r["type"], r["region"], r["chapter"],
                r["date_str"], r["reflection"], r["env_obs"], r["photo_ref"],
            ])

    print(f"  Feature class created: {fc_path} ({len(records)} records)")


# -----------------------------------------------------------------
# ENTRY POINT
# -----------------------------------------------------------------

def main():
    print("=" * 60)
    print("  Vietnam 2026 Field Data Processor")
    print("  Theron W. Wells III")
    print("=" * 60)

    print(f"\n[1/4] Loading: {os.path.basename(INPUT_CSV)}")
    records, warnings = load_and_validate(INPUT_CSV)
    print(f"      {len(records)} valid records | {len(warnings)} warning(s)")

    print("\n[2/4] Computing statistics...")
    stats = compute_statistics(records)
    for region, meta in sorted(REGIONS.items(), key=lambda x: x[1]["chapter"]):
        c = stats["by_region"][region]["count"]
        print(f"      Ch.{meta['chapter']} {region:15s}: {c} stops")
    print(f"      Type breakdown: {dict(stats['by_type'])}")

    print(f"\n[3/4] Exporting GeoJSON -> {os.path.basename(GEOJSON_OUT)}")
    geojson = build_geojson(records)
    with open(GEOJSON_OUT, "w", encoding="utf-8") as f:
        json.dump(geojson, f, ensure_ascii=False, indent=2)
    print(f"      {len(geojson['features'])} features written")

    print(f"\n[4/4] Generating report -> {os.path.basename(REPORT_OUT)}")
    report = generate_report(records, stats, warnings)
    with open(REPORT_OUT, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"      Report written")

    if ARCPY_GDB:
        print(f"\n[OPT] Exporting to feature class -> {ARCPY_FC_NAME}")
        export_to_feature_class(records, ARCPY_GDB, ARCPY_FC_NAME)

    print("\n" + "=" * 60)
    print("  COMPLETE")
    print(f"  GeoJSON  ->  {GEOJSON_OUT}")
    print(f"  Report   ->  {REPORT_OUT}")
    print("=" * 60)
    print("\nNEXT STEPS:")
    print("  1. Commit both output files to GitHub")
    print("     (GitHub auto-renders .geojson as an interactive map!)")
    print("  2. Add your StoryMap + web map URLs to the report links section")
    print("  3. Link the GitHub repo from your StoryMap Methodology panel")


if __name__ == "__main__":
    main()
