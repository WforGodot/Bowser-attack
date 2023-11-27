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
        self.parent = None


def build_tree(node_info):
    # Create the root node of the tree
    try:
        node = DOMNode(node_info)
    # Recursively build the tree for each child
        for child_info in node_info.get('children', []):
            child_node = build_tree(child_info)
            child_node.parent = node
            node.children.append(child_node)
    
        return node
    except Exception as e:
        print(node_info)
        return None


def print_dom_tree(node, depth=0):
    """
    Print all the elements in a DOM tree in a readable format.
    
    :param node: The root node of the DOM tree.
    :param depth: The current depth in the tree (used for indentation).
    """
    if node is None:
        return

    indent = '    ' * depth  # Indentation for hierarchy visualization
    node_info = f"{indent}Tag: {node.tag_name}, Label: {node.label_content}, ID: {node.element_id}"

    print(node_info)

    for child in node.children:
        print_dom_tree(child, depth + 1)


def is_within_area(bounding_rect, area, tolerance=0):
    """
    Check if the bounding rectangle of a node is within the specified area.
    """
    if not bounding_rect:
        return False

    left, top, right, bottom = (bounding_rect.get(key, 0) for key in ['left', 'top', 'right', 'bottom'])
    area_left, area_top, area_right, area_bottom = area

    return (left + tolerance >= area_left and right - tolerance <= area_right and
            top + tolerance >= area_top and bottom - tolerance <= area_bottom)

def delete_node(node):
    """
    Delete a node from the DOM tree.
    """
    if node.parent:
        node.parent.children.remove(node)
        # Add children to the parent
        for child in node.children:
            child.parent = node.parent
            node.parent.children.append(child)
    else:
        pass

def traverse_dom_tree(node, func):
    """
    Traverse the DOM tree and apply a function to each node.
    """
    func(node)
    for child in node.children:
        traverse_dom_tree(child, func)

def crop_dom_tree_by_area(root, window_area, tolerance=10):
    """
    Crop the DOM tree to only include nodes within the window_area with a given tolerance.
    """
    def crop_node(node):
        if not is_within_area(node.bounding_rect, window_area, tolerance):
            delete_node(node)
    
    traverse_dom_tree(root, crop_node)

    return root

def crop_empty_divs(root):
    """
    Crop the DOM tree to only include nodes that only have one child.
    """
    def crop_node(node):
        if node.tag_name == 'div' and len(node.children) <= 1:
            delete_node(node)
    
    traverse_dom_tree(root, crop_node)

    return root




