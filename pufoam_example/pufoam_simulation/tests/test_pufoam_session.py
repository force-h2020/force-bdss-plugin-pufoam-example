from unittest import TestCase, mock

from pufoam_example.pufoam_simulation.pufoam_data.data_format import (
    PUFoamDataDict)
from pufoam_example.pufoam_simulation.pufoam_session import PUFoamSession
from pufoam_example.tests.probe_classes import ProbeResponse

OPEN_PATH = 'pufoam_example.pufoam_simulation.pufoam_session.open'


def return_url(url, **kwargs):
    return ProbeResponse(text=url)


class TestPUFoamSession(TestCase):

    def setUp(self):
        self.session = PUFoamSession()

    def test_url(self):
        self.assertEqual(
            'http://0.0.0.0:5000', self.session._url
        )
        self.session.protocol = 'https'
        self.session.host = 'my_domain'
        self.session.port = 7000
        self.assertEqual(
            'https://my_domain:7000', self.session._url
        )

    def test_upload_data_dict(self):
        control_dict = PUFoamDataDict()

        def return_url_name(url, files, **kwargs):
            text = ' '.join([url, files['file'][0]])
            return ProbeResponse(text=text)

        with mock.patch('requests.post') as mock_post:
            mock_post.side_effect = return_url_name
            self.assertEqual(
                'http://0.0.0.0:5000/upload/ default',
                self.session.upload_data_dict(control_dict).text
            )

    def test_upload_mesh(self):

        def return_url_name(url, files, **kwargs):
            text = ' '.join([url, files['file'][0]])
            return ProbeResponse(text=text)

        with mock.patch('requests.post') as mock_post:
            mock_post.side_effect = return_url_name
            with mock.patch(OPEN_PATH, mock.mock_open()):
                self.assertEqual(
                    'http://0.0.0.0:5000/upload/constant/triSurface'
                    ' default',
                    self.session.upload_mesh('default').text
                )

    def test_unv_to_foam(self):

        with mock.patch('requests.get') as mock_get:
            mock_get.side_effect = return_url
            self.assertEqual(
                'http://0.0.0.0:5000/unv_to_foam/system/default',
                self.session.unv_to_foam('default').text
            )

    def test_block_mesh(self):

        with mock.patch('requests.get') as mock_post:
            mock_post.side_effect = return_url
            self.assertEqual(
                'http://0.0.0.0:5000/block_mesh',
                self.session.block_mesh().text
            )

    def test_check_status(self):

        def raise_error(*args, **kwargs):
            raise Exception

        with mock.patch('requests.get') as mock_get:
            mock_get.return_value = ProbeResponse()
            self.assertTrue(self.session.check_status())

            mock_get.return_value = ProbeResponse(text='')
            self.assertFalse(self.session.check_status())

            mock_get.new_callable = raise_error
            self.assertFalse(self.session.check_status())

    def test_set_fields(self):
        with mock.patch('requests.get') as mock_get:
            mock_get.side_effect = return_url
            self.assertEqual(
                'http://0.0.0.0:5000/set_fields',
                self.session.set_fields().text
            )

    def test_clear_files(self):
        with mock.patch('requests.get') as mock_get:
            mock_get.side_effect = return_url
            self.assertEqual(
                'http://0.0.0.0:5000/clean',
                self.session.clear_files().text
            )

    def test_run_pufoam(self):
        with mock.patch('requests.get') as mock_get:
            mock_get.side_effect = return_url
            self.assertEqual(
                'http://0.0.0.0:5000/run',
                self.session.run_pufoam().text
            )
