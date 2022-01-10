from PySide2 import QtWidgets, QtGui, QtCore
import logging
import os
import hou
import pickle
import codecs

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(os.environ.get("LOGLEVEL", "INFO"))


class awesome(object):
    def onCreateInterface(self):
        widget = Window()
        return widget


class Window(QtWidgets.QMainWindow):
    RENDER_NODE = {"name": "render node",
                   "checkable": True,
                   "checkState": QtCore.Qt.Unchecked,
                   "editable": False,
                   "user_type": "render_node",
                   "setDragEnabled": True,
                   "setDropEnabled": False,
                   "user_icon": "C:/Users/cruss/OneDrive/Documents/houdini19.0/python_panels/icon1.png"}

    FRAME_RANGE = {"name": "frame_range",
                   "checkable": False,
                   "editable": True,
                   "user_type": "frame_range",
                   "setDragEnabled": True,
                   "setDropEnabled": False,
                   "user_icon": "C:/Users/cruss/OneDrive/Documents/houdini19.0/python_panels/icon2.png"}

    SHOT = {"name": "shot",
            "checkable": True,
            "checkState": QtCore.Qt.Unchecked,
            "editable": False,
            "user_type": "shot",
            "setDragEnabled": True,
            "setDropEnabled": False,
            "user_icon": "C:/Users/cruss/OneDrive/Documents/houdini19.0/python_panels/icon3.png"}

    GROUP = {"name": "group",
             "checkable": True,
             "checkState": QtCore.Qt.Unchecked,
             "editable": True,
             "user_type": "group",
             "setDragEnabled": True,
             "setDropEnabled": True,
             "user_icon": "C:/Users/cruss/OneDrive/Documents/houdini19.0/python_panels/icon4.png"}

    def __init__(self):
        super(Window, self).__init__()
        self.model = StandardItemModel()
        self.model.setColumnCount(2)
        self.model.setHorizontalHeaderLabels(['shot', 'frame range'])
        self.setGeometry(50, 50, 700, 900)
        self.view = QtWidgets.QTreeView()
        self.view.setModel(self.model)
        self.setCentralWidget(self.view)
        self.model.invisibleRootItem().setDropEnabled(False)
        self.view.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.view.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.delete_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence('ctrl+d'), self)
        self.delete_shortcut.activated.connect(lambda: (self.delete(self.view.selectedIndexes())))
        self.group_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence('ctrl+g'), self)
        self.group_shortcut.activated.connect(self.group_shots)
        self.iterate_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence('ctrl+i'), self)
        self.iterate_shortcut.activated.connect(lambda: (self.iterate(self.view.selectedIndexes(), "text")))
        self.refresh_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence('ctrl+r'), self)
        self.refresh_shortcut.activated.connect(self.refresh)
        self.copy_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence('ctrl+c'), self)
        self.copy_shortcut.activated.connect(lambda: (self.copy_shot(self.view.selectedIndexes())))
        self.paste_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence('ctrl+v'), self)
        self.paste_shortcut.activated.connect(lambda: (self.paste_shot(self.view.selectedIndexes())))
        self.save_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence('ctrl+shift+s'), self)
        self.save_shortcut.activated.connect(self.save)
        self.load_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence('ctrl+l'), self)
        self.load_shortcut.activated.connect(self.load)
        self.render_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence('ctrl+shift+r'), self)
        self.render_shortcut.activated.connect(self.render)
        self.render_selected_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence('ctrl+shift+alt+r'), self)
        self.render_selected_shortcut.activated.connect(lambda: (self.render_selected(self.view.selectedIndexes())))
        self.model.itemDataChanged.connect(self.on_item_changed)
        self.view.expanded.connect(self.view_expand_collapse_changed)
        self.view.collapsed.connect(self.view_expand_collapse_changed)
        self.view.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.view.customContextMenuRequested.connect(self.open_menu)
        self.model.setItemPrototype(QtGui.QStandardItem())
        if (hou.node("/").userData("whSubmitter")) is None:
            self.populate()
        else:
            self.load()

    def open_menu(self, position):
        index = self.view.selectedIndexes()[0]
        item = self.model.itemFromIndex(index)
        menu = QtWidgets.QMenu()
        self.delete_action = QtWidgets.QAction("delete [ctrl+d]", self)
        self.delete_action.triggered.connect(lambda: (self.delete(self.view.selectedIndexes())))
        menu.addAction((self.delete_action))
        if item.data(QtCore.Qt.UserRole + 1) == "shot":
            self.copy_shots_action = QtWidgets.QAction("copy shots [ctrl+c]", self)
            self.copy_shots_action.triggered.connect(lambda: (self.copy_shot(self.view.selectedIndexes())))
            menu.addAction((self.copy_shots_action))

            self.paste_shots_action = QtWidgets.QAction("paste shots [ctrl+v]", self)
            self.paste_shots_action.triggered.connect(lambda: (self.paste_shot(self.view.selectedIndexes())))
            menu.addAction((self.paste_shots_action))

            self.refresh_action = QtWidgets.QAction("refresh render nodes [ctrl+r]", self)
            self.refresh_action.triggered.connect(lambda: (self.refresh(self.view.selectedIndexes())))
            menu.addAction(self.refresh_action)

            self.render_action = QtWidgets.QAction("render all checked [ctrl+shift+r]", self)
            self.render_action.triggered.connect(self.render)
            menu.addAction(self.render_action)

            self.render_selected_action = QtWidgets.QAction("render all selected [ctrl+shift+alt+r]", self)
            self.render_selected_action.triggered.connect(lambda: (self.render_selected(self.view.selectedIndexes())))
            menu.addAction(self.render_selected_action)

            # self.resolve_render_nodes_action= QtWidgets.QAction("resolve render nodes", self)
            # self.resolve_render_nodes_action.triggered.connect(lambda: (self.resolve(True)))

            # self.resolve_render_frame_range_action= QtWidgets.QAction("complete resolve (SLOW)", self)
            # self.resolve_render_frame_range_action.triggered.connect(lambda: (self.resolve(False)))

            # menu.addAction(self.resolve_render_nodes_action)
            # menu.addAction(self.resolve_render_frame_range_action)
        elif item.data(QtCore.Qt.UserRole + 1) == "render_node":
            self.render_selected_action = QtWidgets.QAction("render all selected [ctrl+shift+alt+r]", self)
            self.render_selected_action.triggered.connect(lambda: (self.render_selected(self.view.selectedIndexes())))
            menu.addAction(self.render_selected_action)

        menu.exec_(self.view.viewport().mapToGlobal(position))


    def refresh(self):
        indexes = self.view.selectedIndexes()
        render_nodes = self.get_render_nodes()
        for index in indexes:
            item = self.model.itemFromIndex(index)
            if item.data(QtCore.Qt.UserRole + 1) != "shot":
                continue
            render_node_dict = list(self.recursive_walk(item))
            render_node_list = [render_node['render_node'] for render_node in render_node_dict]
            logger.info("Column 0 nodes: {0}".format(render_node_list))
            for render_node in render_nodes:
                if render_node not in render_node_list:
                    self.RENDER_NODE['name'] = render_node
                    self.FRAME_RANGE['name'] = 'test'
                    new_item = self.generic_item(**self.RENDER_NODE)
                    new_item2 = self.generic_item(**self.FRAME_RANGE)
                    item.appendRow([new_item, new_item2])

    def recursive_walk(self, item):
        for row in range(item.rowCount()):
            subnode = item.child(row, 0)
            frame_range = item.child(row, 1)
            yield {"render_node":subnode.text(), "frame_range":frame_range.text()}
            yield from self.recursive_walk(subnode)

    def delete(self, indexes):
        logger.info("Deleting Item")
        for index in reversed(indexes):
            if index.column() == 1:
                continue
            self.model.removeRow(index.row(), index.parent())

    def group_shots(self):
        '''
        Creates group node
        '''
        indexes = self.view.selectedIndexes()
        group01 = self.generic_item(**self.GROUP)
        group_frame_range = self.generic_item(**self.FRAME_RANGE)
        if len(indexes) > 0:
            for index in indexes:
                selected_item = self.model.itemFromIndex(index)
                if selected_item.data(QtCore.Qt.UserRole + 1) != "render_node":
                    selected_item.appendRow([group01, group_frame_range])
                    self.view.setExpanded(index, True)
                else:
                    logger.info("Cannot create group under render node")
        else:
            self.model.invisibleRootItem().appendRow([group01, group_frame_range])

    def populate(self):
        render_nodes = self.get_render_nodes()
        for i in range(10):
            self.SHOT['name'] = "shot %s0" % i
            test = self.generic_item(**self.SHOT)
            self.FRAME_RANGE['name'] = "all"
            test2 = self.generic_item(**self.FRAME_RANGE)
            self.model.appendRow([test, test2])
            for x in render_nodes:
                self.RENDER_NODE['name'] = str(x)
                self.RENDER_NODE['number'] = str(x)
                self.FRAME_RANGE['number'] = str(x)
                new_item = self.generic_item(**self.RENDER_NODE)
                new_item2 = self.generic_item(**self.FRAME_RANGE)
                test.appendRow([new_item, new_item2])

    def generic_item(self, **kwargs):
        item = QtGui.QStandardItem(kwargs["name"])
        item.setData(kwargs["user_type"], QtCore.Qt.UserRole + 1)
        item.setData(kwargs["user_icon"], QtCore.Qt.UserRole + 2)
        item.setCheckable(kwargs["checkable"])
        item.setEditable(kwargs["editable"])
        item.setDragEnabled(kwargs["setDragEnabled"])
        item.setDropEnabled(kwargs["setDropEnabled"])
        item.setIcon(QtGui.QIcon(kwargs["user_icon"]))
        item.user_icon = kwargs["user_icon"]
        if item.data(QtCore.Qt.UserRole + 1) != "frame_range":
            item.setCheckState(kwargs["checkState"])
        return item

    def on_item_changed(self, item, role):
        logger.info("Item Changed")
        if role == 10:
            checkState = item.checkState()
            self.iterate([item.index()], "check")
            self.iterate_down(item, checkState)
        elif role == 2:
            self.iterate([item.index()], "text")
        self.view.resizeColumnToContents(0)

    def view_expand_collapse_changed(self, item):
        self.view.resizeColumnToContents(0)

    def get_render_nodes(self):
        render_nodes = ['render node 01', 'render node 02', 'render node 03', 'render node 04', 'render node 05']
        return render_nodes

    def loop_iterate(self, root, text, changeType, checkState):
        logger.info("loop_iterate 01 changeType: {0}".format(changeType))
        logger.info("root: {0}, rowCount {1}".format(root, root.rowCount()))
        for shotIndex in range(root.rowCount()):
            logger.info("loop_iterate 02 shotIndex: {0}".format(shotIndex))
            shot = root.child(shotIndex, 0)
            frame_range = root.child(shotIndex, 1)
            if changeType == "text":
                logger.info("Change type: text")
                frame_range.setText(text)
            elif changeType == "check":
                shot.setCheckState(checkState)
            if shot.hasChildren():
                self.loop_iterate(shot, text, changeType, checkState)

    def iterate(self, indexes, changeType):
        logger.info("Iterate with changeType {0}".format(changeType))
        for num, index in enumerate(indexes):
            item = self.model.itemFromIndex(index)
            row = item.row()
            parent = self.get_parent(item)
            item = parent.child(row, 0)
            text = parent.child(row, 1).text()
            checkState = parent.child(row, 0).checkState()
            self.loop_iterate(item, text, changeType, checkState)

    @staticmethod
    def all_same(item):
        child_list = []
        if item.parent():
            parent = item.parent()
        else:
            parent = item
        for child in range(parent.rowCount()):
            child_state = parent.child(child).checkState()
            child_list.append(child_state)
        allSame = all(x == child_list[0] for x in child_list)
        return (allSame, child_list)

    def construct_dict_from_node(self, node):
        nodeDict = {"name": node.text(),
                    "checkState": node.checkState(),
                    "checkable": node.isCheckable(),
                    "editable": node.isEditable(),
                    "user_type": node.data(QtCore.Qt.UserRole + 1),
                    "setDragEnabled": node.isDragEnabled(),
                    "setDropEnabled": node.isDropEnabled(),
                    "user_icon": node.data(QtCore.Qt.UserRole + 2)}
        return nodeDict

    def iterItems(self, root):
        def recurse(root, dataTree):
            for row in range(root.rowCount()):
                node = root.child(row, 0)
                frame_range_node = root.child(row, 1)
                render_node_dict = self.construct_dict_from_node(node)
                frame_range_node_dict = self.construct_dict_from_node(frame_range_node)
                childNode = dataTree.add_node((render_node_dict, frame_range_node_dict))
                item = root.child(row, 0)
                if item.hasChildren():
                    recurse(item, childNode)
            return dataTree

        parent = self.get_parent(root)
        root_dict = self.construct_dict_from_node(root)
        frame_range_node = parent.child(0, 1)
        root_frame_range_dict = self.construct_dict_from_node(frame_range_node)
        dataTree = NonBinTree((root_dict, root_frame_range_dict))
        dataTree = recurse(root, dataTree)
        return dataTree

    def iterateDataTreeCreateStandardItems(self, a, item):
        for i in a.nodes:
            render_node = self.generic_item(**i.val[0])
            frame_range_node = self.generic_item(**i.val[1])
            item.appendRow([render_node, frame_range_node])
            if len(i.nodes) > 0:
                self.iterateDataTreeCreateStandardItems(i, render_node)

    def return_children_in_list(self, item):
        child_list = []
        for row in range(item.rowCount()):
            child_list.append((item.child(row, 0), item.child(row, 1)))
        return child_list

    def item_get_attrs(self, item):
        attr_dict = {"name": item.text(),
                     "checkable": item.isCheckable(),
                     "checkState": item.checkState(),
                     "editable": item.isEditable(),
                     "user_type": item.user_type,
                     "setDragEnabled": item.isDragEnabled(),
                     "setDropEnabled": item.isDropEnabled(),
                     "user_icon": item.user_icon}
        return attr_dict

    def copy_shot(self, indexes):
        logger.info("Shot Copied")
        index = indexes[0]
        item = (self.model.itemFromIndex(index))
        if item.data(QtCore.Qt.UserRole + 1) == "shot":
            self.copyDataTree = self.iterItems(item)
        else:
            logger.info("Copy function only available for shot nodes")

    def paste_shot(self, indexes):
        '''
        indexe list of indexes
        '''

        for index in indexes:
            if index.column() == 1:
                continue
            item = (self.model.itemFromIndex(index))
            if item.data(QtCore.Qt.UserRole + 1) != "shot":
                logger.info ("Only able to paste copied shots to shot nodes")
                continue

            for row in reversed(range(item.rowCount())):
                self.delete([item.child(row, 0).index()])

            self.iterateDataTreeCreateStandardItems(self.copyDataTree, item)
            parent = self.get_parent(item)

            self.set_attrs_item(item, self.copyDataTree.val[0])
            self.set_attrs_item(parent.child(item.row(), 1), self.copyDataTree.val[1])

    def set_attrs_item(self, item, attributes):
        item.setCheckable(attributes['checkable'])
        item.setEditable(attributes['editable'])
        item.setData(attributes['user_type'], QtCore.Qt.UserRole + 1)
        if attributes['user_type'] != "frame_range":
            item.setCheckState(attributes["checkState"])
        else:
            item.setText(attributes['name'])

    def iterate_down(self, item, checkState):
        """
        sets check box correctly if all
        """
        if item.parent() is None:
            logger.info("Iterate down: item.parent() is None")
        else:
            allSame, child_list = self.all_same(item)
            if allSame and child_list[0] == QtCore.Qt.Unchecked:
                item.parent().setCheckState(QtCore.Qt.Unchecked)
                self.iterate_down(item.parent(), checkState)
            else:
                item.parent().setCheckState(QtCore.Qt.Checked)
                self.iterate_down(item.parent(), checkState)

    def save(self):
        item = self.model.invisibleRootItem()
        treeData = self.iterItems(item)
        pickleData = codecs.encode(pickle.dumps(treeData), "base64").decode()
        hou.node("/").setUserData("whSubmitter", pickleData)
        logger.info("SAVED DATA TO ROOT")

    def load(self):
        arguments_pickle = hou.node("/").userData("whSubmitter")
        unpickled = pickle.loads(codecs.decode(arguments_pickle.encode(), "base64"))
        self.copyDataTree = unpickled
        item = self.model.invisibleRootItem()
        self.load_tree(self.copyDataTree, item)
        logger.info("LOADING DATA FROM ROOT")

    def load_tree(self, dataTree, item):
        for row in reversed(range(item.rowCount())):
            self.delete([item.child(row, 0).index()])
        self.iterateDataTreeCreateStandardItems(dataTree, item)

    def render(self):
        def render_recursive(root, shot_node):
            for row in range(root.rowCount()):
                node = root.child(row, 0)
                user_type = node.data(QtCore.Qt.UserRole + 1)
                if node.checkState() == QtCore.Qt.Unchecked:
                    continue
                if user_type == "render_node":
                    frame_range_node = root.child(row, 1)
                    logger.info("{0} {1} {2}".format(shot_node.text(), node.text(), frame_range_node.text()))
                if user_type == "shot":
                    shot_node = node
                if node.hasChildren():
                    render_recursive(node, shot_node)

        root = self.model.invisibleRootItem()
        render_recursive(root, None)

    def render_selected(self, indexes):
        for index in indexes:
            item = self.model.itemFromIndex(index)
            if item.data(QtCore.Qt.UserRole + 1) == "frame_range":
                continue
            elif item.data(QtCore.Qt.UserRole + 1) == "group":
                continue
            elif item.data(QtCore.Qt.UserRole + 1) == "shot":
                render_node_list = list(self.recursive_walk(item))
                for node in render_node_list:
                    print (item.text(), node['render_node'], node['frame_range'])
            elif item.data(QtCore.Qt.UserRole + 1) == "render_node":
                row = item.row()
                parent = self.get_parent(item)
                frame_range = parent.child(row, 1)
                shot = self.get_shot_from_render_node(item)
                print (list(shot)[0].text(), item.text(), frame_range.text())

    def get_parent(self, item):
        parent = item.parent()
        if parent == None:
            parent = self.model.invisibleRootItem()
        return parent

    def get_shot_from_render_node(self, item):
        parent = item.parent()
        if parent.data(QtCore.Qt.UserRole + 1) == "shot":
            yield parent
        else:
            self.get_shot_from_render_node(parent)


class StandardItemModel(QtGui.QStandardItemModel):
    itemDataChanged = QtCore.Signal(object, object)

    def dropMimeData(self, data, action, row, col, parent):
        """
        Always move the entire row, and don't allow column "shifting"
        """
        response = super().dropMimeData(data, QtCore.Qt.CopyAction, row, 0, parent)

        return response

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        oldvalue = index.data(role)
        result = super(StandardItemModel, self).setData(index, value, role)
        if result and value != oldvalue:
            self.itemDataChanged.emit(self.itemFromIndex(index), role)
        return result

class NonBinTree:
    def __init__(self, val):
        self.val = val
        self.nodes = []

    def add_node(self, val):
        self.nodes.append(NonBinTree(val))
        return self.nodes[-1]

    def __repr__(self):
        return f"NonBinTree({self.val}): {self.nodes}"
