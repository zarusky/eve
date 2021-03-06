#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\carbon\staticData\schema\loaders\dictLoader.py
import ctypes
import collections
from carbon.telemetryMarkup import TelemetryContext

def BinarySearch(key, headerDataList):
    minIndex = 0
    maxIndex = len(headerDataList) - 1
    while 1:
        if maxIndex < minIndex:
            return None
        meanIndex = (minIndex + maxIndex) / 2
        headerDataIndex = headerDataList[meanIndex]
        if headerDataIndex['key'] < key:
            minIndex = meanIndex + 1
        elif headerDataIndex['key'] > key:
            maxIndex = meanIndex - 1
        else:
            return headerDataIndex


class DictLoader(object):

    def __init__(self, data, offset, schema, extraState):
        self.data = data
        self.offset = offset
        self.schema = schema
        self.offsetToData = ctypes.cast(ctypes.byref(data, offset), ctypes.POINTER(ctypes.c_uint32)).contents.value
        self.__extraState__ = extraState
        self.index = {}
        ListFromBinaryString = self.__extraState__.factories['list']
        self.headerData = ListFromBinaryString(data, offset + 4, self.schema['keyHeader'], self.__extraState__)

    def __getitem__(self, key):
        self._Search(key)
        if self.__extraState__.cfgObject is not None:
            cfgObject = self.__extraState__.cfgObject.GetIfExists(key)
            newState = self.__extraState__.CreateNewStateWithCfgObject(cfgObject)
            if self.index[key] != None:
                return newState.RepresentSchemaNode(self.data, self.offset + 4 + self.offsetToData + self.index[key], self.schema['valueTypes'])
            if cfgObject is None:
                raise IndexError('key is not in BSD or FSD table - %s' % str(key))
            else:
                return cfgObject
        else:
            if self.index[key] == None:
                raise IndexError('key is not in BSD or FSD table - %s' % str(key))
            return self.__extraState__.RepresentSchemaNode(self.data, self.offset + 4 + self.offsetToData + self.index[key], self.schema['valueTypes'])

    def __len__(self):
        return len(self.headerData)

    def __contains__(self, item):
        return self._Search(item) != None

    def _Search(self, key):
        if key not in self.index:
            with TelemetryContext('FSD.DictLoader.BinarySearch'):
                searchResult = BinarySearch(key, self.headerData)
            if searchResult != None:
                self.index[key] = searchResult['offset']
            else:
                self.index[key] = None
        return self.index[key]

    def Get(self, key):
        return self.__getitem__(key)

    def get(self, key, default):
        self._Search(key)
        if self.index[key] is not None:
            return self.__getitem__(key)
        else:
            return default

    def GetIfExists(self, key):
        return self.get(key, None)


class IndexLoader(object):

    def __init__(self, fileObject, cacheSize, schema, extraState, offset = 0):
        self.fileObject = fileObject
        self.cacheSize = cacheSize
        self.schema = schema
        self.offset = offset
        self.__extraState__ = extraState
        self.index = {}
        fileObject.seek(offset)
        headerSize = fileObject.read(4)
        headerSize = ctypes.create_string_buffer(headerSize, len(headerSize))
        self.headerDataSize = ctypes.cast(ctypes.byref(headerSize, 0), ctypes.POINTER(ctypes.c_uint32)).contents.value
        dictHeader = fileObject.read(self.headerDataSize)
        dictHeader = ctypes.create_string_buffer(dictHeader, self.headerDataSize)
        ListFromBinaryString = extraState.factories['list']
        self.headerData = ListFromBinaryString(dictHeader, 0, self.schema['keyHeader'], extraState)
        self.cache = collections.OrderedDict()

    def itervalues(self):
        return iter([ self.Get(each['key']) for each in iter(self.headerData) ])

    def iterkeys(self):
        return iter([ each['key'] for each in iter(self.headerData) ])

    def iteritems(self):
        return iter([ (each['key'], self.Get(each['key'])) for each in iter(self.headerData) ])

    def __iter__(self):
        for i in xrange(len(self.headerData)):
            key = self.headerData[i]['key']
            yield key

    def _Search(self, key):
        if key not in self.index:
            searchResult = BinarySearch(key, self.headerData)
            if searchResult != None:
                self.index[key] = (searchResult['offset'], searchResult['size'])
            else:
                self.index[key] = None
        return self.index[key]

    def __getitem__(self, key):
        if key in self.cache:
            v = self.cache[key]
            del self.cache[key]
            self.cache[key] = v
            if isinstance(v, IndexLoader):
                return v
            return self.__extraState__.RepresentSchemaNode(v, 0, self.schema['valueTypes'])
        isSubObjectAnIndex = self.schema['valueTypes'].get('buildIndex', False) and self.schema['valueTypes']['type'] == 'dict'
        with TelemetryContext('FSD.IndexLoader.BinarySearch'):
            dataInfo = self._Search(key)
        if dataInfo == None:
            raise KeyError('key ' + str(key) + ' not found')
        newOffset = self.offset + 4 + self.headerDataSize + dataInfo[0]
        if isSubObjectAnIndex:
            self.cache[key] = IndexLoader(self.fileObject, self.cacheSize, self.schema['valueTypes'], self.__extraState__, offset=newOffset)
            return self.cache[key]
        self.fileObject.seek(newOffset)
        itemData = self.fileObject.read(dataInfo[1])
        dataAsBuffer = ctypes.create_string_buffer(itemData, len(itemData))
        self.cache[key] = dataAsBuffer
        if len(self.cache) > self.cacheSize:
            self.cache.popitem(last=False)
        if self.__extraState__.cfgObject is not None:
            newState = self.__extraState__.CreateNewStateWithCfgObject(self.__extraState__.cfgObject.GetIfExists(key))
            newState.RepresentSchemaNode(dataAsBuffer, 0, self.schema['valueTypes'])
        else:
            return self.__extraState__.RepresentSchemaNode(dataAsBuffer, 0, self.schema['valueTypes'])

    def __contains__(self, item):
        return self._Search(item) != None

    def __len__(self):
        return len(self.headerData)

    def Get(self, key):
        return self.__getitem__(key)

    def GetIfExists(self, key):
        return self.get(key, None)

    def get(self, key, default):
        self._Search(key)
        if self.index[key] is not None:
            return self.__getitem__(key)
        else:
            return default