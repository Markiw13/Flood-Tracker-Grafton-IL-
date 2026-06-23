import tkinter as tk
from PIL import Image, ImageTk
import requests
from io import BytesIO
import collections

# Corrected NOAA NWPS Endpoint & Graph Resources
API_URL = "https://api.water.noaa.gov/nwps/v1/gauges/GRFI2/stageflow"
IMAGE_URL = "https://water.noaa.gov/resources/hydrographs/grfi2_hg.png"
GATE_THRESHOLD = 18.5  

class GhostTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Grafton / Mel Price Onion-Skin Monitor")
        
        # 1. Hardware Screen Configuration
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg='black')
        
        # 2. Deque Cache: Holds exactly up to the last 20 downloaded images automatically
        self.history_cache = collections.deque(maxlen=20)
        
        # 3. GUI Layout Elements
        self.status_label = tk.Label(root, text="Building Timeline History...", font=("Arial", 22, "bold"), fg="white", bg="#333333", height=2)
        self.status_label.pack(fill=tk.X)
        
        self.image_label = tk.Label(root, bg='black')
        self.image_label.pack(expand=True, fill=tk.BOTH)
        
        self.root.bind("<Escape>", lambda e: self.root.destroy())
        
        # Start the processing sequence
        self.update_dashboard()

    def make_transparent_ghost(self, pil_img, opacity=0.15):
        """Converts an image background to transparent and drops its opacity down to a ghost layer."""
        rgba_img = pil_img.convert("RGBA")
        datas = rgba_img.getdata()
        
        # Turn background pixels (white/light gray grid canvas) completely clear
        new_data = []
        for item in datas:
            if item[0] > 240 and item[1] > 240 and item[2] > 240:
                new_data.append((255, 255, 255, 0))
            else:
                new_data.append((item[0], item[1], item[2], int(255 * opacity)))
                
        rgba_img.putdata(new_data)
        return rgba_img

    def update_dashboard(self):
        # --- PHASE A: PULL NOAA API STATUS ---
        try:
            headers = {"User-Agent": "RiverMonitorApp/1.0"}
            response = requests.get(API_URL, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                # Targets the latest indexed observed real-time depth value directly
                current_ft = float(data['observed']['data'][-1]['stage'])
                
                # Dynamic RED / GREEN Flag Gate Logic
                if current_ft >= GATE_THRESHOLD:
                    self.status_label.config(text=f"🔴 FLOOD GATES OPEN (Free River Flow) | {current_ft} FT", bg="#cc0000")
                else:
                    self.status_label.config(text=f"🟢 GATES CLOSED (Regulating Pool) | {current_ft} FT", bg="#006622")
            else:
                self.status_label.config(text="⚠️ NOAA API Service Busy", bg="#cc6600")
        except Exception:
            self.status_label.config(text="⚠️ Data Stream Interrupted", bg="#cc6600")

        # --- PHASE B: DOWNLOAD & RENDER COMBO TIMELINE MAP ---
        try:
            img_response = requests.get(IMAGE_URL, timeout=10)
            if img_response.status_code == 200:
                live_raw = Image.open(BytesIO(img_response.content)).convert("RGBA")
                
                # Optional small hardware panel resizing:
                # live_raw = live_raw.resize((720, 400), Image.Resampling.LANCZOS)
                
                ghost_frame = self.make_transparent_ghost(live_raw, opacity=0.12)
                self.history_cache.append(ghost_frame)
                
                composite_canvas = Image.new("RGBA", live_raw.size, (0, 0, 0, 255))
                
                for historical_ghost in self.history_cache:
                    composite_canvas = Image.alpha_composite(composite_canvas, historical_ghost)
                    
                composite_canvas = Image.alpha_composite(composite_canvas, live_raw)
                
                render_img = ImageTk.PhotoImage(composite_canvas)
                self.image_label.config(image=render_img)
                self.image_label.image = render_img  
        except Exception:
            pass

        # Cycle loop every 15 minutes (900000 ms)
        self.root.after(900000, self.update_dashboard)

if __name__ == "__main__":
    root = tk.Tk()
    app = GhostTrackerApp(root)
    root.mainloop()