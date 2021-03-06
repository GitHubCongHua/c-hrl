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
# Grid = [[0, 0, 0, 0, 0, 0, 0, 0],
#         [0, 0, 0, -1, -1, -1, -1, -1],
#         [0, 0, 0, -1, 0, 0, 0, 0],
#         [0, 0, 0, -1, 0, 0, 0, 0],
#         [0, 0, 0, -1, 0, -1, 0, 0],
#         [0, 0, 0, 0, 0, -1, 0, 0],
#         [-1, -1, 0, 0, 0, -1, 0, 0],
#         [-1, -1, 0, 0, 0, -1, 0, 0]
#         ]
Grid = [[0, 0, -1, 0, 0, 0, 0, 0],
        [0, 0, -1, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, -1, 0, 0],
        [-1, -1, -1, 0, 0, -1, 0, 0],
        [0, 0, -1, 0, 0, -1, 0, 0],
        [0, 0, -1, 0, 0, -1, 0, 0],
        [0, 0, -1, 0, 0, -1, 0, 0],
        [0, 0, 0, 0, 0, -1, 0, 0]
        ]
a1 = Agent(1, (1, 3), 0)
a2 = Agent(2, (7, 3), 0)
agent_list = [a1, a2]
t2_end = (0, 0)
t1_end = (4, 0)
dump_end = (7, 7)
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
P1 = Node('action', 'pick', '', '')
P2 = Node('action', 'put', '', '')
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
    if dump_trash[0] == 1 and dump_trash[1] == 1:
        return True
    elif task.name == 'root':
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


# 这里还缺少联合的q值的那个，就是加了别的智能体的行为，缺少判断和处理！！！？？？
# 但是用到学习中够了，在c_hrl中可以了；c_work中要用的话，还需要添加
def get_q_value(agent_id, task, state, agent_trash, sub_task):
    if sub_task.type == 'action':
        c_value = task.dict.get((agent_id, state, agent_trash, sub_task), 0)
        v_value = sub_task.dict.get((agent_id, task, state, agent_trash, sub_task), 0)
        return c_value + v_value
    else:
        c_value = task.dict.get((agent_id, state, sub_task), 0)
        # 根据策略选择下一个子任务，但是这个子任务只根据最大值选择？还是随机？
        sub_sub_task = random.choice(sub_task.get_children())
        v_value = get_q_value(agent_id, sub_task, state, agent_trash, sub_sub_task)
        return c_value + v_value


def get_max_q(agent_id, task, state, agent_trash):
    sub_tasks = task.get_children()
    # 调用了get_q_value函数
    max_q = max([get_q_value(agent_id, task, state, agent_trash, sub_task) for sub_task in sub_tasks])
    return max_q


# 两处都调用了get_q_value函数，但是选取子任务的策略：最大？？随机？？
def get_max_q_joint(agent_id, task, state, agent_trash, other_action_list):
    sub_tasks = task.get_children()
    if len(other_action_list) == 0:
        max_q_joint = max([(task.dict.get((agent_id, state, sub_task), 0)
                            + get_q_value(agent_id, sub_task, state, agent_trash, random.choice(sub_task.get_children())))
                           for sub_task in sub_tasks])
    else:
        # 由于这里只有一个值，所以不用列表再拼接了
        # 如果换成多于两个agent，这里就必须要改
        other_action = other_action_list[0]
        max_q_joint = max([(task.dict.get((agent_id, state, other_action, sub_task), 0)
                            + get_q_value(agent_id, sub_task, state, agent_trash, random.choice(sub_task.get_children())))
                           for sub_task in sub_tasks])
    return max_q_joint


def get_thread_name():
    return threading.current_thread().getName()


def prim_action_after(task, agent, state, reward, seq):
    old_reward = task.dict.get((agent.id, state, task), None)
    if old_reward is None:
        task.dict[(agent.id, task.parent, state, agent.trash, task)] = reward
    else:
        task.dict[(agent.id, task.parent, state, agent.trash, task)] = round((1 - alpha) * old_reward + alpha * reward, 5)
    temp_seq = [state]
    for agents in agent_list:
        if agents != agent:
            if len(agents.u_action) != 0:
                temp_seq.append(agents.u_action[0])
    seq.append(temp_seq)


def do_action(agent, task, state, seq):
    destination = task.parent.terminal
    next_state = vector_add(state, task.name)
    if (next_state[0] not in range(8)) or (next_state[1] not in range(8)) \
            or (Grid[next_state[0]][next_state[1]] != 0):
        next_state = state
        reward = 0
    else:
        next_state = vector_add(state, task.name)
        if destination == next_state:
            reward = 100
        else:
            reward = 0

    # 执行函数
    prim_action_after(task, agent, state, reward, seq)

    return seq, next_state


def do_pick(agent, task, state, seq):
    if task.parent.name == "collect trash at t1":
        if state == t1_end and trash[0] == 1 and agent.trash == 0:
            # 垃圾桶1里面的垃圾清空,agent拿起垃圾桶1里面的垃圾
            trash[0] = 0
            agent.trash = 1
            print('agent', agent.id, 'pick the trash in t1')
            reward = 100
        else:
            reward = 0
    elif task.parent.name == "collect trash at t2":
        if state == t2_end and trash[1] == 1 and agent.trash == 0:
            # 垃圾桶2里面的垃圾清空,agent拿起垃圾桶2里面的垃圾
            trash[1] = 0
            agent.trash = 2
            print('agent', agent.id, 'pick the trash in t2')
            reward = 100
        else:
            reward = 0
    else:
        print('在pick这步出错了额')

    next_state = state

    prim_action_after(task, agent, state, reward, seq)

    return seq, next_state


def do_put(agent, task, state, seq):
    if task.parent.name == "collect trash at t1":
        if state == dump_end and agent.trash == 1:
            reward = 100
            dump_trash[0] = 1
            agent.trash = 0
            print('agent', agent.id, 'put the trash in t1 into dump')
        else:
            reward = 0
    elif task.parent.name == "collect trash at t2":
        if state == dump_end and agent.trash == 2:
            reward = 100
            dump_trash[1] = 1
            agent.trash = 0
            print('agent', agent.id, 'put the trash in t2 into dump')
        else:
            reward = 0
    else:
        print('在put这步出错了额')
    next_state = state

    prim_action_after(task, agent, state, reward, seq)

    return seq, next_state


def get_depth(a_list):
    if type(a_list) != list:
        return 0
    try:
        if type(a_list[0]) != list:
            return 1
        elif type(a_list[0][0]) != list:
            return 2
        else:
            return 3
    except:
        return 1


def do_extra(agent, task, state, seq):
    while not terminal(task, state):
        # print(terminal(task, state), state, task.name, 'agent', agent.id)

        if task.type == 'c-sub-task':
            sub_task = random.choice(task.get_children())
            if len(agent.u_action) == 0:
                agent.u_action.append(sub_task)
            else:
                agent.u_action[0] = sub_task
            child_seq, next_state = c_hrl(agent, sub_task, state)
            # 获得其他agent在合作层采取的行为
            # 由于这里其他agent只有一个，直接
            temp_list = []
            for agents in agent_list:
                if agents != agent:
                    if len(agents.u_action) != 0:
                        temp_list.append(agents.u_action[0])
            max_q_joint = get_max_q_joint(agent.id, task, next_state, agent.trash, temp_list)
            n = 0
            for each_child_seq in child_seq:
                each_child_seq.append(sub_task)
                joint_s_a = each_child_seq
                joint_s_a.insert(0, agent.id)
                n += 1
                try:
                    old_reward = task.dict.get(tuple(joint_s_a), None)
                except TypeError:
                    pass
                    exit()
                if old_reward is None:
                    task.dict[tuple(joint_s_a)] = round((gamma ** n) * max_q_joint, 5)
                else:
                    task.dict[tuple(joint_s_a)] = round((1 - alpha) * old_reward + alpha * (gamma ** n) * max_q_joint,
                                                        5)

        else:
            sub_task = random.choice(task.get_children())
            sub_task.parent = task
            child_seq, next_state = c_hrl(agent, sub_task, state)
            if next_state is None:
                next_state = state
            max_q = get_max_q(agent.id, task, next_state, agent.trash)
            n = 0
            for child_seqs in child_seq:
                s = child_seqs[0]
                n += 1
                old_reward = task.dict.get((agent.id, s, agent.trash, sub_task), None)
                if old_reward is None:
                    task.dict[(agent.id, s, sub_task)] = round((gamma ** n) * max_q, 5)
                else:
                    task.dict[(agent.id, s, sub_task)] = round((1 - alpha) * old_reward + alpha * (gamma ** n) * max_q, 5)

        seq += child_seq
        # print('child', seq, get_thread_name())
        state = next_state
    return seq, state


def c_hrl(agent, task, state):
    seq = []
    global step
    if task.name == (0, -1) or task.name == (0, 1) or task.name == (1, 0) or task.name == (-1, 0):
        return do_action(agent, task, state, seq)
    elif task.name == 'pick':
        return do_pick(agent, task, state, seq)
    elif task.name == 'put':
        return do_put(agent, task, state, seq)
    else:
        step += 1
        return do_extra(agent, task, state, seq)


count = 0
while count < 1:
    trash = [1, 1]
    dump_trash = [0, 0]
    step = 0
    try:
        t1 = threading.Thread(target=c_hrl, args=(a1, M0, (1, 3)), name="agent-1")
        t2 = threading.Thread(target=c_hrl, args=(a2, M0, (7, 3)), name="agent-2")
        t1.start()
        t2.start()
        t1.join()
        t2.join()
    except ():
        print("Error: unable to start thread")

    # print(M0.dict)
    # print(M1.dict)
    # print(M2.dict)
    # print(M3.dict)
    # print(M4.dict)
    # print(M5.dict)
    # print(P1.dict)
    # print(P2.dict)
    # print(C1.dict)
    # print(C2.dict)
    # print(C3.dict)
    # print(C4.dict)
    count += 1
    print('第', count, '次探索')
    print('所用步数：', step)
    print(dump_trash)


def c_work(agent, task):
    global step
    if task.name == (0, -1) or task.name == (0, 1) or task.name == (1, 0) or task.name == (-1, 0):
        next_state = vector_add(agent.state, task.name)
        if (next_state[0] not in range(8)) or (next_state[1] not in range(8)) \
                or (Grid[next_state[0]][next_state[1]] != 0):
            next_state = agent.state
        else:
            next_state = vector_add(agent.state, task.name)
        agent.state = next_state
        print(agent.state)
    elif task.name == 'pick':
        if task.parent.name == "collect trash at t1":
            if agent.state == t1_end and trash[0] == 1 and agent.trash == 0:
                # 垃圾桶1里面的垃圾清空,agent拿起垃圾桶1里面的垃圾
                trash[0] = 0
                agent.trash = 1
                print('agent', agent.id, 'pick the trash in t1')
        else:
            if agent.state == t2_end and trash[1] == 1 and agent.trash == 0:
                # 垃圾桶2里面的垃圾清空,agent拿起垃圾桶2里面的垃圾
                trash[1] = 0
                agent.trash = 2
                print('agent', agent.id, 'pick the trash in t2')
    elif task.name == 'put':
        if task.parent.name == "collect trash at t1":
            if agent.state == dump_end and agent.trash == 1:
                dump_trash[0] = 1
                agent.trash = 0
                print('agent', agent.id, 'put the trash in t1 into dump')
        else:
            if agent.state == dump_end and agent.trash == 2:
                dump_trash[1] = 1
                agent.trash = 0
                print('agent', agent.id, 'put the trash in t2 into dump')
    else:
        step += 1
        print(task.name, agent.state)
        while not terminal(task, agent.state):
            if task.type == 'c-sub-task':
                # 获得其他agent在合作层采取的行为
                # 由于这里其他agent只有一个，直接
                temp_list = []
                for agents in agent_list:
                    if agents != agent:
                        if len(agents.u_action) != 0:
                            temp_list.append(agents.u_action[0])
                # sub_task = random.choice(task.get_children())
                sub_task = choose_task_joint(task, agent.id, agent.state, temp_list, agent.trash)
                sub_task.parent = task
                c_work(agent, sub_task)
            elif task.name == 'collect trash at t1':
                print("njkkfjvf:collect trash at t1")
                flag = 1
                # sub_task = choose_task_cong(agent, t1_end, flag)
                sub_task = choose_task(task, agent.id, agent.state, agent.trash)
                print(sub_task.name)
                sub_task.parent = task
                c_work(agent, sub_task)
            elif task.name == 'collect trash at t2':
                print("ndfghjksdfghjjkkfjvf:collect trash at t2")
                flag = 2
                # sub_task = choose_task_cong(agent, t2_end, flag)
                sub_task = choose_task(task, agent.id, agent.state, agent.trash)
                print(sub_task.name)
                sub_task.parent = task
                c_work(agent, sub_task)
            else:
                # sub_task = random.choice(task.get_children())
                # sub_task = choose_task(task, agent.id, agent.state, agent.trash)
                # sub_task.parent = task
                # c_work(agent, sub_task)
                agent.state = task.terminal
                c_work(agent, task)


def choose_task_cong(agent, destination, flag):
    if agent.state == destination and agent.trash == 0:
        return P1
    elif agent.state == dump_end and agent.trash == flag:
        return P2
    elif agent.state != dump_end and agent.trash == flag:
        return M5
    elif agent.state != destination and agent.trash == 0 and flag == 1:
        return M3
    elif agent.state != destination and agent.trash == 0 and flag == 2:
        return M4
    else:
        print("choose_task_cong函数出错了")


def choose_task_joint(task, agent_id, state, other_action_list, agent_trash):
    print('choose_task_joint')
    sub_tasks = task.get_children()
    if len(other_action_list) == 0:
        q_value = [(task.dict.get((agent_id, state, sub_task), 0)
                    + get_q_value(agent_id, sub_task, state, agent_trash, random.choice(sub_task.get_children())))
                   for sub_task in sub_tasks]
    else:
        # 由于这里只有一个值，所以不用列表再拼接了
        # 如果换成多于两个agent，这里就必须要改
        other_action = other_action_list[0]
        q_value = [(task.dict.get((agent_id, state, other_action, sub_task), 0)
                   + get_q_value(agent_id, sub_task, state, agent_trash, random.choice(sub_task.get_children())))
                   for sub_task in sub_tasks]
    # 求获得最大值q值的子节点，与下面函数choose_task一样，精简时可抽象出来
    max_q = max(q_value)
    max_q_count = q_value.count(max_q)
    if max_q_count == 1:
        i_index = q_value.index(max_q)
    else:
        i_index_list = [i for i in range(len(sub_tasks)) if q_value[i] == max_q]
        i_index = random.choice(i_index_list)
    best_sub_task = sub_tasks[i_index]
    return best_sub_task


def choose_task(task, agent_id, state, agent_trash):
    print("choose_task")
    sub_tasks = task.get_children()
    q_value = [get_q_value(agent_id, task, state, agent_trash, sub_task) for sub_task in sub_tasks]

    max_q = max(q_value)
    print(q_value, agent_id, task.name, state, 'agent_trash:', agent_trash ,max_q,[task.name for task in sub_tasks])
    max_q_count = q_value.count(max_q)
    if max_q_count == 1:
        i_index = q_value.index(max_q)
    else:
        i_index_list = [i for i in range(len(sub_tasks)) if q_value[i] == max_q]
        i_index = random.choice(i_index_list)
    best_sub_task = sub_tasks[i_index]
    print(best_sub_task.name)
    # print(best_sub_task.name)
    return best_sub_task

# 【！未完成】将探索概率降为0，验证探索多次之后的学习效果
try:
    trash = [1, 1]
    dump_trash = [0, 0]
    step = 0
    print(M3.name)
    t1 = threading.Thread(target=c_work, args=(a1, M0))
    t2 = threading.Thread(target=c_work, args=(a2, M0))
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    print('完成垃圾回收', dump_trash)
    print('所用步数：', step)
except ():
    print("Error: unable to start thread")
