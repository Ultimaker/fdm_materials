import os

from conan import ConanFile
from conan.tools.files import copy
from conan.tools.scm import Version
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=1.56.0"


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

    def export_sources(self):
        copy(self, "*.fdm_material", self.recipe_folder, self.export_sources_folder)
        copy(self, "*.sig", self.recipe_folder, self.export_sources_folder)

    def validate(self):
        if Version(self.version) <= Version("4"):
            raise ConanInvalidConfiguration("Only versions 5+ are support")

    def package(self):
        copy(self, "*.fdm_material", self.source_folder, os.path.join(self.package_folder, "res", "resources", "materials"), keep_path = False)
        copy(self, "*.sig", self.source_folder, os.path.join(self.package_folder, "res", "resources", "materials"), keep_path = False)

    def package_info(self):
        self.cpp_info.includedirs = []
        self.cpp_info.resdirs = ["res"]

    def package_id(self):
        self.info.clear()
