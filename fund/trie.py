class Trie:
    def __init__(self):
        self.nodes = dict()
        self.is_leaf = False

    def insert(self, data):
        temp = self.nodes
        for c in data:
            if temp.get(c) is None:
                temp[c] = Trie()
            temp = temp[c]
        temp.is_leaf = True

    def search(self, string) -> bool:
        temp = self.nodes
        for s in string:
            if temp.get(s) is None:
                return False
            temp = temp[s]
        if temp.is_leaf is False:
            return True
        else:
            return False

    def startWith(self, string) -> list:
        temp, res, mystack = self.nodes, [], []
        for s in string:
            if temp.get(s) is None:
                return res
            temp = temp[s]
        for ne in temp.keys():
            if temp[ne].is_leaf is True:
                res.append(string+ne)
            else:
                mystack.append(temp[ne])
        while len(mystack):
            if temp[mystack[0]].is_leaf is False:
                mystack.append(temp[mystack[0]])




