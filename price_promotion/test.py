from moviepy.editor import *
from unipath import Path

BASE_DIR = Path(__file__).resolve().parent.parent
video1 = VideoFileClip("bufbc_video.mp4")
video1.duration = video1.reader.duration
print(video1.duration)
video = VideoFileClip("tuvfp_video.mp4")
video.duration = video.reader.duration
print(video.duration)
lis =[video,video1]
final = concatenate_videoclips(lis)
final.duration = video1.reader.duration+video.reader.duration
print(final.duration)
final.write_videofile("test.mp4",audio=True,threads=7)
