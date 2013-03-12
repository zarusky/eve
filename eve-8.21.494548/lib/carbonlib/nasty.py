#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\nasty.py
import blue
import log
import sys
import bluepy
import telemetry
from log import LGINFO, LGNOTICE, LGWARN, LGERR
pyver = sys.version[:3]
pyver = pyver[0] + pyver[-1]
if pyver not in ['25', '27']:
    pyver = '27'
try:
    sys.mallocmode(prefs.GetValue('mallocmode', 0))
except AttributeError:
    pass

import types
import blue.crypto
import blue.win32
from stackless import getcurrent
import weakref
import traceback
import re
import cStringIO as StringIO
import zlib
import gc
import base64
import os
import os.path
import util
import thinmock
import inspect
import cPickle
import marshal
import imp
import __builtin__
import const
__builtin__.const = const
try:
    import appConst
    for name, value in appConst.__dict__.iteritems():
        if not name.startswith('__'):
            if name not in __builtin__.const.__dict__:
                __builtin__.const.__dict__[name] = value
            elif inspect.ismodule(value):
                for moduleKey, moduleValue in value.__dict__.iteritems():
                    if not moduleKey.startswith('__'):
                        setattr(__builtin__.const.__dict__[name], moduleKey, moduleValue)

except ImportError:
    log.LogException('appConst module is broken, fix it')

ALLOWED_CODEFILES = ['compiled']

class NamespaceCollisionError(Exception):
    __guid__ = 'exceptions.NameSpaceCollisionError'

    def __repr__(self):
        return 'NameSpaceCollisionError: The additional namespace %s collided with a preexisting varible in the namespace %s.' % (self.args[0], self.args[1])


NamespaceCollisionError.__module__ = 'exceptions'

class NamespaceFailedException(ImportError):
    __guid__ = 'exceptions.NamespaceFailed'

    def __init__(self, *args):
        ImportError.__init__(self, *args)

    def __repr__(self):
        return 'NamespaceFailed: The namespace ' + self.args[0] + ' was not found.'


NamespaceFailedException.__module__ = 'exceptions'

class NamespaceAttributeFailedException(NamespaceFailedException):
    __guid__ = 'exceptions.NamespaceAttributeFailed'
    __persistvars__ = ['args']

    def __repr__(self):
        return 'NamespaceAttributeFailed: The namespace member ' + self.args[0] + '.' + self.args[1] + ' was not found.'


NamespaceAttributeFailedException.__module__ = 'exceptions'

class Namespace(object):

    def __init__(self, name, space):
        self.__dict__['name'] = name
        self.__dict__['space'] = space

    def __getattr__(self, attr):
        if self.space.has_key(attr):
            return self.space[attr]
        raise AttributeError, (attr, self.space)

    def __setattr__(self, attr):
        raise NamespaceAttributeFailedException, (self.name, str(attr))


mainLocalStorage = {}

def GetLocalStorage():
    global mainLocalStorage
    return getattr(getcurrent(), 'localStorage', mainLocalStorage)


def GetOtherLocalStorage(t):
    return getattr(t, 'localStorage', mainLocalStorage)


def SetLocalStorage(s):
    global mainLocalStorage
    try:
        getcurrent().localStorage = s
    except AttributeError:
        mainLocalStorage = s


def UpdateLocalStorage(props):
    try:
        ls = getcurrent().localStorage
    except AttributeError:
        ls = mainLocalStorage

    ret = dict(ls)
    ls.update(props)
    return ret


class UpdatedLocalStorage(object):

    def __init__(self, updatedDict):
        self.__store = updatedDict

    def __enter__(self):
        self.__store = UpdateLocalStorage(self.__store)

    def __exit__(self, e, v, tb):
        SetLocalStorage(self.__store)


class Sissy():

    def __init__(self, what):
        self.__dict__['__sissywhat__'] = what

    def _Obj(self):
        try:
            obj = GetLocalStorage()[self.__sissywhat__]
            if type(obj) is weakref.ref:
                obj = obj()
            return obj
        except (KeyError, ReferenceError):
            return None

    def __nonzero__(self):
        return bool(self._Obj())

    def __repr__(self):
        return '<Sissy: ' + repr(self._Obj()) + ' >'

    def __getattr__(self, k):
        try:
            obj = GetLocalStorage()[self.__sissywhat__]
            if type(obj) is weakref.ref:
                obj = obj()
        except (KeyError, ReferenceError):
            obj = None

        return getattr(obj, k)

    def __setattr__(self, k, v):
        return setattr(self._Obj(), k, v)


def JumbleString(s, zip = False):
    if zip:
        s = zlib.compress(s)
    k = blue.crypto.GetVerCryptKey()
    return blue.crypto.CryptEncrypt(k, None, True, 0, s)


def UnjumbleString(s, zip = False):
    k = blue.crypto.GetVerCryptKey()
    s = blue.crypto.CryptDecrypt(k, None, True, 0, s)
    if zip:
        s = zlib.decompress(s)
    return s


class Compilor(object):

    def __init__(self, files = None):
        self.code = {}
        self.mls = None
        self.cargo = {}
        self.preprocessed = False
        if files:
            self.Compile(files)
        self.modTime = None
        self.compiles = {}
        self.lastSaveTime = None
        self.mockedModules = []

    def ProcessMocks(self):
        for module in self.mockedModules:
            fakeModule = thinmock.ThinMock(module)
            fakeModule.__all__ = []
            sys.modules[module] = fakeModule

        quantity = 'module' if len(self.mockedModules) == 1 else 'modules'
        log.general.Log('Inserting fake {modules} {quantity} into sys.modules'.format(modules=', '.join(self.mockedModules), quantity=quantity), LGNOTICE)

    @telemetry.ZONE_METHOD
    def Load(self, filename):
        filename = blue.paths.ResolvePath(filename)
        try:
            fileData, fileInfo = blue.win32.AtomicFileRead(filename)
        except:
            raise IOError, (None, "couldn't AtomicRead file", filename)

        self.modTime = fileInfo['ftLastWriteTime']
        datain = cPickle.loads(fileData)
        try:
            if datain[0] != sys.getmagic():
                print "Magic in code file doesn't match sys.magic() (%s vs %s)" % (datain[0], sys.getmagic())
                return
            all = cPickle.loads(datain[1])
            code = all['code']
            cargoIn = all['cargo']
            self.preprocessed = all['preprocessed']
            self.lastSaveTime = all['timestamp']
            signature = datain[2]
        except:
            raise IOError, (None, 'compiled.code of old format')

        args = blue.pyos.GetArg()
        if blue.pyos.packaged or '/VerifyCodeSignature' in args:
            if signature == None:
                raise SystemExit, 'Signature not present'
                blue.os.Terminate()
            signatureValid = self.VerifyDataSignature(datain[1], signature)
            if not signatureValid:
                if filename != blue.paths.ResolvePath('script:\\compiled.code'):
                    os.rename(filename, '%s.badsig' % filename)
                raise SystemExit, 'Signature check failed'
                blue.os.Terminate()
        for k, v in code:
            c = v[0]
            c = UnjumbleString(c, True)
            c = marshal.loads(c)
            val = [c] + list(v[1:])
            self.code[k] = val

        cargo = {}
        for k, v in cargoIn.iteritems():
            v = UnjumbleString(v, True)
            cargo[k] = v

        self.cargo = cargo

    @telemetry.ZONE_METHOD
    def VerifyDataSignature(self, data, signature):
        ctx = blue.crypto.GetVerContext()
        hash = blue.crypto.CryptCreateHash(ctx, blue.crypto.CALG_SHA, None, 0)
        blue.crypto.CryptHashData(hash, data)
        pKey = blue.crypto.GetVerKey()
        valid = blue.crypto.CryptVerifySignature(hash, signature, pKey)
        hash.Destroy()
        return valid

    @telemetry.ZONE_METHOD
    def Save(self, filename, codefile, skipFiles = []):
        filename = blue.paths.ResolvePathForWriting(filename)
        dataout = []
        for k, v in self.code.iteritems():
            if k not in skipFiles:
                if k[1] == codefile:
                    code = marshal.dumps(v[0])
                    code = JumbleString(code, True)
                    dataout.append((k, (code, v[1])))

        cargo = {}
        for k, v in self.cargo.iteritems():
            if k not in skipFiles:
                v = JumbleString(v, True)
                cargo[k] = v

        timeStamp = blue.os.GetWallclockTime()
        all = {'code': dataout,
         'cargo': cargo,
         'preprocessed': self.preprocessed,
         'timestamp': timeStamp}
        all = cPickle.dumps(all, -1)
        signature = None
        args = blue.pyos.GetArg()
        if '/signCode' in args:
            if '/sign' in args:
                ix = args.index('/sign') + 1
                pw = None
                if ix <= len(args):
                    pw = args[ix]
                    pw = pw.encode('cp1252')
            else:
                import nt
                pw = nt.environ.get('signaturepwd', '').strip('"')
            import lowdown
            signature = lowdown.SignData(all, password=pw)
            print ('Compiled.Code Signed: ', signature)
        dataout = (sys.getmagic(), all, signature)
        blue.win32.AtomicFileWrite(filename, cPickle.dumps(dataout, -1))

    def Flush(self):
        self.code.clear()
        self.compiles.clear()
        self.cargo.clear()

    def DiscardCode(self, files = None):
        if not files:
            files = self.code.iterkeys()
        for f in files:
            v = self.code[f]
            v[0] = hash(v[0])

    def Delete(self, files):
        for f in files:
            del self.code[f]

    def GetFiles(self):
        return self.code.keys()

    def GetCode(self, filename):
        v = self.code[filename]
        if type(v[0]) is not types.CodeType:
            self.Compile([filename])
        return v[0]

    def HasCargo(self, filename):
        return self.cargo.has_key(self._CargoName(filename))

    def GetCargo(self, filename):
        return self.cargo[self._CargoName(filename)]

    def GetCargoFile(self, filename, mode = 'b'):
        f = self.cargo.get(self._CargoName(filename), None)
        if f is not None:
            if 'b' not in mode:
                f = f.replace('\r\n', '\n')
            f = StringIO.StringIO(f)
        return f

    def AddCargo(self, filename, data):
        self.cargo[self._CargoName(filename)] = data

    def RemoveCargo(self, filename = None):
        if filename in self.cargo:
            del self.cargo[filename]
        elif filename is None:
            self.cargo.clear()

    def _CargoName(self, name):
        n = name.lower().replace('\\', '/')
        while '//' in n:
            n = n.replace('//', '/')

        return n

    def GetAttr(self, filename):
        return self.code[filename][1]

    def GetHash(self, filename):
        return hash(self.code[filename][0])

    def SetAttr(self, filename, attr):
        self.code[filename][1] = attr

    @telemetry.ZONE_METHOD
    def Compile(self, files = None):
        if files is None:
            files = self.code.iterkeys()
        errors = []
        for f in files:
            code, err = self.Compile_int(f)
            errors = errors + err
            if f in self.code:
                self.code[f][0] = code
            else:
                self.code[f] = [code, None]

        if errors:
            errors.sort()
            for e in errors:
                log.general.Log(e, LGERR)

            raise SyntaxError, 'compilation failure'

    def Compile_int(self, pathname):
        file = blue.classes.CreateInstance('blue.ResFile')
        file.OpenAlways(pathname[0])
        source = str(file.Read()).replace('\r\n', '\n') + '\n'
        del file
        filename = blue.paths.ResolvePath(pathname[0])
        errLog = []
        if boot.role != 'client' and '/noConstParsing' not in blue.pyos.GetArg():
            self.preprocessed = True
            try:
                source, errLog = self.PreprocessPythonCode(source, filename)
            except:
                print 'ERROR IN:', filename
                raise 

        print 'compiling %r' % filename
        try:
            code = compile(source, filename.encode('utf8'), 'exec')
            self.compiles[pathname[0]] = None
            return (code, errLog)
        except Exception as e:
            log.general.Log('Compile failed on %r: %s' % (filename, e), LGERR)
            print 'Compile failed on %r: %s' % (pathname[0], e)
            raise 

    def LineGenerator(self, text):
        lines = text.split('\n')
        if lines:
            for line in lines[:-1]:
                yield line + '\n'

            yield lines[-1]
        yield ''

    @telemetry.ZONE_METHOD
    def PreprocessPythonCode(self, codeText, filename):
        from tokenize import generate_tokens, untokenize
        print '    Preprocessing..',
        tokens = generate_tokens(self.LineGenerator(codeText).next)
        errLog = []
        replacedConst = [0, errLog]
        tokens = self.ReplaceConsts(replacedConst, tokens, filename)
        tokens = list(tokens)
        if replacedConst[0] == 0:
            print ' skipping file - nothing to replace'
            return (codeText, errLog)
        print ' replaced %d constants' % replacedConst[0]
        return (untokenize(tokens), errLog)

    def ReplaceConstsRecurseHelper(self, tokens, currentModule):
        dot = tokens.next()
        tok = tokens.next()
        if dot[1] == '.' and tok[1] != '__dict__':
            if tok[1] in currentModule.__dict__:
                nextValue = currentModule.__dict__[tok[1]]
                nextValueType = type(nextValue)
                if nextValueType == types.ModuleType:
                    errorInfo, constValue, tokenEnd = self.ReplaceConstsRecurseHelper(tokens, nextValue)
                    if not errorInfo:
                        return (errorInfo, constValue, tokenEnd)
                    else:
                        return (('in %s: %s' % (tok[1], errorInfo[0]), errorInfo[1] + [tok, dot]), None, 0)
                elif nextValueType in [int,
                 float,
                 long,
                 str,
                 unicode,
                 bool]:
                    return (None, (nextValueType, nextValue), tok[3])
                else:
                    return (('%s is unrecognized type %s' % (tok[1], nextValueType), [tok, dot]), None, 0)

            else:
                return (('%s not found' % tok[1], [tok, dot]), None, 0)
        else:
            return (('Either not a dot or accessing __dict__ directly', [tok, dot]), None, 0)

    def ReplaceConsts(self, count, tokens, filename):
        from tokenize import NAME, NUMBER, STRING
        for token in tokens:
            toktype, string, begin, end, linetext = token
            if toktype == NAME and string == 'const':
                errorInfo, constValue, tokenEnd = self.ReplaceConstsRecurseHelper(tokens, const)
                if not errorInfo:
                    typeToTokenMap = {int: NUMBER,
                     float: NUMBER,
                     long: NUMBER,
                     str: STRING,
                     unicode: STRING,
                     bool: NAME}
                    try:
                        newtoken = (typeToTokenMap[constValue[0]],
                         repr(constValue[1]),
                         begin,
                         tokenEnd,
                         linetext)
                    except:
                        print 'constValue:', constValue
                        print 'token', token

                    count[0] += 1
                    yield newtoken
                else:
                    print 'While parsing %s(%s):  %s' % (filename, begin[0], errorInfo[0])
                    log.general.Log('While precompiling %s(%s): %s' % (filename, begin[0], errorInfo[0]), LGWARN)
                    yield token
                    errorInfo[1].reverse()
                    for errtok in errorInfo[1]:
                        yield errtok

            else:
                yield token


class ResFile(object):
    __slots__ = ['c', 'rf', 'softspace']

    def __init__(self):
        self.rf = blue.ResFile()
        self.c = None

    def Open(self, fn, ro = 1, mode = 'b'):
        global nasty
        self.c = nasty.compiler.GetCargoFile(fn, mode)
        if self.c:
            log.general.Log('nasty.ResFile opened %r from cargo' % fn, LGINFO)
            return True
        if not fn.startswith('wwwroot:'):
            return self.rf.Open(fn, ro, mode)
        return False

    def OpenAlways(self, fn, ro = 1, mode = 'b'):
        if not self.Open(fn, ro, mode):
            raise IOError, (None, 'could not open file', fn)

    def Read(self, amt = -1):
        if self.c:
            return self.c.read(amt)
        return self.rf.Read(amt)

    def read(self, amt = -1):
        if self.c:
            return self.c.read(amt)
        return self.rf.read(amt)

    def Close(self):
        self.rf.Close()
        if self.c:
            self.c.close()
            self.c = None

    close = Close

    def GetFileInfo(self):
        if self.c:
            return {'ftCreationTime': 0,
             'ftLastAccessTime': 0,
             'ftLastWriteTime': 0}
        return self.rf.GetFileInfo()

    @property
    def size(self):
        if self.c:
            where = self.c.tell()
            self.c.seek(0, os.SEEK_END)
            try:
                return self.c.tell()
            finally:
                self.c.seek(where, os.SEEK_SET)

        return self.rf.size

    @property
    def pos(self):
        if self.c:
            return self.c.tell()
        return self.rf.pos


class Nasty():

    class WrappedImportError(Exception):
        pass

    def __init__(self, addScriptDirs = [], codefiles = []):
        self.loadeddlls = []
        import __builtin__
        if hasattr(__builtin__, 'Using'):
            raise RuntimeError('Only one instance of nasty can be running, i.e. only load nasty.py once')
        __builtin__.Import = self.Import
        __builtin__.Using = self.Using
        __builtin__.GetLocalStorage = GetLocalStorage
        __builtin__.GetOtherLocalStorage = GetOtherLocalStorage
        __builtin__.SetLocalStorage = SetLocalStorage
        __builtin__.UpdateLocalStorage = UpdateLocalStorage
        __builtin__.UpdatedLocalStorage = UpdatedLocalStorage
        __builtin__.RecompileFile = self.RecompileFile
        __builtin__.SetGlobal = self.SetGlobal
        __builtin__.nastyStarted = blue.os.GetWallclockTimeNow()
        blue.pyos.AddExitProc(self.Release)
        self.lastModified = 0
        self.addScriptDirs = addScriptDirs
        self.scriptDirs = ['root:/common/script/', 'script:/', 'root:/../carbon/common/script/'] + addScriptDirs
        if boot.role == 'client':
            self.scriptDirs.append('root:/../carbon/client/script/')
        elif boot.role in ('server', 'proxy'):
            self.scriptDirs.append('root:/../carbon/server/script/')
            self.scriptDirs.append('root:/backend/script/')
            self.scriptDirs.append('root:/../carbon/backend/script/')
        if '/jessica' in blue.pyos.GetArg():
            self.scriptDirs.append('root:/backend/script/')
            self.scriptDirs.append('root:/../carbon/backend/script/')
        self.libDirs = blue.paths.GetExpandedSearchPaths()['lib']
        try:
            latestConst = max((os.stat(s).st_mtime for s in (const.__file__, appConst.__file__)))
            compiledCode = self.GetCompiledCodePath()
            latestCompiled = os.stat(compiledCode).st_mtime
            if latestConst >= latestCompiled:
                print 'Compiled code is outdated compared to the const files.  Lets re-pre-process EVERYTHING!!1!'
                try:
                    os.remove(compiledCode)
                except:
                    log.LogException()

        except:
            pass

        expandedDirs = set()
        uniqueScriptDirs = []
        for entry in self.scriptDirs:
            expanded = blue.paths.ResolvePath(unicode(entry))
            if expanded not in expandedDirs:
                expandedDirs.add(expanded)
                uniqueScriptDirs.append(entry)

        self.scriptDirs = uniqueScriptDirs
        for dir in self.scriptDirs:
            try:
                blue.pyos.SpyDirectory(dir, self.OnFileModified)
            except:
                sys.exc_clear()

        for c in codefiles:
            ALLOWED_CODEFILES.append(str(c.strip()))

        self.compiledCodeFile = self.GetCompiledCodePath()
        self.compiler = Compilor()
        if '/thinclient' in blue.pyos.GetArg() and not blue.pyos.packaged:
            mockArgs = filter(lambda e: '/mock' in e, blue.pyos.GetArg())
            if mockArgs:
                mockModules = mockArgs[0][6:].split(';')
                self.compiler.mockedModules = mockModules
                self.compiler.ProcessMocks()
        self.mods = {}
        self.namespaces = {}
        self.waiting = {}
        self.filesByCid = {}
        self.globs = {}
        self.preloads = {}
        __builtin__.Sissy = Sissy
        __builtin__.charsession = Sissy('base.charsession')
        __builtin__.currentcall = Sissy('base.currentcall')
        __builtin__.session = Sissy('base.session')
        __builtin__.caller = Sissy('base.caller')
        self.__fallbackimport__ = __builtin__.__import__
        __builtin__.__import__ = self.ImportNasty
        __builtin__.Using = self.Using
        __builtin__.Import = self.Import
        __builtin__.CreateInstance = self.CreateInstance
        __builtin__.RegisterConstant = self.RegisterConstant
        __builtin__.LtoI = lambda l: (int(l) if l < 2147483648L else ~int(~l & 4294967295L))
        __builtin__.ResFile = ResFile
        self.willCheckModifieds = 0
        self.RegisterNamedObject(NamespaceFailedException, 'exceptions', 'NamespaceFailed', 'nasty.py', globals())
        self.RegisterNamedObject(NamespaceAttributeFailedException, 'exceptions', 'NamespaceAttributeFailed', 'nasty.py', globals())
        self.RegisterNamedObject(NamespaceCollisionError, 'exceptions', 'NamespaceCollisionError', 'nasty.py', globals())
        self.ImportFromBlueDll()
        self.deepReload = False
        try:
            self.useScriptIndexFiles = getattr(boot, 'useScriptIndexFiles', False)
        except KeyError:
            self.useScriptIndexFiles = False

    def GetAppDataCompiledCodePath(self):
        appCodePath = os.path.join(blue.win32.SHGetFolderPath(blue.win32.CSIDL_COMMON_APPDATA), u'CCP\\EVE', util.GetClientUniqueFolderName())
        if not os.path.exists(appCodePath):
            os.makedirs(appCodePath)
        latestBuildNrFound = None
        try:
            for fileName in os.listdir(appCodePath):
                if len(re.findall('^[0-9]+\\.code$', fileName)):
                    nr = fileName.split('.')[0]
                    if nr.isdigit():
                        nr = int(nr)
                        latestBuildNrFound = max(latestBuildNrFound, nr)

        except OSError as e:
            log.general.Log('Nasty could not iterate codepath directory for to look for optional code files. Error Number: %s' % e.errno, LGERR)

        return util.KeyVal(path=appCodePath, build=latestBuildNrFound)

    def GetCompiledCodePath(self):
        if '/jessica' in blue.pyos.GetArg():
            compiledCodeFileName = 'script:/jessicaCompiled.code'
        else:
            compiledCodeFileName = 'script:/compiled.code'
        if boot.role != 'client' or '/safemode' in blue.pyos.GetArg():
            return blue.paths.ResolvePathForWriting(compiledCodeFileName)
        else:
            ret = self.GetAppDataCompiledCodePath()
            if ret.build > boot.build:
                file = os.path.join(ret.path, unicode(ret.build) + u'.code')
                return file
            self.CleanupAppDataCodeFiles()
            return blue.paths.ResolvePathForWriting(compiledCodeFileName)

    def CleanupAppDataCodeFiles(self):
        folder = self.GetAppDataCompiledCodePath().path
        filesDeleted = 0
        for file in os.listdir(folder):
            if file.endswith('.code'):
                try:
                    os.remove(os.path.join(folder, file))
                    filesDeleted = filesDeleted + 1
                except Exception as e:
                    log.general.Log('Could not delete optional upgrade .code file. %s' % e, LGWARN)
                    sys.exc_clear()

        return filesDeleted

    def GetCompiledCodeHash(self, file = None):
        if file is None:
            file = self.GetCompiledCodePath()
        if not os.path.isfile(file):
            return
        readBytes = blue.win32.AtomicFileRead(file)[0]
        cp = blue.crypto.GetVerContext()
        hasher = blue.crypto.CryptCreateHash(cp, blue.crypto.CALG_MD5, None)
        blue.crypto.CryptHashData(hasher, readBytes)
        thehash = blue.crypto.CryptGetHashParam(hasher, blue.crypto.HP_HASHVAL)
        hasher.Destroy()
        return base64.b64encode(thehash).strip().replace('/', '_')

    def IsRunningWithOptionalUpgrade(self):
        if '/jessica' in blue.pyos.GetArg():
            compiledCodeFileName = 'script:/jessicaCompiled.code'
        else:
            compiledCodeFileName = 'script:/compiled.code'
        return os.path.normcase(self.compiledCodeFile) != os.path.normcase(blue.paths.ResolvePath(compiledCodeFileName))

    def ImportNasty(self, name, globals = None, locals = None, fromlist = None, level = -1):
        return self.ImportBootstrap(name, globals, locals, fromlist, level, wrap_error=False)

    def ImportBootstrap(self, name, globals = None, locals = None, fromlist = None, level = -1, wrap_error = True):
        standard_first = level != 0 and globals and globals.get('__package__')
        m = self.FindModule(name, fromlist)
        if m and not standard_first:
            return m
        try:
            try:
                return self.__fallbackimport__(name, globals, locals, fromlist, level)
            except ImportError as e:
                e.args = e.args + (name,)
                if m:
                    return m
                raise 
            except Exception as e:
                if wrap_error:
                    raise self.WrappedImportError, sys.exc_info()[:2], sys.exc_info()[2]
                raise 

        except:
            if name in sys.modules:
                pass
            raise 

    def FindModule(self, name, fromlist):
        if fromlist:
            return self.mods.get(name, None)
        parts = name.split('.')
        head, tail = parts[0], parts[1:]
        mod = self.mods.get(head, None)
        if not mod:
            return
        this = mod
        while tail:
            head, tail = tail[0], tail[1:]
            try:
                this = getattr(this, head)
            except AttributeError:
                return

        return mod

    @telemetry.ZONE_METHOD
    def Initialize(self):
        now = blue.os.GetWallclockTimeNow()
        args = blue.pyos.GetArg()
        if blue.pyos.packaged:
            log.general.Log('Packaged blue, not browsing', LGINFO)
        else:
            log.general.Log('Unpackaged blue, browsing', LGINFO)
        if '/ziplib' in args:
            from createzipfile import CreateZipFile
            for libDir in self.libDirs:
                libDir = libDir.rstrip('/')
                libDirParts = libDir.split(os.sep)
                prefix = libDirParts[-3]
                folderName = '/'.join(libDirParts[0:-1])
                filename = prefix + libDirParts[-1]
                zipName = folderName + '/' + filename + '.ccp'
                zipInput = ((libDir, None),)
                CreateZipFile(zipName, zipInput)

        if not blue.pyos.packaged and '/nobrowse' not in args:
            log.general.Log('Browsing for files in %s' % self.scriptDirs, LGINFO)
            log.general.Log('Mappings are here:', LGNOTICE)
            directories = self.scriptDirs[:]
            directories.sort()
            for directory in directories:
                path = blue.paths.ResolvePathForWriting(unicode(directory))
                exists = os.path.exists(path)
                logLevel = LGNOTICE if exists else LGWARN
                state = '' if exists else ', but this path does not exist on disk!'
                defined = 'autoexec' if directory in self.addScriptDirs else 'nasty'
                string = "    '{directory}' maps to '{path}' as defined by {defined}{state}".format(**locals())
                log.general.Log(string, logLevel)

            files, filecount, dircount = self.BrowseScriptDirectories(self.scriptDirs, self.useScriptIndexFiles)
            log.general.Log('Found %s files in %s directories' % (filecount, dircount), LGINFO)
        else:
            files = []
        for each in args:
            if each.startswith('/wait'):
                blue.pyos.synchro.SleepWallclock(1000 * int(each[5:]))

        browsed_files = set(files)
        to_remove = set()
        to_compile = set()
        self.compiler = Compilor()
        tabularasa = True
        compiled_files = set()
        if '/compile' not in args:
            self.compiler.Flush()
            for codefile in ALLOWED_CODEFILES:
                log.general.Log('Loading codefile: %s' % codefile, LGINFO)
                fileToLoad = self.compiledCodeFile
                if codefile != 'compiled':
                    fileToLoad = 'script:/' + codefile + '.code'
                    fileToLoad = blue.paths.ResolvePath(fileToLoad)
                    if not os.path.exists(fileToLoad):
                        log.general.Log('Codefile: %s does not exists, skipping it' % codefile, LGINFO)
                        continue
                try:
                    self.compiler.Load(fileToLoad)
                    tabularasa = False
                    compiled_files.update(self.compiler.GetFiles())
                except Exception as e:
                    log.general.Log("Couldn't load compiled code: %s" % e, LGWARN)
                    if nasty.IsRunningWithOptionalUpgrade():
                        log.general.Log('Loading a optional upgraded compiled.code file failed, reverting to installed file', LGWARN)
                        self.compiledCodeFile = os.path.normcase(blue.paths.ResolvePathForWriting('script:/compiled.code'))
                        try:
                            self.compiler.Load(self.compiledCodeFile)
                            tabularasa = False
                            compiled_files.update(self.compiler.GetFiles())
                        except Exception as e:
                            log.general.Log("Couldn't load installed compiled code: %s" % e, LGWARN)
                            sys.exc_clear()

        to_compare = browsed_files.intersection(compiled_files)
        to_compile = browsed_files - to_compare
        to_remove = compiled_files - to_compare
        compiledTime = self.compiler.modTime
        if to_compare:
            check = blue.classes.CreateInstance('blue.ResFile')
            for f in to_compare:
                check.Open(f[0])
                if check.GetFileInfo()['ftLastWriteTime'] >= compiledTime:
                    log.general.Log('file %s newer than compiled code' % f[0], LGINFO)
                    to_compile.add(f)

            check.Close()
        if compiledTime:
            codedate = blue.os.FormatUTC(compiledTime)
            log.general.Log('Using %s from %s %s' % (self.compiledCodeFile, codedate[0], codedate[2]), LGINFO)
        canDelete = to_remove and not blue.pyos.packaged
        if canDelete:
            for filename in to_remove:
                log.general.Log('removing deleted file from compiled.code %s' % str(filename), LGWARN)

            self.compiler.Delete(to_remove)
        if to_compile:
            log.general.Log('Compiling code', LGINFO)
            self.compiler.Compile(to_compile)
            cargofiles = blue.ResFile()
            if cargofiles.Open('script:/cargo.txt'):
                lines = str(cargofiles.Read()).split('\n')
                for line in lines:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    if ';' in line:
                        line, target = line.split(';')
                    else:
                        target = line
                        f = target.lower().find('/wwwroot/')
                        if f >= 0:
                            target = 'wwwroot:/' + target[f + 9:]
                    cargo = blue.ResFile()
                    if cargo.Open(line):
                        log.general.Log('adding cargo file %r as %r' % (line, target), LGINFO)
                        self.compiler.AddCargo(target, cargo.Read())
                        cargo.Close()
                    else:
                        log.general.Log('failed adding cargo file %s' % repr(line), LGINFO)

                cargofiles.Close()
        if '/verbose' in args:
            log.general.Log('nasty cargo cointains:', LGINFO)
            cargo = self.compiler.cargo.keys()
            cargo.sort()
            for c in cargo:
                log.general.Log(repr(c), LGINFO)

        self.BootstrapAndReorder(self.compiler.GetFiles(), bool(to_compile), tabularasa)
        if not blue.pyos.packaged:
            codefiles = []
            for key in self.compiler.code:
                if key[1] not in codefiles:
                    codefiles.append(key[1])

            for codefile in codefiles:
                log.general.Log('Saving codefile %s to file' % codefile, LGINFO)
                if codefile == 'compiled':
                    self.compiler.Save(self.compiledCodeFile, codefile)
                else:
                    path = 'script:/' + codefile + '.code'
                    path = blue.paths.ResolvePath(path)
                    self.compiler.Save(path, codefile)

        log.general.Log('Code initialized in %.2f sec.' % (float(blue.os.GetWallclockTimeNow() - now) / 10000000.0,), LGINFO)
        self.compiler.DiscardCode()
        if not blue.pyos.packaged:
            self.compiler.RemoveCargo()
        if '/sign' in args:
            ix = args.index('/sign') + 1
            if ix >= len(args):
                log.general.Log('missing password', LGERR)
                raise SystemExit, 'missing password'
            pw = args[ix]
            pw = pw.encode('cp1252')
            import lowdown
            print 'creating manifest'
            manifestfiles = ['app:/manifest.txt', 'app:/../common/manifest_common.txt']
            if '/signbin' in args:
                ix = args.index('/signbin') + 1
                if ix + 1 >= len(args):
                    log.general.Log('missing bin and dest signbin path', LGERR)
                    raise SystemExit, 'missing bin and dest signbin path'
                bindir = args[ix]
                binpath = args[ix + 1]
                log.general.Log('signing all binaries in %s for %s' % (bindir, binpath))
                binManifest = lowdown.CreateBinManifestSource(bindir, bindir, binpath)
                manifestfiles.append(binManifest)
            lowdown.CreateManifest(manifestfiles, 'app:/../GoldenCD.pikl', 'app:/manifest.dat', pw)
            log.general.Log('nasty created signed manifest')
        if '/compile' in blue.pyos.GetArg():
            report = blue.classes.CreateInstance('blue.ResFile')
            report.Create(blue.paths.ResolvePathForWriting(u'root:/codefiles.txt'))
            for name in self.compiler.GetFiles():
                name = blue.paths.ResolvePath(name[0])
                name = name.replace('/', '\\')
                report.Write(name + '\r\n')

            report.Close()
            bluepy.Terminate('Quitting after compile-only run.')
            raise SystemExit
        if '/nastyquit' in args:
            bluepy.Terminate('Quitting nasty as requested.')
            raise SystemExit
        self.lastModified = blue.os.GetWallclockTime()
        self.timeResetDelta = 0

    def OnTimeReset(self, oldTime, newTime):
        self.timeResetDelta = newTime - oldTime
        self.lastModified += self.timeResetDelta

    def OnFileModified(self):
        if not self.lastModified or self.willCheckModifieds:
            return
        self.willCheckModifieds = 1
        import uthread
        uthread.new(self.OnFileModified_)

    def OnFileModified_(self):
        try:
            blue.pyos.synchro.SleepWallclock(550)
            x = blue.classes.CreateInstance('blue.ResFile')
            lm = 0
            now = blue.os.GetWallclockTime()
            namespaceFiles = set()
            for each in self.compiler.GetFiles():
                if not x.FileExists(each[0]):
                    print 'File deleted %s' % each[0]
                    continue
                x.OpenAlways(each[0])
                ftLast = x.GetFileInfo()['ftLastWriteTime'] + self.timeResetDelta
                if ftLast > now:
                    print 'File from the future detected. It might screw up my auto-compile feature.'
                    print '    ', blue.os.FormatUTC(ftLast)[0], blue.os.FormatUTC(ftLast)[2], each
                if ftLast > self.lastModified:
                    print 'Change detected in file', each, 'reloading classes'
                    namespaceFiles.add(each)
                    lm = max(ftLast, lm)

            if not len(namespaceFiles):
                return
            if len(namespaceFiles):
                print 'modified files: ', list(namespaceFiles)
                allClasses = {}
                self.compiler.DiscardCode(namespaceFiles)
                self.Bootstrap(namespaceFiles, 1, allClasses)
                loadedClasses = [ k for k, v in allClasses.items() if v ]
                updatedClasses = [ k for k, v in allClasses.items() if not v ]
                self.compiler.DiscardCode()
                if loadedClasses:
                    print 'reloaded classes:'
                    for k in loadedClasses:
                        print '    ', k

                if updatedClasses:
                    print 'updated classes:'
                    for k in updatedClasses:
                        print '    ', k

                self.SendReloadEvent(loadedClasses)
                self.SendUpdateEvent(updatedClasses)
                import __builtin__
                if hasattr(__builtin__, 'sm'):
                    guids = allClasses.keys()
                    servicesToReload = [ guid[4:] for guid in guids if guid.startswith('svc.') ]
                    sm.Reload(servicesToReload)
            import linecache
            linecache.clearcache()
            self.lastModified = max(lm, self.lastModified)
        finally:
            self.willCheckModifieds = 0

    def SendReloadEvent(self, c):
        sm.ScatterEvent('OnClassReload', c)

    def SendUpdateEvent(self, c):
        sm.ScatterEvent('OnClassUpdate', c)

    def RecompileFile(self, fileName):
        print 'Recompiling ', fileName
        if fileName in self.compiledCode:
            del self.compiledCode[fileName]
        self.Run([fileName], 1)
        import __builtin__
        if hasattr(__builtin__, 'sm'):
            guids = self.GatherFileGuids(fileName)
            servicesToReload = [ guid[4:] for guid in guids if guid.startswith('svc.') ]
            sm.Reload(servicesToReload)
        import linecache
        linecache.clearcache()

    def BrowseScriptDirectories(self, dirs, useScriptIndexFiles = True):
        files = []
        filecount = 0
        indexCaches = {}
        if useScriptIndexFiles:
            for dirPath in dirs:
                d = indexCaches[dirPath] = {}
                self.IndexScriptDirectories(dirPath, d)

        for dirPath in dirs:
            try:
                fileList = blue.pyos.EnumFolder(dirPath, '*.py')
            except:
                log.general.Log("Nasty was unable to locate the directory '%s'" % dirPath, LGWARN)
                sys.exc_clear()
                continue

            newFiles = self.BrowseEnumFiles(dirPath, fileList[1])
            indexCache = indexCaches.get(dirPath, {})
            for file in newFiles:
                if len(indexCache):
                    if file.lower() in indexCache:
                        codefile = indexCache[file.lower()]
                        files.append((file, codefile))
                elif not useScriptIndexFiles:
                    fileName = os.path.basename(file)
                    if fileName[0] == '_':
                        continue
                    files.append((file, 'compiled'))

            if len(indexCache):
                log.general.Log("Nasty fell back to using 'index.txt' support for: " + dirPath, LGINFO)
            filecount += len(newFiles)

        return (files, filecount, 0)

    def IndexScriptDirectories(self, scriptPath, indexCache):
        f = blue.ResFile()
        indexPath = scriptPath + 'index.txt'
        if f.Open(indexPath):
            lines = str(f.Read()).split('\n')
            for line in lines:
                line = line.strip()
                codefile = 'compiled'
                if '|' in line:
                    line, codefile = line.split('|')
                    if codefile not in ALLOWED_CODEFILES:
                        log.general.Log('Skipping %s since it belongs to a non valid codefile %s' % (line, codefile), LGINFO)
                        continue
                if len(line) and line[0] != ' ' and line[0] != '#':
                    if line[-1] == '/':
                        self.IndexScriptDirectories(scriptPath + line, indexCache)
                    elif line[-3:] == '.py':
                        line = line.replace('\\', '/')
                        indexCache[(scriptPath + line).lower()] = codefile

    def BrowseEnumFiles(self, resPath, fileList):
        if not len(fileList):
            return []
        idx = fileList[0][1].rfind('/script/')
        if idx == -1:
            raise RuntimeError('Bad path in nasty', fileList[0][1], fileList[0][0])
        files = []
        for t in fileList:
            dirPath = t[1]
            relPath = dirPath[idx + 8:]
            if relPath.startswith('wwwroot/'):
                continue
            resDirName = resPath + relPath
            resBaseName = t[0]
            files.append(resDirName + resBaseName)

        return files

    def BrowseWebCargo(self, dirs, add = True):
        filecount = 0
        dircount = 0
        all = []
        for dir in dirs:
            log.general.Log('Adding Web Cargo from %s' % dir, LGINFO)
            dir = blue.paths.ResolvePath(dir)
            all.extend(os.walk(dir))

        for dirpath, dirnames, filenames in all:
            www = dirpath.lower().find('wwwroot/')
            prefix = 'wwwroot:' + dirpath[www + 7:] + '/'
            dircount += 1
            for f in filenames:
                file = os.path.join(dirpath, f)
                target = prefix + f
                log.general.Log('%sing cargo file %s as %s' % (('Remov', 'Add')[add], file, target), LGINFO)
                filecount += 1
                rf = blue.ResFile()
                if rf.Open(file):
                    data = rf.Read()
                    rf.Close()
                    if add:
                        self.compiler.AddCargo(target, data)
                    else:
                        self.compiler.RemoveCargo(target)

        log.general.Log('%sed %s web cargo files from %s directories' % (('Remov', 'Add')[add], filecount, dircount), LGINFO)

    def ExtractClassfiles(self):
        for guid, filename in self.filesByCid.iteritems():
            print 'Guid: ', guid, 'Filename:', filename

    @telemetry.ZONE_METHOD
    def Bootstrap(self, filesToScan, fromReload = 0, loaded = {}):
        candidates = filesToScan
        newOrder = []
        bootPass = 0
        while candidates:
            bootPass += 1
            log.general.Log('Bootstrapping %s files, pass %s' % (len(candidates), bootPass), LGINFO)
            known = self.mods.keys()
            failed = []
            exceptionCounts = {}
            exceptionsByFile = {}
            testOutputByFile = {}
            for each in candidates:
                try:
                    old = __builtin__.__import__
                    __builtin__.__import__ = self.ImportBootstrap
                    ok = False
                    try:
                        self.ImportFromFile(each, fromReload, None, loaded)
                        ok = True
                    finally:
                        __builtin__.__import__ = old

                except self.WrappedImportError as e:
                    raise e.args[0], e.args[1], sys.exc_info()[2]
                except (ImportError, AttributeError, NameError) as val:
                    pass
                except Exception:
                    log.general.Log("UNCAUGHT/UNEXPECTED EXCEPTION; NOTIFY YOUR LOCAL 'nasty' PROGRAMMER", LGERR)
                    raise 

                if ok:
                    newOrder.append(each)
                else:
                    failed.append(each)
                    exceptionsByFile[each] = self.SummarizeException(each, exceptionCounts)
                sys.exc_clear()
                blue.pyos.BeNice()

            if len(failed) == len(candidates):
                self.BootstrapFailure(candidates, fromReload, exceptionsByFile, exceptionCounts, testOutputByFile)
            newValues = []
            for key in self.mods.iterkeys():
                if key not in known:
                    newValues.append(key)

            newValues.sort()
            log.general.Log('Bootstrap pass %s added namespaces %s' % (bootPass, newValues), LGINFO)
            candidates = failed

        return newOrder

    @telemetry.ZONE_METHOD
    def BootstrapAndReorder(self, files, resort = False, tabularasa = False):
        if resort and tabularasa:
            files.sort()
        else:
            files.sort(key=self.compiler.GetAttr)
        files = self.Bootstrap(files)
        if resort:
            for i, file in enumerate(files):
                self.compiler.SetAttr(file, i)

    def BootstrapFailure(self, candidates, fromReload, exceptionsByFile, exceptionCounts, testOutputByFile):
        log.general.Log('Unsurmountable resolution failure while bootstrapping classfiles. errors follow:', LGERR)
        for c in candidates:
            if c in testOutputByFile:
                testOutputByFile[c].FlushBuffer()
            for l in exceptionsByFile[c]:
                log.general.Log(l, LGWARN)

        log.general.Log('end of list.', LGERR)
        log.general.Log('list with duplicates removed:', LGERR)
        for ex, (n, c, full) in exceptionCounts.iteritems():
            lines = ['Bootstrapping %s:' % c[0]]
            lines += full
            lines += ['(%s times)' % n]
            for l in lines:
                log.general.Log(l, LGERR)

        log.general.Log('end of list.', LGERR)
        if bluepy.IsRunningStartupTest():
            log.general.Log('Terminating startup test due to a failure to compile', LGERR)
            bluepy.TerminateStartupTestWithFailure()
        raise ImportError('bootstrap failed on %s' % list(candidates))

    def SummarizeException(self, filename, exceptionCounts = None):
        et, ev, tb = sys.exc_info()
        lines = ['Bootstrapping %s:' % filename[0]]
        full = traceback.format_exception(et, ev, tb)
        tb = traceback.format_list(traceback.extract_tb(tb)[-1:])
        ex = traceback.format_exception_only(et, ev)
        if exceptionCounts is not None:
            exceptionCounts[ex[0]] = (exceptionCounts.get(ex[0], (0, ''))[0] + 1, filename, full)
        lines += tb
        lines += ex
        return lines

    def ReloadClass(self, cid):
        loaded = {}
        if cid in self.filesByCid:
            self.ImportFromFile(self.filesByCid[cid], 1, cid, loaded)
        return loaded.keys()

    def ReloadFile(self, filename):
        return self.ImportFromFile(filename, 1)

    def Import(self, name, hack = 1):
        ns = self.namespaces.get(name, None)
        if ns is None:
            if name not in self.mods:
                try:
                    self.ImportFromBlueDll(name + '.dll')
                except (IOError, blue.error) as e:
                    sys.exc_clear()

            if name in self.mods:
                ns = Namespace(name, self.mods[name].__dict__)
                self.namespaces[name] = ns
            else:
                raise NamespaceFailedException, name
        if hack:
            loc = sys._getframe().f_back.f_globals
            loc[name] = ns
        return ns

    def Release(self):
        blue.pyos.SpyDirectory()
        import __builtin__
        if getattr(__builtin__, 'Using') == self.Using:
            delattr(__builtin__, 'Using')
            delattr(__builtin__, 'CreateInstance')
            del __builtin__.RegisterConstant
        self.namespaces = {}
        self.mods = {}
        self.globs = {}
        self.preloads = {}

    def AddPreLoadVariable(self, name, var):
        self.preloads[name] = var

    class BlueCreateWrapper(object):

        def __init__(self, moduleName, className):
            self.cid = moduleName + '.' + className

        def __call__(self, *args):
            import blue
            return blue.classes.CreateInstance(self.cid, args)

    def GetModuleDict(self, moduleName):
        if moduleName not in self.mods:
            if moduleName not in sys.modules:
                try:
                    self.__fallbackimport__(moduleName)
                except ImportError:
                    sys.exc_clear()

            if moduleName in sys.modules:
                mod = sys.modules[moduleName]
                if '.' in moduleName:
                    self.GetModuleDict(moduleName.rsplit('.', 1)[0])
            else:
                mod = imp.new_module(moduleName)
                if '.' in moduleName:
                    inModule, name = moduleName.rsplit('.', 1)
                    addTo = self.GetModuleDict(inModule)
                    if name in addTo:
                        raise NamespaceCollisionError(name, inModule)
                    else:
                        addTo[name] = mod
            self.mods[moduleName] = mod
        return self.mods[moduleName].__dict__

    def UnregisterFile(self, fileName):
        cids = [ key for key, val in self.filesByCid.items() if val == fileName ]
        for cid in cids:
            del self.filesByCid[cid]

    def RegisterNamedObject(self, obj, moduleName, className, fileName, globaldict = None, allowRedef = None):
        if not className:
            moduleName, className = moduleName.rsplit('.', 1)
        fullName = moduleName + '.' + className
        d = self.GetModuleDict(moduleName)
        if not allowRedef and className in d:
            if obj is d[className]:
                return
            alreadyDefinedIn = self.filesByCid.get(fullName, 'none')
            log.general.Log('Attempting to redefine %s in %s (already defined in %s).' % (fullName, fileName, alreadyDefinedIn), LGINFO)
            log.general.Log('The definition for %s from %s will be ignored.' % (fullName, fileName), LGINFO)
            return
        d[className] = obj
        self.filesByCid[fullName] = fileName
        if '__all__' not in d:
            unique = '__all_%s__' % moduleName
            all = [unique]
            d['__all__'] = d[unique] = all
        d['__all__'].append(className)
        if hasattr(obj, '__module__'):
            try:
                obj.__module__ = moduleName
            except:
                sys.exc_clear()

        if globaldict is not None:
            self.globs[fullName] = globaldict
        return 1

    def UpdateNamedObject(self, obj, moduleName, className, fileName, globaldict = None):
        if not className:
            moduleName, className = moduleName.rsplit('.', 1)
        fullName = moduleName + '.' + className
        d = self.GetModuleDict(moduleName)
        register = className not in d
        if not register:
            old = d[className]
            if str(type(old)) != str(type(obj)):
                register = True
            if not register and not isinstance(obj, (types.TypeType, types.ClassType)):
                register = True
            if not register and getattr(obj, '__dict__', None) is None:
                register = True
        if register:
            ret = self.RegisterNamedObject(obj, moduleName, className, fileName, globaldict, True)
            if ret == 1:
                print 'Registered "%s" from "%s"' % (fullName, fileName)
            else:
                print 'Registering "%s" from "%s" failed' % (fullName, fileName)
            return ret
        print 'Updating "%s" from "%s"' % (fullName, fileName)
        updatedFuncGlobals = False
        for k, v in obj.__dict__.items():
            if k not in ('__dict__', '__doc__', '__module__'):
                try:
                    oldv = old.__dict__.get(k, None)
                    if old.__dict__.has_key(k):
                        if hasattr(oldv, 'func_globals') and v is not None:
                            if (oldv.func_code, oldv.func_defaults, oldv.func_closure) == (v.func_code, v.func_defaults, v.func_closure):
                                v = oldv
                            elif not updatedFuncGlobals:
                                for gk, gv in oldv.func_globals.iteritems():
                                    if v.func_globals.has_key(gk):
                                        gvNew = v.func_globals[gk]
                                        if isinstance(gvNew, (types.TypeType, types.ClassType)) and hasattr(gvNew, '__guid__'):
                                            v.func_globals[gk] = gv

                                updatedFuncGlobals = True
                    if oldv is not v:
                        setattr(old, k, v)
                        if oldv is not None:
                            self.__UpdateObjectReferrers(old, k, oldv, v)
                except:
                    log.LogException()
                    sys.exc_clear()

        self.filesByCid[fullName] = fileName
        return False

    def __UpdateObjectReferrers(self, obj, k, oldValue, newValue):
        if not self.deepReload:
            return
        if isinstance(oldValue, types.FunctionType) and isinstance(newValue, types.FunctionType):
            referrer1List = gc.get_referrers(oldValue)
            for referrer1 in referrer1List:
                if type(referrer1) is types.MethodType and referrer1.im_func is oldValue:
                    for referrer2 in gc.get_referrers(referrer1):
                        if isinstance(referrer2, types.DictType):
                            for rk, rv in referrer2.iteritems():
                                if rv is referrer1:
                                    referrer2[rk] = types.MethodType(newValue, referrer1.im_self, referrer1.im_class)

                        elif isinstance(referrer2, types.ListType) and referrer2 is not referrer1List:
                            if referrer1 not in referrer2:
                                continue
                            idx = referrer2.index(referrer1)
                            referrer2[idx] = types.MethodType(newValue, referrer1.im_self, referrer1.im_class)

                    blue.pyos.BeNice()
                elif not isinstance(referrer1, types.FrameType):
                    pass

    @telemetry.ZONE_METHOD
    def ImportFromFile(self, filename, fromReload = 1, guid = None, loaded = {}):
        if not len(filename):
            return
        telemetry.APPEND_TO_ZONE(filename[0])
        if filename[0][-3:] == '.py':
            code = self.compiler.GetCode(filename)
            globaldict = {'__codehash__': self.compiler.GetHash(filename)}
            globaldict.update(self.preloads)

            def Exec(code, globaldict):
                exec (code, globaldict)

            Mark('^boot::nasty_exec::%s' % filename[0], Exec, code, globaldict)
            self.ImportFromGlobals(globaldict, filename, fromReload, guid, loaded)
            return loaded.keys()
        if filename[-4:] == '.dll':
            return self.ImportFromBlueDll(filename)
        return []

    allMatch = re.compile('__all_(\\w+)__')

    @telemetry.ZONE_METHOD
    def ImportFromGlobals(self, moduleDict, filename, fromReload, onlyGuid, loaded):
        imports = []
        for k, v in moduleDict.iteritems():
            m = self.allMatch.match(k)
            if m:
                module = m.group(1)
                imports.extend([ module + '.' + item for item in v ])

        exports = moduleDict.get('exports', {}).copy()
        for val in moduleDict.itervalues():
            if isinstance(val, thinmock.ThinMock):
                continue
            try:
                guid = val.__dict__['__guid__']
            except AttributeError:
                continue
            except KeyError:
                continue

            if guid and guid not in imports:
                exports[guid] = val

        if fromReload and not onlyGuid:
            self.UnregisterFile(filename)
        for guid, var in exports.iteritems():
            if onlyGuid and onlyGuid != guid:
                continue
            isClass = isinstance(var, (types.TypeType, types.ClassType))
            if isClass and fromReload and (not hasattr(var, '__update_on_reload__') or var.__update_on_reload__):
                r = self.UpdateNamedObject(var, guid, None, filename, moduleDict)
            else:
                r = self.RegisterNamedObject(var, guid, None, filename, moduleDict, fromReload)
            if r:
                loaded[guid] = True
                if isClass and fromReload:
                    self.ReloadDerivedTypes(var, loaded)
            else:
                loaded[guid] = False

    def ReloadDerivedTypes(self, kl, loaded):
        import types
        if type(kl) == types.TypeType:
            stuffToLoad = []
            for name, module in self.mods.iteritems():
                for attribute, kl2 in module.__dict__.iteritems():
                    if type(kl2) != types.TypeType or type(kl2 != types.ClassType):
                        continue
                    if issubclass(kl2, kl) and kl2 != kl:
                        guid = name + '.' + attribute
                        if guid not in loaded:
                            fn = self.filesByCid.get(guid, None)
                            if fn:
                                stuffToLoad.append((fn, guid))

            for f, guid in stuffToLoad:
                self.ImportFromFile(f, 1, guid, loaded)

    @telemetry.ZONE_METHOD
    def ImportFromBlueDll(self, filename = None):
        if filename:
            if filename in self.loadeddlls:
                return []
            modulename = filename[:-4]
            prev = blue.classes.GetClassTypes()
            try:
                blue.classes.LoadModule(modulename)
            except blue.error:
                raise IOError, (None, 'module not loadable by blue', modulename)

        else:
            prev = []
        ret = []
        for each in blue.classes.GetClassTypes():
            if each in prev:
                continue
            moduleInfo = each[0]
            moduleName = moduleInfo['module']
            className = moduleInfo['classname']
            cls = self.BlueCreateWrapper(moduleName, className)
            if self.RegisterNamedObject(cls, moduleName, className, filename):
                ret.append(moduleName + '.' + className)

        if filename:
            self.loadeddlls.append(filename)
        return ret

    def CreateInstance(self, cid, arguments = ()):
        try:
            namespace, name = cid.split('.')
        except:
            raise RuntimeError('InvalidClassID', cid)

        try:
            ns = self.mods[namespace].__dict__
        except:
            raise NamespaceFailedException, namespace

        try:
            constructor = ns[name]
        except:
            raise AttributeError, 'namespace %s has no member %s' % (namespace, name)

        ret = apply(constructor, arguments)
        if hasattr(ret, '__persistvars__'):
            for each in ret.__persistvars__:
                if not hasattr(ret, each):
                    setattr(ret, each, None)

        if hasattr(ret, '__nonpersistvars__'):
            for each in ret.__nonpersistvars__:
                if not hasattr(ret, each):
                    setattr(ret, each, None)

        return ret

    def Using(self, namespace, loc = None):
        import blue, types
        if loc is None:
            f = sys._getframe().f_back
            loc = f.f_globals
        if isinstance(namespace, Namespace):
            stuff = namespace.space
        elif isinstance(namespace, types.ModuleType):
            stuff = namespace.__dict__
        elif type(namespace) == type(blue.os):
            stuff = {}
            meths = namespace.TypeInfo()[3].iterkeys()
            for each in meths:
                stuff[each] = getattr(namespace, each)

            attrs = namespace.TypeInfo()[2].iterkeys()
            for each in attrs:
                stuff[each] = getattr(namespace, each)

        else:
            raise TypeError, namespace
        if '__all__' in stuff:
            keys = stuff['__all__']
        else:
            keys = [ key for key in stuff.keys() if not key.startswith('_') ]
        for key in keys:
            loc[key] = stuff[key]

    def SetGlobal(self, classId, attr, var):
        self.globs[classId][attr] = var

    def RegisterConstant(self, name, var):
        self.RegisterNamedObject(var, 'const', name, 'RegisterConstant')

    def GatherFileGuids(self, files):
        guids = [ key for key, val in self.filesByCid.items() if val in files ]
        return guids


import warnings, log

class WarningHandler(object):

    def __init__(self):
        self.oldhandler = warnings.showwarning
        warnings.showwarning = self.ShowWarning

    def __del__(self):
        if warnings:
            warnings.showwarning = self.oldhandler

    def ShowWarning(self, message, category, filename, lineno, file = None):
        string = warnings.formatwarning(message, category, filename, lineno)
        log.LogTraceback(extraText=string, severity=log.LGWARN, nthParent=3)
        if not file:
            file = sys.stderr
        print >> file, string


def CrtAllocHook(*args):
    if args[0] in (blue.win32._HOOK_ALLOC, blue.win32._HOOK_REALLOC) and args[1] > 104857600:
        try:
            fn = 'root:/logs/AllocDump.dmp'
            f = blue.paths.ResolvePathForWriting(fn)
            blue.win32.MiniDumpWriteDump(f)
            f = blue.ResFile()
            if f.Open(fn):
                data = f.Read()
                sm.StartService('alert').Alert('AllocHook', 'AllocHook Warning', 'Allocating %s' % repr(args), html=0, throttle=None, sysinfo=1, recipients=['kristjan@ccpgames.com', 'matti@ccpgames.com'], attachments=[('AllocDump.dmp', data)])
                f.Close()
        except:
            fn = 'failed'

        log.general.Log('Huge alloc %s' % repr(args), LGWARN)
        log.general.Log('Wrote minidump in %s' % fn, LGWARN)
        log.general.Log('Stacktrace follows:', LGWARN)
        log.LogTraceback()


if prefs.GetValue('clusterName', None) is None:
    prefs.clusterName = blue.pyos.GetEnv().get('COMPUTERNAME', 'LOCALHOST') + '@' + blue.pyos.GetEnv().get('USERDOMAIN', 'NODOMAIN')
if prefs.GetValue('clusterMode', None) is None:
    prefs.clusterMode = 'LOCAL'
prefs.clusterName = prefs.clusterName.upper()
prefs.clusterMode = prefs.clusterMode.upper()
warningHandler = WarningHandler()
if False and boot.role == 'proxy' and prefs.clusterMode != 'LIVE':
    blue.win32._CrtSetAllocHook(CrtAllocHook, 100 * 1024 * 1024)

def gccallback(mode, n = 0):
    if not mode:
        log.LogTraceback('gc traceback', severity=log.LGINFO, toAlertSvc=False)
    else:
        print 'gc released %d objects' % n


nastyInitialized = False
nasty = None

def Startup(addScriptDirs = []):
    global nasty
    global nastyInitialized
    codefiles = []
    if not blue.pyos.packaged:
        for arg in blue.pyos.GetArg():
            if arg.startswith('/codefiles:'):
                for codefile in arg[11:].split(','):
                    codefiles.append(str(codefile))

                break

    nasty = Nasty(addScriptDirs, codefiles)
    nasty.Initialize()
    nastyInitialized = True