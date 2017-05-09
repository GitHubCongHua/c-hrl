#!/usr/bin/python
# -*- coding: UTF-8 -*-
import random
import threading
from Node import Node
from Agent import Agent

'''
这个例子是，多agent任务分层，先分层次

两个agent开始位置（先不随机，直接固定吧！），T1和T2位置固定
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
a1 = Agent(1, (6, 3))
a2 = Agent(2, (7, 3))
agent_list = [a1, a2]
t1_end = (0, 0)
t1_trash = 1
t2_end = (7, 7)
t2_trash = 1
dump_end = (0, 7)
dump_trash = [0, 0]
gamma = 0.8
alpha = 0.7
epsilon = 0.9

#  任务分层, 引用定义的Node类
#  node(type1, name, flag, terminal)，+children属性
M0 = Node('c-sub-task', 'root', 0, '')
M1 = Node('sub-task', 'collect trash at t1', 0, '')
M2 = Node('sub-task', 'collect trash at t2', 0, '')
M3 = Node('sub-task', 'navigate to t1', 0, t1_end)
M4 = Node('sub-task', 'navigate to t2', 0, t2_end)
M5 = Node('sub-task', 'navigate to dump', 0, dump_end)
P1 = Node('action_p', 'pick', '', '')
P2 = Node('action_p', 'put', '', '')
C1 = Node('action', (-1, 0), '', '')
C2 = Node('action', (1, 0), '', '')
C3 = Node('action', (0, -1), '', '')
C4 = Node('action', (0, 1), '', '')
M0.append_children((M1, M2))
M1.append_children((M3, M5, P1, P2))
M2.append_children((M4, M5, P1, P2))
M3.append_children((C1, C2, C3, C4))
M4.append_children((C1, C2, C3, C4))
M5.append_children((C1, C2, C3, C4))


# 如果任务结束，返回True；否则返回False
def terminal(task, state):
    if task.name == 'root':
        if dump_trash[0] == 1 and dump_trash[1] == 1:
            return True
        else:
            return False
    elif task.name == 'collect trash at t1':
        if dump_trash[0] == 1:
            return True
        else:
            return False
    elif task.name == 'collect trash at t2':
        if dump_trash[1] == 1:
            return True
        else:
            return False
    elif task.name == 'navigate to t1':
        if state == t1_end:
            return True
        else:
            return False
    elif task.name == 'navigate to t2':
        if state == t2_end:
            return True
        else:
            return False
    elif task.name == 'navigate to dump':
        if state == dump_end:
            return True
        else:
            return False
    else:
        print('error')


def vector_add(a, b):
    return a[0] + b[0], a[1] + b[1]


def get_max_q(state):
    return 100


def get_max_q_joint(state):
    return 100


def c_hrl(agent, task, state):
    # seq is a sequence store states visited and actions of other agents
    seq = []
    next_state = None

    if task.type == 'action':
        destination = task.parent.terminal
        next_state = vector_add(state, task.name)
        if (next_state[0] not in range(8)) or (next_state[1] not in range(8)) \
                or (Grid[next_state[0]][next_state[1]] != 0):
            next_state = state
        if destination == next_state:
            reward = 100
            task.parent.flag = 1
        else:
            reward = -1
        old_reward = task.parent.dict.get((state, task), None)
        if old_reward is None:
            task.parent.dict[(state, task)] = reward
        else:
            task.parent.dict[(state, task)] = round((1-alpha)*old_reward + alpha*reward, 5)

        seq = [state]
        for agents in agent_list:
            if agents != agent:
                if len(agents.u_action) != 0:
                    seq.append(agents.u_action[0])
        print(seq)
    else:
        while not terminal(task, state):
            if task.type == 'c-sub-task':
                sub_task = random.choice(task.get_children())
                child_seq, next_state = c_hrl(agent, sub_task, state)
                max_q_joint = get_max_q_joint(next_state)
                n = 0
                for child_seqs in child_seq:
                    child_seqs.append(sub_task)
                    joint_s_a = child_seqs
                    n += 1
                    print(tuple(joint_s_a))
                    old_reward = task.dict.get(tuple(joint_s_a), None)
                    if old_reward is None:
                        task.dict[tuple(joint_s_a)] = round((gamma**n)*max_q_joint, 5)
                    else:
                        task.dict[tuple(joint_s_a)] = round((1-alpha)*old_reward + alpha*(gamma**n)*max_q_joint, 5)

                if(children.flag == 1 for children in task.get_children()):
                    task.flag = 1

            else:
                sub_task = random.choice(task.get_children())
                sub_task.parent = task
                child_seq, next_state = c_hrl(agent, sub_task, state)
                max_q = get_max_q(next_state)
                n = 0
                for child_seqs in child_seq:
                    s = child_seqs[0]
                    n += 1
                    old_reward = task.dict.get((s, sub_task), None)
                    if old_reward is None:
                        task.dict[(s, sub_task)] = round((gamma**n)*max_q, 5)
                    else:
                        task.dict[(s, sub_task)] = round((1-alpha)*old_reward + alpha*(gamma**n)*max_q, 5)

            seq.append(child_seq)
            state = next_state

    print("agent:", agent.id)
    return seq, next_state

# print(c_hrl(a1, M0, (6, 3)))
# print(c_hrl(a2, M0, (7, 3)))
try:
    t1 = threading.Thread(target=c_hrl, args=(a1, M0, (6, 3)))
    t2 = threading.Thread(target=c_hrl, args=(a2, M0, (7, 3)))
    t1.start()
    t2.start()
    t1.join()
    t2.join()
except ():
    print("Error: unable to start thread")

print(M1.dict)
print(M2.dict)
