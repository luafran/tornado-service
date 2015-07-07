import os
import setuptools
from pip.download import PipSession
from pip.req import parse_requirements

PACKAGE_PATH = os.path.dirname(os.path.realpath(__file__))
GLOBAL_PATH = os.path.dirname(PACKAGE_PATH)

# parse_requirements() returns generator of pip.req.InstallRequirement objects
PACKAGE_REQS = parse_requirements("requirements.txt", session=PipSession())

# reqs is a list of requirement
# e.g. ['tornado==3.2.2', '...']
REQS = [str(ir.req) for ir in PACKAGE_REQS]

if __name__ == "__main__":
    setuptools.setup(
        name="prjname-common",
        version="0.1",
        description="Project Name Common",
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
            'console_scripts': [
                'prjname-runservice = prjname.common.tornado.runservice:main'
            ],
            'prjname.services': [
                'all = prjname.common.tornado.all_command:AllCommand',
            ],
        },
    )
