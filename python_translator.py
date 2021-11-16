import tkinter as tk
from tkinter.constants import LEFT, RIGHT
import win32clipboard as w
import win32con
import json
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.tmt.v20180321 import tmt_client, models

'''
Fill the key
'''
SecretId = ""
SecretKey = ""

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

# Translate API (en-us -> zh-cn)
def translate_tencent(text):
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



if __name__ == '__main__':
    window = tk.Tk()
    window.title('Translator')
    # window.geometry('500x300') 

    # Window always on top
    window.wm_attributes('-topmost', 1)  
    
    frm1 = tk.Frame(window)
    frm2 = tk.Frame(window)

    var = tk.StringVar()    
    l = tk.Label(frm1, textvariable=var, bg="white", width=40, height=3)
    l.pack(side=tk.LEFT, fill="both", expand=True)
    
    def trans():
        text = getText()
        print(text)
        text_transed = translate_tencent(text)
        var.set(text_transed)
    
    b = tk.Button(frm2, text='go', width=3, height=2, command=trans)
    b.pack(side=tk.RIGHT)

    frm1.pack(fill=tk.Y, side=tk.LEFT)
    frm2.pack(fill=tk.Y, side=tk.RIGHT)
    window.mainloop()