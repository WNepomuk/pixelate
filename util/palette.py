from PIL import Image
import streamlit as st
import json

def hex_to_rgb(hex_color):
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

class Palette:
    def __init__(self, color_array):
        self.hex_array = color_array
        self.rgb_array = [hex_to_rgb(color) for color in self.hex_array]
        self.image = self.get_palette_image()

    def get_palette_image(self, square_size=32):
    
        """
        Create a PNG image where each color from the palette is represented as a square.

        :param palette: List of hex color strings.
        :param square_size: The size of each square (in pixels).
        :param output_path: Path to save the generated image.
        """
        
        # Image dimensions: width = number of colors * square_size, height = square_size
        image_width = len(self.rgb_array) * square_size
        image_height = square_size
        
        # Create a new image with the required size
        image = Image.new("RGB", (image_width, image_height))
        
        # Fill the image with the palette colors
        for i, color in enumerate(self.rgb_array):
            for x in range(i * square_size, (i + 1) * square_size):
                for y in range(square_size):
                    image.putpixel((x, y), color)
        
        # Save the image as PNG
        return image

@st.cache_data
def load_palettes() -> list[Palette]:
    with open('palettes.json', "r") as file:
        palette_list = json.load(file)
    return [Palette(color_list) for color_list in palette_list]