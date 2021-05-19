import os
import time

import docker
from docker.types import Mount
import requests

from traits.api import (
    HasStrictTraits, Directory, Int, Str, Enum, Property)


class PUFoamSession(HasStrictTraits):
    """Class used to initiate and handle a PUFoam simulation session,
    based on the POC Flask app wrapper
    """

    #: Local file path containing PUFoam simulation data files. The
    #: output files from the simulation will also be generated here.
    simulation_directory = Directory

    image_name = Str(
        "registry.gitlab.cc-asp.fraunhofer.de:4567/force/pufoam:latest"
    )

    #: Container name used when running PUFoam image
    container_name = Str('BDSS_PUFOAM')

    #: Protocol used to connect to the PUFoam container
    protocol = Enum('http', 'https')

    #: Host where the PUFoam app container is running
    host = Str('0.0.0.0')

    #: Port used to communicate with the PUFoam container
    port = Int(5000)

    _url = Property(Str, depends_on='protocol,host,port')

    def _get__url(self):
        return f"{self.protocol}://{self.host}:{self.port}"

    def start_container(self, timeout=5):
        """Runs the PUFoam image using Docker SDK. Obtains connection details
        to a Docker client from the local environment. Therefore if using a
        remote host the following environment variables should be set:

        .. envvar:: DOCKER_HOST

            The URL to the Docker host.

        .. envvar:: DOCKER_TLS_VERIFY

            Verify the host against a CA certificate.

        .. envvar:: DOCKER_CERT_PATH

            A path to a directory containing TLS certificates to use when
            connecting to the Docker host.
        """

        client = docker.from_env()

        kwargs = {
            "name": self.container_name,
            "ports": {f"{self.port}/tcp": (self.host, self.port)},
            "detach": True,
            "tty": True
        }
        if self.simulation_directory:
            # Sets up the bind mount to provide required simulation
            # input files. This approach could be edited in the future,
            # since it only works well
            # if the source is on the same machine as the target.
            kwargs['mounts'] = [
                Mount(type='bind', target="/shared/",
                      source=self.simulation_directory)
            ]

        # Start the container running on a assigned host + port
        client.containers.run(
            self.image_name,
            **kwargs
        )

        # Wait for the Flask app inside container to come online or
        # return False if exceeds timeout period
        start = time.time()
        while (time.time() - start) < timeout:
            if self.check_status(timeout=timeout):
                return True
            time.sleep(1)
        return False

    def upload_mesh(self, mesh_path):

        with open(mesh_path, 'r') as infile:
            file_string = infile.read()

        file_name = os.path.basename(mesh_path)
        file_data = file_string.encode()

        return requests.post(
            f"{self._url}/upload/constant/triSurface",
            files={
                'file': (file_name, file_data)
            }
        )

    def unv_to_foam(self, file_name=None):
        return requests.get(
            f"{self._url}/unv_to_foam/system/{file_name}")

    def transform_scale(self, scale, file_name):
        return requests.post(
            f"{self._url}/transform/constant/triSurface",
            data={
                'file_name': file_name,
                'scale': scale
            }
        )

    def block_mesh(self):
        """Prepare block mesh data for a PUFoam simulation using the
        Flask API"""
        return requests.get(f"{self._url}/block_mesh")

    def snappy_hex_mesh(self):
        """Prepare snappy hex mesh data for a PUFoam simulation using
        the Flask API"""
        return requests.get(f"{self._url}/snappy_hex_mesh")

    def surface_feature_extract(self):
        """Extract surface features for a PUFoam simulation using the
        Flask API"""
        return requests.get(f"{self._url}/surface_feature_extract")

    def set_fields(self):
        """Prepare fields data for a PUFoam simulation using the
        Flask API"""
        return requests.get(f"{self._url}/set_fields")

    def clear_files(self):
        """Clear any output files from PUFoam simulation using
        Flask API"""
        return requests.get(f"{self._url}/clean")

    def run_pufoam(self):
        """Run a PUFoam simulation using the Flask API"""
        return requests.get(f"{self._url}/run")

    def upload_data_dict(self, data_dict):
        """Upload contents of a PUFoam dictionary file to the Flask app"""

        file_string = data_dict.format_output()
        file_data = file_string.encode()

        response = requests.post(
            f"{self._url}/upload/{data_dict.file_dir}",
            files={
                'file': (data_dict.file_name, file_data)
            }
        )
        return response

    def check_status(self, timeout=5):
        """Attempts to contact container using Flask API. Returns a
        boolean determining outcome of process
        """
        try:
            response = requests.get(f"{self._url}/", timeout=timeout)
            return response.text == 'Hello World'
        except Exception:
            return False
