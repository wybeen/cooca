# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import errno
import os
import sys
import tempfile
import random
import requests as req
from argparse import ArgumentParser

from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    LineBotApiError, InvalidSignatureError
)
"""
from linebot.models import (
    MessageAction
)
"""
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, PostbackEvent,
    SourceUser, SourceGroup, SourceRoom,
    TemplateSendMessage, ButtonsTemplate
)

app = Flask(__name__)

# get channel_secret and channel_access_token from your environment variable
channel_secret = os.environ.get('line_bot_acc_key', None)
channel_access_token = os.environ.get('line_bot_set_key', None)
if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    print("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except LineBotApiError as e:
        print("Got exception from LINE Messaging API: %s\n" % e.message)
        for m in e.error.details:
            print("  %s: %s" % (m.property, m.message))
        print("\n")
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    if (event.reply_token ==  '00000000000000000000000000000000'):
        return None
    text = event.message.text
    print(text)
    if text == 'profile':
        if isinstance(event.source, SourceUser):
            profile = line_bot_api.get_profile(event.source.user_id)
            line_bot_api.reply_message(
                event.reply_token, [
                    TextSendMessage(text='Display name: ' + profile.display_name),
                    TextSendMessage(text='Status message: ' + profile.status_message)
                ]
            )
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="Bot can't use profile API without user ID"))

@handler.add(PostbackEvent)
def handle_postback(event):
    print("event.postback.data:" + event.postback.data)
    if event.postback.data == 'action=quiz':
        results = req.get('https://opentdb.com/api.php?amount=1&type=multiple').json()
        result = results["results"][0]
        button_title = result["category"] + ' - ' + result["difficulty"]
        question = button_title + '\n' + result["question"]
        actionary = []
        cnt = len(result["incorrect_answers"])
        r = random.randint(0,cnt - 1)
        for x in range(cnt):
            if r==x:
                ans = result["correct_answer"][:20]
                actionary.append({"type":"message", "label": ans, "text":('答案是 ' + ans + ', 我答對了, 請給我拍拍手.')})
            ans = result["incorrect_answers"][x][:20]
            actionary.append({"type":"message", "label":ans, "text":('答案不是 ' + ans + ', 我錯了 orz')})
        buttons_template = ButtonsTemplate(text=question, actions=actionary)
        template_message = TemplateSendMessage(alt_text=question, template=buttons_template)
        line_bot_api.reply_message(event.reply_token, template_message)

# A welcome message to test our server
@app.route('/')
def index():
    return "<h1>Welcome to Cooca !!</h1>"

if __name__ == "__main__":
    app.run()


#  Licensed under the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License. You may obtain
#  a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  License for the specific language governing permissions and limitations
#  under the License.