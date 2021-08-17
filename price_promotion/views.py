from django.http import JsonResponse
from rest_framework.parsers import JSONParser
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from django.contrib.auth import authenticate
from price_promotion import models
from rest_framework.authtoken.models import Token
from django.contrib.auth import logout
from django.contrib.auth.models import User
from pymongo import MongoClient
import gridfs
from moviepy.editor import *
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw 

@api_view(['POST'])
def user_logout(request):
    try:
        request_body = JSONParser().parse(request)
        username = request_body['username']
        user_id = User.objects.get(username=username).id
        try:
            # del request.session[user]
            Token.objects.filter(user_id=user_id).delete()
            logout(request)
            return JsonResponse({"status":"success","response":f"{username} logged out"})
        except: return JsonResponse({"status":"failure","response":f"{username} already logged out"})
    except User.DoesNotExist:
        return JsonResponse({"status":"failure","response":f"User does not exist"})
    except Exception as e:
        print(f'abms_logout: {e}')
        return JsonResponse({"status":"failure","response":f"User logout failed..{e}"})

@api_view(['POST'])
@csrf_exempt
def get_token(request):
    try:
        request_body = JSONParser().parse(request)
        user = request_body['username']
        password = request_body['password']
        user = authenticate(username=user, password=password)
        if user is None:
            return JsonResponse({'status':'failed', 
                                'token': None, 
                                'response': 'Please provide correct username and password'})
        else:
            print(f"{user} autheticated successfully")
            token, created = Token.objects.get_or_create(user=user)
        token = Token.objects.get(user=user)
        return JsonResponse({"status":"success","token": "Token "+ token.key})
    except Exception as e:
        return JsonResponse({"status":"failure", "response": f"{e}"})

def get_video_clip(start, stop, rotate=False, filepath='sadhguru.webm'):
    clip = VideoFileClip(filepath)
    clip = clip.subclip(start, stop)
    # if rotate:
    if clip.size[0] < clip.size[1]:
        clip = clip.rotate(90)
    return clip

@api_view(['POST'])
@csrf_exempt
def create_price_tag(request):
    request_body = JSONParser().parse(request)
    location = request_body['location']
    amt1=request_body['amt1']
    qty1=request_body['qty1']
    amt2=request_body['amt2']
    qty2=request_body['qty2']
    ccy1=request_body['ccy1']
    ccy2=request_body['ccy2']
    rotate=False
    tag_style='default'
    theta = np.linspace( 0 , 2 * np.pi , 150 )
    radius = 0.4
    figure, axes = plt.subplots( 1 )
    axes.plot( radius*np.cos(theta), radius*np.sin(theta), color='black')
    t = np.arange(-0.4, 0.3, 0.2)
    plt.plot(t+0.11, t*0, '-', linestyle='-', color='black')

    plt.text(-0.1, -.15, f'{qty1}oz\n{ccy1}{amt1}', wrap=True, va='center_baseline', size='xx-large', family='DejaVu Sans',weight='extra bold', ma='center')
    # plt.rc("font", size=10, family='DejaVu Sans', weight='bold')
    plt.text(-0.15, .18, f'{qty2}oz\n{ccy2}{amt2}', wrap=True, va='center_baseline', size='20', weight='extra bold', family='DejaVu Sans', ma='center')

    axes.set_frame_on(False)
    axes.axes.get_yaxis().set_visible(False)
    axes.axes.get_xaxis().set_visible(False)
    axes.set_aspect( 1 )        
    if location=='right':
        plt.savefig('rightTag.jpg')
        orig_img=Image.open('rightTag.jpg') 
    else:
        plt.savefig('leftTag.jpg')
        orig_img=Image.open('leftTag.jpg') 
    height,width=orig_img.size 
    npImage=np.array(orig_img) 
    new_img = Image.new('L', orig_img.size,0) # Creating mask image in L mode with same image size 
    draw = ImageDraw.Draw(new_img) # drawing on mask created image using Draw() function
    draw.pieslice([165,21,374.5,230.5],0,360,fill=255) # making circle on mask image using pieslice() function
    np_new=np.array(new_img) # Converting the mask Image to numpy array
    npImage=np.dstack((npImage,np_new)) # stack the array sequence (original image array with mask image) depth wise 
    final_img = Image.fromarray(npImage) # converting array to an image using fromarray() function 
    if rotate:
        final_img = final_img.rotate(90)
    final_img.thumbnail((500,500)) # making thumbnail using thumbnail() function by passing the size in it
    if location=='right':
        final_img.save('Circular_thumbnail_right.png')
    else:
        final_img.save('Circular_thumbnail_left.png')
    # add image in video
    if rotate:
        video = VideoFileClip("sadhguru.webm").rotate(90)
    else:
        video = VideoFileClip("sadhguru.webm")
    try:
        logo = (ImageClip('Circular_thumbnail_right.png')
                # .set_duration(10)
                .resize(height=200) # if you need to resize...
                .margin(left=200, top=40, opacity=0) # (optional) logo-border padding
                .set_pos(("left","top")))
    except Exception as re:
        print(f'right tag error {re}')
    try:
        logo = (ImageClip('Circular_thumbnail_left.png')
                .set_duration(10)
                .resize(height=200) # if you need to resize...
                .margin(left=200, top=40, opacity=0) # (optional) logo-border padding
                .set_pos(("left","top")))
    except Exception as le:
        print(f'left tag error {le}')

    final = CompositeVideoClip([video, logo])
    final.write_videofile("output_video_watermarked.mp4", audio = True)
    return JsonResponse({"status":"success"})

# def mongo_conn():
#     try:
#         conn = MongoClient(host = '127.0.0.1', port = 27017)
#         print('Mongo connected:', conn)
#         return conn.grid_file
#     except Exception as e:
#         print('error in conn', e)
        
@api_view(['POST'])
@csrf_exempt
def upload(request):
    # try:
    request_body = JSONParser().parse(request)
    path = request_body['path']
    # db = mongo_conn()
    # file_data = open(path, 'rb')
    # data = file_data.read()
    # fs = gridfs.GridFS(db)
    # fs.put(data, file_name=path.split('/')[-1])
    print('upload completed')
    return JsonResponse({"status":"success", "path":path})
    # except Exception as e:
    #     return JsonResponse({"status":"failure", "response": f"{e}"})
    