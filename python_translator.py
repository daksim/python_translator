import tkinter as tk
from tkinter.constants import LEFT, RIGHT
import win32clipboard as w
import win32con
import json
import requests
import random
from hashlib import md5
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.tmt.v20180321 import tmt_client, models


# Functions to read or change texts in windows clipboard
def getText():
    w.OpenClipboard()
    d = w.GetClipboardData(win32con.CF_TEXT)
    w.CloseClipboard()
    return d.decode('GBK').replace('-\n', ' ').replace('\n', ' ')

def setText(aString):
    w.OpenClipboard()
    w.EmptyClipboard()
    w.SetClipboardData(win32con.CF_TEXT, aString)
    w.CloseClipboard()

# Tencent translate API (en-us -> zh-cn)
def translate_tencent(text):
    SecretId = ""
    SecretKey = ""
    try:
        cred = credential.Credential(SecretId, SecretKey)
        httpProfile = HttpProfile()
        httpProfile.endpoint = "tmt.tencentcloudapi.com"

        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        client = tmt_client.TmtClient(cred, "ap-shanghai", clientProfile)

        req = models.TextTranslateRequest()
        params = {
            "SourceText": text,
            "Source": "en",
            "Target": "zh",
            "ProjectId": 0
        }
        req.from_json_string(json.dumps(params))

        resp = client.TextTranslate(req)
        return resp.TargetText.replace('\n', ' ')

    except TencentCloudSDKException as err:
        return err

# Baidu translate API (en-us -> zh-cn)
def translate_baidu(text):
    # Set your own appid/appkey.
    appid = ''
    appkey = ''

    # For list of language codes, please refer to `https://api.fanyi.baidu.com/doc/21`
    from_lang = 'en'
    to_lang =  'zh'

    endpoint = 'http://api.fanyi.baidu.com'
    path = '/api/trans/vip/translate'
    url = endpoint + path

    query = text

    # Generate salt and sign
    def make_md5(s, encoding='utf-8'):
        return md5(s.encode(encoding)).hexdigest()

    salt = random.randint(32768, 65536)
    sign = make_md5(appid + query + str(salt) + appkey)

    # Build request
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    payload = {'appid': appid, 'q': query, 'from': from_lang, 'to': to_lang, 'salt': salt, 'sign': sign}

    # Send request
    r = requests.post(url, params=payload, headers=headers)
    result = r.json()

    # Show response
    result_text = result['trans_result'][0]['dst']
    # print(result_text)
    return result_text




if __name__ == '__main__':
    window = tk.Tk()
    window.title('Translator')
    # window.geometry('') 

    # Window always on top
    window.wm_attributes('-topmost', 1)  
    
    frm1 = tk.Frame(window)
    frm2 = tk.Frame(window, width=3)

    # Use tk.Text rather than tk.label
    # # var = tk.StringVar()    
    t = tk.Text(frm1, bg="white", width=50, height=4)
    t.pack(side=tk.LEFT, fill="both", expand=True)
    
    def trans():
        text = getText()
        # print(text)
        text_transed = translate_baidu(text)
        # Delete previous content
        t.delete('1.0','end')
        t.update()
        t.insert('end', text_transed)
    
    b = tk.Button(frm2, text='go', width=3, height=4, command=trans)
    b.pack(side=tk.RIGHT)

    frm1.pack(fill=tk.Y, side=tk.LEFT)
    frm2.pack(fill=tk.Y, side=tk.RIGHT)

    # Prohibit changing window size
    window.resizable(0,0)
    window.mainloop()