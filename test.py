
def c_hrl(m):
    print("c_hrl( {} ) is called".format(m))
    seq = []
    reward = 0
    if m == 1:
        seq.append([m, -1])
        reward = 10
    else:
        while m != 1:
            m -= 1
            child_seq, child_reward = c_hrl(m)
            print("c_hrl( {} )".format(m), "get result", child_seq, child_reward)
            seq += child_seq
            reward = reward + child_reward

    return seq, reward

seq = c_hrl(3)
print(seq)
