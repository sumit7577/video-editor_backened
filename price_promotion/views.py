from django.http import JsonResponse,HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from django.contrib.auth import authenticate,login,logout
from rest_framework.parsers import JSONParser
from rest_framework.authtoken.models import Token
from .models import *
from django.contrib.auth import logout
from django.contrib.auth.models import User
from pymongo import MongoClient
import gridfs
from moviepy.editor import *
from django.conf import settings
import base64
from frozen_brothers import settings
import random
import string


uploaded = "video.mp4"

@api_view(['POST'])
@csrf_exempt
def user_logout(request):
    try:
        request_body = JSONParser().parse(request)
        username = request_body['username']
        user_id = User.objects.get(username=username).id
        try:
            # del request.session[user]
            Token.objects.filter(user_id=user_id).delete()
            logout(request)
            #request.session["video"] = ""
            return JsonResponse({"status":"success","message":f"{username} logged out"})
        except: 
            return JsonResponse({"status":"failed","message":f"{username} already logged out"},status=403)
    except User.DoesNotExist:
        return JsonResponse({"status":"failed","message":f";{username} User does not exist"},status=403)
    except Exception as e:
        return JsonResponse({"status":"failed","message":f"User logout failed..{e}"},status=500)



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
                                'message': 'Please provide correct username and password'},status=403)
        else:
            Token.objects.get_or_create(user=user)
            token = Token.objects.get(user=user)
            return JsonResponse({"status":"success","token":token.key})
    except Exception as e:
        return JsonResponse({"status":"failed", "message": f"{e}"},status=500)



def base(text):
    list = []
    fileName = text.split(";")
    newFileName = fileName[0][5:]
    front = random.choices(string.ascii_lowercase,k=5)
    stringData = ""
    for i in front:
        stringData += i
    extension = newFileName.replace("/",".")
    newExtension = stringData+"_"+extension
    fileData = base64.b64decode(fileName[1][7:])
    with open(newExtension,"wb") as file:
        file.write(fileData)
    list.append([newExtension,fileData])
    return list


def fixCords(cords,coords1,videoSize):
    height = videoSize[1]-100
    width = videoSize[0]
    if(cords):
        if(float(cords["y"])) > float(height):
            while(float(cords["y"]) > float(height)):
                cords["y"] = float(cords["y"]) - 20


    if(coords1):
        if(float(coords1["y"])) > float(height):
            while(float(coords1["y"]) > float(videoSize[1])):
                coords1["y"] = float(coords1["y"]) - 20
    
    return(cords,coords1)


def create_price_tag(icons,tags,rotate,request):
    cords = tags[0]["coord"]
    iconLocation = icons[0]["location"]
    tagLocation = tags[0]["location"]
    iconImage = icons[0]["image"]
    tagIMage = tags[0]["image"]
    iconName = base(iconImage)
    tagName = base(tagIMage)

    iconName1 = None
    tagName1= None

    if len(icons) >1:
        iconImage1 = icons[1]["image"]
        iconLocation1 = icons[1]["location"]
        iconName1 = base(iconImage1)

    if len(tags) >1:
        coords1 = tags[1]["coord"]
        tagImage1 = tags[1]["image"]
        tagLocation1 = tags[1]["location"] or "left"
        tagName1 = base(tagImage1)

    #videoFile = os.path.join(settings.BASE_DIR,request.session["video"])
    test = os.path.join(settings.BASE_DIR,uploaded)
    tagLogo1 = None
    iconLogo1 = None

    if rotate:
        video = VideoFileClip(test,audio=True).rotate(90)
    else:
        video = VideoFileClip(test,audio=True)
    co_ordinates = fixCords(cords,coords1,video.size)

    try:
        iconLogo = ImageClip(iconName[0][0]).resize(height=40,width=50).margin(top=10,bottom=10,left=10,right=10, opacity=0).set_pos((iconLocation,"bottom"))
    except Exception as re:
        print(f'right tag error {re}')

    try:
        iconLogo1 = ImageClip(iconName1[0][0]).resize(height=40,width=50).margin(top=10,bottom=10,left=10,right=10, opacity=0).set_pos((iconLocation1,"bottom"))
    except Exception as re:
        print(f'left tag error {re}')

    try:
        tagLogo = ImageClip(tagName[0][0]).resize(height=60,width=50).set_position((float(cords["x"]),float(co_ordinates[0]["y"])))
    except Exception as re:
        return JsonResponse({"status":"failed","message":"Please enter float type co-ordinates values"},staus=401)

    try:
        tagLogo1 = ImageClip(tagName1[0][0]).resize(height=60,width=50).set_position((float(coords1["x"]),float(co_ordinates[1]["y"])))
            
    except Exception as le:
       return JsonResponse({"status":"failed","message":"Please enter float type co-ordinates values"},status=401)

    final = CompositeVideoClip([video,iconLogo,tagLogo])
    if(final):
        if(iconLogo1 is not None and tagLogo1 is not None):
            final = CompositeVideoClip([video,iconLogo,iconLogo1,tagLogo,tagLogo1])
        elif(iconLogo1 is not None):
            final = CompositeVideoClip([video,iconLogo,iconLogo1,tagLogo])
        elif(tagLogo1 is not None):
            final = CompositeVideoClip([video,iconLogo,tagLogo,tagLogo1])
    else:
        return JsonResponse({"status":"failed","message":"Please input atleast 1 icons and 1 tags"},status=400)

    final.duration = video.reader.duration
    final.write_videofile("outputVideo.mp4", audio = True,threads=7)
    final.close()
    video.close()

    if(os.path.exists(uploaded) and uploaded !="video.mp4"):
        os.remove(uploaded)

    os.remove(iconName[0][0])
    os.remove(tagName[0][0])
    if(iconName1 is not None):
        os.remove(iconName1[0][0])
    if(tagName1 is not None):
        os.remove(tagName1[0][0])

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
    try:
        token = request.headers["Authorization"][7:]
    except:
        return JsonResponse({"status":"failed","message":"Please insert Token in header"},status=403)
    data = Token.objects.filter(key=token)
    if not data:
        return JsonResponse({"status":"failed","message":"Please input valid Token"},status=401)
    #username = data[0].user
    files = request_body["path"]
    decodedFile = base(files)
    global uploaded
    uploaded = decodedFile[0][0]
    #request.session["video"] = decodedFile[0][0]

    #try:
    #except:
        #return JsonResponse({"status":"Error","message":"Please input valid File"},status=500)
    #File.objects.update_or_create(userName=request.user,file=files)
    # db = mongo_conn()
    # file_data = open(path, 'rb')
    # data = file_data.read()
    # fs = gridfs.GridFS(db)
    # fs.put(data, file_name=path.split('/')[-1]
    return JsonResponse({"status":"success","message":"File uploaded"})
    # except Exception as e:
    #     return JsonResponse({"status":"failure", "response": f"{e}"})




@api_view(["POST"])
def download(request):
    request_body = JSONParser().parse(request)
    
    try:
        icons = request_body["icons"]
        tags = request_body["tags"]
        rotate = request_body["rotate"]
        
    except:
        return JsonResponse({"status":"failed","message":"Please provide tags and icons"},status=403)

    try:
        token = request.headers["Authorization"][7:]
        userId = User.objects.filter(auth_token__key= token)
        if(not userId):
            return JsonResponse({"status":"failed","message":"Please input valid Token"},status=401)
        #username = userId[0].id
    except:
        return JsonResponse({"status":"failed","message":"Please insert Token in header"},status=403)
    
    create_price_tag(icons,tags,rotate,request)

    #if len(FileData) == 0:
    #    return JsonResponse({"status":"No file"})
    app = "outputVideo.mp4"

    with open(app, "rb") as f:
        response = HttpResponse(
            f.read(), content_type="application/files")
        response['Content-Disposition'] = 'inline;filename=' + \
            os.path.basename(app)
        try:
            return response
        except:
            return JsonResponse({"status":"failed","message":"something error happened"},status=500)

    