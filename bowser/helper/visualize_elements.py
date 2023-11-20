from PIL import Image, ImageDraw, ImageFont
import random

def is_leaf(node):
    """Check if a node is a leaf."""
    return len(node.children) == 0


def get_color(depth, max_depth):
    """Calculate color based on tree depth."""
    if depth == max_depth:
        return (0, 0, 255)  # Blue for leaves
    else:
        redness = int(255 - (depth / max_depth) * 255)
        return (255, redness, redness)  # Shades of red for non-leaves

def leaf_depth(node):
    """Determine the leaf depth of a node."""
    if not node.children:
        return 1
    return 1 + max(leaf_depth(child) for child in node.children)

def draw_boxes(image, node, viewport_offset, depth=0, max_depth=0):
    """Recursively draw bounding boxes on the image."""
    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.truetype("arial.ttf", 15)
    except IOError:
        font = ImageFont.load_default()

    # Determine the color for the current node
    color = get_color(depth, max_depth) if not is_leaf(node) else (0, 0, 255)

    # Calculate leaf depth for bounding box adjustment
    node_leaf_depth = leaf_depth(node)
    adjustment = 5 * node_leaf_depth

    bounding_box = node.bounding_rect
    if bounding_box:
        left = bounding_box.get('left', 0) + viewport_offset[0] - adjustment
        top = bounding_box.get('top', 0) + viewport_offset[1] - adjustment
        right = bounding_box.get('right', 0) + viewport_offset[0] + adjustment
        bottom = bounding_box.get('bottom', 0) + viewport_offset[1] + adjustment
        draw.rectangle([left, top, right, bottom], outline=color, width=2)

        text_width = 50
        if (right - left) > text_width:
            text_x = random.randint(int(left), int(right - text_width))
        else:
            text_x = left

        text_position = (text_x, top)
        element_type = node.label_content
        draw.text(text_position, element_type, fill=color, font=font)

    # Recursively draw boxes for children
    for child in node.children:
        draw_boxes(image, child, viewport_offset, depth + 1, max_depth)

    return image



def get_max_depth(node, current_depth=0):
    """Determine the maximum depth of a node."""
    if not node.children:
        return current_depth
    return max(get_max_depth(child, current_depth + 1) for child in node.children)

def visualize_dom_tree(image, dom_tree, viewport_offset=(0,0)):
    max_depth = get_max_depth(dom_tree)

    image_with_boxes = draw_boxes(image, dom_tree, viewport_offset, max_depth=max_depth)

    return image_with_boxes

# Example usage:
# image_with_boxes = visualize_dom_tree('screenshot.png', dom_tree_root, (x, y))
# image_with_boxes.show()  # Or image_with_boxes.save('annotated_screenshot.png') to save the image

