class Node:

    def __init__(self, type1, name, flag, terminal):
        self.children = list()
        self.type = type1
        self.name = name
        self.flag = flag
        self.terminal = terminal
        self.dict = {}                # 通过学习不断更新的值
        self.parent = Node

    def get_children(self):
        return self.children

    def append_children(self, nodes):
        for node in nodes:
            self.children.append(node)





