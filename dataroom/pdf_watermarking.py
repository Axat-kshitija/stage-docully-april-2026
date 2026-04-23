# from PyPDF2 import PdfFileWriter, PdfFileReader
from PyPDF2 import PdfWriter, PdfReader

import io
import tempfile
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from django.conf import settings
from reportlab.lib.units import inch
from reportlab.lib.colors import PCMYKColor, PCMYKColorSep, Color, black, blue, red
from reportlab.pdfbase.pdfmetrics import stringWidth
from userauth.models import User,User_time_zone
# from data_documents.utils import convert_to_kolkata
from .models import Dataroom, dataroomProLiteFeatures
import datetime
import os
from dms.settings import *
# from userauth.models import User_time_zone


FONT = '/home/axat/Documents/raveena/cdms/ConfiexDataRoom-djay_latest/static/images/arial.ttf'
wmargin=0
hmargin=72
topMargin=72
bottomMargin=18

def GeneratePDF(datas,ip, user,pk):
    print("pdf_watermarking.py==========>starttttttttttttttttttt")
    # print("path--------",  pk)
    # path_list = path.split("/")
    # del path_list[0]
    # name = path_list[-1]
    # path = '/'.join(path_list)
    # path = path.replace('%20', ' ')
    # print("path_list", path)
    # path = "media/Project Arch_f43a3bc6-ea60-4a12-a532-b8f22b3b32d4/3.0.7_DISCLAIMERS_sOahaPD.pdf"
    packet = io.BytesIO()
    dataroom_no=str(datas[0]['dataroom'])
    # print(dataroom_no,"dataroom_no")
    usrename=str(user)
    # print(usrename,"usrename")
    usrename2=usrename.replace('.com',"")
    # filename=str(dataroom_no)+'_'+usrename+'.pdf'
    filename=str(dataroom_no) +'.pdf'
    # print(filename,"filename")

    os.makedirs('/home/cdms_backend/cdms2/Admin_Watermark/', exist_ok=True)
    temp1 = tempfile.NamedTemporaryFile(
        prefix='first',
        suffix=filename,
        dir='/home/cdms_backend/cdms2/Admin_Watermark/',
        delete=False
    )
    temp2 = tempfile.NamedTemporaryFile(
        prefix='second',
        suffix=filename,
        dir='/home/cdms_backend/cdms2/Admin_Watermark/',
        delete=False
    )
    temp3 = tempfile.NamedTemporaryFile(
        prefix='third',
        suffix=filename,
        dir='/home/cdms_backend/cdms2/Admin_Watermark/',
        delete=False
    )
    OutFile1 = temp1.name
    OutFile2 = temp2.name
    OutFile3 = temp3.name
    temp1.close()
    temp2.close()
    temp3.close()

    # Create a new PDF with Reportlab


    # print("WWWWWWWWWW", W, "HHHHHHHHHHHHHH",H)
    # textWidth = stringWidth(lines, 'Helvetica-Bold', 8) 
    # print("------", textWidth, letter)
    # textHeight = stringWidth


    for i, data in enumerate(datas):
        # print("dataaaa", data)
        # Default values for None fields
        if data.get('font_size') is None:
            data['font_size'] = 40
        if data.get('opacity') is None:
            data['opacity'] = 0.5
        if data.get('rotation') is None:
            data['rotation'] = 0
        if data.get('type') is None:
            data['type'] = 'center :: center'

        if i==0:
            can = canvas.Canvas(OutFile1, pagesize=letter)
        elif i==1:
            can = canvas.Canvas(OutFile2, pagesize=letter)
        else:
            can = canvas.Canvas(OutFile3, pagesize=letter)


        lines = arrangeText(data, ip, user)
        # print(lines,"lines")
        can.translate(inch,inch)
        can.setFont('Helvetica', 24)
        # can.setStrokeColorRGB(0.2,0.5,0.3)
        # can.setFillColorRGB(1,0,1)
        
        W, H = letter

        w = 121
        h = 40

        # if i == 2:
        #   lines.reverse()
        color = Color( 0, 0, 0, alpha=data['opacity'])
        # print( data['font_size'],"fonttt")
        can.setFont('Helvetica', (int(data['font_size'])))
        can.rotate(-int(data['rotation']))

        can.setFillColor(color)
        if data['type'] == 'center :: center':
            # print("1")
            wmargin=0
            hmargin=24
            x,y = ((W-w)/2 - wmargin,((H-h)/2-hmargin))

            for line in lines:
                can.drawCentredString(x, y, line)
                y -= int(data['font_size'])
        elif data['type'] == 'top :: center':
            # print("2")
            wmargin=0
            hmargin=72
            x,y = ((W-w)/2 - wmargin,H - hmargin - h)
            for line in lines:
                can.drawCentredString(x, y, line)
                y -= int(data['font_size'])
        elif data['type'] == 'bottom :: center':
            # print("3")
            # x,y = ((W-w)/2 - wmargin, H - hmargin - h)
            wmargin=0
            hmargin=-60
            x,y = ((W-w)/2 - wmargin,hmargin)
            for line in lines:
                can.drawCentredString(x, y, line)
                y += int(data['font_size'])
        elif data['type'] == 'top :: left':
            # print("4")
            wmargin=-50
            hmargin=72
            x,y = (wmargin, H - hmargin - h)
            for line in lines:
                can.drawString(x, y, line)
                y -= int(data['font_size'])
        elif data['type'] == 'center :: left':
            # print("5")
            # x,y = (wmargin, ((H-h)/2-hmargin))
            wmargin=0
            hmargin=72
            x,y = (wmargin,((H-h)/2-hmargin))
            for line in lines:
                can.drawString(x, y, line)
                y -= int(data['font_size'])
        elif data['type'] == 'bottom :: left':
            # print("6")
            wmargin=-50
            hmargin=60
            x,y = (wmargin, hmargin)
            for line in lines:
                can.drawString(x, y, line)
                y -= int(data['font_size'])
        elif data['type'] == 'top :: right':
            # print("7")
            wmargin=0
            hmargin=72
            x,y = (W - wmargin - w, H - hmargin - h)
            for line in lines:
                can.drawRightString(x, y, line)
                y -= int(data['font_size'])
        elif data['type'] == 'center :: right':
            # print("8")
            wmargin=0
            hmargin=72
            x,y = (W - wmargin - w,((H-h)/2-hmargin))
            for line in lines:
                can.drawRightString(x, y, line)
                y -=int(data['font_size'])
        elif data['type'] == 'bottom :: right':
            # print("9")
            wmargin=0
            hmargin=50
            x,y = (W - wmargin - w, hmargin)
            for line in lines:
                can.drawRightString(x, y, line)
                y -= int(data['font_size'])
        can.showPage()
        can.save()
    
    # textWidth = stringWidth(line2, 'Helvetica', 24) 
    # x += textWidth + 1
    import PyPDF2
    from .models import Watermarking

    inputfile=OutFile1
    outputfile='/home/cdms_backend/cdms2/Admin_Watermark/'+filename
    watermarkfilee=OutFile2
    pdf_writer=PyPDF2.PdfWriter()
    with open(inputfile, 'rb') as fh:
        pdf=PyPDF2.PdfReader(fh)
        with open(watermarkfilee,'rb') as watermarkfile:
            watermarkfile_pdf=PyPDF2.PdfReader(watermarkfile)
            for i in range(len(pdf.pages)):
                # p=pdf.getPage(i)
                p=pdf.pages[i]
                p.merge_page(watermarkfile_pdf.pages[0])
                # p.mergePage(watermarkfile_pdf.getPage(0))
                pdf_writer.add_page(p)
                with open(outputfile,'wb') as outputfileeee:
                    pdf_writer.write(outputfileeee)
    inputfile='/home/cdms_backend/cdms2/Admin_Watermark/'+filename
    outputfile='/home/cdms_backend/cdms2/Admin_Watermark/'+filename
    watermarkfilee=OutFile3
    pdf_writer=PyPDF2.PdfWriter()
    with open(inputfile, 'rb') as fh:
        pdf=PyPDF2.PdfReader(fh)
        with open(watermarkfilee,'rb') as watermarkfile:
            watermarkfile_pdf=PyPDF2.PdfReader(watermarkfile)
            for i in range(len(pdf.pages)):
                p=pdf.pages[i]
                # p=pdf.getPage(i)
                p.merge_page(watermarkfile_pdf.pages[0])
                pdf_writer.add_page(p)
                with open(outputfile,'wb') as outputfileeee:
                    pdf_writer.write(outputfileeee)

    inputfile="/home/cdms_backend/cdms2/mediaa/A_Sample_PDF.pdf"
    os.makedirs('/home/cdms_backend/cdms2/Admin_Preview_Watermarkfile/', exist_ok=True)
    outputfile='/home/cdms_backend/cdms2/Admin_Preview_Watermarkfile/'+filename
    watermarkfilee='/home/cdms_backend/cdms2/Admin_Watermark/'+filename
    pdf_writer=PyPDF2.PdfWriter()
    with open(inputfile, 'rb') as fh:
        pdf=PyPDF2.PdfReader(fh)
        with open(watermarkfilee,'rb') as watermarkfile:
            watermarkfile_pdf=PyPDF2.PdfReader(watermarkfile)
            for i in range(len(pdf.pages)):
                p=pdf.pages[i]
                p.merge_page(watermarkfile_pdf.pages[0])
                pdf_writer.add_page(p)
                with open(outputfile,'wb') as outputfileeee:
                    pdf_writer.write(outputfileeee)
    container_name = 'docullycontainer'
    print(watermarkfilee, "-----------============================filenamewatermark")
    filename_Azurepath = watermarkfilee.split("/").pop()
    print(filename_Azurepath, "-----------============================filename")
    blob_name = filename_Azurepath
    try:
        from azure.storage.blob import BlockBlobService, ContentSettings
        block_blob_service = BlockBlobService(account_name='newdocullystorage', account_key='qOUUYXZxll+/cVmanzs+riupuL5c19VdDD0egQD/KUA5VUssLYF/hM0TEPcHEKgaFAIEzyglVXY7+AStQZEEig==')
        block_blob_service.create_blob_from_path(
            container_name,
            blob_name,
            outputfile,
            content_settings=ContentSettings(content_type='application/pdf'))
        print("Blob uploaded successfully:", blob_name)
    except Exception as blob_err:
        import traceback
        print("Azure blob upload failed:", str(blob_err))
        traceback.print_exc()
    watermarking = Watermarking.objects.filter(dataroom_id=pk)
    for i in watermarking:
        # print(i,"loop")
        i.attachments = watermarkfilee
        # print("data.attachments ===>",data.attachments)
        i.save()

    try:
        os.remove(OutFile1)
    except:
        pass
    try:
        os.remove(OutFile2)
    except:
        pass
    try:
        os.remove(OutFile3)
    except:
        pass
    
    
    
    
    # d=dict(attachments=OutFile)
    # print(d,"dict d")
    # watermarking = Watermarking.objects.filter(dataroom_id=pk).update(**d)
    # for data in datas:
    #   data.attachments = OutFile
    #   print("data.attachments ===>",data)
 #        data.save()
    # Move to the beginning of the StringIO buffer
    # packet.seek(0)a
    # new_pdf = PdfFileReader(packet)
    # # Read your existing PDF
    # existing_pdf = PdfFileReader(open(path, "rb"))
    # output = PdfFileWriter()
    # # Add the "watermark" (which is the new pdf) on the existing page
    # # print("------------",existing_pdf.getNumPages())
    # total = existing_pdf.getNumPages()
    # for x in range(total):
    #   # print("----------",x)
    #   page = existing_pdf.getPage(x)
    #   page.mergePage(new_pdf.getPage(0))
    #   output.addPage(page)
    # Finally, write "output" to a real file
    # outputStream = open("media/watermark/"+name, "wb")
    # output.write(outputStream)
    # outputStream.close()
    # group_folder.watermarking_file = "watermark/"+name
    # group_folder.save()




def convert_to_kolkata(dubai_datetime,timezone):
    from datetime import datetime
    import pytz
    # Set the timezone for Dubai
    dubai_tz = pytz.timezone('Asia/Dubai')
    # Set the timezone for Kolkata
    kolkata_tz = pytz.timezone(timezone)

    # Ensure the datetime is timezone-aware for Dubai
    dubai_aware = dubai_tz.localize(dubai_datetime)

    # Convert the datetime to Kolkata timezone
    kolkata_aware = dubai_aware.astimezone(kolkata_tz)

    return kolkata_aware


def arrangeText(data, ip, user):
    text = []
    # print(data,"dataaaaaaaaaaaa in arange")
    # print(data['user_ipaddress'],"user_ipaddress")
    # print(data['dataroom'],"dataroom id")
    user_obj = User.objects.get(id=data['user'])
    dataroom_obj = Dataroom.objects.get(id=data['dataroom'])
    # print("dataroom_obj-----------", dataroom_obj)
    kolkata_time=''
    timez=''
    if User_time_zone.objects.filter(user_id=user.id).exists():
        user_zone=User_time_zone.objects.filter(user_id=user.id).last()
        timez=user_zone.time_zone.tz
        if timez!='':
            kolkata_time = convert_to_kolkata(datetime.datetime.strptime(str(datetime.datetime.now()),'%Y-%m-%d %H:%M:%S.%f'),timez)
            kolkata_time = str(kolkata_time.strftime('%d/%m/%Y %H:%M'))
        else:
            kolkata_time = str(datetime.datetime.now().strftime('%d/%m/%Y %H:%M'))
    if data['user_ipaddress'] == True:
        text.append(ip)
    if data['user_name'] == True:
        text.append(user_obj.first_name+' '+user_obj.last_name)
    if data['user_email'] == True:
        text.append(user_obj.email)
    if data['current_time']== True:
        text.append(str(kolkata_time)+" "+user_zone.time_zone.abbreviation)
    if data['dataroom_name'] == True:
        text.append(dataroom_obj.dataroom_nameFront)
    if dataroom_obj.dataroom_version=="Lite":
        if dataroomProLiteFeatures.objects.filter(dataroom_id=dataroom_obj.id,custom_watermarking=True).exists():
            if data['custom_text']:
                text.append(data['custom_text'])
            
    else:
        if data['custom_text']:
            data['custom_text']
            text.append(data['custom_text'])
    # print("Texttttttttt", text)
    return text


# datass = ['center :: right','center :: left','center :: center','top :: left', 'top :: center',
#       'top :: right', 'bottom :: left', 'bottom :: center', 'bottom :: right']

# GeneratePDF(datass)
# GeneratePDF('center :: right')
# GeneratePDF('center :: left')
# GeneratePDF('center :: center')
# GeneratePDF('top :: left')
# GeneratePDF('top :: center')
# GeneratePDF('top :: right')
# GeneratePDF('bottom :: left')
# GeneratePDF('bottom :: center')
# GeneratePDF('bottom :: right')