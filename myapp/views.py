import json
import os
import re
import cv2
import pytesseract
from subprocess import call
from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage

def index(request):
    return render(request, 'index.html', {"address": "127.0.0.1"})

@csrf_exempt
def processImage(request):
    
    if request.method == 'POST' and request.FILES['fileName']:
        myfile = request.FILES['fileName']
        path = settings.MEDIA_ROOT + "/" + myfile.name

        does_exist = os.path.exists(path)
        if not does_exist:
            fss = FileSystemStorage()
            fss.save(myfile.name, myfile)
            fss.save(os.path.splitext(path)[0] + ".png", myfile) # Save another png file for display
        
            # calling and waiting
            call(["scripts/generator.sh", path, "eng"])

        msg = "file already exist" if does_exist else "file processed successfully"
        with open(os.path.splitext(path)[0] + ".box", encoding="utf-8") as boxfile:
            x = [line.rstrip("\n") for line in boxfile] 

        data = [line for line in x if line.split(' ')[0] == "WordStr"]
        return JsonResponse({"msg": msg, "data": data}, safe=False)
    else:
        return JsonResponse({"msg": "file not exist"}, safe=False)


@csrf_exempt
def doInpainting(request):
    data = request.body.decode('utf-8') 
    jsonData = json.loads(data)

    print(jsonData["filename"])
    print(jsonData["content"])



    # path = settings.MEDIA_ROOT + "/" + os.path.basename(jsonData["filename"])
    # with open(os.path.splitext(path)[0] + ".box", encoding="utf-8", mode="w+") as boxfile:
    #     boxfile.write(jsonData["content"])

    # with open(os.path.splitext(path)[0] + ".box", "r") as boxfile:
    #     img = cv2.imread(os.path.splitext(path)[0] + ".png")
    #     height, width, _ = img.shape

    #     for line in boxfile:
    #         if "WordStr " in line:
    #             outer_idx = re.search(r' 0 #', line).start()
    #             coor = line[8:outer_idx]
    #             x, y, w, h = getCoor(coor, width, height)

    #             cv2.rectangle(img, (x, y), (x+w, y+h), (0, 0, 255), 1)
        
    #     cv2.imwrite(os.path.splitext(path)[0] + ".jpg", img)

    return JsonResponse({"msg": "inpainting is done"}, safe=False)


def getCoor(coor, width, height):
    each_coor = [int(i) for i in coor.split(' ')]
    y2 = height - each_coor[1]
    y1 = height - each_coor[3]

    each_coor[1] = y1
    each_coor[2] = each_coor[2] - each_coor[0]
    each_coor[3] = y2 - y1

    return each_coor[0], each_coor[1], each_coor[2], each_coor[3]

