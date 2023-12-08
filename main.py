import youtube 
import speech_to_text

import torch
import streamlit as st
import os
import re 
import whisper

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

MODEL_SIZE = 'small' # large-v2
MODEL = whisper.load_model(MODEL_SIZE, device=DEVICE)

BEEP_WAV_DIR = os.path.join('src', 'beep_loop.wav')

OUTPUT_SAVE_DIR = 'save'
OUTPUT_SAVE_MERGED_DIR = 'save_merged'
OUTPUT_SAVE_MERGED_MODIFY_DIR = 'save_merged_modify'

STOPWORDS = ['시발','새끼','쌔끼','씹','뒤질래','비우신색','씨발','쌍년','썅년','미친','시빨','좆밥','ㅅㅂ','애미','새키']
STOPWORDS_PATTERN = re.compile('|'.join(map(re.escape, STOPWORDS)))

def insert_url_form():
    placeholder_insert_url_form = st.empty()
    with placeholder_insert_url_form.container():
        _ , center_col , _ = st.columns([1,2,1])
        with center_col :
            st.title('Youtube')
            st.title('Scripte-Enhancer & Voice-Cloner')
            
            progress_text = "잠시만 기다려주세요..."
            status_progress_ = st.progress(0, text=progress_text)
            status_progress_.empty()
            try : 
                # URL to wav
                col1 , col2 = st.columns([9, 1])
                with col1 :
                    youtube_url = st.text_input('Youtube URL', 'https://www.youtube.com/~')
                    
                with col2 :
                    st.subheader("")
                    if st.button('Play'):
                        # 비디오, 오디오 다운로드 
                        progress_text = "유튜브에 들어가서 영상을 가져오는 중이에요..."
                        status_progress_.progress(0,text=progress_text)
                        video_title, only_video_mp4_filename, only_audio_mp3_filename = youtube.download_video_with_audio(youtube_url, OUTPUT_SAVE_DIR)

                        # 비디오, 오디오 Merge
                        progress_text = "유튜브에 들어가서 영상을 가져오는 중이에요..."
                        status_progress_.progress(40,text=progress_text)
                        merged_mp4_filename = youtube.merge_video_audio(only_video_mp4_filename, only_audio_mp3_filename, OUTPUT_SAVE_DIR, OUTPUT_SAVE_MERGED_DIR)

                        # 스크립트 가져오기
                        progress_text = "유튜브에서 스크립트(자막)를 가져오는 중이에요..."
                        status_progress_.progress(80,text=progress_text)
                        transcript_language , transcript_fetchs = youtube.get_youtube_script(youtube_url)

                        status_progress_.progress(100,text=progress_text)
                        status_progress_.empty()

                        st.session_state.video_title = video_title # 유튜브 영상 이름
                        st.session_state.merged_mp4_filename = merged_mp4_filename
                        st.session_state.merged_mp4_path = os.path.join(OUTPUT_SAVE_MERGED_DIR, merged_mp4_filename) 

                        st.session_state.only_video_mp4_filename = only_video_mp4_filename
                        st.session_state.only_audio_mp3_filename = only_audio_mp3_filename
                        st.session_state.only_video_mp4_path = os.path.join(OUTPUT_SAVE_DIR, only_video_mp4_filename)
                        st.session_state.only_audio_mp3_path = os.path.join(OUTPUT_SAVE_DIR, only_audio_mp3_filename)

                        st.session_state.transcript_language = transcript_language
                        st.session_state.transcript_fetchs = transcript_fetchs

            except:
                st.error('죄송합니다. 에러가 발생했습니다. URL 링크 확인해주시고, 문제가 지속될 경우 문의 주세요.', icon="🚨")
                status_progress_.empty()

def compare_scripts_youtube():
    #######################
    ### 유튜브 스크립트
    #######################
    youtube_script = [f"[{ int(round(x['start']//60,1)) }:{ '0'+str(int(round(x['start']%60,1))) if len(str(int(round(x['start']%60,1)))) == 1 else int(round(x['start']%60,1)) }] {x['text']}" for x in st.session_state.transcript_fetchs]

    st.write("**Youtube Script**", unsafe_allow_html=True)
    tags_left = ["<td style='width: 1200px;'>", "<div style='overflow-y: scroll; height: 478px;'>"]
    
    for words in youtube_script :
        # 욕설 검출
        importances = []
        for x in words.split():
            if STOPWORDS_PATTERN.search(x):
                importances.append(1.0)
            else:
                importances.append(0.0)
        # 형광펜
        for word, importance in zip(words.split(), importances): 
            importance = max(-1, min(1, importance))
            if importance > 0:
                hue = 120
                sat = 75
                lig = 100 - int(50 * importance)
            else:
                hue = 0
                sat = 75
                lig = 100 - int(-40 * importance)
            color =  "hsl({}, {}%, {}%)".format(hue, sat, lig)
            unwrapped_tag = (
                '<mark style="background-color: {color}; opacity:1.0; line-height:1.75">'
                '<font color="black">{word}</font></mark>'.format(color=color, word=word)
            )
            tags_left.append(unwrapped_tag)
        tags_left.append('<br>')
    tags_left.append("</div>")
    tags_left.append("</td>")

    html_left = "".join(tags_left)
    st.write(html_left, unsafe_allow_html=True)

def compare_scripts_ours():
    #######################
    ### Ours 스크립트
    #######################
    st.write("**Our Script**", unsafe_allow_html=True)
    with st.spinner(text='스크립트 생성 중이에요...영상이 길어서 늦어지고 있어요...') :
        # Whipser로 STT
        transcript_fetchs_whisper = speech_to_text.transcribe(os.path.join(OUTPUT_SAVE_DIR, st.session_state.only_audio_mp3_filename ), MODEL)
        st.session_state.transcript_fetchs_whisper = transcript_fetchs_whisper['segments']
        # Ours 스크립트 생성
        our_script = [f"[{ int(round(x['start']//60,1)) }:{ '0'+str(int(round(x['start']%60,1))) if len(str(int(round(x['start']%60,1)))) == 1 else int(round(x['start']%60,1)) }] {x['text']}" for x in st.session_state.transcript_fetchs_whisper]

        tags_right = ["<td style='width: 1200px;'>", "<div style='overflow-y: scroll; height: 478px;'>"]
        for words in our_script :
            # 욕설 검출 & 형광펜
            importances = []
            for x in words.split():
                if STOPWORDS_PATTERN.search(x):
                    importances.append(1.0)
                else:
                    importances.append(0.0)

            for word, importance in zip(words.split(), importances): 
                importance = max(-1, min(1, importance))
                if importance > 0:
                    hue = 120
                    sat = 75
                    lig = 100 - int(50 * importance)
                else:
                    hue = 0
                    sat = 75
                    lig = 100 - int(-40 * importance)
                color =  "hsl({}, {}%, {}%)".format(hue, sat, lig)
                unwrapped_tag = (
                    '<mark style="background-color: {color}; opacity:1.0; line-height:1.75">'
                    '<font color="black">{word}</font></mark>'.format(color=color, word=word)
                )
                tags_right.append(unwrapped_tag)
            tags_right.append('<br>')
        tags_right.append("</div>")
        tags_right.append("</td>")
    
        html_right = "".join(tags_right)
        st.write(html_right, unsafe_allow_html=True)

def compare_videos_youtube():
    #######################
    ### 유튜브 영상
    #######################
    st.write("**Youtube Video**", unsafe_allow_html=True)
    video_file = open(st.session_state.merged_mp4_path, 'rb')
    video_bytes = video_file.read()
    st.video(video_bytes)

def compare_videos_ours():
    #######################
    ### Ours 영상
    #######################
    st.write("**Our Video**", unsafe_allow_html=True)
    with st.spinner(text='영상에서 욕설을 제거하고 있어요...평균적으로 영상 1분당 1분 정도 소요되요...') :
        # 파일명, 경로 지정
        merged_modify_mp4_filename = st.session_state.merged_mp4_filename
        merged_modify_mp4_path = os.path.join(OUTPUT_SAVE_MERGED_MODIFY_DIR, merged_modify_mp4_filename)

        # 캐시 저장
        st.session_state.merged_modify_mp4_filename = merged_modify_mp4_filename
        st.session_state.merged_modify_mp4_path = merged_modify_mp4_path

        # 욕설 검출 - start, end, text 
        result_dict_list = []
        for i, fetch in enumerate(st.session_state.transcript_fetchs_whisper):
            if STOPWORDS_PATTERN.search(fetch['text']):
                for fetch_word in fetch['words']:
                    if STOPWORDS_PATTERN.search(fetch_word['word']):
                        result_dict = {
                            'start': fetch_word['start'],
                            'end': fetch_word['end'],
                            'word': fetch_word['word']
                        }
                        result_dict_list.append(result_dict)

        # 영상에서 욕설 제거 
        youtube.modify_video(st.session_state.merged_mp4_path, 
            BEEP_WAV_DIR, 
            merged_modify_mp4_path, 
            [(x['start'],x['end']) for x in result_dict_list]) # [(46.18, 46.68), (47.24, 47.88)])

        # 영상 보여주기 
        video_file = open(merged_modify_mp4_path, 'rb')
        video_bytes = video_file.read()
        st.video(video_bytes)

def main():
    st.set_page_config(
        page_title="Youtube-GiTi4",
        page_icon="⚔️",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    insert_url_form()
            
    if 'video_title' in st.session_state:
        ###############################
        ### 스크립트(자막) 비교
        ###############################
        st.title('This is YouTube Original Script and Video')
        st.write(f"**Language** : **{st.session_state.transcript_language}**", unsafe_allow_html=True)

        placeholder_compare_scripts = st.empty()
        with placeholder_compare_scripts.container():
            compare_scripts_youtube_col, compare_scripts_ours_col = st.columns(2)
            with compare_scripts_youtube_col:
                compare_scripts_youtube()
            with compare_scripts_ours_col:
                compare_videos_youtube()

        st.divider()
        ###############################
        ### 비디오 비교
        ###############################
        st.title('This is Our Script and Video')
        placeholder_compare_videos = st.empty()
        with placeholder_compare_videos.container():
            compare_videos_youtube_col, compare_videos_ours_col = st.columns(2)
            with compare_videos_youtube_col:
                compare_scripts_ours()
            with compare_videos_ours_col:
                compare_videos_ours()

if __name__ == "__main__":
    if not os.path.exists('save'):
        os.makedirs('save')
    if not os.path.exists('save_merged'):
        os.makedirs('save_merged')
    if not os.path.exists('save_merged_modify'):
        os.makedirs('save_merged_modify')
    main()