from django.conf.urls import url
from .views import *


urlpatterns = [
    url(r'^projectName/my_team/$', MyTeamsApiView.as_view(), name="my_team"),
	url(r'^projectName/my_team_detail_view/(?P<pk>[0-9]+)/$', MyTeamDetailView.as_view()),
	url(r'^projectName/my_team_branding_detail_view/(?P<pk>[0-9]+)/$', MyTeamBrandingDetailView.as_view()),
	url(r'^projectName/revert_default_my_team_branding_setting/(?P<pk>[0-9]+)/$', RevertDefaultMyTeamBrandingSetting.as_view()),
	url(r'^projectName/upload_my_team_logo/(?P<pk>[0-9]+)/$', UploadMyTeamLogo.as_view(), name="my_team"),
	url(r'^projectName/upload_my_team_branding_logo/(?P<pk>[0-9]+)/$', UploadMyTeamBrandingLogo.as_view(), name="my_team_branding"),
	url(r'^projectName/add_new_member_to_my_team/(?P<pk>[0-9]+)/$', AddNewMemberToTeam.as_view(), name="add_new_member_to_team"),
	url(r'^projectName/delete_member_from_my_team/(?P<pk>[0-9]+)/$', DeleteMemberFromMyTeam.as_view(), name="delete_member_from_my_team"),
    url(r'^projectName/my_chanel/$', chanelApiView.as_view(), name="my_chanel"),
	url(r'^projectName/add_new_member_to_my_chanel/(?P<pk>[0-9]+)/$', AddNewMemberTochanel.as_view(), name="add_new_member_to_chanel"),
	url(r'^projectName/chanel_dashboard/$', chanel_dashboard.as_view(), name="chanel_dashboard"),
	url(r'^projectName/chanel_allmember/$', chanel_allmember.as_view(), name="chanel_allmember"),
	url(r'^projectName/delete_member_from_chanel/(?P<pk>[0-9]+)/$', DeleteMemberFromchanel.as_view(), name="DeleteMemberFromchanel"),
	url(r'^projectName/Delete_team/(?P<pk>[0-9]+)/$', Deleteteamm.as_view(), name="Deleteteamm"),
	url(r'^projectName/chanelteamapi/$', chanelteamView.as_view(), name="chanelteam"),
	url(r'^projectName/Delete_channel/(?P<pk>[0-9]+)/$', Deletechanel.as_view(), name="Deletechanel"),
	url(r'^projectName/team_allmember/(?P<pk>[0-9]+)/$', team_allmember.as_view(), name="team_allmember"),
	url(r'^projectName/silveronline/$', silveronline.as_view(), name="silveronline"),
	url(r'^projectName/goldonline/$', goldonline.as_view(), name="goldonline"),
	url(r'^projectName/platinumonline/$', platinumonline.as_view(), name="platinumonline"),
	url(r'^projectName/trialonline/$', trialonline.as_view(), name="trialonline"),
	url(r'^projectName/teamalluseronline/$', team_alluseronline.as_view(), name="teamalluseronline"),
	url(r'^projectName/myteamonlinedashboard/$', myteamonline_dashboard.as_view(), name="myteamonlinedashboard"),
	url(r'^projectName/directdeletedataroom/(?P<pk>[0-9]+)/$', directdeletedataroom.as_view(), name="directdeletedataroom"),
	url(r'^projectName/teamdeletiononline/(?P<pk>[0-9]+)/$', teamdeletiononline.as_view(), name="teamdeletiononline"),
	url(r'^projectName/globalsearchteamdataroom/(?P<pk>[0-9]+)/$', globalsearchteamdataroom.as_view(), name="globalsearchteamdataroom"),
	url(r'^projectName/globalsearchteamdataroomid/$', globalsearchteamdataroomid.as_view(), name="globalsearchteamdataroomid"),

]
