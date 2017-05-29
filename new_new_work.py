#!/usr/bin/python
# -*- coding: UTF-8 -*-
import random
import threading
from Node import Node
from Agent import Agent

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
epsilon = 0.9

a1 = Agent(1, (1, 3), 0)
# 表示的是Agent(id, state, trash)

t1_end = (4, 0)
dump_end = (7, 7)

# 表示的是Node(type, name, flag, terminal)
M1 = Node('sub-task', 'collect trash at t1', 0, '')
M3 = Node('action', 'navigate to t1', 0, t1_end)
M5 = Node('action', 'navigate to dump', 0, dump_end)
P1 = Node('action', 'pick', '', '')
P2 = Node('action', 'put', '', '')
M1.append_children((M3, M5, P1, P2))

def single_hrl(agent, task):
     if task.type == 'action':
         reward = 0
         old_state = agent.state
         old_trash = agent.trash
         if task.name == 'pick':
             reward = do_pick(agent, task)
             print("pick")
         elif task.name == 'put':
             reward = do_put(agent, task)
             print("put")
         elif task.name == 'navigate to t1':
             reward = do_go_to_t1(agent, task)
             print("go to t1")
         elif task.name == 'navigate to dump':
             reward = do_go_to_dump(agent, task)
             print("go to dump")
         else:
             pass
         old_reward = task.parent.dict.get((agent.id, old_state, old_trash, task.name), None)
         if old_reward is None:
             task.parent.dict[(agent.id, old_state, old_trash, task.name)] = reward
         else:
             task.parent.dict[(agent.id, old_state, old_trash, task.name)] = round(
                 (1 - alpha) * old_reward + alpha * reward, 5)
     else:
         while not terminal(task):
             # sub_task = random.choice(task.get_children())
             sub_task = choose_best_task(agent, task)
             sub_task.parent = task
             single_hrl(agent, sub_task)

def choose_best_task(agent, task):
    names = [x.name for x in task.get_children()]
    q_value = [task.dict.get((agent.id, agent.state, agent.trash, name), 0) for name in names]
    max_q = max(q_value)
    max_q_count = q_value.count(max_q)
    if max_q_count == 1:
        i_index = q_value.index(max_q)
    else:
        i_index_list = [i for i in range(len(names)) if q_value[i] == max_q]
        i_index = random.choice(i_index_list)
    best_task_name = names[i_index]
    global best_task
    for x in task.get_children():
        if x.name == best_task_name:
            best_task = x
    print(agent.id, agent.state, agent.trash, best_task.name)
    return best_task

def terminal(task):
    if task.name == 'collect trash at t1':
        if dump_trash[0] == 1:
            return True
        else:
            return False


def do_pick(agent, task):
    if agent.state == t1_end and trash[0] == 1 and agent.trash == 0:
        # 垃圾桶1里面的垃圾清空,agent拿起垃圾桶1里面的垃圾
        trash[0] = 0
        agent.trash = 1
        reward = 100
    else:
        reward = 0
    return reward

def do_put(agent, task):
    if agent.state == dump_end and agent.trash == 1:
        dump_trash[0] = 1
        agent.trash = 0
        reward = 100
    else:
        reward = 0
    return reward

def do_go_to_t1(agent, task):
    if agent.trash == 0 and agent.state != task.terminal:
        reward = 100
    else:
        reward = 0
    agent.state = task.terminal
    return reward

def do_go_to_dump(agent, task):
    if agent.trash == 1 and agent.state != dump_end:
        reward = 100
    else:
        reward = 0
    agent.state = task.terminal
    return reward

count = 0
while count < 10:
    trash = [1, 1]
    dump_trash = [0, 0]
    single_hrl(a1, M1)
    print(dump_trash)
    print(M1.dict)
    count += 1
    print("第", count, "轮实验")