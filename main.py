import tkinter as tk
from tkinter import filedialog, messagebox
import os
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import filedialog, messagebox
import os
from PIL import Image, ImageTk

class FolderCropper:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Folder Image Cropper")
        
        # Data State
        self.image_list = []
        self.current_index = 0
        self.original_img = None
        
        # Cropping State
        self.start_x = self.start_y = 0
        self.rect = None

        # --- UI Layout ---
        self.top_frame = tk.Frame(root)
        self.top_frame.pack(pady=10)

        self.btn_load = tk.Button(self.top_frame, text="Load Folder", command=self.load_folder)
        self.btn_load.pack(side="left", padx=5)

        self.lbl_info = tk.Label(self.top_frame, text="No folder loaded")
        self.lbl_info.pack(side="left", padx=10)

        # The Drawing Canvas
        self.canvas = tk.Canvas(root, cursor="cross", bg="#222")
        self.canvas.pack(fill="both", expand=True)

        # Navigation Frame
        self.nav_frame = tk.Frame(root)
        self.nav_frame.pack(pady=10)

        self.btn_prev = tk.Button(self.nav_frame, text="<< Previous", command=self.prev_image)
        self.btn_prev.pack(side="left", padx=20)

        self.btn_next = tk.Button(self.nav_frame, text="Next >>", command=self.next_image)
        self.btn_next.pack(side="left", padx=20)

        # Bindings
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_move_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

 


class FittedCropper:
    def __init__(self, root):
        self.root = root
        self.root.title("Auto-Fit Image Cropper")
        self.root.geometry("1000x800")
        
        self.image_list = []
        self.current_index = 0
        self.original_img = None  # The high-res original
        self.display_img = None   # The resized version we see
        self.scale_factor = 1.0   # To translate screen clicks back to high-res
        
        # --- UI ---
        controls = tk.Frame(root)
        controls.pack(pady=10)
        
        tk.Button(controls, text="Load Folder", command=self.load_folder).pack(side="left", padx=5)
        self.lbl_info = tk.Label(controls, text="No folder loaded")
        self.lbl_info.pack(side="left", padx=10)

        # Canvas for drawing
        self.canvas = tk.Canvas(root, bg="#333", cursor="cross")
        self.canvas.pack(fill="both", expand=True)

        # Navigation
        nav = tk.Frame(root)
        nav.pack(pady=10)
        # tk.Button(nav, text="<< Prev", command=self.prev_image).pack(side="left", padx=20)
        # tk.Button(nav, text="Next >>", command=self.next_image).pack(side="left", padx=20)

        # Mouse Bindings
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_move_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)
        
        # Start coordinate storage
        self.start_x = self.start_y = 0
        self.rect = None

        # Easy Left Right
        self.root.bind("<Right>", lambda e: self.next_image())
        self.root.bind("<Left>", lambda e: self.prev_image())

    def load_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            exts = ('.png', '.jpg', '.jpeg', '.webp')
            self.image_list = [os.path.join(folder, f) for f in os.listdir(folder) if f.lower().endswith(exts)]
            if self.image_list:
                self.current_index = 0
                self.display_image()

    def display_image(self):
        path = self.image_list[self.current_index]
        self.original_img = Image.open(path)
        
        # --- Scaling Logic ---
        self.root.update() # Ensure canvas size is calculated
        canvas_w = self.canvas.winfo_width()
        canvas_h = self.canvas.winfo_height()
        
        img_w, img_h = self.original_img.size
        
        # Determine the scale factor (the smaller of the two)
        self.scale_factor = min(canvas_w/img_w, canvas_h/img_h)
        
        new_size = (int(img_w * self.scale_factor), int(img_h * self.scale_factor))
        self.display_img = self.original_img.resize(new_size, Image.Resampling.LANCZOS)
        
        self.tk_img = ImageTk.PhotoImage(self.display_img)
        self.canvas.delete("all")
        # Center the image on the canvas
        self.canvas.create_image(canvas_w//2, canvas_h//2, image=self.tk_img, anchor="center")
        
        self.lbl_info.config(text=f"Image {self.current_index+1}/{len(self.image_list)}")

    def load_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.webp')
            self.image_list = [
                os.path.join(folder_path, f) for f in os.listdir(folder_path) 
                if f.lower().endswith(extensions)
            ]
            
            if self.image_list:
                self.current_index = 0
                self.display_image()
            else:
                messagebox.showwarning("No Images", "No supported image files found in that folder.")

    def next_image(self):
        if self.image_list and self.current_index < len(self.image_list) - 1:
            self.current_index += 1
            self.display_image()

    def prev_image(self):
        if self.image_list and self.current_index > 0:
            self.current_index -= 1
            self.display_image()

    # --- Cropping Logic (Same as before) ---
    def on_button_press(self, event):
        self.start_x, self.start_y = event.x, event.y
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, 1, 1, outline='red', width=2)

    def on_move_press(self, event):
        self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)

    def on_button_release(self, event):
        # 1. Get screen coordinates relative to the image center
        # (This math accounts for the image being centered in the canvas)
        canvas_w = self.canvas.winfo_width()
        canvas_h = self.canvas.winfo_height()
        img_w, img_h = self.display_img.size
        
        offset_x = (canvas_w - img_w) / 2
        offset_y = (canvas_h - img_h) / 2

        # 2. Translate screen clicks to "Image Pixels"
        x1 = (min(self.start_x, event.x) - offset_x) / self.scale_factor
        y1 = (min(self.start_y, event.y) - offset_y) / self.scale_factor
        x2 = (max(self.start_x, event.x) - offset_x) / self.scale_factor
        y2 = (max(self.start_y, event.y) - offset_y) / self.scale_factor

        # 3. Crop from the ORIGINAL high-res image
        cropped = self.original_img.crop((x1, y1, x2, y2))
        
        save_path = filedialog.asksaveasfilename(defaultextension=".png")
        if save_path:
            cropped.save(save_path)

class ZoomCropper:
    def __init__(self, root):
        self.root = root
        self.root.title("Zoomable Image Cropper")
        self.root.geometry("1000x800")
        
        self.image_list = []
        self.current_index = 0
        self.original_img = None
        self.zoom_level = 1.0  # 1.0 = Fit to Screen
        self.base_scale = 1.0  # The scale required to 'fit' initially
        
        # UI Setup
        controls = tk.Frame(root)
        controls.pack(pady=5)
        tk.Button(controls, text="Load Folder", command=self.load_folder).pack(side="left")
        self.lbl_info = tk.Label(controls, text="Use Mouse Wheel to Zoom")
        self.lbl_info.pack(side="left", padx=20)

        self.canvas = tk.Canvas(root, bg="#222", cursor="cross")
        self.canvas.pack(fill="both", expand=True)

        # Bindings
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        
        # Windows/Linux mouse wheel
        self.canvas.bind("<MouseWheel>", self.handle_zoom)
        # MacOS mouse wheel
        self.canvas.bind("<Button-4>", self.handle_zoom)
        self.canvas.bind("<Button-5>", self.handle_zoom)

        self.rect = None
        tk.Button(controls, text="<< Prev", command=self.prev_image).pack(side="left", padx=20)
        tk.Button(controls, text="Next >>", command=self.next_image).pack(side="left", padx=20)

        self.root.bind("<Right>", lambda e: self.next_image())
        self.root.bind("<Left>", lambda e: self.prev_image())
        
        self.crop_counts = {}

    def load_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            exts = ('.png', '.jpg', '.jpeg')
            self.image_list = [os.path.join(folder, f) for f in os.listdir(folder) if f.lower().endswith(exts)]
            if self.image_list:
                self.current_index = 0
                self.zoom_level = 1.0 # Reset zoom
                self.display_image()

    def handle_zoom(self, event):
        if not self.original_img: return
        
        # Respond to scroll direction
        if event.num == 4 or event.delta > 0: # Scroll Up
            self.zoom_level *= 1.1
        else: # Scroll Down
            self.zoom_level /= 1.1
            
        # Limit zoom so it doesn't disappear or lag out
        self.zoom_level = max(0.1, min(self.zoom_level, 5.0))
        self.display_image()

    def display_image(self):
        path = self.image_list[self.current_index]
        if not self.original_img or self.zoom_level == 1.0:
            self.original_img = Image.open(path)

        canvas_w = self.canvas.winfo_width()
        canvas_h = self.canvas.winfo_height()
        img_w, img_h = self.original_img.size
        
        # Calculate fit scale then apply user zoom
        self.base_scale = min(canvas_w/img_w, canvas_h/img_h)
        total_scale = self.base_scale * self.zoom_level
        
        new_size = (int(img_w * total_scale), int(img_h * total_scale))
        resized_img = self.original_img.resize(new_size, Image.Resampling.LANCZOS)
        
        self.tk_img = ImageTk.PhotoImage(resized_img)
        self.canvas.delete("all")
        self.canvas.create_image(canvas_w//2, canvas_h//2, image=self.tk_img, anchor="center")
        self.current_display_size = new_size # Store for coordinate math

    def on_press(self, event):
        self.start_x, self.start_y = event.x, event.y
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, 1, 1, outline='lime', width=2)

    def on_drag(self, event):
        self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)

    def save_cropped_image(self, cropped_img):
        # 1. Get the original filename (e.g., "photo.jpg")
        original_full_path = self.image_list[self.current_index]
        original_filename = os.path.basename(original_full_path) # "photo.jpg"
        filename_no_ext = os.path.splitext(original_filename)[0] # "photo"

        # 2. Setup the GESTRACTOR folder one level above the image
        parent_dir = os.path.dirname(os.path.dirname(original_full_path))
        save_dir = os.path.join(parent_dir, "GESTRACTOR")
        
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        # 3. Track the number of crops for THIS specific file
        if filename_no_ext not in self.crop_counts:
            self.crop_counts[filename_no_ext] = 1
        else:
            self.crop_counts[filename_no_ext] += 1
        
        crop_number = self.crop_counts[filename_no_ext]

        # 4. Construct final path: GESTRACTOR/filename_1.png
        new_filename = f"{filename_no_ext}_{crop_number}.png"
        final_save_path = os.path.join(save_dir, new_filename)

        # 5. Save automatically without a popup (for speed!)
        cropped_img.save(final_save_path)
        print(f"Saved: {final_save_path}")

    def on_release(self, event):
        # Math to find the crop coordinates relative to the original image
        canvas_w = self.canvas.winfo_width()
        canvas_h = self.canvas.winfo_height()
        disp_w, disp_h = self.current_display_size
        
        offset_x = (canvas_w - disp_w) / 2
        offset_y = (canvas_h - disp_h) / 2
        
        total_scale = self.base_scale * self.zoom_level

        x1 = (min(self.start_x, event.x) - offset_x) / total_scale
        y1 = (min(self.start_y, event.y) - offset_y) / total_scale
        x2 = (max(self.start_x, event.x) - offset_x) / total_scale
        y2 = (max(self.start_y, event.y) - offset_y) / total_scale

        cropped = self.original_img.crop((x1, y1, x2, y2))
        self.save_cropped_image(cropped)
        
    def next_image(self):
        if self.image_list and self.current_index < len(self.image_list) - 1:
            self.current_index += 1
            self.display_image()

    def prev_image(self):
        if self.image_list and self.current_index > 0:
            self.current_index -= 1
            self.display_image()

if __name__ == "__main__":
    root = tk.Tk()
    app = ZoomCropper(root)
    root.mainloop()
    