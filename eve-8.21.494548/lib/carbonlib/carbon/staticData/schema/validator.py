#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\carbon\staticData\schema\validator.py
import re
import collections
import os
import yaml
try:
    import pyodbc
    dbConnectionForValidationAvailable = True
    dbConnections = {}
except ImportError:
    dbConnectionForValidationAvailable = False

CLIENT = 'Client'
SERVER = 'Server'
EDITOR = 'Editor'
ASCENDING = 'Ascending'
DESCENDING = 'Descending'
import persistence

class SchemaMismatch(object):

    def __init__(self, path, message):
        self.path = path
        self.message = message

    def __str__(self):
        return self.message


class SchemaTypeError(SchemaMismatch):
    pass


class SchemaComparisonError(SchemaMismatch):
    pass


class SchemaObjectAttributeMissingError(SchemaMismatch):
    pass


class SchemaObjectAttributeNotInSchemaError(SchemaMismatch):
    pass


class ExternalReferenceError(SchemaMismatch):
    pass


class SchemaError(Exception):

    def __init__(self, path, message, node, data):
        self.path = path
        self.message = message
        self.node = node
        self.data = data

    def __str__(self):
        return self.message


def ListContainsType(errorList, errorType):
    match = [ e for e in errorList if isinstance(e, errorType) ]
    return len(match) > 0


def AllFloatValues(i):
    return all(map(lambda x: type(x) in (float, int, long), i))


def ValidateInt(schemaNode, o, path = 'root', state = {}):
    if type(o) not in (int, long):
        return [SchemaTypeError(path, '%s: Type Mismatch - should be an integer: %s' % (path, str(o)))]
    errors = []
    if 'min' in schemaNode:
        if o < schemaNode['min']:
            errors.append(SchemaComparisonError(path, '%s: Range mismatch - value %i is less than the minimum value of %i' % (path, o, schemaNode['min'])))
    elif 'exclusiveMin' in schemaNode:
        if o <= schemaNode['exclusiveMin']:
            errors.append(SchemaComparisonError(path, '%s: Range mismatch - value %i is less than or equal to the minimum value of %i' % (path, o, schemaNode['exclusiveMin'])))
    if 'max' in schemaNode:
        if o > schemaNode['max']:
            errors.append(SchemaComparisonError(path, '%s: Range mismatch - value %i is less than the maximum value of %i' % (path, o, schemaNode['max'])))
    elif 'exclusiveMax' in schemaNode:
        if o >= schemaNode['exclusiveMax']:
            errors.append(SchemaComparisonError(path, '%s: Range mismatch - value %i is less than or equal to the maximum value of %i' % (path, o, schemaNode['exclusiveMax'])))
    return errors


def ValidateTypeID(schemaNode, o, path = 'root', state = {}):
    errors = ValidateInt(schemaNode, o, path, state)
    if not ListContainsType(errors, SchemaTypeError) and o < 0:
        errors.append(SchemaComparisonError(path, '%s: Range Mismatch - typeIDs should be > 0, this is %i' % (path, o)))
    return errors


def ValidateFloat(schemaNode, o, path = 'root', state = {}):
    errors = []
    if type(o) is not float:
        return [SchemaTypeError(path, '%s: Type Mismatch - should be a float' % path)]
    if 'min' in schemaNode:
        if o < schemaNode['min']:
            errors.append(SchemaComparisonError(path, '%s: Range mismatch - value %.1g is less than the minimum value of %.1g' % (path, o, schemaNode['min'])))
    elif 'exclusiveMin' in schemaNode:
        if o <= schemaNode['exclusiveMin']:
            errors.append(SchemaComparisonError(path, '%s: Range mismatch - value %.1g is less than or equal to the minimum value of %.1g' % (path, o, schemaNode['exclusiveMin'])))
    if 'max' in schemaNode:
        if o > schemaNode['max']:
            errors.append(SchemaComparisonError(path, '%s: Range mismatch - value %.1g is less than the maximum value of %.1g' % (path, o, schemaNode['max'])))
    elif 'exclusiveMax' in schemaNode:
        if o >= schemaNode['exclusiveMax']:
            errors.append(SchemaComparisonError(path, '%s: Range mismatch - value %.1g is less than or equal to the maximum value of %.1g' % (path, o, schemaNode['exclusiveMax'])))
    return errors


def ValidateBool(schemaNode, o, path = 'root', state = {}):
    errors = []
    if type(o) is not bool:
        errors.append(SchemaTypeError(path, '%s: Type Mismatch - should be a bool' % path))
    return errors


def ValidateString(schemaNode, o, path = 'root', state = {}):
    if type(o) is not str:
        return [SchemaTypeError(path, '%s: Type Mismatch - should be a string' % path)]
    errors = []
    if 'length' in schemaNode:
        if len(o) != schemaNode['length']:
            errors.append(SchemaComparisonError(path, "%s: Length mismatch - string '%s' should be %i characters long" % (path, o, schemaNode['length'])))
    if 'minLength' in schemaNode:
        if len(o) < schemaNode['minLength']:
            errors.append(SchemaComparisonError(path, "%s: Length mismatch - string '%s' should be at least %i characters long" % (path, o, schemaNode['minLength'])))
    if 'maxLength' in schemaNode:
        if len(o) > schemaNode['maxLength']:
            errors.append(SchemaComparisonError(path, "%s: Length mismatch - string '%s' should be at most %i characters long" % (path, o, schemaNode['maxLength'])))
    if 'regex' in schemaNode:
        if not re.match(schemaNode['regex'], o):
            errors.append(SchemaComparisonError(path, '%s: Regex mismatch - string \'%s\' does not match the regex "%s"' % (path, o, schemaNode['regex'])))
    return errors


def ValidateResPath(schemaNode, o, path = 'root', state = {}):
    errors = ValidateString(schemaNode, o, path, state)
    if not ListContainsType(errors, SchemaTypeError):
        if not o.startswith('res:/'):
            errors.append(SchemaComparisonError(path, "%s: Type Mismatch - resPaths should start with 'res:/' - %s" % (path, o)))
        if 'extensions' in schemaNode:
            fileName, fileExtension = os.path.splitext(o)
            fileExtension = fileExtension[1:]
            if fileExtension not in schemaNode['extensions']:
                supportedExtension = ', '.join([ "'%s'" % extension for extension in schemaNode['extensions'] ])
                errors.append(SchemaComparisonError(path, '%s: Type Mismatch - this resPath supports the following extensions: %s - %s' % (path, supportedExtension, o)))
        if ' ' in o:
            errors.append(SchemaComparisonError(path, '%s: Type Mismatch - resPaths should not contain spaces - %s' % (path, o)))
        if '\\' in o:
            errors.append(SchemaComparisonError(path, '%s: Type Mismatch - resPaths should not contain backslashes - %s' % (path, o)))
    return errors


def ValidateVector2(schemaNode, o, path = 'root', state = {}):
    if type(o) not in (tuple, list):
        return [SchemaTypeError(path, '%s: Type Mismatch - should be a vector2' % path)]
    errors = []
    if len(o) != 2:
        errors.append(SchemaComparisonError(path, '%s: Length Mismatch - should be a vector2' % path))
    if not AllFloatValues(o):
        errors.append(SchemaComparisonError(path, '%s: Type Mismatch - should be a vector2 (contents are not all numeric!)' % path))
    return errors


def ValidateVector3(schemaNode, o, path = 'root', state = {}):
    if type(o) not in (tuple, list):
        return [SchemaTypeError(path, '%s: Type Mismatch - should be a vector3' % path)]
    errors = []
    if len(o) != 3:
        errors.append(SchemaComparisonError(path, '%s: Length Mismatch - should be a vector3' % path))
    if not AllFloatValues(o):
        errors.append(SchemaComparisonError(path, '%s: Type Mismatch - should be a vector3 (contents are not all numeric!)' % path))
    return errors


def ValidateVector4(schemaNode, o, path = 'root', state = {}):
    if type(o) not in (tuple, list):
        return [SchemaTypeError(path, '%s: Type Mismatch - should be a vector4' % path)]
    errors = []
    if len(o) != 4:
        errors.append(SchemaComparisonError(path, '%s: Length Mismatch - should be a vector4' % path))
    if not AllFloatValues(o):
        errors.append(SchemaComparisonError(path, '%s: Type Mismatch - should be a vector4 (contents are not all numeric!)' % path))
    return errors


def ValidateObject(schemaNode, o, path = 'root', state = {}):
    errors = []
    if type(o) is not dict:
        return [SchemaTypeError(path, '%s: Type Mismatch - should be an object' % path)]
    for attrName, attrValue in schemaNode.get('attributes').iteritems():
        if not attrValue.get('isOptional', False) and attrName not in o:
            errors.append(SchemaObjectAttributeMissingError(path, "%s: Attribute Mismatch - required attribute '%s' is missing!" % (path, attrName)))
        if attrName in o:
            errors.extend(Validate(attrValue, o[attrName], path + '.%s' % attrName, state))

    for attrName in o:
        if attrName not in schemaNode.get('attributes'):
            errors.append(SchemaObjectAttributeNotInSchemaError(path, "%s: Attribute Mismatch - attribute '%s' does not exist in the schema!" % (path, attrName)))

    return errors


def ValidateList(schemaNode, o, path = 'root', state = {}):
    try:
        it = enumerate(o)
    except TypeError:
        return [SchemaTypeError(path, '%s: Type Mismatch - should be itterable' % path)]

    sortKey = schemaNode.get('sortKey', None)
    sortOrder = schemaNode.get('sortOrder', ASCENDING)
    originalLast = object()
    last = originalLast
    errors = []
    listOutOfOrder = False
    for index, i in it:
        if last is not originalLast:
            compare1 = last
            compare2 = i
            if sortKey is not None:
                if not hasattr(last, sortKey):
                    return [SchemaObjectAttributeMissingError(path + '[%i]' % (index - 1), "%s: Sort Attribute Missing - required attribute '%s' is missing!" % (path + '[%i]' % (index - 1), sortKey))]
                if not hasattr(i, sortKey):
                    return [SchemaObjectAttributeMissingError(path + '[%i]' % index, "%s: Sort Attribute Missing - required attribute '%s' is missing!" % (path + '[%i]' % index, sortKey))]
                compare1 = getattr(last, sortKey)
                compare2 = getattr(i, sortKey)
            if sortOrder == ASCENDING and not listOutOfOrder:
                if compare1 >= compare2:
                    errors.append(SchemaComparisonError(path + '[%i]' % index, '%s: Order Error! Sort key: %s. List should be sorted ASCENDING. %s >= %s!' % (path + '[%i]' % index,
                     sortKey,
                     str(compare1),
                     str(compare2))))
                    listOutOfOrder = True
            elif sortOrder == DESCENDING and not listOutOfOrder:
                if compare1 <= compare2:
                    errors.append(SchemaComparisonError(path + '[%i]' % index, '%s: Order Error! Sort key: %s. List should be sorted DESCENDING. %s <= %s!' % (path + '[%i]' % index,
                     sortKey,
                     str(compare1),
                     str(compare2))))
                    listOutOfOrder = True
        errors.extend(Validate(schemaNode.get('itemTypes'), i, path + '[%i]' % index, state))
        last = i

    return errors


def ValidateDict(schemaNode, o, path = 'root', state = {}):
    if type(o) not in (dict, collections.OrderedDict):
        return [SchemaTypeError(path, '%s: Type Mismatch - should be itterable' % path)]
    errors = []
    for dictKey, dictValue in o.iteritems():
        errors.extend(Validate(schemaNode['keyTypes'], dictKey, path + '<%s>' % str(dictKey), state))
        errors.extend(Validate(schemaNode['valueTypes'], dictValue, path + '[%s]' % str(dictKey), state))

    return errors


def ValidateEnum(schemaNode, o, path = 'root', state = {}):
    if o not in schemaNode.get('values', {}):
        return [SchemaTypeError(path, '%s: Enum value not found in schema: %s' % (path, repr(o)))]
    return []


def ValidateUnion(schemaNode, o, path = 'root', state = {}):
    for s in schemaNode['optionTypes']:
        validationErrors = Validate(s, o, path, state)
        if len(validationErrors) == 0:
            break
    else:
        return [SchemaTypeError(path, '%s: Did not match any of the possible schema types: %s' % (path, repr(o)))]

    return []


builtInValdationFunctions = {'int': ValidateInt,
 'typeID': ValidateTypeID,
 'float': ValidateFloat,
 'vector2': ValidateVector2,
 'vector3': ValidateVector3,
 'vector4': ValidateVector4,
 'dict': ValidateDict,
 'list': ValidateList,
 'object': ValidateObject,
 'enum': ValidateEnum,
 'string': ValidateString,
 'resPath': ValidateResPath,
 'bool': ValidateBool,
 'union': ValidateUnion}

def ValidateReference(schemaNode, o, path, state):
    referenceInfo = schemaNode.get('reference')
    if not state.get('validateReferences', False):
        return []
    if 'database' in referenceInfo and dbConnectionForValidationAvailable:
        serverDB = (referenceInfo['server'], referenceInfo['database'])
        if serverDB in dbConnections:
            connection, cursor = dbConnections[serverDB]
        else:
            try:
                connection = pyodbc.connect('DRIVER={SQL Server};SERVER=%s;DATABASE=%s;Trusted_Connection=yes' % serverDB)
                cursor = connection.cursor()
                dbConnections[serverDB] = (connection, cursor)
            except pyodbc.Error:
                print 'ERROR: Could not connect to server %s and database %s to validate external reference' % serverDB
                connection = None
                cursor = None
                dbConnections[serverDB] = (None, None)
                return []

        if connection is None:
            return []
        rows = cursor.execute('SELECT * from %(table)s WHERE %(key)s = ?' % referenceInfo, o)
        if rows.fetchone() is None:
            errorString = '%(path)s: ' + referenceInfo['errorMessage']
            return [ExternalReferenceError(path, errorString % {'path': path,
              'key': str(o),
              'server': referenceInfo['server'],
              'database': referenceInfo['database'],
              'table': referenceInfo['table']})]
    elif 'schema' in referenceInfo and 'branchRoot' in state:
        if 'openSchemas' not in state:
            state['openSchemas'] = {}
            state['openData'] = {}
        otherSchemaPath = os.path.abspath(os.path.join(state['branchRoot'], referenceInfo['schema']))
        if 'schemaCache' in state and otherSchemaPath in state['schemaCache']:
            otherSchema = state['schemaCache'].Get(otherSchemaPath)
        elif otherSchemaPath not in state['openSchemas']:
            with open(otherSchemaPath, 'r') as otherSchemaFile:
                otherSchema = state['openSchemas'][otherSchemaPath] = persistence.LoadSchema(otherSchemaFile)
        else:
            otherSchema = state['openSchemas'][otherSchemaPath]
        editorSchema = persistence.GetEditorSchema(otherSchema)
        editorFile = otherSchema['editorFile'] % {'key': o}
        fullEditorFilePath = os.path.abspath(os.path.join(state['branchRoot'], editorFile))
        if 'dataCache' in state and fullEditorFilePath in state['dataCache']:
            otherData = state['dataCache'].Get(fullEditorFilePath)
        elif fullEditorFilePath not in state['openData']:
            with open(fullEditorFilePath, 'r') as otherDataFile:
                otherData = state['openData'][fullEditorFilePath] = yaml.load(otherDataFile)
        else:
            otherData = state['openData'][fullEditorFilePath]
        if o not in otherData:
            errorString = '%(path)s: ' + referenceInfo['errorMessage']
            return [ExternalReferenceError(path, errorString % {'path': path,
              'key': str(o),
              'dataFile': fullEditorFilePath})]
    return []


def Validate(schemaNode, o, path = 'root', state = {}):
    nodeType = schemaNode.get('type', None)
    if nodeType is None:
        return [SchemaError(path, "%s: Could not find a 'type' for the schema node" % path, schemaNode, o)]
    errors = []
    if 'reference' in schemaNode:
        errors.extend(ValidateReference(schemaNode, o, path, state))
    if nodeType in state.get('overrides', {}):
        errors.extend(state.get('overrides', {})[nodeType](schemaNode, o, path, state))
    if nodeType in builtInValdationFunctions:
        errors.extend(builtInValdationFunctions[nodeType](schemaNode, o, path, state))
    else:
        return [SchemaError(path, "%s: Could not find a known 'type' for the schema node: %s" % (path, nodeType), schemaNode, o)]
    return errors


def ValidateWithExceptions(schemaNode, o, path = 'root', state = {}):
    errors = Validate(schemaNode, o, path='root', state={})
    if len(errors):
        raise Exception(str(errors[0]))