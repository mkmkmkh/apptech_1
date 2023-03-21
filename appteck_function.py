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