from PyQt5.QtWidgets import QApplication, QTreeView
from PyQt5.QtGui import QStandardItemModel, QStandardItem
import sys


class TreeDisplayApp:
    def __init__(self, root_node):
        self.app = QApplication(sys.argv)
        self.tree_view = QTreeView()
        self.model = QStandardItemModel()
        
        # Set headers for the tree view including bounding box dimensions
        self.model.setHorizontalHeaderLabels([
            'Tag',
            'Label Content',
            'Attributes',
            'Bounding Box'
            'Image'
            'Src'
            'Background Image'
        ])

        # Build tree
        self.build_tree(None, root_node)
        
        self.tree_view.setModel(self.model)
        self.tree_view.expandAll()
        self.tree_view.setWindowTitle('DOM Tree Display')
        self.tree_view.show()
        sys.exit(self.app.exec_())

    def build_tree(self, parent, node):
        if parent is None:
            # Starting with the root node
            parent = self.model.invisibleRootItem()
            
        # Format bounding box dimensions
        bounding_box = node.bounding_rect
        bounding_box_str = f"Width: {bounding_box.get('width', 'N/A')}px, " \
                           f"Height: {bounding_box.get('height', 'N/A')}px, " \
                           f"Top: {bounding_box.get('top', 'N/A')}px, " \
                           f"Left: {bounding_box.get('left', 'N/A')}px"
        
        # Create items for the tree view
        item = QStandardItem(node.tag_name)
        label_content_item = QStandardItem(node.label_content)
        attributes_item = QStandardItem(", ".join(f"{k}: {v}" for k, v in node.attributes.items()))
        bounding_box_item = QStandardItem(bounding_box_str)
        text_item = QStandardItem(node.text)
        src_item = QStandardItem(node.src)
        background_image_item = QStandardItem(node.background_image)

        
        # Append the new row to the parent item
        parent.appendRow([item, label_content_item, attributes_item, bounding_box_item, text_item, src_item, background_image_item])
        
        # Recursively build the tree for each child node
        for child_node in node.children:
            self.build_tree(item, child_node)

# Assuming you have a DOMNode structure you've built named `dom_tree_root`
# TreeDisplayApp(dom_tree_root)
