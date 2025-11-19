"""
โปรแกรมตรวจจับรถยนต์จากวิดีโอ
ใช้ YOLO model สำหรับการตรวจจับวัตถุ
"""

import cv2
import numpy as np
from ultralytics import YOLO
import time
import os
import pyttsx3
from datetime import datetime
import threading
import sys
import locale

# ตั้งค่า encoding สำหรับ Windows
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())
    
# ตั้งค่า locale สำหรับภาษาไทย
try:
    locale.setlocale(locale.LC_ALL, 'th_TH.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_ALL, 'Thai_Thailand.874')
    except:
        pass

class CarDetector:
    def __init__(self, model_path='yolov8n.pt'):
        """
        เริ่มต้น CarDetector
        
        Args:
            model_path (str): เส้นทางไฟล์ YOLO model
        """
        print("กำลังโหลด YOLO model...")
        self.model = YOLO(model_path)
        
        # คลาสที่เกี่ยวข้องกับยานพาหนะ (COCO dataset)
        self.vehicle_classes = [2, 3, 5, 7]  # car, motorcycle, bus, truck
        self.class_names_th = {
            2: 'รถยนต์',
            3: 'จักรยานยนต์',
            5: 'รถบัส',
            7: 'รถบรรทุก'
        }
        self.class_names_en = {
            2: 'Car',
            3: 'Motorcycle',
            5: 'Bus',
            7: 'Truck'
        }
        # ใช้ภาษาอังกฤษเป็นค่าเริ่มต้นเพื่อหลีกเลี่ยงปัญหา encoding
        self.class_names = self.class_names_en
        self.use_thai = False
        
        # สีสำหรับ bounding boxes
        self.colors = {
            2: (0, 255, 0),    # เขียว - รถยนต์
            3: (255, 0, 0),    # น้ำเงิน - จักรยานยนต์
            5: (0, 0, 255),    # แดง - รถบัส
            7: (255, 255, 0)   # ฟ้า - รถบรรทุก
        }
        
        # การตั้งค่าเสียง
        self.enable_audio = True
        self.audio_interval = 5  # แจ้งเตือนทุก 5 วินาที
        self.last_audio_time = 0
        self.tts_engine = None
        self.init_tts()
        
        print("YOLO model loaded successfully!" if not self.use_thai else "โหลด model สำเร็จ!")
    
    def set_language(self, use_thai=False):
        """เปลี่ยนภาษาการแสดงผล"""
        self.use_thai = use_thai
        if use_thai:
            self.class_names = self.class_names_th
        else:
            self.class_names = self.class_names_en
    
    def init_tts(self):
        """เริ่มต้น Text-to-Speech engine"""
        try:
            self.tts_engine = pyttsx3.init()
            # ตั้งค่าเสียง
            self.tts_engine.setProperty('rate', 150)  # ความเร็วในการพูด
            self.tts_engine.setProperty('volume', 0.8)  # ระดับเสียง
            print("เสียง Text-to-Speech พร้อมใช้งาน")
        except Exception as e:
            print(f"Cannot initialize TTS: {e}" if not self.use_thai else f"ไม่สามารถเริ่มต้น TTS ได้: {e}")
            self.enable_audio = False
    
    def speak_timestamp(self, vehicle_count):
        """พูดเวลาและจำนวนรถที่ตรวจพบ"""
        if not self.enable_audio or not self.tts_engine:
            return
        
        current_time = time.time()
        if current_time - self.last_audio_time >= self.audio_interval:
            try:
                now = datetime.now()
                time_str = now.strftime("%H:%M:%S")
                
                if self.use_thai:
                    if vehicle_count > 0:
                        message = f"เวลา {time_str} ตรวจพบรถ {vehicle_count} คัน"
                    else:
                        message = f"เวลา {time_str} ไม่พบรถ"
                else:
                    if vehicle_count > 0:
                        message = f"Time {time_str}, detected {vehicle_count} vehicles"
                    else:
                        message = f"Time {time_str}, no vehicles detected"
                
                # ใช้ thread แยกเพื่อไม่ให้การพูดไปชะงักการประมวลผล
                threading.Thread(target=self._speak, args=(message,), daemon=True).start()
                self.last_audio_time = current_time
                
            except Exception as e:
                error_msg = f"Audio error: {e}" if not self.use_thai else f"ข้อผิดพลาดในการสร้างเสียง: {e}"
                print(error_msg)
    
    def _speak(self, text):
        """ฟังก์ชันพูดใน thread แยก"""
        try:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        except Exception as e:
            error_msg = f"Cannot speak: {e}" if not self.use_thai else f"ไม่สามารถพูดได้: {e}"
            print(error_msg)
    
    def set_audio_settings(self, enable=True, interval=5):
        """ตั้งค่าเสียง"""
        self.enable_audio = enable
        self.audio_interval = interval
    
    def detect_vehicles_in_frame(self, frame, confidence_threshold=0.5):
        """
        ตรวจจับยานพาหนะในเฟรมเดียว
        
        Args:
            frame: เฟรมจากวิดีโอ
            confidence_threshold: ค่าความเชื่อมั่นขั้นต่ำ
            
        Returns:
            tuple: (เฟรมที่มี annotation, จำนวนรถที่พบ, รายละเอียดการตรวจจับ)
        """
        results = self.model(frame)
        vehicle_count = 0
        detection_details = []
        
        for result in results:
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    # ดึงข้อมูลการตรวจจับ
                    confidence = float(box.conf[0])
                    class_id = int(box.cls[0])
                    
                    # ตรวจสอบว่าเป็นยานพาหนะและมีความเชื่อมั่นเพียงพอ
                    if class_id in self.vehicle_classes and confidence >= confidence_threshold:
                        # ดึงพิกัด bounding box
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                        
                        # เพิ่มจำนวนรถ
                        vehicle_count += 1
                        
                        # เก็บรายละเอียด
                        detection_details.append({
                            'class_name': self.class_names[class_id],
                            'confidence': confidence,
                            'bbox': (x1, y1, x2, y2)
                        })
                        
                        # วาด bounding box
                        color = self.colors[class_id]
                        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                        
                        # เขียนป้ายกำกับ
                        label = f"{self.class_names[class_id]}: {confidence:.2f}"
                        label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
                        
                        # สร้างพื้นหลังสำหรับข้อความ
                        cv2.rectangle(frame, (x1, y1 - label_size[1] - 10), 
                                    (x1 + label_size[0], y1), color, -1)
                        
                        # เขียนข้อความ
                        cv2.putText(frame, label, (x1, y1 - 5),
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # เพิ่มการแจ้งเตือนด้วยเสียง
        self.speak_timestamp(vehicle_count)
        
        return frame, vehicle_count, detection_details
    
    def process_video(self, video_path, output_path=None, show_preview=True):
        """
        ประมวลผลวิดีโอทั้งไฟล์
        
        Args:
            video_path: เส้นทางไฟล์วิดีโอ input
            output_path: เส้นทางไฟล์วิดีโอ output (ถ้าต้องการบันทึก)
            show_preview: แสดงตัวอย่างระหว่างประมวลผลหรือไม่
        """
        # เปิดวิดีโอ
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            error_msg = f"Cannot open video file: {video_path}" if not self.use_thai else f"ไม่สามารถเปิดไฟล์วิดีโอ: {video_path}"
            print(error_msg)
            return
        
        # ดึงข้อมูลวิดีโอ
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        if self.use_thai:
            print(f"ข้อมูลวิดีโอ:")
            print(f"  - ความละเอียด: {width}x{height}")
            print(f"  - FPS: {fps}")
            print(f"  - จำนวนเฟรม: {total_frames}")
        else:
            print(f"Video information:")
            print(f"  - Resolution: {width}x{height}")
            print(f"  - FPS: {fps}")
            print(f"  - Total frames: {total_frames}")
        
        # ตั้งค่า VideoWriter สำหรับบันทึกวิดีโอ (ถ้าต้องการ)
        out = None
        if output_path:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        # ตัวแปรสำหรับสถิติ
        frame_count = 0
        total_vehicles = 0
        start_time = time.time()
        
        print("\nเริ่มประมวลผลวิดีโอ...")
        print("กด 'q' เพื่อหยุดการประมวลผล")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            
            # ตรวจจับรถในเฟรม
            processed_frame, vehicle_count, details = self.detect_vehicles_in_frame(frame)
            total_vehicles += vehicle_count
            
            # เพิ่มข้อมูลสถิติและเวลาลงในเฟรม
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            stats_text = f"Frame: {frame_count}/{total_frames} | รถในเฟรม: {vehicle_count} | รวม: {total_vehicles}"
            time_text = f"เวลา: {current_time}"
            
            # แสดงสถิติ
            cv2.putText(processed_frame, stats_text, (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            
            # แสดงเวลา
            cv2.putText(processed_frame, time_text, (10, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
            
            # บันทึกเฟรม (ถ้าต้องการ)
            if out:
                out.write(processed_frame)
            
            # แสดงตัวอย่าง
            if show_preview:
                # ปรับขนาดเฟรมสำหรับแสดงผล (ถ้าใหญ่เกินไป)
                display_frame = processed_frame
                if width > 1280:
                    scale_factor = 1280 / width
                    new_width = int(width * scale_factor)
                    new_height = int(height * scale_factor)
                    display_frame = cv2.resize(processed_frame, (new_width, new_height))
                
                cv2.imshow('การตรวจจับรถยนต์', display_frame)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            
            # แสดงความคืบหน้า
            if frame_count % 30 == 0:  # แสดงทุก 30 เฟรม
                progress = (frame_count / total_frames) * 100
                elapsed_time = time.time() - start_time
                estimated_total_time = elapsed_time / (frame_count / total_frames)
                remaining_time = estimated_total_time - elapsed_time
                
                print(f"ความคืบหน้า: {progress:.1f}% "
                      f"({frame_count}/{total_frames} เฟรม) "
                      f"- เวลาคงเหลือประมาณ: {remaining_time:.0f} วินาที")
        
        # ปิดไฟล์
        cap.release()
        if out:
            out.release()
        cv2.destroyAllWindows()
        
        # แสดงสรุปผลลัพธ์
        total_time = time.time() - start_time
        print(f"\n=== สรุปผลลัพธ์ ===")
        print(f"ประมวลผลเสร็จสิ้น!")
        print(f"เวลาที่ใช้: {total_time:.2f} วินาที")
        print(f"ประมวลผล {frame_count} เฟรม")
        print(f"ความเร็วเฉลี่ย: {frame_count/total_time:.2f} FPS")
        print(f"พบรถทั้งหมด: {total_vehicles} คัน")
        if output_path:
            print(f"บันทึกวิดีโอที่: {output_path}")
    
    def process_webcam(self, camera_index=0):
        """
        ตรวจจับรถจากกล้อง webcam แบบ real-time
        
        Args:
            camera_index: index ของกล้อง (โดยปกติเป็น 0)
        """
        cap = cv2.VideoCapture(camera_index)
        
        if not cap.isOpened():
            error_msg = f"Cannot open camera index: {camera_index}" if not self.use_thai else f"ไม่สามารถเปิดกล้อง index: {camera_index}"
            print(error_msg)
            return
        
        start_msg = "Starting car detection from camera..." if not self.use_thai else "เริ่มตรวจจับรถจากกล้อง..."
        quit_msg = "Press 'q' to quit" if not self.use_thai else "กด 'q' เพื่อหยุด"
        print(start_msg)
        print(quit_msg)
        
        total_vehicles = 0
        frame_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            
            # ตรวจจับรถในเฟรม
            processed_frame, vehicle_count, details = self.detect_vehicles_in_frame(frame)
            total_vehicles += vehicle_count
            
            # เพิ่มข้อมูลสถิติและเวลา
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if self.use_thai:
                stats_text = f"Frame: {frame_count} | รถในเฟรม: {vehicle_count} | รวม: {total_vehicles}"
                time_text = f"เวลา: {current_time}"
                window_title = 'การตรวจจับรถยนต์ - Webcam'
            else:
                stats_text = f"Frame: {frame_count} | Vehicles: {vehicle_count} | Total: {total_vehicles}"
                time_text = f"Time: {current_time}"
                window_title = 'Car Detection - Webcam'
            
            # แสดงสถิติ
            cv2.putText(processed_frame, stats_text, (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            
            # แสดงเวลา
            cv2.putText(processed_frame, time_text, (10, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
            
            cv2.imshow(window_title, processed_frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()

def main():
    """ฟังก์ชันหลัก"""
    detector = CarDetector()
    
    # เลือกภาษา
    print("=== Car Detection Program ===")
    print("1. English")
    print("2. ไทย (Thai)")
    lang_choice = input("Select language / เลือกภาษา (1-2): ")
    
    use_thai = lang_choice == '2'
    detector.set_language(use_thai)
    
    if use_thai:
        print("\n=== โปรแกรมตรวจจับรถยนต์ ===")
        print("1. ประมวลผลจากไฟล์วิดีโอ")
        print("2. ตรวจจับจากกล้อง webcam")
        print("3. ออกจากโปรแกรม")
        choice_prompt = "\nเลือกตัวเลือก (1-3): "
    else:
        print("\n=== Car Detection Program ===")
        print("1. Process video file")
        print("2. Detect from webcam")
        print("3. Exit program")
        choice_prompt = "\nSelect option (1-3): "
    
    while True:
        choice = input(choice_prompt)
        
        if choice == '1':
            if use_thai:
                video_path = input("ใส่เส้นทางไฟล์วิดีโอ: ")
                save_prompt = "ต้องการบันทึกวิดีโอผลลัพธ์ไหม? (y/n): "
                output_prompt = "ใส่ชื่อไฟล์ output (เช่น output.mp4): "
                not_found_msg = "ไม่พบไฟล์วิดีโอ"
            else:
                video_path = input("Enter video file path: ")
                save_prompt = "Save output video? (y/n): "
                output_prompt = "Enter output filename (e.g., output.mp4): "
                not_found_msg = "Video file not found"
                
            if os.path.exists(video_path):
                save_output = input(save_prompt).lower()
                output_path = None
                if save_output == 'y':
                    output_path = input(output_prompt)
                
                detector.process_video(video_path, output_path)
            else:
                print(not_found_msg)
                
        elif choice == '2':
            detector.process_webcam()
            
        elif choice == '3':
            exit_msg = "ออกจากโปรแกรม" if use_thai else "Exiting program"
            print(exit_msg)
            break
            
        else:
            invalid_msg = "กรุณาเลือก 1, 2, หรือ 3" if use_thai else "Please select 1, 2, or 3"
            print(invalid_msg)

if __name__ == "__main__":
    main()