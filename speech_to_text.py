# # Faster-Whisper : https://github.com/guillaumekln/faster-whisper
# from faster_whisper import WhisperModel

# model_size = "small"

# # Run on GPU with FP16
# # model = WhisperModel(model_size, device="cuda", compute_type="float16")

# # or run on GPU with INT8
# # model = WhisperModel(model_size, device="cuda", compute_type="int8_float16")
# # or run on CPU with INT8
# model = WhisperModel(model_size, device="cpu", compute_type="int8")

# import time

# def transcribe(path):
#   # info.language, info.language_probability
#   # segment.start, segment.end, segment.text
#   print(f"Whisper Start")
#   # Speach to Text
#   start_time = time.time()
#   segments, info = model.transcribe(path, beam_size=5)
#   end_time = time.time()
#   print(f"Whisper transcribe successfully, time :{end_time-start_time}")
#   start_time = time.time()
#   segments = list(segments)
#   end_time = time.time()
#   print(f"Whisper tolist all successfully, time :{end_time-start_time}")

#   return segments

import whisper
import time
model = whisper.load_model("small") # large-v2

def transcribe(path):
  print(f"Whisper Start")
  # Speach to Text
  start_time = time.time()
  result = model.transcribe(path, word_timestamps=True)
  end_time = time.time()
  print(f"Whisper successfully, time :{end_time-start_time}")
  return result
