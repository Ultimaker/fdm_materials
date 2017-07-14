from supportEnum import Support


class NozzleSupport:
    """
    Combines support type with nozzle id.
    """

    def __init__(self):
        self.id = ""
        self.support = Support.UNKNOWN
