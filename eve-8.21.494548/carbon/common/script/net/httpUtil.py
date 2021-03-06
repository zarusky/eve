#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/common/script/net/httpUtil.py
import blue
import json
import macho
import util
import bluepy

class ComplexEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, blue.MarshalStream):
            return macho.Loads(obj)
        if isinstance(obj, macho.MachoAddress) or isinstance(obj, macho.MachoPacket):
            return obj.__getstate__()
        if isinstance(obj, blue.DBRow):
            item = {}
            for key in obj.__columns__:
                item[key] = obj[key]

            return item
        if isinstance(obj, util.Rowset):
            return [ r for r in obj ]
        if isinstance(obj, util.Row):
            item = {}
            for key in obj.header:
                item[key] = obj[key]

            return item
        if isinstance(obj, util.SparseRowset):
            items = []
            for item in obj:
                items.append(self.default(item))

            return items
        if isinstance(obj, util.KeyVal):
            return obj.__dict__
        if isinstance(obj, UserError):
            return dict({'error': obj.msg}, **obj.dict)
        print obj, 'cannot be encoded and has', dir(obj)
        return json.JSONEncoder.default(self, obj)


@bluepy.TimedFunction('Crest::ToJSON')
def ToJSON(data, encoding = 'utf-8'):
    return json.dumps(data, encoding=encoding)


@bluepy.TimedFunction('Crest::ToComplexJSON')
def ToComplexJSON(data, encoding = 'utf-8'):
    return json.dumps(data, cls=ComplexEncoder, encoding=encoding)


exports = {'httpUtil.ToJSON': ToJSON,
 'httpUtil.ToComplexJSON': ToComplexJSON}