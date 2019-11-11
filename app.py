from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

app = Flask(__name__)
line_bot_api_key = os.environ.get('line_bot_api')
line_msg_set_key = os.environ.get('line_msg_set')
line_bot_api = LineBotApi(line_bot_api)
handler = WebhookHandler(line_msg_set)


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=event.message.text))

# A welcome message to test our server
@app.route('/')
def index():
    return "<h1>Welcome to Cooca !!</h1>"

if __name__ == "__main__":
    app.run()
