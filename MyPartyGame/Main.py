import os
import random
from typing import List, Dict
import sys
import subprocess

# CRITICAL: This environment variable bypasses the broken Mac touch provider 
# on Python 3.13+ and falls back to standard mouse clicks.
from kivy.utils import platform
if platform in ('macosx', 'win', 'linux'):
    os.environ['KIVY_NO_INPUT'] = '1'

from kivy.app import App
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

# ==========================================
# CONSTANTS & CONFIGURATION (THEMING)
# ==========================================
COLOR_BG = (0.102, 0.102, 0.118, 1)          # #1A1A1E
COLOR_BARREL_BG = (0.145, 0.145, 0.161, 1)   # #252529
COLOR_BORDER = (0.247, 0.247, 0.275, 1)      # #3F3F46
COLOR_ACCENT_BLUE = (0.388, 0.400, 0.945, 1)  # #6366F1
COLOR_ACCENT_GREEN = (0.063, 0.725, 0.506, 1) # #10B981
COLOR_ACCENT_PURPLE = (0.658, 0.356, 0.945, 1)# #A855F7
COLOR_ACCENT_ORANGE = (0.960, 0.501, 0.121, 1)# #F97316
COLOR_BUTTON_BG = (0.180, 0.188, 0.337, 1)    # #2E3056

# Global Game Assets
GAME_DATA_POOLS = {
    "words": [
        "Car (Drive, Wheels, Road, Engine, Transport)", "Diamond (Gem, Ring, Shiny, Expensive, Crystal)", 
        "Butterfly (Wings, Insect, Cocoon, Fly, Colorful)", "Doctor (Hospital, Medicine, Sick, Health, Stethoscope)", 
        "Bridge (River, Cross, Road, Water, Over)", "Robot (Machine, Metal, Future, AI, Gears)", 
        "Camera (Photo, Lens, Flash, Picture, Shoot)", "Dinosaur (Fossil, Bones, Ancient, T-Rex, Extinct)", 
        "Axe (Wood, Chop, Tool, Sharp, Tree)", "Submarine (Underwater, Ocean, Sonar, Navy, Deep)", 
        "Feather (Bird, Wing, Light, Soft, Pen)", "Clock (Time, Hours, Minutes, Tick, Watch)", 
        "Cactus (Desert, Plant, Spikes, Green, Sand)", "Elephant (Trunk, Large, Tusks, Africa, Animal)", 
        "Mirror (Reflection, Glass, Look, Wall, Face)", "Cigarette (Smoke, Ash, Fire, Tobacco, Puff)", 
        "Ocean (Water, Sea, Fish, Waves, Blue)", "Glove (Hand, Winter, Warm, Fingers, Wear)", 
        "Broom (Sweep, Clean, Floor, Witch, Dust)", "Backpack (School, Bag, Straps, Books, Carry)", 
        "Frog (Green, Jump, Pond, Toad, Croak)", "Pillow (Bed, Sleep, Head, Soft, Night)", 
        "Coffee (Drink, Morning, Mug, Caffeine, Beans)", "Bear (Woods, Forest, Hibernate, Teddy, Animal)", 
        "Onion (Vegetable, Cry, Layers, Cook, Ring)", "Castle (King, Queen, Fort, Stone, Moat)", 
        "Shark (Ocean, Teeth, Fin, Swim, Predator)", "Airplane (Fly, Sky, Airport, Wings, Pilot)", 
        "Bee (Honey, Buzz, Insect, Sting, Yellow)", "Volcano (Lava, Magma, Mountain, Erupt, Ash)", 
        "Moneym (Cash, Dollar, Wallet, Buy, Coin)", "Iceberg (Cold, Ocean, Titanic, Glacier, Frozen)", 
        "Computer (Screen, Keyboard, Mouse, Internet, Tech)", "Helicopter (Fly, Blades, Sky, Chopper, Pilot)", 
        "Cat (Meow, Purr, Pet, Whiskers, Feline)", "Astronaut (Space, Rocket, Moon, Suit, NASA)", 
        "Telescope (Stars, Space, Planets, Night, Lens)", "Hat (Head, Wear, Cap, Sun, Fashion)", 
        "Key (Lock, Door, Car, Metal, Open)", "Envelope (Letter, Mail, Stamp, Paper, Send)", 
        "Pizza (Cheese, Sauce, Slice, Italian, Delivery)", "Ladder (Climb, High, Steps, Rungs, Wall)", 
        "Guitar (Music, Strings, Instrument, Play, Rock)", "Alien (Space, UFO, Green, Planet, Martian)", 
        "Flower (Rose, Garden, Plant, Petal, Bloom)", "Rain (Water, Sky, Clouds, Storm, Wet)", 
        "Bicycle (Wheels, Pedals, Ride, Helmet, Chain)", "Anchor (Ship, Boat, Sea, Heavy, Water)", 
        "Scuba (Dive, Ocean, Tank, Mask, Swim)", "Firefighter (Truck, Hose, Water, Siren, Brave)", 
        "Microscope (Science, Lab, Cells, Lens, Tiny)", "Lantern (Light, Lamp, Dark, Camp, Flame)", 
        "Book (Read, Pages, Library, Cover, Story)", "Dog (Bark, Pet, Puppy, Tail, Canine)", 
        "Tornado (Wind, Storm, Twister, Weather, Destruction)", "Piano (Music, Keys, Instrument, Play, Black)", 
        "Ice (Cold, Water, Frozen, Cube, Melt)", "Rocket (Space, Launch, Fly, NASA, Fuel)", 
        "Kangaroo (Jump, Pouch, Australia, Animal, Hop)", "Egg (Chicken, Shell, Breakfast, Yolk, White)", 
        "Blender (Kitchen, Smoothie, Mix, Fruit, Ice)", "Desert (Sand, Hot, Cactus, Dry, Camel)", 
        "Fruit (Fruit, Red, Tree, Crisp, Pie)", "Kite (Fly, Wind, String, Sky, Paper)", 
        "River (Water, Flow, Stream, Fish, Boat)", "Ring (Finger, Gold, Marriage, Diamond, Jewelry)", 
        "Forest (Trees, Woods, Nature, Green, Animals)", "Banana (Fruit, Yellow, Peel, Monkey, Bunch)", 
        "Orange (Fruit, Citrus, Color, Juice, Peel)", "Honey (Bee, Sweet, Jar, Hive, Sticky)", 
        "Octopus (Eight, Tentacles, Ocean, Ink, Sea)", "Knife (Sharp, Cut, Kitchen, Blade, Food)", 
        "Lion (King, Roar, Mane, Safari, Cat)", "Crown (King, Queen, Gold, Head, Royal)", 
        "Spider (Web, Eight, Legs, Bug, Arachnid)", "Mountain (Climb, Peak, Snow, High, Hike)", 
        "Eagle (Bird, Sky, Wings, Prey, American)", "Fish (Swim, Water, Ocean, Scales, Gills)", 
        "Balloon (Air, Party, String, Float, Pop)", "House (Home, Roof, Live, Building, Door)", 
        "Candle (Wax, Flame, Light, Fire, Wick)", "Chair (Sit, Furniture, Table, Legs, Wood)", 
        "Jungle (Trees, Vines, Rainforest, Wild, Animals)", "Owl (Bird, Night, Wise, Hoot, Feathers)", 
        "Chef (Cook, Food, Kitchen, Restaurant, Hat)", "Magnet (Metal, Pull, North, South, Attract)", 
        "Necklace (Jewelry, Neck, Chain, Gold, Wear)", "Hammer (Nail, Tool, Hit, Wood, Build)", 
        "Fork (Eat, Food, Utensil, Prongs, Dinner)", "Dragon (Fire, Myth, Scales, Wings, Treasure)", 
        "Cloud (Sky, Rain, White, Weather, Fluffy)", "Battery (Power, Energy, Charge, Electricity, Toy)", 
        "Beach (Sand, Ocean, Sun, Waves, Towel)", "Pirate (Ship, Treasure, Map, Eye-patch, Captain)", 
        "Door (Open, Close, Handle, Room, Entrance)", "Horse (Ride, Gallop, Animal, Cowboy, Saddle)", 
        "Penguin (Ice, Bird, Tuxedo, Swim, Antarctica)", "Lamp (Light, Bulb, Desk, Switch, Shine)", 
        "Ninja (Stealth, Sword, Black, Shadow, Mask)", "Moon (Night, Sky, Space, Orbit, Stars)"
    ],
    "actions": [
        "Playing rock-paper-scissors", "Defusing a time bomb", "Walking through sand dunes", "Sewing a rip in a jacket", 
        "Pouring a glass of water carefully", "Washing a dirty car", "Building a snowman", "Surfing a massive wave", 
        "Slipping on an icy sidewalk", "Ironing a shirt", "Shaving a beard", "Feeding bread to ducks", 
        "Raking autumn leaves", "Trying to swat a fly", "Climbing a steep mountain", "Driving a racecar", 
        "Playing the flute", "Sneaking past a sleeping guard", "Slicing fresh bread", "Mowing the lawn", 
        "Walking a stubborn dog", "Chopping onions and crying", "Stretching before a big race", "Baking a cake", 
        "Walking down a catwalk", "Skating on smooth ice", "Riding a bumpy camel", "Eating a very spicy pepper", 
        "Typing frantically on a keyboard", "Shoveling snow", "Doing a gymnastics routine", "Tying a necktie", 
        "Putting on makeup", "Watering a garden hose", "Scuba diving underwater", "Blowing up a giant balloon", 
        "Peeling a sticky orange", "Blowing out birthday candles", "Riding a wild rollercoaster", "Directing traffic", 
        "Plucking a guitar string", "Catching a big fish", "Answering a ringing phone", "Walking through deep mud", 
        "Putting on a heavy coat", "Stuck in a heavy downpour", "Licking an ice cream cone", "Hanging up wet laundry", 
        "Walking like a robot", "Skiing down a snowy slope", "Chasing a runaway chicken", "Drinking a sour lemon drink", 
        "Marching in a brass band", "Tying your shoes in a hurry", "Playing a game of bowling", "Swinging a baseball bat", 
        "Lifting heavy weights", "Pumping up a bicycle tire", "Stirring a big pot of soup", "Sweeping up broken glass", 
        "Flying a kite", "Milking a cow", "Juggling three balls", "Planting a small flower seed", 
        "Picking fresh apples from a tree", "Trying to sleep with a mosquito around", "Petting a giant lion", "Rock climbing a cliff face", 
        "Rowing a boat upstream", "Conducting a symphonic orchestra", "Shooting a basketball", "Kicking a soccer ball", 
        "Walking a tightrope", "Opening a stuck jar", "Hitching a ride on a road", "Brushing your teeth", 
        "Playing the drums", "Combing long tangled hair", "Walking through a haunted house", "Painting a masterpiece", 
        "Singing in the shower", "Trying on a tight pair of jeans", "Building a tall card tower", "Dancing the tango", 
        "Wrapping a birthday present", "Changing a flat car tire", "Threading a very small needle", "Doing the moonwalk", 
        "Playing a game of tennis", "Walking on a windy beach"
    ],
    "categories": [
        "Insects", "Websites", "Things Found on a Beach", "Types of Fabric", 
        "Superheroes", "Dances", "Things Made of Wood", "Fast Food Chains", 
        "Historical Figures", "Types of Weather", "A Boy's Name", "Breakfast Foods", 
        "Ocean Life", "Sports Teams", "Vegetables", "A Girl's Name", 
        "Things That Are Sweet", "Holiday Names", "Types of Music", "Tools", 
        "Things in a Classroom", "Types of Shoes", "Types of Candy", "Yard/Garden Tools", 
        "Fairy Tale Characters", "TV Shows", "Things Found in Space", "Apps on a Phone", 
        "Things That Are Cold", "Items In A Refrigerator", "Colors", "Video Games", 
        "Musical Instruments", "Things Made of Metal", "Cites", "Street Names", 
        "Things That Are Fast", "Pizza Toppings", "Things That Are Round", "Shapes", 
        "School Subjects", "Movie Titles", "Monsters", "Types of Cats", 
        "Hot Drinks", "Clothing Items", "Languages", "Things That Are Loud", 
        "Types of Vehicles", "Animals", "Parts of a Car", "Planets", 
        "Board Games", "Types of Sandwiches", "Mythical Creatures", "Soups", 
        "Weapons", "Greek Gods", "Things That Are Wet", "Things That Are Soft", 
        "Bakery Items", "Fish Species", "Ice Cream Flavors", "Supervillains", 
        "Countries", "Things in a Kitchen", "Actresses", "Soft Drinks", 
        "Things in a Bathroom", "Reptiles", "Types of Dogs", "Cartoon Characters", 
        "Hobbies", "Types of Pasta", "Types of Cheese", "Brands of Cars", 
        "Authors", "Spices and Herbs", "Birds", "Constellations", 
        "Flowers", "Things in a Bedroom", "Things in a Living Room", "Book Titles", 
        "Rivers", "Fruits", "Jobs/Professions", "Musical Artists", 
        "Colors in a Rainbow", "Mammals", "Actors", "Things That Are Hot", 
        "Trees", "Mountains"
    ],
    "letters": ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"],
    "vowels": ["A", "E", "I", "O", "U", "Y"]
}


class SilentImage(KivyImage):
    """Custom Kivy Image variant that handles rendering drops cleanly on exception."""
    def on_image_error(self, *args) -> bool:
        self.texture = None
        return True


class BarrelSpinner(Widget):
    """Custom graphical selection wheel widget utilizing OpenGL canvas draws."""
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
        self.canvas.clear()
        if not self.options:
            return

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


class UnifiedCardAndWheelApp(App):
    """Main application controller managing state, core layout setups, and dropdown events."""
    def build(self) -> BoxLayout:
        self.title = "Interactive Card & 5 Barrel Spinners"
        
        # Audio Initialization
        self.card_sound = SoundLoader.load("assets/Sounds/flip.mp3")
        self.spinner_sound = SoundLoader.load("assets/Sounds/spin.mp3")

        # Session Game Tracking State Variables
        self.current_round_num = 1
        self.card_flips_count = 0
        self.flips_target_limit = 5  

        # Load Local Configurations dynamically via standard data pool reference
        self.options1 = GAME_DATA_POOLS["words"]
        self.options2 = GAME_DATA_POOLS["actions"]
        self.options3 = GAME_DATA_POOLS["categories"]
        self.options4 = GAME_DATA_POOLS["letters"]
        self.options5 = GAME_DATA_POOLS["vowels"]

        self.round_descriptions = {
            1: "Round 1: Talk!",
            2: "Round 2: Act!",
            3: "Round 3: Draw!"
        }

        self.card_back_path = "assets/sprites/back.png"
        self.card_pool1 = ["assets/sprites/0.png", "assets/sprites/1.png", "assets/sprites/8.png"]
        self.card_pool2 = ["assets/sprites/6.png", "assets/sprites/7.png"]
        self.card_pool3 = ["assets/sprites/2.png", "assets/sprites/3.png", "assets/sprites/4.png", "assets/sprites/5.png"]

        # Base Layout Parent Container Setup
        self.root_layout = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(8))
        with self.root_layout.canvas.before:
            Color(*COLOR_BG)
            self.bg_rect = Rectangle(pos=self.root_layout.pos, size=self.root_layout.size)
        self.root_layout.bind(pos=self._update_bg, size=self._update_bg)

        # Build UI Sub-Components Modularly
        self._build_top_navbar()
        self._build_main_gameplay_views()
        self._build_status_footer()

        return self.root_layout

    def _build_top_navbar(self):
        """Constructs top navigation view block containing dropdown systems and setup button configs."""
        self.top_nav = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40), spacing=dp(10))
        
        # 'My Games' Sub-engine drop building module setup
        self.my_games_btn = Button(text="My Games", font_size='12sp', bold=True, size_hint_x=None, width=dp(110),
                                   background_normal='', background_color=COLOR_BUTTON_BG, color=(1,1,1,1))
        
        self.games_dropdown = DropDown()
        for item in ["Telestrations", "Chameleon", "Pictionary"]:
            btn = Button(text=item, size_hint_y=None, height=dp(35), font_size='12sp',
                         background_normal='', background_color=COLOR_BARREL_BG, color=(0.9, 0.9, 0.9, 1))
            btn.bind(on_release=lambda btn_obj: self.games_dropdown.select(btn_obj.text))
            self.games_dropdown.add_widget(btn)
            
        self.my_games_btn.bind(on_release=self.games_dropdown.open)
        self.games_dropdown.bind(on_select=self.handle_game_selection)
        
        # Settings menu configuration element properties
        self.menu_btn = Button(text="Settings", font_size='14sp', bold=True, size_hint_x=None, width=dp(100),
                               background_normal='', background_color=COLOR_BUTTON_BG, color=(1,1,1,1))
        self.menu_btn.bind(on_release=self.open_prompt_editor)
        
        self.top_nav.add_widget(self.my_games_btn)
        self.top_nav.add_widget(Widget())  # Spacer layout pushing properties horizontally
        self.top_nav.add_widget(self.menu_btn)
        self.root_layout.add_widget(self.top_nav)

    def _build_main_gameplay_views(self):
        """Builds central responsive core container containing asset cards block and custom spin barrels."""
        self.main_container = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=1.0)
        self.root_layout.bind(size=self.adjust_layout_orientation)

        # Graphical card visualization structures UI
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

        # Five component individual configuration layouts setup assembly blocks
        self.barrels_container = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=0.65)
        
        self.barrel1 = BarrelSpinner("Words", self.options1, COLOR_ACCENT_BLUE, self.update_winner_1)
        self.barrel2 = BarrelSpinner("Action", self.options2, COLOR_ACCENT_GREEN, self.update_winner_2)
        self.barrel3 = BarrelSpinner("Categories", self.options3, COLOR_ACCENT_PURPLE, self.update_winner_3)
        self.barrel4 = BarrelSpinner("Letters", self.options4, COLOR_ACCENT_ORANGE, self.update_winner_4)
        self.barrel5 = BarrelSpinner("Vowels", self.options5, COLOR_ACCENT_BLUE, self.update_winner_5)

        # Append functional nested wrapped elements safely inside visual containers
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
        """Assembles standard bottom output metrics view bar to keep tracking system logs visible."""
        self.output_label = Label(text="Play a card and spin the barrels!", font_size='13sp', bold=True,
                                  color=(1,1,1,1), size_hint_y=None, height=dp(40), halign='center', valign='middle')
        self.output_label.bind(size=lambda i, v: setattr(i, 'text_size', (i.width, None)))
        self.root_layout.add_widget(self.output_label)
        self.game_over_view = None

    def _create_labeled_wrapper(self, label_text: str, accent_color: tuple, widget_element: Widget) -> BoxLayout:
        """Helper construction factory to create standardized design panels layout blocks cleaner."""
        wrapper = BoxLayout(orientation='vertical', spacing=dp(2))
        lbl = Label(text=label_text, font_size='9sp', bold=True, color=accent_color, size_hint_y=None, height=dp(12), halign='left')
        lbl.bind(size=lambda i, v: setattr(i, 'text_size', (i.width, None)))
        wrapper.add_widget(lbl)
        wrapper.add_widget(widget_element)
        return wrapper

    def handle_game_selection(self, instance, game_title: str):
        """
        Intercepts dropdown selection, terminates the current window,
        and launches the target game as an independent script execution.
        """
        self.output_label.text = f"Launching: {game_title}..."
        
        # Map dropdown selections to their corresponding standalone python scripts
        game_script_mapping = {
            "Telestrations": "Telestrations.py",
            "Chameleon": "Chameleon.py",
            "Pictionary": "Pictionary.py"
        }
        
        target_script = game_script_mapping.get(game_title)
        
        if target_script:
            try:
                # 1. Spawn the new Python script as a detached background system process
                subprocess.Popen([sys.executable, target_script])
                
                # 2. Smoothly terminate the dashboard app window to clean up CPU/GPU RAM
                App.get_running_app().stop()
                
            except Exception as e:
                self.output_label.text = f"Failed to execute game script: {str(e)}"
        else:
            self.output_label.text = f"Error: Game script not found for '{game_title}'"

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
        if all(hasattr(self, f"barrel{i}") for i in range(1, 6)):
            for b in barrels:
                b.canvas.clear()
                Clock.schedule_once(lambda dt, b_obj=b: b_obj._redraw())

        width, height = size
        if width > height:  # Adaptive Landscape
            self.main_container.orientation = 'horizontal'
            self.card_layout_block.size_hint = (0.32, 1)
            self.barrels_container.size_hint = (0.68, 1)
            self.card_img.size = (height * 0.35, height * 0.46)
        else:               # Adaptive Portrait
            self.main_container.orientation = 'vertical'
            self.card_layout_block.size_hint = (1, 0.33)
            self.barrels_container.size_hint = (1, 0.67)
            self.card_img.size = (dp(140), dp(180))

    def handle_card_click(self, instance, touch) -> bool:
        if instance.collide_point(*touch.pos):
            pool_mapping = {1: self.card_pool1, 2: self.card_pool2, 3: self.card_pool3}
            active_pool = pool_mapping.get(self.current_round_num, self.card_pool1)

            valid_pool = [p for p in active_pool if os.path.exists(p)]
            if valid_pool:
                if self.card_sound:
                    self.card_sound.play()
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

    # Individual Spinner Value Triggers Output Receivers
    def update_winner_1(self, res: str):
        if self.current_round_num <= 3:
            self.output_label.text = f"Words: {res}"

    def update_winner_2(self, res: str):
        if self.current_round_num <= 3:
            self.output_label.text = f"Action: {res}"

    def update_winner_3(self, res: str):
        if self.current_round_num <= 3:
            self.output_label.text = f"Categories: {res}"

    def update_winner_4(self, res: str):
        if self.current_round_num <= 3:
            self.output_label.text = f"Letters: {res}"

    def update_winner_5(self, res: str):
        if self.current_round_num <= 3:
            self.output_label.text = f"Vowels: {res}"

    def open_prompt_editor(self, instance):
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(6))
        with content.canvas.before:
            Color(*COLOR_BG)
            rect = Rectangle(pos=content.pos, size=content.size)
            content.bind(pos=lambda i, v: setattr(rect, 'pos', i.pos), size=lambda i, v: setattr(rect, 'size', i.size))

        content.add_widget(Label(text="Customize Configuration Settings", font_size='14sp', bold=True, size_hint_y=None, height=dp(20)))

        limit_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(30), spacing=dp(10))
        limit_box.add_widget(Label(text="Card Flips Per Round:", font_size='11sp', bold=True, color=COLOR_ACCENT_ORANGE, size_hint_x=0.6, halign='left'))
        txt_limit = TextInput(text=str(self.flips_target_limit), input_filter='int', multiline=False, background_color=(0.145, 0.145, 0.161, 1), foreground_color=(1,1,1,1))
        limit_box.add_widget(txt_limit)
        content.add_widget(limit_box)

        content.add_widget(Label(text="Words Data Pool:", font_size='10sp', bold=True, color=COLOR_ACCENT_BLUE, size_hint_y=None, height=dp(12)))
        txt_nouns = TextInput(text="\n".join(self.options1), background_color=(0.145, 0.145, 0.161, 1), foreground_color=(1,1,1,1))
        content.add_widget(txt_nouns)

        content.add_widget(Label(text="Action Data Pool:", font_size='10sp', bold=True, color=COLOR_ACCENT_GREEN, size_hint_y=None, height=dp(12)))
        txt_verbs = TextInput(text="\n".join(self.options2), background_color=(0.145, 0.145, 0.161, 1), foreground_color=(1,1,1,1))
        content.add_widget(txt_verbs)

        content.add_widget(Label(text="Categories Data Pool:", font_size='10sp', bold=True, color=COLOR_ACCENT_PURPLE, size_hint_y=None, height=dp(12)))
        txt_categories = TextInput(text="\n".join(self.options3), background_color=(0.145, 0.145, 0.161, 1), foreground_color=(1,1,1,1))
        content.add_widget(txt_categories)

        split_row_labels = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(12), spacing=dp(10))
        split_row_labels.add_widget(Label(text="Letters Data Pool:", font_size='10sp', bold=True, color=COLOR_ACCENT_ORANGE, halign='left'))
        split_row_labels.add_widget(Label(text="Vowels Data Pool:", font_size='10sp', bold=True, color=COLOR_ACCENT_BLUE, halign='left'))
        content.add_widget(split_row_labels)

        split_row_inputs = BoxLayout(orientation='horizontal', spacing=dp(10))
        txt_letters = TextInput(text="\n".join(self.options4), background_color=(0.145, 0.145, 0.161, 1), foreground_color=(1,1,1,1))
        txt_vowels = TextInput(text="\n".join(self.options5), background_color=(0.145, 0.145, 0.161, 1), foreground_color=(1,1,1,1))
        split_row_inputs.add_widget(txt_letters)
        split_row_inputs.add_widget(txt_vowels)
        content.add_widget(split_row_inputs)

        btn_bar = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(35))
        popup = Popup(title='', content=content, size_hint=(0.95, 0.95), separator_height=0)

        def save_changes(btn_instance):
            try:
                val = int(txt_limit.text.strip())
                if val > 0:
                    self.flips_target_limit = val
            except ValueError:
                pass

            anim_lines = [line.strip() for line in txt_nouns.text.splitlines() if line.strip()]
            verb_lines = [line.strip() for line in txt_verbs.text.splitlines() if line.strip()]
            set_lines = [line.strip() for line in txt_categories.text.splitlines() if line.strip()]
            obj_lines = [line.strip() for line in txt_letters.text.splitlines() if line.strip()]
            vwl_lines = [line.strip() for line in txt_vowels.text.splitlines() if line.strip()]
            
            if anim_lines:
                self.options1 = anim_lines
                self.barrel1.options = anim_lines
                self.barrel1.y_offset = 0.0
                self.barrel1._redraw()
            if verb_lines:
                self.options2 = verb_lines
                self.barrel2.options = verb_lines
                self.barrel2.y_offset = 0.0
                self.barrel2._redraw()
            if set_lines:
                self.options3 = set_lines
                self.barrel3.options = set_lines
                self.barrel3.y_offset = 0.0
                self.barrel3._redraw()
            if obj_lines:
                self.options4 = obj_lines
                self.barrel4.options = obj_lines
                self.barrel4.y_offset = 0.0
                self.barrel4._redraw()
            if vwl_lines:
                self.options5 = vwl_lines
                self.barrel5.options = vwl_lines
                self.barrel5.y_offset = 0.0
                self.barrel5._redraw()
                
            self.round_header_label.text = self.get_round_string_meta()
            popup.dismiss()

        save_btn = Button(text="Save Changes", bold=True, background_normal='', background_color=COLOR_BUTTON_BG)
        save_btn.bind(on_release=save_changes)
        cancel_btn = Button(text="Cancel", background_normal='', background_color=(0.247, 0.247, 0.275, 1))
        cancel_btn.bind(on_release=popup.dismiss)

        btn_bar.add_widget(cancel_btn)
        btn_bar.add_widget(save_btn)
        content.add_widget(btn_bar)

        popup.open()


if __name__ == "__main__":
    UnifiedCardAndWheelApp().run()
