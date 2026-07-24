# Vietnam 2026 -- GIS Field Data Report
**Generated:** 2026-07-23  
**Collector:** Theron W. Wells III  
**Platform:** ArcGIS Field Maps -> Hosted Feature Layer -> CSV Export  

---

## Project Summary

Personal GIS field data collection project documenting a 20-day expedition through Vietnam, May-June 2026. Data collected in real time using ArcGIS Field Maps; processed and exported via this script for GitHub hosting, GeoJSON distribution, and StoryMaps integration.

**Workflow:**
```
ArcGIS Field Maps (mobile) --> Hosted Feature Layer (ArcGIS Online)
    --> 6 Hosted Layer Views (one per region)
        --> 6 Map Tour chapters (StoryMaps)
        --> CSV Export --> Python Processing --> GeoJSON + Report (GitHub)
```

---

## Collection Statistics

| Metric | Value |
|--------|-------|
| **Total Field Points** | 71 |
| **Date Range** | May 18 - June 09, 2026 |
| **Trip Duration** | 20 days |
| **Regions / Layer Views** | 6 |
| **Approx. Route Distance** | 2039 km (inter-region legs) |
| **Coordinate System** | WGS 1984 (EPSG:4326) |

---

## Stops by Region

| Chapter | Region | Stops | Description |
|---------|--------|-------|-------------|
| 1 | **Hanoi** | 20 | Capital city; Old Quarter, temples, food culture |
| 2 | **Tam Coc** | 10 | Karst landscape; Trang An UNESCO site, Hang Mua, Thung Nham |
| 3 | **Sapa** | 10 | Northern highlands; H'Mong culture, terraced agriculture, trekking |
| 4 | **Phong Nha** | 5 | Karst cave systems; Phong Nha-Ke Bang NP, Son River |
| 5 | **Hue** | 11 | Imperial capital; Nguyen Dynasty tombs, Perfume River, UNESCO sites |
| 6 | **Hoi An** | 13 | Ancient trading port; coastal ecology, Old Town, artisan culture |
| -- | *Unclassified* | 2 | Outside defined bounding boxes |

---

## Stops by Category

| Type | Count | % of Total | Notes |
|------|-------|-----------|-------|
| **Culture** | 43 | 60.6% | Restaurants, temples, markets, historical sites, artisan stops |
| **Ecology** | 13 | 18.3% | Natural areas, beaches, rivers, karst formations, protected zones |
| **Logistics** | 12 | 16.9% | Hotels, transport hubs, transfer points |
| **Reflective** | 2 | 2.8% | Personal significance; emotional or contemplative stops |
| **Unclassified** | 1 | 1.4% | Type field empty or non-standard at collection time |

---

## Regional Breakdown by Category

### Chapter 1: Hanoi
**Total stops:** 20  
**Layer View:** `Hanoi_Layer_View`  

| Type | Count |
|------|-------|
| Culture | 15 |
| Ecology | 1 |
| Logistics | 3 |
| Reflective | 1 |

### Chapter 2: Tam Coc
**Total stops:** 10  
**Layer View:** `Tam_Coc_Layer_View`  

| Type | Count |
|------|-------|
| Culture | 5 |
| Ecology | 3 |
| Logistics | 2 |

### Chapter 3: Sapa
**Total stops:** 10  
**Layer View:** `Sapa_Layer_View`  

| Type | Count |
|------|-------|
| Culture | 5 |
| Ecology | 2 |
| Logistics | 1 |
| Reflective | 1 |
| Unclassified | 1 |

### Chapter 4: Phong Nha
**Total stops:** 5  
**Layer View:** `Phong_Nha_Layer_View`  

| Type | Count |
|------|-------|
| Culture | 1 |
| Ecology | 2 |
| Logistics | 2 |

### Chapter 5: Hue
**Total stops:** 11  
**Layer View:** `Hue_Layer_View`  

| Type | Count |
|------|-------|
| Culture | 8 |
| Ecology | 2 |
| Logistics | 1 |

### Chapter 6: Hoi An
**Total stops:** 13  
**Layer View:** `Hoi_An_Layer_View`  

| Type | Count |
|------|-------|
| Culture | 7 |
| Ecology | 3 |
| Logistics | 3 |

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
| `Photo Reference` | String | Photo description or filename |
| `Environment Observation` | String | Ecological/environmental conditions |
| `x` | Double | Longitude (WGS 1984) |
| `y` | Double | Latitude (WGS 1984) |
| `Region` *(derived)* | String | Assigned by processor via bounding box |
| `StoryMap_Chapter` *(derived)* | Integer | StoryMap chapter number |

---

## Tools & Workflow

| Tool | Role |
|------|------|
| ArcGIS Field Maps | Mobile field data collection |
| ArcGIS Online | Hosted Feature Layer & Layer View management |
| ArcGIS StoryMaps | Public narrative presentation |
| Python 3 (stdlib) | Validation, GeoJSON export, report generation |
| arcpy *(optional)* | Feature class export to geodatabase |
| GitHub | Version control, GeoJSON map preview, portfolio hosting |

---

## Validation Log

*2 issue(s) flagged during processing:*

- OID 28 (Hai Van Pass lookout): (108.1326, 16.1886) outside defined regions
- OID 67 (Viet Pearl): (108.0780, 16.2393) outside defined regions

---

## Links

- 📖 [Vietnam 2026 StoryMap](#) *(add your ArcGIS StoryMaps URL)*
- 🗺️ [ArcGIS Online Web Map](#) *(add your web map URL)*
- 👤 [Portfolio / LinkedIn](#) *(add your URL)*

---

*Data collected in the field. Processed at home. The map was always the plan.*

*Report generated by `vietnam_field_processor.py` -- 2026-07-23*