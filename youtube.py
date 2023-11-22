
from pytube import YouTube
from moviepy.editor import VideoFileClip
import os
import subprocess
import uuid
from youtube_transcript_api import YouTubeTranscriptApi
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips
import time

def modify_video(video_path, audio_path, output_path, intervals):
    print('영상 변환 시작')
    start_time = time.time()
    # 동영상과 오디오 파일 불러오기
    video = VideoFileClip(video_path)
    beep_audio = AudioFileClip(audio_path)
    
    # 결과물을 저장할 비디오 클립 리스트
    clips = []
    
    # 이전 구간 끝 시간 초기화
    prev_end = 0
    
    for start, end in intervals:
        # 구간 이전의 클립 (이미지는 그대로, 소리는 원래대로)
        clip = video.subclip(prev_end, start)
        clips.append(clip)
        
        # 구간의 클립 (이미지는 그대로, 소리는 beep으로)
        clip = video.subclip(start, end).set_audio(beep_audio.subclip(0, end-start))
        clips.append(clip)
        
        # 이전 구간 끝 시간 업데이트
        prev_end = end
    
    # 마지막 구간 이후의 클립 (이미지는 그대로, 소리는 원래대로)
    clips.append(video.subclip(prev_end, video.duration))
    
    # 모든 클립 합치기
    final = concatenate_videoclips(clips)

    # video.close()
    # beep_audio.close()
    # 결과물 저장하기
    final.write_videofile(output_path, codec='libx264')

    video.close()
    beep_audio.close()
    end_time = time.time()
    print('영상 변환 time :', end_time - start_time)
    #return final

def get_youtube_script(url):
    if url.find('&') != -1 :
        video_id = url[url.index("watch?v=") + len("watch?v="): url.index('&', url.index("watch?v="))]
    else: 
        video_id = url[url.index("watch?v=") + len("watch?v="):]

    # https://github.com/jdepoix/youtube-transcript-api
    transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
    for transcript in transcript_list:
        transcript_language = transcript.language # Korean (auto-generated)
        transcript_fetchs = transcript.fetch()
    return transcript_language , transcript_fetchs

def download_video_with_audio(url, output_path='.'):
    try:
        # YouTube 객체 생성
        yt = YouTube(url)

        # 비디오 및 오디오 스트림 선택
        video_stream = yt.streams.filter(only_video=True).first()
        audio_stream = yt.streams.filter(only_audio=True).first()
        video_title_original = video_stream.title

        # 파일명 및 UUID 생성
        video_title_uuid = str(uuid.uuid4())  # UUID 생성


        # 비디오 다운로드
        video_stream.download(output_path=output_path, filename=f"{video_title_uuid}.mp4")
        print(f"Video downloaded successfully to {output_path}")

        # 오디오 다운로드
        audio_stream.download(output_path=output_path, filename=f"{video_title_uuid}.mp3")
        print(f"Audio downloaded successfully to {output_path}")

        return video_title_original, f"{video_title_uuid}.mp4", f"{video_title_uuid}.mp3"

    except Exception as e:
        print(f"Error: {e}")

def merge_video_audio(video_mp4_filename, audio_mp3_filename, output_path='save', OUTPUT_SAVE_MERGED_DIR='save_merged'):
    try:
        video_path = os.path.join(output_path, video_mp4_filename)
        audio_path = os.path.join(output_path, audio_mp3_filename)

        # Output file name
        merged_filename = f"{video_mp4_filename[:video_mp4_filename.rindex('.mp4')]}.mp4"
        merged_filepath = f"{OUTPUT_SAVE_MERGED_DIR}/{merged_filename}"

        # FFmpeg command to merge video and audio
        command = f"ffmpeg -i {video_path} -i {audio_path} -c:v copy -c:a aac {merged_filepath}"

        # Run FFmpeg command
        subprocess.call(command, shell=True)

        print(f"Merged video and audio successfully to {merged_filepath}")
        return merged_filename

    except Exception as e:
        print(f"Error: {e}")

def convert_mp4_to_wav(save_path, mp4_path, wav_path):
    try:
        mp4_path = os.path.join(save_path, mp4_path)
        wav_path = os.path.join(save_path, wav_path)
        command = "ffmpeg -i {} -ab 160k -ac 2 -ar 44100 -vn {}".format(mp4_path, wav_path)

        # WAV로 변환
        subprocess.call(command, shell=True)
    
    
    except Exception as e:
        print(f"Error: {e}")

def del_mp4_file(mp4_path, OUTPUT_SAVE_DIR):
    mp4_path = os.path.join(OUTPUT_SAVE_DIR, mp4_path)
    os.remove(mp4_path)
    print(f"MP4 file deleted.")