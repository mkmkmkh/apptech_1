
# %%
from ppadb.client import Client
import cv2
import numpy as np
from numpy import random
import datetime
import time
import requests
import os
import subprocess




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
    subprocess.Popen(["mspaint", ""])
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
    templ = cv2.imread('./'+ name[:name.find('_')]+ '/'+ name + '_t.png', cv2.IMREAD_COLOR)
    # img = cv2.resize(img,dsize=None,fx=0.4,fy=0.4)
    # templ = cv2.resize(templ,dsize=None,fx=0.4,fy=0.4)
    res = cv2.matchTemplate(img,templ,cv2.TM_CCOEFF_NORMED)
    threshold = threshold
    loc = np.where(res >= threshold)
    ziloc = list(zip(*loc[::-1]))
    
    return ziloc

#%%
#text중인 함수 merge-location
def merge_locations(ziloc, distance=10):
    merged_ziloc = []
    for i in range(len(ziloc)):
        try:
            x1, y1 = ziloc[i][0], ziloc[i][1]
        except:
            break
        min_x, min_y = x1, y1
        for j in range(len(ziloc)-1, i, -1):
            try:
                x2, y2 = ziloc[j][0], ziloc[j][1]
            except:
                break
            dist = (abs(x1-x2)+abs(y1-y2))/2
            if dist < distance:
                ziloc.pop(j)
                if x2 < min_x:
                    min_x = x2
                if y2 < min_y:
                    min_y = y2        
        merged_ziloc.append((min_x, min_y))
    print(len(ziloc))
    print(merged_ziloc)        
    return merged_ziloc


#%%

def search_merge(img,name,threshold=0.8):
    '''
    img = 현재화면 캡처
    name = 비교할 이미지 (미리 저장해놓은 file)
    threshold = 일치율 지정 ( 기본 0.8 )
    '''
    templ = cv2.imread('./'+ name[:name.find('_')]+ '/'+ name + '_t.png', cv2.IMREAD_COLOR)
    # img = cv2.resize(img,dsize=None,fx=0.4,fy=0.4)
    # templ = cv2.resize(templ,dsize=None,fx=0.4,fy=0.4)
    res = cv2.matchTemplate(img,templ,cv2.TM_CCOEFF_NORMED)
    threshold = threshold
    loc = np.where(res >= threshold)
    ziloc = list(zip(*loc[::-1]))
    ziloc = merge_locations(ziloc)
    #textcode
    return ziloc

def picture_click_byrate_merge(n,img,name,threshold):
    '''
    현재화면(img) 과 template(name) 비교해서,
    일치하는 이미지 있으면 클릭한다.
    '''
    ziloc = search_merge(img,name,threshold)
    basic_template = cv2.imread('./'+ name[:name.find('_')]+ '/'+ name + '_t.png', cv2.IMREAD_COLOR)
    h, w = basic_template.shape[:-1]

    x1 = ziloc[n-1][0]
    y1 = ziloc[n-1][1]
    random_click_picture(x1, y1, w, h)
    print(f'click {n}th picture of {name}')
    
def searchandclick_byrate_merge(n,name,waitingtime,threshold):
    '''
    클릭 후 화면 바뀌는 경우가 자주 있어서, searchandclick 함수 생성
    screenshot → 이미지(name)찾기 → click → 이미지 사라졌는지 check
    watingtime = click후 대기 시간 지정
    
    '''
    for i in range(10):
        img = capture()
        if len(search_merge(img,name,threshold))>0 :
            picture_click_byrate_merge(n,img,name,threshold)
            time.sleep(waitingtime)
            img = capture()
            if len(search_merge(img,name,threshold)) == 0 :
                break


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
    basic_template = cv2.imread('./'+ name[:name.find('_')]+ '/'+ name + '_t.png', cv2.IMREAD_COLOR)
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
    basic_template = cv2.imread('./'+ name[:name.find('_')]+ '/'+ name + '_t.png', cv2.IMREAD_COLOR)
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
    basic_template = cv2.imread('./'+ name[:name.find('_')]+ '/'+ name + '_t.png', cv2.IMREAD_COLOR)
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
time.sleep(0.5)
# %%
device.input_keyevent('KEYCODE_WAKEUP')
time.sleep(0.5)
# %%
device.input_keyevent('KEYCODE_HOME')
time.sleep(waitingtime)
# # %%
# device.input_keyevent('KEYCODE_BACK')
# %%
# 앱실행
searchandclick('amore_stap',3)
time.sleep(waitingtime*2)

#%%업데이트 끄기
searchandclick('amore_update',3)
time.sleep(waitingtime)

# %%
searchandclick('amore_close',3)
time.sleep(waitingtime)
#닫기버튼
# %%
searchandclick('amore_search',3)
time.sleep(waitingtime)
#검색버튼
# %%
searchandclick('amore_search2',3)
time.sleep(waitingtime)
# %%
#  스와이프해서 아래로 내리기
device.input_swipe(0,1000,0,0,1000)
#%%
searchandclick('amore_ckbn',3)
time.sleep(waitingtime)


#%%
device.input_keyevent('KEYCODE_APP_SWITCH')

searchandclick('qnn24_allappclose',3)
time.sleep(waitingtime)

# %%
device.input_keyevent('KEYCODE_SLEEP')





#%% 마지막에 지워야해
# save_cap('amore_1')
# %%
# # 스와이프해서 아래로 내리기
# device.input_swipe(0,1000,0,0,1000)

