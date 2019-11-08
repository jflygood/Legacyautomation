import xml.etree.ElementTree as ET
from os.path import isfile, join



class xmlParserFile():
    """
    xmlParserFile class provide a set of functions which can help to parse XML file.
    """
    __file__ = ""

    def __init__(self, f):
        self.__file__ = f

    def get_parameter_dic(self):
        tree = ET.parse(self.__file__)
        root = tree.getroot()
        # print root.tag
        # print root.attrib
        # for child in root:
        #     print "number=",child.tag, child.attrib
        # print child.attrib
        namevalue_dic= {}
        for parameter in root.iter('parameter'):
            # print "1111-----", parameter.attrib
            namevalue_dic[parameter.attrib['name']] = parameter.attrib['value']
        print "namevalue_dic-------", namevalue_dic
        return namevalue_dic

    def update_parameter_value(self,para_namevalue_pairdic,new_file):
        tree = ET.parse(self.__file__)
        root = tree.getroot()
        for parameter in root.iter('parameter'):
            # print "1111-----", parameter.attrib
            for key,value in para_namevalue_pairdic.iteritems():
                if parameter.attrib['name'] == key:
                    parameter.set('value', value)
        tree.write(new_file)


class FileOperations:
    def __init__(self, filepath, file, fileattr):
        self.filepath = filepath
        self.file = file
        self.fileattr = fileattr

    def open_file(self):
        filename = join(self.filepath, self.file)
        print "filename=",filename
        self.file1 = open(filename, self.fileattr)

    def deleteContent(self):
        self.file1.seek(0)
        self.file1.truncate()

    def write_to_files(self, output):
        self.file1.write(output)

    def close(self):
        self.file1.close()

    def readfile(self):
        # filename = join(self.filepath, self.file)
        try:
            self.open_file()
            # print "filename=",filename
            content = self.file1.read()
            self.close()
            content = content.decode("utf-8").strip()
            # print "content=", content
            # listline = content.split("\n")
            return content
        except Exception, e:
            print str(e)


    # def get_node_value(self, xpath):
    #     """
    #     Get XML node value by using XML path.
    #     @params:
    #         xpath  - Required  : XML path (str).
    #     """
    #     root = ET.parse(self.__file__).getroot()
    #     elem = root.find(xpath)
    #     if elem is not None:
    #         return elem.text
    #     # g_logger.error(ERR_GET_NODE_VALUE)
    #     raise XmlParserError("Get node value error!")
    #
    # def get_attr_value(self, xpath, attrib_name, subnode=None):
    #     """
    #     Get XML parent node attribute value by using XML path and attribute name.
    #     Use Case:
    #         using domain group name to get its UID.
    #     @params:
    #         xpath           - Required  : XML path (str).
    #         attrib_name     - Required  : attribute name (str).
    #         subnode         - Not required  : subnode info include its value, attribute name
    #                                         and attribute value (dict).
    #     """
    #     try:
    #         root = ET.parse(self.__file__).getroot()
    #         if subnode == None:
    #             node = root.find(xpath)
    #             if node != None:
    #                 return node.attrib[attrib_name]
    #             else:
    #                 raise XmlParserError("Get attribute value error!")
    #         else:
    #             for node in root.findall(xpath):
    #                 if node != None:
    #                     for child in node:
    #                         if child != None and child.text == subnode['value'] \
    #                                 and child.attrib[subnode['attrib_name']] == subnode['attrib_value']:
    #                             return node.attrib[attrib_name]
    #             raise XmlParserError("Get attribute value error!")
    #
    #     except KeyError as e:
    #         # g_logger.error(ERR_NO_ATTR + ': {}'.format(e.message))
    #         raise XmlParserError("No Attribute" + ': {}'.format(e.message))



# class XmlParserError(Exception):
    #     pass
# class xmlParserStr():
#     """
#     xmlParserStr class provide a set of functions which can help to parse XML string.
#     """
#     __str__ = ""
#
#     def __init__(self, s):
#         self.__str__ = s
#
#     def get_node_value(self, xpath):
#         """
#         Get XML node value by using XML path.
#         @params:
#             xpath  - Required  : XML path (str).
#         """
#         root = ET.fromstring(self.__str__)
#         elem = root.find(xpath)
#         if elem is not None and bool(elem.text):
#             return elem.text
#         # g_logger.error(ERR_GET_NODE_VALUE)
#         raise XmlParserError("Get node value error!")
