import streamlit as st
from pytube import YouTube
from moviepy.editor import VideoFileClip
import os
import subprocess
import uuid

OUTPUT_SAVE_DIR = 'save'

def download_audio(url, output_path='.'):
    try:
        # YouTube 객체 생성
        yt = YouTube(url)

        # 오디오 형식 및 품질 선택
        audio = yt.streams.filter(only_audio=True).first()
        audio_mime_type = audio.mime_type[audio.mime_type.rindex('/')+1:] # ex) mp4
        audio_title_original = audio.title
        audio_title_uuid = str(uuid.uuid4())  # UUID 생성

        # 다운로드 시작
        audio.download(output_path = output_path,filename=f"{audio_title_uuid+ '.' + audio_mime_type}")
        print(f"Audio downloaded successfully to {output_path}")
        return audio_title_original, audio_title_uuid, audio_mime_type
        #convert_mp4_to_wav(output_path, f"{audio_title_uuid+ '.' + audio_mime_type}", f"{audio_title_uuid + '.wav'}")

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

def del_mp4_file(mp4_path):
    mp4_path = os.path.join(OUTPUT_SAVE_DIR, mp4_path)
    os.remove(mp4_path)
    print(f"MP4 file deleted.")

def main():
    st.set_page_config(
        page_title="Youtube-GiTi4",
        page_icon="⚔️",
        layout="centered",
        initial_sidebar_state="expanded",
    )
    st.title('Youtube')
    st.title('Scripte-Enhancer & Voice-Cloner')
    # URL to wav
    audio_title_original = ""
    col1 , col2 = st.columns([9, 1])
    with col1 :
        youtube_url = st.text_input('Youtube URL', 'https://www.youtube.com/~')
    with col2 :
        st.subheader("")
        if st.button('Play'):
            # 오디오 다운로드
            audio_title_original, audio_title_uuid, audio_mime_type = download_audio(youtube_url, OUTPUT_SAVE_DIR)
            # 오디오 to wav
            convert_mp4_to_wav(OUTPUT_SAVE_DIR, f"{audio_title_uuid+ '.' + audio_mime_type}", f"{audio_title_uuid + '.wav'}")
            # MP4 파일 삭제
            del_mp4_file(f"{audio_title_uuid+ '.' + audio_mime_type}")
            
    # Wav 변환된 파일 보여주기
    if audio_title_original != "":
        st.text(f'파일명 : {audio_title_original}.wav')
        audio_file = open(os.path.join(OUTPUT_SAVE_DIR, f"{audio_title_uuid + '.wav'}"), 'rb')
        audio_bytes = audio_file.read()

        st.audio(audio_bytes, format='audio/wav')

    with st.expander("What is this system?"):
        st.text('비밀^^')

    

    if st.button('🔁'):
        pass



if __name__ == "__main__":
    main()