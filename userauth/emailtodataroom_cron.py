import requests
import json
from django.db.models import F







def email_to_dataroom():

  


  # Define the endpoint URL
  url = "https://oauth2.googleapis.com/token"

  # Define the payload as a dictionary
  payload = {
      
      'client_id': '872398678576-b9fggq45hdjvpc8vpk8hqoj39rap5lfe.apps.googleusercontent.com',
      'client_secret': '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',
      'refresh_token': '1//0gyvG3CaSUGECCgYIARAAGBASNwF-L9IrczKgcWbe4sPzJcZ8AI9qtniRGDLXoDbqOKXmo3BmlIKD-Wny86z4fLj1TeZW7GUH8zM',
      'grant_type': 'refresh_token'
  }

  # Define the headers
  headers = {
      'Content-Type': 'application/x-www-form-urlencoded'
  }

  # Make the POST request
  response = requests.post(url, headers=headers, data=payload)

  # Print the response
  print(response.text)
  resp=response.json()
  access_token=resp['access_token']

  print('----------accesss',access_token)







  url1 = "https://www.googleapis.com/gmail/v1/users/emailtodataroom@docullyinnovations.com/watch"

  payload1 = json.dumps({
    "topicName": "projects/docullyvdr-419813/topics/new_mail",
    "labelIds": [
      "INBOX"
    ],
    "labelFilterBehavior": "INCLUDE"
  })
  headers1 = {
    'Authorization': F'Bearer {access_token}',
    'Content-Type': 'application/json'
  }

  response = requests.request("POST", url1, headers=headers1, data=payload1)

  print(response.text)

