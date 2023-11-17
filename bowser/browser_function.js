function clearBoundingBoxes() {
    var highlights = document.getElementsByClassName('highlight-box');
    while (highlights[0]) {
      highlights[0].parentNode.removeChild(highlights[0]);
    }
  }

  function getDirectTextContent(element) {
    let textContent = '';
    for (let node of element.childNodes) {
      if (node.nodeType === Node.TEXT_NODE) {
        textContent += node.nodeValue;
      }
    }
    return textContent.trim(); // Trim the text to remove any extra whitespace
  }
  
  
  function drawBoundingBoxes() {
    clearBoundingBoxes(); // Clear any existing boxes before drawing new ones
  
    var elements = document.getElementsByTagName('*'); // '*' selects all elements
  
    Array.prototype.forEach.call(elements, function(element) {
      // Check if the element is a leaf node or contains text
      var isLeafNode = element.children.length === 0;
      var containsText = getDirectTextContent(element).trim().length > 0 
  
      if (!isElementHidden(element)) {
        var boundingBox = element.getBoundingClientRect();
        
        // Only draw bounding boxes if the element is visible
        if(boundingBox.width > 0 && boundingBox.height > 0) {
          // Create a visual representation of the bounding box
          var highlight = document.createElement('div');
          highlight.className = 'highlight-box'; // Set a class name for easy removal
          document.body.appendChild(highlight);
          highlight.style.position = 'absolute';
          highlight.style.border = '2px solid red';
          highlight.style.width = boundingBox.width + 'px';
          highlight.style.height = boundingBox.height + 'px';
          highlight.style.left = (boundingBox.left + window.scrollX) + 'px'; // Adjust for horizontal scroll
          highlight.style.top = (boundingBox.top + window.scrollY) + 'px'; // Adjust for vertical scroll
          highlight.style.pointerEvents = 'none'; // Makes the overlay click-through
          highlight.style.zIndex = '10000'; // Ensure the label is above other elements
  
          // Determine the type of content and label it
          var labelContent = element_type(element);
  
          // Create a label for the element's type
          var label = document.createElement('div');
          label.textContent = labelContent;
          highlight.appendChild(label);
          label.style.position = 'absolute';
          label.style.bottom = '100%'; // Position above the highlight box
          label.style.left = '0';
          label.style.backgroundColor = 'rgba(255, 255, 255, 0.8)'; // Slightly transparent white background
          label.style.color = 'red'; // Set text color to red
          label.style.fontSize = '10px'; // Set font size for visibility
          label.style.fontFamily = 'Arial, sans-serif'; // Ensure a consistent font is used
        }
      }
    });
  }
  

function element_type(element) {
    var isLeafNode = element.children.length === 0;
    var containsText = getDirectTextContent(element).trim().length > 0 
    const bgImageUrl = element.getAttribute('data-bg');
    const style = element.style.backgroundImage || element.getAttribute('style');

    var labelContent;
    if (element.tagName.toLowerCase() === 'img') {
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

function isElementHidden(element) {
    // Check the hidden attribute
    if (element.hidden) {
      return true;
    }
  
    // Check computed styles
    const style = window.getComputedStyle(element);
    return style.display === 'none' || style.visibility === 'hidden' || style.opacity === '0';
  }