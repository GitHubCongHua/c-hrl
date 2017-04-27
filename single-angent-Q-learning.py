#!/usr/bin/python
# -*- coding: UTF-8 -*-
import random

#初始化Q矩阵全为0，初始化R矩阵
Q = [[0 for i in range(6)] for i in range(6)]
R = [[-1,-1,-1,-1,0,-1],[-1,-1,-1,0,-1,100],[-1,-1,-1,0,-1,-1],
    [-1,0,0,-1,0,-1],[0,-1,-1,0,-1,100],[-1,0,-1,-1,0,100]]
gamma = 0.8
alpha = 1
print(R)
print(Q)

def get_can_go(state):
    can_go = []
    for i in range(6):
        if (R[state][i] >= 0):
            can_go.append(i)
    return can_go


def learning_Q(state,count):
    print(state)
    can_go_result = get_can_go(state)
    action = random.choice(can_go_result)
    count += 1
    print(action, "递归次数：：：",count)
    # 重要部分：公式
    maxQ = max(Q[action])
    Q[state][action] = (1-alpha)*Q[state][action] + alpha*(R[state][action] + gamma*maxQ)
    if (R[state][action] == 100):
        state = random.choice(range(6))
        return 0
    else:
        state = action
        learning_Q(state, count)

    return 0

flag = 0
count = 0
ex_count = 0
while (ex_count <= 4):
    state = random.choice(range(6))
    print("***********************************state**************",state)
    print(Q)
    learning_Q(state, count)
    ex_count += 1
    print("实验次数：", ex_count)

print(Q)








