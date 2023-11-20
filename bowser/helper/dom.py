

# Collect DOM information from browser
def collect_element_info(driver):
    bounding_boxes_script = """
function getDirectTextContent(element) {
    let textContent = '';
    for (let node of element.childNodes) {
      if (node.nodeType === Node.TEXT_NODE) {
        textContent += node.nodeValue;
      }
    }
    return textContent.trim(); // Trim the text to remove any extra whitespace
  }

function isElementHidden(element) {
    // Check the hidden attribute
    if (element.hidden) {
      return true;
    }
  
    // Check computed styles
    const style = window.getComputedStyle(element);
    return style.display === 'none' || style.visibility === 'hidden' || style.opacity === '0';
  }

function element_type(element) {
    var isLeafNode = element.children.length === 0;
    var containsText = getDirectTextContent(element).trim().length > 0 
    const bgImageUrl = element.getAttribute('data-bg');
    const style = element.style.backgroundImage || element.getAttribute('style');

    var labelContent;
    if (element.tagName.toLowerCase() === 'img') {
      labelContent = 'image';
    } else if (element.tagName.toLowerCase() === 'canvas') {
      labelContent = 'canvas';
    } else if (element.tagName.toLowerCase() === 'svg') {
      labelContent = 'image';
    } else if (containsText) {
      // Check if the element itself contains text
      labelContent = 'text';
    } else if (element.tagName.toLowerCase() === 'input') {
      // Non-leaf nodes without text content are not labeled
      labelContent = 'input';
    } else if (isLeafNode) {
        // For leaf nodes with no text content, assume it's an image/graphic
        labelContent = 'image';
    } else if (bgImageUrl && /\.(jpg|jpeg|png|gif|bmp|svg)$/i.test(bgImageUrl)) {
        // If the element has a background image, assume it's an image/graphic
        labelContent = 'image';
    } else if (style && style.includes('background-image') && /\.(jpg|jpeg|png|gif|bmp|svg)$/i.test(style)) {
        // If the element has a background image, assume it's an image/graphic
        labelContent = 'image';
    } else if (element.tagName.toLowerCase() === 'button') {
        // Non-leaf nodes without text content are not labeled
        labelContent = 'button';
    } else if (element.tagName.toLowerCase() === 'a') {
        // Non-leaf nodes without text content are not labeled
        labelContent = 'link';
    } else {
      // Non-leaf nodes without text content are not labeled
      labelContent = 'div';
    }

    return labelContent;
}

function collectDOMInfo() {
    var elementsInfo = [];
    var elements = document.getElementsByTagName('*');
    var parentStack = [{element: document.body, info: null}]; // Start with the body element

    Array.prototype.forEach.call(elements, function(element) {
        if (!isElementHidden(element)) {
            var boundingBox = element.getBoundingClientRect();
            
            // Only collect data if the element is visible
            if(boundingBox.width > 0 && boundingBox.height > 0) {
                var elementInfo = {
                    tagName: element.tagName,
                    labelContent: element_type(element),
                    boundingRect: {
                        width: boundingBox.width,
                        height: boundingBox.height,
                        top: boundingBox.top,
                        left: boundingBox.left,
                        right: boundingBox.right,
                        bottom: boundingBox.bottom
                    },
                    text: getDirectTextContent(element),
                    children: [],
                    attributes: {},
                    elementId: element.id // Get the element's id
                };

                Array.prototype.forEach.call(element.attributes, function(attr) {
                    elementInfo.attributes[attr.name] = attr.value;
                });

                // If it's an image or has a background image, get the source
                if (element.tagName.toLowerCase() === 'img' && element.src) {
                    elementInfo.src = element.src;
                }
                if (element.style.backgroundImage) {
                    elementInfo.backgroundImage = element.style.backgroundImage;
                }

                // Check for the closest parent element which is not hidden and has a valid bounding box
                while (parentStack.length > 0) {
                    var parentEntry = parentStack[parentStack.length - 1];
                    if (parentEntry.element.contains(element) &&
                        !isElementHidden(parentEntry.element) &&
                        parentEntry.element.getBoundingClientRect().width > 0 &&
                        parentEntry.element.getBoundingClientRect().height > 0) {
                        // Found the parent, add the current element to its children array
                        parentEntry.info.children.push(elementInfo);
                        break;
                    } else {
                        // Current element is not a child of the element on top of the stack
                        parentStack.pop(); // Remove the last element
                    }
                }

                // Push the current element onto the stack
                parentStack.push({element: element, info: elementInfo});
                elementsInfo.push(elementInfo); // Also keep a flat list, if needed
            }
        }
    });

    // Return the root element's info, which contains all other elements as children
    return parentStack.length > 0 ? parentStack[0].info : null;
}


// Call the collectDOMInfo function and return its value
return collectDOMInfo();
"""

    # Execute the script and get the result
    elementInfo = driver.execute_script(bounding_boxes_script)

    return elementInfo