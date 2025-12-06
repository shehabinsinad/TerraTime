# 🌍 TerraTime: The AI Earth Auditor

*TerraTime* is an interactive geospatial intelligence tool built with *Google Earth Engine, **Streamlit, and **Landsat satellite data* to visualize and audit *10 years of vegetation change (2014–2024)* for any point on Earth.

The app converts raw NDVI satellite data into an easy-to-understand *Green Score, generates **health maps, and produces an annual **Landsat timelapse GIF* for deep analysis.

---

## 🚀 Features

### 🛰 Satellite-Powered Audit
- Uses *NASA/USGS Landsat 8 Surface Reflectance* data  
- Computes NDVI for *2014 vs 2024*  
- Converts NDVI → *Green Score (0–100)*  
- Identifies vegetation gain/loss  

### 🗺 Health Map Overlay
- Red = vegetation loss  
- Green = vegetation gain  
- Automatically clipped to user-selected radius  

### ⏱ 10-Year Timelapse GIF (2014–2024)
- Generated using Google Earth Engine + geemap  
- Downloadable from inside the app  

### 🎭 Persona-Based UI
Choose how deep you want to explore the data:
- *Scientist* — full statistics, NDVI time series, technical breakdown  
- *Student* — simplified explanation + NDVI trend chart  
- *Public* — minimal, clean, easy to understand  

### 📍 Location Selection  
- Search any place using OpenStreetMap/Nominatim  
- Adjustable radius (1–50 km depending on persona)  
---

## 🧠 How It Works (Short Technical Summary)

1. User selects a location  
2. App builds a *circular ROI* around the coordinates  
3. TerraTime downloads Landsat SR images for:
   - 2014 composite  
   - 2024 composite  
4. NDVI is calculated:
   - NDVI = (NIR − RED) / (NIR + RED)
5. NDVI → Green Score (0–100)  
6. A difference image produces a *health map*  
7. Annual composites generate a *timelapse GIF* via geemap.create_timelapse()  
8. Output changes depending on persona selected  

---

## 🧩 Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Streamlit |
| Geospatial Engine | Google Earth Engine (ee) |
| Mapping | geemap, folium |
| Geocoding | Nominatim (OpenStreetMap) |
| Timelapse Generation | geemap, ffmpeg |
| Plotting | Streamlit charts |

---

## 📦 Installation

### 1. Clone the repository
bash
git clone https://github.com/shehabinsinad/TerraTime.git
cd TerraTime
5. NDVI → Green Score (0–100)  
6. A difference image produces a **health map**  
7. Annual composites generate a **timelapse GIF** via `geemap.create_timelapse()`  
8. Output changes depending on persona selected  

---

## 🧩 Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Streamlit |
| Geospatial Engine | Google Earth Engine (ee) |
| Mapping | geemap, folium |
| Geocoding | Nominatim (OpenStreetMap) |
| Timelapse Generation | geemap, ffmpeg |
| Plotting | Streamlit charts |

---

## 📦 Installation

### 1. Clone the repository
bash
git clone https://github.com/shehabinsinad/TerraTime.git
cd TerraTime
pip install -r requirements.txt
