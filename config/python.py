""" python deps for this project """

install_requires: list[str] = [
    "azure-identity",
    "azure-mgmt-resource",
    "azure-mgmt-compute",
    "azure-mgmt-network",
    "azure-mgmt-storage",
    "azure-mgmt-web",
]
build_requires: list[str] = [
    "pydmt",
    "pymakehelper",

    "pylint",
    "pytest",
    "mypy",
    "ruff",
    # types
    "types-termcolor",
    "types-PyYAML",
]
requires = install_requires + build_requires
