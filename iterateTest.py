def recursive_walk(self, item):
    for row in range(item.rowCount()):
        subnode = item.child(row, 0)
        yield subnode.text()
        yield from self.recursive_walk(subnode)