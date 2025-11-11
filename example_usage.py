"""
ตัวอย่างการใช้งานโปรแกรมตรวจจับรถยนต์แบบง่าย
"""

from car_detection import CarDetector
import os

def simple_video_detection():
    """ฟังก์ชันตัวอย่างสำหรับตรวจจับรถจากวิดีโอ"""
    
    # สร้าง detector
    detector = CarDetector()
    
    # ตัวอย่างเส้นทางไฟล์วิดีโอ (แก้ไขตามไฟล์จริงของคุณ)
    video_paths = [
        "sample_video.mp4",
        "traffic_video.avi",
        "test_video.mov"
    ]
    
    # ตรวจสอบไฟล์วิดีโอที่มีอยู่
    print("ค้นหาไฟล์วิดีโอ...")
    available_videos = []
    for path in video_paths:
        if os.path.exists(path):
            available_videos.append(path)
            print(f"พบไฟล์: {path}")
    
    if not available_videos:
        print("ไม่พบไฟล์วิดีโอ กรุณาวางไฟล์วิดีโอในโฟลเดอร์เดียวกันกับโปรแกรม")
        print("หรือแก้ไขเส้นทางในโค้ดนี้")
        return
    
    # ประมวลผลไฟล์แรกที่พบ
    video_path = available_videos[0]
    output_path = f"detected_{os.path.basename(video_path)}"
    
    print(f"\nกำลังประมวลผล: {video_path}")
    print(f"ผลลัพธ์จะบันทึกเป็น: {output_path}")
    
    # ประมวลผลวิดีโอ
    detector.process_video(
        video_path=video_path,
        output_path=output_path,
        show_preview=True  # แสดงตัวอย่างระหว่างประมวลผล
    )

def webcam_detection():
    """ฟังก์ชันตัวอย่างสำหรับตรวจจับรถจาก webcam"""
    
    detector = CarDetector()
    
    print("กำลังเริ่มตรวจจับรถจาก webcam...")
    print("กด 'q' ในหน้าต่างวิดีโอเพื่อหยุด")
    
    detector.process_webcam(camera_index=0)

if __name__ == "__main__":
    print("=== ตัวอย่างการใช้งานโปรแกรมตรวจจับรถยนต์ ===")
    print("1. ตรวจจับจากไฟล์วิดีโอ")
    print("2. ตรวจจับจาก webcam")
    
    choice = input("เลือกตัวเลือก (1 หรือ 2): ")
    
    if choice == "1":
        simple_video_detection()
    elif choice == "2":
        webcam_detection()
    else:
        print("กรุณาเลือก 1 หรือ 2")