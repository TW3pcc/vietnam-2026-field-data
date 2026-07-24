# Vietnam 2026 — GIS Field Data Collection Project

**Theron W. Wells III** | GIS Analyst | [ArcGIS StoryMap](https://storymaps.arcgis.com/stories/3fddce57deaa4f1190bdc4a053dbd75b)

---

## Overview

Personal GIS field data collection project documenting a 20-day solo expedition through Vietnam, May–June 2026. Data was collected in real time using **ArcGIS Field Maps** on mobile, organized into six regional hosted feature layer views, and processed via Python for export and analysis.

This repository contains the data processing layer beneath the public-facing StoryMap — the part of the project that doesn't show up in the narrative but demonstrates the technical infrastructure behind it.

> *This is what I do when I go on vacation.*

---

## Repository Contents

| File | Description |
|------|-------------|
| [`Vietnam_2026_Stops.geojson`](./Vietnam_2026_Stops.json) | 71 geo-referenced field points — click to view interactive map |
| [`vietnam_field_processor.py`](./vietnam_field_processor.py) | Python script: validates, region-tags, and exports field data |
| [`Vietnam_2026_Field_Report.md`](./Vietnam_2026_Field_Report.md) | Full field report with statistics, schema, and methodology |

---

## Interactive Map

Click the GeoJSON file above — GitHub automatically renders it as an interactive map showing all 71 collection points across six regions.

---

## Field Statistics

| Metric | Value |
|--------|-------|
| Total field points | 71 |
| Date range | May 18 – June 8, 2026 |
| Trip duration | 20 days |
| Regions / Layer Views | 6 |
| Coordinate system | WGS 1984 (EPSG:4326) |

### Stops by Region

| Ch | Region | Stops | Notes |
|----|--------|-------|-------|
| 1 | Hanoi | 20 | Capital city; Old Quarter, temples, food culture |
| 2 | Tam Coc | 10 | Karst landscape; Trang An UNESCO site |
| 3 | Sapa | 10 | Northern highlands; H'Mong culture, terraced agriculture |
| 4 | Phong Nha | 5 | Karst cave systems; Phong Nha-Ke Bang NP |
| 5 | Hue | 11 | Imperial capital; Nguyen Dynasty, Perfume River |
| 6 | Hoi An | 13 | Ancient trading port; coastal ecology, Old Town |

### Stops by Category

| Type | Count | Description |
|------|-------|-------------|
| Culture | 43 | Restaurants, temples, markets, historical sites |
| Ecology | 13 | Natural areas, beaches, rivers, karst formations |
| Logistics | 12 | Hotels, transport hubs, transfer points |
| Reflective | 2 | Personal significance; contemplative stops |

---

## Technical Workflow

```
ArcGIS Field Maps (mobile collection)
    ↓
Hosted Feature Layer (ArcGIS Online)
    ↓
6 Hosted Layer Views (one per region)
    ↓
6 Map Tour chapters (ArcGIS StoryMaps)
    ↓
CSV Export → vietnam_field_processor.py
    ↓
Vietnam_2026_Stops.geojson + Vietnam_2026_Field_Report.md (this repo)
```

---

## Script Features (`vietnam_field_processor.py`)

- **Coordinate validation** — checks all points fall within Vietnam extent (WGS84)
- **Region assignment** — bounding-box classification into 6 regional chapters
- **Category statistics** — stop counts by type per region
- **Haversine distance** — approximate route distance calculation between stops
- **GeoJSON export** — compatible with ArcGIS Online, QGIS, Mapbox, Leaflet
- **Markdown report** — auto-generated field report with full statistics
- **Optional arcpy export** — feature class output when run from ArcGIS Pro

```bash
python vietnam_field_processor.py
```

---

## Data Schema

| Field | Type | Description |
|-------|------|-------------|
| `OBJECTID` | Integer | Auto-generated unique ID |
| `GlobalID` | GUID | Links to photo attachments in hosted layer |
| `Place` | String | Stop name |
| `Type of Place` | String (Domain) | Culture / Ecology / Logistics / Reflective |
| `Reflection` | String | Field observation at collection time |
| `Date` | Date | Collection date |
| `x` / `y` | Double | Longitude / Latitude (WGS 1984) |
| `Region` *(derived)* | String | Assigned by processor via bounding box |
| `StoryMap_Chapter` *(derived)* | Integer | StoryMap chapter number |

---

## Tools Used

| Tool | Role |
|------|------|
| ArcGIS Field Maps | Mobile field data collection |
| ArcGIS Online | Hosted Feature Layer & Layer View management |
| ArcGIS StoryMaps | Public narrative presentation |
| Python 3 (stdlib) | Validation, GeoJSON export, report generation |
| arcpy *(optional)* | Feature class export from ArcGIS Pro |
| GitHub | Version control, GeoJSON preview, portfolio hosting |

---

## Links

- 📖 [Vietnam 2026 StoryMap](https://storymaps.arcgis.com/stories/3fddce57deaa4f1190bdc4a053dbd75b)
- 👤 [GitHub Profile](https://github.com/TW3pcc)

---

*Data collected in the field. Processed at home. The map was always the plan.*
