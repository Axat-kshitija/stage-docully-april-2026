from django.conf import settings
# from data_documents.views import az_name,az_key
# from storages.backends.s3boto3 import S3Boto3Storage

# class StaticStorage(S3Boto3Storage):
#     location = settings.AWS_STATIC_LOCATION

# class PublicMediaStorage(S3Boto3Storage):
#     location = settings.AWS_PUBLIC_MEDIA_LOCATION
#     file_overwrite = False

# class PrivateMediaStorage(S3Boto3Storage):
#     location = settings.AWS_PRIVATE_MEDIA_LOCATION
#     default_acl = 'private'
#     file_overwrite = False
#     custom_domain = False

# Azure_name=az_name
# Azure_key=az_key
# Azure_name = 'docullystorage'
# Azure_key = 'vyjT1gd5pbx4rlFFo+Q+5z5c3lZBENmF3yBFP9ZjohlWO4y1f1jic39sHatukVPL8dqP4OERbWFQ+AStzUWTnQ=='
Azure_name = 'newdocullystorage'
Azure_key = 'qOUUYXZxll+/cVmanzs+riupuL5c19VdDD0egQD/KUA5VUssLYF/hM0TEPcHEKgaFAIEzyglVXY7+AStQZEEig=='
# Azure_name='uaestorageaccount'
# Azure_key='w7B2do4P0kzcaAWZytcl4dcLq9CSfyDVdyLojw1+drGvJK3EfmqWbtvRlJiqt8xpfGaErwYDd81Z+AStFuaMAQ=='

from storages.backends.azure_storage import AzureStorage

class AzureMediaStorage(AzureStorage):
   # account_name = 'docullystorage'
   # account_key = 'vyjT1gd5pbx4rlFFo+Q+5z5c3lZBENmF3yBFP9ZjohlWO4y1f1jic39sHatukVPL8dqP4OERbWFQ+AStzUWTnQ=='
   account_name = Azure_name
   account_key = Azure_key
   print('----------azure=======',account_name)
   azure_container = 'docullycontainer'
   expiration_secs = None


class AzureMediaStorage1(AzureStorage):
   # account_name = 'docullystorage'
   # account_key = 'vyjT1gd5pbx4rlFFo+Q+5z5c3lZBENmF3yBFP9ZjohlWO4y1f1jic39sHatukVPL8dqP4OERbWFQ+AStzUWTnQ=='
   account_name = 'uaestorageaccount'
   account_key = 'w7B2do4P0kzcaAWZytcl4dcLq9CSfyDVdyLojw1+drGvJK3EfmqWbtvRlJiqt8xpfGaErwYDd81Z+AStFuaMAQ=='
   print('----------azure======1111=',account_name)
   azure_container = 'docullycontainer'
   expiration_secs = None

class AzureStaticStorage(AzureStorage):
   account_name = 'newdocullystorage'
   account_key = 'qOUUYXZxll+/cVmanzs+riupuL5c19VdDD0egQD/KUA5VUssLYF/hM0TEPcHEKgaFAIEzyglVXY7+AStQZEEig=='
   azure_container = 'docullycontainer'
   expiration_secs = None
class AzureUserImageStorage(AzureStorage):
   account_name = 'newdocullystorage'
   account_key = 'qOUUYXZxll+/cVmanzs+riupuL5c19VdDD0egQD/KUA5VUssLYF/hM0TEPcHEKgaFAIEzyglVXY7+AStQZEEig=='
   azure_container = 'quickstartblobs'
   expiration_secs = None