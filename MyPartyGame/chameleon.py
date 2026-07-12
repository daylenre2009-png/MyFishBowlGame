import random
import sys
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle
from kivy.clock import Clock

# Color Theme Constants
COLOR_BG = (0.102, 0.102, 0.118, 1)          
COLOR_BORDER = (0.247, 0.247, 0.275, 1)      
COLOR_BUTTON_BG = (0.180, 0.188, 0.337, 1)    

# Dynamic Game Bank - 30 Categories x 50 Words Each
WORD_BANK = {
    "Animals": [
        "Lion", "Elephant", "Shark", "Penguin", "Kangaroo", "Chameleon", "Eagle", "Dolphin", "Bear", "Snake",
        "Frog", "Giraffe", "Monkey", "Wolf", "Octopus", "Horse", "Tiger", "Owl", "Fox", "Crocodile"
    ],
    "Food & Drink": [
        "Pizza", "Burger", "Sushi", "Taco", "Ice Cream", "Coffee", "Chocolate", "Cheese", "Pasta", "Apple",
        "Bacon", "Salad", "Pancake", "Donut", "Steak", "Popcorn", "Smoothie", "Soup", "Fries", "Watermelon"
    ],
    "Occupations": [
        "Doctor", "Firefighter", "Astronaut", "Teacher", "Chef", "Detective", "Artist", "Pilot", "Scientist", "Farmer",
        "Lawyer", "Actor", "Musician", "Vet", "Builder", "Nurse", "Photographer", "Journalist", "Coach", "Mechanic"
    ],
    "Places & Destinations": [
        "Beach", "School", "Hospital", "Airport", "Library", "Gym", "Museum", "Cinema", "Hotel", "Park",
        "Zoo", "Castle", "Space Station", "Mall", "Restaurant", "Concert", "Desert", "Island", "Mountain", "Supermarket"
    ],
    "Clothing & Fashion": [
        "T-shirt", "Jeans", "Jacket", "Dress", "Sneakers", "Boots", "Hat", "Sunglasses", "Socks", "Scarf",
        "Gloves", "Suit", "Hoodie", "Watch", "Backpack", "Belt", "Sweater", "Swimsuit", "Ring", "Tie"
    ],
    "Hobbies & Sports": [
        "Soccer", "Basketball", "Video Games", "Reading", "Cooking", "Drawing", "Swimming", "Hiking", "Photography", "Dancing",
        "Gardening", "Chess", "Skateboarding", "Camping", "Fishing", "Running", "Yoga", "Tennis", "Cycling", "Painting"
    ],
    "Household Objects": [
        "Couch", "Refrigerator", "Television", "Lamp", "Clock", "Mirror", "Toaster", "Bed", "Pillow", "Towel",
        "Key", "Blender", "Broom", "Laptop", "Umbrella", "Desk", "Chair", "Fan", "Curtain", "Plant"
    ],
    "Transport & Vehicles": [
        "Car", "Airplane", "Bicycle", "Train", "Boat", "Helicopter", "Submarine", "Motorcycle", "Bus", "Rocket",
        "Scooter", "Truck", "Tractor", "Skateboard", "Ambulance", "Taxi", "Ferry", "Hot Air Balloon", "Jet Ski", "Spaceship"
    ],
    "Pop Culture & Media": [
        "Star Wars", "Marvel", "Harry Potter", "Pokémon", "Minecraft", "Batman", "Shrek", "Frozen", "Titanic", "Jurassic Park",
        "Disney", "Barbie", "Netflix", "YouTube", "Anime", "Spider-Man", "Mario", "LEGO", "Fortnite", "Avatar"
    ],
    "Weather & Nature": [
        "Sunshine", "Rain", "Snow", "Thunderstorm", "Rainbow", "Volcano", "Waterfall", "Tornado", "Fog", "Earthquake",
        "Blizzard", "Hurricane", "River", "Forest", "Cave", "Cloud", "Wind", "Lightning", "Wave", "Eclipse"
    ]
}

class GameState:
    def __init__(self):
        self.num_players = 4
        self.imposter_index = 0
        self.current_player = 0
        self.secret_word = ""
        self.category = ""
        self.timer_duration = 180  

    def setup_game(self):
        valid_categories = {k: v for k, v in WORD_BANK.items() if v}
        if not valid_categories:
            self.category = "Custom"
            self.secret_word = "No Words Available"
        else:
            self.category, words = random.choice(list(valid_categories.items()))
            self.secret_word = random.choice(words)
        
        self.imposter_index = random.randint(0, self.num_players - 1)
        self.current_player = 0

game_state = GameState()


class ThemedCard(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 20
        self.spacing = 15
        self.bind(pos=self.update_canvas, size=self.update_canvas)

    def update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*COLOR_BORDER)
            RoundedRectangle(pos=(self.x, self.y), size=(self.width, self.height), radius=[15])
            Color(*COLOR_BG)
            RoundedRectangle(pos=(self.x + 2, self.y + 2), size=(self.width - 4, self.height - 4), radius=[13])


class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        main_layout = BoxLayout(orientation='vertical', padding=30, spacing=20)
        
        card = ThemedCard(size_hint_y=0.75)
        
        title = Label(text="CHAMELEON\nIMPOSTER", font_size='34sp', bold=True, halign='center', color=(1, 1, 1, 1))
        card.add_widget(title)
        
        self.player_label = Label(text=f"Players: {game_state.num_players}", font_size='22sp', bold=True, color=(0.8, 0.8, 0.8, 1))
        card.add_widget(self.player_label)
        
        btn_layout = BoxLayout(orientation='horizontal', spacing=15, size_hint_y=None, height='55dp')
        
        btn_minus = Button(text="-", font_size='26sp', bold=True, background_color=(0,0,0,0), color=(1,1,1,1))
        btn_minus.bind(on_press=self.decrease_players)
        with btn_minus.canvas.before:
            Color(*COLOR_BUTTON_BG)
            self.rect_m = RoundedRectangle(radius=[8])
        btn_minus.bind(pos=lambda obj, pos: setattr(self.rect_m, 'pos', pos), size=lambda obj, size: setattr(self.rect_m, 'size', size))

        btn_plus = Button(text="+", font_size='26sp', bold=True, background_color=(0,0,0,0), color=(1,1,1,1))
        btn_plus.bind(on_press=self.increase_players)
        with btn_plus.canvas.before:
            Color(*COLOR_BUTTON_BG)
            self.rect_p = RoundedRectangle(radius=[8])
        btn_plus.bind(pos=lambda obj, pos: setattr(self.rect_p, 'pos', pos), size=lambda obj, size: setattr(self.rect_p, 'size', size))
        
        btn_layout.add_widget(btn_minus)
        btn_layout.add_widget(btn_plus)
        card.add_widget(btn_layout)
        
        main_layout.add_widget(card)
        
        bottom_layout = BoxLayout(orientation='horizontal', spacing=15, size_hint_y=0.15)
        
        btn_settings = Button(text="SETTINGS", font_size='16sp', bold=True, background_color=(0,0,0,0), color=(1, 1, 1, 1), size_hint_x=0.4)
        with btn_settings.canvas.before:
            Color(*COLOR_BUTTON_BG)
            self.rect_set = RoundedRectangle(radius=[12])
        btn_settings.bind(pos=lambda obj, pos: setattr(self.rect_set, 'pos', pos), size=lambda obj, size: setattr(self.rect_set, 'size', size))
        btn_settings.bind(on_press=self.go_to_settings)
        
        btn_start = Button(text="START MATCH", font_size='18sp', bold=True, background_color=(0,0,0,0), color=(1, 1, 1, 1), size_hint_x=0.6)
        with btn_start.canvas.before:
            Color(*COLOR_BUTTON_BG)
            self.rect_s = RoundedRectangle(radius=[12])
        btn_start.bind(pos=lambda obj, pos: setattr(self.rect_s, 'pos', pos), size=lambda obj, size: setattr(self.rect_s, 'size', size))
        btn_start.bind(on_press=self.start_game)
        
        bottom_layout.add_widget(btn_settings)
        bottom_layout.add_widget(btn_start)
        main_layout.add_widget(bottom_layout)
        
        # Add a custom back to launcher dashboard button
        btn_dashboard = Button(text="DASHBOARD", font_size='14sp', size_hint_y=None, height='40dp', background_color=COLOR_BUTTON_BG)
        btn_dashboard.bind(on_press=self.go_to_dashboard)
        main_layout.add_widget(btn_dashboard)
        
        self.add_widget(main_layout)

    def go_to_dashboard(self, instance):
        self.manager.current = "main_dashboard"

    def decrease_players(self, instance):
        if game_state.num_players > 3:
            game_state.num_players -= 1
            self.player_label.text = f"Players: {game_state.num_players}"

    def increase_players(self, instance):
        if game_state.num_players < 10:
            game_state.num_players += 1
            self.player_label.text = f"Players: {game_state.num_players}"

    def start_game(self, instance):
        game_state.setup_game()
        self.manager.get_screen('chameleon_pass').update_ui()
        self.manager.current = 'chameleon_pass'

    def go_to_settings(self, instance):
        self.manager.get_screen('chameleon_settings').update_ui()
        self.manager.current = 'chameleon_settings'


class SettingsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_category = list(WORD_BANK.keys())[0] if WORD_BANK else ""
        
        self.main_layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # --- TIMER CONFIG CARD ---
        timer_card = ThemedCard(size_hint_y=None, height="130dp")
        self.timer_label = Label(text="", font_size='18sp', bold=True, color=(1, 1, 1, 1))
        timer_card.add_widget(self.timer_label)
        
        t_btn_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height='45dp')
        btn_minus = Button(text="-30s", bold=True, background_color=(0,0,0,0))
        btn_minus.bind(on_press=self.decrease_timer)
        with btn_minus.canvas.before:
            Color(*COLOR_BUTTON_BG)
            self.r_tm = RoundedRectangle(radius=[8])
        btn_minus.bind(pos=lambda o, p: setattr(self.r_tm, 'pos', p), size=lambda o, s: setattr(self.r_tm, 'size', s))

        btn_plus = Button(text="+30s", bold=True, background_color=(0,0,0,0))
        btn_plus.bind(on_press=self.increase_timer)
        with btn_plus.canvas.before:
            Color(*COLOR_BUTTON_BG)
            self.r_tp = RoundedRectangle(radius=[8])
        btn_plus.bind(pos=lambda o, p: setattr(self.r_tp, 'pos', p), size=lambda o, s: setattr(self.r_tp, 'size', s))
        
        t_btn_layout.add_widget(btn_minus)
        t_btn_layout.add_widget(btn_plus)
        timer_card.add_widget(t_btn_layout)
        self.main_layout.add_widget(timer_card)
        
        # --- CATEGORY MANAGER CARD ---
        self.bank_card = ThemedCard(size_hint_y=0.75)
        self.main_layout.add_widget(self.bank_card)
        
        # --- FOOTER BUTTON ---
        btn_back = Button(text="SAVE & CLOSE", font_size='18sp', bold=True, background_color=(0,0,0,0), size_hint_y=None, height="55dp")
        with btn_back.canvas.before:
            Color(*COLOR_BUTTON_BG)
            self.rect_b = RoundedRectangle(radius=[12])
        btn_back.bind(pos=lambda obj, pos: setattr(self.rect_b, 'pos', pos), size=lambda obj, size: setattr(self.rect_b, 'size', size))
        btn_back.bind(on_press=self.exit_to_master_menu)
        self.main_layout.add_widget(btn_back)
        
        self.add_widget(self.main_layout)

    def update_ui(self):
        minutes = game_state.timer_duration // 60
        seconds = game_state.timer_duration % 60
        self.timer_label.text = f"Discussion Time: {minutes:02d}:{seconds:02d}"
        
        self.bank_card.clear_widgets()
        split_layout = BoxLayout(orientation='horizontal', spacing=15)
        
        # Left Panel: List of Categories
        left_panel = BoxLayout(orientation='vertical', spacing=10, size_hint_x=0.4)
        left_panel.add_widget(Label(text="Categories", bold=True, size_hint_y=None, height="30dp"))
        
        cat_scroll = ScrollView()
        cat_list = GridLayout(cols=1, spacing=5, size_hint_y=None)
        cat_list.bind(minimum_height=cat_list.setter('height'))
        
        for cat in WORD_BANK.keys():
            is_selected = (cat == self.selected_category)
            bg_color = (0.25, 0.26, 0.45, 1) if is_selected else COLOR_BUTTON_BG
            
            btn = Button(text=cat, size_hint_y=None, height="40dp", background_color=(0,0,0,0), color=(1,1,1,1))
            btn.cat_name = cat
            btn.bind(on_press=self.select_category)
            with btn.canvas.before:
                Color(*bg_color)
                btn.rect = RoundedRectangle(size=btn.size, pos=btn.pos, radius=[6])
            btn.bind(pos=lambda o, p: setattr(o.rect, 'pos', p), size=lambda o, s: setattr(o.rect, 'size', s))
            cat_list.add_widget(btn)
            
        cat_scroll.add_widget(cat_list)
        left_panel.add_widget(cat_scroll)
        
        new_cat_input = TextInput(hint_text="New Cat...", text_validate_unfocus=False, multiline=False, size_hint_y=None, height="35dp", background_color=(0.08,0.08,0.09,1), foreground_color=(1,1,1,1))
        new_cat_input.bind(on_text_validate=self.add_category)
        left_panel.add_widget(new_cat_input)
        
        # Right Panel: List of words & Multi-line submission
        right_panel = BoxLayout(orientation='vertical', spacing=10, size_hint_x=0.6)
        right_panel.add_widget(BoxLayout(orientation='horizontal', size_hint_y=None, height="30dp"))
        right_panel.children[0].add_widget(Label(text=f"Words ({len(WORD_BANK[self.selected_category]) if self.selected_category in WORD_BANK else 0})", bold=True, halign='left'))
        
        if self.selected_category:
            del_cat_btn = Button(text="Delete Cat", size_hint_x=None, width="80dp", background_color=(0.4, 0.15, 0.15, 1))
            del_cat_btn.bind(on_press=self.delete_category)
            right_panel.children[0].add_widget(del_cat_btn)

        word_scroll = ScrollView(size_hint_y=0.6)
        word_grid = GridLayout(cols=1, spacing=5, size_hint_y=None)
        word_grid.bind(minimum_height=word_grid.setter('height'))
        
        if self.selected_category and self.selected_category in WORD_BANK:
            for word in WORD_BANK[self.selected_category]:
                w_row = BoxLayout(orientation='horizontal', size_hint_y=None, height="35dp", spacing=5)
                w_label = Label(text=word, halign='left', size_hint_x=0.8)
                
                del_w_btn = Button(text="X", size_hint_x=0.2, background_color=(0,0,0,0), color=(0.9,0.3,0.3,1), bold=True)
                del_w_btn.word_val = word
                del_w_btn.bind(on_press=self.delete_word)
                with del_w_btn.canvas.before:
                    Color(*COLOR_BUTTON_BG)
                    del_w_btn.rect = RoundedRectangle(radius=[4])
                del_w_btn.bind(pos=lambda o, p: setattr(o.rect, 'pos', p), size=lambda o, s: setattr(o.rect, 'size', s))
                
                w_row.add_widget(w_label)
                w_row.add_widget(del_w_btn)
                word_grid.add_widget(w_row)
                
        word_scroll.add_widget(word_grid)
        right_panel.add_widget(word_scroll)
        
        right_panel.add_widget(Label(text="Add Word(s) - One Per Line:", size_hint_y=None, height="20dp", font_size="12sp", color=(0.7,0.7,0.7,1)))
        
        self.bulk_word_input = TextInput(
            hint_text="Word1\nWord2\nWord3...", 
            multiline=True, 
            size_hint_y=0.3, 
            background_color=(0.08,0.08,0.09,1), 
            foreground_color=(1,1,1,1)
        )
        right_panel.add_widget(self.bulk_word_input)
        
        btn_submit_words = Button(text="Add Words", bold=True, size_hint_y=None, height="35dp", background_color=(0,0,0,0))
        with btn_submit_words.canvas.before:
            Color(*COLOR_BUTTON_BG)
            btn_submit_words.rect = RoundedRectangle(radius=[6])
        btn_submit_words.bind(pos=lambda o, p: setattr(o.rect, 'pos', p), size=lambda o, s: setattr(o.rect, 'size', s))
        btn_submit_words.bind(on_press=self.add_bulk_words)
        right_panel.add_widget(btn_submit_words)
        
        split_layout.add_widget(left_panel)
        split_layout.add_widget(right_panel)
        self.bank_card.add_widget(split_layout)

    def select_category(self, instance):
        self.selected_category = instance.cat_name
        self.update_ui()

    def add_category(self, instance):
        name = instance.text.strip()
        if name and name not in WORD_BANK:
            WORD_BANK[name] = []
            self.selected_category = name
        self.update_ui()

    def delete_category(self, instance):
        if self.selected_category in WORD_BANK:
            del WORD_BANK[self.selected_category]
            self.selected_category = list(WORD_BANK.keys())[0] if WORD_BANK else ""
        self.update_ui()

    def add_bulk_words(self, instance):
        if not self.selected_category or self.selected_category not in WORD_BANK:
            return
            
        raw_text = self.bulk_word_input.text
        lines = raw_text.split('\n')
        
        for line in lines:
            clean_word = line.strip()
            if clean_word and clean_word not in WORD_BANK[self.selected_category]:
                WORD_BANK[self.selected_category].append(clean_word)
                
        self.bulk_word_input.text = ""
        self.update_ui()

    def delete_word(self, instance):
        target_word = instance.word_val
        if self.selected_category in WORD_BANK and target_word in WORD_BANK[self.selected_category]:
            WORD_BANK[self.selected_category].remove(target_word)
        self.update_ui()

    def decrease_timer(self, instance):
        if game_state.timer_duration > 30:
            game_state.timer_duration -= 30
            self.update_ui()

    def increase_timer(self, instance):
        if game_state.timer_duration < 600:
            game_state.timer_duration += 30
            self.update_ui()

    def exit_to_master_menu(self, instance):
        self.manager.current = 'chameleon_menu'

class PassScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        main_layout = BoxLayout(orientation='vertical', padding=30, spacing=20)
        
        self.card = ThemedCard(size_hint_y=0.7)
        self.instruction_label = Label(text="", font_size='22sp', halign='center', color=(1, 1, 1, 1), markup=True)
        self.card.add_widget(self.instruction_label)
        main_layout.add_widget(self.card)
        
        self.action_btn = Button(text="REVEAL MY ROLE", font_size='20sp', bold=True, background_color=(0,0,0,0), color=(1, 1, 1, 1), size_hint_y=0.15)
        with self.action_btn.canvas.before:
            Color(*COLOR_BUTTON_BG)
            self.rect_a = RoundedRectangle(radius=[12])
        self.action_btn.bind(pos=lambda obj, pos: setattr(self.rect_a, 'pos', pos), size=lambda obj, size: setattr(self.rect_a, 'size', size))
        
        main_layout.add_widget(self.action_btn)
        self.add_widget(main_layout)

    def update_ui(self):
        self.instruction_label.text = f"Pass the device to\n\n[b]Player {game_state.current_player + 1}[/b]"
        self.action_btn.text = "REVEAL MY ROLE"
        self.action_btn.unbind(on_press=self.next_player)
        self.action_btn.bind(on_press=self.reveal_role)

    def reveal_role(self, instance):
        if game_state.current_player == game_state.imposter_index:
            role_text = f"Category: [b]{game_state.category}[/b]\n\n\n[b]YOU ARE THE IMPOSTER![/b]\n\nBlend in, don't get caught."
        else:
            role_text = f"Category: [b]{game_state.category}[/b]\n\n\nSecret Word:\n[b]{game_state.secret_word}[/b]"
        
        self.instruction_label.text = role_text
        self.action_btn.text = "I UNDERSTAND"
        self.action_btn.unbind(on_press=self.reveal_role)
        self.action_btn.bind(on_press=self.next_player)

    def next_player(self, instance):
        game_state.current_player += 1
        if game_state.current_player < game_state.num_players:
            self.update_ui()
        else:
            self.manager.get_screen('chameleon_discussion').start_discussion()
            self.manager.current = 'chameleon_discussion'


class DiscussionScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.main_layout = BoxLayout(orientation='vertical', padding=30, spacing=20)
        
        self.card = ThemedCard(size_hint_y=0.7)
        self.info_label = Label(text="", font_size='18sp', halign='center', color=(1, 1, 1, 1), markup=True)
        self.card.add_widget(self.info_label)
        self.main_layout.add_widget(self.card)
        
        self.button_container = BoxLayout(orientation='horizontal', spacing=15, size_hint_y=0.15)
        
        self.reveal_btn = Button(text="REVEAL IMPOSTER", font_size='20sp', bold=True, background_color=(0,0,0,0), color=(1, 1, 1, 1))
        with self.reveal_btn.canvas.before:
            Color(*COLOR_BUTTON_BG)
            self.rect_d = RoundedRectangle(radius=[12])
        self.reveal_btn.bind(pos=lambda obj, pos: setattr(self.rect_d, 'pos', pos), size=lambda obj, size: setattr(self.rect_d, 'size', size))
        
        self.button_container.add_widget(self.reveal_btn)
        self.main_layout.add_widget(self.button_container)
        self.add_widget(self.main_layout)
        self.time_left = 0

    def start_discussion(self):
        self.time_left = game_state.timer_duration
        
        self.button_container.clear_widgets()
        self.button_container.add_widget(self.reveal_btn)
        
        self.reveal_btn.unbind(on_press=self.back_to_menu)
        self.reveal_btn.bind(on_press=self.reveal_imposter)
        self.update_timer_text()
        
        Clock.unschedule(self.tick_timer)
        Clock.schedule_interval(self.tick_timer, 1)

    def update_timer_text(self):
        minutes = self.time_left // 60
        seconds = self.time_left % 60
        self.info_label.text = f"[b]DISCUSSION TIME[/b]\n\n[size=40sp]{minutes:02d}:{seconds:02d}[/size]\n\nTake turns saying [b]ONE[/b] word related to the \n\n secret category ([b]{game_state.category}[/b]), then vote!"

    def tick_timer(self, dt):
        if self.time_left > 0:
            self.time_left -= 1
            self.update_timer_text()
        else:
            Clock.unschedule(self.tick_timer)
            self.info_label.text = "[b]TIME'S UP![/b]\n\nDiscussion period over.\nCast your final votes now!"

    def reveal_imposter(self, instance):
        Clock.unschedule(self.tick_timer)
        self.info_label.text = f"The Imposter was:\n[b]Player {game_state.imposter_index + 1}[/b]\n\n\nThe secret word was:\n[b]{game_state.secret_word}[/b]"
        
        self.button_container.clear_widgets()
        
        btn_main_menu = Button(text="MAIN MENU", font_size='16sp', bold=True, background_color=(0,0,0,0), color=(1, 1, 1, 1))
        with btn_main_menu.canvas.before:
            Color(*COLOR_BUTTON_BG)
            rect_mm = RoundedRectangle(radius=[12])
        btn_main_menu.bind(pos=lambda obj, pos: setattr(rect_mm, 'pos', pos), size=lambda obj, size: setattr(rect_mm, 'size', size))
        btn_main_menu.bind(on_press=self.back_to_menu)
        
        btn_play_again = Button(text="PLAY AGAIN", font_size='16sp', bold=True, background_color=(0,0,0,0), color=(1, 1, 1, 1))
        with btn_play_again.canvas.before:
            Color(*COLOR_BUTTON_BG)
            rect_pa = RoundedRectangle(radius=[12])
        btn_play_again.bind(pos=lambda obj, pos: setattr(rect_pa, 'pos', pos), size=lambda obj, size: setattr(rect_pa, 'size', size))
        btn_play_again.bind(on_press=self.play_again)
        
        self.button_container.add_widget(btn_main_menu)
        self.button_container.add_widget(btn_play_again)

    def back_to_menu(self, instance):
        self.manager.current = "main_dashboard"

    def play_again(self, instance):
        game_state.setup_game()
        self.manager.get_screen('chameleon_pass').update_ui()
        self.manager.current = 'chameleon_pass'
