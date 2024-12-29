import streamlit as st
import json
from util.image import enhance_image, ImageStats
from util.palette import load_palettes, Palette
from util.colorthief import ColorThief

def reset_sliders():
    with open("config.json") as config_file:
        config = json.load(config_file)
        slider_config = config["slider_defaults"]
        for slider, default in slider_config.items():
            st.session_state[slider] = default
    enhance_image()

def set_palette(index):
    st.session_state.current_palette = st.session_state.palettes[index]

def initialize_session_state():
    if "rembg" not in st.session_state:
        st.session_state.rembg = None

    if "modified_image" not in st.session_state:
        st.session_state.modified_image = None

    if "palettes" not in st.session_state:
        st.session_state.palettes = load_palettes()

    if "current_palette" not in st.session_state:
        set_palette(0)

    if "image_stats" not in st.session_state:
        st.session_state.image_stats = ImageStats()
    
    if "scale_image" not in st.session_state:
        st.session_state.scale_image = True

    if "mapping_method" not in st.session_state:
        st.session_state.mapping_method = "nearest"
    
    if "scale_to_palette" not in st.session_state:
        st.session_state.scale_to_palette = False

@st.cache_data
def load_tooltip_texts()->dict:
    with open('tooltips.json') as file:
        return json.load(file)
    
def get_palette_from_image():
    color_thief = ColorThief(st.session_state.image)
    palette = Palette(['%02x%02x%02x' % color for color in color_thief.get_palette(st.session_state.nr_palette_colors)])
    st.session_state.palettes.append(palette)
