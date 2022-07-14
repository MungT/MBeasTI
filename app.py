#!-- 로그인 영역                                                                            --
import math

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

<<<<<<< HEAD

@app.route('/user')
def user():
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    temp_id = payload['id']
    # print("여기까지는 작동 됩니다!")
    user_info = db.users.find_one({"username": temp_id}, {"_id": False})

    # 변경할 정보 보내주기 ( 닉네임 / 사진 )     속성 : 클래스명
    return render_template('user.html', user_info=user_info)
=======
#---------------------------------------------------------------------------원호[회원정보변경]↓
@app.route('/user')
def user():
    # 각 사용자의 프로필과 글을 모아볼 수 있는 공간
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    user_id = payload["id"]
    user_info = db.users.find_one({"username": user_id}, {"_id": False})
>>>>>>> c3f4c32ea54cc3993b8bd0f1effc269daa3a8977


#---------------------------------------------------------------------------원호[회원정보변경]↑


@app.route('/user_change', methods=['POST'])
def user_change():
    nick_name = request.form['nickname_give']
    user_id = request.form['userid_give']

    db.users.update_one({"username":user_id},{'$set':{'nickname':nick_name}})

    return jsonify({'msg': '수정완료'})
@app.route("/file_upload", methods=["POST"])
def file_upload():
    print("들어오았")
    # if request.method == "POST":
    nick_name = request.form['user_id']
    f = request.files['file']
    fileName = f.filename
    filenameRsplit = fileName.rsplit('.')
    newFileName = filenameRsplit[0]+'_'+ datetime.now().strftime('%Y%m%d%H%M%S%f') +'.'+filenameRsplit[1]

    db.users.update_one({"username":nick_name},{'$set':{'profile_pic_real':secure_filename(newFileName)}})

    f.save('./static/img/'+secure_filename(newFileName))
    return redirect(url_for("index"))
    # else:
    #     return render_template('index.html')

#---------------------------------------------------------------------------원호[회원정보변경]↑


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
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    nickname_receive = request.form['nickname_give']
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    doc = {
        "username": username_receive,  # 아이디
        "password": password_hash,  # 비밀번호
        "nickname": nickname_receive,  # 닉네임
        "profile_name": username_receive,  # 프로필 이름 기본값은 아이디
        "result_mbti": "", # mbti 칸
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
    # 쿠키에서 토큰 꺼내오기
    token_receive = request.cookies.get('mytoken')
    try:
        # 토큰 decode 하기
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        username = payload["id"]
        user_info = db.users.find_one({'username': username}, {'_id': False})
        origin_nickname = user_info['nickname']
        # 클라 nickname / about 저장
        if request.form["nickname_give"] == "":
            nickname_receive = origin_nickname
        else:
            nickname_receive = request.form["nickname_give"]
        about_receive = request.form["about_give"]
        new_doc = {
            "nickname": nickname_receive,
            "profile_info": about_receive
        }

        if 'file_give' in request.files:
            file = request.files["file_give"]
            print(file)
            filename = secure_filename(file.filename)
            print(filename)

            # 사진의 확장자명 ( jpg 등 )
            extension = filename.split(".")[-1]
            print(extension)

            #DB에 저장할 유저명을 붙인 이미지 파일명
            # 접속자 아이디 + 확장자명 ( profile_pics/ + {qwe123}.{jpg} )
            file_path = f"profile_pics/{filename}"
            print(file_path)
            #파일명
            new_doc["profile_pic"] = filename
            #이미지 경로
            new_doc["profile_pic_real"] = file_path

        db.users.update_one({'username': payload['id']}, {'$set': new_doc})
        return jsonify({"result": "success", 'msg': '프로필을 업데이트했습니다.'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


# -------------------------          ----------------------------------------------------

# ------------------------- 원호님 영역 ----------------------------------------------------
@app.route('/result')
def result():
    # 유효성 체크를 합니다
    token_chk()
    # 토큰 가져옵니다
    token_receive = request.cookies.get('mytoken')
    # 디코더를 해서 토큰값의 정보를 추출하려고 합니다.
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    # 토큰을 만들때 사용했던 계정을 추출합니다.
    temp_name = payload["id"]
    # 계정으로 해당유저의 정보를 추출합니다.
    user_info = db.users.find_one({"username": temp_name}, {"_id": False})
    # 유저 정보에서 mbti를 가져옵니다.
    result_mbti = user_info['result_mbti']
    # mbti로 검색해서 보여질 mbti의 정보를 찾습니다.
    user_mbti = db.mbtiComment.find_one({'mc_flag': result_mbti}, {"_id": False})
    print("infos->", user_mbti)
    #                       index로 이동            뿌려질 MBTI의 정보     유저 계정
    return render_template('result.html', mbti_list=user_mbti, user_info=user_info['username'])


# -------------------------          ----------------------------------------------------
# 댓글 작성 하는곳
@app.route('/commentAction', methods=['POST'])
def commentAction():
    # 유효청 체크 함수
    token_chk()

    # 고유번호를 위해 현 시간을 초로 변경
    now = datetime.now()
    comment_receive = request.form['txt']
    user_receive = request.form['user']
    now_mbti = request.form['now_mbti']
    print(comment_receive)

    # -------------------------          ----------------------------------------------------
    doc = {
        'comment_receive': comment_receive,
        'user_name': user_receive,
        'data_time': math.trunc(now.timestamp()),
        'now_mbti': now_mbti
    }
    db.comment.insert_one(doc)
    return jsonify({'msg': '등록완료'})


# -------------------------          ----------------------------------------------------
# 댓글을 들고오는곳
@app.route('/getComment', methods=['GET'])
def getComment():
    token_chk()

    now_mbti = request.args.get('now_mbti')
<<<<<<< HEAD
    print("아아", now_mbti);
    all_comment = list(db.comment.find({'now_mbti': now_mbti}, {'_id': False}))
    # for alls in all_comment:
    #     print(alls)
    print(all_comment)

=======
>>>>>>> c3f4c32ea54cc3993b8bd0f1effc269daa3a8977
    all_comment = list(db.comment.find({'now_mbti':now_mbti},{'_id':False}))
    for alls in all_comment:
        info = db.users.find_one({'username':alls['user_name']})
        img_src=info['profile_pic_real']
        alls['img_src'] = img_src

    return jsonify({'msg': all_comment})


# 댓글 삭제 동작 일어나는곳
@app.route('/commit-del', methods=['POST'])
def commitDel():
    token_chk()

    commentTime = int(request.form['valTime'])
    db.comment.delete_one({'data_time': commentTime})

    return jsonify({'msg': '삭제완료'})


# 수정하기위해 이전 글 가져오는글
@app.route('/commit-up', methods=['POST'])
def commitUp():
    token_chk()
    commentTime = int(request.form['valTime'])
    commit_info = db.comment.find_one({'data_time': commentTime}, {'_id': False})
    return jsonify({'msg': commit_info})


# 수정 동작이 일어나는 곳
@app.route('/commentModify', methods=['POST'])
def commentModify():
    token_chk()

    comment_rece = request.form['txt']
    time_rece = int(request.form['time'])
    db.comment.update_one({'data_time': time_rece}, {'$set': {'comment_receive': comment_rece}})
    return jsonify({'msg': '수정완료'})


# 페이지 이동이나 액션을 취할 때 쿠키값이 있는지 확인을 하는 함수
def token_chk():
    token_receive = request.cookies.get('mytoken')
    try:
        jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


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
def modify_profile():
    return render_template("user.html")


# -------------------------          ----------------------------------------------------


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
