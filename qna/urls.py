from django.conf.urls import url
from .views import *

urlpatterns = [
	url(r'^projectName/qna_view_detail/(?P<pk>[0-9]+)/$', QuestionAnswerDetails.as_view()),
    url(r'^projectName/Create_question/(?P<pk>[0-9]+)/$', Create_question.as_view()),
    url(r'^projectName/user_qna_details/(?P<pk>[0-9]+)/$', UserQnaDetails.as_view()),
    url(r'^projectName/qna_view/(?P<pk>[0-9]+)/$', QuestionAnswerView.as_view()),
    url(r'^projectName/qa_view/(?P<pk>[0-9]+)/$', QAnswerView.as_view()),
    url(r'^projectName/get_reqply_list/(?P<pk>[0-9]+)/$', GetQaReplyView.as_view()),
    url(r'^projectName/accept_question/$', AcceptQuestion.as_view()),
    url(r'^projectName/send_question/(?P<pk>[0-9]+)/$', SendQuestionView.as_view()),
    url(r'^projectName/reg_question/(?P<pk>[0-9]+)/$', RegQuestionView.as_view()),
    url(r'^projectName/qna_report/(?P<pk>[0-9]+)/$', QAnswerReport.as_view()),
    url(r'^projectName/export_qna/(?P<pk>[0-9]+)/$', ExportQNA.as_view()),
    url(r'^projectName/qna_analytics/(?P<pk>[0-9]+)/$', QAnswerAnalytics.as_view()),
    url(r'^projectName/qna_filter_view/(?P<pk>[0-9]+)/(?P<pk1>[-,0-9]+)/$', QuestionAnswerFilteringView.as_view()),
    url(r'^projectName/add_or_remove_faq/(?P<pk>[0-9]+)/$', AddOrRemoveFaq.as_view()),

]
