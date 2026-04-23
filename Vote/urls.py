from django.conf.urls import url
from .views import *

urlpatterns = [
	url(r'^projectName/voting/(?P<pk>[0-9]+)/$', Voting.as_view(), name="voting"),
	url(r'^projectName/voter_group/(?P<pk>[0-9]+)/$', VoterGroupApi.as_view(), name="voter_group"),
	url(r'^projectName/voter_group_member/(?P<pk>[0-9]+)/$', VoterGroupMemberApi.as_view(), name="voter_group_member"),
	url(r'^projectName/vote/(?P<pk>[0-9]+)/$', MemberVoting.as_view(), name="vote"),
	url(r'^projectName/make_vote/(?P<pk>[0-9]+)/$', MakeVote.as_view(), name="make_vote"),
	url(r'^projectName/vote_result/(?P<pk>[0-9]+)/$', VoteResult.as_view(), name="vote_result"),
	url(r'^projectName/vote_count_analysis/(?P<pk>[0-9]+)/$', VoteCountAnalysis.as_view(), name="vote_count_analysis"),
	url(r'^projectName/export_voter_status/(?P<pk>[0-9]+)/$', ExportVoterStatusReport.as_view(), name="export_voter_status"),
	url(r'^projectName/export_vote/(?P<pk>[0-9]+)/$', ExportVoteReport.as_view(), name="export_vote"),
	url(r'^projectName/add_voter/(?P<pk>[0-9]+)/(?P<pk2>[0-9]+)/$', AddVoter.as_view(), name="add_voter"),
	url(r'^projectName/del_group_member/(?P<pk>[0-9]+)/$', DelVoterGroupMember.as_view(), name="del_group_member"),
	url(r'^projectName/upload_attachment/$', UploadVotingAttachment.as_view(), name="upload_attachment"),
    url(r'^projectName/votefile-view/(?P<pk>[0-9]+)/(?P<pk1>[0-9]+)/$', file_view, name="votefile_view"),

]
