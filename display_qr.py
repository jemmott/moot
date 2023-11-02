import pygame
import numpy as np

# Display frequency as color in window - this will get replaced with the LED strip code
pygame.init()
screen_width = 600
screen_height = 600
win = pygame.display.set_mode((screen_width, screen_height))

qr_image = pygame.image.load('moot_qr.png').convert_alpha()
qr_image = pygame.transform.scale(qr_image, (screen_width, screen_height))


def run_display(color):
    # Convert the surfaces to arrays for fast numpy processing
    qr_array = pygame.surfarray.pixels3d(qr_image)
    win_array = pygame.surfarray.pixels3d(win)

    # Create a boolean mask where the QR pixels are black
    mask = np.all(qr_array == [0, 0, 0], axis=-1)

    # Apply the color to the window array using the mask
    win_array[mask] = color

    # Reflect changes from numpy array to pygame surface
    pygame.surfarray.blit_array(win, win_array)
    pygame.display.update()

