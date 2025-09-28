# traffic_light.py
import pygame

LIGHT_RADIUS = 8

class TrafficLight:
    def __init__(self, x, y, direction, lane):
        self.x = x
        self.y = y
        self.direction = direction
        self.lane = lane
        self.state = "red"
        self.remaining_time = 0

    def draw(self, screen):
        if self.state == "green": col = (0, 200, 0)
        elif self.state == "yellow": col = (255, 200, 0)
        else: col = (255, 0, 0)

        pygame.draw.circle(screen, col, (int(self.x), int(self.y)), LIGHT_RADIUS)
        pygame.draw.circle(screen, (50, 50, 50), (int(self.x), int(self.y)), LIGHT_RADIUS, 1)

        # --- UI CLEANUP: Only show details for the primary lane's light ---
        if self.lane == 1:
            # Draw the lane number
            font = pygame.font.SysFont("Arial", 12, bold=True)
            txt = font.render(str(self.direction), True, (255, 255, 255))
            screen.blit(txt, (self.x + LIGHT_RADIUS, self.y - LIGHT_RADIUS))

            # Draw the countdown timer
            if self.remaining_time > 0:
                timer_font = pygame.font.SysFont("Arial", 16, bold=True)
                timer_txt = timer_font.render(str(self.remaining_time), True, (255, 255, 255))
                screen.blit(timer_txt, (self.x - timer_txt.get_width() // 2, self.y - 30))