def c_hrl(m):
    seq = []
    if m == 1:
        seq.append([m])
    else:
        while m != 1:
            m -= 1
            child_seq = c_hrl(m)
            print(child_seq)
            seq += child_seq
    return seq

seq = c_hrl(5)
print(seq)
