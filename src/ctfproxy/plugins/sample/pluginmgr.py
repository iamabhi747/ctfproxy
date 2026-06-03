from ...util.pluginmgr import PluginType, PluginManager

class SamplePluginManager (PluginManager):
    NAME = "SamplePluginManager"
    SHORTNAME = "sample"
    TYPE = PluginType.CLIENT_HOST

    #
