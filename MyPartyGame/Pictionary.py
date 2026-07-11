import sys
import subprocess
from PIL import Image, ImageDraw
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.uix.colorpicker import ColorPicker
from kivy.graphics import Color, Rectangle
from kivy.graphics.texture import Texture
from kivy.clock import Clock
from kivy.core.window import Window

# Set background color to mimic the original app's navy theme
Window.clearcolor = (11/255, 19/255, 43/255, 1)

class KivyCanvasWorkspace(Widget):
    """The central viewport workspace handling touch input and texture updates."""
    def __init__(self, app_instance, **kwargs):
        super().__init__(**kwargs)
        self.app = app_instance
        self.initialized = False
        # Use Clock to schedule the initial resize after Kivy calculates real screen layout sizes
        self.bind(size=self.on_workspace_resize, pos=self.on_workspace_resize)
        
    def on_workspace_resize(self, instance, value):
        # Prevent premature initializing at Kivy's default 100x100 layout state
        if self.width <= 100 or self.height <= 100:
            return
            
        if not self.initialized:
            self.app.canvas_width = int(self.width)
            self.app.canvas_height = int(self.height)
            self.app.pil_image = Image.new("RGB", (self.app.canvas_width, self.app.canvas_height), "white")
            self.app.pil_draw = ImageDraw.Draw(self.app.pil_image)
            self.app.save_to_history()
            self.initialized = True
        else:
            # Safely expand canvas buffer context if window is dynamically maximized
            if self.width > self.app.canvas_width or self.height > self.app.canvas_height:
                new_w = max(int(self.width), self.app.canvas_width)
                new_h = max(int(self.height), self.app.canvas_height)
                new_pil = Image.new("RGB", (new_w, new_h), "white")
                new_pil.paste(self.app.pil_image, (0, 0))
                self.app.pil_image = new_pil
                self.app.pil_draw = ImageDraw.Draw(self.app.pil_image)
                self.app.canvas_width = new_w
                self.app.canvas_height = new_h
        self.refresh_from_pil()

    def refresh_from_pil(self):
        self.canvas.clear()
        if not hasattr(self, 'app') or not hasattr(self.app, 'pil_image'):
            return
            
        # Flip vertically since PIL coordinate space starts Top-Left, Kivy Bottom-Left
        flipped_image = self.app.pil_image.transpose(Image.FLIP_TOP_BOTTOM)
        data = flipped_image.convert('RGBA').tobytes()
        
        texture = Texture.create(size=self.app.pil_image.size, colorfmt='rgba')
        texture.blit_buffer(data, colorfmt='rgba', bufferfmt='ubyte')
        
        with self.canvas:
            Color(1, 1, 1, 1)
            # Clip drawing to match exact container dimensions
            Rectangle(texture=texture, pos=self.pos, size=(self.width, self.height))

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return False
            
        if not self.app.timer_started:
            self.app.start_timer()

        local_x = int(touch.x - self.x)
        local_y = int(self.height - (touch.y - self.y))

        if self.app.current_tool == "fill":
            self.app.flood_fill(local_x, local_y)
            self.app.save_to_history()
        else:
            touch.ud['last_x'] = local_x
            touch.ud['last_y'] = local_y
            # Enable single point dot clicks
            self.app.pil_draw.ellipse(
                [local_x - self.app.brush_size//2, local_y - self.app.brush_size//2, 
                 local_x + self.app.brush_size//2, local_y + self.app.brush_size//2],
                fill=self.app.active_color
            )
            self.refresh_from_pil()
        return True

    def on_touch_move(self, touch):
        if not self.collide_point(*touch.pos) or self.app.current_tool == "fill":
            return False
            
        if 'last_x' in touch.ud:
            local_x = int(touch.x - self.x)
            local_y = int(self.height - (touch.y - self.y))
            
            self.app.pil_draw.line(
                [(touch.ud['last_x'], touch.ud['last_y']), (local_x, local_y)],
                fill=self.app.active_color, width=self.app.brush_size, joint="round"
            )
            touch.ud['last_x'] = local_x
            touch.ud['last_y'] = local_y
            self.refresh_from_pil()
        return True

    def on_touch_up(self, touch):
        if 'last_x' in touch.ud:
            if self.app.current_tool != "fill":
                self.app.save_to_history()
            return True
        return False


class StudioCanvasProApp(App):
    def build(self):
        self.title = "Studio Canvas Pro"
        
        self.CLR_SIDEBAR = (28/255, 37/255, 65/255, 1)
        self.CLR_BTN_IDLE = (58/255, 80/255, 107/255, 1)
        self.CLR_BTN_ACTIVE = (43/255, 59/255, 78/255, 1)
        self.CLR_ACCENT = (91/255, 192/255, 190/255, 1)

        self.brush_color = "#00b4d8"
        self.eraser_color = "#ffffff"
        self.active_color = self.brush_color
        self.brush_size = 5
        self.current_tool = "draw"
        
        self.time_left = 300
        self.timer_running = False
        self.timer_started = False
        self.timer_event = None

        self.undo_stack = []
        self.redo_stack = []

        Window.bind(on_key_down=self.handle_keyboard_shortcuts)

        root_layout = BoxLayout(orientation='horizontal')

        # Set sidebar spacing to 0; elastic spacers will govern layout scaling between groups exclusively
        sidebar = BoxLayout(orientation='vertical', size_hint_x=None, width=240, padding=15, spacing=0)
        with sidebar.canvas.before:
            Color(*self.CLR_SIDEBAR)
            self.sidebar_bg = Rectangle(pos=sidebar.pos, size=sidebar.size)
        sidebar.bind(pos=self._update_sidebar_rect, size=self._update_sidebar_rect)

        title_label = Label(text="STUDIO CANVAS", font_size='16sp', bold=True, color=self.CLR_ACCENT, size_hint_y=None, height=30)
        subtitle_label = Label(text="Professional Edition", font_size='11sp', italic=True, color=(108/255, 117/255, 125/255, 1), size_hint_y=None, height=20)
        sidebar.add_widget(title_label)
        sidebar.add_widget(subtitle_label)
        
        # Spacer below header
        sidebar.add_widget(Widget(size_hint_y=1))

        # --- CLUSTER 1: Tool Buttons (Kept close together) ---
        tools_box = BoxLayout(orientation='vertical', spacing=5, size_hint_y=None, height=130)
        self.btn_draw = Button(text="✏️ Brush Tool", background_color=self.CLR_BTN_ACTIVE, background_normal='', size_hint_y=None, height=40)
        self.btn_draw.bind(on_press=self.set_tool_draw)
        
        self.btn_eraser = Button(text="🧽 Eraser Tool", background_color=self.CLR_BTN_IDLE, background_normal='', size_hint_y=None, height=40)
        self.btn_eraser.bind(on_press=self.set_tool_eraser)
        
        self.btn_fill = Button(text="🪣 Paint Bucket", background_color=self.CLR_BTN_IDLE, background_normal='', size_hint_y=None, height=40)
        self.btn_fill.bind(on_press=self.set_tool_fill)

        tools_box.add_widget(self.btn_draw)
        tools_box.add_widget(self.btn_eraser)
        tools_box.add_widget(self.btn_fill)
        sidebar.add_widget(tools_box)
        
        # Spacer below tools
        sidebar.add_widget(Widget(size_hint_y=1))

        # --- Color Swatch ---
        sidebar.add_widget(Label(text="Active Color Swatch", font_size='12sp', bold=True, size_hint_y=None, height=20, halign='left'))
        self.color_preview = Button(text="Pick Color", background_color=self.hex_to_kivy_rgba(self.brush_color), background_normal='', size_hint_y=None, height=40)
        self.color_preview.bind(on_press=self.open_color_picker)
        sidebar.add_widget(self.color_preview)
        
        # Spacer below color selector
        sidebar.add_widget(Widget(size_hint_y=1))

        # --- Brush Size Slider ---
        sidebar.add_widget(Label(text="Brush Size", font_size='12sp', bold=True, size_hint_y=None, height=20))
        size_slider = Slider(min=1, max=100, value=self.brush_size, step=1, size_hint_y=None, height=30)
        size_slider.bind(value=self.update_size)
        sidebar.add_widget(size_slider)
        
        # Spacer below brush slider
        sidebar.add_widget(Widget(size_hint_y=1))

        # --- Timer Box ---
        timer_box = BoxLayout(orientation='vertical', size_hint_y=None, height=80, padding=5, spacing=5)
        with timer_box.canvas.before:
            Color(11/255, 19/255, 27/255, 1)
            self.timer_bg = Rectangle(pos=timer_box.pos, size=timer_box.size)
        timer_box.bind(pos=self._update_timer_rect, size=self._update_timer_rect)

        self.timer_label = Label(text="⏱️ 05:00", font_size='16sp', bold=True)
        btn_reset_timer = Button(text="Reset Timer", background_color=self.CLR_BTN_IDLE, background_normal='', size_hint_y=None, height=30)
        btn_reset_timer.bind(on_press=self.reset_timer)
        timer_box.add_widget(self.timer_label)
        timer_box.add_widget(btn_reset_timer)
        sidebar.add_widget(timer_box)
        
        # Spacer below timer
        sidebar.add_widget(Widget(size_hint_y=1))

        # --- CLUSTER 2: Action Controls (Kept close together) ---
        actions_box = BoxLayout(orientation='vertical', spacing=5, size_hint_y=None, height=175)
        
        utils_grid = GridLayout(cols=2, spacing=5, size_hint_y=None, height=35)
        btn_undo = Button(text="↩️ Undo", background_color=self.CLR_BTN_IDLE, background_normal='')
        btn_undo.bind(on_press=lambda x: self.undo())
        btn_redo = Button(text="↪️ Redo", background_color=self.CLR_BTN_IDLE, background_normal='')
        btn_redo.bind(on_press=lambda x: self.redo())
        utils_grid.add_widget(btn_undo)
        utils_grid.add_widget(btn_redo)

        btn_export = Button(text="💾 Export Artwork", background_color=self.CLR_BTN_IDLE, background_normal='', size_hint_y=None, height=40)
        btn_export.bind(on_press=self.save_artwork)

        btn_wipe = Button(text="🗑️ Wipe Canvas", background_color=self.CLR_BTN_IDLE, background_normal='', size_hint_y=None, height=40)
        btn_wipe.bind(on_press=self.clear_canvas)

        btn_menu = Button(text="Main Menu", background_color=self.CLR_BTN_IDLE, background_normal='', size_hint_y=None, height=40)
        btn_menu.bind(on_press=self.go_to_menu)

        actions_box.add_widget(utils_grid)
        actions_box.add_widget(btn_export)
        actions_box.add_widget(btn_wipe)
        actions_box.add_widget(btn_menu)
        
        sidebar.add_widget(actions_box)

        self.workspace_widget = KivyCanvasWorkspace(self)
        
        root_layout.add_widget(sidebar)
        root_layout.add_widget(self.workspace_widget)
        return root_layout

    def _update_sidebar_rect(self, instance, value):
        self.sidebar_bg.pos = instance.pos
        self.sidebar_bg.size = instance.size

    def _update_timer_rect(self, instance, value):
        self.timer_bg.pos = instance.pos
        self.timer_bg.size = instance.size

    def start_timer(self):
        if not self.timer_running:
            self.timer_running = True
            self.timer_started = True
            self.timer_event = Clock.schedule_interval(self.update_timer_countdown, 1.0)

    def update_timer_countdown(self, dt):
        if self.time_left > 0:
            mins, secs = divmod(self.time_left, 60)
            self.timer_label.text = f"⏱️ {mins:02d}:{secs:02d}"
            self.timer_label.color = (74/255, 222/255, 128/255, 1)
            self.time_left -= 1
        else:
            self.timer_running = False
            self.timer_label.text = "⏱️ DEADLINE"
            self.timer_label.color = (239/255, 68/255, 68/255, 1)
            if self.timer_event:
                Clock.unschedule(self.timer_event)

    def reset_timer(self, instance=None):
        if self.timer_event:
            Clock.unschedule(self.timer_event)
        self.time_left = 300
        self.timer_running = False
        self.timer_started = False
        self.timer_label.text = "⏱️ 05:00"
        self.timer_label.color = (1, 1, 1, 1)

    def save_to_history(self):
        if hasattr(self, 'pil_image'):
            if len(self.undo_stack) >= 20:
                self.undo_stack.pop(0)
            self.undo_stack.append(self.pil_image.copy())
            self.redo_stack.clear()

    def undo(self):
        if len(self.undo_stack) > 1:
            current_state = self.undo_stack.pop()
            self.redo_stack.append(current_state)
            self.pil_image = self.undo_stack[-1].copy()
            self.pil_draw = ImageDraw.Draw(self.pil_image)
            self.workspace_widget.refresh_from_pil()

    def redo(self):
        if self.redo_stack:
            restored_state = self.redo_stack.pop()
            self.undo_stack.append(restored_state)
            self.pil_image = restored_state.copy()
            self.pil_draw = ImageDraw.Draw(self.pil_image)
            self.workspace_widget.refresh_from_pil()

    def flood_fill(self, start_x, start_y):
        target_rgb = self.hex_to_rgb(self.brush_color)
        ImageDraw.floodfill(self.pil_image, xy=(start_x, start_y), value=target_rgb, thresh=15)
        self.workspace_widget.refresh_from_pil()

    def clear_canvas(self, instance=None):
        self.pil_image = Image.new("RGB", (self.canvas_width, self.canvas_height), "white")
        self.pil_draw = ImageDraw.Draw(self.pil_image)
        self.undo_stack.clear()
        self.redo_stack.clear()
        self.save_to_history()
        self.set_tool_draw()
        self.workspace_widget.refresh_from_pil()

    def save_artwork(self, instance=None):
        output_filename = "masterpiece.png"
        self.pil_image.save(output_filename)
        print(f"Artwork saved locally to {output_filename}")

    def reset_tool_highlights(self):
        self.btn_draw.background_color = self.CLR_BTN_IDLE
        self.btn_eraser.background_color = self.CLR_BTN_IDLE
        self.btn_fill.background_color = self.CLR_BTN_IDLE

    def set_tool_draw(self, instance=None):
        self.current_tool = "draw"
        self.active_color = self.brush_color
        self.reset_tool_highlights()
        self.btn_draw.background_color = self.CLR_BTN_ACTIVE

    def set_tool_eraser(self, instance=None):
        self.current_tool = "erase"
        self.active_color = self.eraser_color
        self.reset_tool_highlights()
        self.btn_eraser.background_color = self.CLR_BTN_ACTIVE

    def set_tool_fill(self, instance=None):
        self.current_tool = "fill"
        self.reset_tool_highlights()
        self.btn_fill.background_color = self.CLR_BTN_ACTIVE

    def update_size(self, instance, value):
        self.brush_size = int(value)

    def open_color_picker(self, instance):
        picker = ColorPicker(color=self.hex_to_kivy_rgba(self.brush_color))
        popup = Popup(title='Pick Active Color Spec', content=picker, size_hint=(0.8, 0.8))
        
        def on_color_chosen(picker_instance, color_value):
            hex_str = '#{:02x}{:02x}{:02x}'.format(
                int(max(0, min(255, color_value[0] * 255))),
                int(max(0, min(255, color_value[1] * 255))),
                int(max(0, min(255, color_value[2] * 255)))
            )
            self.brush_color = hex_str
            self.color_preview.background_color = color_value
            if self.current_tool == "draw":
                self.active_color = hex_str
                
        picker.bind(color=on_color_chosen)
        popup.open()

    def handle_keyboard_shortcuts(self, window, key, scancode, codepoint, modifiers):
        if 'ctrl' in modifiers or 'meta' in modifiers:
            if key == 122: # 'z'
                self.undo()
                return True
            elif key == 121: # 'y'
                self.redo()
                return True
        return False

    def hex_to_rgb(self, hex_str):
        hex_str = hex_str.lstrip('#')
        return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))

    def hex_to_kivy_rgba(self, hex_str):
        rgb = self.hex_to_rgb(hex_str)
        return (rgb[0]/255, rgb[1]/255, rgb[2]/255, 1)

    def go_to_menu(self, instance=None):
        try:
            subprocess.Popen([sys.executable, "main.py"])
            self.stop()
        except Exception as e:
            print(f"Error launching main.py: {e}")

if __name__ == "__main__":
    StudioCanvasProApp().run()
