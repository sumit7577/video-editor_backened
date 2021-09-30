from moviepy.editor import *
from unipath import Path

BASE_DIR = Path(__file__).resolve().parent.parent
video1 = VideoFileClip("ufgdu_video.mp4",target_resolution=(200,150))
video = VideoFileClip("topost.mp4",target_resolution=(200,150))
lis =[video1,video]
final = concatenate_videoclips(lis)
final.duration = video1.reader.duration+video.reader.duration
final.write_videofile("test.mp4",audio=True,threads=7)
