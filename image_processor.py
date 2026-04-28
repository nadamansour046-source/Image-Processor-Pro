import cv2
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk, ImageEnhance, ImageFilter
import os
from datetime import datetime

class ImageProcessorApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("✨ Image Processor Pro")
        self.root.geometry("1200x700")
        self.root.configure(bg="#1e1e1e")
        
        # متغيرات
        self.img_path = None
        self.original_cv = None
        self.current_cv = None
        
        self.setup_styles()
        self.create_widgets()
        
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure("TButton", padding=10, font=("Segoe UI", 10, "bold"))
        style.configure("Title.TLabel", font=("Segoe UI", 16, "bold"), foreground="#E13F7C")
        
    def create_widgets(self):
        # عنوان التطبيق
        title = ttk.Label(self.root, text="Image Processor Pro", style="Title.TLabel")
        title.pack(pady=15)

        # Frame للأزرار
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(pady=10, fill="x", padx=20)

        ttk.Button(btn_frame, text="📤 Upload Image", command=self.load_image).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="🔄 Process Image", command=self.process_image).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="💾 Save Result", command=self.save_image).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="🗑️ Clear All", command=self.clear_all).pack(side="left", padx=5)

        # المنطقة الرئيسية للصور
        self.main_frame = tk.Frame(self.root, bg="#1e1e1e")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # إنشاء Panels
        self.panels = {}
        titles = ["Original", "Grayscale", "Blurred", "Edges", "Enhanced"]
        
        for i, title_text in enumerate(titles):
            frame = tk.Frame(self.main_frame, bg="#2d2d2d", relief="ridge", bd=2)
            frame.grid(row=0, column=i, padx=8, pady=8, sticky="nsew")
            
            lbl_title = tk.Label(frame, text=title_text, bg="#2d2d2d", fg="#00ddff", 
                               font=("Segoe UI", 11, "bold"))
            lbl_title.pack(pady=5)
            
            panel = tk.Label(frame, bg="#1e1e1e")
            panel.pack(padx=10, pady=10)
            
            self.panels[title_text.lower().replace(" ", "_")] = panel

        # تهيئة أعمدة الـ grid
        for i in range(5):
            self.main_frame.columnconfigure(i, weight=1)
        self.main_frame.rowconfigure(0, weight=1)

        # شريط الحالة
        self.status_var = tk.StringVar(value="Ready - Upload an image to begin")
        status_bar = tk.Label(self.root, textvariable=self.status_var, 
                            bg="#1e1e1e", fg="#aaaaaa", anchor="w", padx=15, pady=8)
        status_bar.pack(side="bottom", fill="x")

    def load_image(self):
        path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.tiff")]
        )
        if not path:
            return
            
        self.img_path = path
        self.original_cv = cv2.imread(path)
        
        if self.original_cv is None:
            messagebox.showerror("Error", "Failed to load image!")
            return
            
        self.show_image(self.original_cv, self.panels["original"])
        self.status_var.set(f"Loaded: {os.path.basename(path)}")
        
    def show_image(self, cv_img, panel):
        """تحويل صورة OpenCV وعرضها في Label"""
        if len(cv_img.shape) == 2:  # صورة رمادية
            cv_img = cv2.cvtColor(cv_img, cv2.COLOR_GRAY2RGB)
        else:
            cv_img = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
            
        img_pil = Image.fromarray(cv_img)
        img_pil = img_pil.resize((220, 220), Image.LANCZOS)
        photo = ImageTk.PhotoImage(img_pil)
        
        panel.config(image=photo)
        panel.image = photo  # الحفاظ على المرجع

    def process_image(self):
        if self.original_cv is None:
            messagebox.showwarning("Warning", "Please upload an image first!")
            return

        self.status_var.set("Processing... Please wait")
        self.root.update()

        try:
            img = self.original_cv.copy()
            
            # 1. Grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            self.show_image(gray, self.panels["grayscale"])

            # 2. Gaussian Blur
            blurred = cv2.GaussianBlur(img, (7, 7), 0)
            self.show_image(blurred, self.panels["blurred"])

            # 3. Canny Edges
            edges = cv2.Canny(gray, 50, 150)
            self.show_image(edges, self.panels["edges"])

            # 4. Enhanced (Brightness + Contrast + Sharpness)
            pil_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
            enhancer = ImageEnhance.Contrast(pil_img)
            enhanced = enhancer.enhance(1.5)
            enhancer = ImageEnhance.Brightness(enhanced)
            enhanced = enhancer.enhance(1.1)
            enhanced = enhanced.filter(ImageFilter.SHARPEN)
            
            enhanced_cv = cv2.cvtColor(np.array(enhanced), cv2.COLOR_RGB2BGR)
            self.show_image(enhanced_cv, self.panels["enhanced"])
            
            self.current_cv = enhanced_cv  # حفظ آخر صورة معالجة
            self.status_var.set("Processing completed successfully ✓")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred:\n{str(e)}")
            self.status_var.set("Processing failed")

    def save_image(self):
        if self.current_cv is None:
            messagebox.showwarning("Warning", "No processed image to save!")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".jpg",
            filetypes=[("JPEG", "*.jpg"), ("PNG", "*.png"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                cv2.imwrite(file_path, self.current_cv)
                messagebox.showinfo("Success", f"Image saved successfully!\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save image:\n{str(e)}")

    def clear_all(self):
        if messagebox.askyesno("Clear All", "Are you sure you want to clear all images?"):
            for panel in self.panels.values():
                panel.config(image="")
            self.img_path = None
            self.original_cv = None
            self.current_cv = None
            self.status_var.set("All cleared - Ready for new image")

    def run(self):
        self.root.mainloop()


# تشغيل التطبيق
if __name__ == "__main__":
    import numpy as np   # أضفنا هذا للـ enhanced
    app = ImageProcessorApp()
    app.run()