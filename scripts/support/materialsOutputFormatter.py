import datetime


class MaterialsOutputFormatter:

    __html = "<html><head><title>Material support overview</title></head>\r\n<style TYPE=\"text/css\">" \
             "<!--\r\n" \
             "table{{border-collapse: collapse;}}\r\n" \
             "td{{padding:2px 2px 2px 2px;border:1px solid;}}\r\n" \
             ".sep{{border-left:2px solid;}}" \
             "a{{text-decoration:none;color:black;}}" \
             "td.unknown{{background-color:#ffdd99;}}\r\n" \
             "td.yes{{background-color:green;}}\r\n" \
             "td.hdr{{background-color:grey;}}\r\n" \
             "td.lbl{{background-color:lightgrey;}}\r\n" \
             "td.no{{background-color:red;}}\r\n-->" \
             "abbr{{text-decoration:none !important;}}" \
             "</style>" \
             "<body>\r\n" \
             "<table>" \
             "<tr><td class=\"hdr\" colspan=\"2\">Legend</td></tr>" \
             "<tr><td class=\"no\">No</td><td>Not supported</td></tr>" \
             "<tr><td class=\"yes\">Yes</td><td>Supported</td></tr>" \
             "<tr><td class=\"unknown\">Unknown</td><td>No known profile</td></tr>" \
             "</table><p>If the border surrounding the nozzle list is either green or red the material is, " \
             "by default, supported or unsupported. But depending on the type of nozzle, this can change. " \
             "</br>Use a browser plug-in like 'TableTools2' to filter and/or search the table.</br>" \
             "Clicking on a material name will open the github page to the XML file.</br>" \
             "Hovering on the material name will show the material GUID in a tooltip</p>" \
             "{0}\r\n</body>"

    __table = "<table>\r\n{0}</table>"
    __table_row = "\t<tr>\r\n{0}\t</tr>\r\n"
    __table_data = "\t\t<td class='{1}'>{0}</td>\r\n"
    __table_data_header = "\t\t<td colspan=\"{0}\" class=\"hdr\">[&nbsp;{1}&nbsp;]</td>\r\n"
    __table_title_data = "\t\t<td class='{0}'>" \
                         "<a href=\"https://github.com/Ultimaker/fdm_materials/blob/master/{1}\" target=\"_new\">" \
                         "<abbr title=\"{2}\">{3}&nbsp;({4},&nbsp;&#8960;{5})</abbr></a></td>\r\n"

    __table_data_color = "\t\t<td class='{1}' style=\"background-color:{2}\">{0}</td>\r\n"

    def toHtml(self, materials, all_devices, all_nozzles, nozzle_lookup) -> str:
        sorted_materials = sorted(materials, key=lambda m: m.brand+m.material+m.color+m.diameter, reverse=True)
        sorted_dev = sorted(all_devices)
        sorted_nozzles = sorted(all_nozzles)

        # Build device header
        dev_header_row = self.__table_data.format(str(datetime.datetime.today()), "hdr")
        dev_header_row += self.__table_data.format("ver", "hdr sep")
        dev_header_row += self.__table_data.format("col", "hdr sep")

        for device in sorted_dev:
            dev_header_row += self.__table_data.format(device, "hdr sep")

        device_table = self.__table_row.format(dev_header_row)

        current_brand = ""

        # Build compatibility row per device
        for material in sorted_materials:

            # Insert Material brand header
            if current_brand != material.brand:
                current_brand = material.brand
                dev_td = self.__table_data_header.format(len(sorted_materials), material.brand)
                device_table += self.__table_row.format(dev_td)

            dev_td = self.__table_title_data.format(
                "lbl",
                material.filename,
                material.guid,
                material.material.replace(" ", "&nbsp;"),
                material.color,
                material.diameter
            )

            dev_td += self.__table_data.format(material.version, "lbl sep")
            dev_td += self.__table_data_color.format("", "unknown sep", material.color_code)

            dev_td += self.buildDeviceTable(material, sorted_dev, sorted_nozzles, nozzle_lookup)

            device_table += self.__table_row.format(dev_td)

        return self.__html.format(self.__table.format(device_table))

    def buildDeviceTable(self, material, sorted_dev, sorted_nozzles, nozzle_lookup) -> str:
        dev_td = ""

        for dev in sorted_dev:
            class_td = "unknown"
            nozzle_table = ""

            if dev in material.profiles:
                nozzle_table = self.buildNozzleTable(
                    material.profiles[dev].nozzles,
                    sorted_nozzles,
                    nozzle_lookup.get(dev)
                )
                class_td = material.profiles[dev].device.is_supported

            dev_td += self.__table_data.format(nozzle_table, "{0} sep".format(class_td))

        return dev_td

    def buildNozzleTable(self, nozzles, all_nozzles, nozzle_lookup):
        nozzle_td = ""
        nozzle_ref = nozzle_lookup if nozzle_lookup is not None else all_nozzles

        for nozzle in nozzle_ref:

            nozzle_name = nozzle.replace(" ", "&nbsp;")
            class_td = "unknown"

            if nozzle in nozzles:
                class_td = nozzles[nozzle].is_supported

            nozzle_td += self.__table_data.format(nozzle_name, class_td)

        return self.__table.format(self.__table_row.format(nozzle_td))
