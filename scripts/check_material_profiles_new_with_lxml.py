#!/usr/bin/env python3
# This script is dedicated to the public domain under the terms of the CC0 license.

import os
import sys
import re
from typing import Dict, Optional, List

from lxml import etree


##  This is a material profile validator that works with the lxml library.
#
#   This version is currently unused on our CI server because it was difficult
#   to install lxml on that server. We store it here only as a back-up for when
#   we migrate to a different CI system.
class MaterialProfilesValidator:

    __namespaces = {
        "um": "http://www.ultimaker.com/material",
        "cura": "http://www.ultimaker.com/cura",
    }

    def __init__(self) -> None:
        self._guid_pattern = re.compile(r"<GUID>.*</GUID>")

    def _getGuid(self, content: str) -> str:
        guid = None
        for line in content.splitlines():
            line = line.strip()
            if self._guid_pattern.match(line):
                guid = line.strip("<GUID>").strip("</GUID>")
                break
        return guid

    def _getMaterialsDir(self, dirpath: str) -> str:
        for root_dir, dirnames, filenames in os.walk(dirpath):
            has_materials_file = any(fn.endswith(".xml.fdm_material") for fn in filenames)
            if not has_materials_file:
                for dirname in dirnames:
                    full_dir_path = os.path.join(root_dir, dirname)
                    return self._getMaterialsDir(full_dir_path)

            return dirpath

    #   Find all material files in a given directory.
    #   This returns a dictionary with filename as keys and it's loaded content as value.
    def _getAllMaterialsContentsInDir(self, directory: str) -> Dict[str, Dict[str, str]]:
        result = {}  # type: Dict[str, Dict[str, str]]
        for _, _, filenames in os.walk(directory):
            for filename in filenames:
                file_path = os.path.join(directory, filename)
                if not filename.endswith(".xml.fdm_material"):
                    continue

                result[filename] = {"content": "",
                                    "error": ""}
                try:
                    with open(file_path, "r", encoding = "utf-8") as f:
                        result[filename]["content"] = f.read()
                except Exception as e:
                    print("Failed to read file [%s] : %s", filename, e)
                    result[filename]["error"] = str(e)
            break
        return result

    # Gets the material brand name from the given lxml.etree root node. Return None if the brand cannot be found,
    # otherwise the brand text.
    def _getMaterialBrandName(self, root_node: "etree.Element") -> Optional[str]:
        node = root_node.xpath("./um:metadata/um:name/um:brand", namespaces = self.__namespaces)
        if not node:
            return None

        return node[0].text

    def validateAll(self, repo_root_dir: str) -> bool:
        repo_root_dir = os.path.abspath(repo_root_dir)

        materials_dir = self._getMaterialsDir(repo_root_dir)
        fdmmaterial_xsd_file_path = os.path.join(repo_root_dir, "scripts", "fdmmaterial.xsd")

        material_content_dict = self._getAllMaterialsContentsInDir(materials_dir)
    
        # Store all the guid's linked with their filename. This is later used to find out if there are duplicate guids.
        guid_dict = {}  # type: Dict[str, List[str]]
        xmlschema_doc = etree.parse(fdmmaterial_xsd_file_path)
        xmlschema = etree.XMLSchema(xmlschema_doc)
        has_invalid_files = False

        for file_name, file_info_dict in material_content_dict.items():
            # Show error message if the file failed to load
            if len(file_info_dict["error"]) > 0:
                print("{file_name} failed to load, error: {error}".format(file_name = file_name,
                                                                          error = file_info_dict["error"]))
                has_invalid_files = True
                continue

            material_content = file_info_dict["content"]

            try:
                xml_doc = etree.fromstring(material_content.encode())
            except etree.XMLSyntaxError as e:
                print("{file_name} contains XML syntax error".format(file_name = file_name))
                print(e)
                has_invalid_files = True
                continue

            # Validate the file content with the XSD file.
            guid = self._getGuid(material_content)
            if guid not in guid_dict:
                guid_dict[guid] = []
            guid_dict[guid].append(file_name)
            try:
                xmlschema.assertValid(xml_doc)
            except etree.DocumentInvalid as e:
                has_invalid_files = True
                print("{file_name} is not a valid fdm material".format(file_name = file_name))
                print(e)
                continue

            # Make sure that only the material files such as "generic_<bla>" can have branch "Generic".
            brand = self._getMaterialBrandName(xml_doc)
            if brand is None:
                has_invalid_files = True
                print("{file_name} Could not find <brand>".format(file_name = file_name))
                continue
            if len(brand) == 0:
                has_invalid_files = True
                print("{file_name} contains an empty string for <brand>".format(file_name = file_name))
                continue
            if brand.lower() == "generic" and not file_name.lower().startswith("generic_"):
                has_invalid_files = True
                print("{file_name} has brand [{brand}] but only material files named as [generic*] can have brand [Generic]".format(
                      file_name = file_name, brand = brand))
                continue

        # Check for duplicate GUIDs
        for guid, file_item_list in guid_dict.items():
            if len(file_item_list) <= 1:
                continue
            has_invalid_files = True

            if guid is not None:
                print("-> The following files contain the same GUID [%s]:" % guid)
            else:
                print("-> The following files DO NOT contain any GUID:")
            for file_item in file_item_list:
                print("    -- [%s]" % file_item)
            print("-> PLEASE make sure to generate unique GUIDs for each material.")

        return not has_invalid_files


def main():
    script_dir = os.path.dirname(os.path.realpath(__file__))
    root_dir = os.path.abspath(os.path.join(script_dir, ".."))

    validator = MaterialProfilesValidator()
    is_everything_validated = validator.validateAll(root_dir)

    if is_everything_validated:
        print("All material profiles seem valid.")

    ret_code = 0 if is_everything_validated else 1
    sys.exit(ret_code)


if __name__ == "__main__":
    main()
