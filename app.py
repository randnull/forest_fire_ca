import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import io

from wui_from_osm import load_wui_from_osm
from model.main import WUIModel
from models import WeatherType, ForestState

st.set_page_config(page_title="Forest Fire Simulation", layout="wide")

st.title("Forest Fire Simulation")
st.markdown("Simulate forest fire spread with buildings from OpenStreetMap")

col1, col2 = st.columns([1, 1])

with col1:
    st.header("Parameters")
    
    locations = [
        "Troitsky Administrative Okrug, Moscow, Russia",
        "Zelenograd Administrative Okrug, Moscow, Russia",
        "Novomoskovsky Administrative Okrug, Moscow, Russia",
        "Krasnogorsk, Moscow Oblast, Russia",
        "Khimki, Moscow Oblast, Russia",
        "Mytishchi, Moscow Oblast, Russia",
        "Balashikha, Moscow Oblast, Russia",
        "Podolsk, Moscow Oblast, Russia",
        "Korolev, Moscow Oblast, Russia",
        "Lyubertsy, Moscow Oblast, Russia",
        "Mati, Attica, Greece",
        "Rafina, Attica, Greece",
        "Marathon, Attica, Greece",
        "Loutraki, Corinthia, Greece",
        "Nafplio, Argolis, Greece",
        "Chalkida, Euboea, Greece",
        "Kalamata, Messenia, Greece",
        "Sparta, Laconia, Greece",
        "Kavala, Macedonia, Greece",
        "Alexandroupoli, Thrace, Greece",
        "Ashland, Oregon, USA",
        "Medford, Oregon, USA",
        "Bend, Oregon, USA",
        "Eugene, Oregon, USA",
        "Corvallis, Oregon, USA",
        "Grants Pass, Oregon, USA",
        "Roseburg, Oregon, USA",
        "Klamath Falls, Oregon, USA",
        "La Grande, Oregon, USA",
        "Ontario, Oregon, USA",
        "Flagstaff, Arizona, USA",
        "Sedona, Arizona, USA",
        "Prescott, Arizona, USA",
        "Tucson, Arizona, USA",
        "Bisbee, Arizona, USA",
        "Sierra Vista, Arizona, USA",
        "Yuma, Arizona, USA",
        "Lake Havasu City, Arizona, USA",
        "Kingman, Arizona, USA",
        "Bullhead City, Arizona, USA",
        "Boulder, Colorado, USA",
        "Fort Collins, Colorado, USA",
        "Colorado Springs, Colorado, USA",
        "Pueblo, Colorado, USA",
        "Grand Junction, Colorado, USA",
        "Durango, Colorado, USA",
        "Aspen, Colorado, USA",
        "Steamboat Springs, Colorado, USA",
        "Greeley, Colorado, USA",
        "Loveland, Colorado, USA",
        "Santa Fe, New Mexico, USA",
        "Taos, New Mexico, USA",
        "Las Cruces, New Mexico, USA",
        "Albuquerque, New Mexico, USA",
        "Roswell, New Mexico, USA",
        "Farmington, New Mexico, USA",
        "Carlsbad, New Mexico, USA",
        "Hobbs, New Mexico, USA",
        "Clovis, New Mexico, USA",
        "Alamogordo, New Mexico, USA",
        "Missoula, Montana, USA",
        "Bozeman, Montana, USA",
        "Billings, Montana, USA",
        "Great Falls, Montana, USA",
        "Butte, Montana, USA",
        "Helena, Montana, USA",
        "Kalispell, Montana, USA",
        "Havre, Montana, USA",
        "Miles City, Montana, USA",
        "Livingston, Montana, USA",
        "Spokane, Washington, USA",
        "Yakima, Washington, USA",
        "Wenatchee, Washington, USA",
        "Bellingham, Washington, USA",
        "Olympia, Washington, USA",
        "Tacoma, Washington, USA",
        "Everett, Washington, USA",
        "Bremerton, Washington, USA",
        "Richland, Washington, USA",
        "Pullman, Washington, USA",
        "Annecy, Haute-Savoie, France",
        "Chamonix-Mont-Blanc, France",
        "Grenoble, Isère, France",
        "Avignon, Vaucluse, France",
        "Aix-en-Provence, France",
        "Cannes, Alpes-Maritimes, France",
        "Nice, Alpes-Maritimes, France",
        "Toulon, Var, France",
        "Perpignan, Pyrénées-Orientales, France",
        "Biarritz, Pyrénées-Atlantiques, France",
        "Inverness, Scotland, United Kingdom",
        "Aberdeen, Scotland, United Kingdom",
        "Stirling, Scotland, United Kingdom",
        "Dundee, Scotland, United Kingdom",
        "Perth, Scotland, United Kingdom",
        "Bath, Somerset, United Kingdom",
        "Canterbury, Kent, United Kingdom",
        "York, North Yorkshire, United Kingdom",
        "Cambridge, Cambridgeshire, United Kingdom",
        "Oxford, Oxfordshire, United Kingdom",
        "Freiburg im Breisgau, Germany",
        "Heidelberg, Baden-Württemberg, Germany",
        "Tübingen, Baden-Württemberg, Germany",
        "Konstanz, Baden-Württemberg, Germany",
        "Garmisch-Partenkirchen, Bavaria, Germany",
        "Berchtesgaden, Bavaria, Germany",
        "Bamberg, Bavaria, Germany",
        "Regensburg, Bavaria, Germany",
        "Würzburg, Bavaria, Germany",
        "Passau, Bavaria, Germany",
        "San Sebastian, Basque Country, Spain",
        "Bilbao, Basque Country, Spain",
        "Santander, Cantabria, Spain",
        "Oviedo, Asturias, Spain",
        "Santiago de Compostela, Galicia, Spain",
        "Córdoba, Andalusia, Spain",
        "Granada, Andalusia, Spain",
        "Málaga, Andalusia, Spain",
        "Seville, Andalusia, Spain",
        "Cádiz, Andalusia, Spain",
        "Siena, Tuscany, Italy",
        "Pisa, Tuscany, Italy",
        "Lucca, Tuscany, Italy",
        "Arezzo, Tuscany, Italy",
        "Perugia, Umbria, Italy",
        "Assisi, Umbria, Italy",
        "Orvieto, Umbria, Italy",
        "Bologna, Emilia-Romagna, Italy",
        "Modena, Emilia-Romagna, Italy",
        "Parma, Emilia-Romagna, Italy",
        "Hakone, Kanagawa, Japan",
        "Kamakura, Kanagawa, Japan",
        "Nikko, Tochigi, Japan",
        "Takayama, Gifu, Japan",
        "Kanazawa, Ishikawa, Japan",
        "Matsumoto, Nagano, Japan",
        "Nagano, Nagano, Japan",
        "Kobe, Hyogo, Japan",
        "Nara, Nara, Japan",
        "Wakayama, Wakayama, Japan",
        "Geelong, Victoria, Australia",
        "Ballarat, Victoria, Australia",
        "Bendigo, Victoria, Australia",
        "Warrnambool, Victoria, Australia",
        "Toowoomba, Queensland, Australia",
        "Cairns, Queensland, Australia",
        "Townsville, Queensland, Australia",
        "Rockhampton, Queensland, Australia",
        "Bundaberg, Queensland, Australia",
        "Mackay, Queensland, Australia",
        "Kelowna, British Columbia, Canada",
        "Victoria, British Columbia, Canada",
        "Nanaimo, British Columbia, Canada",
        "Kamloops, British Columbia, Canada",
        "Prince George, British Columbia, Canada",
        "Red Deer, Alberta, Canada",
        "Lethbridge, Alberta, Canada",
        "Medicine Hat, Alberta, Canada",
        "Brandon, Manitoba, Canada",
        "Thunder Bay, Ontario, Canada",
    ]
    
    selected_location = st.selectbox(
        "Location",
        options=locations,
        index=0,
        help="Select a location from the list or enter custom location below"
    )
    
    custom_location = st.text_input(
        "Or enter custom location (OSM query)",
        value="",
        help="Enter a custom location query for OpenStreetMap"
    )
    
    place = custom_location if custom_location else selected_location
    
    cell_length = st.slider(
        "Cell size (meters)",
        min_value=10.0,
        max_value=50.0,
        value=30.0,
        step=5.0
    )
    
    temperature = st.slider(
        "Temperature (°C)",
        min_value=10.0,
        max_value=50.0,
        value=30.0,
        step=1.0
    )
    
    wind_speed = st.slider(
        "Wind speed (m/s)",
        min_value=0.0,
        max_value=30.0,
        value=15.0,
        step=0.5
    )
    
    wind_direction = st.slider(
        "Wind direction (degrees)",
        min_value=0.0,
        max_value=360.0,
        value=130.0,
        step=5.0
    )
    
    relative_humidity = st.slider(
        "Relative humidity (%)",
        min_value=0.0,
        max_value=100.0,
        value=20.0,
        step=1.0
    )
    
    weather_type = st.selectbox(
        "Weather type",
        options=["ADVANTAGE", "NEUTRAL", "DISADVANTAGE"],
        index=1,
        format_func=lambda x: x.capitalize()
    )
    
    total_minutes = st.number_input(
        "Simulation time (minutes)",
        min_value=100,
        max_value=10000,
        value=1000,
        step=100
    )
    
    auto_ignition = st.checkbox("Auto ignition point (center)", value=True)
    
    if not auto_ignition:
        ignition_y = st.number_input(
            "Ignition point Y",
            min_value=0,
            value=0,
            step=1
        )
        
        ignition_x = st.number_input(
            "Ignition point X",
            min_value=0,
            value=0,
            step=1
        )
    else:
        ignition_y = None
        ignition_x = None

with col2:
    st.header("Simulation")
    
    if st.button("Run Simulation", type="primary"):
        with st.spinner("Loading data from OSM..."):
            try:
                H, W, forest_mask, incomb_mask, houses = load_wui_from_osm(place=place, cell_length=cell_length)
                
                st.success(f"Loaded {len(houses)} buildings from OSM")
                st.info(f"Grid size: {H} x {W} cells")
                
                if auto_ignition:
                    ignition_y = H // 2
                    ignition_x = W // 2
                    st.info(f"Using center point: ({ignition_y}, {ignition_x})")
                else:
                    if ignition_y >= H or ignition_x >= W:
                        st.error(f"Ignition point ({ignition_y}, {ignition_x}) is outside grid bounds ({H}, {W})")
                        st.stop()
                
                weather_map = {
                    "ADVANTAGE": WeatherType.ADVANTAGE,
                    "NEUTRAL": WeatherType.NEUTRAL,
                    "DISADVANTAGE": WeatherType.DISADVANTAGE
                }
                
                model = WUIModel(
                    height=H,
                    width=W,
                    forest_mask=forest_mask,
                    incombustible_mask=incomb_mask,
                    houses=houses,
                    temperature=temperature,
                    wind_speed=wind_speed,
                    relative_humidity=relative_humidity,
                    cell_length=cell_length,
                    wind_direction=wind_direction,
                    weather_type=weather_map[weather_type]
                )
                
                model.ignite_forest((ignition_y, ignition_x))
                
                with st.spinner("Running simulation..."):
                    saves = model.run(total_minutes=total_minutes)
                
                st.success(f"Simulation completed! {len(saves)} time steps")
                
                st.subheader("Results")
                
                map_fire_by_time = np.full((H, W), np.inf, dtype=np.float32)
                
                for t, forest_state, _ in saves:
                    next_fire = (forest_state >= ForestState.SF2) & np.isinf(map_fire_by_time)
                    map_fire_by_time[next_fire] = t
                
                for h in houses:
                    for (y, x) in h.cells:
                        if 0 <= y < H and 0 <= x < W:
                            map_fire_by_time[y, x] = None
                
                fig, ax = plt.subplots(figsize=(12, 10))
                
                Z = np.full((H, W), np.nan, dtype=float)
                bins = [0, 10, 15, 20, 25, 50, 60, 70, 80, 100, 200, 500, 700, 800, 1500, 2500]
                
                for y in range(H):
                    for x in range(W):
                        if np.isnan(map_fire_by_time[y, x]):
                            continue
                        if np.isinf(map_fire_by_time[y, x]):
                            Z[y, x] = len(bins) - 1
                        else:
                            for i in range(len(bins) - 1):
                                if bins[i] <= map_fire_by_time[y, x] < bins[i+1]:
                                    Z[y, x] = i
                                    break
                
                X, Y = np.meshgrid(np.arange(W+1), np.arange(H+1))
                cmap = plt.cm.Reds_r
                cmap.set_bad(color='gray', alpha=0.5)
                im = ax.pcolormesh(X, Y, Z, shading='auto', cmap=cmap, vmin=0, vmax=len(bins)-1)
                
                for h in houses:
                    for (y, x) in set(h.cells):
                        if 0 <= y < H and 0 <= x < W:
                            rect = patches.Rectangle(
                                (x, y),
                                1, 1,
                                fill=True,
                                edgecolor="black",
                                linewidth=0.3,
                                facecolor="darkgray",
                                alpha=0.6
                            )
                            ax.add_patch(rect)
                
                ax.plot([ignition_x], [ignition_y], marker='^', markersize=15, color='yellow', markeredgecolor='black', markeredgewidth=2, label='Ignition point')
                
                cbar = plt.colorbar(im, ax=ax)
                cbar.set_label('Time (min) until active fire', fontsize=12)
                tick_pos = list(range(len(bins) - 1))
                tick_lbl = [str(b) for b in bins[:-1]]
                cbar.set_ticks(tick_pos)
                cbar.set_ticklabels(tick_lbl)
                
                ax.set_xlabel('X (cells)', fontsize=12)
                ax.set_ylabel('Y (cells)', fontsize=12)
                ax.set_title('Fire Spread Map', fontsize=14, fontweight='bold')
                ax.legend(loc='upper right')
                ax.set_aspect('equal')
                
                plt.tight_layout()
                
                st.pyplot(fig)
                
                buf = io.BytesIO()
                plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
                buf.seek(0)
                st.download_button(
                    label="Download visualization",
                    data=buf,
                    file_name=f"fire_simulation_{place.replace(' ', '_')}.png",
                    mime="image/png"
                )
                plt.close(fig)
                
                burned_area = np.sum(map_fire_by_time < np.inf)
                total_forest = np.sum(forest_mask)
                burned_percentage = (burned_area / total_forest * 100) if total_forest > 0 else 0
                
                col_stat1, col_stat2, col_stat3 = st.columns(3)
                with col_stat1:
                    st.metric("Burned area", f"{burned_area} cells")
                with col_stat2:
                    st.metric("Burned percentage", f"{burned_percentage:.1f}%")
                with col_stat3:
                    st.metric("Total buildings", len(houses))

            except Exception as e:
                st.error(f"Error: {str(e)}")
                st.exception(e)
