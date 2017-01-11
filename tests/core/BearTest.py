from os.path import abspath, exists, isfile, join, getmtime
import shutil
import unittest

from coalib.core.Bear import Bear
from coalib.results.Result import Result
from coalib.settings.Section import Section
from coalib.settings.Setting import Setting


class BearWithPrerequisites(Bear):
    prerequisites_fulfilled = True

    def __init__(self, section, file_dict):
        Bear.__init__(self, section, file_dict)

        self.was_executed = False

    def run(self):
        self.was_executed = True
        return []

    @classmethod
    def check_prerequisites(cls):
        return cls.prerequisites_fulfilled


class BearTest(unittest.TestCase):

    def tearDown(self):
        for bear in [Bear, BearWithPrerequisites]:
            if exists(bear.data_dir):
                shutil.rmtree(bear.data_dir)

    def test_invalid_types_at_instantiation(self):
        with self.assertRaises(TypeError):
            Bear(Section('test-section'), 2)

        with self.assertRaises(TypeError):
            Bear(None, {})

    def test_analyze(self):
        with self.assertRaises(NotImplementedError):
            Bear(Section('test-section'), {}).analyze()

    def test_generate_tasks(self):
        with self.assertRaises(NotImplementedError):
            Bear(Section('test-section'), {}).generate_tasks()

    def test_check_prerequisites(self):
        section = Section('test-section')
        filedict = {}

        BearWithPrerequisites.prerequisites_fulfilled = True
        BearWithPrerequisites(section, filedict)

        BearWithPrerequisites.prerequisites_fulfilled = False
        with self.assertRaises(RuntimeError) as cm:
            BearWithPrerequisites(section, filedict)

        self.assertEqual(
            str(cm.exception),
            'The bear BearWithPrerequisites does not fulfill all '
            'requirements.')

        BearWithPrerequisites.prerequisites_fulfilled = (
            'This is on purpose due to running inside a test.')
        with self.assertRaises(RuntimeError) as cm:
            BearWithPrerequisites(section, filedict)

        self.assertEqual(
            str(cm.exception),
            'The bear BearWithPrerequisites does not fulfill all '
            'requirements. This is on purpose due to running inside a test.')

    def test_new_result(self):
        bear = Bear(Section('test-section'), {})
        result = bear.new_result('test message', '/tmp/testy')
        expected = Result.from_values(bear, 'test message', '/tmp/testy')
        self.assertEqual(result, expected)

    def test_get_config_dir(self):
        section = Section('default')
        section.append(Setting('files', '**', '/path/to/dir/config'))
        uut = Bear(section, {})
        self.assertEqual(uut.get_config_dir(), abspath('/path/to/dir'))

    def test_download_cached_file(self):
        uut = Bear(Section('test-section'), {})

        url = 'https://google.com'
        filename = 'google.html'
        self.assertFalse(isfile(join(uut.data_dir, filename)))
        expected_filename = join(uut.data_dir, filename)
        result_filename = uut.download_cached_file(url, filename)
        self.assertEqual(result_filename, expected_filename)
        expected_time = getmtime(join(uut.data_dir, filename))
        result_filename = uut.download_cached_file(url, filename)
        self.assertEqual(result_filename, expected_filename)
        result_time = getmtime(join(uut.data_dir, filename))
        self.assertEqual(result_time, expected_time)
