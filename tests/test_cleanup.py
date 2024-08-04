import unittest
from unittest import mock
import os
import datetime
from main import cleanup_files, UPLOAD_FOLDER, SVG_FOLDER  # Reemplaza 'your_module' con el nombre del módulo

class TestCleanupFiles(unittest.TestCase):

    def setUp(self):
        # Crear carpetas de prueba
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER)
        if not os.path.exists(SVG_FOLDER):
            os.makedirs(SVG_FOLDER)

        # Crear archivos de prueba
        self.old_file_path = os.path.join(UPLOAD_FOLDER, "old_image.jpeg")
        self.new_file_path = os.path.join(UPLOAD_FOLDER, "new_image.jpeg")
        self.svg_file_path = os.path.join(SVG_FOLDER, "old_image.svg")

        # Usar 'mock' para reemplazar métodos de os.path.getctime
        self.mock_getctime = mock.patch("os.path.getctime").start()

        # Configurar el mock para que devuelva un tiempo antiguo para el archivo viejo
        self.mock_getctime.side_effect = lambda path: datetime.datetime.now().timestamp() - 2 * 3600 if path == self.old_file_path else datetime.datetime.now().timestamp()

        # Crear el archivo viejo y el archivo nuevo
        with open(self.old_file_path, "w") as f:
            f.write("test")
        with open(self.new_file_path, "w") as f:
            f.write("test")

        # Crear un archivo SVG con metadatos que simulen un tiempo de conversión antiguo
        old_time = datetime.datetime.now() - datetime.timedelta(hours=2)
        svg_content = '''<svg xmlns="http://www.w3.org/2000/svg">
        <conversion_metadata conversion_datetime="{}"/>
        </svg>'''.format(old_time.strftime("%Y-%m-%d %H:%M:%S.%f"))

        with open(self.svg_file_path, "w") as f:
            f.write(svg_content)

    def tearDown(self):
        # Limpiar después de la prueba
        if os.path.exists(self.old_file_path):
            os.remove(self.old_file_path)
        if os.path.exists(self.new_file_path):
            os.remove(self.new_file_path)
        if os.path.exists(self.svg_file_path):
            os.remove(self.svg_file_path)
        if os.path.exists(UPLOAD_FOLDER):
            os.rmdir(UPLOAD_FOLDER)
        if os.path.exists(SVG_FOLDER):
            os.rmdir(SVG_FOLDER)
        mock.patch.stopall()

    @mock.patch("os.remove")
    def test_cleanup_files(self, mock_remove):
        cleanup_files()

        # Verificar que el archivo antiguo fue eliminado
        self.assertFalse(os.path.exists(self.old_file_path))

        # Verificar que el archivo nuevo no fue eliminado
        self.assertTrue(os.path.exists(self.new_file_path))

        # Verificar que el archivo SVG con metadatos antiguos fue eliminado
        self.assertFalse(os.path.exists(self.svg_file_path))

        # Verificar que os.remove fue llamado para el archivo SVG antiguo
        mock_remove.assert_called_once_with(self.svg_file_path)

if __name__ == "__main__":
    unittest.main()
