import sys
import socket
from collections import deque
import heapq

##############################
# 메인 프로그램 통신 변수 정의
##############################
HOST = '127.0.0.1'
PORT = 8747
ARGS = sys.argv[1] if len(sys.argv) > 1 else ''
sock = socket.socket()


##############################
# 메인 프로그램 통신 함수 정의
##############################

# 메인 프로그램 연결 및 초기화
def init(nickname):
    try:
        print(f'[STATUS] Trying to connect to {HOST}:{PORT}...')
        sock.connect((HOST, PORT))
        print('[STATUS] Connected')
        init_command = f'INIT {nickname}'
        return submit(init_command)
    except Exception as e:
        print('[ERROR] Failed to connect. Please check if the main program is waiting for connection.')
        print(e)


# 메인 프로그램으로 데이터(명령어) 전송
def submit(string_to_send):
    try:
        send_data = ARGS + string_to_send + ' '
        sock.send(send_data.encode('utf-8'))
        return receive()
    except Exception as e:
        print('[ERROR] Failed to send data. Please check if connection to the main program is valid.')
    return None


# 메인 프로그램으로부터 데이터 수신
def receive():
    try:
        game_data = (sock.recv(1024)).decode()
        if game_data and game_data[0].isdigit() and int(game_data[0]) > 0:
            return game_data
        print('[STATUS] No receive data from the main program.')
        close()
    except Exception as e:
        print('[ERROR] Failed to receive data. Please check if connection to the main program is valid.')


# 연결 해제
def close():
    try:
        if sock is not None:
            sock.close()
        print('[STATUS] Connection closed')
    except Exception as e:
        print('[ERROR] Network connection has been corrupted.')


##############################
# 입력 데이터 변수 정의
##############################
map_data = [[]]
my_allies = {}
enemies = {}
codes = []


##############################
# 입력 데이터 파싱
##############################
def parse_data(game_data):
    game_data_rows = game_data.split('\n')
    row_index = 0
    header = game_data_rows[row_index].split(' ')
    map_height = int(header[0]) if len(header) >= 1 else 0
    map_width = int(header[1]) if len(header) >= 2 else 0
    num_of_allies = int(header[2]) if len(header) >= 3 else 0
    num_of_enemies = int(header[3]) if len(header) >= 4 else 0
    num_of_codes = int(header[4]) if len(header) >= 5 else 0
    row_index += 1

    map_data.clear()
    map_data.extend([['' for c in range(map_width)] for r in range(map_height)])
    for i in range(map_height):
        col = game_data_rows[row_index + i].split(' ')
        for j in range(len(col)):
            map_data[i][j] = col[j]
    row_index += map_height

    my_allies.clear()
    for i in range(row_index, row_index + num_of_allies):
        ally = game_data_rows[i].split(' ')
        ally_name = ally.pop(0) if ally else '-'
        my_allies[ally_name] = ally
    row_index += num_of_allies

    enemies.clear()
    for i in range(row_index, row_index + num_of_enemies):
        enemy = game_data_rows[i].split(' ')
        enemy_name = enemy.pop(0) if enemy else '-'
        enemies[enemy_name] = enemy
    row_index += num_of_enemies

    codes.clear()
    for i in range(row_index, row_index + num_of_codes):
        codes.append(game_data_rows[i])


def print_data():
    print(f'\n----------입력 데이터----------\n{game_data}\n----------------------------')
    print(f'\n[맵 정보] ({len(map_data)} x {len(map_data[0])})')
    for row in map_data:
        print(' '.join(row))
    print(f'\n[아군 정보] (아군 수: {len(my_allies)})')
    for k, v in my_allies.items():
        if k == 'M':
            print(f'M (내 탱크) - 체력: {v[0]}, 방향: {v[1]}, 일반 포탄: {v[2]}개, 메가 포탄: {v[3]}개')
        elif k == 'H':
            print(f'H (아군 포탑) - 체력: {v[0]}')
        else:
            print(f'{k} (아군 탱크) - 체력: {v[0]}')
    print(f'\n[적군 정보] (적군 수: {len(enemies)})')
    for k, v in enemies.items():
        if k == 'X':
            print(f'X (적군 포탑) - 체력: {v[0]}')
        else:
            print(f'{k} (적군 탱크) - 체력: {v[0]}')
    print(f'\n[암호문 정보] (암호문 수: {len(codes)})')
    for code in codes:
        print(code)


##############################
# 닉네임 설정 및 최초 연결
##############################
NICKNAME = '서울3_문희원'
game_data = init(NICKNAME)


###################################
# 알고리즘 함수/메서드 부분 구현 시작
###################################
def close_find_positions(grid, starts, goal_mark):
    start = goal = None
    distance = []
    close_positions = 0
    for r, row_data in enumerate(grid):
        for c, cell in enumerate(row_data):
            for start_mark in starts:
                if cell == start_mark:
                    start = (r, c)
                elif cell == goal_mark:
                    goal = (r, c)
                
                distance.append(abs(goal[0] - start[0]) + abs(goal[1] - start[1]))
                if min(distance) == (abs(goal[0] - start[0]) + abs(goal[1] - start[1])):
                    close_positions = start_mark
    
    if close_positions == 'M':
        return 1
    else:
        return 2

cnt = close_find_positions(map_data, ['M', 'M1', 'M2'], 'X')


def decrypt_caesar(ciphertext):
    result = ""
    shift = 17
    for char in ciphertext:
        if 'A' <= char <= 'Z':
            result += chr(((ord(char) - ord('A') - shift + 26) % 26) + ord('A'))
        else:
            result += char
    return result


def find_positions(grid, start_mark, goal_mark):
    start = goal = None
    for r, row_data in enumerate(grid):
        for c, cell in enumerate(row_data):
            if cell == start_mark:
                start = (r, c)
            elif cell == goal_mark:
                goal = (r, c)
    return start, goal


def find_allied_tank_positions(grid, allies_dict):
    positions = set()
    ally_tank_names = {name for name in allies_dict.keys() if name not in ['M', 'H']}
    for r, row_data in enumerate(grid):
        for c, cell in enumerate(row_data):
            if cell in ally_tank_names:
                positions.add((r, c))
    return positions


# [NEW] 적 체력에 따라 다른 포탄을 사용하도록 수정
def find_immediate_attack_command(grid, start, enemies_dict, my_tank_info):
    rows, cols = len(grid), len(grid[0])
    r, c = start
    shot_blocking_obstacles = {'R', 'F'}

    # 방향별로 탐색 (R, D, L, U)
    for direction, (dr, dc) in {'R': (0, 1), 'D': (1, 0), 'L': (0, -1), 'U': (-1, 0)}.items():
        for k in range(1, 4):
            nr, nc = r + (dr * k), c + (dc * k)

            if not (0 <= nr < rows and 0 <= nc < cols):
                break  # 맵 범위를 벗어나면 중단

            # 시야를 가로막는 바위가 있는지 확인
            is_blocked = False
            for j in range(1, k):
                br, bc = r + (dr * j), c + (dc * j)
                if grid[br][bc] in shot_blocking_obstacles:
                    is_blocked = True
                    break
            if is_blocked:
                break

            target_name = grid[nr][nc]
            # 적 탱크('E1', 'E2', ...)인 경우
            if target_name in enemies_dict and target_name != 'X':
                enemy_hp = int(enemies_dict[target_name][0])
                has_mega_cannon = int(my_tank_info[3]) >= 1

                # 체력이 30 초과이고 메가 포탄이 있으면 메가 포탄 사용
                if enemy_hp > 30 and has_mega_cannon:
                    return f'{direction} F M'
                else:  # 그 외에는 일반 포탄 사용
                    return f'{direction} F'

            # 적 포탑('X')인 경우
            elif target_name == 'X':
                has_mega_cannon = int(my_tank_info[3]) >= 1
                # 메가 포탄이 있으면 사용, 없으면 일반 포탄
                return f'{direction} F M' if has_mega_cannon else f'{direction} F'

    return None


def find_nearest_f_tile(grid, start, temp_obstacles=set()):
    rows, cols = len(grid), len(grid[0])
    queue = deque([(start, 0)])
    visited = {start}
    dirs = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    while queue:
        (r, c), dist = queue.popleft()
        if grid[r][c] == 'F': return (r, c)
        for dr, dc in dirs:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and (nr, nc) not in visited and grid[nr][nc] not in ['R', 'W',
                                                                                                      'T'] and (
            nr, nc) not in temp_obstacles:
                visited.add((nr, nc))
                queue.append(((nr, nc), dist + 1))
    return None


def find_shortest_path(grid, start, targets, temp_obstacles=set()):
    if not isinstance(targets, set):
        targets = {targets}

    rows, cols = len(grid), len(grid[0])
    pq = [(0, start, [])]
    visited = {start: 0}
    dirs = {'R': (0, 1), 'D': (1, 0), 'L': (0, -1), 'U': (-1, 0)}

    while pq:
        cost, pos, path = heapq.heappop(pq)
        if pos in targets: return path
        if cost > visited.get(pos, float('inf')): continue

        for direction, (dr, dc) in dirs.items():
            nr, nc = pos[0] + dr, pos[1] + dc
            if not (0 <= nr < rows and 0 <= nc < cols): continue
            if (nr, nc) in temp_obstacles: continue

            neighbor_tile = grid[nr][nc]
            if neighbor_tile in ['R', 'W', 'F']: continue

            actions_to_add = []
            if neighbor_tile == 'T':
                new_cost = cost + 2
                actions_to_add.extend([f'{direction} F', f'{direction} A'])
            else:
                new_cost = cost + 1
                actions_to_add.append(f'{direction} A')

            if new_cost < visited.get((nr, nc), float('inf')):
                visited[(nr, nc)] = new_cost
                heapq.heappush(pq, (new_cost, (nr, nc), path + actions_to_add))
    return None


START_SYMBOL = 'M'
TARGET_SYMBOL = 'X'
initial_mega_cannons_secured = False  # [NEW] 메가 포탄 2개 획득 완료 여부 플래그

if game_data: parse_data(game_data)
###################################
# 알고리즘 함수/메서드 부분 구현 끝
###################################

while game_data is not None:
    print_data()
    my_pos, target_pos = find_positions(map_data, START_SYMBOL, TARGET_SYMBOL)
    output = 'A'

    if my_pos:
        # [NEW] 메가 포탄을 2개 이상 보유했다면, 다시는 보급로를 찾지 않도록 플래그 설정
        if not initial_mega_cannons_secured and int(my_allies['M'][3]) >= cnt:
            initial_mega_cannons_secured = True

        allied_tank_coords = find_allied_tank_positions(map_data, my_allies)

        attack_command = find_immediate_attack_command(map_data, my_pos, enemies, my_allies['M'])
        if attack_command:
            output = attack_command
        else:
            path = None
            # [NEW] 최초 2개 획득 전이고, 현재 2개 미만일 때만 보급로 방문
            if not initial_mega_cannons_secured and int(my_allies['M'][3]) < cnt:
                nearest_f_pos = find_nearest_f_tile(map_data, my_pos, allied_tank_coords)
                if nearest_f_pos and codes:
                    is_adjacent = abs(nearest_f_pos[0] - my_pos[0]) + abs(nearest_f_pos[1] - my_pos[1]) == 1

                    if is_adjacent:
                        output = f'G {decrypt_caesar(codes[0])}'
                    else:
                        adjacent_targets = set()
                        for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                            nr, nc = nearest_f_pos[0] + dr, nearest_f_pos[1] + dc
                            if 0 <= nr < len(map_data) and 0 <= nc < len(map_data[0]) and map_data[nr][nc] not in ['R',
                                                                                                                   'T',
                                                                                                                   'F',
                                                                                                                   'W'] and (
                            nr, nc) not in allied_tank_coords:
                                adjacent_targets.add((nr, nc))

                        if adjacent_targets:
                            path = find_shortest_path(map_data, my_pos, adjacent_targets, allied_tank_coords)

            if output == 'A' and target_pos:
                path = find_shortest_path(map_data, my_pos, target_pos, allied_tank_coords)

            if path:
                output = path[0]

    print(f'>>> My Action: {output}')
    game_data = submit(output)
    if not game_data: break
    parse_data(game_data)

close()