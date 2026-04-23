import os
# Create your tests here.
from . import utils
# from celery import Celery
# from myapp.watermark import apply_watermark
from dataroom.models import Dataroom
from data_documents.models import DataroomFolder,BulkDownloadFiles,BulkDownloadstatus
from background_task import background
# from celery import shared_task  # Disabled - not needed for local development
from zipfile import ZipFile
from django.core.mail import EmailMessage, EmailMultiAlternatives
# app = Celery('tasks', broker='redis://localhost:6379/0')

# @app.task
# @background(schedule=0)
# from celery import shared_task
from django.db.models import Max, F

# Celery tasks disabled for local development
def shared_task(func):
    """Dummy decorator to replace celery.shared_task"""
    return func


@shared_task
def process_files(data,file_name,alldata,directory_name):

    # request=alldata['request']
    docaspdf=alldata['docaspdf']
    exelaspdf=alldata['exelaspdf']
    dataroomid=alldata['dataroomid']
    dataindex=alldata['dataindex']
    watermakingcheck=alldata['watermakingcheck']
    bulkid=alldata['bulkid']
    objid=alldata['objid']
    is_la_user=alldata['la_member']
    is_dataroom_admin=alldata['admin_member']
    ip_add=alldata['ip_add']
    # is_file_irm=False
    

    # print("check bulk data",data['data'])
    for file in data['data']:
        # print(file['perm']['is_view_and_print_and_download'])
        file_path_=DataroomFolder.objects.filter(id=file['id']).last()
        if 'is_folder' in file:
            if file['is_folder']:
                print(file,'898989898')
                if is_la_user or is_dataroom_admin:
                    directory = str(directory_name).replace('__',' ')+'/'+str(file['index'])+' '+str(file['name'])
                    # print(directory)
                    # print('2',file['name'])

                    os.mkdir(''+directory+'')
                    # break
                    # user = request.user
                    utils.get_sub_listtwo2(alldata['user_id'],file['id'], directory,file_path_,docaspdf,exelaspdf,dataroomid,dataindex,watermakingcheck,bulkid,objid,ip_add,data,alldata,file_name)

                elif file['is_view_and_print_and_download']==True:
                ## changed the key giving error
                # elif file["perm"]['is_view_and_print_and_download']==True:
                    directory = str(directory_name).replace('__',' ')+'/'+str(file['index'])+' '+str(file['name'])
                    # print(directory)
                    # print('2',file['name'])

                    os.mkdir(''+directory+'')
                    # break
                    # user = request.user
                    utils.get_sub_listtwo2(alldata['user_id'],file['id'], directory,file_path_,docaspdf,exelaspdf,dataroomid,dataindex,watermakingcheck,bulkid,objid,ip_add,data,alldata,file_name)
                    # break
            if not file['is_folder']:
                if file['perm']['is_view_and_print_and_download']==True:
                    # user = request.user
                    
                    utils.downloadtwo2(alldata['user_id'],str(file_path_.path.url), str(directory_name)+'/',file_path_,docaspdf,exelaspdf,dataroomid,dataindex,watermakingcheck,bulkid,objid,ip_add,data,alldata,file_name)

        else:
            if file['folder']['is_folder']:
                if is_la_user or is_dataroom_admin:
                    try:
                        # print('1',file['folder']['name'])
                        os.mkdir(str(directory_name)+'/'+str(file['index'])+' '+str(file['folder']['name']))
                        # break
                        # user = request.user
                        utils.get_sub_listtwo2(alldata['user_id'],file['folder']['id'], str(directory_name)+'/'+str(file['folder']['name']),file_path_,docaspdf,exelaspdf,dataroomid,dataindex,watermakingcheck,bulkid,objid,ip_add,data,alldata,file_name)

                    except:
                        print("File Exist")
                elif file['folder']['perm']['is_view_and_print_and_download']==True:
                    try:
                        # print('1',file['folder']['name'])
                        os.mkdir(str(directory_name)+'/'+str(file['index'])+' '+str(file['folder']['name']))
                        # break
                        # user = request.user
                        utils.get_sub_listtwo2(alldata['user_id'],file['folder']['id'], str(directory_name)+'/'+str(file['folder']['name']),file_path_,docaspdf,exelaspdf,dataroomid,dataindex,watermakingcheck,bulkid,objid,ip_add,data,alldata,file_name)

                    except:
                        print("File Exist")
                    # break
            if not file['folder']['is_folder']:

                if is_la_user or is_dataroom_admin:
                    # user = request.user
                    # file_path_=DataroomFolder.objects.filter(id=file['id']).last()
                    try:
                        utils.downloadtwo2(alldata['user_id'],str(file_path_.path.url), str(directory_name)+'/',file_path_,docaspdf,exelaspdf,dataroomid,dataindex,watermakingcheck,bulkid,objid,ip_add,data,alldata,file_name)                                
                    except:
                        print('-------------------------------------------exception taskss 1111',e)
                        BulkDownloadfailFiles.objects.create(folder_id=file_path_.id,user_id=alldata['user_id'],dataroom_id=dataroomid,bulk_event_id=bulkid,batch_id=objid)                        
                        # pass

                elif file['folder']['perm']['is_view_and_print_and_download']==True:
                    # user = request.user
                    try:
                        utils.downloadtwo2(alldata['user_id'],str(file_path_.path.url), str(directory_name)+'/',file_path_,docaspdf,exelaspdf,dataroomid,dataindex,watermakingcheck,bulkid,objid,ip_add,data,alldata,file_name,is_file_irm)
                    except:
                        # pass
                        print('-------------------------------------------exception tasks 22',e)
                        BulkDownloadfailFiles.objects.create(folder_id=file_path_.id,user_id=alldata['user_id'],dataroom_id=dataroomid,bulk_event_id=bulkid,batch_id=objid)
        # BulkDownloadstatus.objects.filter(id=objid).update(successfilescount=F('successfilescount')+1)
    
    bulkdown = BulkDownloadstatus.objects.filter(id=objid).last()
    print('----------------------------------------------------======+++++++++++++++',bulkdown.is_file_irm)
    if bulkdown.is_file_irm==False:
        if (int(bulkdown.filecount)+int(bulkdown.successfilescount)) == int(bulkdown.successfilescount):
            print('----------##$$$$$$$$####****************inside if')
            # file_name1=alldata['file_name1']
            file_paths_1 = []
            directory_name_array = []
            file_paths = []
            directory_name_array = [''+str(file_name)+'']
            # directory_name=f"/home/cdms_backend/cdms2/media/{file_name}"
            # print('=========str(directory_name)',str(directory_name))
            # print('movinggg 000',os.system("mv -v "+str(directory_name)+" "+str('/home/cdms_backend/cdms2/media/../')))
            os.chdir('/home/cdms_backend/cdms2/media/')
            print('-------directoryy_name_arey',directory_name_array)
            for file_name_1 in directory_name_array:
                # print('------------filename',file_name_1)
                if os.path.isdir(file_name_1):
                    
                    file_paths_1 = utils.get_all_file_paths(file_name_1)
                    for file in file_paths_1:
                        # print('---------file======',file)
                        file_paths.append(file)


        #        zipFileName = utils.randomString2(8)
            #writing files to a zipfile
            with ZipFile('/home/cdms_backend/cdms2/media/'+str(file_name)+'.zip','w') as zip:
                # print(file_paths,'PPPPPPPPPPPPPPPPPP')
                for file in file_paths:
                    outzipname=str(file).replace('/'+str(file_name),'')
                    # print(file,'23232323232323gggggggggggggggggggggg')
                    # print(file,'23232323232323gggggggggggggggggggggg')

                    zip.write(file,outzipname)
            # os.system("rm -r ./"+str(file_name)+"")
            # print(file_name, "ffffffffffff",str(file_name).split('.'), file_name)
            # fsize=os.stat('media'+str(file_name).split('.')[0]+'.zip')
            fsize=os.path.getsize('/home/cdms_backend/cdms2/media/'+str(file_name)+'.zip')/float(1<<20)
            # result = {"size":round(fsize, 2),
            #     "name":str(file_name1)+'.zip',
            #     "path":'/home/cdms_backend/cdms2/media/'+str(file_name)+'.zip'
            #     }
            BulkDownloadstatus.objects.filter(id=objid).update(readytodownload=True)














#     file_name1=alldata['file_name1']
#     file_paths_1 = []
#     directory_name_array = []
#     file_paths = []
#     directory_name_array = [''+str(file_name)+'']
#     print('=========str(directory_name)',str(directory_name))
#     # print('movinggg 000',os.system("mv -v "+str(directory_name)+" "+str('/home/cdms_backend/cdms2/media/../')))
#     os.chdir('/home/cdms_backend/cdms2/media/')
#     print('-------directoryy_name_arey',directory_name_array)
#     for file_name_1 in directory_name_array:
#         # print('------------filename',file_name_1)
#         if os.path.isdir(file_name_1):
            
#             file_paths_1 = utils.get_all_file_paths(file_name_1)
#             for file in file_paths_1:
#                 # print('---------file======',file)
#                 file_paths.append(file)


# #        zipFileName = utils.randomString2(8)
#     #writing files to a zipfile
#     with ZipFile('/home/cdms_backend/cdms2/media/'+str(file_name)+'.zip','w') as zip:
#         # print(file_paths,'PPPPPPPPPPPPPPPPPP')
#         for file in file_paths:
#             outzipname=str(file).replace('/'+str(file_name),'')
#             # print(file,'23232323232323gggggggggggggggggggggg')
#             # print(file,'23232323232323gggggggggggggggggggggg')

#             zip.write(file,outzipname)
#     # os.system("rm -r ./"+str(file_name)+"")
#     # print(file_name, "ffffffffffff",str(file_name).split('.'), file_name)
#     # fsize=os.stat('media'+str(file_name).split('.')[0]+'.zip')
#     fsize=os.path.getsize('/home/cdms_backend/cdms2/media/'+str(file_name)+'.zip')/float(1<<20)
#     result = {"size":round(fsize, 2),
#         "name":str(file_name1)+'.zip',
#         "path":'/home/cdms_backend/cdms2/media/'+str(file_name)+'.zip'
#         }
#     BulkDownloadstatus.objects.filter(id=objid).update(readytodownload=True)

#     # if result['size'] > 0 and result['path'] is not None:
#     #   # print("enter bulk")
#     #   BulkDownloadFiles.objects.create(user_id=user.id,file_name=result['name'],dataroom_id=data['data'][0]['dataroom'],folder_id=data['data'][0]['id'])
#     # else:
#     #   pass
#     if data['notifyemail']:
#         from_email = settings.DEFAULT_FROM_EMAIL
#         subject='Your Files are Ready to Download on '+str(dataaobj.dataroom.dataroom_nameFront)+' on DocullyVDR.'
#         ctx = {
#             'user': str(user.first_name)+' '+str(user.last_name),
#             'Dataroomname': str(dataaobj.dataroom.dataroom_nameFront),
#         }
#         message = get_template('emailer/bulkdownloadnotify.html').render(ctx)
#         msg = EmailMessage(subject, message, to=[user.email], from_email=from_email)
#         msg.content_subtype = 'html'
#         msg.send()
#     return True



from azure.storage.blob import BlockBlobService

# Celery is disabled for local development - using dummy decorator
def shared_task(func):
    return func

import os
import requests
@shared_task
def irm_file_reupload_delayed_task(file_name,file_name1,download_url,headers5):
    sas_url = '?sv=2021-10-04&ss=btq`f&srt=sco&st=2023-02-25T11%3A51%3A17Z&se=2024-02-25T11%3A51%3A00Z&sp=rl&sig=AWXxw55%2FTC%2BUSOIlVQC3naDahCCebIBNszSFRdqRfBc%3D'
    block_blob_service = BlockBlobService(account_name='docullystorage', account_key='vyjT1gd5pbx4rlFFo+Q+5z5c3lZBENmF3yBFP9ZjohlWO4y1f1jic39sHatukVPL8dqP4OERbWFQ+AStzUWTnQ==',sas_token = sas_url)
    container_name ='docullycontainer'
    reponse5=requests.request("GET", download_url, headers=headers5)
    os.chdir('/home/cdms_backend/cdms2/media/irm_files')
    output_file = file_name1

    response = requests.get(download_url)
    with open(output_file, "wb") as f:
        f.write(response.content)

    block_blob_service.create_blob_from_path(
    container_name,
    file_name,
    file_name1)
    print("Delayed task executed after 15 minutes")







@shared_task
def irm_file_bulk_download(file_name12,download_url,headers5,datas_id,user_id,dataroomid,bulkid,objid,data,alldata,file_name):
    # sas_url = '?sv=2021-10-04&ss=btq`f&srt=sco&st=2023-02-25T11%3A51%3A17Z&se=2024-02-25T11%3A51%3A00Z&sp=rl&sig=AWXxw55%2FTC%2BUSOIlVQC3naDahCCebIBNszSFRdqRfBc%3D'
    # block_blob_service = BlockBlobService(account_name='docullystorage', account_key='vyjT1gd5pbx4rlFFo+Q+5z5c3lZBENmF3yBFP9ZjohlWO4y1f1jic39sHatukVPL8dqP4OERbWFQ+AStzUWTnQ==',sas_token = sas_url)
    # container_name ='docullycontainer'
    print('-------------------@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
    reponse5=requests.request("GET", download_url, headers=headers5)
    # os.chdir('/home/cdms_backend/cdms2/irm_files')
    output_file = file_name12
    print('-------output  file',output_file)

    response = requests.get(download_url)
    with open(output_file, "wb") as f:
        f.write(response.content)

    if BulkDownloadFiles.objects.filter(folder_id=datas_id,user_id=user_id,dataroom_id=dataroomid,bulk_event_id=bulkid,batch_id=objid).exists():
        pass
    else:
        BulkDownloadstatus.objects.filter(id=objid).update(successfilescount=F('successfilescount')+1,filecount=F('filecount')-1)
        BulkDownloadFiles.objects.create(folder_id=datas_id,user_id=user_id,dataroom_id=dataroomid,bulk_event_id=bulkid,batch_id=objid)
                            
        bulkdown = BulkDownloadstatus.objects.filter(id=objid).last()
        if (int(bulkdown.filecount)+int(bulkdown.successfilescount)) == int(bulkdown.successfilescount):
            print('----------##$$$$$$$$####****************inside if')
            # file_name1=alldata['file_name1']
            file_paths_1 = []
            directory_name_array = []
            file_paths = []
            directory_name_array = [''+str(file_name)+'']
            # directory_name=f"/home/cdms_backend/cdms2/media/{file_name}"
            # print('=========str(directory_name)',str(directory_name))
            # print('movinggg 000',os.system("mv -v "+str(directory_name)+" "+str('/home/cdms_backend/cdms2/media/../')))
            os.chdir('/home/cdms_backend/cdms2/media/')
            print('-------directoryy_name_arey',directory_name_array)
            for file_name_1 in directory_name_array:
                # print('------------filename',file_name_1)
                if os.path.isdir(file_name_1):
                    
                    file_paths_1 = utils.get_all_file_paths(file_name_1)
                    for file in file_paths_1:
                        # print('---------file======',file)
                        file_paths.append(file)


        #        zipFileName = utils.randomString2(8)
            #writing files to a zipfile
            with ZipFile('/home/cdms_backend/cdms2/media/'+str(file_name)+'.zip','w') as zip:
                # print(file_paths,'PPPPPPPPPPPPPPPPPP')
                for file in file_paths:
                    outzipname=str(file).replace('/'+str(file_name),'')
                    # print(file,'23232323232323gggggggggggggggggggggg')
                    # print(file,'23232323232323gggggggggggggggggggggg')

                    zip.write(file,outzipname)
            # os.system("rm -r ./"+str(file_name)+"")
            # print(file_name, "ffffffffffff",str(file_name).split('.'), file_name)
            # fsize=os.stat('media'+str(file_name).split('.')[0]+'.zip')
            fsize=os.path.getsize('/home/cdms_backend/cdms2/media/'+str(file_name)+'.zip')/float(1<<20)
            # result = {"size":round(fsize, 2),
            #     "name":str(file_name1)+'.zip',
            #     "path":'/home/cdms_backend/cdms2/media/'+str(file_name)+'.zip'
            #     }
            BulkDownloadstatus.objects.filter(id=objid).update(readytodownload=True)

            # if result['size'] > 0 and result['path'] is not None:
            #   # print("enter bulk")
            #   BulkDownloadFiles.objects.create(user_id=user.id,file_name=result['name'],dataroom_id=data['data'][0]['dataroom'],folder_id=data['data'][0]['id'])
            # else:
            #   pass
            # if data['notifyemail']:
            #     from_email = settings.DEFAULT_FROM_EMAIL
            #     subject='Your Files are Ready to Download on '+str(dataaobj.dataroom.dataroom_nameFront)+' on DocullyVDR.'
            #     ctx = {
            #         'user': str(user.first_name)+' '+str(user.last_name),
            #         'Dataroomname': str(dataaobj.dataroom.dataroom_nameFront),
            #     }
            #     message = get_template('emailer/bulkdownloadnotify.html').render(ctx)
            #     msg = EmailMessage(subject, message, to=[user.email], from_email=from_email)
            #     msg.content_subtype = 'html'
            #     msg.send()






@shared_task
def irm_file_bulk_download_single(file_name12,download_url,headers5,datas_id,user_id,dataroomid,bulkid,objid,data,alldata,file_name):
    # sas_url = '?sv=2021-10-04&ss=btq`f&srt=sco&st=2023-02-25T11%3A51%3A17Z&se=2024-02-25T11%3A51%3A00Z&sp=rl&sig=AWXxw55%2FTC%2BUSOIlVQC3naDahCCebIBNszSFRdqRfBc%3D'
    # block_blob_service = BlockBlobService(account_name='docullystorage', account_key='vyjT1gd5pbx4rlFFo+Q+5z5c3lZBENmF3yBFP9ZjohlWO4y1f1jic39sHatukVPL8dqP4OERbWFQ+AStzUWTnQ==',sas_token = sas_url)
    # container_name ='docullycontainer'
    print('-------------------@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
    reponse5=requests.request("GET", download_url, headers=headers5)
    os.chdir('/home/cdms_backend/cdms2/media/irm_files')
    output_file = file_name12
    print('-------output  file',output_file)

    response = requests.get(download_url)
    # os.chmod(output_file, 0o777)
    if os.path.exists(output_file):
        print(" File exists")
        os.remove(output_file)
    with open(output_file, "wb") as f:
        f.write(response.content)

    if BulkDownloadFiles.objects.filter(folder_id=datas_id,user_id=user_id,dataroom_id=dataroomid,bulk_event_id=bulkid,batch_id=objid).exists():
        pass
    else:
        BulkDownloadstatus.objects.filter(id=objid).update(successfilescount=F('successfilescount')+1,filecount=F('filecount')-1)
        BulkDownloadFiles.objects.create(folder_id=datas_id,user_id=user_id,dataroom_id=dataroomid,bulk_event_id=bulkid,batch_id=objid)
                            
        bulkdown = BulkDownloadstatus.objects.filter(id=objid).last()
        if (int(bulkdown.filecount)+int(bulkdown.successfilescount)) == int(bulkdown.successfilescount):
        #     print('----------##$$$$$$$$####****************inside if')
        #     # file_name1=alldata['file_name1']
        #     file_paths_1 = []
        #     directory_name_array = []
        #     file_paths = []
        #     directory_name_array = [''+str(file_name)+'']
        #     # directory_name=f"/home/cdms_backend/cdms2/media/{file_name}"
        #     # print('=========str(directory_name)',str(directory_name))
        #     # print('movinggg 000',os.system("mv -v "+str(directory_name)+" "+str('/home/cdms_backend/cdms2/media/../')))
        #     os.chdir('/home/cdms_backend/cdms2/media/')
        #     print('-------directoryy_name_arey',directory_name_array)
        #     for file_name_1 in directory_name_array:
        #         # print('------------filename',file_name_1)
        #         if os.path.isdir(file_name_1):
                    
        #             file_paths_1 = utils.get_all_file_paths(file_name_1)
        #             for file in file_paths_1:
        #                 # print('---------file======',file)
        #                 file_paths.append(file)


        # #        zipFileName = utils.randomString2(8)
        #     #writing files to a zipfile
        #     with ZipFile('/home/cdms_backend/cdms2/media/'+str(file_name)+'.zip','w') as zip:
        #         # print(file_paths,'PPPPPPPPPPPPPPPPPP')
        #         for file in file_paths:
        #             outzipname=str(file).replace('/'+str(file_name),'')
        #             # print(file,'23232323232323gggggggggggggggggggggg')
        #             # print(file,'23232323232323gggggggggggggggggggggg')

        #             zip.write(file,outzipname)
        #     # os.system("rm -r ./"+str(file_name)+"")
        #     # print(file_name, "ffffffffffff",str(file_name).split('.'), file_name)
        #     # fsize=os.stat('media'+str(file_name).split('.')[0]+'.zip')
        #     fsize=os.path.getsize('/home/cdms_backend/cdms2/media/'+str(file_name)+'.zip')/float(1<<20)
        #     # result = {"size":round(fsize, 2),
        #     #     "name":str(file_name1)+'.zip',
        #     #     "path":'/home/cdms_backend/cdms2/media/'+str(file_name)+'.zip'
        #     #     }
            BulkDownloadstatus.objects.filter(id=objid).update(readytodownload=True)

            # if result['size'] > 0 and result['path'] is not None:
            #   # print("enter bulk")
            #   BulkDownloadFiles.objects.create(user_id=user.id,file_name=result['name'],dataroom_id=data['data'][0]['dataroom'],folder_id=data['data'][0]['id'])
            # else:
            #   pass
            # if data['notifyemail']:
            #     from_email = settings.DEFAULT_FROM_EMAIL
            #     subject='Your Files are Ready to Download on '+str(dataaobj.dataroom.dataroom_nameFront)+' on DocullyVDR.'
            #     ctx = {
            #         'user': str(user.first_name)+' '+str(user.last_name),
            #         'Dataroomname': str(dataaobj.dataroom.dataroom_nameFront),
            #     }
            #     message = get_template('emailer/bulkdownloadnotify.html').render(ctx)
            #     msg = EmailMessage(subject, message, to=[user.email], from_email=from_email)
            #     msg.content_subtype = 'html'
            #     msg.send()




