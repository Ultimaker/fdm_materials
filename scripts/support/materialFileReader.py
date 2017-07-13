import os
import glob
import copy
import xml.etree.ElementTree as EltTree

from material import Material
from profile import Profile
from deviceSupport import DeviceSupport
from nozzleSupport import NozzleSupport


class MaterialFileReader:

    __file_ext = '*.fdm_material'
    all_devices = set()
    all_nozzles = set()

    def __init__(self, folder):
        self.__working_fld = folder

    def read(self) -> []:
        materials = []
        fld = os.path.join(self.__working_fld, self.__file_ext)
        for filename in glob.glob(fld):
            file = open(filename, "r")

            mat = file.read()

            if mat.startswith("<?xml"):
                materials.append(self.xml_to_material(mat, os.path.basename(file.name)))
            else:
                self.json_to_material(mat)
        return materials

    def xml_to_material(self, dat, filename) -> Material:
        material = Material()
        root = EltTree.fromstring(dat)

        # Set basic properties
        ns = {"m": "http://www.ultimaker.com/material"}
        name_data = root.find('./m:metadata/m:name', ns)

        material.brand = name_data.find('m:brand', ns).text
        material.material = name_data.find('m:material', ns).text
        material.color = name_data.find('m:color', ns).text
        material.filename = filename

        color_code_elt = root.find('./m:metadata/m:color_code', ns)

        if color_code_elt is not None:
            material.color_code = color_code_elt.text

        material.version = root.find('./m:metadata/m:version', ns).text
        material.guid = root.find('./m:metadata/m:GUID', ns).text
        material.diameter = root.find('./m:properties/m:diameter', ns).text

        # Find global 'hardware compatible' setting
        global_support_elt = root.find("./m:settings/m:setting[@key='hardware compatible']", ns)
        global_support = 'unknown'

        if global_support_elt is not None:
            global_support = global_support_elt.text

        # Find profiles
        for machine in root.findall('./m:settings/m:machine', ns):

            # Find all devices
            device_support_elt = machine.find("./m:setting[@key='hardware compatible']", ns)

            device_supported = global_support

            # Find device 'hardware compatible' setting
            if device_support_elt is not None:
                device_supported = device_support_elt.text

            nozzles = {}

            # Add nozzle support settings to profile
            for hotend in machine.findall('./m:hotend', ns):
                nozzle_support = NozzleSupport()
                nozzle_support.id = hotend.get('id')
                self.all_nozzles.add(nozzle_support.id)

                nozzle_support_elt = hotend.find("./m:setting[@key='hardware compatible']", ns)

                if nozzle_support_elt is not None:
                    nozzle_support.is_supported = nozzle_support_elt.text
                else:
                    nozzle_support.is_supported = device_supported

                nozzles[nozzle_support.id] = nozzle_support

            # Add device support settings to profile
            for identifier in machine.findall('./m:machine_identifier', ns):
                product = identifier.get('product')
                self.all_devices.add(product)

                device_support = DeviceSupport()
                device_support.name = product
                device_support.is_supported = device_supported

                profile = Profile()
                profile.nozzles = copy.deepcopy(nozzles)
                profile.device = device_support

                material.profiles[product] = profile

        return material

    def json_to_material(self, dat):
        raise NotImplementedError('Not expecting JSON yet')
