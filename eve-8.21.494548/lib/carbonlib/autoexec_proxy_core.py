#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\autoexec_proxy_core.py
import log
import autoexec_common
import bluepy
import const
RESSURECTED_MESH_SLEEP_DURATION_MS = 250
RESSURECTED_MESH_LOG_PERIOD_MS = 5000

def Startup(servicesToRun, servicesToBlock = [], startInline = [], serviceManagerClass = 'ServiceManager'):
    import blue
    blue.os.SetAppTitle('Juuuust a moment...')
    args = blue.pyos.GetArg()[1:]
    autoexec_common.LogStarting('Proxy')
    additionalScriptDirs = ['script:/../../../carbon/backend/script/', 'script:/../../backend/script/']
    if '/jessica' in args:
        additionalScriptDirs.extend(['script:/../../../carbon/tools/jessica/script/'])
        useExtensions = '/noJessicaExtensions' not in args
        if useExtensions:
            additionalScriptDirs.extend(['script:/../../../carbon/tools/jessicaExtensions/script/', 'script:/../../tools/jessicaExtensions/script/'])
    import nasty
    nasty.Startup(additionalScriptDirs)
    import localization
    localization.LoadLanguageData()
    import gc
    gc.disable()
    autoexec_common.LogStarted('Proxy')
    for i in args:
        if len(i) > 0 and i[0] != '-' and i[0] != '/':
            print 'Executing', i
            blue.pyos.ExecFile(i, globals())

    import service
    smClass = getattr(service, serviceManagerClass)
    srvMng = smClass(startInline=['DB2', 'machoNet'] + startInline)
    srvMng.Run(servicesToRun, servicesToBlock)
    macho = sm.services['machoNet']
    blue.os.SetAppTitle('[%s %s.%s] %s %s %s.%s pid=%s' % (macho.GetNodeID(),
     '?',
     boot.region.upper(),
     boot.codename,
     boot.role,
     boot.version,
     boot.build,
     blue.os.pid))
    if bluepy.IsRunningStartupTest():
        bluepy.TerminateStartupTest()
    if macho.IsResurrectedNode():
        log.general.Log('I am a resurrected proxy', log.LGNOTICE)
        currentWaitTime = 0
        while len(macho.transportIDbySolNodeID) == 0:
            blue.pyos.synchro.SleepWallclock(RESSURECTED_MESH_SLEEP_DURATION_MS)
            currentWaitTime += RESSURECTED_MESH_SLEEP_DURATION_MS
            if currentWaitTime >= RESSURECTED_MESH_LOG_PERIOD_MS:
                log.general.Log('Waiting for a Sol to contact me in order to bootstrap the mesh', log.LGWARN)
                currentWaitTime = 0

        log.general.Log('Got a connection from a Sol, waiting for connectivity to be established', log.LGNOTICE)
        connectionProperties = macho.ConnectToRemoteService('machoNet', macho.transportIDbySolNodeID.keys()[0], macho.session).GetConnectionProperties()
        log.general.Log('Got cluster connection state: %s proxies and %s sols' % (connectionProperties['proxies'], connectionProperties['servers'] + 1), log.LGNOTICE)
        currentWaitTime = 0
        while len(macho.transportIDbySolNodeID) + len(macho.transportIDbyProxyNodeID) != connectionProperties['proxies'] + connectionProperties['servers']:
            blue.pyos.synchro.SleepWallclock(RESSURECTED_MESH_SLEEP_DURATION_MS)
            currentWaitTime += RESSURECTED_MESH_SLEEP_DURATION_MS
            if currentWaitTime >= RESSURECTED_MESH_LOG_PERIOD_MS:
                currentWaitTime = 0
                connectionProperties = macho.ConnectToRemoteService('machoNet', macho.transportIDbySolNodeID.keys()[0], macho.session).GetConnectionProperties()
                log.general.Log('Waiting for full mesh, current: %s/%s proxies and %s/%s sols' % (len(macho.transportIDbyProxyNodeID),
                 connectionProperties['proxies'] - 1,
                 len(macho.transportIDbySolNodeID),
                 connectionProperties['servers'] + 1), log.LGWARN)

        polarisNodeID = macho.ConnectToRemoteService('machoNet', macho.transportIDbySolNodeID.keys()[0], macho.session).GetNodeFromAddress(const.cluster.SERVICE_POLARIS, 0)
        log.general.Log('Got Polaris nodeID %s' % polarisNodeID, log.LGNOTICE)
        log.general.Log('Full mesh ok. Injecting OnClusterStarting to myself now', log.LGNOTICE)
        sm.ScatterEvent('OnClusterStarting', polarisNodeID)


def StartProxy(servicesToRun, servicesToBlock = [], startInline = [], serviceManagerClass = 'ServiceManager'):
    import blue
    blue.pyos.CreateTasklet(Startup, (servicesToRun,
     servicesToBlock,
     startInline,
     serviceManagerClass), {})