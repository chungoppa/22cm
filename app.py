import time
from collections import Counter
from flask import Flask, request, abort, app
import json
import locale
from linebot.models import *
import gspread
from oauth2client.service_account import ServiceAccountCredentials

from flask import Flask, request, abort, send_from_directory
from werkzeug.middleware.proxy_fix import ProxyFix
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError,
    LineBotApiError)
app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_host=1, x_proto=1)
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('dumbbot-8fad35afb0c6.json', scope)
client = gspread.authorize(creds)
mainsheet = client.open('SGVN')
sheet = client.open('SGVN').sheet1
tmpordersheet = mainsheet.worksheet('tmporder')
tmpuserinfo = mainsheet.worksheet(('tmpuserinfo'))
ordersheet = mainsheet.worksheet('orders')
userinfosheet = mainsheet.worksheet('userinfo')
# questionssheet = mainsheet.worksheet('questionsInOderdelivery')
# submenusheet = mainsheet.worksheet('subMenu')
# menusheet = mainsheet.worksheet('Menu')
reportReceiver = mainsheet.worksheet('reportReceiver')

#  locale
locale.setlocale(locale.LC_ALL, 'de_DE.utf-8')
# Channel Access Token
#line_bot_api = LineBotApi('E32ScD/CUH3lsXhc5G0DxYcGNteGlkRllINxS64FasXlTZX/0mwjqRmROimkIHW7VCa2eRmC7wE6jV1VaUDddifZ4hXV8iZUG47tvXDYT2fSRPWSEKIMNfZRhA7wIgRGAq6QKtyvX9GwWH5pRs2aWAdB04t89/1O/w1cDnyilFU=')

line_bot_api = LineBotApi('bOiXla2lbcGsYnZkXnhxOAkyAzuGTSDrGVZGF/hrMjlws0+DhIoFq8i9f3xjR8DHmR6KqVpU/UW+SR8yAKDyt/PEecZg5jU9AjAIPQBvYpZRrQPrzWVQCmd10l8q4E0q17mtskg/bljPsPxPFSUj9QdB04t89/1O/w1cDnyilFU=')
# Channel Secret
handler = WebhookHandler('6c7ba1b67dfdafeb29f7b546465154c4')
#handler = WebhookHandler('f711b7b7c6a484191cbdb24593e766bc').



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
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(FollowEvent)
def sendGreetingms(event):
        if isinstance(event.source, SourceUser):
            profile = line_bot_api.get_profile(event.source.user_id)
            uid = profile.user_id
            line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='ご登録ありがとうございます。 \nこちらは居酒屋「くーろん」・原田商店のページでございます。\nこちらからレストラン予約・食材、弁当のデリバリー注文が可能です。 \n下記メニューからお進みください。\n今後とも宜しくお願いします。'))



@handler.add((MessageEvent),message=TextMessage)
def getUserinfo(event):
    text = event.message.text
    try:
        tmp = tmpordersheet.find(str(event.source.user_id))
    except:
        tmp = None
    if tmp is None:
        print("")
    else:
        col= None
        row =None
        try:
            tmp2 = tmpuserinfo.find(str(event.source.user_id))
            cell_list = tmpuserinfo.range('B' + str(tmp2.row) + ':G' + str(tmp2.row))
            for cell in cell_list:
                if cell.value == '':
                    col = cell.col
                    row = cell.row
                    break
        except:
            tmp2 = None
        if col == 2 and (not cell_list is None):
            tmpuserinfo.update_cell(row, col, text)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='電話番号を教えてください。'))
        elif col == 3 and (not cell_list is None):
            tmpuserinfo.update_cell(row, col, text)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='住所を教えてください。'))
        elif col == 4 and (not cell_list is None):
            tmpuserinfo.update_cell(row, col, text)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='マンション名を教えてください。'))
        elif col == 5 and (not cell_list is None):
            tmpuserinfo.update_cell(row, col, text)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='ご希望の配達日時を教えてください。'))
        elif col == 6 and (not cell_list is None):
            tmpuserinfo.update_cell(row, col, text)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='その他特別な要求がありますか？。'))
        elif col == 7 and (not cell_list is None):
            tmpuserinfo.update_cell(row, col, text)
            cell_listo= []
            cell_list = tmpordersheet.range('B' + str(tmp.row) + ':Z' + str(tmp.row))
            for cell in cell_list:
                if not cell.value == '':
                    cell_listo.append(cell.value)
            line_bot_api.reply_message(event.reply_token, [TextSendMessage(text='Here is your information\n'+'Name : ' + str(tmpuserinfo.cell(row,2).value)
                                                                        +'\nPhonenumber : '+ str(tmpuserinfo.cell(row,3).value)
                                                                        +'\nAddress : ' + str(tmpuserinfo.cell(row,4).value)
                                                                        +'\nHouseNumber : ' + str(tmpuserinfo.cell(row,5).value)
                                                                        +'\nTime : ' + str(tmpuserinfo.cell(row,6).value)
                                                                        +'\nAddictional Info : ' + str(tmpuserinfo.cell(row,7).value)
                                                                        +'\n Order list : \n'+getorderfromlist(cell_listo)
                                                                        ,quick_reply=QuickReply(items=[
                                                                                   QuickReplyButton(
                                                                                       action=MessageAction(label="Ok", text="ok")
                                                                                   ),QuickReplyButton(
                                                                                       action=MessageAction(label="Edit", text="edit")
                                                                                   )]))
                                                           ])

        elif col is None and ( not cell_list is None) and text == 'ok':
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='さて、今私はあなたの注文をレストランに送ります。'))
            cell_listo= []
            cell_list = tmpordersheet.range('B' + str(tmp.row) + ':Z' + str(tmp.row))
            for cell in cell_list:
                if not cell.value == '':
                    cell_listo.append(cell.value)
            receiver = reportReceiver.cell(1,1).value
            line_bot_api.push_message(str(receiver),TextSendMessage(text='Order of Customer\n'+'Name : ' + str(tmpuserinfo.cell(tmp2.row,2).value)
                                                                        +'\nPhonenumber : '+ str(tmpuserinfo.cell(tmp2.row,3).value)
                                                                        +'\nAddress : ' + str(tmpuserinfo.cell(tmp2.row,4).value)
                                                                        +'\nHouseNumber : ' + str(tmpuserinfo.cell(tmp2.row,5).value)
                                                                        +'\nTime : ' + str(tmpuserinfo.cell(tmp2.row,6).value)
                                                                        +'\nAddictional Info : ' + str(tmpuserinfo.cell(tmp2.row,7).value)+'\nList of oder : \n' +getorderfromlist(cell_listo)))
            ordersheet.insert_row(tmpordersheet.row_values(tmp.row))
            userinfosheet.insert_row(tmpuserinfo.row_values(tmp2.row))
            tmpordersheet.delete_row(tmp.row)
            tmpuserinfo.delete_row(tmp2.row)
        elif col is None and (not cell_list is None) and text =='edit' :
            tmpuserinfo.delete_row(tmp2.row)
            line_bot_api.reply_message(event.reply_token,[TextSendMessage(text='並べ替える場合は、もう一度食材・弁当デリバリーを選択します \nさて、今私はあなたにもう一度あなたの情報を尋ねます'),TextSendMessage(text='お名前を教えてください。?')])
            new = [str(event.source.user_id), ""]
            tmpuserinfo.insert_row(new)

def getorderfromlist(list):
    strorder = ''
    tmplist = list
    totalprice = 0
    for i in Counter(tmplist) :
        count = list.count(i)
        price = getpricebyname(i)*count
        totalprice = totalprice+ price
        strorder = strorder + str(i) +' : x '+ str(count) +'    -    ' + str(price)+'\n'
    return strorder + '\n Total :'+str(totalprice)

# def getReportofOrder(event,rowinTmpuserInfo):
#     question_list = questionssheet.row_values(2)
#     tmpuserinfo_list = tmpuserinfo.row_values(rowinTmpuserInfo)
#     getUserInfofromList(question_list,tmpuserinfo_list)
#     line_bot_api.reply_message(event.reply_token,TextSendMessage(text=getUserInfofromList(question_list,tmpuserinfo_list),quick_reply=QuickReply(items=[
#                 QuickReplyButton(
#                     action=MessageAction(label="Ok", text="ok")
#                 ), QuickReplyButton(
#                     action=MessageAction(label="Edit", text="edit")
#                 )])))
def getUserInfofromList(qlist,ulist):
    string = 'Here is your infomation :'
    i=1
    for num in qlist:
        string = '\n'+ string +str(num) +  str(ulist[i])
        i=i+1
    return string

def clearorder(event):
    tmp = None
    tmp2 = None
    try:
        tmp = tmpordersheet.find(str(event.source.user_id))
        tmp2 = tmpuserinfo.find(str(event.source.user_id))
    except:
        print(' something wrong !, im not able to clear your temporary data  。')
    if not tmp is None :
        tmpordersheet.delete_row(tmp.row)
    if not tmp2 is None :
        tmpuserinfo.delete_row(tmp2.row)

def getpricebyname(name):
    if name == 'サンマの開き':
        return 60000
    elif name == '塩サバ切り身' :
        return 60000
    elif name == 'サケ切り身':
        return 75000
    elif name == 'サワラの味噌漬け':
        return 65000
    elif name == '野菜サラダ':
        return 20000
    elif name == 'れんこんキンピラ':
        return 30000
    elif name == 'ひじきの炒め煮':
        return 30000
    elif name == '高菜のじゃこ炒め':
        return 30000
    elif name == '紅茶豚（スライス５枚）':
        return 110000
    elif name == '手作り冷凍餃子（５個）':
        return 35000
    elif name == '砂肝にんにく炒め':
        return 80000
    elif name == 'ハンバーグ（ソース付）':
        return 110000
    elif name == 'エビチリ':
        return 100000
    elif name == 'サバの味噌煮':
        return 100000
    elif name == '豚生姜焼き':
        return 90000
    elif name == 'レバニラ炒め':
        return 90000
    elif name == '手羽醤油焼き':
        return 90000
    elif name == '中華丼（ソースのみ）':
        return 100000

# '生鮮食品
def submenu1(event):
    サンマの開き = request.url_root + '/static/サンマの開き.JPG'
    塩サバ切り身 = request.url_root + '/static/塩サバ切り身.JPG'
    サケ切り身 = request.url_root + '/static/サケ切り身.JPG'
    サワラの味噌漬け = request.url_root +'/static/サワラの味噌漬け.JPG'
    carousel_template = CarouselTemplate(columns=[
        CarouselColumn(text=format(getpricebyname('サンマの開き'),',d'), title='サンマの開き',
                       thumbnail_image_url=サンマの開き, actions=[PostbackAction(label='カートに追加', data='サンマの開き')]),
        CarouselColumn(text=format(getpricebyname('塩サバ切り身'),',d'), title='塩サバ切り身',
                       thumbnail_image_url=塩サバ切り身, actions=[PostbackAction(label='カートに追加', data='塩サバ切り身')]),
        CarouselColumn(text=format(getpricebyname('サケ切り身'),',d'), title='サケ切り身',
                       thumbnail_image_url=サケ切り身, actions=[PostbackAction(label='カートに追加', data='サケ切り身')]),
        CarouselColumn(text=format(getpricebyname('サワラの味噌漬け'),',d'), title='サワラの味噌漬け',
                       thumbnail_image_url=サワラの味噌漬け, actions=[PostbackAction(label='カートに追加', data='サワラの味噌漬け')])
    ])
    template_message = TemplateSendMessage(
        alt_text='Carousel alt text', template=carousel_template)
    line_bot_api.reply_message(event.reply_token, template_message)

# 一品物
def submenu2(event):
    紅茶豚= request.url_root + '/static/紅茶豚（スライス５枚）.JPG'
    手作り = request.url_root + '/static/1.JPG'
    砂肝にんにく炒め = request.url_root + '/static/砂肝にんにく炒め.JPG'
    ハンバーグ = request.url_root +'/static/ハンバーグ（ソース付）.JPG'

    エビチリ = request.url_root +'/static/エビチリ.JPG'
    サバの味噌煮 = request.url_root + '/static/サバの味噌煮.JPG'
    豚生姜焼き = request.url_root + '/static/豚生姜焼き.JPG'
    レバニラ炒め = request.url_root + '/static/レバニラ炒め.JPG'

    手羽醤油焼き = request.url_root + '/static/手羽醤油焼き.JPG'
    中華丼 = request.url_root + '/static/中華丼（ソースのみ）.JPG'
    carousel_template = CarouselTemplate(columns=[
        CarouselColumn(text=format(getpricebyname('紅茶豚（スライス５枚）'),',d'), title='紅茶豚（スライス５枚）',
                       thumbnail_image_url=紅茶豚, actions=[PostbackAction(label='カートに追加', data='紅茶豚（スライス５枚）')]),
        CarouselColumn(text=format(getpricebyname('手作り冷凍餃子（５個）'),',d'), title='手作り冷凍餃子（５個）',
                        thumbnail_image_url=手作り, actions=[PostbackAction(label='カートに追加', data='手作り冷凍餃子（５個）')]),
        CarouselColumn(text=format(getpricebyname('砂肝にんにく炒め'),',d'), title='砂肝にんにく炒め',
                       thumbnail_image_url=砂肝にんにく炒め, actions=[PostbackAction(label='カートに追加', data='砂肝にんにく炒め')]),
        CarouselColumn(text=format(getpricebyname('ハンバーグ（ソース付）'),',d'), title='ハンバーグ',
                       thumbnail_image_url=ハンバーグ, actions=[PostbackAction(label='カートに追加', data='ハンバーグ')]),

        CarouselColumn(text=format(getpricebyname('エビチリ'),',d'),title='エビチリ',
                       thumbnail_image_url=エビチリ, actions=[PostbackAction(label='カートに追加', data='エビチリ')]),
        CarouselColumn(text=format(getpricebyname('サバの味噌煮'),',d'), title='サバの味噌煮',
                       thumbnail_image_url=サバの味噌煮, actions=[PostbackAction(label='カートに追加', data='サバの味噌煮')]),
        CarouselColumn(text=format(getpricebyname('豚生姜焼き'),',d'), title='豚生姜焼き',
                       thumbnail_image_url=豚生姜焼き, actions=[PostbackAction(label='カートに追加', data='豚生姜焼き')]),
        CarouselColumn(text=format(getpricebyname('レバニラ炒め'),',d'), title='レバニラ炒め',
                       thumbnail_image_url=レバニラ炒め, actions=[PostbackAction(label='カートに追加', data='レバニラ炒め')]),

        CarouselColumn(text=format(getpricebyname('手羽醤油焼き'),',d'), title='手羽醤油焼き',
                       thumbnail_image_url=手羽醤油焼き, actions=[PostbackAction(label='カートに追加', data='手羽醤油焼き')]),
        CarouselColumn(text=format(getpricebyname('中華丼（ソースのみ）'),',d'), title='中華丼（ソースのみ）',
                       thumbnail_image_url=中華丼, actions=[PostbackAction(label='カートに追加', data='中華丼（ソースのみ）')]),
    ])
    template_message = TemplateSendMessage(
        alt_text='Carousel alt text', template=carousel_template)
    line_bot_api.reply_message(event.reply_token, template_message)

# お潰物・サラダ他　約一人前
def submenu3(event):
    野菜サラダ = request.url_root + '/static/野菜サラダ.JPG'
    carousel_template = CarouselTemplate(columns=[
        CarouselColumn(text=format(getpricebyname('野菜サラダ'),',d'), title='野菜サラダ',
                       thumbnail_image_url=野菜サラダ, actions=[PostbackAction(label='カートに追加', data='野菜サラダ')]),
    ])
    template_message = TemplateSendMessage(
        alt_text='Carousel alt text', template=carousel_template)
    line_bot_api.reply_message(event.reply_token, template_message)

# お惣菜1袋50ｇ 約一人前
def submenu4(event):
    れんこんキンピラ = request.url_root + '/static/れんこんキンピラ.JPG'
    ひじきの炒め煮 = request.url_root + '/static/ひじきの炒め煮.JPG'
    高菜のじゃこ炒め = request.url_root + '/static/高菜のじゃこ炒め.JPG'
    carousel_template = CarouselTemplate(columns=[
        CarouselColumn(text=format(getpricebyname('れんこんキンピラ'),',d'), title='れんこんキンピラ',
                       thumbnail_image_url=れんこんキンピラ, actions=[PostbackAction(label='カートに追加', data='れんこんキンピラ')]),
        CarouselColumn(text=format(getpricebyname('ひじきの炒め煮'),',d'), title='ひじきの炒め煮',
                       thumbnail_image_url=ひじきの炒め煮, actions=[PostbackAction(label='カートに追加', data='ひじきの炒め煮')]),
        CarouselColumn(text=format(getpricebyname('高菜のじゃこ炒め'),',d'), title='サケ切り身',
                       thumbnail_image_url=高菜のじゃこ炒め, actions=[PostbackAction(label='カートに追加', data='高菜のじゃこ炒め')]),
    ])
    template_message = TemplateSendMessage(
        alt_text='Carousel alt text', template=carousel_template)
    line_bot_api.reply_message(event.reply_token, template_message)


#  カートに追加 and handle Post back event
@handler.add(PostbackEvent)
def handle_postback(event):
    # sub1
    if event.postback.data == 'サンマの開き':
        addtocart(event,"サンマの開き")
        line_bot_api.reply_message(event.reply_token,
                                   TextSendMessage(text='サンマの開きカートに追加 ', quick_reply=QuickReply(
                                           items=[
                                               QuickReplyButton(
                                                   action=MessageAction(label="完了", text="完了")
                                               )])))
    elif event.postback.data == '塩サバ切り身':
        addtocart(event,"塩サバ切り身")
        line_bot_api.reply_message(event.reply_token,
                                   TextSendMessage(text='塩サバ切り身カートに追加', quick_reply=QuickReply(
                                           items=[
                                               QuickReplyButton(
                                                   action=MessageAction(label="完了", text="完了")
                                               )])))
    elif event.postback.data == 'サケ切り身':
        addtocart(event, "サケ切り身")
        line_bot_api.reply_message(event.reply_token,
                                   TextSendMessage(text='サケ切り身カートに追加', quick_reply=QuickReply(
                                       items=[
                                           QuickReplyButton(
                                               action=MessageAction(label="完了", text="完了")
                                           )])))
    elif event.postback.data =='サワラの味噌漬け':
        addtocart(event, "サワラの味噌漬け")
        line_bot_api.reply_message(event.reply_token,
                                   TextSendMessage(text='サワラの味噌漬けカートに追加', quick_reply=QuickReply(
                                       items=[
                                           QuickReplyButton(
                                               action=MessageAction(label="完了", text="完了")
                                           )])))
    # sub2
    elif event.postback.data == '紅茶豚（スライス５枚）':
        addtocart(event,"紅茶豚（スライス５枚）")
        line_bot_api.reply_message(event.reply_token,
                                   TextSendMessage(text='紅茶豚（スライス５枚）カートに追加', quick_reply=QuickReply(
                                           items=[
                                               QuickReplyButton(
                                                   action=MessageAction(label="完了", text="完了")
                                               )])))
    elif event.postback.data == '手作り-冷凍餃子':
        addtocart(event, "手作り-冷凍餃子")
        line_bot_api.reply_message(event.reply_token,
                                   TextSendMessage(text='手作り-冷凍餃子カートに追加', quick_reply=QuickReply(
                                       items=[
                                           QuickReplyButton(
                                               action=MessageAction(label="完了", text="完了")
                                           )])))
    elif event.postback.data =='砂肝にんにく炒め':
        addtocart(event, "砂肝にんにく炒め")
        line_bot_api.reply_message(event.reply_token,
                                   TextSendMessage(text='砂肝にんにく炒めカートに追加', quick_reply=QuickReply(
                                       items=[
                                           QuickReplyButton(
                                               action=MessageAction(label="完了", text="完了")
                                           )])))

    elif event.postback.data == 'ハンバーグ（ソース付）':
        addtocart(event,"ハンバーグ（ソース付）")
        line_bot_api.reply_message(event.reply_token,
                                   TextSendMessage(text='ハンバーグ（ソース付）カートに追加', quick_reply=QuickReply(
                                           items=[
                                               QuickReplyButton(
                                                   action=MessageAction(label="完了", text="完了")
                                               )])))
    elif event.postback.data == 'エビチリ':
        addtocart(event, "エビチリ")
        line_bot_api.reply_message(event.reply_token,
                                   TextSendMessage(text='エビチリ', quick_reply=QuickReply(
                                       items=[
                                           QuickReplyButton(
                                               action=MessageAction(label="完了", text="完了")
                                           )])))
    elif event.postback.data =='サバの味噌煮':
        addtocart(event, "サバの味噌煮")
        line_bot_api.reply_message(event.reply_token,
                                   TextSendMessage(text='サバの味噌煮カートに追加', quick_reply=QuickReply(
                                       items=[
                                           QuickReplyButton(
                                               action=MessageAction(label="完了", text="完了")
                                           )])))

    elif event.postback.data == '豚生姜焼き':
        addtocart(event,"豚生姜焼き")
        line_bot_api.reply_message(event.reply_token,
                                   TextSendMessage(text='豚生姜焼きカートに追加', quick_reply=QuickReply(
                                           items=[
                                               QuickReplyButton(
                                                   action=MessageAction(label="完了", text="完了")
                                               )])))
    elif event.postback.data == 'レバニラ炒め':
        addtocart(event, "レバニラ炒め")
        line_bot_api.reply_message(event.reply_token,
                                   TextSendMessage(text='レバニラ炒めカートに追加', quick_reply=QuickReply(
                                       items=[
                                           QuickReplyButton(
                                               action=MessageAction(label="完了", text="完了")
                                           )])))
    elif event.postback.data =='手羽醤油焼き':
        addtocart(event, "手羽醤油焼き")
        line_bot_api.reply_message(event.reply_token,
                                   TextSendMessage(text='手羽醤油焼きカートに追加', quick_reply=QuickReply(
                                       items=[
                                           QuickReplyButton(
                                               action=MessageAction(label="完了", text="完了")
                                           )])))

    elif event.postback.data == '中華丼（ソースのみ）':
        addtocart(event,"中華丼（ソースのみ）")
        line_bot_api.reply_message(event.reply_token,
                                   TextSendMessage(text='中華丼（ソースのみ）カートに追加', quick_reply=QuickReply(
                                           items=[
                                               QuickReplyButton(
                                                   action=MessageAction(label="完了", text="完了")
                                               )])))
    #     sub3
    elif event.postback.data == '野菜サラダ':
        addtocart(event,"野菜サラダ")
        line_bot_api.reply_message(event.reply_token,
                                   TextSendMessage(text='野菜サラダカートに追加', quick_reply=QuickReply(
                                           items=[
                                               QuickReplyButton(
                                                   action=MessageAction(label="完了", text="完了")
                                               )])))
    #         sub4
    elif event.postback.data == 'れんこんキンピラ':
        addtocart(event,"れんこんキンピラ")
        line_bot_api.reply_message(event.reply_token,
                                   TextSendMessage(text='れんこんキンピラカートに追加', quick_reply=QuickReply(
                                           items=[
                                               QuickReplyButton(
                                                   action=MessageAction(label="完了", text="完了")
                                               )])))
    elif event.postback.data == 'ひじきの炒め煮':
        addtocart(event, "ひじきの炒め煮")
        line_bot_api.reply_message(event.reply_token,
                                   TextSendMessage(text='ひじきの炒め煮カートに追加', quick_reply=QuickReply(
                                       items=[
                                           QuickReplyButton(
                                               action=MessageAction(label="完了", text="完了")
                                           )])))
    elif event.postback.data =='高菜のじゃこ炒め':
        addtocart(event, "高菜のじゃこ炒め")
        line_bot_api.reply_message(event.reply_token,
                                   TextSendMessage(text='高菜のじゃこ炒めカートに追加', quick_reply=QuickReply(
                                       items=[
                                           QuickReplyButton(
                                               action=MessageAction(label="完了", text="完了")
                                           )])))

def addtocart(event,orderid):
    # tmp = None
    try:
        tmp = tmpordersheet.find(str(event.source.user_id))
    except:
        tmp = None
    if tmp is None:
        renew = [str(event.source.user_id), str(orderid)]
        tmpordersheet.insert_row(renew)
    else:
        cell_list = tmpordersheet.range('A'+str(tmp.row) +':Z'+str(tmp.row))
        for cell in cell_list:
            if cell.value == '':
                tmpordersheet.update_cell(cell.row,cell.col,str(orderid))

                return

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    message = TextSendMessage(text=event.message.text)
    text = event.message.text
    if text== 'getid':
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=event.source.user_id))
    elif text == 'レストラン予約':
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="This feature being developed"))
    elif text == '食材・弁当デリバリー':
        clearorder(event)
        carousel_template = CarouselTemplate(columns=[
            CarouselColumn(text=' ', title='生鮮食品', actions=[
                MessageAction(label='生鮮食品', text='生鮮食品')
            ]),
            CarouselColumn(text=' ', title='お潰物・サラダ他-約一人前', actions=[
                MessageAction(label='お潰物・サラダ他 \n 約一人前', text='お潰物・サラダ他-約一人前')
            ]),
            CarouselColumn(text=' ', title='一品物',actions=[
                               MessageAction(label='一品物', text='一品物')
                           ]),
            CarouselColumn(text=' ', title='お惣菜1袋50ｇ-約一人前',actions=[
                               MessageAction(label='お惣菜1袋50ｇ-約一人前', text='お惣菜1袋50ｇ-約一人前')
                           ]),
        ])
        template_message = TemplateSendMessage(
            alt_text='Carousel alt text', template=carousel_template)
        line_bot_api.reply_message(event.reply_token, template_message)

    elif text == '生鮮食品':
        submenu1(event)
    elif text=='一品物':
        submenu2(event)
    elif text == 'お潰物・サラダ他-約一人前':
        submenu3(event)
    elif text == 'お惣菜1袋50ｇ-約一人前':
        submenu4(event)
    elif text == 'お問合せ':
        clearorder(event)
        line_bot_api.reply_message(
            event.reply_token, [
                TextSendMessage(
                    text='・居酒屋「くーろん」 \n・原田商店 \n \n 63 Pham Viet Chanh street.,District Binh Thanh,Ho Chi Minh \n \n TEL：08 3840 9826 \n 携帯：090 829 5470')
            ]
        )
    elif text == 'メニュー':
        url = 'https://comps.gograph.com/japanese-food-icons-set-cartoon-style_gg96256953.jpg'
        app.logger.info("url=" + url)
        line_bot_api.reply_message(
            event.reply_token,
            ImageSendMessage(url, url)
        )
    elif text == '営業時間':
        clearorder(event)
        line_bot_api.reply_message(
            event.reply_token, [
                TextSendMessage(text='【レストラン】 \n月曜日　17:30～23:00 \n火曜日　17:30～23:00 \n水曜日　17:30～23:00 \n木曜日　17:30～23:00 \n金曜日　17:30～23:00 \n土曜日　11:30～23:00 \n日曜日　定休日\n \n 【食材・弁当デリバリー】 \n配達希望日の前日午前3時までの受付になります。 \n食材のみのデリバリーは14時以降の配達です。' ),
            ]
        )
    elif text == 'cancel':
        try :
            tmp2 = tmpordersheet.find(str(event.source.user_id))
            tmpordersheet.delete_row(tmp2.row)
            line_bot_api.reply_message(event.reply_token,
                                       TextSendMessage(text=' Ok-desu ! now you can re-order '))
        except :
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='Add at least 1 item to your cart befor cancel ! idiot '))
    elif text == '完了':
        try:
            tmp = tmpordersheet.find(str(event.source.user_id))
        except:
            tmp = None
        if tmp is None:
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text=' Your cart is empty'))
        else :
            try:
                tmp2 = tmpuserinfo.find(str(event.source.user_id))
                tmpuserinfo.delete_row(tmp2.row)
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text='お名前を教えてください。?'))
                new = [str(event.source.user_id), ""]
                tmpuserinfo.insert_row(new)
            except:
                tmp2 = None
            if tmp2 is None :
                line_bot_api.reply_message(event.reply_token,TextSendMessage(text='お名前を教えてください。?'))
                new = [str(event.source.user_id), ""]
                tmpuserinfo.insert_row(new)
    elif 1==1:
        getUserinfo(event)




import os

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='127.0.0.1', port=port)
