#!/usr/bin/env python3
"""
Validation for `*.xml.fdm_material` Material Profile files, based on an XML Schema
Definition.

This script is dedicated to the public domain under the terms of the CC0 license.
"""

import logging
import os
from pathlib import Path
import sys
from typing import Dict, Iterable, Optional, List

from lxml import etree


NAMESPACES = {
    "um": "http://www.ultimaker.com/material",
    "cura": "http://www.ultimaker.com/cura",
}


class MaterialProfile:

    def __init__(self, document: etree.Element, filename: Optional[Path]) -> None:
        self.document = document
        self.filename = filename

    @classmethod
    def fromFile(cls, p: Path) -> 'MaterialProfile':
        with p.open("rb") as f:
            return cls(etree.fromstring(f.read()), p)

    @property
    def brand(self) -> Optional[str]:
        """Get the material brand name from the given lxml.etree root node.

        @returns None if the brand cannot be found, otherwise the brand text.
        """
        node = self.document.xpath("./um:metadata/um:name/um:brand", namespaces=NAMESPACES)
        return node[0].text if node else None

    @property
    def guid(self) -> Optional[str]:
        node = self.document.xpath("./um:metadata/um:GUID", namespaces=NAMESPACES)
        return node[0].text if node else None


class MaterialProfilesValidator:
    """Material Profile validator that validates against an XML Schema"""

    class ValidationError(Exception):
        pass

    def __init__(self, xsd_file: Path) -> None:
        self._schema = self.loadSchema(xsd_file)
        self._guids_seen: Dict[str, Path] = dict()

    @staticmethod
    def loadSchema(xsd_file: Path) -> etree.XMLSchema:
        xmlschema_doc = etree.parse(str(xsd_file))
        return etree.XMLSchema(xmlschema_doc)

    def validate(self, profile: MaterialProfile) -> None:
        """Validate the given material profile file against the XML schema, plus additional rules

        Additional rules:
        - Only material profile files whose name starts with "generic_" are allowed to have
          their brand set to "Generic".
        - The GUID in each profile should be unique; no other profiles can use the same GUID.

        @raises ValidationError if any problems are found.
        """
        # Validate the file content with the XSD file.
        try:
            self._schema.assertValid(profile.document)
        except etree.DocumentInvalid as e:
            raise self.ValidationError(f"{profile.filename} is not a valid FDM Material file:\n{e}")

        # Make sure that only the material files such as "generic_<bla>" can have brand "Generic".
        brand = profile.brand
        if brand is None:
            raise self.ValidationError(f"{profile.filename} is missing '<brand>' information")
        elif len(brand) == 0:
            raise self.ValidationError(f"{profile.filename} contains empty '<brand>' information")
        elif brand.lower() == "generic" and not profile.filename.name.lower().startswith("generic_"):
            raise self.ValidationError(
                f"{profile.filename} contains a 'generic' brand, but only material profiles with a "
                f"filename that starts with 'generic_' are allowed to have a generic brand set.")

        # Check that we haven't seen this GUID before.
        guid = profile.guid
        if not guid:
            raise self.ValidationError(f"{profile.filename} is missing '<GUID>' information")
        if guid in self._guids_seen and self._guids_seen.get(guid) != profile.filename:
            raise self.ValidationError(
                f"{profile.filename} has duplicate GUID '{guid}', the same GUID is also "
                f"used by: {self._guids_seen[guid]}")
        self._guids_seen[guid] = profile.filename


def validateFiles(xsd_file: Path, files_to_check: Iterable[Path]) -> bool:
    """Validate a given list of FDM material profile files using the given XSD schema file

    @returns Whether all files were validated successfully
    """
    validator = MaterialProfilesValidator(xsd_file)

    n_success, n_fail = 0, 0

    for f in files_to_check:
        try:
            logging.info(f"Checking {f.name}")
            profile = MaterialProfile.fromFile(f)
            validator.validate(profile)
        except etree.XMLSyntaxError as e:
            logging.error(f"{f} is not a valid XML file:\n{e}")
            n_fail += 1
        except MaterialProfilesValidator.ValidationError as e:
            logging.error(str(e))
            n_fail += 1
        else:
            n_success += 1

    logging.info(f"Checked {n_success + n_fail} file(s): {n_success} OK, {n_fail} error(s)")
    return (n_fail == 0)


def main():
    import argparse

    SCRIPT_DIR = Path(__file__).parent.resolve()
    PROJECT_DIR = SCRIPT_DIR.parent

    parser = argparse.ArgumentParser(
        description="Validator for Material Profile (*.xml.fdm_material) files")
    parser.add_argument("-x", "--xsd", default=(SCRIPT_DIR / "fdmmaterial.xsd"),
                        help="XML Schema Definition file to use for validation (default: fdmmaterial.xsd)")
    parser.add_argument("file", metavar="FILE", nargs="*",
                        help="One or more *.xml.fdm_material files to check. Default: all files in project root.")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Increase output verbosity.")
    args = parser.parse_args()

    logging.basicConfig(
        format="%(levelname)s %(message)s",
        level=(logging.INFO if args.verbose else logging.WARNING))

    if args.file:
        files_to_check = [Path(_) for _ in args.file]
    else:
        files_to_check = sorted(list(PROJECT_DIR.glob("*.fdm_material")))

    success = validateFiles(args.xsd, files_to_check)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
