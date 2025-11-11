"""
โปรแกรมตรวจจับรถยนต์จากวิดีโอ พร้อม GUI
ใช้ YOLO model สำหรับการตรวจจับวัตถุ
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import cv2
import numpy as np
from ultralytics import YOLO
import time
import os
from PIL import Image, ImageTk
import threading

class CarDetectorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("โปรแกรมตรวจจับรถยนต์")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        
        # ตัวแปรสำหรับการควบคุม
        self.detector = None
        self.is_processing = False
        self.cap = None
        self.video_thread = None
        
        # ตัวแปรสถิติ
        self.total_vehicles = 0
        self.current_frame = 0
        self.total_frames = 0
        
        # สร้าง GUI
        self.create_widgets()
        self.load_model()
    
    def create_widgets(self):
        """สร้างส่วนประกอบ GUI"""
        
        # หัวข้อหลัก
        title_frame = tk.Frame(self.root, bg='#2c3e50', height=60)
        title_frame.pack(fill='x', padx=5, pady=5)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(title_frame, text="โปรแกรมตรวจจับรถยนต์", 
                              font=('Arial', 20, 'bold'), fg='white', bg='#2c3e50')
        title_label.pack(expand=True)
        
        # เฟรมหลัก
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # แผงควบคุมซ้าย
        control_frame = tk.Frame(main_frame, bg='#ecf0f1', width=300, relief='raised', bd=2)
        control_frame.pack(side='left', fill='y', padx=(0, 10))
        control_frame.pack_propagate(False)
        
        # แผงแสดงผลวิดีโอขวา
        video_frame = tk.Frame(main_frame, bg='#34495e', relief='raised', bd=2)
        video_frame.pack(side='right', fill='both', expand=True)
        
        # === แผงควบคุม ===
        
        # กลุ่มการเลือกไฟล์
        file_group = tk.LabelFrame(control_frame, text="เลือกไฟล์วิดีโอ", 
                                  font=('Arial', 12, 'bold'), bg='#ecf0f1', fg='#2c3e50')
        file_group.pack(fill='x', padx=10, pady=10)
        
        self.file_path_var = tk.StringVar()
        file_entry = tk.Entry(file_group, textvariable=self.file_path_var, width=35)
        file_entry.pack(padx=10, pady=5)
        
        file_button = tk.Button(file_group, text="เลือกไฟล์วิดีโอ", 
                               command=self.select_video_file, bg='#3498db', fg='white',
                               font=('Arial', 10, 'bold'))
        file_button.pack(padx=10, pady=5)
        
        # กลุ่มการตั้งค่า
        settings_group = tk.LabelFrame(control_frame, text="การตั้งค่า", 
                                      font=('Arial', 12, 'bold'), bg='#ecf0f1', fg='#2c3e50')
        settings_group.pack(fill='x', padx=10, pady=10)
        
        # ความเชื่อมั่น
        tk.Label(settings_group, text="ระดับความเชื่อมั่น:", bg='#ecf0f1').pack(anchor='w', padx=10)
        self.confidence_var = tk.DoubleVar(value=0.5)
        confidence_scale = tk.Scale(settings_group, from_=0.1, to=0.9, resolution=0.1,
                                   orient='horizontal', variable=self.confidence_var, bg='#ecf0f1')
        confidence_scale.pack(fill='x', padx=10, pady=5)
        
        # บันทึกผลลัพธ์
        self.save_output_var = tk.BooleanVar()
        save_check = tk.Checkbutton(settings_group, text="บันทึกวิดีโอผลลัพธ์", 
                                   variable=self.save_output_var, bg='#ecf0f1')
        save_check.pack(anchor='w', padx=10, pady=5)
        
        # กลุ่มปุ่มควบคุม
        control_group = tk.LabelFrame(control_frame, text="ควบคุมการทำงาน", 
                                     font=('Arial', 12, 'bold'), bg='#ecf0f1', fg='#2c3e50')
        control_group.pack(fill='x', padx=10, pady=10)
        
        self.start_button = tk.Button(control_group, text="เริ่มประมวลผล", 
                                     command=self.start_processing, bg='#27ae60', fg='white',
                                     font=('Arial', 12, 'bold'), height=2)
        self.start_button.pack(fill='x', padx=10, pady=5)
        
        self.webcam_button = tk.Button(control_group, text="เริ่มกล้อง Webcam", 
                                      command=self.start_webcam, bg='#e67e22', fg='white',
                                      font=('Arial', 12, 'bold'), height=2)
        self.webcam_button.pack(fill='x', padx=10, pady=5)
        
        self.stop_button = tk.Button(control_group, text="หยุดการทำงาน", 
                                    command=self.stop_processing, bg='#e74c3c', fg='white',
                                    font=('Arial', 12, 'bold'), height=2, state='disabled')
        self.stop_button.pack(fill='x', padx=10, pady=5)
        
        # กลุ่มสถิติ
        stats_group = tk.LabelFrame(control_frame, text="สถิติการตรวจจับ", 
                                   font=('Arial', 12, 'bold'), bg='#ecf0f1', fg='#2c3e50')
        stats_group.pack(fill='x', padx=10, pady=10)
        
        self.frame_label = tk.Label(stats_group, text="เฟรม: 0/0", bg='#ecf0f1', font=('Arial', 10))
        self.frame_label.pack(anchor='w', padx=10, pady=2)
        
        self.vehicles_label = tk.Label(stats_group, text="รถในเฟรม: 0", bg='#ecf0f1', font=('Arial', 10))
        self.vehicles_label.pack(anchor='w', padx=10, pady=2)
        
        self.total_label = tk.Label(stats_group, text="รถทั้งหมด: 0", bg='#ecf0f1', font=('Arial', 10))
        self.total_label.pack(anchor='w', padx=10, pady=2)
        
        self.fps_label = tk.Label(stats_group, text="FPS: 0", bg='#ecf0f1', font=('Arial', 10))
        self.fps_label.pack(anchor='w', padx=10, pady=2)
        
        # Progress Bar
        self.progress = ttk.Progressbar(control_frame, length=280, mode='determinate')
        self.progress.pack(padx=10, pady=10)
        
        # === แผงแสดงผลวิดีโอ ===
        
        # Canvas สำหรับแสดงวิดีโอ
        self.canvas = tk.Canvas(video_frame, bg='black')
        self.canvas.pack(fill='both', expand=True, padx=10, pady=10)
        
        # ข้อความเริ่มต้น
        self.canvas.create_text(400, 300, text="เลือกไฟล์วิดีโอหรือเริ่มกล้อง Webcam", 
                               fill='white', font=('Arial', 16))
    
    def load_model(self):
        """โหลด YOLO model"""
        try:
            model_path = 'yolov8n.pt'
            if not os.path.exists(model_path):
                messagebox.showwarning("แจ้งเตือน", 
                                     f"ไม่พบไฟล์ model: {model_path}\n"
                                     f"โปรแกรมจะดาวน์โหลดอัตโนมัติเมื่อใช้งานครั้งแรก")
            
            from car_detection import CarDetector
            self.detector = CarDetector(model_path)
            messagebox.showinfo("สำเร็จ", "โหลด YOLO model เสร็จสิ้น!")
            
        except Exception as e:
            messagebox.showerror("ข้อผิดพลาด", f"ไม่สามารถโหลด model ได้: {str(e)}")
    
    def select_video_file(self):
        """เลือกไฟล์วิดีโอ"""
        file_path = filedialog.askopenfilename(
            title="เลือกไฟล์วิดีโอ",
            filetypes=[
                ("Video files", "*.mp4 *.avi *.mov *.mkv *.wmv *.flv"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            self.file_path_var.set(file_path)
    
    def start_processing(self):
        """เริ่มประมวลผลวิดีโอ"""
        if not self.detector:
            messagebox.showerror("ข้อผิดพลาด", "ยังไม่ได้โหลด model")
            return
        
        video_path = self.file_path_var.get()
        if not video_path or not os.path.exists(video_path):
            messagebox.showerror("ข้อผิดพลาด", "กรุณาเลือกไฟล์วิดีโอก่อน")
            return
        
        if self.is_processing:
            return
        
        # เปลี่ยนสถานะปุ่ม
        self.start_button.config(state='disabled')
        self.webcam_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.is_processing = True
        
        # เริ่ม thread สำหรับประมวลผล
        self.video_thread = threading.Thread(target=self.process_video_thread, args=(video_path,))
        self.video_thread.daemon = True
        self.video_thread.start()
    
    def start_webcam(self):
        """เริ่มกล้อง webcam"""
        if not self.detector:
            messagebox.showerror("ข้อผิดพลาด", "ยังไม่ได้โหลด model")
            return
        
        if self.is_processing:
            return
        
        # เปลี่ยนสถานะปุ่ม
        self.start_button.config(state='disabled')
        self.webcam_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.is_processing = True
        
        # เริ่ม thread สำหรับ webcam
        self.video_thread = threading.Thread(target=self.process_webcam_thread)
        self.video_thread.daemon = True
        self.video_thread.start()
    
    def stop_processing(self):
        """หยุดการประมวลผล"""
        self.is_processing = False
        if self.cap:
            self.cap.release()
        
        # เปลี่ยนสถานะปุ่ม
        self.start_button.config(state='normal')
        self.webcam_button.config(state='normal')
        self.stop_button.config(state='disabled')
        
        # ล้างหน้าจอ
        self.canvas.delete("all")
        self.canvas.create_text(400, 300, text="การประมวลผลหยุดแล้ว", 
                               fill='white', font=('Arial', 16))
    
    def process_video_thread(self, video_path):
        """ประมวลผลวิดีโอใน thread แยก"""
        try:
            self.cap = cv2.VideoCapture(video_path)
            if not self.cap.isOpened():
                messagebox.showerror("ข้อผิดพลาด", f"ไม่สามารถเปิดไฟล์วิดีโอได้: {video_path}")
                return
            
            # ดึงข้อมูลวิดีโอ
            self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = self.cap.get(cv2.CAP_PROP_FPS)
            
            # ตั้งค่า output (ถ้าต้องการบันทึก)
            out = None
            if self.save_output_var.get():
                output_path = filedialog.asksaveasfilename(
                    defaultextension=".mp4",
                    filetypes=[("MP4 files", "*.mp4"), ("All files", "*.*")]
                )
                if output_path:
                    width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                    height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
            
            self.total_vehicles = 0
            frame_count = 0
            start_time = time.time()
            
            while self.is_processing:
                ret, frame = self.cap.read()
                if not ret:
                    break
                
                frame_count += 1
                self.current_frame = frame_count
                
                # ตรวจจับรถ
                processed_frame, vehicle_count, _ = self.detector.detect_vehicles_in_frame(
                    frame, self.confidence_var.get()
                )
                self.total_vehicles += vehicle_count
                
                # บันทึกเฟรม (ถ้าต้องการ)
                if out:
                    out.write(processed_frame)
                
                # แสดงผลใน GUI
                self.update_display(processed_frame, vehicle_count, fps, start_time, frame_count)
                
                # อัปเดต progress
                progress = (frame_count / self.total_frames) * 100
                self.progress['value'] = progress
                
                time.sleep(0.033)  # ประมาณ 30 FPS
            
            # ปิดไฟล์
            if out:
                out.release()
            self.cap.release()
            
            if frame_count >= self.total_frames:
                messagebox.showinfo("เสร็จสิ้น", "ประมวลผลวิดีโอเสร็จสิ้นแล้ว!")
            
        except Exception as e:
            messagebox.showerror("ข้อผิดพลาด", f"เกิดข้อผิดพลาดในการประมวลผล: {str(e)}")
        
        finally:
            self.is_processing = False
            self.root.after(0, self.stop_processing)
    
    def process_webcam_thread(self):
        """ประมวลผล webcam ใน thread แยก"""
        try:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                messagebox.showerror("ข้อผิดพลาด", "ไม่สามารถเปิดกล้อง webcam ได้")
                return
            
            self.total_vehicles = 0
            frame_count = 0
            start_time = time.time()
            
            while self.is_processing:
                ret, frame = self.cap.read()
                if not ret:
                    break
                
                frame_count += 1
                self.current_frame = frame_count
                
                # ตรวจจับรถ
                processed_frame, vehicle_count, _ = self.detector.detect_vehicles_in_frame(
                    frame, self.confidence_var.get()
                )
                self.total_vehicles += vehicle_count
                
                # แสดงผลใน GUI
                self.update_display(processed_frame, vehicle_count, 30, start_time, frame_count)
                
                time.sleep(0.033)  # ประมาณ 30 FPS
            
            self.cap.release()
            
        except Exception as e:
            messagebox.showerror("ข้อผิดพลาด", f"เกิดข้อผิดพลาดในการใช้ webcam: {str(e)}")
        
        finally:
            self.is_processing = False
            self.root.after(0, self.stop_processing)
    
    def update_display(self, frame, vehicle_count, fps, start_time, frame_count):
        """อัปเดตการแสดงผลใน GUI"""
        try:
            # แปลงเฟรมสำหรับแสดงใน tkinter
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # ปรับขนาดเฟรมให้พอดีกับ canvas
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            if canvas_width > 1 and canvas_height > 1:
                h, w = frame_rgb.shape[:2]
                scale = min(canvas_width/w, canvas_height/h)
                new_w, new_h = int(w*scale), int(h*scale)
                
                frame_resized = cv2.resize(frame_rgb, (new_w, new_h))
                
                # แปลงเป็น PIL Image และ PhotoImage
                pil_image = Image.fromarray(frame_resized)
                photo = ImageTk.PhotoImage(pil_image)
                
                # แสดงใน canvas
                self.canvas.delete("all")
                x = (canvas_width - new_w) // 2
                y = (canvas_height - new_h) // 2
                self.canvas.create_image(x, y, anchor='nw', image=photo)
                
                # เก็บ reference ไว้ป้องกันการถูก garbage collect
                self.canvas.image = photo
            
            # อัปเดตสถิติ
            elapsed_time = time.time() - start_time
            current_fps = frame_count / elapsed_time if elapsed_time > 0 else 0
            
            self.root.after(0, lambda: self.update_stats(vehicle_count, current_fps))
            
        except Exception as e:
            print(f"ข้อผิดพลาดในการแสดงผล: {e}")
    
    def update_stats(self, vehicle_count, current_fps):
        """อัปเดตข้อมูลสถิติ"""
        if self.total_frames > 0:
            self.frame_label.config(text=f"เฟรม: {self.current_frame}/{self.total_frames}")
        else:
            self.frame_label.config(text=f"เฟรม: {self.current_frame}")
        
        self.vehicles_label.config(text=f"รถในเฟรม: {vehicle_count}")
        self.total_label.config(text=f"รถทั้งหมด: {self.total_vehicles}")
        self.fps_label.config(text=f"FPS: {current_fps:.1f}")

def main():
    """ฟังก์ชันหลัก"""
    root = tk.Tk()
    app = CarDetectorGUI(root)
    
    # ปิดโปรแกรมอย่างถูกต้องเมื่อกดปิดหน้าต่าง
    def on_closing():
        if app.is_processing:
            app.stop_processing()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()