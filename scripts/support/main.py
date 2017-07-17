import os
import sys

from gitHubConnector import GitHubConnector
from materialFileReader import MaterialFileReader
from materialsOutputFormatter import MaterialsOutputFormatter

## @brief Retrieves contents from GitHub for the Ultimaker/fdm_materials project.
# Reads the files and translates the data to an (static) HTML which shows what material is
# supported (or not) for which device and nozzle.
# @return 0 if successful
def main():

    working_dir = "/var/tmp/fdm_material_overview"
    github_url = "git@github.com:Ultimaker/fdm_materials.git"
    generated_file = "mat_overview.html"
    additional_devices = set(sys.argv[1:])

    nozzle_lookup = {
        "Ultimaker 2 Extended+": ["0.25 mm", "0.4 mm", "0.6 mm", "0.8 mm"],
        "Ultimaker 2+": ["0.25 mm", "0.4 mm", "0.6 mm", "0.8 mm"],
        "Ultimaker 3": ["AA 0.25", "AA 0.4", "AA 0.8", "BB 0.4", "BB 0.8"],
        "Ultimaker 3 Extended": ["AA 0.25", "AA 0.4", "AA 0.8", "BB 0.4", "BB 0.8"]
    }

    try:
        os.mkdir(working_dir)
    except OSError:
        pass

    github_connector = GitHubConnector(working_dir, github_url)
    github_connector.getSourceFiles()

    material_reader = MaterialFileReader(working_dir)
    materials = material_reader.read()

    materials_output_formatter = MaterialsOutputFormatter()

    excluded_devices = {
        "cartesio", "IMADE3D JellyBOX", "Ultimaker 2", "Ultimaker 2 Extended","Ultimaker 2 Go","Ultimaker Original"
    }

    filtered_devices = {dev for dev in material_reader.all_devices if dev not in excluded_devices}

    html = materials_output_formatter.toHtml(
        materials,
        filtered_devices | additional_devices,
        material_reader.all_nozzles,
        nozzle_lookup
    )

    with open(os.path.join(working_dir, generated_file), "w") as file:
        file.write(html)

    sys.exit(0)

if __name__ == "__main__":
    main()
