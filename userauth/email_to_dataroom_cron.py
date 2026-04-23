from data_documents.models import azure_token_model
import requests
import json

def renew_subscription():

    from datetime import datetime,timedelta,date

    url1 = "https://login.microsoftonline.com/182443d6-de18-49a9-8bb9-68979df5d44d/oauth2/v2.0/token"
    token=azure_token_model.objects.last()
    payload1 = 'client_id=3f9c984c-da21-467a-a806-7d695961f387&grant_type=refresh_token&scope=%20offline_access%20Mail.ReadWrite&client_secret=0Oc8Q~btIC57lTaytKIOq9CALnR0zDO7aQ1mVcSo&refresh_token='+token.refresh_token
    headers1 = {
      'Content-Type': 'application/x-www-form-urlencoded',
        'Cookie': 'fpc=AvPoNvK1eFtEqjoJKyLNrjCTXgNEAQAAAFZUrt8OAAAA'
        }

    response1 = requests.request("GET", url1, headers=headers1, data=payload1)

    print(response1.text)
    # Print the response
    
    resp1=response1.json()
    access_token=resp1['access_token']
    refresh_token=resp1['refresh_token']
    azure_token_model.objects.create(access_token=access_token,refresh_token=refresh_token,access_token_date=datetime.now(),refresh_token_date=datetime.now())




    url = "https://graph.microsoft.com/v1.0/subscriptions"
    future_date=date.today()+timedelta(days=2)
    print('-----future date',future_date)
    payload = json.dumps({
      "changeType": "created",
      "notificationUrl": "https://stage.docullyvdr.com/projectName/outlook_email_read/",
      "resource": "/me/messages",
      "expirationDateTime": str(future_date)
    })
    headers = {
      'Authorization': 'Bearer '+access_token ,
      'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)



