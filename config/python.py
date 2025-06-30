""" python deps for this project """

import config.shared


install_requires: list[str] = [
    "azure-identity",
    "azure-mgmt-resource",
    "azure-mgmt-compute",
    "azure-mgmt-network",
    "azure-mgmt-storage",
    "azure-mgmt-web",
]
build_requires: list[str] = config.shared.BUILD
test_requires: list[str] = config.shared.TEST
types_requires: list[str] = [
    "types-termcolor",
    "types-PyYAML",
]
requires = install_requires + build_requires + test_requires + types_requires
