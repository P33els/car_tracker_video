"""
ตัวอย่างการใช้งานโปรแกรมตรวจจับรถยนต์แบบ GUI อย่างง่าย
"""

import tkinter as tk
from tkinter import messagebox
import os

def run_gui():
    """เรียกใช้โปรแกรม GUI"""
    try:
        # ตรวจสอบว่ามีไฟล์ GUI หรือไม่
        gui_file = "car_detection_gui.py"
        if not os.path.exists(gui_file):
            messagebox.showerror("ข้อผิดพลาด", f"ไม่พบไฟล์ {gui_file}")
            return
        
        # เรียกใช้โปรแกรม GUI
        import car_detection_gui
        car_detection_gui.main()
        
    except ImportError as e:
        messagebox.showerror("ข้อผิดพลาด", 
                           f"ไม่สามารถ import ได้: {e}\n"
                           f"กรุณาติดตั้ง packages ที่จำเป็น:\n"
                           f"pip install opencv-python ultralytics pillow")
    except Exception as e:
        messagebox.showerror("ข้อผิดพลาด", f"เกิดข้อผิดพลาด: {e}")

def run_cli():
    """เรียกใช้โปรแกรม Command Line"""
    try:
        # ตรวจสอบว่ามีไฟล์ CLI หรือไม่
        cli_file = "car_detection.py"
        if not os.path.exists(cli_file):
            messagebox.showerror("ข้อผิดพลาด", f"ไม่พบไฟล์ {cli_file}")
            return
        
        # เรียกใช้โปรแกรม CLI
        import car_detection
        car_detection.main()
        
    except ImportError as e:
        messagebox.showerror("ข้อผิดพลาด", 
                           f"ไม่สามารถ import ได้: {e}\n"
                           f"กรุณาติดตั้ง packages ที่จำเป็น:\n"
                           f"pip install opencv-python ultralytics")
    except Exception as e:
        messagebox.showerror("ข้อผิดพลาด", f"เกิดข้อผิดพลาด: {e}")

def main():
    """หน้าเลือกโปรแกรม"""
    root = tk.Tk()
    root.title("เลือกโปรแกรมตรวจจับรถยนต์")
    root.geometry("400x300")
    root.configure(bg='#f0f0f0')
    
    # หัวข้อ
    title_label = tk.Label(root, text="โปรแกรมตรวจจับรถยนต์", 
                          font=('Arial', 18, 'bold'), bg='#f0f0f0', fg='#2c3e50')
    title_label.pack(pady=30)
    
    # คำอธิบาย
    desc_label = tk.Label(root, text="เลือกรูปแบบโปรแกรมที่ต้องการใช้:", 
                         font=('Arial', 12), bg='#f0f0f0', fg='#34495e')
    desc_label.pack(pady=10)
    
    # ปุ่ม GUI
    gui_button = tk.Button(root, text="🖥️ โปรแกรมแบบ GUI\n(แนะนำสำหรับผู้ใช้ทั่วไป)", 
                          command=lambda: [root.destroy(), run_gui()],
                          bg='#3498db', fg='white', font=('Arial', 12, 'bold'),
                          width=25, height=3, relief='raised', bd=3)
    gui_button.pack(pady=15)
    
    # ปุ่ม CLI
    cli_button = tk.Button(root, text="💻 โปรแกรมแบบ Command Line\n(สำหรับผู้ใช้ขั้นสูง)", 
                          command=lambda: [root.destroy(), run_cli()],
                          bg='#2ecc71', fg='white', font=('Arial', 12, 'bold'),
                          width=25, height=3, relief='raised', bd=3)
    cli_button.pack(pady=15)
    
    # ปุ่มออก
    exit_button = tk.Button(root, text="❌ ออกจากโปรแกรม", 
                           command=root.destroy,
                           bg='#e74c3c', fg='white', font=('Arial', 10, 'bold'),
                           width=20, height=2, relief='raised', bd=2)
    exit_button.pack(pady=20)
    
    # ข้อมูลเพิ่มเติม
    info_label = tk.Label(root, text="ต้องการ: Python 3.7+, OpenCV, YOLO", 
                         font=('Arial', 9), bg='#f0f0f0', fg='#7f8c8d')
    info_label.pack(side='bottom', pady=10)
    
    root.mainloop()

if __name__ == "__main__":
    main()