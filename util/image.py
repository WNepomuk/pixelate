from PIL import Image, ImageEnhance
import numpy as np
from util.palette import Palette
import io
from math import sqrt
from colorsys import rgb_to_hsv
import streamlit as st

class ImageStats:
    saturation = 1
    contrast = 1
    brightness = 1
    sharpness = 1
    r = 0
    g = 0
    b = 0


def adjust_channel(image, channel, adjustment):
    # Split the image into channels
    r, g, b = image.split()
    channels = {"r": r, "g": g, "b": b}

    # Apply adjustment to the specified channel
    channel_data = channels[channel].point(lambda i: max(0, min(255, i + adjustment)))

    # Replace the adjusted channel
    channels[channel] = channel_data

    # Recombine channels into an image
    return Image.merge("RGB", (channels["r"], channels["g"], channels["b"]))

def adjust_saturation(image: Image, value)->Image:
    enhancer = ImageEnhance.Color(image)
    return enhancer.enhance(value)

def enhance(image, image_stats: ImageStats):
    if image_stats.saturation is not None:
        enhancer = ImageEnhance.Color(image)
        image = enhancer.enhance(image_stats.saturation)
    if image_stats.contrast is not None:
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(image_stats.contrast)
    if image_stats.brightness is not None:
        enhancer = ImageEnhance.Brightness(image)
        image = enhancer.enhance(image_stats.brightness)

    if image_stats.sharpness is not  None:
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(image_stats.sharpness)
    
    if image_stats.r is not None:
        image = adjust_channel(image, "r", image_stats.r)
    
    if image_stats.g is not None:
        image = adjust_channel(image, "g", image_stats.g)
    
    if image_stats.b is not None:
        image = adjust_channel(image, "b", image_stats.b)
    
    return image

def scale_to_palette_bounds(value, old_min, old_max, new_min, new_max):
    """
    Scale a value from one range (old_min, old_max) to another (new_min, new_max) using the formula.
    """
    return (((value - old_min) * (new_max - new_min)) / (old_max - old_min)) + new_min

def rgb_to_hsv_np(rgb):
    rgb = np.array(rgb) / 255.0  # Normalize RGB to [0, 1]
    return np.array(rgb_to_hsv(rgb[0], rgb[1], rgb[2]))

def reduce_colors(image:Image, palette: Palette, method="nearest", scale_to_palette=True)->Image:
    """
    Reduce the number of colors in an image based on a provided palette.
    """

    # Load the image
    image_data = np.array(image)

    # Convert the palette to a numpy array for vectorized computation
    palette_array = np.array(palette.rgb_array)

    if scale_to_palette:
        image_min_vals = np.min(image_data, axis=(0, 1))
        image_max_vals = np.max(image_data, axis=(0, 1))
        palette_min_vals = np.min(palette_array, axis=0)
        palette_max_vals = np.max(palette_array, axis=0)

        # Now, for each pixel, scale the components based on the formula
        def scale_pixel_color(pixel):
            return [
                scale_to_palette_bounds(pixel[0], image_min_vals[0], image_max_vals[0], palette_min_vals[0], palette_max_vals[0]),
                scale_to_palette_bounds(pixel[1], image_min_vals[1], image_max_vals[1], palette_min_vals[1], palette_max_vals[1]),
                scale_to_palette_bounds(pixel[2], image_min_vals[2], image_max_vals[2], palette_min_vals[2], palette_max_vals[2])
            ]

        image_data = np.apply_along_axis(scale_pixel_color, axis=-1, arr=image_data)
                           
    # We use color[0:3] to exclude transparency values if there are any.
    def find_nearest_color(color):
        distances = np.sqrt(np.sum((palette_array - color[0:3]) ** 2, axis=1))
        return palette_array[np.argmin(distances)]

    def manhattan_distance(color):
        distances = np.sum(np.abs(palette_array - color[0:3]), axis=1)
        return palette_array[np.argmin(distances)]
    
    def weighted_eucledian(color, weights=(0.3, 0.59, 0.11)):
        weights_array = np.array(weights)
        distances = np.sqrt(np.sum(weights_array * (palette_array - color[0:3]) ** 2, axis=1))
        return palette_array[np.argmin(distances)]
    
    def hsv_distance(color):
        target_hsv = rgb_to_hsv_np(color[0:3])
        palette_hsv = np.array([rgb_to_hsv_np(rgb) for rgb in palette_array])
        hue_diff = np.abs(palette_hsv[:, 0] - target_hsv[0])
        hue_distance = np.minimum(hue_diff, 1 - hue_diff)
        
        distances = np.sqrt(
            (hue_distance ** 2) +
            ((palette_hsv[:, 1] - target_hsv[1]) ** 2) +
            ((palette_hsv[:, 2] - target_hsv[2]) ** 2)
        )

        return palette_array[np.argmin(distances)]
    
    if method == "manhattan":
        reduced_data = np.apply_along_axis(manhattan_distance, axis=-1, arr=image_data)
    elif method == "weighted":
        reduced_data = np.apply_along_axis(weighted_eucledian, axis=-1, arr=image_data)
    elif method == "hsv":
        reduced_data = np.apply_along_axis(hsv_distance, axis=-1, arr=image_data)
    else:
        reduced_data = np.apply_along_axis(find_nearest_color, axis=-1, arr=image_data)

    reduced_image = Image.fromarray(np.uint8(reduced_data))
    return reduced_image

def resize_image(image: Image.Image, target_width, target_height):
    # Resize the image to the target dimensions
    resized_image = image.resize((target_width, target_height), resample=Image.Resampling.NEAREST)
    return resized_image

def resize_image_for_display(image: Image.Image):
    width = 1024
    heigth = int((width/image.width) * image.height)
    return image.resize((width, heigth), resample=Image.Resampling.NEAREST)

def enhance_image():
    new_image_stats = ImageStats()
    
    if st.session_state.image_stats.saturation == st.session_state.saturation_slider:
        new_image_stats.saturation = None
    else:
        new_image_stats.saturation = st.session_state.saturation_slider
        st.session_state.image_stats.saturation = st.session_state.saturation_slider
    
    if st.session_state.image_stats.contrast == st.session_state.contrast_slider:
        new_image_stats.contrast = None
    else:
        new_image_stats.contrast = st.session_state.contrast_slider
        st.session_state.image_stats.contrast = st.session_state.contrast_slider
    
    if st.session_state.image_stats.brightness == st.session_state.brightness_slider:
        new_image_stats.brightness = None
    else:
        new_image_stats.brightness = st.session_state.brightness_slider
        st.session_state.image_stats.brightness = st.session_state.brightness_slider

    
    if st.session_state.image_stats.sharpness == st.session_state.sharpness_slider:
        new_image_stats.sharpness = None
    else:
        new_image_stats.sharpness = st.session_state.sharpness_slider
        st.session_state.image_stats.sharpness = st.session_state.sharpness_slider

    if st.session_state.image_stats.r == st.session_state.red_slider:
        new_image_stats.r = None
    else:
        new_image_stats.r = st.session_state.red_slider
        st.session_state.image_stats.r = st.session_state.red_slider
    
    if st.session_state.image_stats.g == st.session_state.green_slider:
        new_image_stats.g = None
    else:
        new_image_stats.g = st.session_state.green_slider
        st.session_state.image_stats.g = st.session_state.green_slider
    
    if st.session_state.image_stats.b == st.session_state.blue_slider:
        new_image_stats.b = None
    else:
        new_image_stats.b = st.session_state.blue_slider
        st.session_state.image_stats.b = st.session_state.blue_slider
    

    st.session_state.modified_image = enhance(st.session_state.modified_image_original, new_image_stats)

def resize():
    if st.session_state.keep_ratio == "keep ratio (set width)":
                width = st.session_state.target_width
                ratio = width/st.session_state.image.width
                heigth = ratio * st.session_state.image.height
    elif st.session_state.keep_ratio == "keep ratio (set height)":
        heigth = st.session_state.target_height
        ratio = heigth/st.session_state.image.height
        width = ratio * st.session_state.image.width
    else:
        width = st.session_state.target_width
        heigth = st.session_state.target_height
    st.session_state.image = resize_image(st.session_state.image, int(width), int(heigth))