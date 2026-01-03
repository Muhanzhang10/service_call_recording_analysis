import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
import assemblyai as aai
# aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY")

# audio_file = "./local_file.mp3"
audio_file = "data/39472_N_Darner_Dr_2.m4a"

config = aai.TranscriptionConfig(
    speech_models=["universal"],
    speaker_labels=True  # Enable speaker diarization
)

transcript = aai.Transcriber(config=config).transcribe(audio_file)

if transcript.status == "error":
  raise RuntimeError(f"Transcription failed: {transcript.error}")

# Save the transcription with timestamps and speaker labels
output_file = "data/transcription.txt"
with open(output_file, "w", encoding="utf-8") as f:
  f.write("=== Service Call Transcription ===\n\n")
  
  # Write utterances with timestamps and speaker labels
  for utterance in transcript.utterances:
    start_time = utterance.start / 1000  # Convert to seconds
    end_time = utterance.end / 1000
    speaker = utterance.speaker
    text = utterance.text
    
    f.write(f"[{start_time:.2f}s - {end_time:.2f}s] Speaker {speaker}:\n")
    f.write(f"{text}\n\n")

print(f"Transcription with timestamps saved to {output_file}")
print(f"Total speakers detected: {len(set(u.speaker for u in transcript.utterances))}")
print(f"Total utterances: {len(transcript.utterances)}")

# Also save raw text without timestamps
raw_output = "data/transcription_raw.txt"
with open(raw_output, "w", encoding="utf-8") as f:
  f.write(transcript.text)
print(f"Raw text (no timestamps) saved to {raw_output}")

# Save structured JSON for easier post-processing
json_output = "data/transcription.json"
transcript_data = {
    "id": transcript.id,
    "status": transcript.status,
    "text": transcript.text,
    "utterances": [
        {
            "speaker": u.speaker,
            "text": u.text,
            "start": u.start / 1000,  # in seconds
            "end": u.end / 1000,
            "confidence": u.confidence
        }
        for u in transcript.utterances
    ],
    "words": [
        {
            "text": w.text,
            "start": w.start / 1000,
            "end": w.end / 1000,
            "confidence": w.confidence,
            "speaker": w.speaker if hasattr(w, 'speaker') else None
        }
        for w in transcript.words
    ]
}

with open(json_output, "w", encoding="utf-8") as f:
    json.dump(transcript_data, f, indent=2)
print(f"JSON data saved to {json_output}")
 