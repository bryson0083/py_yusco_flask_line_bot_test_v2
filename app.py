# -*- coding: utf-8 -*-
"""
 app Line bot網站主程式

@Usage:
    app.route("/callback", methods=['POST'])
    說明: 
        LINE使用者動作Listner

    app.route("/auth", methods=['GET'])
    說明: 
        LINE使用者，內部身分驗證


@Note: 
    
"""

from flask import Flask, request, abort, Response, send_from_directory

from linebot import (
    LineBotApi, WebhookHandler, WebhookParser
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageSendMessage
)
import os

### 以下import自行開發公用程式 ###
import util.APP_ENVIR_ARGS as APP_ENVIR_ARGS
import util.LINE_BOT_AUTH_MAIL as LB_AUTH_MAIL
import util.LINE_BOT_AUTH_TOKEN as LB_AUTH_TOKEN

### program start ##########################################################
app = Flask(__name__)

#取得line bot參數
line_token = APP_ENVIR_ARGS.getArg('line_bot_arg','token')
line_channel_sec = APP_ENVIR_ARGS.getArg('line_bot_arg','channel_sec')

# Channel Access Token
line_bot_api = LineBotApi(line_token)

# Channel Secret
parser = WebhookParser(line_channel_sec)

line_bot_api.push_message('Ucfd9d2f4a7a45fbf4143ed44fda3989d', TextSendMessage(text='你好!我是毛君伯 from YUSCO.'))

# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)

    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue

        text=event.message.text
        print('**** user input=' + str(text))
        #userId = event['source']['userId']
        if(text.lower()=='/me'):
            content = str(event.source.user_id)

            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=content)
            )
        elif(text.lower()=='/profile'):
            profile = line_bot_api.get_profile(str(event.source.user_id))
            print(profile.display_name)
            print(profile.user_id)
            print(profile.picture_url)
            print(profile.status_message)
        elif(text.lower()[:5]=='/auth'):
            empl_no = text.lower()[6:]
            profile = line_bot_api.get_profile(str(event.source.user_id))

            print('工號' + empl_no + '進行身分驗證.')

            #發送認證信件
            rt_code = LB_AUTH_MAIL.SEND_MAIL(empl_no, str(event.source.user_id))
            
            if rt_code == 0:
                msg = '你好，請至公司信箱收取認證信件'
            elif rt_code == 1:
                msg = '帳號' + empl_no + '已驗證過，不再重複認證.'
            elif rt_code == 2:
                msg = '帳號' + empl_no + '短時間重複認證請求.'
            else:
                msg = '其他原因錯誤，驗證請求失敗.'

            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=msg)
            )

        elif(text.lower()=='/pic'):
            site_url = 'https://103562e5.ngrok.io'
            img_url = site_url + "/img/tb_img2.png"
            #img_url = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRZVn4lAwCOhTZvgAFIFLTVdzKe4JIVKcgnBL3pBSzzsBjY1FpM"
            print("@@ img url=>" + img_url)
            line_bot_api.reply_message(
                event.reply_token,
                [ImageSendMessage(
                                    original_content_url=img_url,
                                    preview_image_url=img_url
                                )]
            )

        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text='咩~!我不認識這個指令啦> <')
            )

    return 'OK'

@app.route("/auth", methods=['GET'])
def user_auth():
    token = request.args.get('token')

    #郵件驗證
    rt_code, line_userid = LB_AUTH_TOKEN.AUTH_URL_TOKEN(token)

    msg = ""
    if rt_code == 0:
        msg = '你已通過驗證，歡迎使用!'
    else:
        msg = '驗證失敗'

    return msg

@app.route('/getfile/<name>')
def get_output_file(name):
    OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
    file_name = os.path.join(OUTPUT_DIR, name)
    #print(file_name)

    if not os.path.isfile(file_name):
        return "No File"

    # read without gzip.open to keep it compressed
    with open(file_name, 'rb') as f:
        resp = Response(f.read())
        
    # set headers to tell encoding and to send as an attachment
    #resp.headers["Content-Encoding"] = 'gzip'
    resp.headers["Content-Disposition"] = "attachment; filename={0}".format(name)
    resp.headers["Content-type"] = "application/pdf"
    return resp

@app.route('/img/<path:path>')
def send_js(path):
    return send_from_directory('img', path)


@app.route("/", methods=['GET'])
def basic_url():
    return 'OK'

import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
