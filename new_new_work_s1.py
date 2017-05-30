#!/usr/bin/python
# -*- coding: UTF-8 -*-
import random

Grid = [[0, 0, -1, 0, 0, 0, 0, 0],
        [0, 0, -1, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, -1, 0, 0],
        [-1, -1, -1, 0, 0, -1, 0, 0],
        [0, 0, -1, 0, 0, -1, 0, 0],
        [0, 0, -1, 0, 0, -1, 0, 0],
        [0, 0, -1, 0, 0, -1, 0, 0],
        [0, 0, 0, 0, 0, -1, 0, 0]
        ]
gamma = 0.8
alpha = 0.7

directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]


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


def get_reward(state, action, destination):
    if vector_add(state, action) == destination:
        return 100
    else:
        return 0


def get_max_q(state, task):
    actions = get_can_direction(state)
    max_q = max([task.dict.get((state, a), 0) for a in actions])
    return max_q


def get_best_action(state, task):
    actions = get_can_direction(state)
    q_value = [task.dict.get((state, a), 0) for a in actions]
    max_q = max(q_value)
    max_q_count = q_value.count(max_q)
    if max_q_count == 1:
        i_index = q_value.index(max_q)
    else:
        i_index_list = [i for i in range(len(actions)) if q_value[i] == max_q]
        i_index = random.choice(i_index_list)
    best_action = actions[i_index]
    return best_action


def learning_q(state, destination, task, step):

    action = get_best_action(state, task)

    next_state = vector_add(state, action)
    step += 1

    # <<------------更新学习到的Q_dict部分----------->>
    reward = get_reward(state, action, destination)
    max_q = get_max_q(next_state, task)
    old_reward = task.dict.get((state, action), None)
    if old_reward is None:
        task.dict[(state, action)] = reward + gamma * max_q
    else:
        task.dict[(state, action)] = round((1 - alpha) * old_reward + alpha * (reward + gamma * max_q), 5)
    # <<------------更新学习到的Q_dict部分----------->>

    print(next_state, "这次导航子任务已迈出步数：", step)
    if next_state == destination:
        print("到达子任务目标地点！", "  这次导航子任务累计步数：", step)
        return None, step
    else:
        return next_state, step


