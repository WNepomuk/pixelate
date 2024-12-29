import streamlit as st
from PIL import Image
from util.image import reduce_colors, resize, resize_image_for_display
import io
from util.util import reset_sliders, initialize_session_state, set_palette, load_tooltip_texts, get_palette_from_image
from util.render import render_modify_sliders


st.set_page_config(
    page_title="Pixelate",
    layout="wide",
)

initialize_session_state()

tooltips = load_tooltip_texts()

st.title("Pixelate")
st.text("""This application lets you turn images into pixel art! 
        Just upload any image, select a palette and hit the pixelate button. 
        You can also control the color matching algorithm as well as the downsampling.
        Once you are happy with the result you can download the image.""")

st.divider()
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "png", "jpeg", "webp"], label_visibility="collapsed")
st.divider()

if uploaded_file is not None:

    # Show the uploaded image
    col1, col2, col3 = st.columns(3, border=True)
    with col1:
        image = Image.open(uploaded_file)
        st.text(f"Size: {image.width} x {image.height}")
        st.session_state.image = image
        st.image(image, caption="Uploaded Image", use_container_width=True)
        
        if st.button("Pixelate!", type="primary", use_container_width=True):
            if st.session_state.scale_image:
                resize()
            st.session_state.modified_image = reduce_colors(st.session_state.image, st.session_state.current_palette, method=st.session_state.mapping_method, scale_to_palette=st.session_state.scale_to_palette)
            st.session_state.modified_image_original = st.session_state.modified_image
        
        st.divider()
        col11, col12 = st.columns(2)
        with col11:
            st.button("Get Palette from Image", on_click=get_palette_from_image)
        with col12:
            st.number_input("Number of colors", min_value=2, max_value=50, key="nr_palette_colors", value=8, label_visibility="collapsed")
        st.toggle('Remove background', help="Careful, this can take a loooong time.")
    
    # Show the modified image
    if st.session_state.modified_image:
        with col2:
            st.text(f"Size: {st.session_state.modified_image.width} x {st.session_state.modified_image.height}")
            modified_display_image = resize_image_for_display(st.session_state.modified_image)
            st.image(modified_display_image, caption="Pixelated Image", use_container_width=True, output_format="PNG")
    
            img_byte_arr = io.BytesIO()
            st.session_state.modified_image.save(img_byte_arr, format="PNG")
            img_byte_arr.seek(0)  # Reset the stream to the beginning

            file_name = st.text_input("file name", value="pixelate", help="File name for the downloaded file.")
            st.download_button(label="Download Resized Image", data=img_byte_arr, file_name=f"{file_name}.png", mime="image/png")
    
        with col3:
            if "saturation_slider" not in st.session_state:
                reset_sliders()
            render_modify_sliders()
            st.button("Reset Sliders", on_click=reset_sliders)
    st.divider()

col1, col2 = st.columns([1,7])
with col1:
    st.subheader("Palette")
with col2:
    if st.session_state.current_palette:
        st.image(st.session_state.current_palette.image)
with st.expander('Select a palette'):
    for index, palette in enumerate(st.session_state.palettes):
        col1, col2 = st.columns([2,1])
        with col1:
            st.image(palette.image)
        with col2:
            st.button('Use', key=f"use_palette_{index}", on_click=set_palette, kwargs={"index": index})

st.divider()
with st.expander("Options"):
    st.subheader("Color Mapping")
    st.selectbox("Mapping method", ["nearest", "manhattan", "weighted", "hsv"], key="mapping_method")

    st.checkbox("Scale pixel colors to palette color space", help=tooltips["scale_to_palette"], key="scale_to_palette")
    
    st.divider()
    st.subheader("Image Scaling")
    scale_image = st.checkbox("Scale image", value=True, key="scale_image")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.number_input("width", step=1, value=128, key="target_width")
    with col2:
        st.number_input("height", step=1, value=128, key="target_height")
    with col3:
        st.radio("Keep ratio", [ "ignore ratio","keep ratio (set width)", "keep ratio (set height)"], label_visibility="collapsed", index=1, key="keep_ratio")
