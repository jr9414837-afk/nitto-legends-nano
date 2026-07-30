import sys
import time
import random
import json
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle

class NittoVisualGame(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=20, spacing=15, **kwargs)
        
        # Core Game State Management
        self.cash = 2500
        self.distance = 0.0
        self.velocity = 0.0
        self.current_gear = 1
        self.gear_ratios = [0.0, 3.3, 2.1, 1.4, 1.0]
        self.max_rpm = 7200
        self.torque = 180.0
        self.mass = 1200.0
        self.is_racing = False
        self.green_light_time = 0.0
        
        # Visual Render Canvas Box (The Drag Strip Track)
        self.canvas_widget = BoxLayout(size_hint_y=0.3)
        with self.canvas_widget.canvas:
            Color(0.15, 0.15, 0.15, 1) # Asphalt track
            self.bg_rect = Rectangle(size=(800, 200), pos=(0, 400))
            Color(1, 0, 0, 1) # Player Red Car
            self.car_rect = Rectangle(size=(60, 30), pos=(20, 450))
        self.add_widget(self.canvas_widget)

        # Telemetry Display Readout
        self.telemetry_label = Label(
            text=f"★ NITTO 1320 NANO: READY ★\nWallet Cash: ${self.cash}\nStatus: Stage your vehicle...",
            font_size='18sp', halign='center', size_hint_y=0.4
        )
        self.add_widget(self.telemetry_label)
        
        # Interactive Layout Buttons Container
        self.button_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=0.3)
        
        self.stage_btn = Button(text="STAGE CAR", font_size='18sp')
        self.stage_btn.bind(on_press=self.trigger_burnout_staging)
        self.button_layout.add_widget(self.stage_btn)
        
        self.shift_btn = Button(text="SHIFT GEAR", font_size='18sp', disabled=True)
        self.shift_btn.bind(on_press=self.execute_gear_shift)
        self.button_layout.add_widget(self.shift_btn)
        
        self.add_widget(self.button_layout)
        
        # Dynamic responsive layout adjustments for canvas assets
        self.bind(size=self.reposition_graphics_canvas)

    def reposition_graphics_canvas(self, *args):
        self.bg_rect.size = (self.canvas_widget.width, self.canvas_widget.height)
        self.bg_rect.pos = self.canvas_widget.pos
        self.car_rect.pos = (self.canvas_widget.x + 20, self.canvas_widget.y + (self.canvas_widget.height / 2) - 15)

    def trigger_burnout_staging(self, instance):
        if self.is_racing: return
        self.stage_btn.disabled = True
        self.telemetry_label.text = "🚦 PRE-STAGED...\n🚦 STAGED...\n🔴 AMBER LIGHT COUNTDOWN ACTIVE..."
        Clock.schedule_once(self.fire_green_light, random.uniform(1.8, 3.2))

    def fire_green_light(self, dt):
        self.green_light_time = time.time()
        self.telemetry_label.text = "🟢 GREEN LIGHT! LAUNCH NOW!"
        self.stage_btn.text = "LAUNCH!"
        self.stage_btn.disabled = False

    def execute_gear_shift(self, instance):
        if not self.is_racing: return
        if self.current_gear < len(self.gear_ratios) - 1:
            self.current_gear += 1
            self.telemetry_label.text += f"\n⚙ Shifted up to Gear {self.current_gear}!"

    def trigger_race_launch(self):
        self.is_racing = True
        self.shift_btn.disabled = False
        self.stage_btn.disabled = True
        self.distance = 0.0
        self.velocity = 2.0
        self.current_gear = 1
        Clock.schedule_interval(self.process_physics_step, 0.05)

    def process_physics_step(self, dt):
        if not self.is_racing: return False
        
        # Dynamic engine calculations
        wheel_rpm = (self.velocity / (2 * 3.14 * 0.32)) * 60.0
        engine_rpm = wheel_rpm * self.gear_ratios[self.current_gear] * 4.10
        if engine_rpm > self.max_rpm: engine_rpm = self.max_rpm
        
        # Forward Force vector physics
        force_vector = (self.torque * self.gear_ratios[self.current_gear] * 4.10) / 0.32
        drag = 0.5 * 0.35 * 2.2 * 1.2 * (self.velocity ** 2)
        acceleration = (force_vector - drag) / self.mass
        
        self.velocity += acceleration * dt
        self.distance += self.velocity * dt
        
        # Map physics metrics to screen canvas layout positions
        track_progress = min(1.0, self.distance / 402.34)
        canvas_max_travel = self.canvas_widget.width - 80
        self.car_rect.pos = (self.canvas_widget.x + 20 + (track_progress * canvas_max_travel), self.car_rect.pos[1])
        
        self.telemetry_label.text = (
            f"🏁 Quarter-Mile Track: {self.distance:.1f}m / 402.3m\n"
            f"⚙ Gear Status: {self.current_gear} | Tachometer: {int(engine_rpm)} RPM\n"
            f"⚡ Trap Speed: {self.velocity * 3.6:.1f} km/h"
        )
        
        # Check finish line status loop
        if self.distance >= 402.34:
            self.is_racing = False
            self.shift_btn.disabled = True
            self.stage_btn.text = "STAGE CAR"
            self.stage_btn.disabled = False
            self.cash += 450
            self.telemetry_label.text = f"🏆 WINNER! Crossed the quarter-mile timing traps!\nWallet Balance: ${self.cash}"
            return False
        return True

    def handle_button(self, instance):
        if self.stage_btn.text == "LAUNCH!":
            rt = time.time() - self.green_light_time
            if rt < 0.05:
                self.telemetry_label.text = f"❌ RED LIGHT FOUL! Reaction: {rt:.3f}s\nPenalty: -$200"
                self.cash = max(0, self.cash - 200)
                self.stage_btn.text = "STAGE CAR"
            else:
                self.trigger_race_launch()
        else:
            self.trigger_burnout_staging(instance)

class NittoNanoApp(App):
    def build(self):
        root = NittoVisualGame()
        root.stage_btn.unbind(on_press=root.trigger_burnout_staging)
        root.stage_btn.bind(on_press=root.handle_button)
        return root

if __name__ == '__main__':
    NittoNanoApp().run()

