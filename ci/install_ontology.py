import emmo_cfd
import subprocess


def install():
    subprocess.run(
        [
            "pico",
            "install",
            emmo_cfd.get_file("ontology.pufoam", ".yml"),
            "--overwrite"
        ]
    )


if __name__ == '__main__':
    install()
