#!-- 로그인 영역                                                                            --
from flask import Flask, render_template, jsonify, request, session, redirect, url_for
# JWT 패키지를 사용합니다. (설치해야할 패키지 이름: PyJWT)
import jwt
# 토큰에 만료시간을 줘야하기 때문에, datetime 모듈도 사용합니다.
import datetime
# 회원가입 시엔, 비밀번호를 암호화하여 DB에 저장해두는 게 좋습니다.
# 그렇지 않으면, 개발자(=나)가 회원들의 비밀번호를 볼 수 있으니까요.^^;
import hashlib
# OS가 접근할 환경변수에 키 보관을 위한 패키지 -> python-dotenv 다운
from dotenv import load_dotenv
# 파일 단위를 넘어서 변수를 가져올 수 있는 패키지
import os

# import certifi

from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from pymongo import MongoClient

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = "./static/profile_pics"

# .env 환경 변수 사용
load_dotenv()

# OS를 통해 경로 추적
MONGODB_URL = os.getenv('MONGODB_URL')
# JWT 토큰을 만들 때 필요한 비밀문자열입니다. 아무거나 입력해도 괜찮습니다.
# 이 문자열은 서버만 알고있기 때문에, 내 서버에서만 토큰을 인코딩(=만들기)/디코딩(=풀기) 할 수 있습니다.
SECRET_KEY = os.getenv('SECRET_KEY')

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = "./static/profile_pics"

client = MongoClient(MONGODB_URL)
db = client.M_Beast_I
db = client.MBTI


#################################
##  HTML을 주는 부분             ##
#################################
@app.route('/')
def home():
    # 여기는 토큰의 유효기간만 확인
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))
    # 여기서 MBTI 정보 유무에 따라 result or index 이동 로직
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    user_info = db.users.find_one({"username": payload['id']}, {"_id": False})
    user_mbti = user_info['result_mbti']
    if user_mbti != "":
        return redirect(url_for("result"))
    else:
        return redirect(url_for("index"))




@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)


@app.route('/user/<username>')
def user(username):
    # 각 사용자의 프로필과 글을 모아볼 수 있는 공간
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        status = (username == payload["id"])  # 내 프로필이면 True, 다른 사람 프로필 페이지면 False

        user_info = db.users.find_one({"username": username}, {"_id": False})
        return render_template('user.html', user_info=user_info, status=status)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route('/sign_in', methods=['POST'])
def sign_in():
    # 로그인
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    result = db.users.find_one({'username': username_receive, 'password': pw_hash})

    if result is not None:
        payload = {
            'id': username_receive,
            'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 로그인 24시간 유지
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


# ------------------------- 회원가입 정보 DB에 저장 -----------------------------------------
@app.route('/sign_up/save', methods=['POST'])
def sign_up():
    mbti_receive = request.form['mbti_give']
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    nickname_receive = request.form['nickname_give']
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    doc = {
        "username": username_receive,  # 아이디
        "password": password_hash,  # 비밀번호
        "nickname": nickname_receive,  # 닉네임
        "profile_name": username_receive,  # 프로필 이름 기본값은 아이디
        "result_mbti": mbti_receive, # <- 이 자리가 mbti DB 자리 입니다.
        "profile_pic": "",  # 프로필 사진 파일 이름
        "profile_pic_real": "profile_pics/profile_placeholder.png",  # 프로필 사진 기본 이미지
        "profile_info": ""  # 프로필 한 마디
    }
    db.users.insert_one(doc)
    return jsonify({'result': 'success'})
# ------------------------- MBTI 결과 DB 저장용    --------------------------------------
# 여긴 성공!
## 위에 포스트로는 실패했어요 ...
@app.route('/db_mbti/save', methods=['POST'])
def db_upload():
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    mbti_receive = request.form['mbti_give']

    db.users.update_one({'username': payload['id']}, {'$set': {'result_mbti': mbti_receive}})
    return jsonify({'result': 'success'})





# ------------------------- 중복체크 ----------------------------------------------------
@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    # ID 중복확인
    username_receive = request.form['username_give']
    exists = bool(db.users.find_one({"username": username_receive}))
    return jsonify({'result': 'success', 'exists': exists})


@app.route('/sign_up/check_dup_nick', methods=['POST'])
def check_dup_nick():
    # nick 중복확인
    nickname_receive = request.form['nickname_give']
    checks = bool(db.users.find_one({"nickname": nickname_receive}))
    return jsonify({'result': 'success', 'checks': checks})


# -------------------------          ----------------------------------------------------

@app.route('/update_profile', methods=['POST'])
def save_img():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        # 프로필 업데이트
        return jsonify({"result": "success", 'msg': '프로필을 업데이트했습니다.'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


# -------------------------          ----------------------------------------------------

# ------------------------- 원호님 영역 ----------------------------------------------------
@app.route('/result')
def result():
    return render_template('result.html')


# -------------------------          ----------------------------------------------------

@app.route('/commentAction', methods=['POST'])
def commentAction():
    comment_receive = request.form['txt']
    print(comment_receive)
    doc = {
        'comment_receive': comment_receive
    }
    db.comment.insert_one(doc)
    return jsonify({'msg': '등록완료'})


# -------------------------          ----------------------------------------------------

@app.route('/getComment', methods=['GET'])
def getComment():
    # comment_receive = request.agrs.get['txt']
    all_comment = list(db.comment.find({}, {'_id': False}))
    return jsonify({'msg': all_comment})


# ---------------------------------------------------------------------------------------
# MBTI 검사 관련

@app.route('/index')
def index():
    return render_template("index.html")


@app.route('/index2')
def index2():
    return render_template("index2.html")


@app.route('/index3')
def index3():
    return render_template("index3.html")


@app.route('/index4')
def index4():
    return render_template("index4.html")


@app.route('/index5')
def index5():
    return render_template("index5.html")


# -------------------------  유저 페이지로 이동 ----------------------------------------------------

@app.route('/modified_profile')
def modified_profile():
    return render_template('userpage.html')

# -------------------------  닉네임 가져오기    ----------------------------------------------------

@app.route('/find_nickname', methods=['POST'])
def find_nickname():
    your_nickname = list(db.users.find({}, {'_id': False}))
    return jsonify({'get_nick': your_nickname})


# -------------------------          ----------------------------------------------------


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
