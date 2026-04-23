



import json
import os

import openai
from dotenv import load_dotenv

load_dotenv()

# openai.api_key = os.getenv("OPENAI_API_KEY")
openai.api_key = "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"


def parse_unstructured_text(input):
    pp='hello there  i want a car for rent from 20 nov to 30 nov at 12.30 pm '
    prompt = f"""
            mail_body :{pp}
            check the above mail_body content and let me know that the content is to book a taxi or
             any vehicle for any ride or
            any vehicle for rent .

            
            
            
            give response in yes or no:
              """
    # queries = prompt.split()
    # for query in queries:
    #   print('-----------------------',query)
    # Python3 code to demonstrate working of
    # Add Phrase in middle of String
    # Using split() + slicing + join()

    # initializing string
    # test_str = 'geekforgeeks is for geeks'

    # # printing original string
    # print("The original string is : " + str(test_str))

    # # initializing mid string
    # mid_str = "JSON: is best"

    # # splitting string to list
    # temp = prompt.split('JSON:')
    # print('-------temp',temp[0])
    # print('-------temp',temp[1])
    # print('-------temp',temp[-1])

    # mid_pos = len(temp) // 2
    # print('-------mid_pos',mid_pos)
    # appending in mid
    # res = [str(temp[0])] + [mid_str] + [str(temp[1])]
    # print('-------res',res)
    # # conversion back
    # res = ' '.join(res)
    # print('-------res2',res)
    # # printing result
    # print("Formulated String : " + str(res))
 

    response = openai.Completion.create(
                model="text-davinci-003", 
                prompt=prompt, 
                temperature=0, 
                max_tokens=3000,
                        top_p=1, 
                frequency_penalty=0, 
                presence_penalty=0
            )
    print('------------------response',response)
    # try:
    #     j = json.loads(response["choices"][0]["text"])
    # except json.decoder.JSONDecodeError:
    #     j = None
    print('-----------------respionse 1',response["choices"][0]["text"])  
#     out = {"prompt": prompt, "output": response["choices"][0]["text"], "json": j, "response": response}

#     return out


def main():
    input = """ Client ID: 123456, Daniel Lawson | Data Analytics Consultant, The Data School Australia |
            Lvl 12 500 Collins Street Melbourne Victoria 3000 // mob. 0455123456 / 
            e. daniel.lee.lawson@example.com insta: @_danlsn, twitter: @_danlsn, github: @danlsn, 
            w. danlsn.com.au | bus. 9555 5555 | B.Arch (Design), M.Marketing (Distinction)"""

    out = parse_unstructured_text(input)
    # print(out["output"])


if __name__ == "__main__":
    main()





#2222222222222222222222222222222222222222222=====================================


# def GetMessageMemory(NewQuestion,lastmessage):

#   # Append the new question to the last message
#   lastmessage.append({"role": "user", "content": NewQuestion})
#     # Make a call to ChatGPT API
#   msgcompletion = openai.ChatCompletion.create(
#     model="gpt-3.5-turbo",
#     messages=lastmessage
#   )
#   # Get the response from ChatGPT API
#   msgresponse = msgcompletion.choices[0].message.content
#   # You can print it if you like.
#   #print(msgresponse)

#   # Print the question
#   print("Question : " + NewQuestion)
#   # We return the new answer back to the calling function
#   return msgresponse



# content='Client ID: 123456, Dantel Lawson | Data Analytics Consultant, The Data School Australia | Lvl 12 500 Collins Street Melbourne Victoria 3000 // 0455123456 / e. dantel.lee. Lawson@example.com ig. danlsn, tw. @_danlsn, gh. @danlsn, w. danlsn.com.au | bus. 9555 5555 ext. 123456'


# question = "Use this text to answer my questions. " + content


# messages = []
# # Set the question to answer
# cresponse = GetMessageMemory(question, messages)
# messages.append({"role": "system", "content": cresponse})



# cresponse = GetMessageMemory("extract the client_id"
#                     , messages)
# print(cresponse)












# def chat(system, user_assistant):
#     assert isinstance(system, str), "`system` should be a string"
#     assert isinstance(user_assistant, list), "`user_assistant` should be a list"
#     system_msg = [{"role": "system", "content": system}]
#     user_assistant_msgs = [
#         {"role": "assistant", "content": user_assistant[i]} if i % 2 else {"role": "user", "content": user_assistant[i]}
#         for i in range(len(user_assistant))]

#     msgs = system_msg + user_assistant_msgs
#     response = openai.ChatCompletion.create(model="gpt-3.5-turbo",
#                                             messages=msgs)
#     status_code = response["choices"][0]["finish_reason"]
#     assert status_code == "stop", f"The status code was {status_code}."
#     return response["choices"][0]["message"]["content"]


# response_fn_test = chat("You are a machine learning expert.",["Explain what a neural network is."])

# display(Markdown(response_fn_test))