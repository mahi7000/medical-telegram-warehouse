import pathlib
from ultralytics import YOLO

def run_medical_detection():
    # 1. Initialize a lightweight pre-trained YOLOv8 model (automatically downloads on first run)
    print("🚀 Initializing YOLOv8 Model Architecture...")
    model = YOLO("yolov8n.pt")

    # 2. Define our structured Data Lake source media paths based on your real tree
    project_root = pathlib.Path(__file__).parent.resolve()
    media_dir = project_root / "data" / "raw" / "images"
    
    # Target channels specified by Kara Solutions
    channels = ['CheMed123', 'lobelia4cosmetics', 'tikvahpharma']
    image_extensions = {".jpg", ".jpeg", ".png", ".webp"}
    total_processed = 0

    print("\n🔍 Scanning Data Lake Partition Layers...")
    for channel in channels:
        channel_path = media_dir / channel
        if not channel_path.exists():
            print(col := f"⚠️ Path not found, skipping: {channel_path}")
            continue
            
        print(f"\n📂 Processing Channel Stream: [{channel.upper()}]")
        
        # Gather all valid target images in the directory
        images = [f for f in channel_path.iterdir() if f.suffix.lower() in image_extensions]
        
        if not images:
            print("   ↳ No images found in this partition.")
            continue

        for img_path in images:
            print(f"   📸 Running inference on: {img_path.name}")
            
            # Run inference without saving raw image copies to keep the drive clean
            results = model.predict(source=str(img_path), save=False, verbose=False, device='cpu')
            
            # Extract detection metadata
            for result in results:
                boxes = result.boxes
                if len(boxes) == 0:
                    print("     ↳ No distinct objects detected.")
                else:
                    for box in boxes:
                        class_id = int(box.cls[0])
                        label = model.names[class_id]
                        confidence = float(box.conf[0])
                        print(f"     ↳ Detected: [{label}] with {confidence:.2%} confidence")
                        
            total_processed += 1

    print(f"\n✅ Processing Finished! Total Data Lake images scanned: {total_processed}")

if __name__ == "__main__":
    run_medical_detection()