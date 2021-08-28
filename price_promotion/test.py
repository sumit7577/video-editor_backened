from moviepy.editor import *
from unipath import Path

BASE_DIR = Path(__file__).resolve().parent.parent
print(BASE_DIR)
uploaded = "video.mp4"
test = os.path.join(BASE_DIR,uploaded)

video = VideoFileClip(test,audio=True)
image2 = ImageClip("test1.jpg").resize(height=100).margin(top=10,bottom=10,left=10,right=10, opacity=0).set_pos(("left","bottom"))
image1 = ImageClip("test2.jpg").resize(height=100).set_pos(("right","top")).margin(top=10,bottom=10,left=10,right=10, opacity=0)
final  = CompositeVideoClip([video,image2,image1])
final.duration = video.reader.duration
final.write_videofile("test.mp4",audio=True,threads=7)