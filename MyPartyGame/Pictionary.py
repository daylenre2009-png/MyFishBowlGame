import tkinter as tk
from tkinter import colorchooser, messagebox, filedialog, ttk
from PIL import Image, ImageDraw, ImageTk
import subprocess  # Added to launch external scripts
import sys         # Added to detect the current python interpreter path

class ProfessionalDrawingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Studio Canvas Pro")
        self.root.geometry("1150x750")
        
        # --- Professional Deep Navy Color Palette ---
        self.CLR_BG = "#0b132b"         
        self.CLR_SIDEBAR = "#1c2541"   
        self.CLR_BTN_IDLE = "#3a506b"  
        self.CLR_BTN_ACTIVE = "#2b3b4e" 
        self.CLR_ACCENT = "#5bc0be"     
        
        self.root.configure(bg=self.CLR_BG)

        # --- Configure ttk Styles for Mac Compatibility ---
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Base settings for Normal Buttons
        self.style.configure('Custom.TButton', 
                             background=self.CLR_BTN_IDLE, 
                             foreground="white", 
                             font=("Helvetica", 10, "bold"),
                             borderwidth=0,
                             focuscolor='none')
        # HOVER FIX: Forces the button to stay CLR_BTN_IDLE or slightly shift when hovered/active
        self.style.map('Custom.TButton',
                       background=[('active', self.CLR_BTN_IDLE), ('pressed', self.CLR_BTN_ACTIVE)],
                       foreground=[('active', 'white')])
        
        # Base settings for Selected Active Tool Buttons
        self.style.configure('Active.TButton', 
                             background=self.CLR_BTN_ACTIVE, 
                             foreground="white", 
                             font=("Helvetica", 10, "bold"),
                             borderwidth=0,
                             focuscolor='none')
        # HOVER FIX: Forces active tools to stay CLR_BTN_ACTIVE when hovered
        self.style.map('Active.TButton',
                       background=[('active', self.CLR_BTN_ACTIVE)],
                       foreground=[('active', 'white')])
                             
        # Base settings for the Color Picker Button
        self.style.configure('ColorPicker.TButton',
                             background=self.CLR_BTN_IDLE,
                             foreground="white",
                             font=("Helvetica", 10, "bold"),
                             borderwidth=0,
                             focuscolor='none')
        # HOVER FIX: Dynamic tracking handled in choose_color, initialization state mapping here
        self.style.map('ColorPicker.TButton',
                       background=[('active', self.CLR_BTN_IDLE)],
                       foreground=[('active', 'white')])

        # Application Core States
        self.brush_color = "#00b4d8"    
        self.eraser_color = "#ffffff"
        self.active_color = self.brush_color
        self.brush_size = 5
        self.current_tool = "draw" 
        
        # Timer Setup
        self.time_left = 300 
        self.timer_running = False
        self.timer_started = False  
        self.timer_id = None
        
        # Undo/Redo Engine History Stacks
        self.undo_stack = []
        self.redo_stack = []
        
        self.last_x, self.last_y = None, None

        # --- Base Layout Infrastructure ---
        self.setup_sidebar()
        self.setup_canvas_workspace()

        # Core Backing Engine (Hidden PIL high-res layer)
        self.canvas_width = 900
        self.canvas_height = 650
        self.pil_image = Image.new("RGB", (self.canvas_width, self.canvas_height), "white")
        self.pil_draw = ImageDraw.Draw(self.pil_image)
        
        # Save initial blank slate to undo history
        self.save_to_history()
        
        # Keyboard Shortcut Bindings (Undo & Redo)
        self.root.bind("<Command-z>", lambda event: self.undo())
        self.root.bind("<Control-z>", lambda event: self.undo())
        self.root.bind("<Command-y>", lambda event: self.redo())
        self.root.bind("<Control-y>", lambda event: self.redo())

    def setup_sidebar(self):
        """Builds a professional creative suite sidebar on the left side."""
        self.sidebar = tk.Frame(self.root, bg=self.CLR_SIDEBAR, width=220, bd=0)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=0, pady=0)
        self.sidebar.pack_propagate(False) 

        # App Title Header
        title = tk.Label(self.sidebar, text="STUDIO CANVAS", font=("Helvetica", 14, "bold"), 
                         bg=self.CLR_SIDEBAR, fg=self.CLR_ACCENT)
        title.pack(pady=(20, 5))
        
        subtitle = tk.Label(self.sidebar, text="Professional Edition", font=("Helvetica", 9, "italic"), 
                            bg=self.CLR_SIDEBAR, fg="#6c757d")
        subtitle.pack(pady=(0, 20))

        # --- Interactive Tool Control Buttons ---
        self.btn_draw = self.create_ui_button("✏️ Brush Tool", self.set_tool_draw)
        self.btn_draw.pack(pady=5, fill=tk.X, padx=15)
        
        self.btn_eraser = self.create_ui_button("🧽 Eraser Tool", self.set_tool_eraser)
        self.btn_eraser.pack(pady=5, fill=tk.X, padx=15)
        
        self.btn_fill = self.create_ui_button("🪣 Paint Bucket", self.set_tool_fill)
        self.btn_fill.pack(pady=5, fill=tk.X, padx=15)
        
        self.set_tool_draw()

        # Color Spectrum Picker Block
        color_frame = tk.Frame(self.sidebar, bg=self.CLR_SIDEBAR)
        color_frame.pack(pady=15, fill=tk.X, padx=15)
        
        cl_label = tk.Label(color_frame, text="Active Color Swatch", font=("Helvetica", 9, "bold"), bg=self.CLR_SIDEBAR, fg="white")
        cl_label.pack(anchor=tk.W, pady=(0, 4))
        
        self.color_preview = ttk.Button(color_frame, text="Pick Color", style='ColorPicker.TButton', command=self.choose_color)
        self.color_preview.pack(fill=tk.X, ipady=4)

        # Dynamic Size Slider Configuration
        size_frame = tk.Frame(self.sidebar, bg=self.CLR_SIDEBAR)
        size_frame.pack(pady=15, fill=tk.X, padx=15)
        
        sz_label = tk.Label(size_frame, text="Brush Size", font=("Helvetica", 9, "bold"), bg=self.CLR_SIDEBAR, fg="white")
        sz_label.pack(anchor=tk.W)
        
        self.size_scale = tk.Scale(size_frame, from_=1, to=100, orient=tk.HORIZONTAL, 
                                   bg=self.CLR_SIDEBAR, fg="white", highlightthickness=0,
                                   troughcolor=self.CLR_BG, activebackground=self.CLR_BTN_ACTIVE,
                                   command=self.update_size)
        self.size_scale.set(self.brush_size)
        self.size_scale.pack(fill=tk.X, pady=5)

        # --- TIMER WIDGET DISPLAY ---
        self.timer_container = tk.Frame(self.sidebar, bg="#0b132b", bd=0, pady=10, padx=10)
        self.timer_container.pack(pady=15, fill=tk.X, padx=15)
        
        self.timer_label = tk.Label(self.timer_container, text="⏱️ 05:00", bg="#0b132b", fg="#e2e8f0", 
                                    font=("Courier New", 14, "bold"))
        self.timer_label.pack(side=tk.TOP, pady=2)
        
        reset_timer_btn = ttk.Button(self.timer_container, text="Reset Timer", style='Custom.TButton', command=self.reset_timer)
        reset_timer_btn.pack(side=tk.TOP, pady=4)

        # --- UTILITY COMMAND PANEL (BOTTOM) ---
        utils_frame = tk.Frame(self.sidebar, bg=self.CLR_SIDEBAR)
        utils_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=15, padx=15)

        # History Buttons Layout Side-By-Side
        hist_frame = tk.Frame(utils_frame, bg=self.CLR_SIDEBAR)
        hist_frame.pack(fill=tk.X, pady=2)
        
        ttk.Button(hist_frame, text="↩️ Undo", style='Custom.TButton', command=self.undo).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 2))
        ttk.Button(hist_frame, text="↪️ Redo", style='Custom.TButton', command=self.redo).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(2, 0))
        
        ttk.Button(utils_frame, text="💾 Export Artwork", style='Custom.TButton', command=self.save_artwork).pack(fill=tk.X, pady=4)
        ttk.Button(utils_frame, text="🗑️ Wipe Canvas", style='Custom.TButton', command=self.clear_canvas).pack(fill=tk.X, pady=4)
        
        # New Main Menu Navigation Button
        ttk.Button(utils_frame, text="Main Menu", style='Custom.TButton', command=self.go_to_menu).pack(fill=tk.X, pady=(10, 4))

    def create_ui_button(self, text, command):
        """Helper to create stylized, modern flat buttons using ttk."""
        return ttk.Button(self.sidebar, text=text, style='Custom.TButton', command=command)

    def setup_canvas_workspace(self):
        """Maintains clean canvas positioning in center screen viewport workspace."""
        self.workspace = tk.Frame(self.root, bg=self.CLR_BG)
        self.workspace.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=30, pady=30)

        canvas_border = tk.Frame(self.workspace, bg="#111827", bd=1)
        canvas_border.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(canvas_border, bg="#ffffff", cursor="crosshair", bd=0, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.canvas.bind("<Button-1>", self.handle_click)
        self.canvas.bind("<B1-Motion>", self.draw)
        self.canvas.bind("<ButtonRelease-1>", self.stop_drawing)
        self.canvas.bind("<Configure>", self.on_canvas_resize)

    # --- Timer Subroutines ---
    def start_timer(self):
        if not self.timer_running:
            self.timer_running = True
            self.timer_started = True
            self.update_timer_countdown()

    def update_timer_countdown(self):
        if self.time_left > 0:
            mins, secs = divmod(self.time_left, 60)
            self.timer_label.config(text=f"⏱️ {mins:02d}:{secs:02d}", fg="#4ade80")
            self.time_left -= 1
            self.timer_id = self.root.after(1000, self.update_timer_countdown)
        else:
            self.timer_running = False
            self.timer_label.config(text="⏱️ DEADLINE", fg="#ef4444")
            messagebox.showinfo("Session Expired", "5 Minutes are complete! Excellent work.")

    def reset_timer(self):
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
        self.time_left = 300
        self.timer_running = False
        self.timer_started = False
        self.timer_label.config(text="⏱️ 05:00", fg="#e2e8f0")

    # --- Structural Drawing Logic ---
    def handle_click(self, event):
        if not self.timer_started:
            self.start_timer()

        if self.current_tool == "fill":
            self.flood_fill(event.x, event.y)
            self.save_to_history() 
        else:
            self.last_x, self.last_y = event.x, event.y

    def draw(self, event):
        if self.current_tool == "fill":
            return
            
        if self.last_x is not None and self.last_y is not None:
            self.canvas.create_line(
                self.last_x, self.last_y, event.x, event.y,
                width=self.brush_size, fill=self.active_color,
                capstyle=tk.ROUND, smooth=True
            )
            self.pil_draw.line(
                [(self.last_x, self.last_y), (event.x, event.y)],
                fill=self.active_color, width=self.brush_size, joint="round"
            )
        self.last_x, self.last_y = event.x, event.y

    def stop_drawing(self, event):
        if self.current_tool != "fill":
            self.save_to_history() 
        self.last_x, self.last_y = None, None

    def flood_fill(self, start_x, start_y):
        if start_x >= self.canvas.winfo_width() or start_y >= self.canvas.winfo_height() or start_x < 0 or start_y < 0:
            return
        target_rgb = self.hex_to_rgb(self.brush_color)
        ImageDraw.floodfill(self.pil_image, xy=(start_x, start_y), value=target_rgb, thresh=15)
        self.refresh_canvas_from_pil()

    # --- History Engine: Undo & Redo System ---
    def save_to_history(self):
        """Pushes a snapshot copy of the current drawing onto history stack tracking."""
        if hasattr(self, 'pil_image'):
            if len(self.undo_stack) >= 20:
                self.undo_stack.pop(0)
            self.undo_stack.append(self.pil_image.copy())
            self.redo_stack.clear()

    def undo(self):
        """Reverts the canvas back by one stroke operation."""
        if len(self.undo_stack) > 1:
            current_state = self.undo_stack.pop()
            self.redo_stack.append(current_state)
            
            previous_snapshot = self.undo_stack[-1].copy()
            self.pil_image = previous_snapshot
            self.pil_draw = ImageDraw.Draw(self.pil_image)
            self.refresh_canvas_from_pil()
        else:
            messagebox.showinfo("Undo", "Canvas is already back at its initial state.")

    def redo(self):
        """Restores a previously undone stroke action if no newer edits occurred."""
        if self.redo_stack:
            restored_state = self.redo_stack.pop()
            self.undo_stack.append(restored_state)
            
            self.pil_image = restored_state.copy()
            self.pil_draw = ImageDraw.Draw(self.pil_image)
            self.refresh_canvas_from_pil()
        else:
            messagebox.showinfo("Redo", "Nothing to redo!")

    def save_artwork(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG Image", "*.png"), ("JPEG Image", "*.jpg"), ("All Files", "*.*")]
        )
        if file_path:
            cw, ch = self.canvas.winfo_width(), self.canvas.winfo_height()
            cropped_output = self.pil_image.crop((0, 0, cw, ch))
            cropped_output.save(file_path)
            messagebox.showinfo("Success", "Masterpiece saved successfully!")

    def refresh_canvas_from_pil(self):
        self.canvas.delete("all")
        self.tk_image = ImageTk.PhotoImage(self.pil_image)
        self.canvas.create_image(0, 0, image=self.tk_image, anchor=tk.NW)

    def on_canvas_resize(self, event):
        if event.width > self.canvas_width or event.height > self.canvas_height:
            new_pil = Image.new("RGB", (event.width, event.height), "white")
            new_pil.paste(self.pil_image, (0, 0))
            self.pil_image = new_pil
            self.pil_draw = ImageDraw.Draw(self.pil_image)
            self.canvas_width = event.width
            self.canvas_height = event.height

    def hex_to_rgb(self, hex_str):
        hex_str = hex_str.lstrip('#')
        return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))

    # --- Professional Interactive UI State Handlers ---
    def reset_tool_button_highlights(self):
        if hasattr(self, 'btn_draw'): self.btn_draw.config(style='Custom.TButton')
        if hasattr(self, 'btn_eraser'): self.btn_eraser.config(style='Custom.TButton')
        if hasattr(self, 'btn_fill'): self.btn_fill.config(style='Custom.TButton')

    def set_tool_draw(self):
        self.current_tool = "draw"
        self.active_color = self.brush_color
        self.reset_tool_button_highlights()
        if hasattr(self, 'btn_draw'): self.btn_draw.config(style='Active.TButton')

    def set_tool_eraser(self):
        self.current_tool = "erase"
        self.active_color = self.eraser_color
        self.reset_tool_button_highlights()
        if hasattr(self, 'btn_eraser'): self.btn_eraser.config(style='Active.TButton')

    def set_tool_fill(self):
        self.current_tool = "fill"
        self.reset_tool_button_highlights()
        if hasattr(self, 'btn_fill'): self.btn_fill.config(style='Active.TButton')

    def choose_color(self):
        color = colorchooser.askcolor(color=self.brush_color)[1]
        if color:
            self.brush_color = color
            
            # Dynamically adjusts text color to preserve legibility against dark/light swatches
            rgb = self.hex_to_rgb(color)
            luminance = (0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]) / 255
            text_color = "black" if luminance > 0.5 else "white"
            
            # Reconfigures the style layout + the map hover array to match the color chosen
            self.style.configure('ColorPicker.TButton', background=color, foreground=text_color)
            self.style.map('ColorPicker.TButton', background=[('active', color)])
            
            if self.current_tool == "draw":
                self.active_color = color

    def update_size(self, size):
        self.brush_size = int(size)

    def clear_canvas(self):
        if messagebox.askyesno("Clear All", "Are you sure you want to clear your current work completely?"):
            self.canvas.delete("all")
            self.pil_image = Image.new("RGB", (2000, 2000), "white")
            self.pil_draw = ImageDraw.Draw(self.pil_image)
            self.undo_stack.clear()
            self.redo_stack.clear()
            self.save_to_history()
            self.set_tool_draw()

    def go_to_menu(self):
        """Launches main.py in a separate process and terminates the current window."""
        try:
            # Uses sys.executable to ensure main.py runs with the same python environment
            subprocess.Popen([sys.executable, "main.py"])
            self.root.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Could not launch main.py:\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ProfessionalDrawingApp(root)
    root.mainloop()