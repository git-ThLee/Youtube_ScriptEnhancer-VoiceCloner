import whisper
import time

model = whisper.load_model("large-v2") # large-v2

def transcribe(path):
  print(f"Whisper Start")
  # Speach to Text
  start_time = time.time()
  result = model.transcribe(path, word_timestamps=True)
  end_time = time.time()
  print(f"Whisper successfully, time :{end_time-start_time}")
  return result
