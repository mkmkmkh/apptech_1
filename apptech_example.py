# %%
#mobile화면보기 
!scrcpy
# %%
# wifi 무선연결 - 아래 코드 돌리고 USB 연결 해제
!adb disconnect
!adb kill-server
!adb tcpip 5555
!adb connect 192.168.0.5:5555 # wifi ip 주소 입력 

# %% 
from ppadb.client import Client
import cv2
import numpy as np
from numpy import random
from datetime import datetime
import time
import requests
import os

#adb 연결

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


# %%
device.input_keyevent('KEYCODE_SLEEP')
# %%
device.input_keyevent('KEYCODE_WAKEUP')
# %%
device.input_keyevent('KEYCODE_BACK')
# %%
device.input_keyevent('KEYCODE_HOME')
# %%
device.input_keyevent('KEYCODE_BACK')

# %%
# device.input_tap() 매크로 걸릴 수 있으므로 사용하지 않는다.
# device.input_swipe(시작점x좌표,시작점y좌표,끝점x좌표,끝점y좌표,누르는시간(ms))

#screenshot 저장
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

save_cap('example_1')

# %%
#탭하기
device.input_swipe(544,1848,523,846,300)
# %%
#스와이프하기
device.input_swipe(0,0,0,1000,1000)

# %%
# 조금 더 복잡한 조작

#전체화면 capture
def capture():
    img_byte = device.screencap()
    img = cv2.imdecode(np.frombuffer(img_byte,np.uint8), flags=-1)
    img = img[:,:,:3]
    return img

#부분캡쳐
def part_capture(x1,y1,x2,y2):
    img_byte = device.screencap()
    img = cv2.imdecode(np.frombuffer(img_byte,np.uint8), flags=-1)
    img = img[:,:,:3]
    roi = img[y1:y2,x1:x2]
    return roi

#screenshot 저장
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

# (x1,y1) ~ (x2,y2) 임의 클릭 (매크로 감지 피하기용)
def random_click(x1,y1,x2,y2):
    new_x = random.randint(x1,x2)
    new_y = random.randint(y1,y2)
    delay = random.randint(50,111)  
    device.input_swipe(new_x,new_y,new_x,new_y,delay)

# 저장해논 사진 범위 내로 임의 클릭/ picture_click 함수와 사용
def random_click_picture(x1,y1,w,h):
    new_x = random.randint(x1,x1+int(w))
    new_y = random.randint(y1,y1+int(h))
    delay = random.randint(50,111)  
    device.input_swipe(new_x,new_y,new_x,new_y,delay)

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

# 화면에서 이미지 위치 찾기
def get_position(img,name):
    ziloc = search(img,name)
    basic_template = cv2.imread('./'+ name[:name.find('_')]+ '/'+ name + '_template.png', cv2.IMREAD_COLOR)
    h, w = basic_template.shape[:-1]
    x1 = ziloc[0][0]
    y1 = ziloc[0][1]
    return x1,y1,w,h

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

# %%
#1. 현재화면 caputre -> 이미지
#2. 미리 만들어놓은 이미지 -> template
#3. 이미지와 탬플릿 비교해서 같은 이미지가 있는지 확인

#ex1) 앱 눌러서 들어가기 

# template만들기
save_cap('folder_app')
# %%
# 현재 화면 capture
img = capture()
# %%
#이미지와 탬플릿 비교 
search(img,'folder_app')
# %%
#인식 하기
len(search(img,'folder_app'))

# %%
#인식한 것 바탕으로 행동 명령하기
if len(search(img,'folder_app'))>0 :
    picture_click(img, 'folder_app')

# %%
# 최종
img = capture()
if len(search(img,'folder_app'))>0 :
    picture_click(img, 'folder_app')

# -> 이게 기본이지만, 이렇게만 쓰면
# 로딩 때문에 해당 이미지가 제대로 인식이 안될 수도 있고,
# click이 제대로 안될경우가 있을 수 있음.
# 자동화 문제발생 방어막 필요


# %%
# 직접 작성해보기











# %%
#searchand click 코드 설명 

searchandclick('folder_app',3)




