# simulation/intersection.py
from simulation.config import YELLOW_DURATION, MIN_GREEN, MAX_GREEN, FIXED_GREEN_DURATION

class IntersectionManager:
    def __init__(self, lights):
        self.lights = lights
        self.active_group = ("N", "S")
        self.phase = "green"
        self.phase_timer = 0.0
        self.green_duration = FIXED_GREEN_DURATION # Start with a default
        self.yellow_duration = YELLOW_DURATION

        self._set_initial_light_states()

    def _set_initial_light_states(self):
        for light in self.lights:
            light.state = "green" if light.direction in self.active_group else "red"

    def _update_light_states(self):
        for light in self.lights:
            if light.direction in self.active_group:
                light.state = self.phase
                light.remaining_time = self._get_remaining_time()
            else:
                light.state = "red"
                light.remaining_time = 0

    def _get_remaining_time(self):
        duration = self.green_duration if self.phase == "green" else self.yellow_duration
        return max(0, int(duration - self.phase_timer))
    
    def _count_waiting(self, vehicles, directions):
        return sum(1 for v in vehicles if v.direction in directions and v.speed == 0 and v._is_before_stop_line())

    # --- UPDATED: Main update method now handles both modes ---
    def update(self, dt, vehicles, is_smart_mode):
        self.phase_timer += dt

        # Smart Mode Logic (Adaptive and Responsive)
        if is_smart_mode:
            emergency_vehicle = next((v for v in vehicles if v.is_emergency and not v.has_crossed), None)
            if emergency_vehicle:
                self._handle_emergency(emergency_vehicle)
                return

            if self.phase == "green" and self.phase_timer >= self.green_duration:
                self.phase = "yellow"
                self.phase_timer = 0
            elif self.phase == "yellow" and self.phase_timer >= self.yellow_duration:
                self.phase = "green"
                self.phase_timer = 0
                self.active_group = ("E", "W") if self.active_group == ("N", "S") else ("N", "S")
                self._adapt_green_duration(vehicles)
        
        # Standard Mode Logic (Fixed Timer)
        else:
            self.green_duration = FIXED_GREEN_DURATION # Always use the fixed time
            if self.phase == "green" and self.phase_timer >= self.green_duration:
                self.phase = "yellow"
                self.phase_timer = 0
            elif self.phase == "yellow" and self.phase_timer >= self.yellow_duration:
                self.phase = "green"
                self.phase_timer = 0
                self.active_group = ("E", "W") if self.active_group == ("N", "S") else ("N", "S")
        
        self._update_light_states()

    def _adapt_green_duration(self, vehicles):
        count = self._count_waiting(vehicles, self.active_group)
        self.green_duration = min(MAX_GREEN, max(MIN_GREEN, 4 + count // 2))

    def _handle_emergency(self, vehicle):
        for light in self.lights:
            light.state = "green" if light.direction == vehicle.direction else "red"
            light.remaining_time = 0
        self.phase_timer = 0