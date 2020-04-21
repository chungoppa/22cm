import time
from collections import Counter
from flask import Flask, request, abort, app
import json
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
questionssheet = mainsheet.worksheet('questionsInOderdelivery')
submenusheet = mainsheet.worksheet('subMenu')
menusheet = mainsheet.worksheet('Menu')
reportReceiver = mainsheet.worksheet('reportReceiver')
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
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='Stop texting dude !'))
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
        else :
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='stop texting dude  。'))
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
def getReportofOrder(event,rowinTmpuserInfo):
    question_list = questionssheet.row_values(2)
    tmpuserinfo_list = tmpuserinfo.row_values(rowinTmpuserInfo)
    getUserInfofromList(question_list,tmpuserinfo_list)
    line_bot_api.reply_message(event.reply_token,TextSendMessage(text=getUserInfofromList(question_list,tmpuserinfo_list),quick_reply=QuickReply(items=[
                QuickReplyButton(
                    action=MessageAction(label="Ok", text="ok")
                ), QuickReplyButton(
                    action=MessageAction(label="Edit", text="edit")
                )])))
def getUserInfofromList(qlist,ulist):
    string = 'Here is your infomation :'
    i=1
    for num in qlist:
        string = '\n'+ string +str(num) +  str(ulist[i])
        i=i+1
    return string
def getpricebyname(name) :
    if name == '天婦羅':
        return 900
    elif name == 'すき焼き':
        return 2000
    elif name =='hamburger':
        return 200
    elif name == 'pizza':
        return 700
def getcarousel():
    carousel ="""{
    "type": "carousel",
    "contents": [
      {
        "type": "bubble",
        "hero": {
          "type": "image",
          "url": "https://haithuycatering.com/image/5c300d9951046d646e172578/original.jpg",
          "size": "full",
          "aspectRatio": "20:13",
          "aspectMode": "cover"
        },
        "body": {
          "type": "box",
          "layout": "vertical",
          "spacing": "sm",
          "contents": [
            {
              "type": "text",
              "text": "天麩羅",
              "size": "xl",
              "weight": "bold",
              "wrap": true
            },
            {
              "type": "box",
              "layout": "baseline",
              "contents": [
                {
                  "type": "text",
                  "text": "¥900",
                  "flex": 0,
                  "size": "xl",
                  "weight": "bold",
                  "wrap": true
                }
              ]
            }
          ]
        },
        "footer": {
          "type": "box",
          "layout": "vertical",
          "spacing": "sm",
          "contents": [
            {
              "type": "button",
              "action": {
                "type": "postback",
                "label": "Add to Cart",
                "data": "1"
              },
              "style": "primary"
            }
          ]
        }
      },
      {
        "type": "bubble",
        "hero": {
          "type": "image",
          "url": "https://product.hstatic.net/1000308381/product/fotolia_130245786_subscription_monthly_m_master.jpg",
          "size": "full",
          "aspectRatio": "20:13",
          "aspectMode": "cover"
        },
        "body": {
          "type": "box",
          "layout": "vertical",
          "spacing": "sm",
          "contents": [
            {
              "type": "text",
              "text": "すき焼き",
              "size": "xl",
              "weight": "bold",
              "wrap": true
            },
            {
              "type": "box",
              "layout": "baseline",
              "contents": [
                {
                  "type": "text",
                  "text": "¥2000",
                  "flex": 0,
                  "size": "xl",
                  "weight": "bold",
                  "wrap": true
                }
              ]
            }
          ]
        },
        "footer": {
          "type": "box",
          "layout": "vertical",
          "spacing": "sm",
          "contents": [
            {
              "type": "button",
              "action": {
                "type": "postback",
                "label": "Add to Cart",
                "data": "2"
              },
              "style": "primary"
            }
          ]
        }
      }
    ]
  }"""
    return carousel
def getcarousel2():
    carousel ="""{
    "type": "carousel",
    "contents": [
      {
        "type": "bubble",
        "hero": {
          "type": "image",
          "url": "https://www.thewholesomedish.com/wp-content/uploads/2019/04/The-Best-Classic-Hamburgers-550.jpg",
          "size": "full",
          "aspectRatio": "20:13",
          "aspectMode": "cover"
        },
        "body": {
          "type": "box",
          "layout": "vertical",
          "spacing": "sm",
          "contents": [
            {
              "type": "text",
              "text": "Hamburger",
              "size": "xl",
              "weight": "bold",
              "wrap": true
            },
            {
              "type": "box",
              "layout": "baseline",
              "contents": [
                {
                  "type": "text",
                  "text": "¥900",
                  "flex": 0,
                  "size": "xl",
                  "weight": "bold",
                  "wrap": true
                }
              ]
            }
          ]
        },
        "footer": {
          "type": "box",
          "layout": "vertical",
          "spacing": "sm",
          "contents": [
            {
              "type": "button",
              "action": {
                "type": "postback",
                "label": "Add to Cart",
                "data": "3"
              },
              "style": "primary"
            }
          ]
        }
      },
      {
        "type": "bubble",
        "hero": {
          "type": "image",
          "url": "https://storage.googleapis.com/phx2-uat-wordpress-uploads/1/2019/03/Fan-Favourite-640x390.jpg",
          "size": "full",
          "aspectRatio": "20:13",
          "aspectMode": "cover"
        },
        "body": {
          "type": "box",
          "layout": "vertical",
          "spacing": "sm",
          "contents": [
            {
              "type": "text",
              "text": "pizza",
              "size": "xl",
              "weight": "bold",
              "wrap": true
            },
            {
              "type": "box",
              "layout": "baseline",
              "contents": [
                {
                  "type": "text",
                  "text": "¥2000",
                  "flex": 0,
                  "size": "xl",
                  "weight": "bold",
                  "wrap": true
                }
              ]
            }
          ]
        },
        "footer": {
          "type": "box",
          "layout": "vertical",
          "spacing": "sm",
          "contents": [
            {
              "type": "button",
              "action": {
                "type": "postback",
                "label": "Add to Cart",
                "data": "4"
              },
              "style": "primary"
            }
          ]
        }
      }
    ]
  }"""
    return carousel
def xxx(event):
    rownum = sheet.row_count
    cell_list = sheet.range('A1:A{}'.format(rownum))
    for cell in cell_list:
        if cell.value == event.source.user_id:
            sheet.delete_row(cell.row)
            renew = [str(event.source.user_id), "", "", "", "", ""]
            sheet.insert_row(renew)
            return
    renew = [str(event.source.user_id), "", "", "", "", ""]
    sheet.insert_row(renew)
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
            CarouselColumn(text='pizza, hamburger , cocacola.....', title='生鮮食品', thumbnail_image_url='https://cache5.amanaimages.com/preview640/11014027918.jpg', actions=[
                MessageAction(label='生鮮食品', text='生鮮食品')
            ]),
            CarouselColumn(text='Makizushi , Miso soup, tempura ....', title='お潰物・サラダ他-約一人前',thumbnail_image_url='https://d18gmz9e98r8v5.cloudfront.net/review/20200301055026_1674288578_9.jpg', actions=[
                MessageAction(label='お潰物・サラダ他 \n 約一人前', text='お潰物・サラダ他-約一人前')
            ]),
            CarouselColumn(text='pizza, hamburger , cocacola.....', title='一品物',thumbnail_image_url='https://geography-vnu.edu.vn/wp-content/uploads/wordpress/b%C3%A0i-lu%E1%BA%ADn-ti%E1%BA%BFng-Anh-v%E1%BB%81-m%C3%B3n-%C4%83n-nhanh.jpg',actions=[
                               MessageAction(label='一品物', text='一品物')
                           ]),
            CarouselColumn(text='Makizushi , Miso soup, tempura ....', title='お漬け物',thumbnail_image_url='https://cdn.macaro-ni.jp/assets/img/shutterstock/shutterstock_305525699.jpg',actions=[
                               MessageAction(label='お漬け物', text='お漬け物')
                           ]),
        ])
        template_message = TemplateSendMessage(
            alt_text='Carousel alt text', template=carousel_template)
        line_bot_api.reply_message(event.reply_token, template_message)
        # getsubmenu(event)
        # bubble = getcarousel()
        # # xxx(event)
        # message = FlexSendMessage(alt_text="hello", contents=json.loads(bubble))
        # line_bot_api.reply_message(
        #     event.reply_token,[
        #     TextSendMessage(text='以下は当社の食材・弁当デリバリーューメニューです。\n注文完了したら、「完了」ボタンを押してください。'),message]
        # )
    elif text == '生鮮食品':
        サンマの開き = request.url_root + '/static/サンマの開き.JPG'
        塩サバ切り身 = request.url_root + '/static/塩サバ切り身.JPG'
        サケ切り身 = request.url_root + '/static/サケ切り身.JPG'
        carousel_template = CarouselTemplate(columns=[
            CarouselColumn(text='Price : 60000 vnd', title='サンマの開き',
                           thumbnail_image_url=サンマの開き, actions=[MessageAction(label='Add To Cart', text='サンマの開き')]),
            CarouselColumn(text='Price : 60000 vnd', title='塩サバ切り身',
                           thumbnail_image_url=塩サバ切り身,actions=[MessageAction(label='Add To Cart', text='塩サバ切り身')]),
            CarouselColumn(text='Price : 60000 vnd', title='サケ切り身',
                           thumbnail_image_url=サケ切り身, actions=[MessageAction(label='Add To Cart', text='サケ切り身')]),
            CarouselColumn(text='Price : 60000 vnd', title='塩サバ切り身',
                           thumbnail_image_url=塩サバ切り身, actions=[MessageAction(label='Add To Cart', text='塩サバ切り身')]),
        ])



        template_message = TemplateSendMessage(
            alt_text='Carousel alt text', template=carousel_template)
        line_bot_api.reply_message(event.reply_token, template_message)
    elif text == 'mainmeal':
        bubble = getcarousel()
        message = FlexSendMessage(alt_text="hello", contents=json.loads(bubble))
        line_bot_api.reply_message(
            event.reply_token,[
            TextSendMessage(text='以下は当社の食材・弁当デリバリーューメニューです。\n注文完了したら、「完了」ボタンを押してください。'),message]
        )
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
    elif text == 'checkout':
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
def getpricebyName(name):
    if name == 'サンマの開き':
        return 60000
    elif name == '塩サバ切り身' :
        return 60000
    elif name == 'サケ切り身' :
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
        return 11000
    elif name == '手作り-冷凍餃子（５個）':
        return 0
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

#  Post back event
@handler.add(PostbackEvent)
def handle_postback(event):
    if event.postback.data == '1':
        addtocart(event,"天婦羅")
        line_bot_api.reply_message(event.reply_token,
                                   TextSendMessage(text='天婦羅カートに追加 ', quick_reply=QuickReply(
                                           items=[
                                               QuickReplyButton(
                                                   action=MessageAction(label="Check out", text="checkout")
                                               )])))
    elif event.postback.data == '2':
        addtocart(event,"すき焼き")
        line_bot_api.reply_message(event.reply_token,
                                   TextSendMessage(text='すき焼きカートに追加', quick_reply=QuickReply(
                                           items=[
                                               QuickReplyButton(
                                                   action=MessageAction(label="Check out", text="checkout")
                                               )])))
    elif event.postback.data == '3':
        addtocart(event, "hamburger")
        line_bot_api.reply_message(event.reply_token,
                                   TextSendMessage(text='Hamburgerカートに追加', quick_reply=QuickReply(
                                       items=[
                                           QuickReplyButton(
                                               action=MessageAction(label="Check out", text="checkout")
                                           )])))
    elif event.postback.data =='4':
        addtocart(event, "pizza")
        line_bot_api.reply_message(event.reply_token,
                                   TextSendMessage(text='Pizzaカートに追加', quick_reply=QuickReply(
                                       items=[
                                           QuickReplyButton(
                                               action=MessageAction(label="Check out", text="checkout")
                                           )])))
import os

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='127.0.0.1', port=port)