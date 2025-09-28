# simulation/dashboard.py
import pygame
import time

class Dashboard:
    HEIGHT = 140

    def __init__(self, width, height):
        self.width = width
        self.sim_height = height - self.HEIGHT
        if not pygame.font.get_init():
            pygame.font.init()
        self.font = pygame.font.SysFont("Arial", 18, bold=True)
        self.title_font = pygame.font.SysFont("Arial", 22, bold=True)
        self.last_flash = 0
        self.flash_on = True

    def draw_light_status(self, screen, light, x, y):
        color_map = {"green": (0, 200, 0), "yellow": (255, 255, 0), "red": (200, 0, 0)}
        color = color_map[light.state]
        time_str = f"({light.remaining_time}s)" if light.remaining_time > 0 else ""
        txt = f"{light.direction}: {light.state.upper()} {time_str}"
        surf = self.font.render(txt, True, color)
        screen.blit(surf, (x, y))

    # --- UPDATED: Draw method now accepts and displays the current mode ---
    def draw(self, screen, vehicles, lights, predictor, is_smart_mode):
        panel_y = self.sim_height
        pygame.draw.rect(screen, (30, 30, 30), (0, panel_y, self.width, self.HEIGHT))
        title = self.title_font.render("Simulation Dashboard", True, (240, 240, 240))
        screen.blit(title, (10, panel_y + 10))

        primary_lights = []
        for d in ["N", "S", "E", "W"]:
            light = next((l for l in lights if l.direction == d and l.lane == 1), None)
            if light:
                primary_lights.append(light)
        lx, ly = 20, panel_y + 50
        for i, light in enumerate(primary_lights):
            col = i // 2
            row = i % 2
            self.draw_light_status(screen, light, lx + col * 180, ly + row * 35)

        start_x = 400
        total_vehicles = len(vehicles)
        q_ns = sum(1 for v in vehicles if v.direction in ("N", "S") and v.speed == 0)
        q_ew = sum(1 for v in vehicles if v.direction in ("E", "W") and v.speed == 0)
        txt = self.font.render(f"Total Vehicles: {total_vehicles}", True, (230,230,230))
        screen.blit(txt, (start_x, panel_y + 40))
        q_txt = self.font.render(f"Queued N/S: {q_ns}", True, (230,230,230))
        screen.blit(q_txt, (start_x, panel_y + 65))
        q_txt_ew = self.font.render(f"Queued E/W: {q_ew}", True, (230,230,230))
        screen.blit(q_txt_ew, (start_x, panel_y + 90))

        # --- NEW: Display the current operational mode ---
        if is_smart_mode:
            mode_text = "MODE: SMART (ADAPTIVE)"
            mode_color = (0, 255, 150)
        else:
            mode_text = "MODE: STANDARD (FIXED TIMER)"
            mode_color = (255, 100, 100)
        
        mode_surf = self.font.render(mode_text, True, mode_color)
        screen.blit(mode_surf, (560, panel_y + 15))
        
        green_txt = self.font.render(f"Green Time: {predictor.current_green_duration}s", True, (0, 255, 0))
        screen.blit(green_txt, (620, panel_y + 40))

        if any(v.is_emergency for v in vehicles):
            now = time.time()
            if now - self.last_flash > 0.4:
                self.flash_on = not self.flash_on
                self.last_flash = now
            if self.flash_on:
                alert = self.title_font.render("🚨 EMERGENCY 🚨", True, (255, 80, 80))
                screen.blit(alert, (620, panel_y + 80))