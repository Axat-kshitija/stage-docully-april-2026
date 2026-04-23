from PyPDF2 import PdfFileWriter, PdfFileReader
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from django.conf import settings
from reportlab.lib.units import inch
from reportlab.lib.colors import PCMYKColor, PCMYKColorSep, Color, black, blue, red
from reportlab.pdfbase.pdfmetrics import stringWidth
from userauth.models import User
from .models import Dataroom
import datetime
import os
from dms.settings import *


FONT = '/home/axat/Documents/raveena/cdms/ConfiexDataRoom-djay_latest/static/images/arial.ttf'
wmargin=0
hmargin=72
topMargin=72
bottomMargin=18

def GeneratePDF(datas,ip, user,pk):
	print("pdf_watermarking.py==========>firstttttt")
	print("path--------",  pk)
	# path_list = path.split("/")
	# del path_list[0]
	# name = path_list[-1]
	# path = '/'.join(path_list)
	# path = path.replace('%20', ' ')
	# print("path_list", path)
	# path = "media/Project Arch_f43a3bc6-ea60-4a12-a532-b8f22b3b32d4/3.0.7_DISCLAIMERS_sOahaPD.pdf"
	packet = io.BytesIO()
	dataroom_no=str(datas[0]['dataroom'])
	print(dataroom_no,"dataroom_no")
	usrename=str(user)
	print(usrename,"usrename")
	usrename2=usrename.replace('.com',"")
	# filename=str(dataroom_no)+'_'+usrename+'.pdf'
	filename=str(dataroom_no) +'.pdf'
	print(filename,"filename")
	OutFile = '/home/cdms_backend/cdms2/Admin_Watermark/'+filename
	# Create a new PDF with Reportlab
	can = canvas.Canvas(OutFile, pagesize=letter)
	can.translate(inch,inch)
	can.setFont('Helvetica', 24)
	# can.setStrokeColorRGB(0.2,0.5,0.3)
	# can.setFillColorRGB(1,0,1)
	
	
	W, H = letter
	# print("WWWWWWWWWW", W, "HHHHHHHHHHHHHH",H)
	# textWidth = stringWidth(lines, 'Helvetica-Bold', 8) 
	print("------sddddddddddletter", letter)
	# textHeight = stringWidth
	w = 121
	h = 40

	for i, data in enumerate(datas):
		# print("dataaaa", data)
		lines = arrangeText(data, ip, user)
		# print(lines,"lines")
		if i == 2:
			lines.reverse()
		color = Color( 0, 0, 0, alpha=data['opacity'])
		print( data['font_size'],"fonttt")
		can.setFont('Helvetica', (int(data['font_size'])))
		can.setFillColor(color)
		# print("dataaaa", data.rotation)
		can.rotate(int(data['rotation']))
		if data['type'] == 'center :: center':
			print("1")
			wmargin=0
			hmargin=24
			x,y = ((W-w)/2 - wmargin,((H-h)/2-hmargin))
			for line in lines:
				can.drawCentredString(x, y, line)
				y -= int(data['font_size'])
		elif data['type'] == 'top :: center':
			print("2")
			wmargin=0
			hmargin=72
			x,y = ((W-w)/2 - wmargin,H - hmargin - h)
			for line in lines:
				can.drawCentredString(x, y, line)
				y -= int(data['font_size'])
		elif data['type'] == 'bottom :: center':
			print("3")
			# x,y = ((W-w)/2 - wmargin, H - hmargin - h)
			wmargin=0
			hmargin=-60
			x,y = ((W-w)/2 - wmargin,hmargin)
			for line in lines:
				can.drawCentredString(x, y, line)
				y += int(data['font_size'])
		elif data['type'] == 'top :: left':
			print("4")
			wmargin=-50
			hmargin=72
			x,y = (wmargin, H - hmargin - h)
			for line in lines:
				can.drawString(x, y, line)
				y -= int(data['font_size'])
		elif data['type'] == 'center :: left':
			print("5")
			# x,y = (wmargin, ((H-h)/2-hmargin))
			wmargin=0
			hmargin=72
			x,y = (wmargin,((H-h)/2-hmargin))
			for line in lines:
				can.drawString(x, y, line)
				y -= int(data['font_size'])
		elif data['type'] == 'bottom :: left':
			print("6")
			wmargin=-50
			hmargin=60
			x,y = (wmargin, hmargin)
			for line in lines:
				can.drawString(x, y, line)
				y -= int(data['font_size'])
		elif data['type'] == 'top :: right':
			print("7")
			wmargin=0
			hmargin=72
			x,y = (W - wmargin - w, H - hmargin - h)
			for line in lines:
				can.drawRightString(x, y, line)
				y -= int(data['font_size'])
		elif data['type'] == 'center :: right':
			print("8")
			wmargin=0
			hmargin=72
			x,y = (W - wmargin - w,((H-h)/2-hmargin))
			for line in lines:
				can.drawRightString(x, y, line)
				y -=int(data['font_size'])
		elif data['type'] == 'bottom :: right':
			print("9")
			wmargin=0
			hmargin=50
			x,y = (W - wmargin - w, hmargin)
			for line in lines:
				can.drawRightString(x, y, line)
				y -= int(data['font_size'])

	
	# textWidth = stringWidth(line2, 'Helvetica', 24) 
	# x += textWidth + 1
	print("10")
	can.showPage()
	can.save()
	print(pk,"pkk")
	print(type(pk))
	import PyPDF2
	from .models import Watermarking
	from azure.storage.blob import BlockBlobService, PublicAccess,ContentSettings
	inputfile="/home/cdms_backend/cdms2/media/A_Sample_PDF.pdf"
	outputfile='/home/cdms_backend/cdms2/Admin_Preview_Watermarkfile/'+filename
	watermarkfile='/home/cdms_backend/cdms2/Admin_Watermark'+filename
	pdf_writer=PyPDF2.PdfFileWriter()
	with open(inputfile, 'rb') as fh:
		pdf=PyPDF2.PdfFileReader(fh)
		with open(OutFile,'rb') as watermarkfile:
			watermarkfile_pdf=PyPDF2.PdfFileReader(watermarkfile)
			for i in range(pdf.getNumPages()):
				p=pdf.getPage(i)
				p.mergePage(watermarkfile_pdf.getPage(0))
				pdf_writer.addPage(p)
				with open(outputfile,'wb') as outputfileeee:
					pdf_writer.write(outputfileeee)
	block_blob_service = BlockBlobService(account_name='newdocullystorage', account_key='qOUUYXZxll+/cVmanzs+riupuL5c19VdDD0egQD/KUA5VUssLYF/hM0TEPcHEKgaFAIEzyglVXY7+AStQZEEig==')
	container_name ='docullycontainer'
	filename_Azurepath=OutFile.split("/").pop()
	print(filename_Azurepath,"filename")
	blob_name=filename_Azurepath
	print(blob_name,"blob_name")
	block_blob_service.create_blob_from_path(
	container_name,
	blob_name,
	outputfile,content_settings=ContentSettings(content_type='application/pdf'))
	watermarking = Watermarking.objects.filter(dataroom_id=pk)
	for i in watermarking:
		# print(i,"loop")
		i.attachments = OutFile
		# print("data.attachments ===>",data.attachments)
		i.save()

	
	
	
	
	# d=dict(attachments=OutFile)
	# print(d,"dict d")
	# watermarking = Watermarking.objects.filter(dataroom_id=pk).update(**d)
	# for data in datas:
	# 	data.attachments = OutFile
	# 	print("data.attachments ===>",data)
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
	# 	# print("----------",x)
	# 	page = existing_pdf.getPage(x)
	# 	page.mergePage(new_pdf.getPage(0))
	# 	output.addPage(page)
	# Finally, write "output" to a real file
	# outputStream = open("media/watermark/"+name, "wb")
	# output.write(outputStream)
	# outputStream.close()
	# group_folder.watermarking_file = "watermark/"+name
	# group_folder.save()


def arrangeText(data, ip, user):
	text = []
	print(data,"dataaaaaaaaaaaa in arange")
	print(data['user_ipaddress'],"user_ipaddress")
	print(data['dataroom'],"dataroom id")
	user_obj = User.objects.get(id=data['user'])
	dataroom_obj = Dataroom.objects.get(id=data['dataroom'])
	print("dataroom_obj-----------", dataroom_obj)
	if data['user_ipaddress'] == True:
		text.append(ip)
	if data['user_name'] == True:
		text.append(user_obj.first_name+' '+user_obj.last_name)
	if data['user_email'] == True:
		text.append(user_obj.email)
	if data['current_time']== True:
		text.append(str(datetime.datetime.now()))
	if data['dataroom_name'] == True:
		text.append(dataroom_obj.dataroom_name)
	if data['custom_text']:
		text.append(data['custom_text'])
	print("Texttttttttt", text)
	return text


# datass = ['center :: right','center :: left','center :: center','top :: left', 'top :: center',
# 		'top :: right', 'bottom :: left', 'bottom :: center', 'bottom :: right']

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