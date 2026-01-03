"""
Helper script to relabel speakers in the transcription
Run this AFTER reviewing transcription.txt and identifying who each speaker is
"""

import json

# CONFIGURE THIS: Map speaker letters to roles
SPEAKER_MAP = {
    "A": "Technician",  # Change this based on your transcript
    "B": "Customer",    # Change this based on your transcript
    # Add more if there are additional speakers
    # "C": "Manager",
}

def relabel_transcription():
    # Load the JSON transcription
    with open("transcription.json", "r") as f:
        data = json.load(f)
    
    # Create relabeled text file
    with open("transcription_labeled.txt", "w", encoding="utf-8") as f:
        f.write("=== Service Call Transcription (Labeled) ===\n\n")
        
        for utterance in data["utterances"]:
            speaker = utterance["speaker"]
            labeled_speaker = SPEAKER_MAP.get(speaker, f"Speaker {speaker}")
            start = utterance["start"]
            end = utterance["end"]
            text = utterance["text"]
            
            f.write(f"[{start:.2f}s - {end:.2f}s] {labeled_speaker}:\n")
            f.write(f"{text}\n\n")
    
    print("✅ Relabeled transcription saved to transcription_labeled.txt")
    print(f"\nSpeaker mapping used:")
    for original, labeled in SPEAKER_MAP.items():
        print(f"  Speaker {original} → {labeled}")

if __name__ == "__main__":
    print("Relabeling speakers...")
    print("\n⚠️  Make sure to edit SPEAKER_MAP in this script first!")
    print("   Review transcription.txt to identify who each speaker is.\n")
    
    try:
        relabel_transcription()
    except FileNotFoundError:
        print("❌ Error: transcription.json not found. Run transcribe.py first!")
    except Exception as e:
        print(f"❌ Error: {e}")

