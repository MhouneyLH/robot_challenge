import paho.mqtt.client as mqtt
from getkey import getkey, keys
import json
import time
import numpy as np
import configparser

MAX_SPEED = 100
MIN_SPEED = 15
SPEED = 70
TURNING_DURATION = 3
TURNING_SPEED = 70


class Rover:
    id = -1
    goal_id = -1
    _client = False
    position = False  # {'x':0, 'y':0, 'h':0.0}
    goal_position = {'x': 0, 'y': 0, 'h': 0.0}
    acceleration = False  # {'x':0, 'y':0, 'z':0}
    _last_speed_A = None
    _last_speed_B = None
    servos = {'pos': [90, 90]}
    status = False  # {'bat':0, 'FW':0.54}
    measurement = -1

    _t_start = 0
    delta_t = 0.2

    _heading_error_i = 0
    _dist_i = 0
    _heading_error = []

    #############################################
    def turn_right(self):
        self.set_motor_speed(TURNING_SPEED, -TURNING_SPEED)
        # time.sleep(TURNING_DURATION)

    def turn_left(self):
        self.set_motor_speed(-TURNING_SPEED, TURNING_SPEED)
        # time.sleep(TURNING_DURATION)

    def remote_control(self):
        key = "0"
        while key != "b":
            key = getkey()

            match key:
                case "w":
                    self.set_motor_speed(SPEED, SPEED)
                case "s":
                    self.set_motor_speed(-SPEED, -SPEED)
                case "a":
                    self.turn_left()
                case "d":
                    self.turn_right()
                case "c":
                    self.set_motor_speed(0, 0)
    #############################################

    def wait_for_position(self):
        while (not self.position):
            print("waiting for position data..")
            time.sleep(0.2)
        print("ok")

    def wait_for_status(self):
        while (not self.status):
            print("waiting for status data..")
            time.sleep(0.2)
        print("ok")

    def wait_for_accel(self):
        while (not self.acceleration):
            print("waiting for acceleration data..")
            time.sleep(0.2)
        print("ok")

    def set_motor_speed(self, speed_A, speed_B):
        speed_A = -int(speed_A)
        speed_B = -int(speed_B)

        if ((speed_A == self._last_speed_A) and (speed_B == self._last_speed_B)):
            return

        payload = {"speed_A": speed_A, "speed_B": speed_B}
        self._client.publish(
            f'robot/{self.id}/motor', json.dumps(payload), qos=1)
        self._last_speed_A = speed_A
        self._last_speed_B = speed_B
        time.sleep(0.1)

    def set_servo1_pos(self, pos):
        self.servos['pos'][0] = pos
        self._client.publish(
            f'robot/{self.id}/servo', json.dumps(self.servos), qos=1)
        time.sleep(1)

    def set_servo2_pos(self, pos):
        self.servos['pos'][1] = pos
        self._client.publish(
            f'robot/{self.id}/servo', json.dumps(self.servos), qos=1)
        time.sleep(1)

    def set_leds(self, top_1, top_2, side):
        payload = {"top_1": top_1, "top_2": top_2, "side": side}
        self._client.publish(
            f'robot/{self.id}/leds', json.dumps(payload), qos=1)
        time.sleep(1)

    def beep(self):
        self._client.publish(f'robot/{self.id}/beep', "{}", qos=1)

    def cheat(self):
        print("activated cheat measurement")
        self.beep()
        self._client.publish(f'overwatch/cheat', self.id, qos=1)

    def _on_message(self, client, userdata, message):
        if (message.topic == f'robot/{self.id}/accel'):
            m_decode = str(message.payload.decode("utf-8", "ignore"))
            self.acceleration = json.loads(m_decode)  # decode json data
        elif (message.topic == f'robot/{self.id}/position'):
            self.position = json.loads(message.payload)
        elif (message.topic == f'robot/{self.goal_id}/position'):
            self.goal_position = json.loads(message.payload)
        elif (message.topic == f'user/{self.id}/message'):
            print(message.payload)
            quit()
        elif (message.topic == f'robot/{self.id}/status'):
            self.status = json.loads(message.payload)
            if (int(self.status['bat']) < 2700):
                print("warning: low battery!")
        elif (message.topic == f'robot/{self.id}/measurement'):
            self.measurement = int(message.payload)

    def set_goal_id(self, goal_id):
        self.goal_id = goal_id
        self._client.subscribe(f'robot/{goal_id}/position')

    def unset_goal_id(self):
        self._client.unsubscribe(f'robot/{self.goal_id}/position')
        self.goal_id = "??"
        self.goal_position = {'x': 0, 'y': 0, 'h': 0.0}

    def isset_goal_id(self):
        return (self.goal_id != "??")

    def move_to(self, point, speed=50, threshold=50):

        self.wait_for_position()

        self.goal_position['x'] = point[0]
        self.goal_position['y'] = point[1]

        while (True):
            if (self._move_to_goal(speed, threshold)):
                break
            try:
                time.sleep(0.2)
            except KeyboardInterrupt:
                self.set_motor_speed(0, 0)
                print("Rover halted.")
                time.sleep(1)
                quit()

    def _move_to_goal(self, speed, threshold):
        KP_turn = 0.4
        KI_turn = 0.05

        x = self.goal_position['x'] - self.position['x']
        y = self.goal_position['y'] - self.position['y']

        dist = np.sqrt(x**2+y**2)

        if (dist < threshold):
            self.set_motor_speed(0, 0)
            self._heading_error_i = 0
            self._dist_i = 0
            return True

        else:
            goal_heading = np.arctan2(x, y)*180/np.pi

            if (self.position['h'] >= 0 and goal_heading > 0):
                heading_error = self.position['h'] - goal_heading
                # print("fall 1")
            elif (self.position['h'] <= 0 and goal_heading < 0):
                heading_error = self.position['h'] - goal_heading
                # print("fall 2")
            else:
                heading_error = abs(self.position['h']) + abs(goal_heading)
                heading_error = heading_error * np.sign(self.position["h"])

                # print("fall 3")
                if abs(heading_error) > 180:
                    heading_error = np.sign(
                        goal_heading)*(360-abs(heading_error))
                    # print("fall 4")

            # print(f'{goal_heading} {self.position["h"]} {heading_error} {dist}')

            self._heading_error_i = self._heading_error_i + heading_error*self.delta_t
            turn_speed = heading_error * KP_turn + self._heading_error_i * KI_turn

            self._dist_i = self._dist_i + dist*self.delta_t
            forward_speed = speed  # dist * KP_fwd + self.dist_i * KI_fwd

            left_speed = int(turn_speed+forward_speed)
            right_speed = int(-turn_speed+forward_speed)

            if (left_speed > MAX_SPEED):
                left_speed = MAX_SPEED
            if (left_speed < -MAX_SPEED):
                left_speed = -MAX_SPEED
            if (right_speed > MAX_SPEED):
                right_speed = MAX_SPEED
            if (right_speed < -MAX_SPEED):
                right_speed = -MAX_SPEED

            # print(f'{dist}: {left_speed} / {right_speed}')

            self.set_motor_speed(right_speed, left_speed)

            return False

    def head_to(self, heading, threshold=3, turn_rate=4):
        self.goal_heading = heading

        while (True):
            if (self._head_to(threshold, turn_rate)):
                break
            try:
                time.sleep(0.2)
            except KeyboardInterrupt:
                self.set_motor_speed(0, 0)
                print("Rover halted.")
                time.sleep(1)
                quit()

    def _head_to(self, threshold, turn_rate):
        KP_turn = turn_rate
        KI_turn = 0.05

        if (self.position['h'] >= 0 and self.goal_heading > 0):
            heading_error = self.position['h'] - self.goal_heading
            # print("fall 1")
        elif (self.position['h'] <= 0 and self.goal_heading < 0):
            heading_error = self.position['h'] - self.goal_heading
            # print("fall 2")
        else:
            heading_error = abs(self.position['h']) + abs(self.goal_heading)
            heading_error = heading_error * np.sign(self.position["h"])

            # print("fall 3")
            if abs(heading_error) > 180:
                heading_error = np.sign(
                    self.goal_heading)*(360-abs(heading_error))
                # print("fall 4")

        # print(f'{self.goal_heading} {self.position["h"]} {heading_error}')

        if (abs(heading_error) < threshold):
            self.set_motor_speed(0, 0)
            self._heading_error_i = 0
            self._heading_error.clear()
            return True

        else:
            turn_speed = np.sign(heading_error) * \
                np.sqrt(abs(heading_error)) * KP_turn

            if (len(self._heading_error) < 5):
                self._heading_error.append(heading_error)
            else:
                self._heading_error.pop(0)
                self._heading_error.append(heading_error)

            if abs(turn_speed) < 25:
                turn_speed = np.sign(turn_speed)*25 + \
                    np.sum(self._heading_error)*KI_turn

            left_speed = int(-turn_speed)
            right_speed = int(turn_speed)

            if (left_speed > MAX_SPEED):
                left_speed = MAX_SPEED
            if (left_speed < -MAX_SPEED):
                left_speed = -MAX_SPEED
            if (right_speed > MAX_SPEED):
                right_speed = MAX_SPEED
            if (right_speed < -MAX_SPEED):
                right_speed = -MAX_SPEED

            # print(f'{heading_error}: {left_speed} / {right_speed}')

            self.set_motor_speed(-right_speed, -left_speed)

            return False

    def __init__(self):

        config = configparser.ConfigParser()
        config.read('rover.properties')

        self.id = config.get("rover", "rover_id")

        self._client = mqtt.Client(f'User-{self.id}')
        self._client.on_message = self._on_message

        self._client.connect(config.get("mqtt", "broker_ip"))

        self._client.subscribe(f'robot/{self.id}/position')
        self._client.subscribe(f'robot/{self.id}/accel')
        self._client.subscribe(f'robot/{self.id}/status')
        self._client.subscribe(f'robot/{self.id}/measurement')
        self._client.subscribe(f'user/{self.id}/message')

        print(f'Rover {self.id} started.')

        self.set_motor_speed(0, 0)

        self._client.loop_start()
