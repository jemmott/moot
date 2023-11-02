import webcolors

# This is a totally silly function to be able to print the names of various colors


def closest_color(requested_color):
    min_colors = {}
    for key, name in webcolors.CSS3_HEX_TO_NAMES.items():
        r_c, g_c, b_c = webcolors.hex_to_rgb(key)
        rd = (r_c - requested_color[0]) ** 2
        gd = (g_c - requested_color[1]) ** 2
        bd = (b_c - requested_color[2]) ** 2
        min_colors[(rd + gd + bd)] = name
    return min_colors[min(min_colors.keys())]


def print_results(freq, rgb_tuple):
    color_name = closest_color(rgb_tuple)
    print(f"Frequency: {freq:.2f} Hz is color: {color_name}")