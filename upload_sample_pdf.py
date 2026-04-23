from azure.storage.blob import BlockBlobService, ContentSettings

bbs = BlockBlobService(
    account_name='newdocullystorage',
    account_key='qOUUYXZxll+/cVmanzs+riupuL5c19VdDD0egQD/KUA5VUssLYF/hM0TEPcHEKgaFAIEzyglVXY7+AStQZEEig=='
)

# Upload default dataroom icon
bbs.create_blob_from_path(
    'docullycontainer',
    'images/dataroom-icon.png',
    '/home/cdms_backend/cdms2/static/assets/images/dataroom-icon.png',
    content_settings=ContentSettings(content_type='image/png')
)
print('dataroom-icon.png uploaded successfully!')
