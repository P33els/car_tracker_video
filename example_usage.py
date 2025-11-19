"""
ตัวอย่างการใช้งานโปรแกรมตรวจจับรถยนต์
พร้อมฟีเจอร์เสียง timestamp และรองรับหลายภาษา
"""

from car_detection import CarDetector
import os
import time

def demo_english():
    """Demo in English"""
    print("=== Car Detection Demo (English) ===")
    
    # Create detector with English language
    detector = CarDetector()
    detector.set_language(use_thai=False)  # Use English
    
    print("Detector initialized with English language")
    print("Audio notifications enabled")
    print("Detection classes: Car, Motorcycle, Bus, Truck")
    
    # Test webcam (if available)
    print("\nStarting webcam demo...")
    print("Press 'q' to quit the webcam demo")
    
    try:
        detector.process_webcam(camera_index=0)
    except KeyboardInterrupt:
        print("\nDemo stopped by user")
    except Exception as e:
        print(f"Error: {e}")

def demo_thai():
    """Demo ภาษาไทย"""
    print("=== การสาธิต โปรแกรมตรวจจับรถยนต์ (ภาษาไทย) ===")
    
    # สร้าง detector พร้อมภาษาไทย
    detector = CarDetector()
    detector.set_language(use_thai=True)  # ใช้ภาษาไทย
    
    print("เริ่มต้น detector ด้วยภาษาไทย")
    print("เปิดการแจ้งเตือนด้วยเสียง")
    print("ประเภทที่ตรวจจับ: รถยนต์, จักรยานยนต์, รถบัส, รถบรรทุก")
    
    # ทดสอบ webcam (ถ้ามี)
    print("\nเริ่มการสาธิตด้วย webcam...")
    print("กด 'q' เพื่อออกจากการสาธิต")
    
    try:
        detector.process_webcam(camera_index=0)
    except KeyboardInterrupt:
        print("\nผู้ใช้หยุดการสาธิต")
    except Exception as e:
        print(f"ข้อผิดพลาด: {e}")

def simple_video_detection():
    """ฟังก์ชันตัวอย่างสำหรับตรวจจับรถจากวิดีโอ (พร้อมเสียง)"""
    
    # สร้าง detector
    detector = CarDetector()
    detector.set_language(use_thai=False)  # ใช้ภาษาอังกฤษเพื่อหลีกเลี่ยงปัญหา encoding
    
    # ตั้งค่าเสียงแจ้งเตือน
    print("🔊 Setting audio alerts every 5 seconds")
    detector.set_audio_settings(enable=True, interval=5)
    
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
    """ฟังก์ชันตัวอย่างสำหรับตรวจจับรถจาก webcam (พร้อมเสียง)"""
    
    detector = CarDetector()
    detector.set_language(use_thai=False)  # ใช้ภาษาอังกฤษ
    
    # ตั้งค่าเสียงแจ้งเตือนสำหรับ webcam (บ่อยกว่า)
    print("🔊 Setting audio alerts every 3 seconds for webcam")
    detector.set_audio_settings(enable=True, interval=3)
    
    print("Starting car detection from webcam...")
    print("📢 You will hear audio alerts with time and vehicle count")
    print("Press 'q' in video window to quit")
    
    detector.process_webcam(camera_index=0)

def demo_audio_settings():
    """สาธิตการตั้งค่าเสียงต่างๆ"""
    
    print("\n=== สาธิตฟีเจอร์เสียง ===")
    detector = CarDetector()
    
    print("1. ทดสอบเสียงแจ้งเตือนพร้อมจำนวนรถ")
    detector.speak_timestamp(8)  # จำลองพบ 8 คัน
    time.sleep(4)
    
    print("2. ทดสอบเสียงเมื่อไม่พบรถ")
    detector.speak_timestamp(0)  # จำลองไม่พบรถ
    time.sleep(4)
    
    print("3. การปรับการตั้งค่า:")
    print("   • เปิด/ปิดเสียง: detector.set_audio_settings(enable=True/False)")
    print("   • เปลี่ยนช่วงเวลา: detector.set_audio_settings(interval=3-15)")
    print("   • ความเร็วและระดับเสียงปรับได้อัตโนมัติ")
    
    # ทดสอบการเปลี่ยนการตั้งค่า
    print("\n4. ทดสอบการเปลี่ยนช่วงเวลา")
    detector.set_audio_settings(enable=True, interval=2)
    print("ตั้งค่าใหม่: แจ้งเตือนทุก 2 วินาที")
    
    detector.speak_timestamp(15)
    print("เสียงแจ้งเตือนใช้งานได้แล้ว! ✅")

if __name__ == "__main__":
    print("=== Car Detection Demo Program (Multi-Language Support) ===")
    print("🎉 New Features: Audio timestamp alerts & Language selection!")
    print("\nDemo Options:")
    print("1. English Demo (Webcam)")
    print("2. Thai Demo - สาธิตภาษาไทย (Webcam)")
    print("3. Video Processing Demo")
    print("4. Audio Settings Demo")
    print("5. Exit")
    
    while True:
        try:
            choice = input("\nSelect demo mode (1-5): ")
            
            if choice == "1":
                demo_english()
            elif choice == "2":
                demo_thai()
            elif choice == "3":
                simple_video_detection()
            elif choice == "4":
                demo_audio_settings()
            elif choice == "5":
                print("Goodbye! / ลาก่อน!")
                break
            else:
                print("Please select 1-5")
                
        except KeyboardInterrupt:
            print("\nProgram interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"An error occurred: {e}")
    
    print("\n✨ New Audio Features:")
    print("• Time and vehicle count audio alerts")
    print("• Adjustable alert intervals (3-15 seconds)")
    print("• Enable/disable audio anytime")
    print("• Real-time timestamp display on video")
    print("• Multi-language support (English/Thai)")