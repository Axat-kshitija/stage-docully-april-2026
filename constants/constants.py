dataroom_stages = ['Hold','Live']

site_settings = {
	'domain_name':'Confiex Dataroom', 
	'support_email_id':'support@docullyvdr.com', 
	'help_email_id': 'support@docullyvdr.com', 
	'phone_no':'9699131189', 
	'domain_url':'https://docully.com/'
	}	

emailer_types = ['dataroom_deletion_email', 'dataroom_archive_email', 
				'account_verification_email', 'password_successfully_changed', 
				'forgot_password_email', 'welcome_email', 'dataroom_invitation_email'
				]

invitation_status = ['Pending', 'Expired', 'Verified']

dataroom_disclaimer_status = ['Processed', 'Processing']

end_user_types = ['dataroom_admin','member', 'dataroom_la_admin']

extensions = {".au":"audio/basic",
        ".avi":"video/msvideo ,video/avi, video/x-msvideo",
        ".bmp":"image/bmp",
        ".bz2":"application/x-bzip2",
        ".css":"text/css",
        ".dtd":"application/xml-dtd",
        ".doc":"application/msword",
        ".docx":"application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ".dotx":"application/vnd.openxmlformats-officedocument.wordprocessingml.template",
        ".es":"application/ecmascript",
        ".exe":"application/octet-stream",
        ".gif":"image/gif",
        ".gz":"application/x-gzip",
        ".hqx":"application/mac-binhex40",
        ".html":"text/html",
        ".jar":"application/java-archive",
        ".jpg":"image/jpeg",
        ".jpeg":"image/jpg",
        ".js":"application/x-javascript",
        ".midi":"audio/x-midi",
        ".mp3":"audio/mpeg",
        ".mpeg":"video/mpeg",
        ".ogg":"audio/vorbis, application/ogg",
        ".pdf":"application/pdf",
        ".PDF":"application/pdf",
        ".pl":"application/x-perl",
        ".png":"image/png",
        ".potx":"application/vnd.openxmlformats-officedocument.presentationml.template",
        ".ppsx":"application/vnd.openxmlformats-officedocument.presentationml.slideshow",
        ".ppt":"application/vnd.ms-powerpointtd",
        ".pptx":"application/vnd.openxmlformats-officedocument.presentationml.presentation",
        ".ps":"application/postscript",
        ".qt":"video/quicktime",
        ".ra":"audio/x-pn-realaudio, audio/vnd.rn-realaudio",
        ".ram":"audio/x-pn-realaudio, audio/vnd.rn-realaudio",
        ".rdf":"application/rdf, application/rdf+xml",
        ".rtf":"application/rtf",
        ".sgml":"text/sgml",
        ".sit":"application/x-stuffit",
        ".sldx":"application/vnd.openxmlformats-officedocument.presentationml.slide",
        ".svg":"image/svg+xml",
        ".swf":"application/x-shockwave-flash",
        ".tar.gz":"application/x-tar",
        ".tgz":"application/x-tar",
        ".tiff":"image/tiff",
        ".tsv":"text/tab-separated-values",
        ".txt":"text/plain",
        ".wav":"audio/wav, audio/x-wav",
        ".xlam":"application/vnd.ms-excel.addin.macroEnabled.12",
        ".xls":"application/vnd.ms-excel",
        ".xlsb":"application/vnd.ms-excel.sheet.binary.macroEnabled.12",
        ".xlsx":"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ".xltx":"application/vnd.openxmlformats-officedocument.spreadsheetml.template",
        ".xml":"application/xml",
        ".zip":"application/zip, application/x-compressed-zip",
        ".odt":"application/vnd.oasis.opendocument.text",
        ".ods":"application/vnd.oasis.opendocument.spreadsheet",
        ".ots":"application/vnd.oasis.opendocument.spreadsheet-template",
        ".csv":".csv"
        }

# backend_ip = "localhost:8000"
backend_ip = "http://20.193.245.169:8080"

backend_ip2 = "https://stage.docullyvdr.com/projectName"
# backend_ip = "https://services.docully.com/"
frontend_ip = "https://services.docullyvdr.com/"
