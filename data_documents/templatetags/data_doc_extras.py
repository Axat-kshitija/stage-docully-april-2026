from django import template
from qna.models import QuestionAnswer

register = template.Library()

@register.simple_tag
def get_rate(crit,):
	rates = QuestionAnswer.objects.filter(qna_id=int(crit))
	return rates
