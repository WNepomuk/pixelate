import streamlit as st
from util.image import enhance_image

def render_modify_sliders():
    st.slider("Saturation", key="saturation_slider", min_value=0.0, max_value=4.0, step=0.1, on_change=enhance_image)
    st.slider("Contrast", key="contrast_slider", min_value=0.0, max_value=4.0, step=0.1, on_change=enhance_image)
    st.slider("Brightness", key="brightness_slider", min_value=0.0, max_value=4.0, step=0.1, on_change=enhance_image)
    st.slider("Sharpness", key="sharpness_slider", min_value=0.0, max_value=4.0, step=0.1, on_change=enhance_image)
    st.slider("Red", key="red_slider", min_value=-255, max_value=255, on_change=enhance_image)
    st.slider("Green", key="green_slider", min_value=-255, max_value=255, on_change=enhance_image)
    st.slider("Blue", key="blue_slider", min_value=-255, max_value=255, on_change=enhance_image)