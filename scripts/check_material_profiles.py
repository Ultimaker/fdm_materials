#!/usr/bin/env python
from collections import OrderedDict
import os
import sys
import re
from typing import Dict, Optional, List


class MaterialProfilesValidator:
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

    def _getMaterialsDir(self, dirpath: str):
        for root_dir, dirnames, filenames in os.walk(dirpath):
            has_materials_file = any(fn.endswith(".xml.fdm_material") for fn in filenames)
            if not has_materials_file:
                for dirname in dirnames:
                    full_dir_path = os.path.join(root_dir, dirname)
                    return self._getMaterialsDir(full_dir_path)

            return dirpath

    #   Find all material files in a given directory.
    #   This returns a dictionary with filename as keys and it's loaded content as value.
    def _getAllMaterialsContentsInDir(self, directory: str) -> Dict[str, Optional[str]]:
        result = {}
        for _, _, filenames in os.walk(directory):
            for filename in filenames:
                file_path = os.path.join(directory, filename)
                if not filename.endswith(".xml.fdm_material"):
                    print("Skipping \"%s\"" % filename)
                    continue
                try:
                    with open(file_path, "r", encoding = "utf-8") as f:
                        result[filename] = f.read()
                except:
                    result[filename] = None
            break
        return result

    def validateAll(self, directory: str) -> bool:
        materials_dir = self._getMaterialsDir(os.path.abspath(directory))

        material_content_dict = self._getAllMaterialsContentsInDir(materials_dir)

        # Store all the guid's linked with their filename. This is later used to find out if there are duplicate guids.
        guid_dict = {}  # type: Dict[str, List[str]]

        for file_name, material_content in material_content_dict.items():
            guid = self._getGuid(material_content)
            if guid not in guid_dict:
                guid_dict[guid] = []
            guid_dict[guid].append(file_name)

        has_invalid_files = False
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


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.realpath(__file__))
    root_dir = os.path.abspath(os.path.join(script_dir, ".."))

    validator = MaterialProfilesValidator()
    is_everything_validated = validator.validateAll(root_dir)

    ret_code = 0 if is_everything_validated else 1
    sys.exit(ret_code)
