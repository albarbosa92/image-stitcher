import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageDraw, ImageFont
import os
import gc
import subprocess

COLORS_MAP = {
    "White": (255, 255, 255),
    "Black": (0, 0, 0),
    "Yellow": (255, 230, 0),
    "Red": (235, 30, 30),
    "Blue": (0, 120, 255),
    "Green": (0, 200, 70)
}

FORMATS_MAP = {
    "PNG (.png)": (".png", [("PNG Image", "*.png")]),
    "JPG (.jpg)": (".jpg", [("JPEG Image", "*.jpg;*.jpeg")]),
    "TIFF (.tif)": (".tif", [("TIFF Image", "*.tif;*.tiff")])
}

selected_files = []

def convert_image_safe(path):
    """Sanitizes TIFFs using ImageMagick if available, falling back to Pillow."""
    base_name = os.path.splitext(path)[0]
    temp_png = f"{base_name}_temp_safe.png"
    try:
        subprocess.run(['magick', path, '-colorspace', 'sRGB', '-type', 'truecolor', temp_png], 
                       check=True, creationflags=subprocess.CREATE_NO_WINDOW)
        return temp_png, True
    except:
        try:
            with Image.open(path) as img:
                img.convert("RGB").save(temp_png, "PNG")
            return temp_png, True
        except:
            return path, False

def add_images():
    try:
        rows = int(entry_rows.get())
        cols = int(entry_cols.get())
        max_capacity = rows * cols
    except:
        messagebox.showerror("Error", "Please enter valid numbers for rows and columns.")
        return

    new_files = filedialog.askopenfilenames(
        title="Select one or more images",
        filetypes=[("Images", "*.png *.jpg *.jpeg *.tif *.tiff"), ("All files", "*.*")]
    )
    
    if not new_files:
        return

    for f in new_files:
        if len(selected_files) >= max_capacity:
            messagebox.showwarning("Limit Reached", f"The {rows}x{cols} grid holds a maximum of {max_capacity} images.")
            break
        selected_files.append(f)
    
    update_listbox()

def remove_selected(event=None):
    indices = listbox.curselection()
    if not indices: return
    for idx in reversed(indices):
        selected_files.pop(idx)
    update_listbox()

def clear_all():
    selected_files.clear()
    update_listbox()

def move_up():
    indices = listbox.curselection()
    if len(indices) != 1 or indices[0] == 0: return
    i = indices[0]
    selected_files[i], selected_files[i-1] = selected_files[i-1], selected_files[i]
    update_listbox()
    listbox.selection_set(i-1)

def move_down():
    indices = listbox.curselection()
    if len(indices) != 1 or indices[0] == len(selected_files)-1: return
    i = indices[0]
    selected_files[i], selected_files[i+1] = selected_files[i+1], selected_files[i]
    update_listbox()
    listbox.selection_set(i+1)

def update_listbox():
    listbox.delete(0, tk.END)
    labels = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    for i, f in enumerate(selected_files):
        prefix = f"[{labels[i]}] " if i < len(labels) else ""
        parent_folder = os.path.basename(os.path.dirname(f))
        listbox.insert(tk.END, f"{prefix}{os.path.basename(f)}  ({parent_folder})")
    lbl_count.config(text=f"Images in list: {len(selected_files)}")

def calculate_text_coords(x_pos, y_pos, single_w, single_h, text, font, pos_choice):
    margin = 40
    bbox = font.getbbox(text)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    if "Left" in pos_choice:
        tx = x_pos + margin
    elif "Right" in pos_choice:
        tx = x_pos + single_w - text_w - margin
    else:
        tx = x_pos + (single_w - text_w) // 2

    if "Top" in pos_choice:
        ty = y_pos + margin
    else:
        ty = y_pos + single_h - text_h - margin - 10

    return tx, ty

def start_processing():
    if not selected_files:
        messagebox.showwarning("Warning", "Please add at least one image before generating the figure.")
        return

    try:
        rows = int(entry_rows.get())
        cols = int(entry_cols.get())
        if len(selected_files) > rows * cols:
            messagebox.showerror("Error", f"You have {len(selected_files)} images in the list, but the {rows}x{cols} grid only fits {rows*cols}.")
            return
    except:
        messagebox.showerror("Error", "Please enter valid numbers for rows and columns.")
        return

    label_pos = combo_pos.get()
    text_color = COLORS_MAP[combo_color.get()]
    use_shadow = var_shadow.get()
    export_format = combo_format.get()

    root.withdraw()
    process_and_save(list(selected_files), rows, cols, label_pos, text_color, use_shadow, export_format)
    root.deiconify()

def process_and_save(files, rows, cols, label_pos, text_color, use_shadow, export_format):
    temp_files_to_clean = []
    try:
        max_width = 1800
        padding = 20
        labels = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        imgs = []
        
        for path in files:
            work_path, was_converted = convert_image_safe(path)
            if was_converted: temp_files_to_clean.append(work_path)

            with Image.open(work_path) as temp_img:
                w_percent = (max_width / float(temp_img.size[0]))
                h_size = int((float(temp_img.size[1]) * float(w_percent)))
                imgs.append(temp_img.convert("RGB").resize((max_width, h_size), Image.Resampling.LANCZOS))
            gc.collect()

        single_w, single_h = imgs[0].size
        canvas_w = (single_w * cols) + (padding * (cols - 1))
        canvas_h = (single_h * rows) + (padding * (rows - 1))
        
        canvas = Image.new('RGB', (canvas_w, canvas_h), (255, 255, 255))
        draw = ImageDraw.Draw(canvas)
        
        try:
            font = ImageFont.truetype("arialbd.ttf", 80)
        except:
            try:
                font = ImageFont.truetype("arial.ttf", 80)
            except:
                font = ImageFont.load_default()

        stroke_color = (255, 255, 255) if text_color == (0, 0, 0) else (0, 0, 0)
        stroke_w = 4 if use_shadow else 0

        for i, img in enumerate(imgs):
            r, c = divmod(i, cols)
            x_pos = c * (single_w + padding)
            y_pos = r * (single_h + padding)
            
            canvas.paste(img, (x_pos, y_pos))
            
            tx, ty = calculate_text_coords(x_pos, y_pos, single_w, single_h, labels[i], font, label_pos)
            
            if use_shadow:
                draw.text((tx + 4, ty + 4), labels[i], fill=stroke_color, font=font)
            
            draw.text((tx, ty), labels[i], fill=text_color, font=font, 
                      stroke_width=stroke_w, stroke_fill=stroke_color)

        default_ext, file_filter = FORMATS_MAP[export_format]

        save_path = filedialog.asksaveasfilename(
            title=f"Save Final Figure ({default_ext.upper()})",
            defaultextension=default_ext,
            filetypes=file_filter
        )
        
        if save_path:
            save_path = os.path.normpath(save_path)
            
            if not save_path.lower().endswith(default_ext):
                save_path += default_ext

            if default_ext == ".png":
                canvas.save(save_path, format="PNG", dpi=(300, 300), optimize=True)
            elif default_ext == ".jpg":
                canvas.convert("RGB").save(save_path, format="JPEG", quality=95, subsampling=0, dpi=(300, 300))
            elif default_ext == ".tif":
                canvas.save(save_path, format="TIFF", compression="tiff_lzw", dpi=(300, 300))

            subprocess.run(['explorer', '/select,', save_path])
        
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save: {e}")
    finally:
        for f in temp_files_to_clean:
            try: os.remove(f)
            except: pass
        gc.collect()

# --- Main GUI ---
root = tk.Tk()
root.title("Image Stitcher Pro")
root.geometry("500x610")

# Frame 1: Grid and Export Format
frame_grid = tk.LabelFrame(root, text="1. Grid & Export Format", padx=10, pady=8, font=('Arial', 9, 'bold'))
frame_grid.pack(fill=tk.X, padx=15, pady=(10, 5))

tk.Label(frame_grid, text="Rows:").grid(row=0, column=0, padx=(0, 3))
entry_rows = tk.Entry(frame_grid, justify='center', width=5)
entry_rows.insert(0, "3")
entry_rows.grid(row=0, column=1, padx=(0, 12))

tk.Label(frame_grid, text="Columns:").grid(row=0, column=2, padx=(0, 3))
entry_cols = tk.Entry(frame_grid, justify='center', width=5)
entry_cols.insert(0, "2")
entry_cols.grid(row=0, column=3, padx=(0, 15))

tk.Label(frame_grid, text="Export as:").grid(row=0, column=4, padx=(5, 3))
combo_format = ttk.Combobox(frame_grid, values=list(FORMATS_MAP.keys()), state="readonly", width=11)
combo_format.set("PNG (.png)")
combo_format.grid(row=0, column=5)

# Frame 2: Label Styling
frame_text = tk.LabelFrame(root, text="2. Label Style (A, B, C...)", padx=10, pady=8, font=('Arial', 9, 'bold'))
frame_text.pack(fill=tk.X, padx=15, pady=5)

tk.Label(frame_text, text="Position:").grid(row=0, column=0, sticky="w", pady=2)
position_options = [
    "Top Left", "Top Center", "Top Right",
    "Bottom Left", "Bottom Center", "Bottom Right"
]
combo_pos = ttk.Combobox(frame_text, values=position_options, state="readonly", width=18)
combo_pos.set("Top Left")
combo_pos.grid(row=0, column=1, padx=5, pady=2)

tk.Label(frame_text, text="Color:").grid(row=0, column=2, sticky="w", padx=(10, 0), pady=2)
combo_color = ttk.Combobox(frame_text, values=list(COLORS_MAP.keys()), state="readonly", width=10)
combo_color.set("White")
combo_color.grid(row=0, column=3, padx=5, pady=2)

var_shadow = tk.BooleanVar(value=True)
chk_shadow = tk.Checkbutton(frame_text, text="Add outline / drop shadow for high contrast", variable=var_shadow)
chk_shadow.grid(row=1, column=0, columnspan=4, sticky="w", pady=(5, 0))

# Frame 3: Image Selection & Sequence
frame_files = tk.LabelFrame(root, text="3. Images & Sequence (Multi-folder)", padx=10, pady=8, font=('Arial', 9, 'bold'))
frame_files.pack(expand=True, fill=tk.BOTH, padx=15, pady=5)

btn_top_frame = tk.Frame(frame_files)
btn_top_frame.pack(fill=tk.X, pady=(0, 5))

tk.Button(btn_top_frame, text="+ Add Images", command=add_images, bg="#007bff", fg="white", font=('Arial', 9, 'bold')).pack(side=tk.LEFT, padx=(0, 5))
tk.Button(btn_top_frame, text="Remove", command=remove_selected).pack(side=tk.LEFT, padx=2)
tk.Button(btn_top_frame, text="Clear All", command=clear_all).pack(side=tk.LEFT, padx=2)

lbl_count = tk.Label(btn_top_frame, text="Images in list: 0", font=('Arial', 8, 'italic'))
lbl_count.pack(side=tk.RIGHT)

list_frame = tk.Frame(frame_files)
list_frame.pack(expand=True, fill=tk.BOTH)

listbox = tk.Listbox(list_frame, selectmode=tk.EXTENDED, font=('Arial', 9))
listbox.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
listbox.bind('<Delete>', remove_selected)

scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=listbox.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
listbox.config(yscrollcommand=scrollbar.set)

btn_order_frame = tk.Frame(frame_files)
btn_order_frame.pack(fill=tk.X, pady=(5, 0))
tk.Button(btn_order_frame, text="↑ Move Up", command=move_up, width=12).pack(side=tk.LEFT, padx=5)
tk.Button(btn_order_frame, text="↓ Move Down", command=move_down, width=12).pack(side=tk.LEFT, padx=5)

# Generate Button
tk.Button(root, text="GENERATE & SAVE FIGURE", command=start_processing, 
          bg="#28a745", fg="white", font=('Arial', 11, 'bold'), height=2).pack(fill=tk.X, padx=15, pady=(5, 15))

root.mainloop()