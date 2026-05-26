import google.generativeai as genai

genai.configure(api_key="AIzaSyD4WMl_Lpxb6mwGMgjX4Y0HmptC59-yQ1c")

for m in genai.list_models():
    print(m.name, m.supported_generation_methods)
