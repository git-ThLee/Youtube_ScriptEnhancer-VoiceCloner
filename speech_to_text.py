import time

def transcribe(path, model):
  print(f"Whisper Start")
  # Speach to Text
  start_time = time.time()
  result = model.transcribe(path, word_timestamps=True)
  end_time = time.time()
  print(f"Whisper successfully, time :{end_time-start_time}")
  return result
