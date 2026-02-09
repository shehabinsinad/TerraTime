# 🌍 TerraTime: Environmental Change Monitoring

An interactive web application for analyzing 10-year vegetation changes using satellite imagery and NDVI calculations.

## 📋 Overview

TerraTime allows users to visualize environmental changes for any location on Earth by analyzing NASA/USGS Landsat satellite data from 2014 to 2024.

## ✨ Key Features

- **Global Location Search** - Analyze any point on Earth using OpenStreetMap geocoding
- **NDVI Analysis** - Normalized Difference Vegetation Index calculations showing vegetation health
- **Visual Health Maps** - Color-coded maps (red = vegetation loss, green = vegetation gain)
- **Green Score** - 0-100 score representing vegetation health
- **Multi-User Modes** - Public (simple), Student (educational), Scientist (detailed data)
- **10-Year Timelapse** - Animated visualization of environmental change (optional feature)

## 🌱 What is NDVI?

**NDVI (Normalized Difference Vegetation Index)** measures vegetation health using satellite spectral data:
```
NDVI = (NIR - Red) / (NIR + Red)
```

- **NIR:** Near-Infrared light (reflected strongly by healthy plants)
- **Red:** Red visible light (absorbed by chlorophyll)
- **Range:** -1 to +1 (higher = healthier vegetation)

## 🛠️ Tech Stack

- **Frontend:** Python, Streamlit
- **Geospatial Processing:** Google Earth Engine API
- **Mapping:** geemap, folium
- **Data Source:** NASA/USGS Landsat 8 Surface Reflectance
- **Geocoding:** Nominatim (OpenStreetMap)

## 🎯 How It Works

1. User enters location name (e.g., "Amazon Rainforest")
2. App geocodes location to coordinates
3. Google Earth Engine fetches Landsat imagery:
   - 2014 composite (cloud-free median)
   - 2024 composite (cloud-free median)
4. NDVI calculated for both time periods
5. Difference map shows vegetation change
6. Green Score generated (0-100 scale)
7. Results displayed based on user mode (Public/Student/Scientist)

## 👥 Hackathon Project - My Contribution

This was a **5-person hackathon project** (24-hour build). My specific contributions:

- **Google Earth Engine API integration** - Authentication, image collection setup, error handling
- **Data processing pipeline optimization** - Reduced load times from 30+ seconds to <10 seconds through caching
- **Location validation** - Implemented error handling for invalid coordinates and API failures
- **Cloud filtering logic** - Ensured only cloud-free images are used in analysis

**Other components** (NDVI calculations, UI design, timelapse generation, health map visualization, persona modes) were developed by teammates.

## 📂 Project Structure
```
TerraTime/
├── app.py                  # Main Streamlit application
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## 🚀 Setup Instructions

### Prerequisites
- Python 3.10+
- Google Earth Engine account ([signup free](https://earthengine.google.com))

### Installation

1. Clone the repository
```bash
git clone https://github.com/shehabinsinad/TerraTime.git
cd TerraTime
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Authenticate Google Earth Engine
```bash
earthengine authenticate
```

4. Configure your project
- Visit [Google Earth Engine](https://code.earthengine.google.com)
- Create/select a cloud project
- Update `app.py` line 60 with your project ID

5. Run the application
```bash
streamlit run app.py
```

Access at `http://localhost:8501`

## ⚙️ Performance Notes

For optimal performance (<10 second load times):
- Timelapse GIF generation is disabled by default
- Can be re-enabled in code (requires ffmpeg, increases load time to 2-5 minutes)

## 📊 Use Cases

- **Environmental Research:** Track deforestation, urban expansion, drought impact
- **Education:** Teach remote sensing concepts and environmental change
- **Public Awareness:** Visualize climate impact on specific regions

## 📝 Learning Outcomes

This hackathon project taught me:
- Working with large-scale geospatial APIs (Google Earth Engine)
- Optimizing data processing pipelines under time constraints
- REST API integration and error handling
- Rapid prototyping in a team environment

## 📄 License

Hackathon project developed in 2024.

## 🙏 Acknowledgments

- NASA/USGS for Landsat 8 satellite data
- Google Earth Engine for geospatial processing platform
- OpenStreetMap for geocoding services

---

**Note:** This project was built during a 24-hour hackathon with a team of 5. The codebase represents a rapid prototype and may require refactoring for production use.
