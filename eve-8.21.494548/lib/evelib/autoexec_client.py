#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\eve\common\lib\autoexec_client.py
import autoexec_client_core
import eveLog
import blue
import stackless
stackless.getcurrent().block_trap = True
appCacheDirs = ['Browser',
 'Browser/Img',
 'Map',
 'Pictures',
 'Pictures/Alliances',
 'Pictures/Gids',
 'Pictures/Planets',
 'Pictures/Portraits',
 'Pictures/Characters',
 'Pictures/Characters/Chat',
 'Pictures/Types',
 'Pictures/Blueprints',
 'Temp',
 'Temp/Mapbrowser',
 'Texture',
 'Texture/Planets',
 'Texture/Planets/Visited',
 'Shader',
 'Fonts']
userCacheDirs = ['/EVE/capture',
 '/EVE/capture/Screenshots',
 '/EVE/capture/Portraits',
 '/EVE/logs',
 '/EVE/logs/Chatlogs',
 '/EVE/logs/Gamelogs',
 '/EVE/logs/Marketlogs',
 '/EVE/logs/Fleetlogs']

def builtinSetupHook():
    import eve
    import base
    import __builtin__
    evetmp = eve.eve
    evetmp.session = __builtin__.session
    del eve
    __builtin__.eve = evetmp


servicesToRun = ['counter',
 'sessionMgr',
 'addressbook',
 'clientStatsSvc',
 'dataconfig',
 'godma',
 'photo',
 'machoNet',
 'mailSvc',
 'notificationSvc',
 'objectCaching',
 'LSC',
 'patch',
 'inv',
 'pwn',
 'focus',
 'debug',
 'jumpQueue',
 'scanSvc',
 'browserHostManager',
 'localizationClient',
 'launcher',
 'jumpMonitor',
 'calendar',
 'liveUpdateSvc',
 'monitor',
 'processHealth',
 'planetInfo',
 'district']
if blue.pyos.packaged:
    preUIStartArgProcessHook = None
else:

    def preUIStartArgProcessHook(args):
        if '/autologin' in args:
            import autoLogin
            handler = autoLogin.AutoLoginHandler()
            blue.pyos.CreateTasklet(handler.ParseCommandLineAndLogin, (), {})


StartupUIServiceName = 'gameui'
startInline = ['config',
 'machoNet',
 'objectCaching',
 'dataconfig',
 'dogmaIM',
 'device']
import eveLocalization
if boot.region == 'optic':
    eveLocalization.SetTimeDelta(28800)
    prefs.SetValue('languageID', 'ZH')
autoexec_client_core.StartClient(appCacheDirs, userCacheDirs, builtinSetupHook, servicesToRun, preUIStartArgProcessHook, StartupUIServiceName, startInline, serviceManagerClass='EveServiceManager')