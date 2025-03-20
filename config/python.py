from typing import List


dev_requires: List[str] = [
    "pypitools",
    "black",
]
config_requires: List[str] = [
    "pyclassifiers",
]
install_requires: List[str] = [
    "azure-identity",
    "azure-mgmt-resource",
    "azure-mgmt-compute",
    "azure-mgmt-network",
    "azure-mgmt-storage",
    "azure-mgmt-web",
]
build_requires: List[str] = [
    "pymakehelper",
    "pydmt",
]
test_requires: List[str] = [
    "pylint",
    "pytest",
    "pytest-cov",
    "flake8",
    "pyflakes",
    "pycodestyle",
    "mypy",
    # types
    "types-termcolor",
    "types-PyYAML",
]
requires = config_requires + install_requires + build_requires + test_requires
