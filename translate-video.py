import os
import subprocess
import json
from deep_translator import GoogleTranslator
import whisper

# 1. 음성 추출
def extract_audio(video_path, audio_path):
    command = f"ffmpeg -i {video_path} -q:a 0 -map a {audio_path} -y"
    subprocess.run(command, shell=True)

# 2. 음성 인식
def transcribe_audio(audio_path):
    model = whisper.load_model("base")
    result = model.transcribe(audio_path, language="zh")
    return result

# 3. 텍스트 번역
def translate_text(original_text):
    translator = GoogleTranslator(source='zh-CN', target='ko')
    return translator.translate(original_text)

# 4. SRT 파일 생성
def generate_srt(transcription_result, translated_texts, output_srt_path):
    with open(output_srt_path, "w", encoding="utf-8") as srt_file:
        for i, segment in enumerate(transcription_result["segments"]):
            start_time = format_time(segment["start"])
            end_time = format_time(segment["end"])
            srt_file.write(f"{i + 1}\n")
            srt_file.write(f"{start_time} --> {end_time}\n")
            srt_file.write(f"{translated_texts[i]}\n\n")

def format_time(seconds):
    millis = int((seconds % 1) * 1000)
    seconds = int(seconds)
    minutes = seconds // 60
    seconds = seconds % 60
    hours = minutes // 60
    minutes = minutes % 60
    return f"{hours:02}:{minutes:02}:{seconds:02},{millis:03}"

# 5. 자막 삽입
def embed_subtitles(video_path, srt_path, output_video_path):
    command = f"ffmpeg -i {video_path} -vf subtitles={srt_path} {output_video_path} -y"
    subprocess.run(command, shell=True)

# 전체 파이프라인 실행
def main(video_path, output_video_path, temp_audio_path, temp_srt_path):
    # 1. 동영상에서 음성 추출
    extract_audio(video_path, temp_audio_path)

    # 2. 음성을 텍스트로 변환
    transcription_result = transcribe_audio(temp_audio_path)
    original_texts = [seg["text"] for seg in transcription_result["segments"]]

    # 3. 텍스트를 한글로 번역
    translated_texts = [translate_text(text) for text in original_texts]

    # 4. SRT 파일 생성
    generate_srt(transcription_result, translated_texts, temp_srt_path)

    # 5. 자막을 동영상에 삽입
    embed_subtitles(video_path, temp_srt_path, output_video_path)

# 실행
video_path = "test.mp4"  # 원본 동영상 경로
output_video_path = "output_video_with_subtitles.mp4"  # 자막 포함 동영상 경로
temp_audio_path = "temp_audio.mp3"  # 추출된 음성 파일 경로
temp_srt_path = "temp_subtitles.srt"  # 생성된 자막 파일 경로

main(video_path, output_video_path, temp_audio_path, temp_srt_path)

