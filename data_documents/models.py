from django.db import models
from userauth.models import User, Profile
from dataroom.models import Dataroom
import uuid
from django.db.models.signals import post_save
from django.dispatch import receiver
from dms.custom_azure import AzureMediaStorage,AzureMediaStorage1

from dms.settings import *

azz=''
def store_dataroom_files(instance, filename): 
    # print ("store dataroom files")
    u_id = instance.user.id
    dataroom_uuid = instance.dataroom.dataroom_uuid
    dataroom_name = instance.dataroom.dataroom_name
    parent_folder_id = instance.parent_folder.id
    # print ("file name is:", filename)
    # global azz
    # if instance.dataroom.is_usa_blob == True:
    #     azz=AzureMediaStorage1 
    #     print('----------------------------------------------------------------tetye',azz)
    # else: 
    #     azz=AzureMediaStorage
    # print("user_id ===>",u_id)
    if instance.is_folder:
        # print ("if instance is folder")
        if instance.is_root_folder:
            # print ("if instance is root folder")
            return '{0}_{1}'.format(dataroom_name, dataroom_uuid)
        else:
            # print ("if instance is not root folder")
            return '{0}_{1}'.format(dataroom_name, dataroom_uuid)
    else:
        # print ("if instance is not folder")
        # print ("file path is", '{0}_{1}/{2}'.format(dataroom_name, dataroom_uuid, filename))
        return '{0}_{1}/{2}'.format(dataroom_name, dataroom_uuid, filename)


def select_storage(instance):
    print('--------inwtqbqqqq',instance)
    return AzureMediaStorage1 if instance.dataroom.is_usa_blob == True else AzureMediaStorage


import datetime
import posixpath

from django import forms
from django.core import checks
from django.core.files.base import File
from django.core.files.images import ImageFile
from django.core.files.storage import Storage, default_storage
from django.core.files.utils import validate_file_name
from django.db.models import signals
from django.db.models.fields import Field
from django.db.models.query_utils import DeferredAttribute
from django.utils.translation import gettext_lazy as _


class FieldFile(File):
    def __init__(self, instance, field, name):
        super().__init__(None, name)
        self.instance = instance
        self.field = field
        # self.storage = field.storage
        if instance.dataroom.is_usa_blob == True:
            self.storage = AzureMediaStorage1()
        else:
            self.storage = AzureMediaStorage()
        self._committed = True

    def __eq__(self, other):
        # Older code may be expecting FileField values to be simple strings.
        # By overriding the == operator, it can remain backwards compatibility.
        if hasattr(other, 'name'):
            return self.name == other.name
        return self.name == other

    def __hash__(self):
        return hash(self.name)

    # The standard File contains most of the necessary properties, but
    # FieldFiles can be instantiated without a name, so that needs to
    # be checked for here.

    def _require_file(self):
        if not self:
            raise ValueError("The '%s' attribute has no file associated with it." % self.field.name)

    def _get_file(self):
        self._require_file()
        if getattr(self, '_file', None) is None:
            self._file = self.storage.open(self.name, 'rb')
        return self._file

    def _set_file(self, file):
        self._file = file

    def _del_file(self):
        del self._file

    file = property(_get_file, _set_file, _del_file)

    @property
    def path(self):
        self._require_file()
        return self.storage.path(self.name)

    @property
    def url(self):
        self._require_file()
        return self.storage.url(self.name)

    @property
    def size(self):
        self._require_file()
        if not self._committed:
            return self.file.size
        return self.storage.size(self.name)

    def open(self, mode='rb'):
        self._require_file()
        if getattr(self, '_file', None) is None:
            self.file = self.storage.open(self.name, mode)
        else:
            self.file.open(mode)
        return self
    # open() doesn't alter the file's contents, but it does reset the pointer
    open.alters_data = True

    # In addition to the standard File API, FieldFiles have extra methods
    # to further manipulate the underlying file, as well as update the
    # associated model instance.

    def save(self, name, content, save=True):
        name = self.field.generate_filename(self.instance, name)
        self.name = self.storage.save(name, content, max_length=self.field.max_length)
        setattr(self.instance, self.field.attname, self.name)
        self._committed = True

        # Save the object because it has changed, unless save is False
        if save:
            self.instance.save()
    save.alters_data = True

    def delete(self, save=True):
        if not self:
            return
        # Only close the file if it's already open, which we know by the
        # presence of self._file
        if hasattr(self, '_file'):
            self.close()
            del self.file

        self.storage.delete(self.name)

        self.name = None
        setattr(self.instance, self.field.attname, self.name)
        self._committed = False

        if save:
            self.instance.save()
    delete.alters_data = True

    @property
    def closed(self):
        file = getattr(self, '_file', None)
        return file is None or file.closed

    def close(self):
        file = getattr(self, '_file', None)
        if file is not None:
            file.close()

    def __getstate__(self):
        # FieldFile needs access to its associated model field, an instance and
        # the file's name. Everything else will be restored later, by
        # FileDescriptor below.
        return {
            'name': self.name,
            'closed': False,
            '_committed': True,
            '_file': None,
            'instance': self.instance,
            'field': self.field,
        }

    def __setstate__(self, state):
        self.__dict__.update(state)
        self.storage = self.field.storage


class FileDescriptor(DeferredAttribute):
    """
    The descriptor for the file attribute on the model instance. Return a
    FieldFile when accessed so you can write code like::

        >>> from myapp.models import MyModel
        >>> instance = MyModel.objects.get(pk=1)
        >>> instance.file.size

    Assign a file object on assignment so you can do::

        >>> with open('/path/to/hello.world') as f:
        ...     instance.file = File(f)
    """
    def __get__(self, instance, cls=None):
        if instance is None:
            return self

        # This is slightly complicated, so worth an explanation.
        # instance.file`needs to ultimately return some instance of `File`,
        # probably a subclass. Additionally, this returned object needs to have
        # the FieldFile API so that users can easily do things like
        # instance.file.path and have that delegated to the file storage engine.
        # Easy enough if we're strict about assignment in __set__, but if you
        # peek below you can see that we're not. So depending on the current
        # value of the field we have to dynamically construct some sort of
        # "thing" to return.

        # The instance dict contains whatever was originally assigned
        # in __set__.
        file = super().__get__(instance, cls)

        # If this value is a string (instance.file = "path/to/file") or None
        # then we simply wrap it with the appropriate attribute class according
        # to the file field. [This is FieldFile for FileFields and
        # ImageFieldFile for ImageFields; it's also conceivable that user
        # subclasses might also want to subclass the attribute class]. This
        # object understands how to convert a path to a file, and also how to
        # handle None.
        if isinstance(file, str) or file is None:
            attr = self.field.attr_class(instance, self.field, file)
            instance.__dict__[self.field.attname] = attr

        # Other types of files may be assigned as well, but they need to have
        # the FieldFile interface added to them. Thus, we wrap any other type of
        # File inside a FieldFile (well, the field's attr_class, which is
        # usually FieldFile).
        elif isinstance(file, File) and not isinstance(file, FieldFile):
            file_copy = self.field.attr_class(instance, self.field, file.name)
            file_copy.file = file
            file_copy._committed = False
            instance.__dict__[self.field.attname] = file_copy

        # Finally, because of the (some would say boneheaded) way pickle works,
        # the underlying FieldFile might not actually itself have an associated
        # file. So we need to reset the details of the FieldFile in those cases.
        elif isinstance(file, FieldFile) and not hasattr(file, 'field'):
            file.instance = instance
            file.field = self.field
            file.storage = self.field.storage

        # Make sure that the instance is correct.
        elif isinstance(file, FieldFile) and instance is not file.instance:
            file.instance = instance

        # That was fun, wasn't it?
        return instance.__dict__[self.field.attname]

    def __set__(self, instance, value):
        instance.__dict__[self.field.attname] = value


class FileField(Field):

    # The class to wrap instance attributes in. Accessing the file object off
    # the instance will always return an instance of attr_class.
    attr_class = FieldFile

    # The descriptor to use for accessing the attribute off of the class.
    descriptor_class = FileDescriptor

    description = _("File")

    def __init__(self, verbose_name=None, name=None, upload_to='', storage=None, **kwargs):
        self._primary_key_set_explicitly = 'primary_key' in kwargs

        self.storage = storage or default_storage
        if callable(self.storage):
            # Hold a reference to the callable for deconstruct().
            self._storage_callable = self.storage
            self.storage = self.storage()
            if not isinstance(self.storage, Storage):
                raise TypeError(
                    "%s.storage must be a subclass/instance of %s.%s"
                    % (self.__class__.__qualname__, Storage.__module__, Storage.__qualname__)
                )
        self.upload_to = upload_to

        kwargs.setdefault('max_length', 100)
        super().__init__(verbose_name, name, **kwargs)

    def check(self, **kwargs):
        return [
            *super().check(**kwargs),
            *self._check_primary_key(),
            *self._check_upload_to(),
        ]

    def _check_primary_key(self):
        if self._primary_key_set_explicitly:
            return [
                checks.Error(
                    "'primary_key' is not a valid argument for a %s." % self.__class__.__name__,
                    obj=self,
                    id='fields.E201',
                )
            ]
        else:
            return []

    def _check_upload_to(self):
        if isinstance(self.upload_to, str) and self.upload_to.startswith('/'):
            return [
                checks.Error(
                    "%s's 'upload_to' argument must be a relative path, not an "
                    "absolute path." % self.__class__.__name__,
                    obj=self,
                    id='fields.E202',
                    hint='Remove the leading slash.',
                )
            ]
        else:
            return []

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        if kwargs.get("max_length") == 100:
            del kwargs["max_length"]
        kwargs['upload_to'] = self.upload_to
        if self.storage is not default_storage:
            kwargs['storage'] = getattr(self, '_storage_callable', self.storage)
        return name, path, args, kwargs

    def get_internal_type(self):
        return "FileField"

    def get_prep_value(self, value):
        value = super().get_prep_value(value)
        # Need to convert File objects provided via a form to string for database insertion
        if value is None:
            return None
        return str(value)

    def pre_save(self, model_instance, add):
        file = super().pre_save(model_instance, add)
        if file and not file._committed:
            # Commit the file to storage prior to saving the model
            file.save(file.name, file.file, save=False)
        return file

    def contribute_to_class(self, cls, name, **kwargs):
        super().contribute_to_class(cls, name, **kwargs)
        setattr(cls, self.attname, self.descriptor_class(self))

    def generate_filename(self, instance, filename):
        """
        Apply (if callable) or prepend (if a string) upload_to to the filename,
        then delegate further processing of the name to the storage backend.
        Until the storage layer, all file paths are expected to be Unix style
        (with forward slashes).
        """
        if callable(self.upload_to):
            filename = self.upload_to(instance, filename)
        else:
            dirname = datetime.datetime.now().strftime(str(self.upload_to))
            filename = posixpath.join(dirname, filename)
        filename = validate_file_name(filename, allow_relative_path=True)
        return self.storage.generate_filename(filename)

    def save_form_data(self, instance, data):
        # Important: None means "no change", other false value means "clear"
        # This subtle distinction (rather than a more explicit marker) is
        # needed because we need to consume values that are also sane for a
        # regular (non Model-) Form to find in its cleaned_data dictionary.
        if data is not None:
            # This value will be converted to str and stored in the
            # database, so leaving False as-is is not acceptable.
            setattr(instance, self.name, data or '')

    def formfield(self, **kwargs):
        return super().formfield(**{
            'form_class': forms.FileField,
            'max_length': self.max_length,
            **kwargs,
        })








# from .fields import DynamicStorageFileField
# from django.db.models.fields.files import FieldFile
# class DynamicStorageFieldFile(FieldFile):

#     def __init__(self, instance, field, name):
#         super(DynamicStorageFieldFile, self).__init__(
#             instance, field, name
#         )
#         if instance.dataroom.is_usa_blob == True:
#             self.storage = AzureMediaStorage1
#         else:
#             self.storage = AzureMediaStorage


# class DynamicStorageFileField(models.FileField):
#     attr_class = DynamicStorageFieldFile

#     def pre_save(self, model_instance, add):
#         if model_instance.dataroom.is_usa_blob == True:
#             storage = AzureMediaStorage1
#         else:
#             storage = AzureMediaStorage
#         self.storage = storage
#         model_instance.path.storage = storage
#         path = super(DynamicStorageFileField, self
#                      ).pre_save(model_instance, add)
#         return path




class DataroomFolder(models.Model):
    user = models.ForeignKey(User, models.CASCADE, related_name="dataroom_folder_user")
    dataroom = models.ForeignKey(Dataroom, models.CASCADE)
    name = models.CharField(max_length=1000, null=True, blank=True)
    path = FileField(blank= True, upload_to=store_dataroom_files, null=True, default="",max_length=500)
    index = models.IntegerField(default=0)
    is_file_index = models.IntegerField(default=0)
    last_updated_user = models.ForeignKey(User, models.CASCADE, related_name="last_updated_user")
    parent_path = models.CharField(max_length=1000, null=True, blank=True)
    is_root_folder = models.BooleanField(default=False)
    is_folder = models.BooleanField(default=False)
    is_infected = models.BooleanField(default=False)
    file_content_type = models.CharField(max_length=1000, blank=True, null=True)
    file_size = models.FloatField(blank=True, null=True)
    parent_folder = models.ForeignKey('self', models.CASCADE, related_name="dataroom_folder", null=True, blank=False)
    pages = models.IntegerField(default=0)
    version = models.IntegerField(default=0)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField()
    dataroom_folder_uuid = models.UUIDField(primary_key=False, default=uuid.uuid4, editable=False)
    uploaded_by = models.ForeignKey(User, models.CASCADE, related_name="uploaded_by",  blank=True, null=True)
    selected = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default = False)
    deleted_by = models.ForeignKey(User, models.CASCADE, related_name="deleted_by",  blank=True, null=True)
    deleted_by_date = models.DateTimeField(auto_now_add=True)
    is_view = models.BooleanField(default = False)
    is_print = models.BooleanField(default = False)
    is_download = models.BooleanField(default = False)
    file_size_mb = models.FloatField(blank=True, null=True)
    conversion_path = models.FileField(blank= True, upload_to=store_dataroom_files, null=True, default="" ,max_length=500)
    access_path=models.CharField(max_length=1000, null=True, blank=True)
    uploadedin_batch=models.BooleanField(default = False)
    is_deleted_permanent=models.BooleanField(default = False)
    permanent_deleted_by = models.ForeignKey(User, models.CASCADE, related_name="permanent_deleted_by",  blank=True, null=True) 
    notifymember=models.BooleanField(default = False)
    is_compatable=models.BooleanField(default=True)

    # deleteatdatetime = models.DateTimeField(null=True, blank=True)
    
    def save(self, *args, **kwargs):
        try:
            # size_c = ((instance.file_size)/1024)
            # print(instance.file_size,"<====== value of sized c ==>",instance.file_size/100000)
            self.file_size_mb = round(self.file_size/1024/1024, 3)
            # print("value of instance ===>",instance.file_size_mb)
            # instance.save()     
        except:
            pass
        from notifications.models import AllNotifications
        from users_and_permission.models import DataroomMembers,DataroomGroupFolderSpecificPermissions


        if self.uploadedin_batch==False and self.notifymember==True:
            member = DataroomMembers.objects.filter(dataroom_id = self.dataroom_id, is_deleted=False)
            for mem in member:
                if mem.is_la_user == True or mem.is_dataroom_admin == True:
                    allnot=AllNotifications.objects.filter(dataroom_folder_id=self.id, dataroom_id=self.dataroom_id, user_id=mem.member.id).exists()
                    if allnot==False:

                        AllNotifications.objects.create(dataroom_folder_id=self.id, dataroom_id=self.dataroom_id, user_id=mem.member.id)
                else:
                    if mem.end_user_group.first():
                        if self.is_root_folder==False:
                            if DataroomGroupFolderSpecificPermissions.objects.filter(folder_id=self.parent_folder,dataroom_id=self.dataroom_id, dataroom_groups_id=mem.end_user_group.first().id).exists():
                                perm_obj = DataroomGroupFolderSpecificPermissions.objects.get(folder_id=self.parent_folder,dataroom_id=self.dataroom_id, dataroom_groups_id=mem.end_user_group.first().id)
                                if perm_obj.is_no_access==False: 
                                    allnot=AllNotifications.objects.filter(dataroom_folder_id=self.id, dataroom_id=self.dataroom_id, user_id=mem.member.id).exists()
                                    if allnot==False:                               
                                        AllNotifications.objects.create(dataroom_folder_id=self.id, dataroom_id=self.dataroom_id, user_id=mem.member.id)


        # if self.path: 
            # if (str(self.access_path).find(sas_url) == -1):
                # if self.dataroom.is_usa_blob==True:
                #     sas_url='?sp=racwdli&st=2023-09-12T14:00:21Z&se=2024-08-31T22:00:21Z&spr=https&sv=2022-11-02&sr=c&sig=lrUSru11G6%2F8kp1nq4AW30xMbtdKYWJQ3EkQB4mghZk%3D'
                # else:
                #     sas_url='?sv=2021-10-04&ss=btqf&srt=sco&st=2023-02-25T11%3A51%3A17Z&se=2024-02-25T11%3A51%3A00Z&sp=rl&sig=AWXxw55%2FTC%2BUSOIlVQC3naDahCCebIBNszSFRdqRfBc%3D'   
                # self.access_path=str(self.path.url)+sas_url
                # print(self.access_path)
        # if self.index:
        #   if self.index<=0:
        #       self.index=1

        # if self.conversion_path:
        #   if (str(self.conversion_path.url).find(sas_url) == -1):

        #       self.conversion_path=str(self.conversion_path.url)+sas_url
        #       print(self.conversion_path.url)

        super(DataroomFolder, self).save(*args, **kwargs) 

    def __str__(self):
        return str(self.id)







# method for updating
# @receiver(post_save, sender=DataroomFolder, dispatch_uid="update_file_size_mb")
def update_stock(sender, instance, **kwargs):
    
    if instance.uploadedin_batch==False and instance.notifymember==True:
        member = DataroomMembers.objects.filter(dataroom_id = instance.dataroom_id, is_deleted=False)
        for mem in member:
            if mem.is_la_user == True or mem.is_dataroom_admin == True:
                allnot=AllNotifications.objects.filter(dataroom_folder_id=instance.id, dataroom_id=instance.dataroom_id, user_id=mem.member.id).exists()
                if allnot==False:

                    AllNotifications.objects.create(dataroom_folder_id=instance.id, dataroom_id=instance.dataroom_id, user_id=mem.member.id)
            else:
                if mem.end_user_group.first():
                    if instance.is_root_folder==False:
                        if DataroomGroupFolderSpecificPermissions.objects.filter(folder_id=instance.parent_folder,dataroom_id=instance.dataroom_id, dataroom_groups_id=mem.end_user_group.first().id).exists():
                            perm_obj = DataroomGroupFolderSpecificPermissions.objects.get(folder_id=instance.parent_folder,dataroom_id=instance.dataroom_id, dataroom_groups_id=mem.end_user_group.first().id)
                            if perm_obj.is_no_access==False: 
                                allnot=AllNotifications.objects.filter(dataroom_folder_id=instance.id, dataroom_id=instance.dataroom_id, user_id=mem.member.id).exists()
                                if allnot==False:                               
                                    AllNotifications.objects.create(dataroom_folder_id=instance.id, dataroom_id=instance.dataroom_id, user_id=mem.member.id)

    # try:
    #     # size_c = ((instance.file_size)/1024)
    #     # print(instance.file_size,"<====== value of sized c ==>",instance.file_size/100000)
    #     instance.file_size_mb = round(instance.file_size/1024/1024, 3)
    #     # print("value of instance ===>",instance.file_size_mb)
    #     instance.save()     
    # except:
    #     pass

    # member = DataroomMembers.objects.filter(dataroom_id=instance.dataroom_id,is_deleted=False,is_deleted_end=False,is_end_user=True,is_deleted_la=False)
    # print(member,'IIIIIIIIIIIIIII')
    # if instance.is_folder:
    #   for i in member:
    #       if i.end_user_group.exists():

    #           DataroomGroupFolderSpecificPermissions.objects.create(folder_id=instance.id,dataroom_id=instance.dataroom_id,dataroom_groups_id=i.end_user_group.first().id)
    # else:
    #   for i in member:
    #       print(i,'RRRRRRRRRRRRRRRRRR')
    #       if i.end_user_group.exists():

    #           dataa=DataroomGroupFolderSpecificPermissions.objects.filter(folder_id=instance.parent_folder.id,dataroom_id=instance.dataroom_id,dataroom_groups_id=i.end_user_group.first().id).last() 
    #           if dataa is not None:   
    #               print(dataa,'wwwwwwwwwwwwwww')
    #               DataroomGroupFolderSpecificPermissions.objects.create(folder_id=instance.id,dataroom_id=instance.dataroom_id,dataroom_groups_id=i.end_user_group.first().id,is_no_access=dataa.is_no_access,is_access=dataa.is_access,is_view_only=dataa.is_view_only,is_view_and_print=dataa.is_view_and_print,is_view_and_print_and_download=dataa.is_view_and_print_and_download,is_upload=dataa.is_upload,is_watermarking=dataa.is_watermarking,is_drm=dataa.is_drm,is_editor=dataa.is_editor,is_shortcut=dataa.is_shortcut)
    #           else:
    #               print(dataa,'uuuuuuuuuuuuuuu')
    #               DataroomGroupFolderSpecificPermissions.objects.create(folder_id=instance.id,dataroom_id=instance.dataroom_id,dataroom_groups_id=i.end_user_group.first().id)








class FolderTrash(models.Model):
    folder=models.ForeignKey(DataroomFolder,models.CASCADE, null=True, )
    parent_folder_trash=models.ForeignKey('self', models.CASCADE, related_name="folder_trash_parent", null=True, blank=False)
    dataroom = models.ForeignKey(Dataroom, models.CASCADE, null=True)
    is_single=models.BooleanField(default=False,null=True,blank=True)
    is_folder=models.BooleanField(default=False,null=True,blank=True)
    is_file=models.BooleanField(default=False,null=True,blank=True)
    is_show=models.BooleanField(default=False,null=True,blank=True)
    unique_id=models.IntegerField(default=0,null=True,blank=True)
    is_deleted_by=models.ForeignKey(User, models.CASCADE, null=True)
    created_date=models.DateTimeField(auto_now_add=True)
    is_restored=models.BooleanField(default=False,null=True,blank=True)
    is_deleted_permanent=models.BooleanField(default=False,null=True,blank=True)














class Bulkuploadstatus(models.Model):
    dataroom = models.ForeignKey(Dataroom, models.CASCADE, null=True)
    user = models.ForeignKey(User, models.CASCADE, null=True)
    isuploadfail= models.BooleanField(default=True)
    totalnumberoffiles = models.IntegerField(default=0)
    totaluploadedfiles = models.IntegerField(default=0)
    totalfailedfiles = models.IntegerField(default=0)
    totalnumberoffolders = models.IntegerField(default=0)
    totaluploadedfolders = models.IntegerField(default=0)
    totalfailedfolders = models.IntegerField(default=0)
    parentfolder = models.ForeignKey(DataroomFolder,models.CASCADE, null=True,blank=True)
    is_root_folder=models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)
    event = models.CharField(max_length = 50, default = 'batch upload')
    notifymember=models.BooleanField(default=False)
    processcomplete=models.BooleanField(default=False)
    is_cancelled=models.BooleanField(default=False)


class Folderuploadinbulk(models.Model):
    folder = models.ForeignKey(DataroomFolder,models.CASCADE, null=True, )
    user = models.ForeignKey(User, models.CASCADE, null=True)
    dataroom = models.ForeignKey(Dataroom, models.CASCADE, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    is_folder=models.BooleanField(default=False)
    file_name = models.CharField(max_length=255,null=True)
    event = models.CharField(default="file/folder in batch upload", max_length=50)
    bulkupload=models.ForeignKey(Bulkuploadstatus, models.CASCADE, null=True, blank=True)


class Folderfailinbulk(models.Model):
    user = models.ForeignKey(User, models.CASCADE, null=True)
    dataroom = models.ForeignKey(Dataroom, models.CASCADE, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    file_name = models.CharField(max_length=255,null=True)
    file_pathh = models.CharField(max_length=255,null=True)
    is_folder=models.BooleanField(default=False)
    event = models.CharField(default="file/folder fail in batch upload", max_length=50)
    bulkupload=models.ForeignKey(Bulkuploadstatus, models.CASCADE, null=True, blank=True)

class DataroomViewerImage(models.Model):
    status = models.CharField(max_length=1000, blank=True)
    page_number = models.IntegerField()
    expiring_url = models.CharField(max_length=1000, blank=True)
    expiring_thumbnail_url = models.CharField(max_length=1000, blank=True)


class IndexDownload(models.Model):
    user = models.ForeignKey(User, models.CASCADE, null=True, related_name="index_user")
    dataroom = models.ForeignKey(Dataroom, models.CASCADE, null=True, related_name="index_user")
    created_date = models.DateTimeField(auto_now_add=True)

class FolderView(models.Model):
    folder = models.ForeignKey(DataroomFolder,models.CASCADE, null=True, )
    user = models.ForeignKey(User, models.CASCADE, null=True, related_name="view_user")
    dataroom = models.ForeignKey(Dataroom, models.CASCADE, null=True, related_name="view_dataroom")
    created_date = models.DateTimeField(auto_now_add=True)
    event = models.CharField(default="file view", max_length=50)

class BulkActivityTracker(models.Model):
    user = models.ForeignKey(User, models.CASCADE, null=True, related_name="bulk_activity_tracker")
    event = models.CharField(default="bulk_event_tracker", max_length=50)
    created_date = models.DateTimeField(auto_now_add=True)
    dataroom = models.ForeignKey(Dataroom, models.CASCADE, null=True, related_name="bulk_dataroom")

class FolderDownload(models.Model):
    folder = models.ForeignKey(DataroomFolder,models.CASCADE, null=True, )
    user = models.ForeignKey(User, models.CASCADE, null=True, related_name="download_user")
    dataroom = models.ForeignKey(Dataroom, models.CASCADE, null=True, related_name="download_dataroom")
    created_date = models.DateTimeField(auto_now_add=True)
    event = models.CharField(default="file download", max_length=50)
    bulk_event = models.ForeignKey(BulkActivityTracker, models.CASCADE, null=True)

class Folderupload(models.Model):
    folder = models.ForeignKey(DataroomFolder,models.CASCADE, null=True, )
    user = models.ForeignKey(User, models.CASCADE, null=True, related_name="folderupload_user")
    dataroom = models.ForeignKey(Dataroom, models.CASCADE, null=True, related_name="folderupload_dataroom")
    created_date = models.DateTimeField(auto_now_add=True)
    file_name = models.CharField(max_length=255,null=True)
    event = models.CharField(default="uploaded", max_length=50)

class FolderPrint(models.Model):
    folder = models.ForeignKey(DataroomFolder,models.CASCADE, null=True, )
    user = models.ForeignKey(User, models.CASCADE, null=True, related_name="print_user")
    dataroom = models.ForeignKey(Dataroom, models.CASCADE, null=True, related_name="print_dataroom")
    created_date = models.DateTimeField(auto_now_add=True)
    event = models.CharField(default="file print", max_length=50)
    bulk_event = models.ForeignKey(BulkActivityTracker, models.CASCADE, null=True)

class FolderDrmDownload(models.Model):
    folder = models.ForeignKey(DataroomFolder,models.CASCADE, null=True, )
    user = models.ForeignKey(User, models.CASCADE, null=True, related_name="download_drm")
    dataroom = models.ForeignKey(Dataroom, models.CASCADE, null=True, related_name="download_drm")
    created_date = models.DateTimeField(auto_now_add=True)
    event = models.CharField(default="drm download", max_length=50)
    bulk_event = models.ForeignKey(BulkActivityTracker, models.CASCADE, null=True)

class FolderDeleteDownload(models.Model):
    folder = models.ForeignKey(DataroomFolder,models.CASCADE, null=True, )
    user = models.ForeignKey(User, models.CASCADE, null=True, related_name="delete_file")
    dataroom = models.ForeignKey(Dataroom, models.CASCADE, null=True, related_name="delete_file_dataroom")
    created_date = models.DateTimeField(auto_now_add=True)
    event = models.CharField(default="delete", max_length=50)
    bulk_event = models.ForeignKey(BulkActivityTracker, models.CASCADE, null=True)





class FolderOrFileCopy(models.Model):
    COPY_CHOICES = ( 
    ("Copy Folder", "Copy Folder"), 
    ("Copy File", "Copy File"),
    ("None", "None"),)
    folder = models.ForeignKey(DataroomFolder,models.CASCADE, null=True, )
    user = models.ForeignKey(User, models.CASCADE, null=True, related_name="copy_file")
    dataroom = models.ForeignKey(Dataroom, models.CASCADE, null=True, related_name="copy_file_dataroom")
    created_date = models.DateTimeField(auto_now_add=True)
    event = models.CharField(max_length = 50, choices = COPY_CHOICES, default = 'None')
    bulk_event = models.ForeignKey(BulkActivityTracker, models.CASCADE, null=True)


class FolderOrFileMove(models.Model):
    MOVE_CHOICES = ( 
    ("Move Folder", "Move Folder"), 
    ("Move File", "Move File"),
    ("None", "None"),)
    folder = models.ForeignKey(DataroomFolder,models.CASCADE, null=True, )
    user = models.ForeignKey(User, models.CASCADE, null=True, related_name="move_file")
    dataroom = models.ForeignKey(Dataroom, models.CASCADE, null=True, related_name="move_file_dataroom")
    created_date = models.DateTimeField(auto_now_add=True)
    event = models.CharField(max_length = 50, choices = MOVE_CHOICES, default = 'None')
    bulk_event = models.ForeignKey(BulkActivityTracker, models.CASCADE, null=True)


class RestoreFiles(models.Model):
    RESTORE_CHOICES = ( 
    ("Restore Folder", "Restore Folder"), 
    ("Restore File", "Restore File"),
    ("None", "None"),)
    folder = models.ForeignKey(DataroomFolder,models.CASCADE, null=True, )
    user = models.ForeignKey(User, models.CASCADE, null=True, related_name="restore_file")
    dataroom = models.ForeignKey(Dataroom, models.CASCADE, null=True, related_name="restore_file_dataroom")
    created_date = models.DateTimeField(auto_now_add=True)
    event = models.CharField(max_length = 50, choices = RESTORE_CHOICES, default = 'None')
    bulk_event = models.ForeignKey(BulkActivityTracker, models.CASCADE, null=True)

class BulkDownloadstatus(models.Model):
    user=models.ForeignKey(User, models.CASCADE, null=True, blank=True)
    dataroom = models.ForeignKey(Dataroom, models.CASCADE, null=True, blank=True)
    filecount = models.IntegerField(default=0)
    successfilescount = models.IntegerField(default=0)
    failfilecount = models.IntegerField(default=0)
    downloaded = models.BooleanField(default=False)
    readytodownload=models.BooleanField(default=False)
    filename = models.CharField(max_length = 500, null=True,blank=True)
    downloadedcount = models.IntegerField(default=0)
    is_overview_report = models.BooleanField(default=False) 
    is_index_report = models.BooleanField(default=False)
    is_index_report_2 = models.BooleanField(default=False)
    is_activity_by_files_report = models.BooleanField(default=False)
    is_user_and_grp_report = models.BooleanField(default=False)
    is_activity_by_date_report = models.BooleanField(default=False)
    is_q_and_a_report = models.BooleanField(default=False)
    is_download_report = models.BooleanField(default=False)
    is_user_and_status_report = models.BooleanField(default=False)
    is_voting_report = models.BooleanField(default=False)
    is_deleted=models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)
    is_single_file= models.BooleanField(default=False)
    is_file_irm=models.BooleanField(default=False)


class BulkDownloadfailFiles(models.Model):
    folder = models.ForeignKey(DataroomFolder,models.CASCADE, null=True)
    user = models.ForeignKey(User, models.CASCADE, null=True, related_name="bulk_failfile")
    dataroom = models.ForeignKey(Dataroom, models.CASCADE, null=True, related_name="bulk_filefail_dataroom")
    created_date = models.DateTimeField(auto_now_add=True)
    #Rushikesh0033
    batch=models.ForeignKey(BulkDownloadstatus, models.CASCADE, null=True, blank=True)
    event = models.CharField(max_length = 50, default = 'bulk_download_fail')
    bulk_event = models.ForeignKey(BulkActivityTracker, models.CASCADE, null=True)  

class BulkDownloadFiles(models.Model):
    folder = models.ForeignKey(DataroomFolder,models.CASCADE, null=True, )
    user = models.ForeignKey(User, models.CASCADE, null=True, related_name="bulk_file")
    dataroom = models.ForeignKey(Dataroom, models.CASCADE, null=True, related_name="bulk_file_dataroom")
    created_date = models.DateTimeField(auto_now_add=True)
    batch=models.ForeignKey(BulkDownloadstatus, models.CASCADE, null=True, blank=True)
    event = models.CharField(max_length = 50, default = 'bulk_download')
    bulk_event = models.ForeignKey(BulkActivityTracker, models.CASCADE, null=True)


    

class Categories(models.Model):
    """docstring for Categories"""
    categories_name = models.CharField(max_length=50, blank=True, null=True)    
    dataroom = models.ForeignKey(Dataroom, models.CASCADE, blank=True, null=True)
    

def store_dataroom_files1(instance, filename): 
    # print ("store dataroom files")
    u_id = instance.user.id
    dataroom_uuid = instance.dataroom.dataroom_uuid
    dataroom_name = instance.dataroom.dataroom_name
    parent_folder_id = instance.parent_folder.id
    # print ("file name is:", filename)
    if instance.is_folder:
        # print ("if instance is folder")
        if instance.is_root_folder:
            # print ("if instance is root folder")
            return '{0}_{1}'.format(dataroom_name, dataroom_uuid)
        else:
            # print ("if instance is not root folder")
            return '{0}_{1}'.format(dataroom_name, dataroom_uuid)
    else:
        # print ("if instance is not folder")
        # print ("file path is", '{0}_{1}/{2}'.format(dataroom_name, dataroom_uuid, filename))
        return '{0}_{1}/{2}'.format(dataroom_name, dataroom_uuid, filename)


class ManageDataroomCategories(models.Model):
    user = models.ForeignKey(User, models.CASCADE,)
    dataroom = models.ForeignKey(Dataroom, models.CASCADE,)
    category = models.ForeignKey(Categories, models.CASCADE, related_name="category_details")
    # category = models.ManyToManyField(Categories, models.CASCADE,)

class documentpagecount(models.Model):
    dataroom = models.ForeignKey(DataroomFolder,models.CASCADE, null=True)
    document_count = models.CharField(max_length=50)
    pages_count = models.CharField(max_length=50)
    created_date = models.DateTimeField(auto_now_add=True)

from dataroom.models import DataroomView
# from Vote.models import Voteactivity

class dataroomactivitymerge(models.Model):
    user = models.ForeignKey(User, models.CASCADE)
    dataroom = models.ForeignKey(Dataroom,models.CASCADE)
    FolderView= models.ForeignKey(FolderView,models.CASCADE,null=True,blank=True)
    FolderPrint= models.ForeignKey(FolderPrint,models.CASCADE,null=True,blank=True)
    FolderDownload= models.ForeignKey(FolderDownload,models.CASCADE,null=True,blank=True)
    FolderDrmDownload= models.ForeignKey(FolderDrmDownload,models.CASCADE,null=True,blank=True)
    FolderDeleteDownload= models.ForeignKey(FolderDeleteDownload,models.CASCADE,null=True,blank=True)
    FolderOrFileCopy= models.ForeignKey(FolderOrFileCopy,models.CASCADE,null=True,blank=True)
    FolderOrFileMove= models.ForeignKey(FolderOrFileMove,models.CASCADE,null=True,blank=True)
    BulkDownloadstatus= models.ForeignKey(BulkDownloadstatus,models.CASCADE,null=True,blank=True)
    Folderupload= models.ForeignKey(Folderupload,models.CASCADE,null=True,blank=True)
    Bulkuploadstatus= models.ForeignKey(Bulkuploadstatus,models.CASCADE,null=True,blank=True)
    RestoreFiles= models.ForeignKey(RestoreFiles,models.CASCADE,null=True,blank=True)
    DataroomView= models.ForeignKey(DataroomView,models.CASCADE,null=True,blank=True)
    # Folderversionupdate= models.ForeignKey(Folderversionupdate,models.CASCADE,null=True,blank=True)
    BulkActivityTracker= models.ForeignKey(BulkActivityTracker,models.CASCADE,null=True,blank=True)
    DataroomMembersid= models.CharField(max_length=500,null=True,blank=True)
    Voteactivityid=models.CharField(max_length=500,null=True,blank=True)
    Updateactivityid=models.CharField(max_length=500,null=True,blank=True)
    qnaactivityid=models.CharField(max_length=500,null=True,blank=True)
    groupactivityid=models.CharField(max_length=500,null=True,blank=True)
    created_date = models.DateTimeField(auto_now_add=True)



@receiver(post_save, sender=FolderView, dispatch_uid="FolderView_activity")
def FolderViewactivity(sender, instance, **kwargs):
        dataroomactivitymerge.objects.create(user_id=instance.user.id,dataroom_id=instance.dataroom.id,FolderView_id=instance.id)

# @receiver(post_save, sender=Folderversionupdate, dispatch_uid="Folderversionupdate_activity")
# def Folderversionupdateactivity(sender, instance, **kwargs):
#         dataroomactivitymerge.objects.create(user_id=instance.user.id,dataroom_id=instance.dataroom.id,Folderversionupdate_id=instance.id)

@receiver(post_save, sender=FolderPrint, dispatch_uid="FolderPrint_activity")
def FolderPrintactivity(sender, instance, **kwargs):
        dataroomactivitymerge.objects.create(user_id=instance.user.id,dataroom_id=instance.dataroom.id,FolderPrint_id=instance.id)

@receiver(post_save, sender=FolderDownload, dispatch_uid="FolderDownload_activity")
def FolderDownloadactivity(sender, instance, **kwargs):
        if instance.bulk_event:
            dataroomactivitymerge.objects.create(user_id=instance.user.id,dataroom_id=instance.dataroom.id,FolderDownload_id=instance.id, BulkActivityTracker_id=instance.bulk_event.id)
        else:
            dataroomactivitymerge.objects.create(user_id=instance.user.id,dataroom_id=instance.dataroom.id,FolderDownload_id=instance.id)

@receiver(post_save, sender=FolderDrmDownload, dispatch_uid="FolderDrmDownload_activity")
def FolderDrmDownloadactivity(sender, instance, **kwargs):
        if instance.bulk_event:
            dataroomactivitymerge.objects.create(user_id=instance.user.id,dataroom_id=instance.dataroom.id,FolderDrmDownload_id=instance.id, BulkActivityTracker_id=instance.bulk_event.id)
        else:
            dataroomactivitymerge.objects.create(user_id=instance.user.id,dataroom_id=instance.dataroom.id,FolderDrmDownload_id=instance.id)

@receiver(post_save, sender=FolderDeleteDownload, dispatch_uid="FolderDeleteDownload_activity")
def FolderDeleteDownloadactivity(sender, instance, **kwargs):
        if instance.bulk_event:
            dataroomactivitymerge.objects.create(user_id=instance.user.id,dataroom_id=instance.dataroom.id,FolderDeleteDownload_id=instance.id, BulkActivityTracker_id=instance.bulk_event.id)
        else:
            dataroomactivitymerge.objects.create(user_id=instance.user.id,dataroom_id=instance.dataroom.id,FolderDeleteDownload_id=instance.id)

@receiver(post_save, sender=FolderOrFileCopy, dispatch_uid="FolderOrFileCopy_activity")
def FolderOrFileCopyactivity(sender, instance, **kwargs):
        if instance.bulk_event:
            dataroomactivitymerge.objects.create(user_id=instance.user.id,dataroom_id=instance.dataroom.id,FolderOrFileCopy_id=instance.id, BulkActivityTracker_id=instance.bulk_event.id)
        else:
            dataroomactivitymerge.objects.create(user_id=instance.user.id,dataroom_id=instance.dataroom.id,FolderOrFileCopy_id=instance.id)

@receiver(post_save, sender=FolderOrFileMove, dispatch_uid="FolderOrFileMove_activity")
def FolderOrFileMoveactivity(sender, instance, **kwargs):
        if instance.bulk_event:
            dataroomactivitymerge.objects.create(user_id=instance.user.id,dataroom_id=instance.dataroom.id,FolderOrFileMove_id=instance.id, BulkActivityTracker_id=instance.bulk_event.id)
        else:
            dataroomactivitymerge.objects.create(user_id=instance.user.id,dataroom_id=instance.dataroom.id,FolderOrFileMove_id=instance.id)

@receiver(post_save, sender=BulkDownloadstatus, dispatch_uid="BulkDownloadstatus_activity")
def BulkDownloadstatusactivity(sender, instance, **kwargs):
        dataroomactivitymerge.objects.create(user_id=instance.user.id,dataroom_id=instance.dataroom.id,BulkDownloadstatus_id=instance.id)

@receiver(post_save, sender=Folderupload, dispatch_uid="Folderupload_activity")
def Folderuploadactivity(sender, instance, **kwargs):
        dataroomactivitymerge.objects.create(user_id=instance.user.id,dataroom_id=instance.dataroom.id,Folderupload_id=instance.id)

@receiver(post_save, sender=RestoreFiles, dispatch_uid="RestoreFiles_activity")
def RestoreFilesactivity(sender, instance, **kwargs):
        if instance.bulk_event:
            dataroomactivitymerge.objects.create(user_id=instance.user.id,dataroom_id=instance.dataroom.id,RestoreFiles_id=instance.id, BulkActivityTracker_id=instance.bulk_event.id)
        else:
            dataroomactivitymerge.objects.create(user_id=instance.user.id,dataroom_id=instance.dataroom.id,RestoreFiles_id=instance.id)

@receiver(post_save, sender=DataroomView, dispatch_uid="DataroomView_activity")
def DataroomViewactivity(sender, instance, **kwargs):
    dataroomactivitymerge.objects.create(user_id=instance.user.id,dataroom_id=instance.dataroom.id,DataroomView_id=instance.id)



class Favourite(models.Model):
    folder=models.ForeignKey(DataroomFolder, models.CASCADE)
    user=models.ForeignKey(User, models.CASCADE)
    dataroom=models.ForeignKey(Dataroom, models.CASCADE,null=True,blank=True)
    created_date=models.DateTimeField(auto_now_add=True,blank=True,null=True)


class Redacted_Pdf(models.Model):
    folder=models.ForeignKey(DataroomFolder, models.CASCADE)
    name=models.CharField(max_length=10000,null=True,blank=True)
    user=models.ForeignKey(User, models.CASCADE)
    dataroom=models.ForeignKey(Dataroom, models.CASCADE,null=True,blank=True)
    file=models.CharField(max_length=100000,null=True,blank=True)
    notes=models.TextField(blank=True, null=True)
    created_date=models.DateTimeField(auto_now_add=True,blank=True,null=True)
    updated_date=models.DateTimeField(auto_now_add=True,blank=True,null=True)
    current_version=models.BooleanField(default=False)
    version=models.CharField(max_length=100,null=True,blank=True)
    file_size = models.FloatField(blank=True, null=True)
    file_size_mb = models.FloatField(blank=True, null=True)
    is_deleted = models.BooleanField(default = False)
    deleted_by = models.ForeignKey(User, models.CASCADE, related_name="deleted_by_redect",  blank=True, null=True)
    deleted_by_date = models.DateTimeField(auto_now_add=True,blank=True, null=True)
    is_deleted_permanent=models.BooleanField(default = False)
    permanent_deleted_by = models.ForeignKey(User, models.CASCADE, related_name="permanent_deleted_by_redect",  blank=True, null=True) 

    def save(self, *args, **kwargs):
        try:
            # size_c = ((instance.file_size)/1024)
            # print(instance.file_size,"<====== value of sized c ==>",instance.file_size/100000)
            self.file_size_mb = round(self.file_size/1024/1024, 3)
            # print("value of instance ===>",instance.file_size_mb)
            # instance.save()     
        except:
            pass
        super(Redacted_Pdf, self).save(*args, **kwargs) 

    def __str__(self):
        return str(self.id)



# class FolderTrash(models.Model):
#     folder=models.ForeignKey(DataroomFolder,models.CASCADE, null=True, )
#     parent_folder_trash=models.ForeignKey('self', models.CASCADE, related_name="folder_trash_parent", null=True, blank=False)
#     dataroom = models.ForeignKey(Dataroom, models.CASCADE, null=True)
#     is_single=models.BooleanField(default=False,null=True,blank=True)
#     is_folder=models.BooleanField(default=False,null=True,blank=True)
#     is_file=models.BooleanField(default=False,null=True,blank=True)
#     is_show=models.BooleanField(default=False,null=True,blank=True)
#     unique_id=models.IntegerField(default=0,null=True,blank=True)
#     is_deleted_by=models.ForeignKey(User, models.CASCADE, null=True)
#     created_date=models.DateTimeField(auto_now_add=True)
#     is_restored=models.BooleanField(default=False,null=True,blank=True)
#     is_deleted_permanent=models.BooleanField(default=False,null=True,blank=True)



class RedactorVersion(models.Model):
    folder = models.ForeignKey(DataroomFolder,models.CASCADE, null=True, )
    redact = models.ForeignKey(Redacted_Pdf,models.CASCADE, null=True, )
    user = models.ForeignKey(User, models.CASCADE, null=True, related_name="redacted_u")
    dataroom = models.ForeignKey(Dataroom, models.CASCADE, null=True, related_name="redacted_d")
    created_date = models.DateTimeField(auto_now_add=True)
    event = models.CharField(default="redacted", max_length=50)
    event1 = models.CharField(default="redact", max_length=50)
    bulk_event = models.ForeignKey(BulkActivityTracker, models.CASCADE, null=True)
    # batch=models.ForeignKey(BulkDownloadstatus, models.CASCADE, null=True, blank=True)



    


class azure_token_model(models.Model):
    access_token=models.CharField(max_length=10000,blank=True,null=True)
    refresh_token=models.CharField(max_length=10000,blank=True,null=True)
    access_token_date=models.DateTimeField(null=True,blank=True)
    refresh_token_date=models.DateTimeField(null=True,blank=True)
    is_email=models.BooleanField(default=False)
    is_drm=models.BooleanField(default=False)