### 실행(run)

```bash

# 0. ffmpeg 설치 
# 윈도우 : 구글 검색 설치
# 우분투
sudo apt update
sudo apt install ffmpeg
ffmpeg -version

# 1. 가상환경 생성
python -m venv ysevc

# 2. 가상환경 실행
ysevc\Scripts\activate

# 3. Whisper 설치
pip install git+https://github.com/openai/whisper.git

# 4. requirements.txt 설치
pip install -r requirements.txt  

# 5. Streamlit 실행
streamlit run main.py

```

### 결과물(result)

```
결과물은 result 폴더에서 확인이 가능합니다.

1. txt 파일 : 본 프로젝트를 통해 생성된 자막
2. mp4 : 본 프로젝트를 통해 생성된 욕설이 삐소리 처리된 영상

```

### 가상환경 

```
# 가상환경 생성
python -m venv ysevc

# 가상환경 실행
ysevc\Scripts\activate

# 가상환경 종료
deactivate
```

### requirements.txt

```
# requirements 생성
pip freeze > requirements.txt  

# requirements 설치
pip install -r requirements.txt  
```

### Streamlit 실행

```
streamlit run main.py
```

### 설치

```
# Whisper
pip install git+https://github.com/openai/whisper.git  
```

### ffmpeg 설치 

```
# 윈도우 : 구글 검색 설치
# 우분투
sudo apt update
sudo apt install ffmpeg
ffmpeg -version
```

---

### Reference

- 유튜브 스크립트 가져오기 : [youtube_transcript_api](https://github.com/jdepoix/youtube-transcript-api)
- [GCP에서 Streamlit 방화벽 해결](https://velog.io/@bandi12/GCP%EC%97%90%EC%84%9C-streamlit-%EC%8B%A4%ED%96%89%ED%95%98%EA%B8%B0)