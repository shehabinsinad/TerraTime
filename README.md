# 🌍 TerraTime: The AI Earth Auditor

*TerraTime* is an interactive geospatial intelligence tool built with *Google Earth Engine, **Streamlit, and **Landsat satellite data* to visualize and audit *10 years of vegetation change (2014–2024)* for any point on Earth.

The app converts raw NDVI satellite data into an easy-to-understand *Green Score* and generates *health maps* for deep environmental analysis.

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

### ⏱ 10-Year Timelapse GIF (2014–2024) ⚠️
- *Currently disabled by default for performance*
- Can be enabled in code (requires ffmpeg)
- When enabled: downloadable annual composites  

### 🎭 Persona-Based UI
Choose how deep you want to explore the data:
- *Scientist* — full statistics, technical breakdown, customizable radius
- *Student* — simplified explanation with key metrics
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
```bash
git clone https://github.com/shehabinsinad/TerraTime.git
cd TerraTime
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up Google Earth Engine
Before running the app, you need to:

**A. Authenticate:**
```python
import ee
ee.Authenticate()
```

**B. Create/Register a Cloud Project:**
1. Visit https://code.earthengine.google.com/
2. Sign in with your Google account
3. Create or select a cloud project
4. The project will be automatically registered

### 4. Configure your project
Edit `app.py` line 60 and replace `'terratime-autocomplete'` with your Google Cloud project ID.

### 5. Run the application
```bash
streamlit run app.py
```

The app will open in your default browser at `http://localhost:8501`

---

## 🎯 Quick Start Guide

1. **Choose your identity**: Select Scientist, Student, or Public mode
2. **Enter a location**: Type any city, address, or landmark
3. **Adjust settings**: Set your analysis radius and preferences
4. **Run Audit**: Click the button to analyze 10 years of vegetation change
5. **Explore results**: View maps, green scores, and download timelapses

---

## 📝 Requirements

- Python 3.10+
- Google Earth Engine account (free at [earthengine.google.com](https://earthengine.google.com))
- *Optional:* ffmpeg (for timelapse generation, if you enable it)

---

## 📄 License

This project is open source and available under the MIT License.

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

---

## ⚙️ Performance Notes

For optimal performance (< 30 second load times), the following features are disabled by default:
- NDVI time series (2014-2024 trend chart)
- Timelapse GIF generation

These can be re-enabled in `app.py` if needed, but will increase load times to 2-5 minutes.

---
