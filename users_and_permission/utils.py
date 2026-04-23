from datetime import datetime, timedelta


def send_inviatation_email_to_admin():
	print ("send send_inviatation_email")

def send_invitation_email_to_enduser():
	print ("send invitation email to user")

def set_permission(grpprm, data):
	if grpprm.is_watermarking== True:
		data['is_watermarking'] = True
	else:
		data['is_watermarking'] = False

	if grpprm.is_overview == True:
		data['is_overview'] = True
	else:
		data['is_overview'] = False

	if grpprm.is_drm == True:
		data['is_drm'] = True
	else:
		data['is_drm'] = False

	if grpprm.is_q_and_a == True:
		data['is_q_and_a'] = True
	else:
		data['is_q_and_a'] = False

	if grpprm.is_reports == True:
		data['is_reports'] = True
	else:
		data['is_reports'] = False

	if grpprm.is_updates == True:
		data['is_updates'] = True
	else:
		data['is_updates'] = False

	if grpprm.is_users_and_permission == True:
		data['is_users_and_permission'] = True
	else:
		data['is_users_and_permission'] = False

	if grpprm.is_edit_index == True:
		data['is_edit_index'] = True
	else:
		data['is_edit_index'] = False

	if grpprm.is_voting == True:
		data['is_voting'] = True
	else:
		data['is_voting'] = False

	# print("dataa", data)
	return data

def getExcelDataUsersStatusReport(data):
	datas = []
	for da in data:
		status = 'Inactive'
		if da.get('memberactivestatus'):
			status = 'Active'

		
		if da.get('is_dataroom_admin') == True:
			member_type = 'Admin'
		elif da.get('is_end_user') == True:
			member_type = 'End User'
		else:
			member_type = 'Limited Access User'
		act = ()
		temppp2=da.get('invitatation_sent_date')
		# temppp2 = datetime.strptime(temppp,"%Y-%m-%dT%H:%M:%S.%f")
		# print('_____this date___________',temppp2)
		date22=da.get('last_view')
		if date22:
			temppp22 = date22
			act = act + (da.get('member').get('first_name')+' '+da.get('member').get('last_name'),da.get('member').get('email'), temppp2, da.get('member_added_by').get('first_name')+' '+da.get('member_added_by').get('last_name'),da.get('invitatation_acceptance_date'), member_type,temppp22, status, )
		else:
			act = act + (da.get('member').get('first_name')+' '+da.get('member').get('last_name'),da.get('member').get('email'), temppp2, da.get('member_added_by').get('first_name')+' '+da.get('member_added_by').get('last_name'),da.get('invitatation_acceptance_date'), member_type,' ', status, )

		datas.append(act)
	header_data = [
		'Member','Email Id','Invitation Send Date', 'Invitation By','Dataroom Joining Date', 'Member Type', 'Last View', 'User Status'
		]
	# print(datas)
	return header_data, datas


def getExcelDataUsersGroupsReport(data):
	datas = []
	for da in data: 
		status = 'Inactive'
		if da.get('memberactivestatus'):
			status = 'Active'
		if da.get('invitatation_sent_date') == '' or da.get('invitatation_sent_date') == None:
			date1 = ' '
		else:
			# print(da.get('date_joined'))
			# dateobject=datetime.strptime(str(da.get('date_joined')).replace('T',' '),'%d/%m/%Y %H:%M:%S.%f')
			date1=da.get('invitatation_sent_date')
			# date1=datetime.strptime(str(da.get('date_joined')),'%d/%m/%Y %H:%M:%S')

		act = ()
		act = act + (da.get('member').get('first_name')+' '+da.get('member').get('last_name'), da.get('group'),date1,da.get('invitatation_acceptance_date'),status,da.get('member_added_by').get('first_name') )
		datas.append(act)
	header_data = [
		'User','Group','Invitation Send Date','Dataroom Joining Date','User Status','Invited By'
		]
	return header_data, datas
