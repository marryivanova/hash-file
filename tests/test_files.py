import os
import unittest
from tempfile import TemporaryDirectory

from src.app.file_dir import StorageDir, Extensions, get_file_path, allowed_file


class TestStorageDir(unittest.TestCase):
    def test_storage_dir_path(self):
        self.assertEqual(StorageDir.STORE.path, "store")


class TestExtensions(unittest.TestCase):
    def test_extensions_paths(self):
        self.assertEqual(Extensions.TXT.path, "txt")
        self.assertEqual(Extensions.PDF.path, "pdf")
        self.assertEqual(Extensions.PNG.path, "png")
        self.assertEqual(Extensions.JPG.path, "jpg")
        self.assertEqual(Extensions.JPEG.path, "jpeg")
        self.assertEqual(Extensions.GIF.path, "gif")


class TestGetFilePath(unittest.TestCase):
    def setUp(self):
        self.temp_dir = TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)

    def test_get_file_path_valid_hash(self):
        file_hash = "abcdef123456"
        expected = os.path.join("store", "ab", "abcdef123456")
        self.assertEqual(get_file_path(file_hash), expected)

    def test_get_file_path_short_hash(self):
        self.assertIsNone(get_file_path("a"))
        self.assertIsNone(get_file_path(""))

    def test_get_file_path_none_hash(self):
        with self.assertRaises(TypeError):
            get_file_path(None)


class TestAllowedFile(unittest.TestCase):
    def test_allowed_extensions(self):
        for ext in Extensions:
            filename = f"test.{ext.path}"
            self.assertTrue(allowed_file(filename))

    def test_disallowed_extensions(self):
        self.assertFalse(allowed_file("test.exe"))
        self.assertFalse(allowed_file("test."))
        self.assertFalse(allowed_file("test"))

    def test_no_extension(self):
        self.assertFalse(allowed_file("no_extension"))
        self.assertFalse(allowed_file("dot_at_end."))

    def test_uppercase_extensions(self):
        self.assertTrue(allowed_file("test.TXT"))
        self.assertTrue(allowed_file("test.PdF"))

    def test_multiple_dots(self):
        self.assertTrue(allowed_file("file.name.txt"))
        self.assertFalse(allowed_file("file.name.exe"))
