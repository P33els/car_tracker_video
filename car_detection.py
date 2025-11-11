"""
โปรแกรมตรวจจับรถยนต์จากวิดีโอ
ใช้ YOLO model สำหรับการตรวจจับวัตถุ
"""

import cv2
import numpy as np
from ultralytics import YOLO
import time
import os

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
        self.class_names = {
            2: 'รถยนต์',
            3: 'จักรยานยนต์',
            5: 'รถบัส',
            7: 'รถบรรทุก'
        }
        
        # สีสำหรับ bounding boxes
        self.colors = {
            2: (0, 255, 0),    # เขียว - รถยนต์
            3: (255, 0, 0),    # น้ำเงิน - จักรยานยนต์
            5: (0, 0, 255),    # แดง - รถบัส
            7: (255, 255, 0)   # ฟ้า - รถบรรทุก
        }
        
        print("โหลด model สำเร็จ!")
    
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
            print(f"ไม่สามารถเปิดไฟล์วิดีโอ: {video_path}")
            return
        
        # ดึงข้อมูลวิดีโอ
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        print(f"ข้อมูลวิดีโอ:")
        print(f"  - ความละเอียด: {width}x{height}")
        print(f"  - FPS: {fps}")
        print(f"  - จำนวนเฟรม: {total_frames}")
        
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
            
            # เพิ่มข้อมูลสถิติลงในเฟรม
            stats_text = f"Frame: {frame_count}/{total_frames} | รถในเฟรม: {vehicle_count} | รวม: {total_vehicles}"
            cv2.putText(processed_frame, stats_text, (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            
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
            print(f"ไม่สามารถเปิดกล้อง index: {camera_index}")
            return
        
        print("เริ่มตรวจจับรถจากกล้อง...")
        print("กด 'q' เพื่อหยุด")
        
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
            
            # เพิ่มข้อมูลสถิติ
            stats_text = f"Frame: {frame_count} | รถในเฟรม: {vehicle_count} | รวม: {total_vehicles}"
            cv2.putText(processed_frame, stats_text, (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            
            cv2.imshow('การตรวจจับรถยนต์ - Webcam', processed_frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()

def main():
    """ฟังก์ชันหลัก"""
    detector = CarDetector()
    
    print("=== โปรแกรมตรวจจับรถยนต์ ===")
    print("1. ประมวลผลจากไฟล์วิดีโอ")
    print("2. ตรวจจับจากกล้อง webcam")
    print("3. ออกจากโปรแกรม")
    
    while True:
        choice = input("\nเลือกตัวเลือก (1-3): ")
        
        if choice == '1':
            video_path = input("ใส่เส้นทางไฟล์วิดีโอ: ")
            if os.path.exists(video_path):
                save_output = input("ต้องการบันทึกวิดีโอผลลัพธ์ไหม? (y/n): ").lower()
                output_path = None
                if save_output == 'y':
                    output_path = input("ใส่ชื่อไฟล์ output (เช่น output.mp4): ")
                
                detector.process_video(video_path, output_path)
            else:
                print("ไม่พบไฟล์วิดีโอ")
                
        elif choice == '2':
            detector.process_webcam()
            
        elif choice == '3':
            print("ออกจากโปรแกรม")
            break
            
        else:
            print("กรุณาเลือก 1, 2, หรือ 3")

if __name__ == "__main__":
    main()