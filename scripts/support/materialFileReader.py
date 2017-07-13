import os
import glob
import copy
import xml.etree.ElementTree as EltTree

from material import Material
from profile import Profile
from deviceSupport import DeviceSupport
from nozzleSupport import NozzleSupport


class MaterialFileReader:

    all_devices = set()
    all_nozzles = set()

    __ns = {"m": "http://www.ultimaker.com/material"}
    __file_ext = '*.fdm_material'

    def __init__(self, folder):
        self.__working_fld = folder

    def read(self) -> []:
        materials = []
        fld = os.path.join(self.__working_fld, self.__file_ext)
        for filename in glob.glob(fld):
            file = open(filename, "r")

            mat = file.read()

            if mat.startswith("<?xml"):
                materials.append(self.xmlToMaterial(mat, os.path.basename(file.name)))
            else:
                self.jsonToMaterial(mat)
        return materials

    def xmlToMaterial(self, dat, filename) -> Material:
        material = Material()
        root = EltTree.fromstring(dat)

        # Set basic properties
        name_data = root.find("./m:metadata/m:name", self.__ns)

        material.brand = name_data.find("m:brand", self.__ns).text
        material.material = name_data.find("m:material", self.__ns).text
        material.color = name_data.find("m:color", self.__ns).text
        material.filename = filename

        color_code_elt = root.find("./m:metadata/m:color_code", self.__ns)

        if color_code_elt is not None:
            material.color_code = color_code_elt.text

        material.version = root.find("./m:metadata/m:version", self.__ns).text
        material.guid = root.find("./m:metadata/m:GUID", self.__ns).text
        material.diameter = root.find("./m:properties/m:diameter", self.__ns).text

        # Find global 'hardware compatible' setting
        global_support_elt = root.find("./m:settings/m:setting[@key='hardware compatible']", self.__ns)
        global_support = "unknown"

        if global_support_elt is not None:
            global_support = global_support_elt.text

        for machine in root.findall("./m:settings/m:machine", self.__ns):

            device_support_elt = machine.find("./m:setting[@key='hardware compatible']", self.__ns)
            device_supported = global_support

            if device_support_elt is not None:
                device_supported = device_support_elt.text

            nozzles = self.collectNozzles(machine, device_supported)
            self.collectProfiles(material, machine, nozzles, device_supported)

        return material

    def collectNozzles(self, machine, device_supported) -> {}:
        nozzles = {}

        for hotend in machine.findall("./m:hotend", self.__ns):
            nozzle_support = NozzleSupport()
            nozzle_support.id = hotend.get("id")
            self.all_nozzles.add(nozzle_support.id)

            nozzle_support_elt = hotend.find("./m:setting[@key='hardware compatible']", self.__ns)

            if nozzle_support_elt is not None:
                nozzle_support.is_supported = nozzle_support_elt.text
            else:
                nozzle_support.is_supported = device_supported

            nozzles[nozzle_support.id] = nozzle_support

        return nozzles

    def collectProfiles(self, material, machine, nozzles, device_supported):

        for identifier in machine.findall("./m:machine_identifier", self.__ns):
            product = identifier.get("product")
            self.all_devices.add(product)

            device_support = DeviceSupport()
            device_support.name = product
            device_support.is_supported = device_supported

            profile = Profile()
            profile.nozzles = copy.deepcopy(nozzles)
            profile.device = device_support

            material.profiles[product] = profile

    def jsonToMaterial(self, dat):
        raise NotImplementedError("Not expecting JSON yet")
