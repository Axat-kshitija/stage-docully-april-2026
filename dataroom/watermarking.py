from userauth.models import User
from .models import Dataroom
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import os, sys
from django.conf import settings 
import datetime
import textwrap
from django.core.files import File
import codecs
import shutil

FONT = settings.STATIC_PATH+'/images/arial.ttf'
InFile = settings.STATIC_PATH+'/images/blank_watermark.png'
# InFile = settings.STATIC_PATH+'/images/img2.png'
 
def add_watermark_cc(datas, ip):
    img = Image.open(InFile).convert('RGBA')
    MEDIA_FILE = settings.MEDIA_ROOT
    STATIC_FILE = settings.STATIC_ROOT
    # print("media_file ==>",settings.STATIC_ROOT)
    # outfile = settings.MEDIA_ROOT+'watermark_preview1.png'
    watermark = Image.new('RGBA', img.size, (0,0,0,0))
    # print("watermark", watermark.size)
    (W,H) = watermark.size
    draw = ImageDraw.Draw(watermark, 'RGBA')
    margin = 30
    i_count = 0
    # print("datas ===>",datas)
    for i, data in enumerate(datas):
        # print(i,"=====",data)
        # print(data.user.email)
        user = data.user.email
        getmail(user)
        dataroom = data.dataroom.dataroom_name
        OutFile = '/home/cdms_backend/cdms2/media/'+dataroom+'&'+user+'.png'
        # OutFile = settings.MEDIA_ROOT+'watermark/watermark_preview='+dataroom+'&'+user+'.png'
        # http://docullystorage.backends.blob.core.windows.net/ = settings.MEDIA_ROOT
        # print("watermarking.py_settings ====>",settings.MEDIA_ROOT)
        opacity = data.opacity
        angle = data.rotation
        size = data.font_size
        texts = arrangeText(data, ip)
        if i == 1 or i == 2:
            texts.reverse()
        n_font = ImageFont.truetype(FONT, size)
        wmargin, hmargin, pad = 20, 20, 2
        for text in texts:
            w, h = n_font.getsize(text)
            if data.type == 'center :: center':
                position = ((W-w)/2 - wmargin,((H-h)/2-hmargin))
            elif data.type == 'top :: center':
                position = ((W-w)/2 - wmargin,hmargin)
            elif data.type == 'bottom :: center':
                position = ((W-w)/2 - wmargin, H - hmargin - h)
            elif data.type == 'top :: left':
                position = (wmargin, hmargin)
            elif data.type == 'center :: left':
                position = (wmargin, ((H-h)/2-hmargin))
            elif data.type == 'bottom :: left':
                position = (wmargin, H - hmargin - h)
            elif data.type == 'top :: right':
                position = (W - wmargin - w, hmargin)
            elif data.type == 'center :: right':
                position = (wmargin, ((H-h)/2-hmargin))
            elif data.type == 'bottom :: right':
                position = (W - wmargin - w, H - hmargin - h)
            draw.text(position, text, font=n_font,fill=(0, 0, 0, 200))
            hmargin += h + pad 
        # http://www.thecodingcouple.com/watermark-images-python-pillow-pil/
    watermark = watermark.rotate(angle,Image.BICUBIC)
    alpha = watermark.split()[3]
    alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
    watermark.putalpha(alpha)
    # print("watermarking.py ======>",watermark)
    # print("this new line after watermarking")
    # print("value of datas ------->",datas)
    Image.composite(watermark, img, watermark).save(OutFile, 'PNG')
    # print("000000000",OutFile)
    # print("os===>",os.getcwd())
    new_ouput_path = OutFile.split('/')
    # print("new_ouput_path==>",new_ouput_path[-1])
    shutil.copy2(OutFile, '/var/www/html/assets/images/'+ new_ouput_path[-1])
    
    for data in datas:
        data.attachments = '/media/'+data.dataroom.dataroom_name+'&'+data.user.email+'.png'
        # print("data.attachments ===>",data.attachments)
        data.save()


    return True
        # print(data.__dict__)

    # if __name__ == '__main__':
    #     if len(sys.argv) < 3:
    #         sys.exit('Usage: %s <input-image> <text> <output-image> ' \
    #                  '<angle> <opacity> ' % os.path.basename(sys.argv[0]))
    #     add_watermark_cc(*sys.argv[1:])


def arrangeText(data, ip):
    text = []
    user_obj = User.objects.get(id=data.user.id)
    # print(data.dataroom.id,"data.dataroom.id")
    dataroom_obj = Dataroom.objects.get(id=data.dataroom.id)
    # print("IPPPPPP-----------", ip)
    if data.user_ipaddress == True:
        text.append(ip)
    if data.user_name == True:
        text.append(user_obj.first_name+' '+user_obj.last_name)
    if data.user_email == True:
        text.append(user_obj.email)
    if data.current_time== True:
        text.append(str(datetime.datetime.now()))
    if data.dataroom_name == True:
        text.append(dataroom_obj.dataroom_name)
    if data.custom_text:
        text.append(data.custom_text)
        # print("Texttttttttt", text)
        # a = data.custom_text
        # getdetails(a)
    return text

def getmail(user):
    # print("getmail",type(user))
    return user


# def getdetails(a):
#     print("getdetais",type(a))
#     return a
