import os
import json
from dotenv import load_dotenv

import paho.mqtt.client as paho
from paho import mqtt
import time

#import GameClient

user_client_id = ""
running = True
map_updated = False
waiting_for_move = True

known_map = [[0 for _ in range(10)] for _ in range(10)]
# Iterate through each element of the matrix
for i in range(10):
    for j in range(10):
        known_map[i][j] = "None"

# setting callbacks for different events to see if it works, print the message etc.
def on_connect(client, userdata, flags, rc, properties=None):
    """
        Prints the result of the connection with a reasoncode to stdout ( used as callback for connect )
        :param client: the client itself
        :param userdata: userdata is set when initiating the client, here it is userdata=None
        :param flags: these are response flags sent by the broker
        :param rc: stands for reasonCode, which is a code for the connection result
        :param properties: can be used in MQTTv5, but is optional
    """
    print("CONNACK received with code %s." % rc)


# with this callback you can see if your publish was successful
def on_publish(client, userdata, mid, properties=None):
    """
        Prints mid to stdout to reassure a successful publish ( used as callback for publish )
        :param client: the client itself
        :param userdata: userdata is set when initiating the client, here it is userdata=None
        :param mid: variable returned from the corresponding publish() call, to allow outgoing messages to be tracked
        :param properties: can be used in MQTTv5, but is optional
    """
    print("mid: " + str(mid))


# print which topic was subscribed to
def on_subscribe(client, userdata, mid, granted_qos, properties=None):
    """
        Prints a reassurance for successfully subscribing
        :param client: the client itself
        :param userdata: userdata is set when initiating the client, here it is userdata=None
        :param mid: variable returned from the corresponding publish() call, to allow outgoing messages to be tracked
        :param granted_qos: this is the qos that you declare when subscribing, use the same one for publishing
        :param properties: can be used in MQTTv5, but is optional
    """
    print("Subscribed: " + str(mid) + " " + str(granted_qos))


# print message, useful for checking if it was successful
def on_message(client, userdata, msg):
    """
        Prints a mqtt message to stdout ( used as callback for subscribe )
        :param client: the client itself
        :param userdata: userdata is set when initiating the client, here it is userdata=None
        :param msg: the message with topic and payload
    """
    msgTopic = "games/" + lobby_name + "/" + user_client_id + "/game_state"
    if(msg.topic == msgTopic):
        print_game_state(msg.payload)
    if ("message: " + msg.topic + " " + str(msg.qos) + " " + str(msg.payload) == "message: games/TestLobby/lobby 0 b'Game Over: All coins have been collected'"):
        running = False
        map_updated = True
        waiting_for_move = False
    print("message: " + msg.topic + " " + str(msg.qos) + " " + str(msg.payload))


#functions for getting user input ans sh
def get_team():
    user_team = input("Enter team to join (a or b): ")
    ateam = 'ATeam'
    bteam = 'BTeam'
    if(user_team == 'a' or user_team == 'A'):
        return ateam
    elif (user_team == 'b' or user_team == 'B'):
        return bteam
    else:
        print("Please enter either a or b")
        return get_team()

def get_move():
    move = input("Enter your move (up, down, left, right): ")
    move = move.lower()
    if move == "up":
        waiting_for_move = False
        client.publish(f"games/{lobby_name}/{user_client_id}/move", "UP")
    elif move == "down":
        waiting_for_move = False
        client.publish(f"games/{lobby_name}/{user_client_id}/move", "DOWN")
    elif move == "left":
        waiting_for_move = False
        client.publish(f"games/{lobby_name}/{user_client_id}/move", "LEFT")
    elif move == "right":
        waiting_for_move = False
        client.publish(f"games/{lobby_name}/{user_client_id}/move", "RIGHT")   
    else:
        move = get_move()     

def print_game_state(state):
    state = json.loads(state)
    fill_map(state)
    map_updated = True
    waiting_for_move = True
    print_map()


def fill_map(state):
    clear_map()
    for key, value in state.items():
        if key == "teammateNames" :
            continue
        elif key == "currentPosition":
            if isinstance(value, list):
                x_pos = -1
                y_pos = -1
                for val in value:
                    if x_pos == -1:
                        x_pos = val
                    else:
                        y_pos = val
                known_map[x_pos][y_pos] = what_to_put_on_map(state, key)
        if not value:
            continue
        elif isinstance(value, list) and key != "currentPosition":
            thing = what_to_put_on_map(state, key)
            for val in value:
                known_map[val[0]][val[1]] = thing
        else:
            thing = what_to_put_on_map(state, key)
            known_map[value[0]][value[1]] = thing

            

def clear_map():
    for i in range(10):
        for j in range(10):
            if known_map[i][j] == "Wall":
                known_map[i][j] = "Wall"
            else:
                known_map[i][j] = "None"

def print_map():
    for i in range(10):
        for j in range(10):
        # Accessing and printing each element
            print(known_map[i][j], end="    ")
        print()  # Move to the next line after printing each row
    map_updated = False


def what_to_put_on_map(state, key):
    if key == "teammatePositions":
        return state["teammateNames"]
    elif key == "enemyPositions":
        return "ENEMY"
    elif key == "currentPosition":
        return "*" + user_client_id + "*"
    elif key == "coin1":
        return "Coin1"
    elif key == "coin2":
        return "Coin2"
    elif key == "coin3":
        return "Coin3"
    elif key == "walls":
        return "Wall"



if __name__ == '__main__':
    load_dotenv(dotenv_path='./credentials.env')
    
    broker_address = os.environ.get('BROKER_ADDRESS')
    broker_port = int(os.environ.get('BROKER_PORT'))
    username = os.environ.get('USER_NAME')
    password = os.environ.get('PASSWORD')


    #user_input = input("Enter up arrow: ")
    #print("You entered:", user_input)
    #if(user_input == "up"):
    #    print("up")


    user_client_id = input("Player Name: ")

    client = paho.Client(callback_api_version=paho.CallbackAPIVersion.VERSION1, client_id=user_client_id, userdata=None, protocol=paho.MQTTv5)
    # enable TLS for secure connection
    client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
    # set username and password
    client.username_pw_set(username, password)
    # connect to HiveMQ Cloud on port 8883 (default for MQTT)
    client.connect(broker_address, broker_port)

    # setting callbacks, use separate functions like above for better visibility
    client.on_subscribe = on_subscribe # Can comment out to not print when subscribing to new topics
    client.on_message = on_message
    client.on_publish = on_publish # Can comment out to not print when publishing to topics

    lobby_name = "TestLobby"

    client.loop_start()

    client.subscribe(f"games/{lobby_name}/lobby")
    client.subscribe(f'games/{lobby_name}/+/game_state')
    client.subscribe(f'games/{lobby_name}/scores')

    user_team = get_team()

    client.publish("new_game", json.dumps({'lobby_name':lobby_name,
                                            'team_name':user_team,
                                            'player_name' : user_client_id}))
    

    print("The game is starting soon")
    time.sleep(10) # Wait a second to resolve game start
    client.publish(f"games/{lobby_name}/start", "START")
    #client.publish(f"games/{lobby_name}/{user_client_id}/move", "UP")
    #client.publish(f"games/{lobby_name}/start", "STOP")

    while (running == True):
        if not map_updated:
            time.sleep(1)
        if waiting_for_move:
            get_move()
            time.sleep(1)
        


