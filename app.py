"""
TerraTime: The AI Earth Auditor
--------------------------------
Streamlit + Google Earth Engine + geemap app.

FLOW:
1) Splash screen
2) Persona selection
3) Main app (Scientist / Student / Public)
"""

import os

import streamlit as st
import ee
import geemap.foliumap as geemap
import geemap as geemap_core
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderServiceError, GeocoderTimedOut


# --------------------------
# GLOBAL BACKGROUND WALLPAPER
# --------------------------

BACKGROUND_URL = (
    "https://eoimages.gsfc.nasa.gov/images/imagerecords/73000/73909/"
    "world.topo.bathy.200412.3x5400x2700.jpg"
)


def apply_wallpaper():
    """
    Set a dark overlay + NASA Earth wallpaper as the full app background.
    """
    css = f"""
    <style>
    .stApp {{
        background-image:
            linear-gradient(rgba(0,0,0,0.70), rgba(0,0,0,0.92)),
            url("{BACKGROUND_URL}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        color: #f5f5f5;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


# --------------------------
# Google Earth Engine initialization
# --------------------------
def initialize_earth_engine():
    """
    Initialize Earth Engine using geemap.ee_initialize().
    """
    try:
        geemap_core.ee_initialize()
    except Exception as e:
        st.error(
            "Could not initialize Google Earth Engine.\n\n"
            "Make sure you have authenticated already:\n"
            "1) In a Python shell: `import ee; ee.Authenticate(); ee.Initialize()`\n"
            "   OR\n"
            "2) In a terminal: `earthengine authenticate`\n\n"
            f"Raw error: {e}"
        )
        st.stop()


# --------------------------
# OpenStreetMap / Nominatim helpers
# --------------------------
def get_osm_suggestions(query: str, max_results: int = 5):
    """
    Use OpenStreetMap Nominatim to get multiple matching locations for a query.
    """
    if not query or len(query.strip()) < 3:
        return []

    geolocator = Nominatim(user_agent="terrra_time_app_suggestions")
    try:
        results = geolocator.geocode(
            query,
            exactly_one=False,
            limit=max_results,
        )
        if not results:
            return []
        return results
    except (GeocoderTimedOut, GeocoderServiceError):
        return []
    except Exception:
        return []


def geocode_location(address: str):
    """
    Geocode a text address into (latitude, longitude) using OSM Nominatim.
    """
    geolocator = Nominatim(user_agent="terrra_time_app_geocode")
    try:
        location = geolocator.geocode(address)
    except (GeocoderTimedOut, GeocoderServiceError):
        return None
    except Exception:
        return None

    return location


# --------------------------
# NDVI + imagery helpers
# --------------------------
def create_roi(lon: float, lat: float, buffer_km: float = 5.0):
    """
    Create an Earth Engine geometry: a circular buffer around the point
    with the given radius in kilometers.
    """
    point = ee.Geometry.Point([lon, lat])
    roi = point.buffer(buffer_km * 1000)  # circle
    return roi


def get_ndvi_image(year: int, roi: ee.Geometry) -> ee.Image:
    """
    Median composite Landsat 8 Surface Reflectance NDVI for a given year.
    """
    start = ee.Date.fromYMD(year, 1, 1)
    end = ee.Date.fromYMD(year, 12, 31)

    collection = (
        ee.ImageCollection("LANDSAT/LC08/C02/T1_L2")
        .filterDate(start, end)
        .filterBounds(roi)
        .filter(ee.Filter.lt("CLOUD_COVER", 60))
    )

    composite = collection.median()
    ndvi = composite.normalizedDifference(["SR_B5", "SR_B4"]).rename("NDVI")
    return ndvi


def compute_mean_ndvi(ndvi_image: ee.Image, roi: ee.Geometry):
    """
    Reduce NDVI image over ROI to get a mean NDVI value.
    """
    stats = ndvi_image.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=roi,
        scale=30,
        maxPixels=1e13,
    )
    value = stats.get("NDVI")

    if value is None:
        return None

    try:
        return float(value.getInfo())
    except Exception:
        return None


def compute_ndvi_series(roi: ee.Geometry, start_year: int = 2014, end_year: int = 2024):
    """
    Compute mean NDVI for each year in [start_year, end_year] over the same ROI.
    """
    years = list(range(start_year, end_year + 1))
    values = []
    for y in years:
        try:
            ndvi_img = get_ndvi_image(y, roi)
            mean_v = compute_mean_ndvi(ndvi_img, roi)
        except Exception:
            mean_v = None
        values.append(mean_v)
    return years, values


def create_timelapse_gif(roi: ee.Geometry, out_gif: str = "terrtime_timelapse.gif"):
    """
    Create a 2014–2024 Landsat timelapse GIF for the ROI.

    Uses geemap.create_timelapse (your version doesn't like fps).
    """
    try:
        collection = (
            ee.ImageCollection("LANDSAT/LC08/C02/T1_L2")
            .filterDate("2014-01-01", "2024-12-31")
            .filterBounds(roi)
            .filter(ee.Filter.lt("CLOUD_COVER", 60))
        )

        geemap_core.create_timelapse(
            collection=collection,
            start_date="2014-01-01",
            end_date="2024-12-31",
            region=roi,
            bands=["SR_B4", "SR_B3", "SR_B2"],
            frequency="year",
            reducer="median",
            vis_params={
                "min": 5000,
                "max": 15000,
            },
            out_gif=out_gif,
        )

        if os.path.exists(out_gif):
            return out_gif
        return None
    except Exception as e:
        print("Timelapse error:", e)
        return None


def build_health_map(ndvi_2014: ee.Image, ndvi_2024: ee.Image, roi: ee.Geometry) -> ee.Image:
    """
    Health Map:
        - Red = NDVI decrease (vegetation loss)
        - Green = NDVI increase (vegetation gain)
    Clipped to ROI.
    """
    diff = ndvi_2024.subtract(ndvi_2014).rename("NDVI_diff").clip(roi)
    vis = {
        "min": -0.3,
        "max": 0.3,
        "palette": ["red", "white", "green"],
    }
    styled = diff.visualize(**vis)
    return styled


def get_true_color_year(year: int, roi: ee.Geometry) -> ee.Image:
    """
    Median Landsat 8 true-color composite for a given year over the ROI.
    """
    start = ee.Date.fromYMD(year, 1, 1)
    end = ee.Date.fromYMD(year, 12, 31)

    collection = (
        ee.ImageCollection("LANDSAT/LC08/C02/T1_L2")
        .filterDate(start, end)
        .filterBounds(roi)
        .filter(ee.Filter.lt("CLOUD_COVER", 60))
    )

    composite = collection.median().select(["SR_B4", "SR_B3", "SR_B2"]).clip(roi)
    return composite


# --------------------------
# Splash screen
# --------------------------
def splash_screen():
    """
    Splash screen:
    Centered title, subtitle, and button. No globe picture.
    """

    st.markdown("<br><br><br>", unsafe_allow_html=True)

    col_left, col_center, col_right = st.columns([1, 2, 1])

    with col_center:
        st.markdown(
            """
            <h1 style="text-align: center;
                       font-size: 2.8rem;
                       font-weight: 800;
                       margin-top: 1.5rem;
                       margin-bottom: 0.5rem;">
                TerraTime: The AI Earth Auditor
            </h1>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <p style="text-align: center;
                      font-size: 1.05rem;
                      opacity: 0.9;
                      margin-bottom: 1.5rem;">
                See how Earth has changed over the last decade.
            </p>
            """,
            unsafe_allow_html=True,
        )

        if st.button("✨ Choose your identity", use_container_width=True):
            st.session_state["stage"] = "persona"
            st.rerun()


# --------------------------
# Persona selection screen
# --------------------------
def persona_screen():
    # Bigger heading for "Who are you today?"
    st.markdown(
        """
        <h1 style="font-size: 2.4rem; font-weight: 800; margin-top: 1.5rem; margin-bottom: 0.3rem;">
            Who are you today?
        </h1>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        "Choose how deep you want to go with TerraTime. You can always go back and switch later."
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### 🧪 Scientist")
        st.write(
            "- Full NDVI statistics\n"
            "- NDVI time series chart\n"
            "- Health map overlays\n"
            "- Technical descriptions of data + methods"
        )
        if st.button("Use Scientist Mode"):
            st.session_state["persona"] = "scientist"
            st.session_state["stage"] = "app"
            st.rerun()

    with col2:
        st.markdown("### 🎓 Student")
        st.write(
            "- Clean controls\n"
            "- NDVI trend chart\n"
            "- Explanations tuned for learning"
        )
        if st.button("Use Student Mode"):
            st.session_state["persona"] = "student"
            st.session_state["stage"] = "app"
            st.rerun()

    with col3:
        st.markdown("### 🌱 Public")
        st.write(
            "- Simple interface\n"
            "- Straightforward green health score\n"
            "- Plain-language explanation"
        )
        if st.button("Use Public Mode"):
            st.session_state["persona"] = "public"
            st.session_state["stage"] = "app"
            st.rerun()


# --------------------------
# Sidebar per persona (ONLY type location now)
# --------------------------
def render_sidebar(persona: str):
    with st.sidebar:
        st.title("TerraTime")
        st.markdown(f"**Mode:** `{persona.capitalize()}`")

        if st.button("← Change identity"):
            st.session_state["stage"] = "persona"
            st.rerun()

        if persona == "scientist":
            st.caption("Scientist mode: full detail, extra charts, technical copy.")
        elif persona == "student":
            st.caption("Student mode: you see the core metrics plus a trend chart.")
        else:
            st.caption("Public mode: simple wording, but real controls.")

        # Only "Type location" – drop-pin removed
        search_query = st.text_input(
            "Location",
            value="",
            key="location_input",
            placeholder="Type a city, address, or landmark…",
            help="Type at least 3 characters to get suggestions.",
        )

        suggestions = []
        suggestion_labels = []
        if search_query.strip() and len(search_query.strip()) >= 3:
            suggestions = get_osm_suggestions(search_query.strip())
            suggestion_labels = [s.address for s in suggestions]

        selected_label = None
        if suggestion_labels:
            options = ["Use exactly what I typed"] + suggestion_labels
            choice = st.radio(
                "Suggestions",
                options=options,
                index=0,
                help="Pick a match, or keep the first option to use your own text.",
            )
            if choice != "Use exactly what I typed":
                selected_label = choice

        address = search_query if selected_label is None else selected_label

        # Persona-specific sliders
        year_preview = None

        if persona == "scientist":
            buffer_km = st.slider(
                "Analysis radius (km)",
                min_value=1,
                max_value=50,
                value=10,
                help="Larger radius = more area and more pixels in the analysis.",
            )
            show_health = st.checkbox(
                "Show Vegetation Health Map overlay",
                value=True,
                help="Red = vegetation loss, Green = vegetation gain (2014 ➜ 2024).",
            )
            year_option = st.selectbox(
                "Optional: Focus map on a specific year",
                options=["(Auto context 2014–2024)"] + [str(y) for y in range(2014, 2025)],
                help="Adds an extra true-color layer for that year only.",
            )
            if year_option != "(Auto context 2014–2024)":
                year_preview = int(year_option)

        elif persona == "student":
            buffer_km = st.slider(
                "Analysis radius (km)",
                min_value=1,
                max_value=20,
                value=5,
                help="How far around your location we should analyze vegetation.",
            )
            show_health = st.checkbox(
                "Show Health Map overlay",
                value=True,
                help="Color overlay that highlights vegetation loss/gain.",
            )
            year_option = st.selectbox(
                "Optional: Year snapshot",
                options=["(No specific year)"] + [str(y) for y in range(2014, 2025)],
                help="Just visual; does not change the 2014 vs 2024 comparison.",
            )
            if year_option != "(No specific year)":
                year_preview = int(year_option)

        else:  # public
            buffer_km = st.slider(
                "Analysis radius (km)",
                min_value=1,
                max_value=20,
                value=5,
                help="How big an area around your location we should check.",
            )
            show_health = st.checkbox(
                "Show Health Map overlay",
                value=True,
                help="Color overlay that highlights vegetation loss/gain.",
            )
            year_option = st.selectbox(
                "Optional: View a specific year's satellite image",
                options=["(No specific year)"] + [str(y) for y in range(2014, 2025)],
                help="Just for visualization. Does not affect the main 2014–2024 comparison.",
            )
            if year_option != "(No specific year)":
                year_preview = int(year_option)

        run_audit = st.button("Run Audit")

    return address, buffer_km, show_health, year_preview, run_audit


# --------------------------
# Report rendering (per persona)
# --------------------------
def render_report(
    persona: str,
    address: str,
    buffer_km: float,
    mean_ndvi_2014: float,
    mean_ndvi_2024: float,
    green_score_2014: float,
    green_score_2024: float,
    pct_change: float,
    gif_path: str | None,
    ndvi_years,
    ndvi_values,
):
    st.subheader("Audit Report")

    st.metric("Green Score (2014)", f"{green_score_2014:.1f} / 100")
    st.metric("Green Score (2024)", f"{green_score_2024:.1f} / 100")

    if pct_change < 0:
        change_label = f"{abs(pct_change):.1f}% Vegetation Loss"
    elif pct_change > 0:
        change_label = f"{pct_change:.1f}% Vegetation Gain"
    else:
        change_label = "No significant change"

    st.metric("Vegetation Change (2014 ➜ 2024)", change_label)

    st.markdown("---")

    if persona == "public":
        st.markdown(
            f"""
### What this means

- **Place:** `{address}`
- **Area checked:** About **{buffer_km} km radius** around it.
- **Green Score change:** {change_label}

Higher scores = more healthy vegetation (trees, crops, green cover).  
Lower scores = more concrete, bare soil, or degraded land.
"""
        )
    elif persona == "student":
        st.markdown("### Interpretation (Student mode)")
        st.markdown(
            f"""
- **Location:** `{address}`  
- **Analysis Radius:** ~{buffer_km} km  
- **Mean NDVI 2014:** `{mean_ndvi_2014:.3f}`  
- **Mean NDVI 2024:** `{mean_ndvi_2024:.3f}`  
- **Change (NDVI units):** `{mean_ndvi_2024 - mean_ndvi_2014:.3f}`  

**How to read this:**

- NDVI ranges from **-1 to 1**. Values closer to **1** mean denser, healthy vegetation.
- We compare NDVI in **2014** and **2024** for the exact same area.
- We turn NDVI into a **Green Score (0–100)** so it's easy to compare.
- The **Health Map overlay** shows where vegetation decreased or increased over 10 years.
"""
        )
    else:  # scientist
        st.markdown("### Technical summary (Scientist mode)")
        st.markdown(
            f"""
- **Location:** `{address}`  
- **Analysis Radius:** ~{buffer_km} km  
- **Dataset:** `LANDSAT/LC08/C02/T1_L2` (Surface Reflectance, Collection 2 Level 2)  
- **Derived index:** NDVI = (NIR − RED) / (NIR + RED), bands = `SR_B5` (NIR), `SR_B4` (RED)  
- **Mean NDVI 2014:** `{mean_ndvi_2014:.3f}`  
- **Mean NDVI 2024:** `{mean_ndvi_2024:.3f}`  
- **Δ NDVI (2024 − 2014):** `{mean_ndvi_2024 - mean_ndvi_2014:.3f}`  
- **Relative change:** `{pct_change:.1f}%` (w.r.t. |NDVI 2014|)

**Notes:**

- Clouds are filtered using `CLOUD_COVER < 60` and median compositing at 30 m.
- Green Score is an affine transform of NDVI: `(NDVI + 1) / 2 * 100`.
- Timelapse frames use yearly median composites with the same collection.
"""
        )

    if persona in ("scientist", "student") and ndvi_years and any(v is not None for v in ndvi_values):
        st.markdown("---")
        st.subheader("NDVI trend (2014–2024)")

        chart_data = {
            "year": ndvi_years,
            "mean_ndvi": [v if v is not None else None for v in ndvi_values],
        }

        st.line_chart(
            data=chart_data,
            x="year",
            y="mean_ndvi",
        )

    st.markdown("---")
    st.subheader("10-Year Satellite Timelapse (2014–2024)")

    if gif_path and os.path.exists(gif_path):
        with open(gif_path, "rb") as f:
            gif_bytes = f.read()

        if st.button("▶ View Timelapse GIF"):
            st.image(
                gif_bytes,
                caption="Landsat Timelapse – TerraTime Audit Window (2014–2024)",
                use_column_width=True,
            )

        st.download_button(
            label="⬇ Download Timelapse GIF",
            data=gif_bytes,
            file_name="terrtime_2014_2024_timelapse.gif",
            mime="image/gif",
        )
    else:
        st.warning(
            "Timelapse could not be generated for this location "
            "(no imagery or server error). The rest of the audit still uses "
            "valid satellite statistics."
        )


# --------------------------
# Main app (persona = scientist/student/public)
# --------------------------
def app_screen(persona: str):
    initialize_earth_engine()

    address, buffer_km, show_health, year_preview, run_audit = render_sidebar(persona)

    st.title("🌍 TerraTime: The AI Earth Auditor")
    if persona == "scientist":
        st.caption("Scientist mode – full controls, technical detail, and time series.")
    elif persona == "student":
        st.caption("Student mode – balanced controls, clear explanations, and NDVI trend.")
    else:
        st.caption("Public mode – simple wording, serious data.")

    if not run_audit:
        st.info("Set your location and settings on the left, then click **Run Audit**.")
        return

    with st.spinner("Running TerraTime audit..."):
        if not address or not address.strip():
            st.error("Please enter a valid location string.")
            return

        try:
            location = geocode_location(address)
        except Exception as e:
            st.error(f"Geocoding failed: {e}")
            return

        if location is None:
            st.error("Could not find that location. Try a more specific address or another place.")
            return

        lat = location.latitude
        lon = location.longitude

        roi = create_roi(lon, lat, buffer_km=buffer_km)

        try:
            ndvi_2014 = get_ndvi_image(2014, roi)
            ndvi_2024 = get_ndvi_image(2024, roi)

            mean_ndvi_2014 = compute_mean_ndvi(ndvi_2014, roi)
            mean_ndvi_2024 = compute_mean_ndvi(ndvi_2024, roi)
        except Exception as e:
            st.error(f"Error computing NDVI statistics from Earth Engine: {e}")
            return

        if (mean_ndvi_2014 is None) or (mean_ndvi_2024 is None):
            st.error(
                "Could not compute vegetation stats for this area. "
                "Try a slightly larger radius or a different location."
            )
            return

        green_score_2014 = (mean_ndvi_2014 + 1) / 2 * 100
        green_score_2024 = (mean_ndvi_2024 + 1) / 2 * 100

        if mean_ndvi_2014 != 0:
            ndvi_change = mean_ndvi_2024 - mean_ndvi_2014
            pct_change = (ndvi_change / abs(mean_ndvi_2014)) * 100
        else:
            pct_change = 0.0

        ndvi_years, ndvi_values = ([], [])
        if persona in ("scientist", "student"):
            ndvi_years, ndvi_values = compute_ndvi_series(roi, 2014, 2024)

        Map = geemap.Map(center=[lat, lon], zoom=10)
        Map.add_basemap("SATELLITE")

        try:
            tc_2024 = get_true_color_year(2024, roi)
            true_color_vis = {
                "bands": ["SR_B4", "SR_B3", "SR_B2"],
                "min": 5000,
                "max": 15000,
            }
            Map.addLayer(tc_2024, true_color_vis, "Landsat True Color (2024)", True)
        except Exception:
            pass

        if year_preview is not None and year_preview != 2024:
            try:
                tc_year = get_true_color_year(year_preview, roi)
                year_vis = {
                    "bands": ["SR_B4", "SR_B3", "SR_B2"],
                    "min": 5000,
                    "max": 15000,
                }
                Map.addLayer(
                    tc_year,
                    year_vis,
                    f"Landsat True Color ({year_preview})",
                    True,
                )
            except Exception:
                pass

        roi_style = {"color": "yellow", "fillColor": "#00000000", "weight": 1}
        Map.addLayer(roi, roi_style, "Analysis Area", True)

        if show_health:
            try:
                health_map = build_health_map(ndvi_2014, ndvi_2024, roi)
                Map.addLayer(
                    health_map,
                    {},
                    "Vegetation Health (Red = Loss, Green = Gain)",
                    True,
                    opacity=0.4,
                )
            except Exception:
                pass

        Map.centerObject(roi, 10)

        gif_path = create_timelapse_gif(roi, out_gif="terrtime_timelapse.gif")

    st.subheader("Map & Health Overlay")
    Map.to_streamlit(height=600)

    render_report(
        persona,
        address,
        buffer_km,
        mean_ndvi_2014,
        mean_ndvi_2024,
        green_score_2014,
        green_score_2024,
        pct_change,
        gif_path,
        ndvi_years,
        ndvi_values,
    )


# --------------------------
# Main entry
# --------------------------
def main():
    st.set_page_config(
        page_title="TerraTime: The AI Earth Auditor",
        layout="wide",
    )

    apply_wallpaper()

    if "stage" not in st.session_state:
        st.session_state["stage"] = "splash"

    stage = st.session_state["stage"]
    persona = st.session_state.get("persona", None)

    if stage == "splash":
        splash_screen()
    elif stage == "persona":
        persona_screen()
    else:
        if not persona:
            st.session_state["stage"] = "persona"
            st.rerun()
        app_screen(persona)


if __name__ == "__main__":
    main()
