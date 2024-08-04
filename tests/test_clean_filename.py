import unittest
from main import clean_filename  # Asegúrate de que el nombre del módulo principal sea correcto

class TestCleanFilename(unittest.TestCase):
    def test_clean_filename(self):
        # Casos de prueba con caracteres especiales
        self.assertEqual(clean_filename("test@file!.jpg"), "testfile.jpg")
        self.assertEqual(clean_filename("my_document(1).pdf"), "my_document1.pdf")
        self.assertEqual(clean_filename("clean-me-up!!.png"), "clean-me-up.png")
        
        # Casos de prueba sin caracteres especiales
        self.assertEqual(clean_filename("simplefile.jpg"), "simplefile.jpg")
        self.assertEqual(clean_filename("another-file.png"), "another-file.png")
        
        # Casos de prueba con solo caracteres permitidos
        self.assertEqual(clean_filename("file_with_underscores_and-dashes.png"), "file_with_underscores_and-dashes.png")
        
        # Casos de prueba con espacios
        self.assertEqual(clean_filename("file with spaces.txt"), "filewithspaces.txt")
        
        # Casos de prueba con nombre de archivo vacío
        self.assertEqual(clean_filename(""), "")
        
        # Casos de prueba con caracteres no alfanuméricos múltiples
        self.assertEqual(clean_filename("!!@@##$$%%^^&&**()"), "")
        
        # Casos de prueba con solo extensiones
        self.assertEqual(clean_filename(".hiddenfile"), ".hiddenfile")
        self.assertEqual(clean_filename("normal.file.name.ext"), "normal.file.name.ext")

if __name__ == '__main__':
    unittest.main()
