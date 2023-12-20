import firebase_admin
from firebase_admin import credentials, firestore
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

from flask import Flask, render_template, request, make_response, jsonify
from datetime import datetime,timezone, timedelta

import requests, json
from bs4 import BeautifulSoup


app = Flask(__name__)

@app.route("/")
def index():
    homepage = "<h1>楊子青Python網頁2023-12-11</h1>"
    homepage += "<a href=/mis>MIS</a><br>"
    homepage += "<a href=/today>顯示日期時間</a><br>"
    homepage += "<a href=/welcome?nick=楊子青>傳送使用者暱稱</a><br>"
    homepage += "<a href=/about>子青簡介網頁</a><br>"
    homepage += "<a href=/account>網頁表單輸入帳密傳值</a><br><br>"
    homepage += "<a href=/read>人選之人演員</a><br>"
    homepage += "<a href=/search>根據角色查詢演員</a><br><br>"
    homepage += "<a href=/books>精選圖書列表</a><br>"
    homepage += "<a href=/query>書名查詢</a><br><br>"
    homepage += "<a href=/spider>網路爬蟲抓取子青老師課程</a><br>"

    homepage += "<br><a href=/spider_movie>讀取開眼電影即將上映影片，寫入Firestore</a><br>"
    homepage += "<a href=/search_movie>查詢開眼電影即將上映影片</a><br>"

    homepage += "<br><a href=/movie_rate>讀取開眼電影即將上映影片(含分級資訊)，寫入Firestore</a><br>"
    homepage += "<br><a href=/movieBot>電影聊天機器人</a><br>"
    return homepage

@app.route("/mis")
def course():
    return "<h1>資訊管理導論</h1>"

@app.route("/today")
def today():
    tz = timezone(timedelta(hours=+8))
    now = datetime.now(tz)
    return render_template("today.html",datetime = str(now))

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/welcome", methods=["GET", "POST"])
def welcome():
    user = request.values.get("nick")
    return render_template("welcome.html", name=user)

@app.route("/account", methods=["GET", "POST"])
def account():
    if request.method == "POST":
        user = request.form["user"]
        pwd = request.form["pwd"]
        result = "您輸入的帳號是：" + user + "; 密碼為：" + pwd 
        return result
    else:
        return render_template("account.html")


@app.route("/read")
def read():
    Result = ""
    db = firestore.client()
    collection_ref = db.collection("人選之人─造浪者")    
    docs = collection_ref.get()    
    for doc in docs:         
        Result += "文件內容：{}".format(doc.to_dict()) + "<br>"    
    return Result


@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        keyword = request.form["keyword"]
        Result = "您輸入的角色關鍵字是：" + keyword + "，查詢結果如下：<br><br>"
        db = firestore.client()
        collection_ref = db.collection("人選之人─造浪者")    
        docs = collection_ref.order_by("birth").get()    
        for doc in docs:
            x = doc.to_dict()
            if keyword in x["role"]:    
                Result += x["name"] + "在劇中扮演" + x["role"] + "，出生於西元" + str(x["birth"]) + "<br>" 
        return Result
    else:
        return render_template("cond.html")

@app.route("/books1")
def books1():
    Result = ""
    db = firestore.client()
    collection_ref = db.collection("圖書精選")    
    docs = collection_ref.order_by("anniversary").get()    
    for doc in docs:
        bk = doc.to_dict()
        Result += "書名：<a href=" + bk["url"] + ">" + bk["title"] + "</a><br>"
        Result += "作者：" + bk["author"] + "<br>"
        Result += str(bk["anniversary"]) + "週年<br>"
        Result += "<img src=" + bk["cover"] + "></img><br><br>" 
    return Result

@app.route("/books")
def books():
    Result = ""
    db = firestore.client()
    collection_ref = db.collection("圖書精選")    
    docs = collection_ref.get()    
    for doc in docs:
        bk = doc.to_dict()        
        Result += "書名：<a href=" + bk["url"] + ">" + bk["title"] + "</a><br>"  
        Result += "作者：" + bk["author"] + "<br>" 
        Result += str(bk["anniversary"]) + "週年紀念版<br>"
        Result += "<img src=" + bk["cover"] + "> </img><br><br>"  
    return Result


@app.route("/query", methods=["GET", "POST"])
def query():
    if request.method == "POST":
        keyword = request.form["keyword"]
        result = "您輸入的關鍵字是：" + keyword

        Result = ""
        db = firestore.client()
        collection_ref = db.collection("圖書精選")    
        docs = collection_ref.get()    
        for doc in docs:
            bk = doc.to_dict()
            if keyword in bk["title"]:       
                Result += "書名：<a href=" + bk["url"] + ">" + bk["title"] + "</a><br>"  
                Result += "作者：" + bk["author"] + "<br>" 
                Result += str(bk["anniversary"]) + "週年紀念版<br>"
                Result += "<img src=" + bk["cover"] + "> </img><br><br>" 
        return Result
    else:
        return render_template("searchbk.html")

@app.route("/lucky", methods=["GET", "POST"])
def lucky():
    if request.method == "POST":
        name = request.form["name"]
        number = request.form["number"]
        lucky = request.form["lucky"]
        result = "您的姓名是：" + name + "，學號為：" + number + "，幸運數字是:" + lucky
        result += "<br><br><a href=/>返回首頁</a>"

        db = firestore.client()

        doc = {
          "name": name,
          "number": number,
          "lucky": int(lucky)
        }

        doc_ref = db.collection("幸運兒").document(number)
        doc_ref.set(doc)
      
        return result
    else:
        return render_template("lucky.html")


@app.route("/answer", methods=["POST","GET"])
def answer():
    info = "根據lucky由小排到大，依序為："
    db = firestore.client()     
    collection_ref = db.collection("幸運兒")
    docs = collection_ref.order_by("lucky").get()
    score = 0
    count = 0
    winner = ""
    for doc in docs:
        x = doc.to_dict()
        if x["lucky"] != score:
            score = x["lucky"]
            info += "<br>" + str(score) + ": "
            if winner ==  "":
                winner = x["name"]
            count = 1
        else:
            winner = ""
            count += 1

        info += " " + x["name"]

    if winner != "":
        info += "<br><br>贏家是：" + winner
    else:
        info += "<br><br>本次沒有贏家" 
    return info


@app.route("/spider")
def spider():
    url = "https://www1.pu.edu.tw/~tcyang/course.html"
    Data = requests.get(url)
    Data.encoding = "utf-8"
    sp = BeautifulSoup(Data.text, "html.parser")
    result=sp.select(".team-box")
    info = ""
    for x in result:
        info += "<a href=" + x.find("a").get("href") + ">" + x.text + "</a><br>"
        info += x.find("a").get("href") + "<br>"
        info += "<img src=https://www1.pu.edu.tw/~tcyang/" + x.find("img").get("src") + " width=330 height=400></img><br><br>"
    return info



@app.route("/spider_movie")
def spider_movie():
    url = "http://www.atmovies.com.tw/movie/next/"
    Data = requests.get(url)
    Data.encoding = "utf-8"
    sp = BeautifulSoup(Data.text, "html.parser")
    result=sp.select(".filmListAllX li")
    lastUpdate = sp.find("div", class_="smaller09").text[5:]

    for item in result:
        picture = item.find("img").get("src").replace(" ", "")
        title = item.find("div", class_="filmtitle").text
        movie_id = item.find("div", class_="filmtitle").find("a").get("href").replace("/", "").replace("movie", "")
        hyperlink = "http://www.atmovies.com.tw" + item.find("div", class_="filmtitle").find("a").get("href")
        show = item.find("div", class_="runtime").text.replace("上映日期：", "")
        show = show.replace("片長：", "")
        show = show.replace("分", "")    
        showDate = show[0:10]
        showLength = show[13:]

        doc = {
            "title": title,
            "picture": picture,
            "hyperlink": hyperlink,
            "showDate": showDate,
            "showLength": showLength,
            "lastUpdate": lastUpdate
        }

        db = firestore.client()
        doc_ref = db.collection("電影").document(movie_id)
        doc_ref.set(doc)    
    return "近期上映電影已爬蟲及存檔完畢，網站最近更新日期為：" + lastUpdate 


@app.route("/search_movie", methods=["POST","GET"])
def ssearch_movie():
    if request.method == "POST":
        MovieTitle = request.form["MovieTitle"]
        info = ""
        db = firestore.client()
        collection_ref = db.collection("電影")
        docs = collection_ref.order_by("showDate").get()
        for doc in docs:
            if MovieTitle in doc.to_dict()["title"]:
                info += "片名：" + doc.to_dict()["title"] + "<br>"
                info += "影片介紹：<a href=" + doc.to_dict()["hyperlink"] + ">" + doc.to_dict()["hyperlink"] + "</a><br>"
                info += "片長：" + doc.to_dict()["showLength"] + " 分鐘<br>"
                info += "上映日期：" + doc.to_dict()["showDate"] + "<br><br>"
        return info
    else:  
        return render_template("input.html")


@app.route("/movie_rate")
def movie_rate():
    url = "http://www.atmovies.com.tw/movie/next/"
    Data = requests.get(url)
    Data.encoding = "utf-8"
    sp = BeautifulSoup(Data.text, "html.parser")
    result=sp.select(".filmListAllX li")
    lastUpdate = sp.find(class_="smaller09").text[5:]

    for x in result:
        picture = x.find("img").get("src").replace(" ", "")
        title = x.find("img").get("alt")    
        movie_id = x.find("div", class_="filmtitle").find("a").get("href").replace("/", "").replace("movie", "")
        hyperlink = "http://www.atmovies.com.tw" + x.find("a").get("href")

        t = x.find(class_="runtime").text
        showDate = t[5:15]

        showLength = ""
        if "片長" in t:
            t1 = t.find("片長")
            t2 = t.find("分")
            showLength = t[t1+3:t2]

        r = x.find(class_="runtime").find("img")
        rate = ""
        if r != None:
            rr = r.get("src").replace("/images/cer_", "").replace(".gif", "")
            if rr == "G":
                rate = "普遍級"
            elif rr == "P":
                rate = "保護級"
            elif rr == "F2":
                rate = "輔12級"
            elif rr == "F5":
                rate = "輔15級"
            else:
                rate = "限制級"

        doc = {
            "title": title,
            "picture": picture,
            "hyperlink": hyperlink,
            "showDate": showDate,
            "showLength": showLength,
            "rate": rate,
            "lastUpdate": lastUpdate
        }

        db = firestore.client()
        doc_ref = db.collection("電影含分級").document(movie_id)
        doc_ref.set(doc)
    return "近期上映電影已爬蟲及存檔完畢，網站最近更新日期為：" + lastUpdate


@app.route("/webhook", methods=["POST"])
def webhook():
    # build a request object
    req = request.get_json(force=True)
    # fetch queryResult from json
    action =  req["queryResult"]["action"]
    msg =  req["queryResult"]["queryText"]
    info = "動作：" + action + "； 查詢內容：" + msg
    return make_response(jsonify({"fulfillmentText": info}))



@app.route("/webhook2", methods=["POST"])
def webhook2():
    # build a request object
    req = request.get_json(force=True)
    # fetch queryResult from json
    action =  req["queryResult"]["action"]
    #msg =  req["queryResult"]["queryText"]
    #info = "動作：" + action + "； 查詢內容：" + msg
    if (action == "rateChoice"):
        rate =  req["queryResult"]["parameters"]["rate"]
        info = "您選擇的電影分級是：" + rate
    return make_response(jsonify({"fulfillmentText": info}))


@app.route("/webhook3", methods=["POST"])
def webhook3():
    # build a request object
    req = request.get_json(force=True)
    # fetch queryResult from json
    action =  req["queryResult"]["action"]
    #msg =  req["queryResult"]["queryText"]
    #info = "動作：" + action + "； 查詢內容：" + msg
    if (action == "rateChoice"):
        rate =  req["queryResult"]["parameters"]["rate"]
        info = "我是楊子青開發的電影聊天機器人,您選擇的電影分級是：" + rate + "，相關電影：\n"

        db = firestore.client()
        collection_ref = db.collection("電影含分級")
        docs = collection_ref.get()
        result = ""
        for doc in docs:
            dict = doc.to_dict()
            if rate in dict["rate"]:
                result += "片名：" + dict["title"] + "\n"
                result += "介紹：" + dict["hyperlink"] + "\n\n"
        info += result
    return make_response(jsonify({"fulfillmentText": info}))


@app.route("/movieBot")
def movieBot():
    return render_template("Movie.html")



@app.route("/AI")
def AI():
    #openai.api_key = os.getenv("OPENAI_API_KEY")
    openai.api_key = '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'
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt="靜宜大學資管系楊子青老師在獲獎方面？",
        max_tokens=128,
        temperature=0.5,
    )
    msg = response.choices[0].text
    return msg



@app.route("/chatgpt")
def chatgpt():
    openai.api_key = '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'
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt="靜宜大學資管系楊子青老師在獲獎方面？",
        max_tokens=128,
        temperature=0.5,
    )
    msg = response.choices[0].text
    return msg

@app.route("/webhook4", methods=["POST"])
def webhook4():
    req = request.get_json(force=True)
    action =  req["queryResult"]["action"]
    if (action == "rateChoice"):
        rate =  req["queryResult"]["parameters"]["rate"]
        info = "我是楊子青開發的電影聊天機器人，您選擇的電影分級是：" + rate + "，相關電影：\n"

        db = firestore.client()
        collection_ref = db.collection("電影含分級")
        docs = collection_ref.get()
        result = ""
        for doc in docs:
            dict = doc.to_dict()
            if rate in dict["rate"]:
                result += "片名：" + dict["title"] + "\n"
                result += "介紹：" + dict["hyperlink"] + "\n\n"
        info += result
    elif (action == "MovieDetail"):
        question =  req.get("queryResult").get("parameters").get("filmq")
        keyword =  req.get("queryResult").get("parameters").get("any")
        info = "我是楊子青開發的電影聊天機器人，您要查詢電影的" + question + "，關鍵字是：" + keyword + "\n\n"
    return make_response(jsonify({"fulfillmentText": info}))

@app.route("/webhook5", methods=["POST"])
def webhook5():
    req = request.get_json(force=True)
    action =  req["queryResult"]["action"]
    if (action == "rateChoice"):
        rate =  req["queryResult"]["parameters"]["rate"]
        info = "我是楊子青開發的電影聊天機器人，您選擇的電影分級是：" + rate + "，相關電影：\n"

        db = firestore.client()
        collection_ref = db.collection("電影含分級")
        docs = collection_ref.get()
        result = ""
        for doc in docs:
            dict = doc.to_dict()
            if rate in dict["rate"]:
                result += "片名：" + dict["title"] + "\n"
                result += "介紹：" + dict["hyperlink"] + "\n\n"
        info += result
    elif (action == "MovieDetail"):
        question =  req.get("queryResult").get("parameters").get("filmq")
        keyword =  req.get("queryResult").get("parameters").get("any")
        info = "我是楊子青開發的電影聊天機器人，您要查詢電影的" + question + "，關鍵字是：" + keyword + "\n\n"

        if (question == "片名"):
            db = firestore.client()
            collection_ref = db.collection("電影含分級")
            docs = collection_ref.get()
            found = False
            for doc in docs:
                dict = doc.to_dict()
                if keyword in dict["title"]:
                    found = True 
                    info += "片名：" + dict["title"] + "\n"
                    info += "海報：" + dict["picture"] + "\n"
                    info += "影片介紹：" + dict["hyperlink"] + "\n"
                    info += "片長：" + dict["showLength"] + " 分鐘\n"
                    info += "分級：" + dict["rate"] + "\n" 
                    info += "上映日期：" + dict["showDate"] + "\n\n"
            if not found:
                info += "很抱歉，目前無符合這個關鍵字的相關電影喔"
    return make_response(jsonify({"fulfillmentText": info}))


@app.route("/webhook6", methods=["POST"])
def webhook6():
    req = request.get_json(force=True)
    action =  req["queryResult"]["action"]
    if (action == "rateChoice"):
        rate =  req["queryResult"]["parameters"]["rate"]
        info = "我是楊子青開發的電影聊天機器人，您選擇的電影分級是：" + rate + "，相關電影：\n"

        db = firestore.client()
        collection_ref = db.collection("電影含分級")
        docs = collection_ref.get()
        result = ""
        for doc in docs:
            dict = doc.to_dict()
            if rate in dict["rate"]:
                result += "片名：" + dict["title"] + "\n"
                result += "介紹：" + dict["hyperlink"] + "\n\n"
        info += result
    elif (action == "MovieDetail"):
        question =  req.get("queryResult").get("parameters").get("filmq")
        keyword =  req.get("queryResult").get("parameters").get("any")
        info = "我是楊子青開發的電影聊天機器人，您要查詢電影的" + question + "，關鍵字是：" + keyword + "\n\n"

        if (question == "片名"):
            db = firestore.client()
            collection_ref = db.collection("電影含分級")
            docs = collection_ref.get()
            found = False
            for doc in docs:
                dict = doc.to_dict()
                if keyword in dict["title"]:
                    found = True 
                    info += "片名：" + dict["title"] + "\n"
                    info += "海報：" + dict["picture"] + "\n"
                    info += "影片介紹：" + dict["hyperlink"] + "\n"
                    info += "片長：" + dict["showLength"] + " 分鐘\n"
                    info += "分級：" + dict["rate"] + "\n" 
                    info += "上映日期：" + dict["showDate"] + "\n\n"
            if not found:
                info += "很抱歉，目前無符合這個關鍵字的相關電影喔"

    elif (action == "Weather"):
        city =  req.get("queryResult").get("parameters").get("city")
        info = "為您查詢 " + city + " 最近36小時的天氣\n\n"

        token = "rdec-key-123-45678-011121314"
        url = "https://opendata.cwb.gov.tw/api/v1/rest/datastore/F-C0032-001?Authorization=" + token + "&format=JSON&locationName=" + str(city)
        Data = requests.get(url)

        sTime = json.loads(Data.text)["records"]["location"][0]["weatherElement"][0]["time"][0]["startTime"]
        eTime = json.loads(Data.text)["records"]["location"][0]["weatherElement"][0]["time"][0]["endTime"]
        Weather = json.loads(Data.text)["records"]["location"][0]["weatherElement"][0]["time"][0]["parameter"]["parameterName"]
        Rain = json.loads(Data.text)["records"]["location"][0]["weatherElement"][1]["time"][0]["parameter"]["parameterName"]
        Min = json.loads(Data.text)["records"]["location"][0]["weatherElement"][2]["time"][0]["parameter"]["parameterName"]
        Max = json.loads(Data.text)["records"]["location"][0]["weatherElement"][4]["time"][0]["parameter"]["parameterName"]
        CT = json.loads(Data.text)["records"]["location"][0]["weatherElement"][3]["time"][0]["parameter"]["parameterName"]
        info += sTime + "～" + eTime + "\n"
        info += Weather + "，降雨機率：" + str(Rain) + "%" + "，氣溫：" + str(Min) + "～" + str(Max) + "度，" + CT + "\n\n"


        sTime = json.loads(Data.text)["records"]["location"][0]["weatherElement"][0]["time"][1]["startTime"]
        eTime = json.loads(Data.text)["records"]["location"][0]["weatherElement"][0]["time"][1]["endTime"]
        Weather = json.loads(Data.text)["records"]["location"][0]["weatherElement"][0]["time"][1]["parameter"]["parameterName"]
        Rain = json.loads(Data.text)["records"]["location"][0]["weatherElement"][1]["time"][1]["parameter"]["parameterName"]
        Min = json.loads(Data.text)["records"]["location"][0]["weatherElement"][2]["time"][1]["parameter"]["parameterName"]
        Max = json.loads(Data.text)["records"]["location"][0]["weatherElement"][4]["time"][1]["parameter"]["parameterName"]
        CT = json.loads(Data.text)["records"]["location"][0]["weatherElement"][3]["time"][1]["parameter"]["parameterName"]
        info += sTime + "～" + eTime + "\n"
        info += Weather + "，降雨機率：" + str(Rain) + "%" + "，氣溫：" + str(Min) + "～" + str(Max) + "度，" + CT + "\n\n"

        sTime = json.loads(Data.text)["records"]["location"][0]["weatherElement"][0]["time"][2]["startTime"]
        eTime = json.loads(Data.text)["records"]["location"][0]["weatherElement"][0]["time"][2]["endTime"]
        Weather = json.loads(Data.text)["records"]["location"][0]["weatherElement"][0]["time"][2]["parameter"]["parameterName"]
        Rain = json.loads(Data.text)["records"]["location"][0]["weatherElement"][1]["time"][2]["parameter"]["parameterName"]
        Min = json.loads(Data.text)["records"]["location"][0]["weatherElement"][2]["time"][2]["parameter"]["parameterName"]
        Max = json.loads(Data.text)["records"]["location"][0]["weatherElement"][4]["time"][2]["parameter"]["parameterName"]
        CT = json.loads(Data.text)["records"]["location"][0]["weatherElement"][3]["time"][2]["parameter"]["parameterName"]
        info += sTime + "～" + eTime + "\n"
        info += Weather + "，降雨機率：" + str(Rain) + "%" + "，氣溫：" + str(Min) + "～" + str(Max) + "度，" + CT

    return make_response(jsonify({"fulfillmentText": info}))


if __name__ == "__main__":
    app.run(debug=True)