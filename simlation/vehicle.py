# simulation/vehicle.py
import pygame
import random
from simulation.config import WIDTH, HEIGHT, STOP_OFFSET, VEHICLE_WIDTH, VEHICLE_HEIGHT, BASE_SPEED, LANE_WIDTH, DILEMMA_ZONE_DISTANCE, BRAKING_DISTANCE

class Vehicle:
    def __init__(self, direction, all_vehicles, is_emergency=False):
        self.direction = direction
        self.is_emergency = is_emergency
        self.color = (255, 60, 60) if is_emergency else (0, 150, 255)
        self.width, self.height = (VEHICLE_WIDTH, VEHICLE_HEIGHT) if direction in ("N", "S") else (VEHICLE_HEIGHT, VEHICLE_WIDTH)
        self.lane = random.choice([1, 2])
        self.x, self.y = self._start_pos_for_direction(direction)
        self.speed = BASE_SPEED
        self.has_crossed = False
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def _start_pos_for_direction(self, d):
        cx, cy = WIDTH // 2, HEIGHT // 2
        offset = (LANE_WIDTH * 0.5) if self.lane == 1 else (LANE_WIDTH * 1.5)
        if d == "N": return (cx + offset, -self.height)
        if d == "S": return (cx - offset, HEIGHT)
        if d == "E": return (WIDTH, cy - offset)
        if d == "W": return (-self.width, cy + offset)
        return (0, 0)

    def draw(self, screen):
        self.rect.topleft = (self.x, self.y)
        pygame.draw.rect(screen, self.color, self.rect)

    def move(self, lights, all_vehicles):
        if not self.has_crossed and self._passed_intersection():
            self.has_crossed = True
        if self.is_emergency or self.has_crossed:
            self.speed = BASE_SPEED
            self._advance()
            return

        stop_signal, light_state = self._check_traffic_light(lights)
        is_stopped_by_vehicle_ahead = self._check_vehicle_ahead(all_vehicles)
        is_stopped_by_cross_traffic = False
        if not stop_signal and not is_stopped_by_vehicle_ahead and self._is_at_stop_line():
            is_stopped_by_cross_traffic = self._check_cross_traffic(all_vehicles)
            
        must_stop = stop_signal or is_stopped_by_vehicle_ahead or is_stopped_by_cross_traffic

        if not must_stop:
            self.speed = min(BASE_SPEED, self.speed + 0.2)
        else:
            dist_to_line = self._distance_to_stop_line()
            
            if self.speed > dist_to_line and dist_to_line >= 0:
                self.speed = max(0, dist_to_line)
            elif is_stopped_by_vehicle_ahead or (dist_to_line <= BRAKING_DISTANCE):
                deceleration = 0.2
                self.speed = max(0, self.speed - deceleration)
            elif not self._is_before_stop_line():
                self.speed = 0
            else:
                 self.speed = BASE_SPEED

        self._advance()
    
    def _check_traffic_light(self, lights):
        for light in lights:
            if light.direction == self.direction and light.lane == self.lane:
                if light.state == 'red':
                    return (self._is_before_stop_line(), 'red') 
                
                if light.state == 'yellow':
                    dist = self._distance_to_stop_line()
                    should_stop = (dist > DILEMMA_ZONE_DISTANCE) and self._is_before_stop_line()
                    return (should_stop, 'yellow')
                
                return (False, 'green')
        return (False, 'off')

    def _distance_to_stop_line(self):
        if self.direction == "N": return (HEIGHT // 2 - STOP_OFFSET) - (self.y + self.height)
        if self.direction == "S": return self.y - (HEIGHT // 2 + STOP_OFFSET)
        if self.direction == "E": return self.x - (WIDTH // 2 + STOP_OFFSET)
        if self.direction == "W": return (WIDTH // 2 - STOP_OFFSET) - (self.x + self.width)
        return float('inf')

    def _check_vehicle_ahead(self, all_vehicles):
        safe_distance = self.height * 1.5
        for other in all_vehicles:
            if self == other or self.direction != other.direction or self.lane != other.lane:
                continue
            dist = float('inf')
            if self.direction == 'N' and other.y > self.y: dist = other.y - self.y
            elif self.direction == 'S' and other.y < self.y: dist = self.y - other.y
            elif self.direction == 'W' and other.x > self.x: dist = other.x - self.x
            elif self.direction == 'E' and other.x < self.x: dist = self.x - other.x
            if 0 < dist < (safe_distance + self.height):
                return True
        return False

    def _check_cross_traffic(self, all_vehicles):
        intersection_box = pygame.Rect((WIDTH // 2) - (LANE_WIDTH * 2), (HEIGHT // 2) - (LANE_WIDTH * 2), LANE_WIDTH * 4, LANE_WIDTH * 4)
        perpendicular_dirs = {"N": ("E", "W"), "S": ("E", "W"), "E": ("N", "S"), "W": ("N", "S")}
        for other in all_vehicles:
            if self != other and other.direction in perpendicular_dirs[self.direction] and intersection_box.colliderect(other.rect):
                return True
        return False

    def _advance(self):
        if self.direction == "N": self.y += self.speed
        elif self.direction == "S": self.y -= self.speed
        elif self.direction == "E": self.x -= self.speed
        elif self.direction == "W": self.x += self.speed

    def _is_before_stop_line(self):
        if self.direction == "N": return self.y + self.height < (HEIGHT // 2 - STOP_OFFSET)
        if self.direction == "S": return self.y > (HEIGHT // 2 + STOP_OFFSET)
        if self.direction == "E": return self.x > (WIDTH // 2 + STOP_OFFSET)
        if self.direction == "W": return self.x + self.width < (WIDTH // 2 - STOP_OFFSET)
        return False
    
    def _is_at_stop_line(self):
        check_range = BASE_SPEED * 2 
        if self.direction == "N": return abs((self.y + self.height) - (HEIGHT // 2 - STOP_OFFSET)) < check_range
        if self.direction == "S": return abs(self.y - (HEIGHT // 2 + STOP_OFFSET)) < check_range
        if self.direction == "E": return abs(self.x - (WIDTH // 2 + STOP_OFFSET)) < check_range
        if self.direction == "W": return abs((self.x + self.width) - (WIDTH // 2 - STOP_OFFSET)) < check_range
        return False

    def _passed_intersection(self):
        center_buffer = 10
        # --- SYNTAX FIX ---
        if self.direction == "N" and self.y > HEIGHT // 2 + center_buffer: return True
        if self.direction == "S" and self.y < HEIGHT // 2 - center_buffer: return True
        if self.direction == "E" and self.x < WIDTH // 2 - center_buffer: return True
        if self.direction == "W" and self.x > WIDTH // 2 + center_buffer: return True
        return False