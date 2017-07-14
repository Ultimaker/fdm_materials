from supportEnum import Support


class DeviceSupport:
    """
    Combines support type with device name.
    """
    def __init__(self):
        self.name = ""
        self.support = Support.UNKNOWN
