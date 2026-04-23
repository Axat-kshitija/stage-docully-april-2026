from django.template.loader import render_to_string, get_template
from django.core.mail import EmailMessage, EmailMultiAlternatives
import logging
from django.conf import settings


def send_personal_message(msg):
	
	subject = msg.user_send.first_name+" send you a personal message on Docully"
	to = [msg.user_rec.email]
	from_email = settings.DEFAULT_FROM_EMAIL
	
	ctx = {
		'subject': subject,
		'data':msg,
	}
	message = get_template('emailer/notification/send_personal_message.html').render(ctx)
	msg = EmailMessage(subject, message, to=to, from_email=from_email)
	msg.content_subtype = 'html'
	msg.send()
	# print ("Email send.")
	return True

def send_replied_message(msg):
	subject = msg.user_send.first_name+" replied to your message on Docully"
	to = [msg.user_rec.email]
	from_email = settings.DEFAULT_FROM_EMAIL
	
	ctx = {
		'subject': subject,
		'data':msg,
	}
	message = get_template('emailer/notification/send_replied_message.html').render(ctx)
	msg = EmailMessage(subject, message, to=to, from_email=from_email)
	msg.content_subtype = 'html'
	msg.send()
	# print ("Email send.")
	return True
