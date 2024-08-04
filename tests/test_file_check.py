
import unittest
from main import is_allowed_file 

class TestIsAllowedFile(unittest.TestCase):
    def test_allowed_extensions(self):
        # Archivos con extensiones permitidas
        self.assertTrue(is_allowed_file('/tests/test.jpg'))
        self.assertTrue(is_allowed_file('test.png'))
       

    def test_disallowed_extensions(self):
        # Archivos con extensiones no permitidas
        self.assertFalse(is_allowed_file('test.bmp'))
        self.assertFalse(is_allowed_file('test.gif'))
        self.assertFalse(is_allowed_file('test.txt'))
        self.assertFalse(is_allowed_file('test.pdf'))
        
    def test_no_extension(self):
        # Archivo sin extensión
        self.assertFalse(is_allowed_file('testfile'))

if __name__ == '__main__':
    unittest.main()
