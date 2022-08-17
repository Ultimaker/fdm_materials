# fdm_materials

<p align="center">
    <a href="https://github.com/Ultimaker/fdm_materials/actions/workflows/cicd.yml" alt="Unit Tests">
        <img src="https://github.com/Ultimaker/fdm_materials/actions/workflows/cicd.yml/badge.svg" /></a>
    <a href="https://github.com/Ultimaker/fdm_materials/actions/workflows/conan-package.yml" alt="Unit Tests">
        <img src="https://github.com/Ultimaker/fdm_materials/actions/workflows/conan-package.yml/badge.svg" /></a>
    <a href="https://github.com/Ultimaker/fdm_materials/issues" alt="Open Issues">
        <img src="https://img.shields.io/github/issues/ultimaker/fdm_materials" /></a>
    <a href="https://github.com/Ultimaker/fdm_materials/issues?q=is%3Aissue+is%3Aclosed" alt="Closed Issues">
        <img src="https://img.shields.io/github/issues-closed/ultimaker/fdm_materials?color=g" /></a>
    <a href="https://github.com/Ultimaker/fdm_materials/pulls" alt="Pull Requests">
        <img src="https://img.shields.io/github/issues-pr/ultimaker/fdm_materials" /></a>
    <a href="https://github.com/Ultimaker/fdm_materials/graphs/contributors" alt="Contributors">
        <img src="https://img.shields.io/github/contributors/ultimaker/fdm_materials" /></a>
    <a href="https://github.com/Ultimaker/fdm_materials" alt="Repo Size">
        <img src="https://img.shields.io/github/repo-size/ultimaker/fdm_materials?style=flat" /></a>
    <a href="https://github.com/Ultimaker/fdm_materials/blob/master/LICENSE" alt="License">
        <img src="https://img.shields.io/github/license/ultimaker/fdm_materials?style=flat" /></a>
</p>


FDM material database, used in Cura.

## License

![License](https://img.shields.io/github/license/ultimaker/fdm_materials?style=flat)  
fdm_materials is released under terms of the CC0-1.0 License. Terms of the license can be found in the LICENSE file. Or at
https://creativecommons.org/publicdomain/zero/1.0/

> But in general it boils down to:  
> **We waive all rights to the extend of the law. You can copy, modify, distribute as you like, even for commercial purposes**

## System Requirements

### Windows
- Python 3.6 or higher

### MacOs
- Python 3.6 or higher

### Linux
- Python 3.6 or higher

## How To Build

> **Note:**  
> We are currently in the process of switch our builds and pipelines to an approach which uses [Conan](https://conan.io/)
> and pip to manage our dependencies, which are stored on our JFrog Artifactory server and in the pypi.org.
> At the moment not everything is fully ported yet, so bare with us.

If you want to develop Cura with fdm_materials see the Cura Wiki: [Running Cura from source](https://github.com/Ultimaker/Cura/wiki/Running-Cura-from-Source)

If you have never used [Conan](https://conan.io/) read their [documentation](https://docs.conan.io/en/latest/index.html)
which is quite extensive and well maintained. Conan is a Python program and can be installed using pip

### 1. Configure Conan

```bash
pip install conan --upgrade
conan config install https://github.com/ultimaker/conan-config.git
conan profile new default --detect --force
```

Community developers would have to remove the Conan cura repository because it requires credentials. 

Ultimaker developers need to request an account for our JFrog Artifactory server at IT
```bash
conan remote remove cura
```

### 2. Clone fdm_materials
```bash
git clone https://github.com/Ultimaker/fdm_materials.git
cd fdm_materials
```

## Creating a new fdm_materials Conan package

To create a new fdm_materials Conan package such that it can be used in Cura and Uranium, run the following command:

```shell
conan create . fdm_materials/<version>@<username>/<channel> --build=missing --update
```

This package will be stored in the local Conan cache (`~/.conan/data` or `C:\Users\username\.conan\data` ) and can be used in downstream
projects, such as Cura and Uranium by adding it as a requirement in the `conanfile.py` or in `conandata.yml`.

Note: Make sure that the used `<version>` is present in the conandata.yml in the fdm_materials root

You can also specify the override at the commandline, to use the newly created package, when you execute the `conan install`
command in the root of the consuming project, with:


```shell
conan install . -build=missing --update --require-override=fdm_materials/<version>@<username>/<channel>
```

## Developing fdm_materials In Editable Mode

You can use your local development repository downsteam by adding it as an editable mode package.
This means you can test this in a consuming project without creating a new package for this project every time.

```bash
    conan editable add . fdm_materials/<version>@<username>/<channel>
```

Then in your downsteam projects (Cura) root directory override the package with your editable mode package.  

```shell
conan install . -build=missing --update --require-override=fdm_materials/<version>@<username>/<channel>
```