child_seq = []
for child_seqs in child_seq:
    if type(child_seqs) == list:
        s = child_seqs[0]
        print("aha")
    else:
        s = child_seqs
        print("njknjknj")
    print(s)