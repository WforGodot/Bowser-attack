class DOMNode:
    def __init__(self, info):
        self.tag_name = info.get('tagName', 'undefined')
        self.label_content = info.get('labelContent', 'undefined')
        self.bounding_rect = info.get('boundingRect', {})
        self.text = info.get('text', '')
        self.src = info.get('src', '')
        self.background_image = info.get('backgroundImage', '')
        self.children = []
        self.attributes = info.get('attributes', {})  # Store all other attributes
        self.element_id = info.get('elementId', '')


def build_tree(node_info):
    # Create the root node of the tree
    node = DOMNode(node_info)
    
    # Recursively build the tree for each child
    for child_info in node_info.get('children', []):
        child_node = build_tree(child_info)
        node.children.append(child_node)
    
    return node



