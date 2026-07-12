import sys
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.image import Image as UIImage
from kivy.graphics import Color, Rectangle, Line
from kivy.clock import Clock
from kivy.utils import platform

# --- COLOR PALETTE ---
BG_COLOR = (0.102, 0.102, 0.118, 1)       # #1A1A1E Theme Background
BUTTON_BG = (0.180, 0.188, 0.337, 1)      # #2E3056 Button Color
CANVAS_BG = (1, 1, 1, 1)                  # Pure White Canvas
INK_COLOR = (0, 0, 0, 1)                  # Black Ink

# --- GLOBAL GAME CONFIG ---
game_history = [] 
TOTAL_MINUTES = 5
TOTAL_PASSES = 4  

class ColoredScreen(Screen):
    """ Base screen class to automatically apply the custom dark theme background """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(*BG_COLOR)
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

    def _update_rect(self, instance, value):
        self.bg_rect.size = instance.size
        self.bg_rect.pos = instance.pos


class MainMenu(ColoredScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        root_anchor = AnchorLayout(anchor_x='center', anchor_y='center', padding=30)
        is_mobile = platform in ('android', 'ios')
        
        main_layout = BoxLayout(
            orientation='vertical', 
            spacing=25, 
            size_hint=(0.9 if is_mobile else 0.6, None),
            height=410 if is_mobile else 450             
        )
        
        header_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=80, spacing=15)
        
        title_label = Label(
            text="Telestrations", 
            bold=True, 
            size_hint_x=0.70,  
            halign='left', 
            valign='middle'
        )
        title_label.bind(size=title_label.setter('text_size'))
        title_label.bind(height=lambda instance, val: setattr(instance, 'font_size', f'{val * 0.55}sp'))
        header_layout.add_widget(title_label)
        
        settings_btn = Button(
            text="Total passes?",
            markup=True, 
            size_hint=(None, 1.0), 
            width=140 if is_mobile else 180, 
            background_color=BUTTON_BG, 
            background_normal='',
            font_size='14sp' if is_mobile else '18sp'
        )
        settings_btn.bind(on_press=self.open_settings)
        
        settings_anchor = AnchorLayout(anchor_x='right', anchor_y='center', size_hint_x=0.30)
        settings_anchor.add_widget(settings_btn)
        header_layout.add_widget(settings_anchor)
        
        main_layout.add_widget(header_layout)
        
        self.word_input = TextInput(
            hint_text="Enter a secret word/phrase to start...",
            multiline=False,
            size_hint_y=None,
            height=55 if is_mobile else 65,
            font_size='18sp' if is_mobile else '22sp',
            padding=[15, 12, 15, 12],
            background_color=(0.95, 0.95, 0.95, 1)
        )
        main_layout.add_widget(self.word_input)
        
        start_btn = Button(
            text="Start Game", 
            size_hint_y=None, 
            height=60 if is_mobile else 70, 
            font_size='20sp' if is_mobile else '24sp',
            background_color=BUTTON_BG, 
            background_normal=''
        )
        start_btn.bind(on_press=self.start_game)
        main_layout.add_widget(start_btn)

        # Added dynamic native system dashboard return button
        back_btn = Button(
            text="Back to Dashboard", 
            size_hint_y=None, 
            height=45, 
            font_size='16sp',
            background_color=BUTTON_BG, 
            background_normal=''
        )
        back_btn.bind(on_press=self.go_to_dashboard)
        main_layout.add_widget(back_btn)
        
        root_anchor.add_widget(main_layout)
        self.add_widget(root_anchor)

    def go_to_dashboard(self, instance):
        self.manager.current = "main_dashboard"

    def open_settings(self, instance):
        global TOTAL_PASSES
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        pass_control_layout = BoxLayout(orientation='horizontal', size_hint_y=0.6, spacing=10)
        pass_control_layout.add_widget(Label(text="Number of Passes:", font_size='18sp'))
        
        self.passes_label = Label(text=str(TOTAL_PASSES), font_size='22sp', bold=True)
        
        btn_minus = Button(text="-", size_hint_x=0.2, background_color=BUTTON_BG, background_normal='')
        btn_minus.bind(on_press=self.decrement_passes)
        
        btn_plus = Button(text="+", size_hint_x=0.2, background_color=BUTTON_BG, background_normal='')
        btn_plus.bind(on_press=self.increment_passes)
        
        pass_control_layout.add_widget(btn_minus)
        pass_control_layout.add_widget(self.passes_label)
        pass_control_layout.add_widget(btn_plus)
        content.add_widget(pass_control_layout)
        
        close_btn = Button(text="Save & Close", size_hint_y=0.4, background_color=BUTTON_BG, background_normal='')
        content.add_widget(close_btn)
        
        popup = Popup(title="Settings Menu", content=content, size_hint=(0.8, 0.4), background_color=BG_COLOR)
        close_btn.bind(on_press=popup.dismiss)
        popup.open()

    def increment_passes(self, instance):
        global TOTAL_PASSES
        TOTAL_PASSES += 1
        self.passes_label.text = str(TOTAL_PASSES)

    def decrement_passes(self, instance):
        global TOTAL_PASSES
        if TOTAL_PASSES > 1:
            TOTAL_PASSES -= 1
            self.passes_label.text = str(TOTAL_PASSES)

    def start_game(self, instance):
        global game_history
        game_history = [] 
        if self.word_input.text.strip():
            game_history.append(self.word_input.text.strip())
            self.manager.current = 'telestrations_draw_screen'

class DrawingCanvas(BoxLayout):
    def __init__(self, on_start_drawing=None, **kwargs):
        super().__init__(**kwargs)
        self.on_start_drawing = on_start_drawing  
        self.drawing_started = False
        with self.canvas.before:
            Color(*CANVAS_BG)
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

    def _update_rect(self, instance, value):
        self.bg_rect.size = instance.size
        self.bg_rect.pos = instance.pos

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if self.on_start_drawing and not self.drawing_started:
                self.drawing_started = True
                self.on_start_drawing()

            with self.canvas:
                Color(*INK_COLOR)  
                touch.ud['line'] = Line(points=(touch.x, touch.y), width=4)

    def on_touch_move(self, touch):
        if 'line' in touch.ud and self.collide_point(*touch.pos):
            制造_points = [touch.x, touch.y]
            touch.ud['line'].points += 制造_points

    def clear_canvas(self):
        self.canvas.clear()
        self.drawing_started = False  
        with self.canvas.before:
            self.canvas.before.clear()
            Color(*CANVAS_BG)
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)

class DrawScreen(ColoredScreen):
    def on_enter(self):
        self.clear_widgets()
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        prompt = game_history[-1]
        layout.add_widget(Label(text=f"Draw this: [b]{prompt}[/b]", markup=True, font_size='22sp', size_hint_y=0.08))
        
        self.time_left = TOTAL_MINUTES * 60
        self.timer_label = Label(text=f"Time Left: {TOTAL_MINUTES}:00 (Starts when you draw)", font_size='18sp', size_hint_y=0.05, color=(1, 0.7, 0.3, 1))
        layout.add_widget(self.timer_label)
        
        self.canvas_widget = DrawingCanvas(on_start_drawing=self.start_timer)
        layout.add_widget(self.canvas_widget)
        
        submit_btn = Button(text="Done! Pass Device", size_hint_y=0.1, font_size='18sp', background_color=BUTTON_BG, background_normal='')
        submit_btn.bind(on_press=self.submit_drawing)
        layout.add_widget(submit_btn)
        
        self.add_widget(layout)

    def start_timer(self):
        self.timer_label.color = (1, 0.3, 0.3, 1) 
        Clock.schedule_interval(self.update_timer, 1)

    def update_timer(self, dt):
        self.time_left -= 1
        mins, secs = divmod(self.time_left, 60)
        self.timer_label.text = f"Time Left: {mins:02d}:{secs:02d}"
        if self.time_left <= 0:
            self.submit_drawing(None)

    def submit_drawing(self, instance):
        Clock.unschedule(self.update_timer)
        
        saved_image = self.canvas_widget.export_as_image()
        texture = saved_image.texture
        texture.flip_vertical()
        
        fixed_texture = texture.get_region(0, 0, texture.width, texture.height)
        game_history.append(fixed_texture)
        
        self.canvas_widget.clear_canvas()
        self.manager.current = 'telestrations_guess_screen'

class GuessScreen(ColoredScreen):
    def on_enter(self):
        self.clear_widgets()
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        layout.add_widget(Label(text="What is this drawing?", font_size='22sp', size_hint_y=0.08))
        
        self.time_left = TOTAL_MINUTES * 60
        self.timer_label = Label(text=f"Time Left: {TOTAL_MINUTES}:00", font_size='18sp', size_hint_y=0.05, color=(1, 0.3, 0.3, 1))
        layout.add_widget(self.timer_label)
        
        last_drawing_texture = game_history[-1]
        display_img = UIImage(allow_stretch=True)
        display_img.texture = last_drawing_texture
        layout.add_widget(display_img)
        
        self.guess_input = TextInput(hint_text="Type your guess here...", multiline=False, size_hint_y=0.1, font_size='16sp')
        layout.add_widget(self.guess_input)
        
        submit_btn = Button(text="Submit Guess & Pass", size_hint_y=0.1, font_size='18sp', background_color=BUTTON_BG, background_normal='')
        submit_btn.bind(on_press=self.submit_guess)
        layout.add_widget(submit_btn)
        
        self.add_widget(layout)
        Clock.schedule_interval(self.update_timer, 1)

    def update_timer(self, dt):
        self.time_left -= 1
        mins, secs = divmod(self.time_left, 60)
        self.timer_label.text = f"Time Left: {mins:02d}:{secs:02d}"
        if self.time_left <= 0:
            self.submit_guess(None)

    def submit_guess(self, instance):
        Clock.unschedule(self.update_timer)
        guess_text = self.guess_input.text.strip() if instance else "Ran out of time!"
        if not guess_text:
            guess_text = "No Guess Given"
            
        game_history.append(guess_text)
        
        if len(game_history) >= TOTAL_PASSES + 1: 
            self.manager.current = 'telestrations_end_screen'
        else:
            self.manager.current = 'telestrations_draw_screen'

class EndScreen(ColoredScreen):
    def on_enter(self):
        self.clear_widgets() 
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        layout.add_widget(Label(text="Game Over! Here is the chain:", font_size='26sp', size_hint_y=0.1, bold=True))
        
        from kivy.uix.scrollview import ScrollView
        scroll_content = BoxLayout(orientation='vertical', size_hint_y=None, spacing=15)
        scroll_content.bind(minimum_height=scroll_content.setter('height'))
        
        for idx, item in enumerate(game_history):
            if idx % 2 == 0:
                label_text = f"Original Word: [b]{item}[/b]" if idx == 0 else f"Guess: [b]{item}[/b]"
                scroll_content.add_widget(Label(text=label_text, markup=True, font_size='18sp', size_hint_y=None, height=40))
            else:
                img = UIImage(size_hint_y=None, height=250, allow_stretch=True)
                img.texture = item
                scroll_content.add_widget(img)
                
        scroll = ScrollView()
        scroll.add_widget(scroll_content)
        layout.add_widget(scroll)
        
        restart_btn = Button(text="Main Menu", size_hint_y=0.1, font_size='18sp', background_color=BUTTON_BG, background_normal='')
        restart_btn.bind(on_press=self.go_to_menu)
        layout.add_widget(restart_btn)
        
        self.add_widget(layout)

    def go_to_menu(self, instance):
        self.manager.current = 'telestrations_menu'
