import os
import setuptools
from pip.download import PipSession
from pip.req import parse_requirements

PACKAGE_PATH = os.path.dirname(os.path.realpath(__file__))

# parse_requirements() returns generator of pip.req.InstallRequirement objects
PACKAGE_REQS = parse_requirements("requirements.txt", session=PipSession())

# reqs is a list of requirement
# e.g. ['tornado==3.2.2', '...']
REQS = [str(ir.req) for ir in PACKAGE_REQS]

if __name__ == "__main__":
    setuptools.setup(
        name="prjname-service1",
        version="1.0.0",
        description="Project Name Service 1",
        author="The Company",
        namespace_packages=['prjname'],
        packages=setuptools.find_packages(PACKAGE_PATH, exclude=["*.test",
                                                                 "*.test.*",
                                                                 "test.*",
                                                                 "test"]),
        keywords="prjname",
        install_requires=REQS,
        include_package_data=True,
        entry_points={
            'prjname.services': [
                'service1 = '
                    'prjname.service1.tornado.service1_command:Service1Command',
            ],
            'prjname.health.plugins': [
            ],
        },
    )
