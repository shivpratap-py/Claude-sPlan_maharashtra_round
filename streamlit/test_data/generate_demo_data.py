import os
import cv2
import numpy as np
import scipy.io.wavfile as wavfile
from pathlib import Path

def generate_tone(filename, freq=440, duration=3, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    audio = 0.5 * np.sin(2 * np.pi * freq * t)
    wavfile.write(filename, sample_rate, (audio * 32767).astype(np.int16))

def generate_image(filename, color=(255, 255, 255), size=(500, 500)):
    img = np.zeros((size[1], size[0], 3), dtype=np.uint8)
    img[:] = color
    cv2.imwrite(filename, img)

def generate_video(filename, color=(0, 255, 0), fps=30, duration=3, size=(500, 500)):
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(filename, fourcc, fps, size)
    img = np.zeros((size[1], size[0], 3), dtype=np.uint8)
    img[:] = color
    for _ in range(fps * duration):
        out.write(img)
    out.release()

def create_case(base_dir, case_name, image_color, audio_freq, text_claim):
    case_dir = os.path.join(base_dir, case_name)
    os.makedirs(case_dir, exist_ok=True)
    
    generate_image(os.path.join(case_dir, "image.jpg"), color=image_color)
    generate_tone(os.path.join(case_dir, "audio.wav"), freq=audio_freq)
    # generate_video(os.path.join(case_dir, "video.mp4"), color=image_color)
    
    with open(os.path.join(case_dir, "claim.txt"), "w", encoding="utf-8") as f:
        f.write(text_claim)

def main():
    base_dir = Path(__file__).parent
    
    create_case(
        base_dir, 
        "authentic_case", 
        image_color=(200, 200, 200), 
        audio_freq=440, 
        text_claim="This video shows Person X at the London office on 2026-09-20."
    )
    
    create_case(
        base_dir, 
        "manipulated_case", 
        image_color=(50, 50, 200), # Red
        audio_freq=880, 
        text_claim="The image shows a protest in Paris on 2024-02-10."
    )
    
    create_case(
        base_dir, 
        "coordinated_case", 
        image_color=(0, 0, 0), 
        audio_freq=220, 
        text_claim="Recorded in Delhi inside a courtroom on 2025-01-01."
    )
    
    create_case(
        base_dir, 
        "uncertain_case", 
        image_color=(128, 128, 128), 
        audio_freq=440, 
        text_claim="Unknown context."
    )
    
    print(f"Generated demo data in {base_dir}")

if __name__ == "__main__":
    main()
