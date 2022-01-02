class NonBinTree:

    def __init__(self, val):
        self.val = val
        self.nodes = []

    def add_node(self, val):
        self.nodes.append(NonBinTree(val))
        return self.nodes[-1]

    def __repr__(self):
        return f"NonBinTree({self.val}): {self.nodes}"


class Test(object):
    def __init__(self):
        self.a = NonBinTree("root")
    def tester(self):
        print (self.a)


test  = Test()

test.tester()