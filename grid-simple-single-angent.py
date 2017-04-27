#!/usr/bin/python
# -*- coding: UTF-8 -*-
import random

'''
这个例子是在格子中，一个agent学习最快到底目的地，
agent开始位置随机，目的地一定，这个例子中目的地是（0，0）左上角位置
'''
# 初始化格子布局状态，-1代表墙不能走，0代表可以通行的格子
Grid = [[0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, -1, -1, -1, -1, -1],
        [0, 0, 0, -1, 0, 0, 0, 0],
        [0, 0, 0, -1, 0, 0, 0, 0],
        [0, 0, 0, -1, 0, -1, 0, 0],
        [0, 0, 0, 0, 0, -1, 0, 0],
        [-1, -1, 0, 0, 0, -1, 0, 0],
        [-1, -1, 0, 0, 0, -1, 0, 0]
        ]
destination = (0, 0)
gamma = 0.8
alpha = 0.7
epsilon = 0.9
# Q-learning学习之后更新的列表，不断添加列表行，[位置(x,y)，行为(dx,dy)，奖赏Reward]
Q_dict = {}
directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]


def choice_start():
    start = (random.choice(range(8)), random.choice(range(8)))
    while Grid[start[0]][start[1]] == -1:
        start = (random.choice(range(8)), random.choice(range(8)))
    print("开始起点位置：", start)
    return start


def vector_add(a, b):
    return a[0] + b[0], a[1] + b[1]


def get_can_direction(state):
        temp = []
        for i in range(len(directions)):
                temp.append(vector_add(state, directions[i]))
        can_direction = []
        for i in range(len(directions)):
                if ((temp[i][0] in range(8)) and (temp[i][1] in range(8))
                        and (Grid[temp[i][0]][temp[i][1]] == 0)):
                        can_direction.append(directions[i])
        return can_direction


def get_reward(state, action):
    if vector_add(state, action) == destination:
        return 100
    else:
        return 0


def get_max_q(state):
    actions = get_can_direction(state)
    max_q = max([Q_dict.get((state, a), 0) for a in actions])
    return max_q


def learning_q(state, step):
        # 加入探索概率
        if random.random() < epsilon:
            can_direction = get_can_direction(state)
            action = random.choice(can_direction)
        else:
            action = get_best_action(state)

        next_state = vector_add(state, action)
        step += 1

        # <<------------更新学习到的Q_dict部分----------->>
        reward = get_reward(state, action)
        max_q = get_max_q(next_state)
        old_reward = Q_dict.get((state, action), None)
        if old_reward is None:
            Q_dict[(state, action)] = reward + gamma*max_q
        else:
            Q_dict[(state, action)] = round((1 - alpha)*old_reward + alpha*(reward + gamma*max_q), 5)
        # <<------------更新学习到的Q_dict部分----------->>

        print(next_state, "此次探索已迈出步数：", step)
        if next_state == destination:
            print("到达终点！", "  此次探索累计步数：", step)
            return None, None
        else:
            return next_state, step


def get_best_action(state):
    actions = get_can_direction(state)
    q_value = [Q_dict.get((state, a), 0) for a in actions]
    max_q = max(q_value)
    max_q_count = q_value.count(max_q)
    if max_q_count == 1:
        i_index = q_value.index(max_q)
    else:
        i_index_list = [i for i in range(len(actions)) if q_value[i] == max_q]
        i_index = random.choice(i_index_list)
    best_action = actions[i_index]
    return best_action


count = 0
while count < 100:
    start_position = choice_start()
    num_step = 0
    if start_position != destination:
        state_position, num_steps = learning_q(start_position, num_step)
        while state_position is not None:
            state_position, num_steps = learning_q(state_position, num_steps)
    else:
        print("现在已经位于终点")
    count += 1
    print("完成探索次数：", count)


print(Q_dict)
# for value in range(len(Q_dict)):
#     if Q_dict.values()[value] != 0:
#         print Q_dict.values()[value]


while True:

    try:
        x = input("请输入开始位置（表示位置的元组）(eg.输入3,4)：")
        input_position = tuple(eval(x))
        if type(input_position) is not tuple:
            print("输入不规范，不是元组，请重新输入")
            continue
    except (NameError, SyntaxError, TypeError):
        print("输入类型错误")
        continue

    if input_position == destination:
        print("已经位于目的地")
    elif (input_position[0] not in range(8) or input_position[1] not in range(8) or
          Grid[input_position[0]][input_position[1]] == -1):
        print("输入位置不合理，请重新输入")
    else:
        position = input_position
        # 路径存起来，然后逆向输出路径
        position_list = []
        while position != destination:
            the_action = get_best_action(position)
            position = vector_add(position, the_action)
            print(position)
            position_list.append(position)
        position_list.reverse()
        print(position_list)
        print("抵达目的地")
