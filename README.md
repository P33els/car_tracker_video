# โปรแกรมตรวจจับรถยนต์จากวิดีโอ

โปรแกรมนี้ใช้ YOLO (You Only Look Once) model เพื่อตรวจจับรถยนต์และยานพาหนะประเภทต่างๆ จากวิดีโอหรือกล้อง webcam

## คุณสมบัติหลัก

- ตรวจจับรถยนต์, จักรยานยนต์, รถบัส, และรถบรรทุก
- ประมวลผลไฟล์วิดีโอ (MP4, AVI, MOV, ฯลฯ)
- ตรวจจับจากกล้อง webcam แบบ real-time
- บันทึกวิดีโอผลลัพธ์
- แสดงสถิติการตรวจจับ
- แสดงความเชื่อมั่นของการตรวจจับ

## การติดตั้ง

ติดตั้ง Python packages ที่จำเป็น:

```bash
pip install opencv-python ultralytics numpy matplotlib Pillow
```

## การใช้งาน

### วิธีที่ 1: รันโปรแกรมหลัก

```bash
python car_detection.py
```

จากนั้นเลือกตัวเลือกที่ต้องการ:
1. ประมวลผลจากไฟล์วิดีโอ
2. ตรวจจับจากกล้อง webcam

### วิธีที่ 2: ใช้ตัวอย่างที่เตรียมไว้

```bash
python example_usage.py
```

### วิธีที่ 3: เขียนโค้ดเอง

```python
from car_detection import CarDetector

# สร้าง detector
detector = CarDetector()

# ประมวลผลวิดีโอ
detector.process_video(
    video_path="input_video.mp4",
    output_path="output_video.mp4",
    show_preview=True
)

# หรือใช้กับ webcam
detector.process_webcam(camera_index=0)
```

## รายละเอียดการทำงาน

### คลาสที่ตรวจจับได้
- **รถยนต์** (สีเขียว): รถยนต์ทั่วไป
- **จักรยานยนต์** (สีน้ำเงิน): รถจักรยานยนต์
- **รถบัส** (สีแดง): รถโดยสาร/รถบัส
- **รถบรรทุก** (สีฟ้า): รถบรรทุก

### ผลลัพธ์ที่ได้
- Bounding box รอบยานพาหนะที่ตรวจพบ
- ชื่อประเภทยานพาหนะ
- ค่าความเชื่อมั่น (confidence score)
- จำนวนยานพาหนะในแต่ละเฟรม
- สถิติรวมยานพาหนะทั้งหมด

## การปรับแต่ง

### เปลี่ยน confidence threshold
```python
detector = CarDetector()
# เปลี่ยนค่าความเชื่อมั่นขั้นต่ำ (0.0-1.0)
processed_frame, count, details = detector.detect_vehicles_in_frame(
    frame, confidence_threshold=0.7
)
```

### ใช้ YOLO model ที่ต่างออกไป
```python
# ใช้ model ที่แม่นยำกว่า (ช้ากว่า)
detector = CarDetector(model_path='yolov8s.pt')  # หรือ yolov8m.pt, yolov8l.pt, yolov8x.pt

# ใช้ model ที่เร็วกว่า (แม่นยำน้อยกว่า)
detector = CarDetector(model_path='yolov8n.pt')  # default
```

## ไฟล์ที่สำคัญ

- `car_detection.py`: โปรแกรมหลัก
- `example_usage.py`: ตัวอย่างการใช้งาน
- `README.md`: คำแนะนำนี้

## ข้อกำหนดระบบ

- Python 3.7 ขึ้นไป
- กล้อง webcam (สำหรับการตรวจจับแบบ real-time)
- การ์ดจอที่รองรับ CUDA (ไม่บังคับ แต่จะเร็วกว่า)

## การแก้ปัญหา

### ถ้าไม่พบกล้อง
- ตรวจสอบว่าปิดโปรแกรมอื่นที่ใช้กล้องแล้ว
- ลองเปลี่ยน camera_index เป็นค่าอื่น (1, 2, ฯลฯ)

### ถ้าประมวลผลช้า
- ใช้ YOLO model ที่เล็กกว่า (yolov8n.pt)
- ลดขนาดวิดีโอก่อนประมวลผล
- ปิดการแสดงตัวอย่าง (show_preview=False)

### ถ้าตรวจจับไม่แม่นยำ
- ใช้ YOLO model ที่ใหญ่กว่า (yolov8s.pt, yolov8m.pt)
- ลดค่า confidence_threshold
- ตรวจสอบคุณภาพของวิดีโอ input

## ตัวอย่างผลลัพธ์

โปรแกรมจะแสดง:
```
=== สรุปผลลัพธ์ ===
ประมวลผลเสร็จสิ้น!
เวลาที่ใช้: 45.23 วินาที
ประมวลผล 1200 เฟรม
ความเร็วเฉลี่ย: 26.52 FPS
พบรถทั้งหมด: 3456 คัน
บันทึกวิดีโอที่: output_video.mp4
```