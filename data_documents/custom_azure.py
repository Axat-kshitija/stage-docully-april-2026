from storages.backends.azure_storage import AzureStorage

class AzureMediaStorage(AzureStorage):
    account_name = 'newdocullystorage' 
    account_key = 'qOUUYXZxll+/cVmanzs+riupuL5c19VdDD0egQD/KUA5VUssLYF/hM0TEPcHEKgaFAIEzyglVXY7+AStQZEEig=='
    azure_container = 'docullycontainer'
    expiration_secs = None

class AzureStaticStorage(AzureStorage):
    account_name = 'newdocullystorage'
    account_key = 'qOUUYXZxll+/cVmanzs+riupuL5c19VdDD0egQD/KUA5VUssLYF/hM0TEPcHEKgaFAIEzyglVXY7+AStQZEEig=='
    azure_container = 'docullycontainer'
    expiration_secs = None
