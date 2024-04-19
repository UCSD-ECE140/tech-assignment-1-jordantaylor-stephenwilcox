import os
import json
from dotenv import load_dotenv

import paho.mqtt.client as paho
from paho import mqtt
import time
import random
import math
from collections import deque

running = True
counter = 0
lobby_name = "TestLobby"
player_1 = "Player1"
player_2 = "Player2"
player_3 = "Player3"
player_4 = "Player4"

known_map_A = [[0 for _ in range(10)] for _ in range(10)]
known_map_B = [[0 for _ in range(10)] for _ in range(10)]
for i in range(10):
    for j in range(10):
        known_map_A[i][j] = "None"
        known_map_B[i][j] = "None"
known_coins_A = []
known_coins_B = []

vistited_map_A = [[0 for _ in range(10)] for _ in range(10)]
vistited_map_B = [[0 for _ in range(10)] for _ in range(10)]


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
    msgTopic1 = "games/" + lobby_name + "/" + player_1 + "/game_state"
    msgTopic2 = "games/" + lobby_name + "/" + player_2 + "/game_state"
    msgTopic3 = "games/" + lobby_name + "/" + player_3 + "/game_state"
    msgTopic4 = "games/" + lobby_name + "/" + player_4 + "/game_state"
    if(msg.topic == msgTopic1):
        fill_map(msg.payload, player_1)
    elif(msg.topic == msgTopic2):
        fill_map(msg.payload, player_2)
    elif(msg.topic == msgTopic3):
        fill_map(msg.payload, player_3)
    elif(msg.topic == msgTopic4):
        fill_map(msg.payload, player_4)
    if ("message: " + msg.topic + " " + str(msg.qos) + " " + str(msg.payload) == "message: games/TestLobby/lobby 0 b'Game Over: All coins have been collected'"):
        running = False
    print("message: " + msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
    #need to move after all maps have been filled
    


def count():
    global counter
    counter = counter + 1
    c = str(counter)
    if counter >= 4:
        move()
        counter = 0
        clear_map_A()
        clear_map_B()

def fill_map(state, player):
    state = json.loads(state)
    if player == player_1 or player == player_2:
        fill_map_A(state, player)
    else:
        fill_map_B(state, player)

def fill_map_A(state, player):
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
                known_map_A[x_pos][y_pos] = what_to_put_on_map(state, key, player)
        if not value:
            continue
        elif isinstance(value, list) and key != "currentPosition":
            thing = what_to_put_on_map(state, key, player)
            for val in value:
                known_map_A[val[0]][val[1]] = thing
        else:
            thing = what_to_put_on_map(state, key, player)
            known_map_A[value[0]][value[1]] = thing
    count()

def clear_map_A():
    for i in range(10):
        for j in range(10):
            if known_map_A[i][j] == "Wall":
                known_map_A[i][j] = "Wall"
            else:
                known_map_A[i][j] = "None"


def fill_map_B(state, player):
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
                known_map_B[x_pos][y_pos] = what_to_put_on_map(state, key, player)
        if not value:
            continue
        elif isinstance(value, list) and key != "currentPosition":
            thing = what_to_put_on_map(state, key, player)
            for val in value:
                known_map_B[val[0]][val[1]] = thing
        else:
            thing = what_to_put_on_map(state, key, player)
            known_map_B[value[0]][value[1]] = thing
    count()

def clear_map_B():
    for i in range(10):
        for j in range(10):
            if known_map_B[i][j] == "Wall":
                known_map_B[i][j] = "Wall"
            else:
                known_map_B[i][j] = "None"

def what_to_put_on_map(state, key, player):
    if key == "teammatePositions":
        if player == player_1:
            return player_2
        elif player == player_2:
            return player_1
        elif player == player_3:
            return player_4
        elif player == player_4:
            return player_3
    elif key == "enemyPositions":
        return "ENEMY"
    elif key == "currentPosition":
        return player
    elif key == "coin1":
        return "Coin1"
    elif key == "coin2":
        return "Coin2"
    elif key == "coin3":
        return "Coin3"
    elif key == "walls":
        return "Wall"
    
def move():
    move_order = get_move_order()
    for player in move_order:
        move = get_move(player)
        client.publish(f"games/{lobby_name}/{player}/move", move)
    time.sleep(1)

def get_move(player):
    move = ""
    if player == player_1 or player == player_2:
        move = get_move_f(player, known_map_A, vistited_map_A)
    elif player == player_3 or player == player_4:
        move = get_move_f(player, known_map_B, vistited_map_B)
    return move
    
def get_move_f(player, map, visited):
    for i in range(10):
        for j in range(10):
            if map[i][j] == player:
                move = get_move_p(i, j, map, player, visited)
                return move
                #move = check_map(i, j, map)
#    for i in range(10):
#        for j in range(10):
#           if map[i][j] == player:
#               i_s = str(i)
#               j_s = str(j)
#               print("map[" + i_s + " ][" + j_s + "] == " + player)
#    rand = random.randint(1, 4)
#    if rand == 1:
#        return "UP"
#    elif rand == 2:
#        return "DOWN"
#    elif rand == 3:
#        return "LEFT"
#    elif rand == 4:
#        return "RIGHT"
            
def check_for_coin_nearby(x, y, matrix):
    directions = [(1, 0, 'DOWN'), (-1, 0, 'UP'), (0, 1, 'RIGHT'), (0, -1, 'LEFT')]
    rows, cols = len(matrix), len(matrix[0])

    for dx, dy, direction in directions:
        new_x, new_y = x + dx, y + dy
        if 0 <= new_x < rows and 0 <= new_y < cols and matrix[new_x][new_y].startswith("Coin"):
            return direction

    return None
                

def get_move_p(x, y, map, player, visited):
    direction = check_for_coin_nearby(x, y, map)
    if direction is not None:
        return direction
    player_position = (x,y)
    nearest_coin, distance = find_nearest_coin(map, player_position)
    if nearest_coin:
        path = find_path(map, player_position, nearest_coin)
        moves = get_moves([(player_position[0], player_position[1])] + path)
        if moves:
            for move in moves:
                if move:
                    return move
        else:
            moves = move_opposite(x, y, map)
            for move in moves:
                if move:
                    return move
            return move
    else:
        return check_walls(x, y, map)
    #move =  dfs(map, visited, x, y)
    #print("GET MOVE P FUNCTION")
    #print(move)
    #return move
    #moves = ["UP", "RIGHT", "DOWN", "LEFT"]
    #themove = check_map(x, y, map, player)
    #if themove in moves:
    #    return themove
    #return "UP"
    '''
    move_order = []
    if player == player_1:
        move_order = ["UP", "RIGHT", "DOWN", "LEFT"]
    elif player == player_2:
        move_order = ["RIGHT", "DOWN", "LEFT", "UP"]
    elif player == player_3:
        move_order = ["DOWN", "LEFT", "UP", "RIGHT"]
    elif player == player_4:
        move_order = ["LEFT", "UP", "RIGHT", "DOWN"]
    for move in move_order:
        cx = 0
        cy = 0
        if move == "UP":
            cy = y + 1
        elif move == "RIGHT":
            cx = x + 1
        elif move == "DOWN":
            cy = y - 1
        else:
            cx = x - 1
        if check_valid(x, y):
            if no_walls(x, y, map):
                print(move)
                return move
    return "UP"
    '''

def check_valid(x, y):
    if x < 0 or x > 9 or y < 0 or y > 9:
        return False    
    return True

def no_walls(x, y, map):
    if map[x][y] == "Wall":
        return False
    return True

def is_valid_move(x, y, visited, map):
    if check_valid(x, y):
        if no_walls(x, y, map):
            if not visited[x][y]:
                return True
    return False


def dfs(map, visited, x, y):
    # Mark the current square as visited
    visited[x][y] = True
    
    # Check all possible moves (up, down, left, right)
    #moves = [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]
    moves = ["UP", "RIGHT", "DOWN", "LEFT"]
    for move in moves:
        if move == "UP":
            new_y = y
            new_x = x - 1
        elif move == "RIGHT":
            new_y = y + 1
            new_x = x
        elif move == "DOWN":
            new_y = y
            new_x = x + 1
        else:
            new_y = y - 1
            new_x = x
        #new_x, new_y = move
        # Check if the move is valid and not visited yet
        if is_valid_move(new_x, new_y, visited, map):
            # Recursively explore the valid move
            #dfs(map, visited, new_x, new_y)
            return move
    



def check_map(x, y, map, player):
    moves = ["UP", "RIGHT", "DOWN", "LEFT"]
    coin_x = 100
    coin_y = 100
    for i in range(10):
        for j in range(10):
            if map[i][j] == "Coin1" or map[i][j] == "Coin2" or map[i][j] == "Coin3":
                if player == player_1 or player == player_2:
                    if not coin_is_known(i, j, known_coins_A):
                        known_coins_A.append([i, j])
                if closer(x, y, coin_x, coin_y, i, j):
                    coin_x = i
                    coin_y = j
    if coin_x == 100 and coin_y == 100:
        return check_walls(x, y, map)
    if coin_y < y:
        return "LEFT"
    if coin_x > x:
        return "DOWN"
    if coin_y > y:
        return "RIGHT"
    if coin_x < x:
        return "UP"
    
def check_walls(x, y, map):
    player = map[x][y]
    
    if player == "Player1":
        if check_valid(x, y + 1) and no_walls(x, y + 1, map):
            return "RIGHT"
        if check_valid(x + 1, y) and no_walls(x + 1, y, map):
            return "DOWN"
        if check_valid(x, y - 1) and no_walls(x, y - 1, map):
            return "LEFT"
        if check_valid(x - 1, y) and no_walls(x - 1, y, map):
            return "UP"
    elif player == "Player2":
        if check_valid(x, y + 1) and no_walls(x, y + 1, map):
            return "RIGHT"
        if check_valid(x - 1, y) and no_walls(x - 1, y, map):
            return "UP"
        if check_valid(x + 1, y) and no_walls(x + 1, y, map):
            return "DOWN"
        if check_valid(x, y - 1) and no_walls(x, y - 1, map):
            return "LEFT"
    elif player == "Player3":
        if check_valid(x - 1, y) and no_walls(x - 1, y, map):
            return "UP"
        if check_valid(x, y - 1) and no_walls(x, y - 1, map):
            return "LEFT"
        if check_valid(x, y + 1) and no_walls(x, y + 1, map):
            return "RIGHT"
        if check_valid(x + 1, y) and no_walls(x + 1, y, map):
            return "DOWN"
    elif player == "Player4":
        if check_valid(x, y - 1) and no_walls(x, y - 1, map):
            return "LEFT"
        if check_valid(x + 1, y) and no_walls(x + 1, y, map):
            return "DOWN"
        if check_valid(x - 1, y) and no_walls(x - 1, y, map):
            return "UP"
        if check_valid(x, y + 1) and no_walls(x, y + 1, map):
            return "RIGHT"
    return None
            

def closer(x, y, coin_x, coin_y, new_x, new_y):
    distance_to_coin = distance(x, y, coin_x, coin_y)
    distance_to_new = distance(x, y, new_x, new_y)
    
    if distance_to_new < distance_to_coin:
        return True
    else:
        return False

def distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def print_map_T():
    map = [[0 for _ in range(10)] for _ in range(10)]
    for i in range(10):
        for j in range(10):
            if known_map_A[i][j] != "None":
                map[i][j] = known_map_A[i][j]
            elif known_map_B[i][j] != "None":
                map[i][j] = known_map_B[i][j]
            else:
                map[i][j] = "None"
    for i in range(10):
        for j in range(10):
        # Accessing and printing each element
            print(map[i][j], end="    ")
        print()  # Move to the next line after printing each row

def print_map(map):
    for i in range(10):
        for j in range(10):
        # Accessing and printing each element
            print(map[i][j], end="    ")
        print()  # Move to the next line after printing each row

def get_move_order():
    order = []
    while len(order) < 4:
        rand = random.randint(1,4)
        if rand == 1:
            if not check_list(order, player_1):
                order.append(player_1)
        elif rand == 2:
            if not check_list(order, player_2):
                order.append(player_2)
        elif rand == 3:
            if not check_list(order, player_3):
                order.append(player_3)
        elif rand == 4:
            if not check_list(order, player_4):
                order.append(player_4)
    return order

def check_list(list, player):
    for item in list:
        if item == player:
            return True
    return False

def coin_is_known(i, j, known_coins):
    for pos in known_coins:
        if pos:
            if pos[0] == i and pos[1] == j:
                return True
    return False



def find_nearest_coin(matrix, player_position):
    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    rows, cols = len(matrix), len(matrix[0])
    visited = [[False] * cols for _ in range(rows)]

    queue = deque([(player_position[0], player_position[1], 0)])
    visited[player_position[0]][player_position[1]] = True

    while queue:
        row, col, distance = queue.popleft()

        if matrix[row][col].startswith("Coin"):
            return (row, col), distance

        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            if 0 <= new_row < rows and 0 <= new_col < cols and matrix[new_row][new_col] != "Wall" and not visited[new_row][new_col]:
                visited[new_row][new_col] = True
                queue.append((new_row, new_col, distance + 1))

    return None, float('inf')

def find_path(matrix, start_pos, end_pos):
    directions = [(1, 0, 'DOWN'), (-1, 0, 'UP'), (0, 1, 'RIGHT'), (0, -1, 'LEFT')]
    rows, cols = len(matrix), len(matrix[0])
    parent = {}

    queue = deque([start_pos])

    while queue:
        row, col = queue.popleft()

        if (row, col) == end_pos:
            path = []
            while (row, col) != start_pos:
                row, col = parent[(row, col)]
                path.append((row, col))
            return path[::-1]

        for dr, dc, move in directions:
            new_row, new_col = row + dr, col + dc
            if 0 <= new_row < rows and 0 <= new_col < cols and matrix[new_row][new_col] != "Wall" and (new_row, new_col) not in parent:
                parent[(new_row, new_col)] = (row, col)
                queue.append((new_row, new_col))

    return None

def get_moves(path):
    moves = []
    for (prev_row, prev_col), (row, col) in zip(path[:-1], path[1:]):
        if row - prev_row == 1:
            moves.append('DOWN')
        elif row - prev_row == -1:
            moves.append('UP')
        elif col - prev_col == 1:
            moves.append('RIGHT')
        elif col - prev_col == -1:
            moves.append('LEFT')
    return moves


def random_move():
    rand = random.randint(1, 4)
    if rand == 1:
        return "UP"
    elif rand == 2:
        return "DOWN"
    elif rand == 3:
        return "LEFT"
    elif rand == 4:
        return "RIGHT"
    
def move_opposite(x, y, matrix):
    def find_path_to_opposite_side(matrix, start_pos, end_pos):
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        rows, cols = len(matrix), len(matrix[0])
        visited = [[False] * cols for _ in range(rows)]
        queue = deque([(start_pos[0], start_pos[1], [])])
        visited[start_pos[0]][start_pos[1]] = True

        while queue:
            row, col, path = queue.popleft()

            if (row, col) == end_pos:
                return path

            for dr, dc in directions:
                new_row, new_col = row + dr, col + dc
                if 0 <= new_row < rows and 0 <= new_col < cols and matrix[new_row][new_col] != "Wall" and not visited[new_row][new_col]:
                    visited[new_row][new_col] = True
                    queue.append((new_row, new_col, path + [(new_row, new_col)]))

        return None

    # Find the opposite side of the map
    target_row = 0 if x >= 5 else 9
    target_col = 0 if y >= 5 else 9
    target_position = (target_row, target_col)

    # Find the path to the opposite side
    path_to_opposite = find_path_to_opposite_side(matrix, (x, y), target_position)

    if path_to_opposite:
        moves = get_moves([(x, y)] + path_to_opposite)
        return moves
    else:
        return check_walls(x, y, matrix)


if __name__ == '__main__':
    load_dotenv(dotenv_path='./credentials.env')
    
    broker_address = os.environ.get('BROKER_ADDRESS')
    broker_port = int(os.environ.get('BROKER_PORT'))
    username = os.environ.get('USER_NAME')
    password = os.environ.get('PASSWORD')

    client = paho.Client(callback_api_version=paho.CallbackAPIVersion.VERSION1, client_id="Player1", userdata=None, protocol=paho.MQTTv5)
    
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

    client.loop_start()

    client.subscribe(f"games/{lobby_name}/lobby")
    client.subscribe(f'games/{lobby_name}/+/game_state')
    client.subscribe(f'games/{lobby_name}/scores')

    client.publish("new_game", json.dumps({'lobby_name':lobby_name,
                                            'team_name':'ATeam',
                                            'player_name' : player_1}))
    
    client.publish("new_game", json.dumps({'lobby_name':lobby_name,
                                            'team_name':'ATeam',
                                            'player_name' : player_2}))
    
    client.publish("new_game", json.dumps({'lobby_name':lobby_name,
                                        'team_name':'BTeam',
                                        'player_name' : player_3}))
    
    client.publish("new_game", json.dumps({'lobby_name':lobby_name,
                                        'team_name':'BTeam',
                                        'player_name' : player_4}))
    
    #while True:
    time.sleep(3) # Wait a second to resolve game start
    client.publish(f"games/{lobby_name}/start", "START")
    #client.publish(f"games/{lobby_name}/{player_1}/move", "UP")
    #client.publish(f"games/{lobby_name}/{player_2}/move", "DOWN")
    #client.publish(f"games/{lobby_name}/{player_3}/move", "DOWN")
    #client.publish(f"games/{lobby_name}/start", "STOP")


    #client.loop_forever()
    while (running == True):
        print("while loop")
        time.sleep(1)