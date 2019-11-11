import os

from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler, WebhookParser
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

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

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=event.message.text)
        )

    return 'OK'


# A welcome message to test our server
@app.route('/')
def index():
    return "<h1>Welcome to Cooca !!</h1>"

if __name__ == "__main__":
    app.run()
