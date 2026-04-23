from .models import QuestionAnswer
from django.template.loader import render_to_string, get_template
from django.core.mail import EmailMessage, EmailMultiAlternatives

def getExcelDataQnaReport(data):
	datas = []
	for da in data: 
		if da['pending'] == True:
			status = "Unanswered"
		else:
			status = "Answered"
		act = ()
		act = act + (da.get('question'),da.get('user').get('first_name')+' '+da.get('user').get('last_name'),da.get('category').get('categories_name'), status, str(da.get('created_date')), str(da.get('folder').get('name')), str(da.get('answer')), str(da.get('updated_date')))
		datas.append(act)
	header_data = [
		'Question','Submitted By','Category', 'Status', 'Posted On','File Name', 'Answer', 'Answered Date'
		]
	return header_data, datas

def send_qna_reply_mail(data):
	qna = QuestionAnswer.objects.get(id=data.get('qna'))
	subject = "Replied to your Question****"
	to = [qna.user.email]
	from_email = data.get('user').get('email')
	from constants.constants import backend_ip
	ctx = {
		'email': to,
		'subject': subject,
		'data':data,
		'qna':qna
	}
	message = get_template('emailer/replied_question.html').render(ctx)
	msg = EmailMessage(subject, message, to=to, from_email=from_email)
	# msg.attach_file(data.path.path)
	msg.content_subtype = 'html'
	msg.send()
	print ("Email send.")
	return True
