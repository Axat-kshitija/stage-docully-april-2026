from emailer.models import Emailer, SiteSettings


domain = ""#SiteSettings.objects.get(id=1)#"http://34.212.28.247:8070/"
# LOCALHOST_SERVER = "http://34.212.28.247:8070/"
LOCALHOST_SERVER = "http://52.172.204.102:8000/"
# LOCALHOST_SERVER = "https://services.docullyvdr.com/"

domain = LOCALHOST_SERVER
# domain = 'https://services.docullyvdr.com/'
link =  domain#domain.domain_url