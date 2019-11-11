import os
import random

from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler, WebhookParser
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageSendMessage,
)
from pixabay import Image

app = Flask(__name__)
line_bot_acc_key = os.environ.get('line_bot_acc_key', None)
if line_bot_acc_key is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)
    
line_bot_set_key = os.environ.get('line_bot_set_key', None)
if line_bot_set_key is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)

line_bot_api = LineBotApi(line_bot_set_key)
parser = WebhookParser(line_bot_acc_key)


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    print("Request body: " + body)

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

        # line_bot_api.reply_message(
        #    event.reply_token,
        #    TextSendMessage(text=event.message.text)
        # )
        pixabay_key = os.environ.get('pixabay_key')
        # image operations
        image = Image(pixabay_key)
        # custom image search
        ims = image.search(q=event.message.text,
            image_type='photo',
            order='popular',
            page=1,
            per_page=20)
            
        hits = ims.get("hits")
        
        if len(hits) != 0:
            r = random.randint(0,len(hits))
            hit = hits[r]
            previewURL = hit["webformatURL"]            
            line_bot_api.reply_message(event.reply_token,ImageSendMessage(previewURL, previewURL))
        else:
            imgurl = "https://cdn.hk01.com/di/media/images/2246786/org/3d7a7f543222c5b5f20fe142f2b35e4a.jpg/ikLi2r1cCiuwJpW3Hw7MUk90Ueb6y_TatUNPvLVDT7w"
            line_bot_api.reply_message(event.reply_token,ImageSendMessage(imgurl, imgurl))
            
    return 'OK'


# A welcome message to test our server
@app.route('/')
def index():
    return "<h1>Welcome to Cooca !!</h1>"

if __name__ == "__main__":
    app.run()
