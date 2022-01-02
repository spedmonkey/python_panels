class NonBinTree:

    def __init__(self, val):
        self.val = val
        self.nodes = []

    def add_node(self, val):
        self.nodes.append(NonBinTree(val))
        return self.nodes[-1]

    def __repr__(self):
        return f"NonBinTree({self.val}): {self.nodes}"
def traverse(tree_of_lists):
    for item in tree_of_lists:
        if isinstance(item, list):
            for x in traverse(item):
                yield x
        else:
            yield item

a = NonBinTree("root")
grandparents = ["grandfather", "grandmother"]
parents = ["father", "mother"]
children = ["child01", "child02", "child03"]
for i in grandparents:
    awesome = a.add_node(i)
    for x in parents:
        child  =awesome.add_node(x)
        for z in children:
            child.add_node(z)



def iterate(a):
    for i in a.nodes:
        print (i.val)
        if len ( i.nodes ) > 0:
            iterate(i)

iterate(a)