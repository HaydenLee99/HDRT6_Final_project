from flask import Flask, request, jsonify
import os
import torch
from ultralytics import YOLO

import csv
import time
from threading import Lock

REQUEST_INTERVAL = 1.0      # 시뮬레이터가 API를 호출하는 주기[초]

t0 = time.time()            # 초기 시간
def get_time():
    return time.time() - t0
app = Flask(__name__)
model = YOLO('yolo11n.pt')
# print(model.names)

fire_lock = Lock()
last_fire_time = -1     # 마지막 포격 시간
FIRE_COOLDOWN = 6       # 재장전 소요 시간

ammo_lock = Lock()
AMMO_CAPACITY = 40      # 적재 포탄
ammo_count = 40           # 잔탄

def fire_state(trigger_fire=False):
    global last_fire_time, ammo_count

    now = get_time()

    with fire_lock, ammo_lock:

        if trigger_fire:
            if ammo_count <= 0:
                return {"state": "empty", "ammo": ammo_count}

            ammo_count -= 1
            last_fire_time = now
            return {"state": "fire", "ammo": ammo_count}

        if ammo_count <= 0:
            return {"state": "empty", "ammo": 0}

        if last_fire_time < 0:
            return {"state": "ready", "ammo": ammo_count}

        if now - last_fire_time < FIRE_COOLDOWN:
            return {"state": "reloading", "ammo": ammo_count}

        return {"state": "ready", "ammo": ammo_count}

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
    wait(), rotation_R(), rotation_R(), fire(),
    # wait(), rotation_F(), rotation_F(), fire(),

    wait(), rotation_E(0.1), wait(), wait(), wait(), fire(), wait(), rotation_E(0.1), wait(), wait(), wait(), fire(),
    wait(), rotation_E(0.1), wait(), wait(), wait(), fire(), wait(), rotation_E(0.1), wait(), wait(), wait(), fire(),
    wait(), rotation_E(0.1), wait(), wait(), wait(), fire(), wait(), rotation_E(0.1), wait(), wait(), wait(), fire(),
    wait(), rotation_E(0.1), wait(), wait(), wait(), fire(), wait(), rotation_E(0.1), wait(), wait(), wait(), fire(),
    wait(), rotation_E(0.1), wait(), wait(), wait(), fire(), wait(), rotation_E(0.1), wait(), wait(), wait(), fire(),

    wait(), rotation_E(0.1), wait(), wait(), wait(), fire(), wait(), rotation_E(0.1), wait(), wait(), wait(), fire(),
    wait(), rotation_E(0.1), wait(), wait(), wait(), fire(), wait(), rotation_E(0.1), wait(), wait(), wait(), fire(),
    wait(), rotation_E(0.1), wait(), wait(), wait(), fire(), wait(), rotation_E(0.1), wait(), wait(), wait(), fire(),
    wait(), rotation_E(0.1), wait(), wait(), wait(), fire(), wait(), rotation_E(0.1), wait(), wait(), wait(), fire(),
    wait(), rotation_E(0.1), wait(), wait(), wait(), fire(), wait(), rotation_E(0.1), wait(), wait(), wait(), fire(),

    wait(), rotation_E(0.1), wait(), wait(), wait(), fire(), wait(), rotation_E(0.1), wait(), wait(), wait(), fire(),
    wait(), rotation_E(0.1), wait(), wait(), wait(), fire(), wait(), rotation_E(0.1), wait(), wait(), wait(), fire(),
    wait(), rotation_E(0.1), wait(), wait(), wait(), fire(), wait(), rotation_E(0.1), wait(), wait(), wait(), fire(),
    wait(), rotation_E(0.1), wait(), wait(), wait(), fire(), wait(), rotation_E(0.1), wait(), wait(), wait(), fire(),
    wait(), rotation_E(0.1), wait(), wait(), wait(), fire(), wait(), rotation_E(0.1), wait(), wait(), wait(), fire(),

    wait(), rotation_E(0.1), wait(), wait(), wait(), fire(), wait(), rotation_E(0.1), wait(), wait(), wait(), fire(),
    wait(), rotation_E(0.1), wait(), wait(), wait(), fire(), wait(), rotation_E(0.1), wait(), wait(), wait(), fire(),
    wait(), rotation_E(0.1), wait(), wait(), wait(), fire(), wait(), rotation_E(0.1), wait(), wait(), wait(), fire(),
    wait(), rotation_E(0.1), wait(), wait(), wait(), fire(), wait(), rotation_E(0.1), wait(), wait(), wait(), fire(),
    wait(), rotation_E(0.1), wait(), wait(), wait(), fire(), wait(), rotation_E(0.1), wait(), wait(), wait(), fire(),

    wait(), rotation_E(0.1), wait(), wait(), wait(), fire(), wait(), rotation_E(0.1), wait(), wait(), wait(), fire(),
    wait(), rotation_E(0.1), wait(), wait(), wait(), fire(), wait(), rotation_E(0.1), wait(), wait(), wait(), fire(),
    wait(), rotation_E(0.1), wait(), wait(), wait(), fire(), wait(), rotation_E(0.1), wait(), wait(), wait(), fire(),
    wait(), rotation_E(0.1), wait(), wait(), wait(), fire(), wait(), rotation_E(0.1), wait(), wait(), wait(), fire(),
    wait(), rotation_E(0.1), wait(), wait(), wait(), fire(), wait(), rotation_E(0.1), wait(), wait(), wait(), fire(),

    wait(), rotation_E(0.1), wait(), wait(), wait(), fire(), wait(), rotation_E(0.1), wait(), wait(), wait(), fire(),
    wait(), rotation_E(0.1), wait(), wait(), wait(), fire(), wait(), rotation_E(0.1), wait(), wait(), wait(), fire(),
    wait(), rotation_E(0.1), wait(), wait(), wait(), fire(), wait(), rotation_E(0.1), wait(), wait(), wait(), fire(),
    wait(), rotation_E(0.1), wait(), wait(), wait(), fire(), wait(), rotation_E(0.1), wait(), wait(), wait(), fire(),
    wait(), rotation_E(0.1), wait(), wait(), wait(), fire(), wait(), rotation_E(0.1), wait(), wait(), wait(), fire(),

    wait(), rotation_E(0.1), wait(), wait(), wait(), fire(), wait(), rotation_E(0.1), wait(), wait(), wait(), fire(),
    wait(), rotation_E(0.1), wait(), wait(), wait(), fire(), wait(), rotation_E(0.1), wait(), wait(), wait(), fire(),
    wait(), rotation_E(0.1), wait(), wait(), wait(), fire(), wait(), rotation_E(0.1), wait(), wait(), wait(), fire(),
    wait(), rotation_E(0.1), wait(), wait(), wait(), fire(), wait(), rotation_E(0.1), wait(), wait(), wait(), fire(),
    wait(), rotation_E(0.1), wait(), wait(), wait(), fire(), wait(), rotation_E(0.1), wait(), wait(), wait(), fire(),

    wait(), rotation_E(0.1), wait(), wait(), wait(), fire(), wait(), rotation_E(0.1), wait(), wait(), wait(), fire(),
    wait(), rotation_E(0.1), wait(), wait(), wait(), fire(), wait(), rotation_E(0.1), wait(), wait(), wait(), fire(),
    wait(), rotation_E(0.1), wait(), wait(), wait(), fire(), wait(), rotation_E(0.1), wait(), wait(), wait(), fire(),
    wait(), rotation_E(0.1), wait(), wait(), wait(), fire(), wait(), rotation_E(0.1), wait(), wait(), wait(), fire(),
    wait(), rotation_E(0.1), wait(), wait(), wait(), fire(), wait(), rotation_E(0.1), wait(), wait(), wait(), fire(),

    wait(), rotation_E(0.1), wait(), wait(), wait(), fire(), wait(), rotation_E(0.1), wait(), wait(), wait(), fire(),
    wait(), rotation_E(0.1), wait(), wait(), wait(), fire(), wait(), rotation_E(0.1), wait(), wait(), wait(), fire(),
    wait(), rotation_E(0.1), wait(), wait(), wait(), fire(), wait(), rotation_E(0.1), wait(), wait(), wait(), fire(),
    wait(), rotation_E(0.1), wait(), wait(), wait(), fire(), wait(), rotation_E(0.1), wait(), wait(), wait(), fire(),
    wait(), rotation_E(0.1), wait(), wait(), wait(), fire(), wait(), rotation_E(0.1), wait(), wait(), wait(), fire()

]

# =========================
# LOG SYSTEM - Bullet
# =========================
bullet_log_lock = Lock()
log_file = "flat_bullet_log.csv"     # 착탄 정보

with open(log_file, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([
        "time",
        "impact_x",
        "impact_y",
        "impact_z",
        "hit"
    ])

def log_bullet(row):
    with bullet_log_lock:
        with open(log_file, "a", newline="") as f:
            csv.writer(f).writerow(row)

# =========================
# LOG SYSTEM - action
# =========================
action_log_lock = Lock()
action_log_file = "flat_action_log.csv"     # 착탄 정보

with open(action_log_file, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([
        "time",
        "pos_x", "pos_y", "pos_z",
        "turret_x", "turret_y",
        "moveWS",
        "moveAD",
        "turretQE",
        "turretRF",
        "fire",
        "ammo",
        "fire_state"
    ])

def log_action(state, action):
    with action_log_lock:
        with open(action_log_file, "a", newline="") as f:
            csv.writer(f).writerow([
                get_time(),

                state["pos_x"],
                state["pos_y"],
                state["pos_z"],

                state["turret_x"],
                state["turret_y"],

                action["moveWS"]["command"],
                action["moveAD"]["command"],
                action["turretQE"]["command"],
                action["turretRF"]["command"],

                action["fire"],

                state["ammo"],
                state["fire_state"]
            ])
# =========================
# DETECT
# =========================
@app.route('/detect', methods=['POST'])
def detect():
    image = request.files.get('image')
    if not image:
        return jsonify({"error": "No image received"}), 400

    image_path = 'temp_image.jpg'
    image.save(image_path)

    results = model(image_path)
    detections = results[0].boxes.data.cpu().numpy()

    target_classes = {0: "tank",1: "rock", 2: "car", 7: "truck", 15: "rock"}
    filtered_results = []

    for box in detections:
        class_id = int(box[5])
        if class_id in target_classes:
            filtered_results.append({
                'className': target_classes[class_id],
                'bbox': [float(coord) for coord in box[:4]],
                'confidence': float(box[4]),
                'color': '#00FF00',
                'filled': False,
                'updateBoxWhileMoving': False
            })

    return jsonify(filtered_results)

# =========================
# STEREO
# =========================
@app.route('/stereo_image', methods=['POST'])
def stereo_image():
    left_image = request.files.get('left_image')
    right_image = request.files.get('right_image')

    if not left_image or not right_image:
        return jsonify({"result": "error", "message": "Left or Right image missing"}), 400

    left_path = "temp_left.jpg"
    right_path = "temp_right.jpg"

    try:
        left_image.save(left_path)
        right_image.save(right_path)
    except Exception as e:
        return jsonify({"result": "error", "message": str(e)}), 500

    return jsonify({"result": "success"})

# =========================
# INFO
# =========================
@app.route('/info', methods=['POST'])
def info():
    data = request.get_json(force=True)
    if not data:
        return jsonify({"error": "No JSON received"}), 400

    print("📨 /info data received:", data)

    # Auto-pause after 15 seconds
    # if data.get("time", 0) > 15:
    #    return jsonify({"status": "success", "control": "pause"})

# =========================
# GET ACTION
# =========================
@app.route('/get_action', methods=['POST'])
def get_action():
    data = request.get_json(force=True)

    position = data.get("position", {})
    turret = data.get("turret", {})

    state = {
        "pos_x": position.get("x", 0),
        "pos_y": position.get("y", 0),
        "pos_z": position.get("z", 0),
        "turret_x": turret.get("x", 0),
        "turret_y": turret.get("y", 0),
    }

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
    # fire state 계산
    fire_info = fire_state(trigger_fire=command["fire"])

    state = {
        "pos_x": position.get("x", 0),
        "pos_y": position.get("y", 0),
        "pos_z": position.get("z", 0),

        "turret_x": turret.get("x", 0),
        "turret_y": turret.get("y", 0),

        "ammo": fire_info["ammo"],
        "fire_state": fire_info["state"]
    }
    log_action(state, command)

    print("🔁 Sent Combined Action:", command)
    return jsonify(command)

# =========================
# BULLET LOG
# =========================
@app.route('/update_bullet', methods=['POST'])
def update_bullet():
    data = request.get_json()
    if not data:
        return jsonify({"status": "ERROR"}), 400
    x = data.get("x")
    y = data.get("y")
    z = data.get("z")
    hit = data.get("hit")

    print(f"💥 Bullet Impact: ({x}, {y}, {z}) | hit={hit}")

    row = [
        get_time(),     # 착탄 시간
        x, y, z,        # 착탄 좌표
        hit             # 착탄 대상?
    ]

    log_bullet(row)

    return jsonify({"status": "OK"})

# =========================
# DESTINATION
# =========================
@app.route('/set_destination', methods=['POST'])
def set_destination():
    data = request.get_json()
    if not data or "destination" not in data:
        return jsonify({"status": "ERROR"}), 400

    try:
        x, y, z = map(float, data["destination"].split(","))
        print(f"🎯 Destination set to: x={x}, y={y}, z={z}")
        return jsonify({"status": "OK", "destination": {"x": x, "y": y, "z": z}})
    except Exception as e:
        return jsonify({"status": "ERROR", "message": str(e)}), 400

# =========================
# OBSTACLE
# =========================
@app.route('/update_obstacle', methods=['POST'])
def update_obstacle():
    data = request.get_json()
    if not data:
        return jsonify({'status': 'error'}), 400

    print("🪨 Obstacle Data:", data)
    return jsonify({'status': 'success'})

# =========================
# COLLISION
# =========================
@app.route('/collision', methods=['POST'])
def collision():
    data = request.get_json()
    if not data:
        return jsonify({'status': 'error'}), 400

    object_name = data.get('objectName')
    position = data.get('position', {})

    print(f"💥 Collision - Object: {object_name}, Pos: ({position.get('x')}, {position.get('y')}, {position.get('z')})")

    return jsonify({'status': 'success'})

# =========================
# INIT
# =========================
@app.route('/init', methods=['GET'])
def init():
    config = {
        "startMode": "start",
        "blStartX": 150,
        "blStartY": 10,
        "blStartZ": 150,

        "trackingMode": True,
        "detectMode": False,
        "logMode": False,
        "stereoCameraMode": False,
        "enemyTracking": False,
        "saveSnapshot": False,
        "saveLog": False,
        "saveLidarData": False,
        "lux": 30000,
        "destoryObstaclesOnHit": True
    }
    print("🛠️ Init config sent")
    return jsonify(config)

# =========================
# START
# =========================
@app.route('/start', methods=['GET'])
def start():
    global t0
    t0 = time.time()
    print("🚀 Episode start - time reset")
    return jsonify({"control": "", "t0": t0})

# =========================
# RUN
# =========================
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)