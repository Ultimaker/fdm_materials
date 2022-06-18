import os

from conan import ConanFile
from conans import tools
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=1.47.0"


class FDM_MaterialsConan(ConanFile):
    name = "fdm_materials"
    license = "LGPL-3.0"
    author = "Ultimaker B.V."
    url = "https://github.com/Ultimaker/fdm_materials"
    description = "FDM Material database"
    topics = ("conan", "profiles", "cura", "ultimaker", "filament")
    build_policy = "missing"
    exports = "LICENSE*"
    settings = "os", "compiler", "build_type", "arch"
    no_copy_source = True
    scm = {
        "type": "git",
        "subfolder": ".",
        "url": "auto",
        "revision": "auto"
    }

    def validate(self):
        if tools.Version(self.version) <= tools.Version("4"):
            raise ConanInvalidConfiguration("Only versions 5+ are support")

    def package(self):
        self.copy("*.fdm_material", src = ".", dst = os.path.join(self.cpp.package.resdirs[0], "materials"))
        self.copy("*.sig", src = ".", dst = os.path.join(self.cpp.package.resdirs[0], "materials"))

    def package_id(self):
        del self.info.settings.os
        del self.info.settings.compiler
        del self.info.settings.build_type
        del self.info.settings.arch
