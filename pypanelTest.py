from PySide2 import QtWidgets, QtGui, QtCore
import logging
import os
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.setLevel(os.environ.get("LOGLEVEL", "INFO"))

class awesome(object):
    def onCreateInterface(self):
        widget = Window()
        return widget

class Window(QtWidgets.QMainWindow):

    RENDER_NODE = {"name": "render node",
                   "checkable": True,
                   "editable": False,
                   "user_type": "render_node",
                   "setDragEnabled":True,
                    "setDropEnabled":False,
                   "icon": "C:/Users/cruss/OneDrive/Documents/houdini19.0/python_panels/icon1.png"}

    FRAME_RANGE = {"name": "frame_range",
                   "checkable": False,
                   "editable": True,
                   "user_type": "frame_range",
                    "setDragEnabled": True,
                    "setDropEnabled": False,
                   "icon": "C:/Users/cruss/OneDrive/Documents/houdini19.0/python_panels/icon2.png"}

    SHOT = {"name": "shot",
                   "checkable": True,
                   "editable": False,
                   "user_type": "shot",
                    "setDragEnabled": True,
                    "setDropEnabled": False,
            "icon": "C:/Users/cruss/OneDrive/Documents/houdini19.0/python_panels/icon3.png"}

    GROUP = {"name": "group",
                   "checkable": True,
                   "editable": True,
                   "user_type": "group",
                    "setDragEnabled": True,
                    "setDropEnabled": True,
                    "icon": "C:/Users/cruss/OneDrive/Documents/houdini19.0/python_panels/icon4.png"}

    def __init__(self, parent = None):
        super(Window, self).__init__()
        menubar = self.menuBar()
        view_menu = menubar.addMenu("View")
        self.model = StandardItemModel()
        self.model.setColumnCount(2)
        self.model.setHorizontalHeaderLabels(['shot', 'frame range'])
        self.setGeometry(50, 50, 700, 900)
        self.view = QtWidgets.QTreeView()
        self.view.setModel(self.model)
        self.setCentralWidget(self.view)
        self.populate()

        self.delete_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence('ctrl+d'), self)
        self.delete_shortcut.activated.connect(self.delete)
        self.group_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence('ctrl+g'), self)
        self.group_shortcut.activated.connect(self.group_shots)
        self.iterate_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence('ctrl+i'), self)
        self.iterate_shortcut.activated.connect(lambda: (self.iterate(self.view.selectedIndexes(),"text")))
        self.refresh_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence('ctrl+r'), self)
        self.refresh_shortcut.activated.connect(self.refresh)

        self.check_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence('ctrl+c'), self)
        self.check_shortcut.activated.connect(self.iterate_up)

        self.model.itemDataChanged.connect(self.on_item_changed)
        self.view.expanded.connect(self.view_expand_collapse_changed)
        self.view.collapsed.connect(self.view_expand_collapse_changed)

        self.model.setItemPrototype(StandardItem())

    #def check(self):
    #    index = self.view.selectedIndexes()[0]
    #    item = self.model.itemFromIndex(index)
    #    item.setCheckState(QtCore.Qt.Checked)



    def refresh(self):
        indexes = self.view.selectedIndexes()
        render_nodes = self.get_render_nodes()

        for index in indexes:
            item = self.model.itemFromIndex(index)
            if item.user_type != "shot":
                continue
            render_node_list = self.get_active_render_nodes(item)

            for render_node in render_nodes:
                if render_node not in render_node_list:
                    self.RENDER_NODE['name'] = render_node
                    self.FRAME_RANGE['name'] = 'test'
                    new_item =  self.generic_item(**self.RENDER_NODE)
                    new_item2 =  self.generic_item(**self.FRAME_RANGE)
                    item.appendRow([new_item, new_item2])

    def loop_get_active_render_nodes(self, item, render_node_list):
        for row in range(item.rowCount()):
            child = item.child(row,0)
            if child.hasChildren() == True:
                self.loop_get_active_render_nodes(child, render_node_list)
            else:
                render_node_list.append(item.child(row, 0).text())
            #render_node_list.append(item.child(row, 0).text())

    def get_active_render_nodes(self, item):
        render_node_list = []
        self.loop_get_active_render_nodes(item, render_node_list)
        return render_node_list

    def delete(self):
        indexes = self.view.selectedIndexes()
        row_list = []
        index_list = []
        for index in indexes:
            if index.row() not in row_list:
                row_list.append(index.row())
                index_list.append(index.parent())

        for index, value in reversed(list(enumerate(row_list))):
            self.model.removeRow(row_list[index], index_list[index])

    def group_shots(self):
        '''
        Need to refactor this function
        '''

        indexes = self.view.selectedIndexes()

        if len(indexes) > 0:
            for index in indexes:
                self.GROUP['number'] = 0
                self.FRAME_RANGE['number'] = 0
                group01 = self.generic_item(**self.GROUP)
                group_frame_range = self.generic_item(**self.FRAME_RANGE)
                selected_item = self.model.itemFromIndex(index)
                if selected_item.user_type != "render_node":
                    selected_item.appendRow([group01, group_frame_range])
                    self.view.setExpanded(index, True)
                else:
                    logger.info("Cannot create group under render node")
        else:
            self.GROUP['number'] = 0
            self.FRAME_RANGE['number'] = 0
            group01 = self.generic_item(**self.GROUP)
            group_frame_range = self.generic_item(**self.FRAME_RANGE)
            self.model.invisibleRootItem().appendRow([group01, group_frame_range])

    def populate(self):
        render_nodes = self.get_render_nodes()
        for i in range(10):
            self.SHOT['number'] = str(i)
            test = self.generic_item(**self.SHOT)
            self.FRAME_RANGE['number'] = str(i)
            test2 = self.generic_item(**self.FRAME_RANGE)
            self.model.appendRow([test, test2])
            for x in render_nodes:
                self.RENDER_NODE['name'] = str(x)
                self.RENDER_NODE['number'] =str(x)
                self.FRAME_RANGE['number']=str(x)
                new_item =  self.generic_item(**self.RENDER_NODE)
                new_item2 =  self.generic_item(**self.FRAME_RANGE)
                test.appendRow([new_item, new_item2])

        self.view.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.view.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

    def generic_item(self, *args, **kwargs):
        #item = QtGui.QStandardItem(kwargs["name"])
        item = StandardItem(kwargs["name"])
        item.setCheckable(kwargs["checkable"])
        item.setEditable(kwargs["editable"])
        item.setDragEnabled(kwargs["setDragEnabled"])
        item.setDropEnabled(kwargs["setDropEnabled"])
        item.user_type = kwargs["user_type"]
        item.setIcon(QtGui.QIcon(kwargs["icon"]))
        return item

    def on_item_changed(self, item, role):
        #print (item, role)
        #if Qt.DisplayRole in roles:
        #    print(topLeft.data())
        logger.debug("Item Changed")
        if role == 10:
            checkState = item.checkState()
            self.iterate([item.index()], "check")
            self.iterate_up(item.index())
            self.iterate_down(item, checkState)
        elif role == 2:
            self.iterate([item.index()], "text")
        self.view.resizeColumnToContents(0)

    def view_expand_collapse_changed(self, item):
        self.view.resizeColumnToContents(0)

    def get_render_nodes(self):
        render_nodes = ['render node 01','render node 02','render node 03','render node 04','render node 05']
        return render_nodes

    def loop_iterate(self, root, text, changeType, checkState):
        logger.debug("loop_iterate 01 changeType: {0}".format(changeType))
        logger.debug ("root: {0}, rowCount {1}".format(root, root.rowCount()))
        for shotIndex in range(root.rowCount()):
            logger.debug("loop_iterate 02 shotIndex: {0}".format(shotIndex))
            shot = root.child(shotIndex, 0)
            frame_range = root.child(shotIndex, 1)
            if changeType == "text":
                logger.debug("Change type: text")
                frame_range.setText(text)
            elif changeType == "check":
                shot.setCheckState(checkState)
            if shot.hasChildren() == True:
                self.loop_iterate(shot, text, changeType, checkState)

    def iterate(self, indexes, changeType):
        logger.debug("Iterate with changeType {0}".format(changeType))
        for num, index in enumerate(indexes):
            item = self.model.itemFromIndex(index)
            row = item.row()
            parent = item.parent()

            if parent == None:
                parent = self.model.invisibleRootItem()
            item = parent.child(row, 0)
            text = parent.child(row, 1).text()
            checkState = parent.child(row, 0).checkState()
            self.loop_iterate(item, text, changeType, checkState)

    def loop_iterate_up(self, item, items_list):
        if item == None:
            print (items_list)
            for item in items_list:
                try:
                    item.setCheckState(QtCore.Qt.Checked)
                except:
                    pass
        else:
            items_list.append(item)
            self.loop_iterate_up(item.parent(), items_list)

    def iterate_up(self, index):
        items_list = []
        item = self.model.itemFromIndex(index)
        parent = item.parent()
        self.loop_iterate_up(parent, items_list)

    def iterate_down(self, item, checkState):
        if item.parent() is None:
            print ("END")
        else:
            allSame, child_list = self.all_same(item)
            if allSame and child_list[0] == QtCore.Qt.Unchecked:
                item.parent().setCheckState(QtCore.Qt.Unchecked)
                self.iterate_down(item.parent(), checkState)
            else:
                item.parent().setCheckState(QtCore.Qt.Checked)
                self.iterate_down(item.parent(), checkState)

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

class StandardItemModel(QtGui.QStandardItemModel):
    itemDataChanged = QtCore.Signal(object, object)
    def dropMimeData(self, data, action, row, col, parent):
        """
        Always move the entire row, and don't allow column "shifting"
        """
        response = super().dropMimeData(data,  QtCore.Qt.CopyAction, row, 0, parent)

        return response

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        oldvalue = index.data(role)
        result = super(StandardItemModel, self).setData(index, value, role)
        if result and value != oldvalue:
            self.itemDataChanged.emit(self.itemFromIndex(index), role)
        return result

class StandardItem(QtGui.QStandardItem):
    '''This is the item I'd like to drop into the view'''
    _user_typeRole = QtCore.Qt.UserRole + 2
    def __init__(self, parent=None):
        super(StandardItem, self).__init__(parent)
        self.user_type = 'shot'

    def clone(self):
        return StandardItem()

    @property
    def user_type(self):
        return self.data(self._user_typeRole)

    @user_type.setter
    def user_type(self, value):
        self.setData(value, self._user_typeRole)