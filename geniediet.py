
# %%
from ppadb.client import Client
import cv2
import numpy as np
from numpy import random
import datetime
import time
import requests
import os



# %%
def connect():
    client = Client(host='127.0.0.1', port=5037) # Default is "127.0.0.1" and 5037
    devices = client.devices()

    if len(devices) == 0:
        print('No devices')
        quit()

    device = devices[0]
    print(f'Connected to {device}')
    return device, client

device, client = connect()




#%%
def save_cap(name):
    '''
    현재화면 캡처해서 png파일로 저장하는 함수
    name 형식 : folder이름_img이름 ex) apptech_abc 
    '''
    app_title = name[:name.find('_')]
    img_byte = device.screencap()
    img = cv2.imdecode(np.frombuffer(img_byte,np.uint8), flags=-1)
    img = img[:,:,:3] # alpha channel 제거
    if app_title not in os.listdir('./'):
        os.makedirs(app_title, exist_ok=True)
    cv2.imwrite('./' + app_title + '/'+ name + '.png',img)

save_cap('geniediet_1')
# %%

#전체화면 capture 함수정의
def capture():
    img_byte = device.screencap()
    img = cv2.imdecode(np.frombuffer(img_byte,np.uint8), flags=-1)
    img = img[:,:,:3]
    return img

# ★ search함수 
def search(img,name,threshold=0.8):
    '''
    img = 현재화면 캡처
    name = 비교할 이미지 (미리 저장해놓은 file)
    threshold = 일치율 지정 ( 기본 0.8 )
    '''
    templ = cv2.imread('./'+ name[:name.find('_')]+ '/'+ name + '_template.png', cv2.IMREAD_COLOR)
    # img = cv2.resize(img,dsize=None,fx=0.4,fy=0.4)
    # templ = cv2.resize(templ,dsize=None,fx=0.4,fy=0.4)
    res = cv2.matchTemplate(img,templ,cv2.TM_CCOEFF_NORMED)
    threshold = threshold
    loc = np.where(res >= threshold)
    ziloc = list(zip(*loc[::-1]))
    return ziloc

# 저장해논 사진 범위 내로 임의 클릭/ picture_click 함수와 사용
def random_click_picture(x1,y1,w,h):
    new_x = random.randint(x1,x1+int(w))
    new_y = random.randint(y1,y1+int(h))
    delay = random.randint(50,111)  
    device.input_swipe(new_x,new_y,new_x,new_y,delay)

# ★ picture click 
def picture_click(img,name):
    '''
    현재화면(img) 과 template(name) 비교해서,
    일치하는 이미지 있으면 클릭한다.
    '''
    ziloc = search(img,name)
    basic_template = cv2.imread('./'+ name[:name.find('_')]+ '/'+ name + '_template.png', cv2.IMREAD_COLOR)
    h, w = basic_template.shape[:-1]
    x1 = ziloc[0][0]
    y1 = ziloc[0][1]
    random_click_picture(x1, y1, w, h)
    print(f'click {name}')

def picture_click_byrate(img,name,threshold):
    '''
    현재화면(img) 과 template(name) 비교해서,
    일치하는 이미지 있으면 클릭한다.
    '''
    ziloc = search(img,name,threshold)
    basic_template = cv2.imread('./'+ name[:name.find('_')]+ '/'+ name + '_template.png', cv2.IMREAD_COLOR)
    h, w = basic_template.shape[:-1]
    x1 = ziloc[0][0]
    y1 = ziloc[0][1]
    random_click_picture(x1, y1, w, h)
    print(f'click {name}')

def searchandclick(name,waitingtime):
    '''
    클릭 후 화면 바뀌는 경우가 자주 있어서, searchandclick 함수 생성
    screenshot → 이미지(name)찾기 → click → 이미지 사라졌는지 check
    watingtime = click후 대기 시간 지정
    
    '''
    for i in range(10):
        img = capture()
        if len(search(img,name))>0 :
            picture_click(img,name)
            time.sleep(waitingtime)
            img = capture()
            if len(search(img,name)) == 0 :
                break

#사진 일치율 수정(이미지가 반응하여 약간만 변하는 경우에 사용)
def searchandclick_byrate(name,waitingtime,threshold):
    '''
    클릭 후 화면 바뀌는 경우가 자주 있어서, searchandclick 함수 생성
    screenshot → 이미지(name)찾기 → click → 이미지 사라졌는지 check
    watingtime = click후 대기 시간 지정
    
    '''
    for i in range(10):
        img = capture()
        if len(search(img,name,threshold))>0 :
            picture_click_byrate(img,name,threshold)
            time.sleep(waitingtime)
            img = capture()
            if len(search(img,name,threshold)) == 0 :
                break

#이미지가 안사라지는 경우 10번까지는 안돌리고 2번만 돌리자

def searchandclick_twice(name,waitingtime):
    '''
    클릭 후 화면 바뀌는 경우가 자주 있어서, searchandclick 함수 생성
    screenshot → 이미지(name)찾기 → click → 이미지 사라졌는지 check
    watingtime = click후 대기 시간 지정
    
    '''
    for i in range(2):
        img = capture()
        if len(search(img,name))>0 :
            picture_click(img,name)
            time.sleep(waitingtime)
            img = capture()
            if len(search(img,name)) == 0 :
                break

#part-search-and click function

#사진의 특정 위치를 클릭/ 사진을 왼쪽 위부터 순서대로 총 16개(0-15)로 분할 어디를 클릭할지 숫자로 기입
def part_click_picture(x1,y1,w,h,position):
    position = position
    new_x = random.randint(x1+int(((position%4)*w/4)),x1+int(((position%4)+1)*w/4))
    new_y = random.randint(y1+int((int(position/4)*h/4)),y1+int(((int(position/4)+1)*h/4)))
    delay = random.randint(50,111)  
    device.input_swipe(new_x,new_y,new_x,new_y,delay)

#사진의 특정 위치를 클릭/ 사진을 왼쪽 위부터 순서대로 총 16개(0-15)로 분할 하는 part_click_picture를 쓴 함수들.
def picture_click_position(img,name,position):
    '''
    현재화면(img) 과 template(name) 비교해서,
    일치하는 이미지 있으면 클릭한다. 다만 그 클릭하는 위치를 설정한다.
    '''
    position=position
    ziloc = search(img,name)
    basic_template = cv2.imread('./'+ name[:name.find('_')]+ '/'+ name + '_template.png', cv2.IMREAD_COLOR)
    h, w = basic_template.shape[:-1]
    x1 = ziloc[0][0]
    y1 = ziloc[0][1]
    part_click_picture(x1, y1, w, h, position)
    print(f'click {position} 번쨰 part of {name}')

#사진의 특정 위치를 클릭/ 사진을 왼쪽 위부터 순서대로 총 16개(0-15)로 분할
def searchandclick_byposition(name,waitingtime,position=6):
    '''
    클릭 후 화면 바뀌는 경우가 자주 있어서, searchandclick 함수 생성
    screenshot → 이미지(name)찾기 → click → 이미지 사라졌는지 check
    watingtime = click후 대기 시간 지정
    
    '''
    for i in range(10):
        img = capture()
        if len(search(img,name))>0 :
            picture_click_position(img,name,position)
            time.sleep(waitingtime)
            img = capture()
            if len(search(img,name)) == 0 :
                break

def searchandclick_byposition_twice(name,waitingtime,position=6):
    '''
    클릭 후 화면 바뀌는 경우가 자주 있어서, searchandclick 함수 생성
    screenshot → 이미지(name)찾기 → click → 이미지 사라졌는지 check
    watingtime = click후 대기 시간 지정
    
    '''
    for i in range(2):
        img = capture()
        if len(search(img,name))>0 :
            picture_click_position(img,name,position)
            time.sleep(waitingtime)
            img = capture()
            if len(search(img,name)) == 0 :
                break
# %%
waitingtime = 3

# %%
device.input_keyevent('KEYCODE_SLEEP')
# %%
device.input_keyevent('KEYCODE_WAKEUP')
# %%
device.input_keyevent('KEYCODE_HOME')
# # %%
# device.input_keyevent('KEYCODE_BACK')
# %%
# 앱실행
searchandclick('geniediet_1',3)
time.sleep(waitingtime)

# %%
#광고끄기
searchandclick('geniediet_ad1',3)
time.sleep(waitingtime)

# %%
#기록
searchandclick('geniediet_write',3)
time.sleep(waitingtime)

# %% 
# 달력 접기
searchandclick_byrate('geniediet_calenderfold',3,0.9)
time.sleep(waitingtime)


# ##### 체중부분 #################################

# %% 
# 체중+버튼
searchandclick_byposition('geniediet_weight',3,15)
time.sleep(waitingtime)

# %%

# 체중 스와이프하기 ##이미지서치 후  있으면 스와이프 하도록 바꾸자
today=datetime.date.today()

if today.day % 2 == 0:
    device.input_swipe(540,858,600,858,500)
# 날짜별로 다르게 설정해서 계속 움직이지만 결국 원래대로 돌아오도록 스와이프하기 31일이 들어간 달에면 조금 변하겟네
else:
    device.input_swipe(600,858,540,858,500)

# %% 
# 체중 진행
searchandclick('geniediet_weight2',3)
time.sleep(waitingtime)

# %% 
# 체중 진행/ 포인트 닫기버튼
searchandclick('geniediet_pointclose',3)
time.sleep(waitingtime)

# %% 
# 체중 진행/ 확인버튼
searchandclick('geniediet_ok',3)
time.sleep(waitingtime)


# ##### 인바디부분 ##################################
# %% 
# 인바디 클릭
searchandclick_byposition('geniediet_inbody',3, 15)
time.sleep(waitingtime)

# %% 
# 인바디 데이터입력 클릭
searchandclick('geniediet_inbodyinputdata',3)
time.sleep(waitingtime)

# %% 
# 인바디 체중부터 단백질까지 입력
searchandclick_byposition_twice('geniediet_inbodyinputweight',3,7)
time.sleep(waitingtime)

#%%
#체중70
device.input_keyevent(14,1)
device.input_keyevent(0,1)
device.input_keyevent(66,1)
#체지방량20
device.input_keyevent(9,1)
device.input_keyevent(0,1)
device.input_keyevent(66,1)
#골격근량30
device.input_keyevent(10,1)
device.input_keyevent(0,1)
device.input_keyevent(66,1)
#체수분35
device.input_keyevent(10,1)
device.input_keyevent(12,1)
device.input_keyevent(66,1)
#단백질10
device.input_keyevent(10,1)
device.input_keyevent(0,1)
#뒤로가기 키로 숫자패드내림
device.input_keyevent('KEYCODE_BACK')
#결과보기 클릭
# %%
# 인바디 결과보기 클릭
searchandclick('geniediet_inbodyresult',3)
time.sleep(waitingtime)

# %% 
# 인바디부분 포인트 닫기버튼
searchandclick('geniediet_pointclose',3)
time.sleep(waitingtime)
# %%
#뒤로가기 키로 원래 자리로
device.input_keyevent('KEYCODE_BACK')

#  %%
# 스와이프해서 아래로 내리기
device.input_swipe(0,1000,0,0,1000)


# #물 부분

# # %% 
# # 물 +버튼 클릭
# searchandclick_twice('geniediet_waterplus',3)
# time.sleep(waitingtime)




# #####식단부분################################



#%%
# 아침부분 클릭
searchandclick_byposition('geniediet_foodmain',3,0)
time.sleep(waitingtime)
#단식했어요
searchandclick_byrate('geniediet_foodnoeat',3,0.9)
time.sleep(waitingtime)
#저장
searchandclick('geniediet_foodsave',3)
time.sleep(waitingtime)
#포인트닫기(조금다른지0.6으로 설정해야만 먹힘 0.8로는 인식못하나봄)
searchandclick_byrate('geniediet_pointclose',3,0.6)
time.sleep(waitingtime)
#뒤로가기 키로 원래 자리로
device.input_keyevent('KEYCODE_BACK')
device.input_keyevent('KEYCODE_BACK')


# %%
# 점심부분 클릭-아침을 입력하고나면 사진이 바뀌어서 2로 또 설정..
searchandclick_byposition('geniediet_foodmain2',3,1)
time.sleep(waitingtime)
#단식했어요
searchandclick_byrate('geniediet_foodnoeat',3,0.9)
time.sleep(waitingtime)
#저장
searchandclick('geniediet_foodsave',3)
time.sleep(waitingtime)
#포인트닫기(조금다른지0.6으로 설정해야만 먹힘 0.8로는 인식못하나봄)
searchandclick_byrate('geniediet_pointclose',3,0.6)
time.sleep(waitingtime)
#뒤로가기 키로 원래 자리로
device.input_keyevent('KEYCODE_BACK')
device.input_keyevent('KEYCODE_BACK')




# %%
# 저녁부분 클릭
searchandclick_byposition('geniediet_foodmain3',3,3)
time.sleep(waitingtime)
#단식했어요
searchandclick_byrate('geniediet_foodnoeat',3,0.9)
time.sleep(waitingtime)
#저장
searchandclick('geniediet_foodsave',3)
time.sleep(waitingtime)
#포인트닫기(조금다른지0.6으로 설정해야만 먹힘 0.8로는 인식못하나봄)
searchandclick_byrate('geniediet_pointclose',3,0.6)
time.sleep(waitingtime)
#뒤로가기 키로 원래 자리로
device.input_keyevent('KEYCODE_BACK')
device.input_keyevent('KEYCODE_BACK')

#  %%
# 스와이프해서 아래로 내리기
device.input_swipe(0,1000,0,0,1000)




# #####눈바디부분################################



# #%%
# #정면


# searchandclick('geniediet_eyebodyfront',3)
# time.sleep(waitingtime)
# #%%
# searchandclick('geniediet_eyebody2',3)
# time.sleep(waitingtime)
# #%%
# searchandclick('geniediet_eyebodypictureclick1',3)
# time.sleep(waitingtime)
# #%%
# #갤러리에서 내사진클릭
# searchandclick_byrate('geniediet_eyebodypictureclickfront',3,0.9)
# time.sleep(waitingtime)
# #%%
# #등록클릭
# searchandclick('geniediet_eyebodyok',3)
# time.sleep(waitingtime)
# #%%
# #저장클릭
# searchandclick('geniediet_colorsave',3)
# time.sleep(waitingtime)


# #%%
# #사이드

# searchandclick('geniediet_eyebodyside',3)
# time.sleep(waitingtime)
# searchandclick('geniediet_eyebody2',3)
# time.sleep(waitingtime)
# searchandclick('geniediet_eyebodypictureclick1',3)
# time.sleep(waitingtime)
# searchandclick_byrate('geniediet_eyebodypictureclickside',3,0.9)
# time.sleep(waitingtime)
# searchandclick('geniediet_eyebodyok',3)
# time.sleep(waitingtime)
# searchandclick('geniediet_colorchangeok',3)
# time.sleep(waitingtime)
# searchandclick('geniediet_ok',3)
# time.sleep(waitingtime)


# %%
device.input_keyevent('KEYCODE_APP_SWITCH')
#%%
searchandclick('geniediet_allappclose',3)
time.sleep(waitingtime)

#엔터키: device.input_keyevent(66,1)
#탭키: device.input_keyevent(61,1)




# %% 
# # 스크린샷
# save_cap('geniediet_1')


# # %%
# #탭하기
# device.input_swipe(544,1848,523,846,300)

# # %%
# #스와이프하기
# device.input_swipe(0,1000,0,0,1000)