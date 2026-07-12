import os
import random
from typing import List, Dict
import sys

os.environ['KIVY_NO_INPUT'] = '1'

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image as KivyImage
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.dropdown import DropDown
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.core.text import Label as CoreLabel  
from kivy.graphics import Color, Rectangle, Line
from kivy.metrics import dp

# Dynamic import configuration links
import chameleon
import Telestrations

# ==========================================
# CONSTANTS & CONFIGURATION (THEMING)
# ==========================================
COLOR_BG = (0.102, 0.102, 0.118, 1)          
COLOR_BARREL_BG = (0.145, 0.145, 0.161, 1)   
COLOR_BORDER = (0.247, 0.247, 0.275, 1)      
COLOR_ACCENT_BLUE = (0.388, 0.400, 0.945, 1)  
COLOR_ACCENT_GREEN = (0.063, 0.725, 0.506, 1) 
COLOR_ACCENT_PURPLE = (0.658, 0.356, 0.945, 1)
COLOR_ACCENT_ORANGE = (0.960, 0.501, 0.121, 1)
COLOR_BUTTON_BG = (0.180, 0.188, 0.337, 1)    

GAME_DATA_POOLS = {
    "words": [
        "Astronaut (Space, Rocket, Moon, Suit, NASA)", "Apple (Fruit, Red, Tree, Crisp, Pie)", 
        "Airplane (Fly, Sky, Airport, Wings, Pilot)", "Alien (Space, UFO, Green, Planet, Martian)", 
        "Anchor (Ship, Boat, Sea, Heavy, Water)", "Backpack (School, Bag, Straps, Books, Carry)", 
        "Bicycle (Wheels, Pedals, Ride, Helmet, Chain)", "Blender (Kitchen, Smoothie, Mix, Fruit, Ice)", 
        "Bear (Woods, Forest, Hibernate, Teddy, Animal)", "Banana (Fruit, Yellow, Peel, Monkey, Bunch)"
    ],
    "actions": [
        "Playing rock-paper-scissors", "Defusing a time bomb", "Walking through sand dunes", 
        "Sewing a rip in a jacket", "Pouring a glass of water carefully", "Washing a dirty car"
    ],
    "categories": [
        "A Boy's Name", "A Girl's Name", "Animals", "Things That Are Cold", 
        "Insects", "TV Shows", "Items In A Refrigerator", "Street Names"
    ],
    "letters": ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"],
    "vowels": ["A", "E", "I", "O", "U", "Y"]
}

class SilentImage(KivyImage):
    def on_image_error(self, *args) -> bool:
        self.texture = None
        return True

class BarrelSpinner(Widget):
    def __init__(self, title: str, options: List[str], accent_color: tuple, on_finish_callback, **kwargs):
        super().__init__(**kwargs)
        self.title = title
        self.options = options
        self.accent_color = accent_color
        self.on_finish_callback = on_finish_callback
        
        self.y_offset = 0.0
        self.speed = 0.0
        self.is_spinning = False
        self.row_height = dp(38)
        
        self.bind(size=self._redraw, pos=self._redraw)
        
    def _redraw(self, *args):
        if self.height <= 0 or self.width <= 0 or not self.options:
            return
            
        self.canvas.clear()

        with self.canvas:
            Color(*COLOR_BARREL_BG)
            Rectangle(pos=self.pos, size=self.size)
            
            Color(*COLOR_BORDER)
            Line(rectangle=(self.x, self.y, self.width, self.height), width=1)
            
            cx = self.x + self.width / 2
            cy = self.y + self.height / 2
            num_opts = len(self.options)
            
            for i in range(-2, 3):
                item_index = (int(self.y_offset // self.row_height) + i) % num_opts
                exact_y = cy + (i * self.row_height) - (self.y_offset % self.row_height)
                
                if exact_y < self.y or exact_y > self.y + self.height:
                    continue
                    
                dist_from_center = abs(exact_y - cy)
                ratio = max(0, 1 - (dist_from_center / (self.height / 2)))
                
                if ratio > 0.1:
                    if abs(exact_y - cy) < self.row_height / 2:
                        text_color = (1, 1, 1, 1)
                    else:
                        text_color = (0.6, 0.6, 0.6, float(ratio))
                    
                    display_string = self.options[item_index]
                    max_chars = max(10, int(self.width / (dp(12) * 0.58)))
                    if len(display_string) > max_chars:
                        display_string = display_string[:max_chars - 3] + "..."
                    
                    font_sz = dp(13) + (dp(3) * ratio)
                    
                    lbl = CoreLabel(text=display_string, font_name="Roboto", font_size=font_sz,
                                    color=text_color, bold=(ratio > 0.7))
                    lbl.refresh()
                    
                    Color(1, 1, 1, text_color[3])
                    Rectangle(texture=lbl.texture, 
                              pos=(cx - lbl.texture.size[0]/2, exact_y - lbl.texture.size[1]/2), 
                              size=lbl.texture.size)

            Color(*self.accent_color)
            box_half_h = self.row_height * 0.55
            Line(rectangle=(self.x + dp(4), cy - box_half_h, self.width - dp(8), box_half_h * 2), width=2)

    def on_touch_down(self, touch) -> bool:
        if self.collide_point(*touch.pos) and not self.is_spinning:
            if self.options:
                app = App.get_running_app()
                if app.spinner_sound:
                    app.spinner_sound.play()
                    
                self.is_spinning = True
                self.speed = random.uniform(30, 50)
                Clock.schedule_interval(self.animate, 1/60.0)
            return True
        return super().on_touch_down(touch)

    def animate(self, dt: float):
        if self.speed > 0.4:
            self.y_offset += self.speed
            self.speed *= 0.965
            self._redraw()
        else:
            remainder = self.y_offset % self.row_height
            if remainder != 0:
                if remainder > (self.row_height / 2):
                    self.y_offset += (self.row_height - remainder)
                else:
                    self.y_offset -= remainder
            
            self.is_spinning = False
            Clock.unschedule(self.animate)
            self._redraw()
            
            num_opts = len(self.options)
            winning_index = int(self.y_offset // self.row_height) % num_opts
            self.on_finish_callback(self.options[winning_index])


class CardAndWheelScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_round_num = 1
        self.card_flips_count = 0
        self.flips_target_limit = 5  

        self.options1 = GAME_DATA_POOLS["words"]
        self.options2 = GAME_DATA_POOLS["actions"]
        self.options3 = GAME_DATA_POOLS["categories"]
        self.options4 = GAME_DATA_POOLS["letters"]
        self.options5 = GAME_DATA_POOLS["vowels"]

        self.round_descriptions = {1: "Round 1: Talk!", 2: "Round 2: Act!", 3: "Round 3: Draw!"}
        self.card_back_path = "assets/sprites/back.png"
        self.card_pool1 = ["assets/sprites/0.png", "assets/sprites/1.png", "assets/sprites/8.png"]
        self.card_pool2 = ["assets/sprites/6.png", "assets/sprites/7.png"]
        self.card_pool3 = ["assets/sprites/2.png", "assets/sprites/3.png", "assets/sprites/4.png", "assets/sprites/5.png"]

        self.root_layout = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(8))
        with self.root_layout.canvas.before:
            Color(*COLOR_BG)
            self.bg_rect = Rectangle(pos=self.root_layout.pos, size=self.root_layout.size)
        self.root_layout.bind(pos=self._update_bg, size=self._update_bg)

        self._build_top_navbar()
        self._build_main_gameplay_views()
        self._build_status_footer()
        self.add_widget(self.root_layout)

    def _build_top_navbar(self):
        self.top_nav = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40), spacing=dp(10))
        self.my_games_btn = Button(text="My Games", font_size='12sp', bold=True, size_hint_x=None, width=dp(110),
                                   background_normal='', background_color=COLOR_BUTTON_BG, color=(1,1,1,1))
        
        self.games_dropdown = DropDown()
        for item in ["Dashboard", "Telestrations", "Chameleon"]:
            btn = Button(text=item, size_hint_y=None, height=dp(35), font_size='12sp',
                         background_normal='', background_color=COLOR_BARREL_BG, color=(0.9, 0.9, 0.9, 1))
            btn.bind(on_release=lambda btn_obj: self.games_dropdown.select(btn_obj.text))
            self.games_dropdown.add_widget(btn)
            
        self.my_games_btn.bind(on_release=self.games_dropdown.open)
        self.games_dropdown.bind(on_select=self.handle_game_selection)
        
        self.menu_btn = Button(text="Settings", font_size='14sp', bold=True, size_hint_x=None, width=dp(100),
                               background_normal='', background_color=COLOR_BUTTON_BG, color=(1,1,1,1))
        self.menu_btn.bind(on_release=self.open_prompt_editor)
        
        self.top_nav.add_widget(self.my_games_btn)
        self.top_nav.add_widget(Widget())
        self.top_nav.add_widget(self.menu_btn)
        self.root_layout.add_widget(self.top_nav)

    def _build_main_gameplay_views(self):
        self.main_container = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=1.0)
        self.root_layout.bind(size=self.adjust_layout_orientation)

        self.card_layout_block = BoxLayout(orientation='vertical', size_hint_y=0.35, spacing=dp(4))
        self.round_header_label = Label(text=self.get_round_string_meta(), font_size='11sp', bold=True,
                                        color=COLOR_ACCENT_ORANGE, size_hint_y=None, height=dp(18), halign='center')
        self.card_layout_block.add_widget(self.round_header_label)

        self.card_anchor = AnchorLayout(anchor_x='center', anchor_y='center')
        initial_card = self.card_back_path if os.path.exists(self.card_back_path) else ''
        self.card_img = SilentImage(source=initial_card, allow_stretch=True, keep_ratio=True, 
                                    size_hint=(None, None), size=(dp(140), dp(180)))
        self.card_img.bind(on_touch_down=self.handle_card_click)
        self.card_anchor.add_widget(self.card_img)
        self.card_layout_block.add_widget(self.card_anchor)

        self.barrels_container = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=0.65)
        
        self.barrel1 = BarrelSpinner("Words", self.options1, COLOR_ACCENT_BLUE, self.update_winner_1)
        self.barrel2 = BarrelSpinner("Action", self.options2, COLOR_ACCENT_GREEN, self.update_winner_2)
        self.barrel3 = BarrelSpinner("Categories", self.options3, COLOR_ACCENT_PURPLE, self.update_winner_3)
        self.barrel4 = BarrelSpinner("Letters", self.options4, COLOR_ACCENT_ORANGE, self.update_winner_4)
        self.barrel5 = BarrelSpinner("Vowels", self.options5, COLOR_ACCENT_BLUE, self.update_winner_5)

        self.barrels_container.add_widget(self._create_labeled_wrapper("Words", COLOR_ACCENT_BLUE, self.barrel1))
        self.barrels_container.add_widget(self._create_labeled_wrapper("Action", COLOR_ACCENT_GREEN, self.barrel2))
        self.barrels_container.add_widget(self._create_labeled_wrapper("Categories", COLOR_ACCENT_PURPLE, self.barrel3))

        split_row = BoxLayout(orientation='horizontal', spacing=dp(10))
        split_row.add_widget(self._create_labeled_wrapper("Letters", COLOR_ACCENT_ORANGE, self.barrel4))
        split_row.add_widget(self._create_labeled_wrapper("Vowels", COLOR_ACCENT_BLUE, self.barrel5))
        self.barrels_container.add_widget(split_row)

        self.main_container.add_widget(self.card_layout_block)
        self.main_container.add_widget(self.barrels_container)
        self.root_layout.add_widget(self.main_container)

    def _build_status_footer(self):
        self.output_label = Label(text="Play a card and spin the barrels!", font_size='13sp', bold=True,
                                  color=(1,1,1,1), size_hint_y=None, height=dp(40), halign='center', valign='middle')
        self.output_label.bind(size=lambda i, v: setattr(i, 'text_size', (i.width, None)))
        self.root_layout.add_widget(self.output_label)
        self.game_over_view = None

    def _create_labeled_wrapper(self, label_text: str, accent_color: tuple, widget_element: Widget) -> BoxLayout:
        wrapper = BoxLayout(orientation='vertical', spacing=dp(2))
        lbl = Label(text=label_text, font_size='9sp', bold=True, color=accent_color, size_hint_y=None, height=dp(12), halign='left')
        lbl.bind(size=lambda i, v: setattr(i, 'text_size', (i.width, None)))
        wrapper.add_widget(lbl)
        wrapper.add_widget(widget_element)
        return wrapper

    def handle_game_selection(self, instance, game_title: str):
        if game_title == "Dashboard":
            self.manager.current = "main_dashboard"
        elif game_title == "Telestrations":
            self.manager.current = "telestrations_menu"
        elif game_title == "Chameleon":
            self.manager.current = "chameleon_menu"

    def get_round_string_meta(self) -> str:
        desc = self.round_descriptions.get(self.current_round_num, "Game Session Completed!")
        remaining = self.flips_target_limit - self.card_flips_count
        return f"{desc}  |  ({remaining} Flips Left)"

    def _update_bg(self, instance, value):
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size

    def adjust_layout_orientation(self, instance, size: List[float]):
        if self.current_round_num > 3:
            return  
        barrels = [self.barrel1, self.barrel2, self.barrel3, self.barrel4, self.barrel5]
        for b in barrels:
            b.canvas.clear()
            Clock.schedule_once(lambda dt, b_obj=b: b_obj._redraw())

        width, height = size
        if width > height:
            self.main_container.orientation = 'horizontal'
            self.card_layout_block.size_hint = (0.32, 1)
            self.barrels_container.size_hint = (0.68, 1)
            self.card_img.size = (height * 0.35, height * 0.46)
        else:
            self.main_container.orientation = 'vertical'
            self.card_layout_block.size_hint = (1, 0.33)
            self.barrels_container.size_hint = (1, 0.67)
            self.card_img.size = (dp(140), dp(180))

    def handle_card_click(self, instance, touch) -> bool:
        if instance.collide_point(*touch.pos):
            pool_mapping = {1: self.card_pool1, 2: self.card_pool2, 3: self.card_pool3}
            active_pool = pool_mapping.get(self.current_round_num, self.card_pool1)
            valid_pool = [p for p in active_pool if os.path.exists(p)]
            
            app = App.get_running_app()
            if app.card_sound:
                app.card_sound.play()
                
            if valid_pool:
                instance.source = random.choice(valid_pool)
            
            self.card_flips_count += 1
            if self.card_flips_count >= self.flips_target_limit:
                self.card_flips_count = 0
                self.current_round_num += 1
                if self.current_round_num > 3:
                    self.show_game_over_screen()
                    return True
            
            self.round_header_label.text = self.get_round_string_meta()
            return True
        return False

    def show_game_over_screen(self):
        self.root_layout.remove_widget(self.main_container)
        self.root_layout.remove_widget(self.output_label)
        self.menu_btn.disabled = True  
        self.my_games_btn.disabled = True

        self.game_over_view = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15), size_hint_y=1.0)
        go_title = Label(text="GAME OVER!", font_size='28sp', bold=True, color=COLOR_ACCENT_ORANGE, size_hint_y=0.4, halign='center')
        go_desc = Label(text="All three gameplay rounds have been successfully finished.", font_size='13sp', color=(0.8, 0.8, 0.8, 1), size_hint_y=0.2, halign='center')
        
        restart_anchor = AnchorLayout(anchor_x='center', anchor_y='center', size_hint_y=0.4)
        restart_btn = Button(text="Start Again", size_hint=(None, None), size=(dp(160), dp(45)),
                             font_size='14sp', bold=True, background_normal='', background_color=COLOR_ACCENT_GREEN)
        restart_btn.bind(on_release=self.reset_game_session)
        restart_anchor.add_widget(restart_btn)

        self.game_over_view.add_widget(go_title)
        self.game_over_view.add_widget(go_desc)
        self.game_over_view.add_widget(restart_anchor)
        self.root_layout.add_widget(self.game_over_view)

    def reset_game_session(self, instance):
        self.current_round_num = 1
        self.card_flips_count = 0
        if self.game_over_view:
            self.root_layout.remove_widget(self.game_over_view)
            self.game_over_view = None
            
        self.menu_btn.disabled = False
        self.my_games_btn.disabled = False
        
        initial_card = self.card_back_path if os.path.exists(self.card_back_path) else ''
        self.card_img.source = initial_card
        self.round_header_label.text = self.get_round_string_meta()
        self.output_label.text = "Spin a barrel drum to see your prompt!"
        
        self.root_layout.add_widget(self.main_container)
        self.root_layout.add_widget(self.output_label)
        self.adjust_layout_orientation(self.root_layout, self.root_layout.size)

    def update_winner_1(self, res: str): self.output_label.text = f"Words: {res}"
    def update_winner_2(self, res: str): self.output_label.text = f"Action: {res}"
    def update_winner_3(self, res: str): self.output_label.text = f"Categories: {res}"
    def update_winner_4(self, res: str): self.output_label.text = f"Letters: {res}"
    def update_winner_5(self, res: str): self.output_label.text = f"Vowels: {res}"

    def open_prompt_editor(self, instance):
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(6))
        txt_limit = TextInput(text=str(self.flips_target_limit), input_filter='int', multiline=False)
        content.add_widget(Label(text="Card Flips Per Round:"))
        content.add_widget(txt_limit)
        
        popup = Popup(title='Quick Settings', content=content, size_hint=(0.8, 0.4))
        save_btn = Button(text="Save", background_color=COLOR_ACCENT_GREEN)
        
        def save(el):
            try: self.flips_target_limit = int(txt_limit.text)
            except: pass
            self.round_header_label.text = self.get_round_string_meta()
            popup.dismiss()
            
        save_btn.bind(on_release=save)
        content.add_widget(save_btn)
        popup.open()


class UnifiedCardAndWheelApp(App):
    def build(self) -> ScreenManager:
        self.title = "Interactive Boardgame Companion"
        
        self.card_sound = SoundLoader.load("assets/Sounds/flip.mp3")
        self.spinner_sound = SoundLoader.load("assets/Sounds/spin.mp3")

        sm = ScreenManager()
        
        # 1. Main Dashboard
        sm.add_widget(CardAndWheelScreen(name="main_dashboard"))
        
        # 2. Telestrations Screens
        sm.add_widget(Telestrations.MainMenu(name='telestrations_menu'))
        sm.add_widget(Telestrations.DrawScreen(name='telestrations_draw_screen'))
        sm.add_widget(Telestrations.GuessScreen(name='telestrations_guess_screen'))
        sm.add_widget(Telestrations.EndScreen(name='telestrations_end_screen'))
        
        # 3. Chameleon Screens
        sm.add_widget(chameleon.MenuScreen(name='chameleon_menu'))
        sm.add_widget(chameleon.SettingsScreen(name='chameleon_settings'))
        sm.add_widget(chameleon.PassScreen(name='chameleon_pass'))
        sm.add_widget(chameleon.DiscussionScreen(name='chameleon_discussion'))
        
        return sm

if __name__ == "__main__":
    UnifiedCardAndWheelApp().run()
