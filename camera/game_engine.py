import pygame
import sys
from threading import Thread
from queue import Queue
from camera_record import update_hand_gesture

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Jumping Rectangle")
clock = pygame.time.Clock()

# Rectangle variables
rect_x = WIDTH // 2
rect_y = HEIGHT - 150
rect_width = 50
rect_height = 50
rect_color = (255, 0, 0)  # Red color

# Jump variables
gravity = 1
jump_speed = -20
velocity_y = 0
ground_y = HEIGHT - 150
jumping = False

# Queue for gesture updates
gesture_queue = Queue()

def jump():
    global velocity_y, jumping
    if not jumping:  # Only jump if not already jumping
        velocity_y = jump_speed
        jumping = True

def process_jump():
    global rect_y, velocity_y, jumping
    # If we are jumping, apply velocity and gravity
    if jumping:
        rect_y += velocity_y
        velocity_y += gravity

        # If we've landed back on the ground, reset
        if rect_y > ground_y:
            rect_y = ground_y
            jumping = False

# Start the hand gesture detection thread
hand_thread = Thread(target=update_hand_gesture, args=(gesture_queue,), daemon=True)
hand_thread.start()

# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Check the gesture queue for the left hand raised signal
    try:
        while not gesture_queue.empty():  # Process all available signals
            left_hand_raised = gesture_queue.get_nowait()
            if left_hand_raised:
                jump()
    except queue.Empty:
        pass  # No more signals to process

    # Process jump physics
    process_jump()

    # Fill the screen with white
    screen.fill((255, 255, 255))

    # Draw the rectangle
    pygame.draw.rect(screen, rect_color, (rect_x, rect_y, rect_width, rect_height))

    # Update the display
    pygame.display.update()

    # Tick the clock
    clock.tick(60)

# Clean up
pygame.quit()
sys.exit()
