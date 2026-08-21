-- python deps for this project

dofile("config/shared.lua")

-- append every element of "src" onto "dst"
local function extend(dst, src)
    for _, value in ipairs(src) do
        table.insert(dst, value)
    end
    return dst
end

INSTALL_REQUIRES = {
    "azure-identity",
    "azure-mgmt-resource",
    "azure-mgmt-compute",
    "azure-mgmt-network",
    "azure-mgmt-storage",
    "azure-mgmt-web",
}
BUILD_REQUIRES = BUILD
TEST_REQUIRES = TEST
TYPES_REQUIRES = {
    "types-termcolor",
    "types-PyYAML",
}

REQUIRES = {}
extend(REQUIRES, INSTALL_REQUIRES)
extend(REQUIRES, BUILD_REQUIRES)
extend(REQUIRES, TEST_REQUIRES)
extend(REQUIRES, TYPES_REQUIRES)
