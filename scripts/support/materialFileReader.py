import os
import glob
import copy
import xml.etree.ElementTree as EltTree

from material import Material
from profile import Profile
from deviceSupport import DeviceSupport
from nozzleSupport import NozzleSupport


class MaterialFileReader:
    """
    Reads and parses material definition files.
    """

    all_devices = set()
    all_nozzles = set()

    __ns = {"m": "http://www.ultimaker.com/material"}
    __file_ext = '*.fdm_material'

    def __init__(self, folder):
        self.__working_dir = folder

    def read(self) -> []:
        """
        Reads material definitions from a directory. Parses either XML or JSON (currently not supported).
        Please not: not every bit of information in the XML is used.

        :return: List of material objects.
        """

        materials = []
        fld = os.path.join(self.__working_dir, self.__file_ext)
        for filename in glob.glob(fld):
            file = open(filename, "r")

            mat = file.read()

            if mat.startswith("<?xml"):
                materials.append(self.xmlToMaterial(mat, os.path.basename(file.name)))
            else:
                self.jsonToMaterial(mat)
        return materials

    def xmlToMaterial(self, data, filename) -> Material:
        """
        Converts the raw XML data from a material file to a material object.

        :param data: Raw XML data
        :param filename: Material data file name
        :return: Material data object
        """
        material = Material()
        root = EltTree.fromstring(data)

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
        """
        Parses the nozzle specific XML data from the XML data.

        :param machine: raw machine XML material data.
        :param device_supported: List of devices supported by the material.
        :return:  dictionary containing 'nozzle id' - 'NozzleSupport' pairs.
        """

        nozzles = {}

        for hotend in machine.findall("./m:hotend", self.__ns):
            nozzle_support = NozzleSupport()
            nozzle_support.id = hotend.get("id")
            self.all_nozzles.add(nozzle_support.id)

            nozzle_support_elt = hotend.find("./m:setting[@key='hardware compatible']", self.__ns)

            if nozzle_support_elt is not None:
                nozzle_support.support = nozzle_support_elt.text
            else:
                nozzle_support.support = device_supported

            nozzles[nozzle_support.id] = nozzle_support

        return nozzles

    def collectProfiles(self, material, machine, nozzles, device_supported):
        """
        Parses nozzle and device support data by matching device with available nozzles and
        registers their support type.

        :param material: material object to add results to.
        :param machine: raw machine XML material data.
        :param nozzles: list of available nozzels for device.
        :param device_supported: list of supported devices.
        """

        for identifier in machine.findall("./m:machine_identifier", self.__ns):
            product = identifier.get("product")
            self.all_devices.add(product)

            device_support = DeviceSupport()
            device_support.name = product
            device_support.support = device_supported

            profile = Profile()
            profile.nozzles = copy.deepcopy(nozzles)
            profile.device = device_support

            material.profiles[product] = profile

    def jsonToMaterial(self, data):
        """
        I was under the impression that JSON material files existed, but there does not seems to be one.
        This is a placeholder for parsing JSON material should they appear in the future.

        Currently throws an NotImplementedError exception.

        :param data: raw JSON material data.
        :return: Nothing yet.
        """
        raise NotImplementedError("Not expecting JSON yet")
