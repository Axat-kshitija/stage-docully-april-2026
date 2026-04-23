from django.db import models

# Create your models here.

from django.db import models
#from django.contrib.auth.models import User, Group
from userauth.models import User 

from django.utils import timezone

class EmailerType(models.Model):
	emailer_type = models.CharField(max_length=100, blank=False)

class Emailer(models.Model):
    user = models.ForeignKey(User, models.CASCADE)
    from_email = models.CharField(max_length=100, blank=True)
    subject = models.CharField(max_length=10000, blank=True)
    body_html = models.CharField(max_length = 10000, blank=True)
    emailer_type = models.ForeignKey(EmailerType, models.CASCADE)
    to_email = models.CharField(max_length=100, blank=True, default='dhananjay.s@axat-tech.com')
    email_sent_date = models.DateTimeField(auto_now_add=True)

class SiteSettings(models.Model):
	domain_name = models.CharField(max_length=1000, blank=True)
	support_email_id = models.CharField(max_length=1000, blank=True)
	help_email_id = models.CharField(max_length = 1000, blank=True)
	phone_no = models.CharField(max_length =100 , blank=True)
	domain_url = models.CharField(max_length=1000, blank=True)
	
	def save(self, *args, **kwargs):
		self.pk = 1
		super(SiteSettings, self).save(*args, **kwargs)


	def delete(self, *args, **kwargs):
		pass

	@classmethod
	def load(cls):
		obj, created = cls.objects.get_or_create(pk=1)
		return obj


