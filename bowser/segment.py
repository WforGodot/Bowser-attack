from dom_parser import DOMParser
from instance_segmentation import InstanceSegmentator
from ocr_processor import OCRProcessor
from image_analyzer import ImageAnalyzer
from graph_builder import GraphBuilder

class Segmenter:
    def __init__(self):
        # Load necessary models for each component.
        self.dom_parser = DOMParser()
        self.segmentator = InstanceSegmentator()
        self.ocr_processor = OCRProcessor()
        self.image_analyzer = ImageAnalyzer()
        self.graph_builder = GraphBuilder()

    def run_segmentation(self, screenshot_path, dom_data):
        # Parse DOM to identify text elements.
        text_elements = self.dom_parser.parse(dom_data)

        # Perform instance segmentation on the screenshot.
        words_not_in_dom, shapes, images = self.segmentator.segment(screenshot_path, dom_data)

        # Run OCR on words not found in the DOM.
        ocr_results = self.ocr_processor.run_ocr(words_not_in_dom)

        # Transform shapes into a set of features.
        shape_features = self.segmentator.extract_features(shapes)

        # Analyze images using CLIP or similar models.
        image_descriptions = self.image_analyzer.analyze(images)

        # Construct the graph of all objects.
        object_graph = self.graph_builder.build_graph(text_elements, ocr_results, shape_features, image_descriptions)

        return object_graph