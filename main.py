import argparse
import subprocess
from pathlib import Path

import requests
from pytube import YouTube
from mutagen.id3 import ID3, APIC, TPE1, TALB  # type: ignore


class MyYouTube(YouTube):

    def __init__(self, video_id: str):
        YouTube.__init__(self, f"https://youtu.be/{video_id}")


def print_streams(yt: YouTube):
    for s in yt.streams:
        print(s)


def print_tags(mp3: Path):
    for key, val in ID3(mp3).items():
        print(key, val)


def get_audio(yt: YouTube):
    stream = yt.streams.filter(mime_type="audio/webm").order_by('abr').last()
    return Path(stream.download())


def get_thumbnail(yt: YouTube):
    return requests.get(yt.thumbnail_url).content


def convert_to_mp3(file: Path):
    mp3_file = Path("mp3", file.stem + ".mp3")
    if mp3_file.is_file():
        mp3_file.unlink()
    subprocess.run(f'ffmpeg -i "{file}" "{mp3_file}"', stderr=subprocess.DEVNULL)
    file.unlink()
    return mp3_file


def get_youtube_obj():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--id', type=str)
    group.add_argument('--url', type=str)
    args = parser.parse_args()
    if args.id:
        return MyYouTube(args.id)
    if args.url:
        return YouTube(args.url)


def main():
    yt = get_youtube_obj()
    audio_file = get_audio(yt)
    tags = ID3(convert_to_mp3(audio_file))
    tags.add(APIC(encoding=0, mime='image/jpg', type=3, desc='', data=get_thumbnail(yt)))
    tags.add(TPE1(encoding=3, text=yt.author))
    tags.add(TALB(encoding=1, text=yt.title))
    tags.save()


if __name__ == "__main__":
    main()
