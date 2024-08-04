import unittest
import tempfile
import os
from main import convert_image_to_svg
from PIL import Image

class TestConvertImageToSvg(unittest.TestCase):
    def setUp(self):
      
        self.test_dir = tempfile.TemporaryDirectory()
        self.input_path = os.path.join(self.test_dir.name, 'test_image.png')
        self.output_path = os.path.join(self.test_dir.name, 'output_image.svg')

      
        image = Image.new('RGB', (100, 100), color = 'white')
        image.save(self.input_path)

    def tearDown(self):
        
        self.test_dir.cleanup()

    def test_convert_image_to_svg(self):
        # Llamar a la función para convertir la imagen a SVG
        convert_image_to_svg(self.input_path, self.output_path, colormode='color', mode='spline', hierarchical='stacked', filter_speckle=4, color_precision=6, layer_difference=16, corner_threshold=60, length_threshold=4.0, max_iterations=10, splice_threshold=45, path_precision=3)

        # Verificar que el archivo SVG de salida se haya creado
        self.assertTrue(os.path.exists(self.output_path))

        # Verificar que el archivo SVG no esté vacío
        with open(self.output_path, 'r') as svg_file:
            content = svg_file.read()
            self.assertGreater(len(content), 0)

if __name__ == '__main__':
    unittest.main()
