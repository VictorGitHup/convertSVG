import unittest
from datetime import datetime
from xml.etree import ElementTree as ET
import os
from main import add_conversion_metadata
class TestAddConversionMetadata(unittest.TestCase):

    def setUp(self):
        # Crear carpeta de prueba
        if not os.path.exists('test_folder'):
            os.makedirs('test_folder')

        # Crear archivo SVG de prueba
        self.svg_file_path = os.path.join('test_folder', 'test_image.svg')
        svg_content = '''<svg xmlns="http://www.w3.org/2000/svg">
        </svg>'''
        with open(self.svg_file_path, 'w') as f:
            f.write(svg_content)

    def tearDown(self):
        # Limpiar después de la prueba
        if os.path.exists(self.svg_file_path):
            os.remove(self.svg_file_path)
        if os.path.exists('test_folder'):
            os.rmdir('test_folder')

    def test_add_conversion_metadata(self):
        # Ejecutar la función para añadir metadatos
        add_conversion_metadata(self.svg_file_path)
        
        # Leer el archivo SVG después de añadir metadatos
        tree = ET.parse(self.svg_file_path)
        root = tree.getroot()
        
        # Verificar que el elemento conversion_metadata existe
        metadata_element = root.find("conversion_metadata")
        self.assertIsNotNone(metadata_element, "El elemento conversion_metadata no fue añadido")
        
        # Verificar que el atributo conversion_datetime está presente
        conversion_datetime = metadata_element.get("conversion_datetime")
        self.assertIsNotNone(conversion_datetime, "El atributo conversion_datetime no fue añadido")
        
        # Verificar que la fecha y hora están en el formato esperado
        try:
            datetime.strptime(conversion_datetime, "%Y-%m-%d %H:%M:%S.%f")
        except ValueError:
            self.fail("El formato de conversion_datetime es incorrecto")

if __name__ == "__main__":
    unittest.main()
