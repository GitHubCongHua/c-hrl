
class Agent:

    def __init__(self, id, state, trash):
        self.id = id
        self.state = state
        self.u_action = list()
        self.trash = trash

    def get_u_action(self):
        return self.u_action

    def add_u_action(self, node):
        self.u_action.append(node)
