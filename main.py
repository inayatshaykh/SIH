# main.py
import pygame
import random
import os
import json

from simulation.vehicle import Vehicle
from simulation.traffic_light import TrafficLight
from ai.traffic_predictor import TrafficPredictor
from simulation.config import WIDTH, HEIGHT, FPS, LANE_WIDTH, STOP_OFFSET
from simulation.dashboard import Dashboard
from simulation.intersection import IntersectionManager

def create_lights():
    lights = []
    cx, cy = WIDTH // 2, HEIGHT // 2
    
    def get_pos(direction, lane):
        offset = (LANE_WIDTH * 0.5) if lane == 1 else (LANE_WIDTH * 1.5)
        if direction == "N": return (cx + offset, cy - STOP_OFFSET + 15)
        if direction == "S": return (cx - offset, cy + STOP_OFFSET - 15)
        if direction == "E": return (cx + STOP_OFFSET - 15, cy - offset)
        if direction == "W": return (cx - STOP_OFFSET + 15, cy + offset)

    for direction in ["N", "S", "E", "W"]:
        for lane in [1, 2]:
            x, y = get_pos(direction, lane)
            lights.append(TrafficLight(x, y, direction, lane))
            
    return lights

def draw_road(screen):
    center_x, center_y = WIDTH // 2, HEIGHT // 2
    road_color = (60, 60, 60)
    road_width = LANE_WIDTH * 4

    pygame.draw.rect(screen, road_color, (0, center_y - road_width//2, WIDTH, road_width))
    pygame.draw.rect(screen, road_color, (center_x - road_width//2, 0, road_width, HEIGHT))
    pygame.draw.line(screen, (255, 255, 0), (center_x, 0), (center_x, HEIGHT), 3)
    pygame.draw.line(screen, (255, 255, 0), (0, center_y), (WIDTH, center_y), 3)
    dash_color = (200, 200, 200)
    dash_length, gap = 20, 15
    for y in range(0, HEIGHT, dash_length + gap):
        pygame.draw.line(screen, dash_color, (center_x - LANE_WIDTH, y), (center_x - LANE_WIDTH, y + dash_length), 1)
        pygame.draw.line(screen, dash_color, (center_x + LANE_WIDTH, y), (center_x + LANE_WIDTH, y + dash_length), 1)
    for x in range(0, WIDTH, dash_length + gap):
        pygame.draw.line(screen, dash_color, (x, center_y - LANE_WIDTH), (x + dash_length, center_y - LANE_WIDTH), 1)
        pygame.draw.line(screen, dash_color, (x, center_y + LANE_WIDTH), (x + dash_length, center_y + LANE_WIDTH), 1)
    
    font = pygame.font.SysFont("Arial", 40, bold=True)
    text_color = (220, 220, 220)
    n_text = font.render("N", True, text_color)
    screen.blit(n_text, (center_x - LANE_WIDTH * 1.8, center_y + STOP_OFFSET + 5))
    s_text = font.render("S", True, text_color)
    screen.blit(s_text, (center_x + LANE_WIDTH * 0.8, center_y - STOP_OFFSET - s_text.get_height()))
    w_text = font.render("W", True, text_color)
    screen.blit(w_text, (center_x + STOP_OFFSET + 5, center_y - LANE_WIDTH * 1.8))
    e_text = font.render("E", True, text_color)
    screen.blit(e_text, (center_x - STOP_OFFSET - e_text.get_width() - 5, center_y + LANE_WIDTH * 0.8))

def main_loop():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Smart Traffic Management System")
    clock = pygame.time.Clock()

    vehicles = []
    lights = create_lights()
    predictor = TrafficPredictor(name="Intersection-1")
    predictor.train()
    dashboard = Dashboard(WIDTH, HEIGHT)
    intersection_manager = IntersectionManager(lights)

    running = True
    spawn_timer = 0.0
    is_smart_mode = True
    
    print("--- Simulation starting ---") # DEBUG PRINT 1

    while running:
        # Check if the main loop is running ---
        print("New frame started...")

        dt = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    d = random.choice(["N", "S", "E", "W"])
                    vehicles.append(Vehicle(d, vehicles, is_emergency=True))
                if event.key == pygame.K_m:
                    is_smart_mode = not is_smart_mode

        spawn_cooldown = 0.8 if is_smart_mode else 0.4
        spawn_timer += dt
        if spawn_timer > spawn_cooldown:
            rush_hour_directions = ["N", "N", "N", "S", "S", "S", "E", "W"]
            d = random.choice(rush_hour_directions)
            vehicles.append(Vehicle(d, vehicles))
            spawn_timer = 0

        intersection_manager.update(dt, vehicles, is_smart_mode)
        
        #  Check if the logic before drawing is complete ---
        print("Updating vehicle movements...")
        for v in list(vehicles):
            v.move(lights, vehicles)
            if v.x < -200 or v.x > WIDTH + 200 or v.y < -200 or v.y > HEIGHT + 200:
                vehicles.remove(v)

        predictor.current_green_duration = intersection_manager.green_duration

        # Check if the program reaches the drawing step ---
        print("Drawing all elements...")
        screen.fill((18, 18, 18))
        draw_road(screen)
        
        for l in lights:
            l.draw(screen)
        for v in vehicles:
            v.draw(screen)
            
        dashboard.draw(screen, vehicles, lights, predictor, is_smart_mode)

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main_loop()