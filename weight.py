'''
# 전차 자세 제어를 위한 필요 weight 계산 함수
# weight 는 액션에 대한 가중치로 0.1 ~ 1.0 사이 값을 갖는다.
# 시뮬레이션에 반영은 (기존 물리량 * weight)
# weight 1.0 일 때 turretQE는 41.33 deg/s  터렛의 회전 (운동 범위 0~360도)
# weight 1.0 일 때 turretRF는 5.17 deg/s   터렛의 포의 상하 각도 변경 (운동 범위 -5~10도)
# weight 1.0 일 때 moveAD는 41.33 deg/s    바디의 회전 (운동 범위 0~360도)
# Player 전차의 크기를 하단 몸체(body) 그리고 좌표기준으로 최대값들을 연결한 박스로 측정한다면 (3.667, 1.582, 8.066) 입니다.
# Player 전차의 포탑(turret)의 크기는 (3.297, 2.779, 5.891) 입니다.
# Terrain의 크기는 Unity의 좌표기준으로 300 X 300 사이즈
# moveWS command는 "W":전진, "S":후진, "STOP":정지, "":입력 없음
# moveAD command는 "A":좌회전, "D":우회전, "":입력 없음
# turretQE command는 "Q":터렛 좌회전, "E":터렛 우회전, "":입력 없음
# turretRF command는 "R":터렛 상방향 각도 조정, "F":터렛 하방향 각도 조정, "":입력 없음
# fire command는 True 발사, False 발사 안함, 발사 후 쿨다운 6초
# 사격 시 반발로 탱크 위치가 뒤로 밀림을 시뮬레이션 상에서 확인함 (포 정렬 상태) get_action 로그는 소수점 둘째자리 까지 받아서 안보이는데
     info로그는 4자리까지 보이는데 0.001,2 정도 밀리긴 함
 # 사거리 -5 21 10 130 즈음
Request_Interval = 0.5      # 시뮬레이터가 API를 호출하는 주기
combined_commands = [
    {
        "moveWS": {"command": "", "weight": 1.0},
        "moveAD": {"command": "", "weight": 0.0},
        "turretQE": {"command": "", "weight": 0.0},
        "turretRF": {"command": "", "weight": 0.0},
        "fire": False
    }

]
# 시뮬레이터는 아래 처럼 동작한다
@app.route('/get_action', methods=['POST'])
def get_action():
    global last_fire_context

    data = request.get_json(force=True)

    position = data.get("position", {})
    turret = data.get("turret", {})

    pos_x = position.get("x", 0)
    pos_y = position.get("y", 0)
    pos_z = position.get("z", 0)

    turret_x = turret.get("x", 0)
    turret_y = turret.get("y", 0)

    if combined_commands:
        command = combined_commands.pop(0)
    else:
        command = {
            "moveWS": {"command": "STOP", "weight": 1.0},
            "moveAD": {"command": "", "weight": 0.0},
            "turretQE": {"command": "", "weight": 0.0},
            "turretRF": {"command": "", "weight": 0.0},
            "fire": False
        }
'''

def wait():
    # 정지 or 대기
    return    {
        "moveWS": {"command": "STOP", "weight": 1.0},
        "moveAD": {"command": "", "weight": 0.0},
        "turretQE": {"command": "", "weight": 0.0},
        "turretRF": {"command": "", "weight": 0.0},
        "fire": False
    }

def fire():
    # 포격
    return    {
        "moveWS": {"command": "STOP", "weight": 1.0},
        "moveAD": {"command": "", "weight": 0.0},
        "turretQE": {"command": "", "weight": 0.0},
        "turretRF": {"command": "", "weight": 0.0},
        "fire": True
    }

def rotation_E(weight=1.0):
    # 회전 이동
    return {   # R 이동
        "moveWS": {"command": "", "weight": 1.0},
        "moveAD": {"command": "", "weight": 0.6},
        "turretQE": {"command": "E", "weight": weight},
        "turretRF": {"command": "", "weight": 0.1},
        "fire": False
    }

def rotation_Q(weight=1.0):
    # 회전 이동
    return {   # R 이동
        "moveWS": {"command": "", "weight": 1.0},
        "moveAD": {"command": "", "weight": 0.6},
        "turretQE": {"command": "Q", "weight": weight},
        "turretRF": {"command": "", "weight": 0.1},
        "fire": False
    }

def rotation_R(weight=1.0):
    # 회전 이동
    return {   # R 이동
        "moveWS": {"command": "", "weight": 1.0},
        "moveAD": {"command": "", "weight": 0.6},
        "turretQE": {"command": "", "weight": 0.1},
        "turretRF": {"command": "R", "weight": weight},
        "fire": False
    }

def rotation_F(weight=1.0):
    # 회전 이동
    return {   # F 이동
        "moveWS": {"command": "", "weight": 1.0},
        "moveAD": {"command": "", "weight": 0.6},
        "turretQE": {"command": "", "weight": 0.1},
        "turretRF": {"command": "F", "weight": weight},
        "fire": False
    }


combined_commands = [
    wait(),
    rotation_E(), rotation_E(), rotation_R(), rotation_R(), fire(),
    rotation_E(), rotation_E(), rotation_R(), rotation_R(), fire(),

]
print(len(combined_commands))