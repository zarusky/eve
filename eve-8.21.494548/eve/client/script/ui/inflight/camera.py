#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/ui/inflight/camera.py
import mathUtil
import blue
import service
import trinity
import uthread
import state
import destiny
import geo2
import uiconst
import localization
from math import sin, cos, acos, pi, asin, atan, fmod, isnan
from mapcommon import ZOOM_MIN_STARMAP, ZOOM_MAX_STARMAP, ZOOM_NEAR_SYSTEMMAP, ZOOM_FAR_SYSTEMMAP
SIZEFACTOR = 1e-07
FREELOOK_KEYS = 'WASDRF'

class CameraTarget(object):

    def __init__(self, camera, target = 'parent'):
        self._translationCurve = None
        self._camera = camera
        self._translAttrib = target
        self.SetTranslationCurve(camera.parent)

    def SetTranslationCurve(self, curve):
        self._translationCurve = curve
        if self._camera is not None:
            setattr(self._camera, self._translAttrib, curve)

    def GetTranslationCurve(self):
        return self._translationCurve

    def SetTranslation(self, value):
        if self._translationCurve is None:
            self.SetTranslationCurve(trinity.EveSO2ModelCenterPos())
        self._translationCurve.value.SetXYZ(*value)

    def GetTranslation(self):
        curve = self.GetTranslationCurve()
        if curve is None:
            return (0, 0, 0)
        if hasattr(curve, 'value'):
            if hasattr(curve.value, 'x'):
                return (curve.value.x, curve.value.y, curve.value.z)
            return curve.value
        return (curve.x, curve.y, curve.z)

    def SetParent(self, parent):
        if hasattr(self._translationCurve, 'parent'):
            self._translationCurve.parent = parent

    def GetParent(self):
        return getattr(self._translationCurve, 'parent', None)

    def SetCamera(self, camera):
        self._camera = camera
        self.SetTranslationCurve(self._translationCurve)

    def GetCamera(self):
        return self._camera

    translation = property(GetTranslation, SetTranslation)
    translationCurve = property(GetTranslationCurve, SetTranslationCurve)
    parent = property(GetParent, SetParent)


class CameraMgr(service.Service):
    __guid__ = 'svc.camera'
    __update_on_reload__ = 0
    __notifyevents__ = ['OnSpecialFX',
     'DoBallClear',
     'DoBallRemove',
     'OnSessionChanged',
     'OnSetDevice']
    __startupdependencies__ = ['settings']

    def __init__(self):
        service.Service.__init__(self)
        self.freeLook = False
        self.clientToolsScene = None
        self.checkDistToEgoThread = None
        self.maxLookatRange = 100000.0
        self.tracking = None
        self.previousTracking = None
        self.oldTracking = None
        self.tiltX = 0
        self.tiltY = 0
        self.trackerRunning = False
        self.chaseCam = False
        self.lockedCamVector = None
        self.trackingPointX, self.trackingPointY = settings.char.ui.Get('tracking_cam_location', (uicore.desktop.width / 2 * 0.8, uicore.desktop.height / 2 * 0.8))
        self.lastTime = blue.os.GetWallclockTime()
        self.trackSwitchTime = blue.os.GetWallclockTime()
        self.cameraParents = {}

    def Run(self, *args):
        self.Reset()
        self.pending = None
        self.busy = None

    def Stop(self, stream):
        self.Cleanup()

    def DoBallClear(self, solitem):
        if self.IsFreeLook():
            self.SetFreeLook(False)
        cameraParent = self.GetCameraParent()
        if cameraParent is not None:
            cameraParent.parent = None

    def DoBallRemove(self, ball, slimItem, terminal):
        if session.shipid is not None:
            lookingAtID = self.LookingAt()
            if lookingAtID is not None and ball.id == lookingAtID:
                uthread.new(self.AdjustLookAtTarget, ball)

    def AdjustLookAtTarget(self, ball):
        if session.shipid is not None:
            cameraParent = self.GetCameraParent()
            lookingAtID = self.LookingAt()
            if cameraParent and cameraParent.parent and cameraParent.parent == ball.model:
                if self.IsFreeLook():
                    self.SetFreeLook(False)
                cameraParent.parent = None
            if lookingAtID and ball.id == lookingAtID and lookingAtID != session.shipid:
                self.LookAt(session.shipid)

    def OnSpecialFX(self, shipID, moduleID, moduleTypeID, targetID, otherTypeID, area, guid, isOffensive, start, active, duration = -1, repeat = None, startTime = None, graphicInfo = None):
        if guid == 'effects.Warping' and shipID == eve.session.shipid:
            if self.IsFreeLook():
                self.SetFreeLook(False)
            self.LookAt(eve.session.shipid)

    def OnSetDevice(self, *args):
        if session.stationid:
            return
        camera = sm.GetService('sceneManager').GetRegisteredCamera('default')
        blue.synchro.Yield()
        self.boundingBoxCache = {}
        if camera is not None:
            camera.translationFromParent = self.CheckTranslationFromParent(camera.translationFromParent)

    def OnSessionChanged(self, isRemote, sess, change):
        if 'locationid' in change.iterkeys():
            if self.IsFreeLook():
                self.SetFreeLook(False)

    def Cleanup(self):
        pass

    def Reset(self):
        self.inited = 0
        self.lookingAt = None
        self.ssitems = {}
        self.boundingBoxCache = {}
        self.solarsystem = None
        self.rangeCircles = None
        self.currentSolarsystemID = None
        self.solarsystemSunID = None
        self.current = None
        self.flareData = None
        self.hiddenSpaceObjects = {}
        self.lastInflightLookat = None
        self.zoomFactor = None
        self.ssbracketsLoaded = False
        self.rangeNumberShader = None
        self.viewlevels = ['default', 'systemmap', 'starmap']
        self.mmUniverse = (-100.0, -20000.0)
        self.mmRegion = (-100.0, -20000.0)
        self.mmConstellation = (-100.0, -20000.0)
        self.mmSolarsystem = (-1000.0, -300000.0)
        self.mmTactical = (-500.0, -700000.0)
        self.mmSpace = (-30.0, -1000000.0)
        tm = sm.GetService('tactical').GetMain()
        if tm:
            for each in tm.children[:]:
                if each.name in ('camerastate', 'camlevels'):
                    each.Close()

        st = uicore.layer.station
        if st:
            for each in st.children[:]:
                if each.name in ('camerastate', 'camlevels'):
                    each.Close()

        self.freeLook = False
        self.drawAxis = True
        self.gridEnabled = True
        self.gridSpacing = 1000.0
        self.gridLength = 20000.0

    def Zoom(self, direction = 1):
        pass

    def SetCameraInterest(self, itemID):
        if self.freeLook:
            return
        cameraInterest = self.GetCameraInterest()
        camera = sm.GetService('sceneManager').GetRegisteredCamera('default')
        if camera is None:
            return
        if itemID is None:
            cameraInterest.translationCurve = None
            return
        item = sm.StartService('michelle').GetBall(itemID)
        if item is None or getattr(item, 'model', None) is None:
            cameraInterest.translationCurve = None
            return
        tracker = None
        if item.model.__bluetype__ in ('trinity.EveShip2', 'trinity.EveStation2', 'trinity.EveRootTransform'):
            tracker = trinity.EveSO2ModelCenterPos()
            tracker.parent = item.model
        if tracker:
            cameraInterest.translationCurve = tracker
        else:
            cameraInterest.translationCurve = item

    def SetCameraParent(self, itemID):
        if self.freeLook:
            return
        cameraParent = self.GetCameraParent()
        if cameraParent is None:
            return
        item = sm.StartService('michelle').GetBall(itemID)
        if item is None or getattr(item, 'model', None) is None:
            self.LookAt(eve.session.shipid)
            return
        tracker = None
        if item.model.__bluetype__ in ('trinity.EveShip2', 'trinity.EveStation2', 'trinity.EveRootTransform'):
            tracker = trinity.EveSO2ModelCenterPos()
            tracker.parent = item.model
        camera = sm.GetService('sceneManager').GetRegisteredCamera('default')
        if camera is None:
            return
        if tracker:
            cameraParent.translationCurve = tracker
        else:
            cameraParent.translationCurve = item

    def _CheckDistanceToEgo(self):
        while self.checkDistToEgoThread is not None:
            if self.lookingAt is not None:
                lookingAtItem = sm.GetService('michelle').GetBall(self.lookingAt)
                if lookingAtItem.surfaceDist > self.maxLookatRange:
                    self.ResetCamera()
                    self.checkDistToEgoThread = None
            blue.synchro.Sleep(1000)

    def LookAt(self, itemID, setZ = None, ignoreDist = 0, resetCamera = False, smooth = True):
        if itemID != session.shipid:
            self.TrackItem(None)
        item = sm.StartService('michelle').GetBall(itemID)
        if item is None or getattr(item, 'model', None) is None:
            if hasattr(item, 'loadingModel'):
                while item.loadingModel:
                    blue.synchro.Yield()

        if self.IsFreeLook():
            self.GetCameraParent().translation = (item.x, item.y, item.z)
            return
        obs = sm.GetService('target').IsObserving()
        scene = sm.GetService('sceneManager').GetRegisteredScene('default')
        if scene:
            if itemID != eve.session.shipid:
                if scene.dustfield is not None:
                    scene.dustfield.display = 0
                if item.mode == destiny.DSTBALL_WARP:
                    return
                if not (ignoreDist or obs) and item.surfaceDist > self.maxLookatRange:
                    uicore.Say(localization.GetByLabel('UI/Camera/OutsideLookingRange'))
                    return
            elif scene.dustfield is not None:
                scene.dustfield.display = 1
            uthread.pool('MenuSvc>LookAt', self._LookAt, item, itemID, setZ, resetCamera, smooth)
            if itemID != eve.session.shipid:
                if self.checkDistToEgoThread is None:
                    self.checkDistToEgoThread = uthread.pool('MenuSvc>checkDistToEgoThread', self._CheckDistanceToEgo)
            else:
                self.checkDistToEgoThread = None

    def _LookAt(self, item, itemID, setZ, resetCamera, smooth):
        if not item:
            return
        if item.GetModel() is None:
            return
        camera = sm.GetService('sceneManager').GetRegisteredCamera('default')
        if camera is None:
            return
        camera.interest = None
        self.GetCameraInterest().translationCurve = None
        cameraParent = self.GetCameraParent()
        if cameraParent is None:
            return
        sm.StartService('state').SetState(itemID, state.lookingAt, 1)
        self.lookingAt = itemID
        item.LookAtMe()
        if cameraParent.translationCurve is not None:
            startPos = cameraParent.translationCurve.GetVectorAt(blue.os.GetSimTime())
            startPos = (startPos.x, startPos.y, startPos.z)
            cameraParent.translationCurve = None
        else:
            startPos = cameraParent.translation
        startFov = camera.fieldOfView
        if resetCamera:
            endFov = sm.GetService('sceneManager').maxFov
        else:
            endFov = camera.fieldOfView
        if setZ is None:
            startTrZ = camera.translationFromParent
            endTrZ = self.CheckTranslationFromParent(1.0)
        elif setZ < 0.0:
            camera.translationFromParent = 2.0 * self.CheckTranslationFromParent(setZ)
            startTrZ = None
            endTrZ = None
        else:
            camera.translationFromParent = self.CheckTranslationFromParent(setZ)
            startTrZ = None
            endTrZ = None
        start = blue.os.GetWallclockTime()
        ndt = 0.0
        time = 500.0
        tracker = None
        tempTF = None
        if item.model.__bluetype__ in ('trinity.EveShip2', 'trinity.EveStation2', 'trinity.EveRootTransform'):
            tracker = trinity.EveSO2ModelCenterPos()
            tracker.parent = item.model
        while ndt != 1.0 and smooth:
            ndt = max(0.0, min(blue.os.TimeDiffInMs(start, blue.os.GetWallclockTime()) / time, 1.0))
            if tracker is None:
                break
            if hasattr(tracker.parent, 'modelWorldPosition'):
                endPos = tracker.parent.modelWorldPosition
            elif getattr(item.model, 'translationCurve', None) is not None:
                endPos = item.model.translationCurve.GetVectorAt(blue.os.GetSimTime())
                endPos = (endPos.x, endPos.y, endPos.z)
            else:
                endPos = item.model.translation
            if startPos and endPos:
                cameraParent.translation = geo2.Vec3Lerp(startPos, endPos, ndt)
            if startTrZ and endTrZ:
                if endTrZ > startTrZ or resetCamera:
                    camera.translationFromParent = mathUtil.Lerp(startTrZ, endTrZ, ndt)
            if startFov != endFov:
                camera.fieldOfView = mathUtil.Lerp(startFov, endFov, ndt)
            blue.pyos.synchro.Yield()

        if tracker:
            cameraParent.translationCurve = tracker
        else:
            cameraParent.translationCurve = item
        if self.current == 'default':
            self.lastInflightLookat = [itemID, camera.translationFromParent]

    def CalcAngle(self, x, y):
        angle = 0
        if x != 0:
            angle = atan(y / x)
            if x < 0 and y >= 0:
                angle = atan(y / x) + pi
            if x < 0 and y < 0:
                angle = atan(y / x) - pi
        else:
            if y > 0:
                angle = pi / 2
            if y < 0:
                angle = -pi / 2
        return angle

    def ToggleChaseCam(self, lockCurrent = False):
        if lockCurrent:
            camera = sm.GetService('sceneManager').GetRegisteredCamera('default')
            self.lockedCamVector = camera.viewVec
            shipBall = sm.GetService('michelle').GetBall(self.lookingAt)
            if shipBall is not None and shipBall.model is not None:
                q = shipBall.model.rotationCurve.GetQuaternionAt(blue.os.GetSimTime())
                q = geo2.QuaternionInverse((q.x,
                 q.y,
                 q.z,
                 q.w))
                v = self.lockedCamVector
                self.lockedCamVector = geo2.QuaternionTransformVector(q, v)
        else:
            self.lockedCamVector = None
        self.chaseCam = not self.chaseCam

    def TrackItem(self, itemID):
        if itemID == self.lookingAt:
            return
        camera = sm.GetService('sceneManager').GetRegisteredCamera('default')
        if camera is None:
            return
        if itemID == None and self.tracking is not None:
            self.previousTracking = None
            self.chaseCam = False
            camera.maxPitch = self.camMaxPitch
            camera.minPitch = self.camMinPitch
            camera.rotationOfInterest = geo2.QuaternionIdentity()
            self.tiltX = 0
            self.tiltY = 0
        if self.trackerRunning and itemID is not None:
            camera.maxPitch = 2 * pi
            camera.minPitch = -2 * pi
        self.tracking = itemID
        if not self.trackerRunning:
            self.camMaxPitch = camera.maxPitch
            self.camMinPitch = camera.minPitch
            self.job = trinity.CreateRenderJob()
            self.job.PythonCB(self._TrackItem)
            self.job.ScheduleRecurring()

    def _TrackItem(self):
        self.trackerRunning = True
        if sm.GetService('viewState').GetCurrentView().name != 'inflight':
            return
        tx, ty = pos = settings.char.ui.Get('tracking_cam_location', (uicore.desktop.width / 2, uicore.desktop.height / 2))
        if tx > uicore.desktop.width:
            self.trackingPointX = 0.9 * uicore.desktop.width
        if ty > uicore.desktop.height:
            self.trackingPointY = 0.9 * uicore.desktop.height
        if self.chaseCam or self.tracking is not None:
            self.PointCameraTo(self.tracking, pi / 1500)
        else:
            self.lastTime = blue.os.GetWallclockTime()

    def ToggleCenterTrackingPoint(self, on):
        camera = sm.GetService('sceneManager').GetRegisteredCamera('default')
        if camera is None:
            return
        middle = uicore.desktop.width / 2
        centerX, centerY = middle * (1 - camera.centerOffset), uicore.desktop.height / 2
        if not on:
            self.trackingPointX, self.trackingPointY = settings.char.ui.Get('tracking_cam_location', (centerX * 0.8, centerY * 0.8))
        else:
            self.trackingPointX, self.trackingPointY = centerX, centerY
        self.retrack = True

    def SetTrackingPoint(self, x, y):
        self.trackingPointX = x
        self.trackingPointY = y

    def PointCameraTo(self, itemID, panSpeed = pi / 500, retrack = False):
        timeDelta = max(blue.os.TimeDiffInMs(self.lastTime, blue.os.GetWallclockTime()), 16)
        self.lastTime = blue.os.GetWallclockTime()
        camera = sm.GetService('sceneManager').GetRegisteredCamera('default')
        if camera is None:
            return
        shipBall = sm.GetService('michelle').GetBall(self.lookingAt)
        if shipBall is None:
            return
        itemBall = sm.GetService('michelle').GetBall(itemID)
        if not itemBall:
            return
        try:
            if itemBall.exploded:
                return
        except:
            return

        if itemBall.IsCloaked():
            return
        maxDistance = shipBall.radius * 150
        if camera.translationFromParent > maxDistance:
            if self.oldTracking != self.tracking:
                camera.translationFromParent -= 100 + (camera.translationFromParent - maxDistance) / 10
            else:
                return
        else:
            self.oldTracking = self.tracking
        shipPos = shipBall.GetVectorAt(blue.os.GetSimTime())
        m, h = uicore.desktop.width / 2, uicore.desktop.height
        center = trinity.TriVector(m * (1 - camera.centerOffset), h / 2, 0)
        itemPos = itemBall.GetVectorAt(blue.os.GetSimTime())
        v2 = shipPos - itemPos
        dx2 = center.x - self.trackingPointX
        dy2 = center.y - self.trackingPointY
        v2.Normalize()
        yzProj = trinity.TriVector(0, v2.y, v2.z)
        zxProj = trinity.TriVector(v2.x, 0, v2.z)
        yaw = self.CalcAngle(zxProj.z, zxProj.x)
        pitch = -asin(yzProj.y)
        oldYaw = camera.yaw
        oldPitch = camera.pitch
        alphaX = pi * dx2 * camera.fieldOfView / uicore.desktop.width
        alphaY = pi * dy2 * camera.fieldOfView / uicore.desktop.width
        dPitchTotal = pitch - camera.pitch
        dYawTotal = (yaw - camera.yaw) % (2 * pi) - alphaX * 0.75
        dPitchTotal = min(2 * pi - dPitchTotal, dPitchTotal) - alphaY * 0.75
        if dYawTotal > pi:
            dYawTotal = -(2 * pi - dYawTotal)
        arc = geo2.Vec2Length((dYawTotal, dPitchTotal))
        if self.previousTracking != self.tracking or self.retrack:
            self.retrack = False
            self.trackSwitchTime = blue.os.GetWallclockTime()
            self.previousTracking = self.tracking
        t = blue.os.GetWallclockTime()
        rampUp = 1
        timeSinceTargetChange = 0
        if t > self.trackSwitchTime:
            timeSinceTargetChange = min(float(blue.os.TimeDiffInMs(self.trackSwitchTime, t)), 5000.0)
            rampUp = min(timeSinceTargetChange / 2000.0, 1.0)
            panSpeed = pi / 500 * rampUp
        part = min(1, timeDelta * panSpeed)
        dYawPart = dYawTotal * part
        dPitchPart = dPitchTotal * part
        arcPart = geo2.Vec2Length((dYawPart, dPitchPart))
        Yaw = oldYaw + dYawPart
        Pitch = oldPitch + dPitchPart
        camera.SetOrbit(Yaw, Pitch)
        br = sm.GetService('bracket')
        itemBracket = br.GetBracket(itemID)
        if not self.chaseCam and itemBracket and itemBracket not in br.overlaps:
            if itemBracket.renderObject is not None and itemBracket.renderObject.display:
                dx = self.trackingPointX - itemBracket.renderObject.displayX
                dy = self.trackingPointY - itemBracket.renderObject.displayY
                dist = geo2.Vec2Length((dx, dy))
                tiltBrake = 25000 + 1000000 * pow(arc, 2) * (1 - min(timeSinceTargetChange / 5000, 1))
                tdx = min(round(dx / tiltBrake, 4), 0.005)
                tdy = min(round(dy / tiltBrake, 4), 0.005)
                tiltAngle = geo2.Vec2Length((tdx, tdy))
                if tiltAngle > 0.0005:
                    self.tiltX += tdx
                    self.tiltY += tdy
                    self.tiltX = fmod(self.tiltX, pi * 2)
                    self.tiltY = fmod(self.tiltY, pi * 2)
                    camera.SetRotationOnOrbit(self.tiltX, self.tiltY)

    def PanCamera(self, posbeg = None, posend = None, cambeg = None, camend = None, time = 500.0, thread = 1, fovEnd = None, source = 'default'):
        if self.IsFreeLook():
            return
        if thread:
            uthread.new(self._PanCamera, posbeg, posend, cambeg, camend, fovEnd, time, source)
        else:
            self._PanCamera(posbeg, posend, cambeg, camend, fovEnd, time, source)

    def _PanCamera(self, posbeg = None, posend = None, cambeg = None, camend = None, fovEnd = None, time = 500.0, source = 'default'):
        cameraParent = self.GetCameraParent(source)
        if cameraParent is None:
            return
        start = blue.os.GetWallclockTime()
        ndt = 0.0
        fovBeg = None
        camera = sm.GetService('sceneManager').GetRegisteredCamera(source)
        if camera is None:
            return
        if fovEnd is not None:
            fovBeg = camera.fieldOfView
        while ndt != 1.0:
            ndt = max(0.0, min(blue.os.TimeDiffInMs(start, blue.os.GetWallclockTime()) / time, 1.0))
            if posbeg and posend:
                cameraParent.translation.x = mathUtil.Lerp(posbeg.x, posend.x, ndt)
                cameraParent.translation.y = mathUtil.Lerp(posbeg.y, posend.y, ndt)
                cameraParent.translation.z = mathUtil.Lerp(posbeg.z, posend.z, ndt)
            if cambeg and camend:
                camera.translationFromParent = self.CheckTranslationFromParent(mathUtil.Lerp(cambeg, camend, ndt), source=source)
            if fovBeg and fovEnd:
                camera.fieldOfView = mathUtil.Lerp(fovBeg, fovEnd, ndt)
            blue.pyos.synchro.Yield()

    def ClearCameraParent(self, source = 'default'):
        cameraParent = self.cameraParents.get(source, None)
        if cameraParent is None:
            return
        cameraParent.translationCurve = None
        del self.cameraParents[source]

    def GetCameraParent(self, source = 'default'):
        sceneManager = sm.services.get('sceneManager', None)
        if sceneManager is None or sceneManager.state != service.SERVICE_RUNNING:
            return
        camera = sceneManager.GetRegisteredCamera(source)
        if camera is None:
            return
        cameraParent = self.cameraParents.get(source, None)
        if cameraParent is None:
            cameraParent = CameraTarget(camera)
            self.cameraParents[source] = cameraParent
        return cameraParent

    def GetCameraInterest(self, source = 'default'):
        cameraInterest = getattr(self, 'cameraInterest_%s' % source, None)
        if cameraInterest is None:
            camera = sm.GetService('sceneManager').GetRegisteredCamera(source)
            cameraInterest = CameraTarget(camera, 'interest')
            setattr(self, 'cameraInterest_%s' % source, cameraInterest)
        return cameraInterest

    def ResetCamera(self, *args):
        self.LookAt(eve.session.shipid, resetCamera=True)

    def LookingAt(self):
        return getattr(self, 'lookingAt', eve.session.shipid)

    def GetTranslationFromParentForItem(self, itemID, fov = None):
        camera = sm.GetService('sceneManager').GetRegisteredCamera('default')
        if camera is None:
            return
        if fov is None:
            fov = camera.fieldOfView
        ballpark = sm.GetService('michelle').GetBallpark()
        if ballpark:
            ball = ballpark.GetBall(itemID)
            if ball and ball.model:
                rad = None
                if ball.model.__bluetype__ in ('eve.EveShip', 'eve.EveStation', 'trinity.EveShip2', 'trinity.EveStation2', 'trinity.EveRootTransform'):
                    rad = ball.model.GetBoundingSphereRadius()
                    zoomMultiplier = 1.0
                    aspectRatio = trinity.GetAspectRatio()
                    if aspectRatio > 1.6:
                        zoomMultiplier = aspectRatio / 1.6
                    return (rad + camera.frontClip) * zoomMultiplier + 2
                if hasattr(ball.model, 'children'):
                    if ball.model.children:
                        rad = ball.model.children[0].GetBoundingSphereRadius()
                if not rad or rad <= 0.0:
                    rad = ball.radius
                camangle = camera.fieldOfView * 0.5
                return max(15.0, rad / sin(camangle) * cos(camangle))

    def CheckTranslationFromParent(self, distance, getMinMax = 0, source = 'default'):
        if source == 'starmap':
            mn, mx = ZOOM_MIN_STARMAP, ZOOM_MAX_STARMAP
        elif source == 'systemmap':
            mn, mx = ZOOM_NEAR_SYSTEMMAP, ZOOM_FAR_SYSTEMMAP
            aspectRatio = trinity.device.viewport.GetAspectRatio()
            if aspectRatio > 1.6:
                mx = mx * aspectRatio / 1.6
        else:
            lookingAt = self.LookingAt() or eve.session.shipid
            mn = 10.0
            if lookingAt not in self.boundingBoxCache:
                mn = self.GetTranslationFromParentForItem(lookingAt)
                if mn is not None:
                    self.boundingBoxCache[lookingAt] = mn
            else:
                mn = self.boundingBoxCache[lookingAt]
            mn, mx = mn, 1000000.0
        retval = max(mn, min(distance, mx))
        if getMinMax:
            return (retval, mn, mx)
        self.RegisterCameraTranslation(retval, source)
        return retval

    def ClearBoundingInfoForID(self, id):
        if id in self.boundingBoxCache:
            del self.boundingBoxCache[id]

    def RegisterCameraTranslation(self, tr, source):
        settings.user.ui.Set('%sTFP' % source, tr)
        if source == 'default' and getattr(self, 'lastInflightLookat', None):
            self.lastInflightLookat[1] = tr

    def IsFreeLook(self):
        return self.freeLook

    def SetFreeLook(self, freeLook = True):
        if self.freeLook == freeLook:
            return
        self.freeLook = freeLook
        camera = sm.GetService('sceneManager').GetRegisteredCamera(None, defaultOnActiveCamera=True)
        if camera is None:
            return
        if freeLook:
            cameraParent = self.GetCameraParent()
            cameraParent.translationCurve = None
            self.axisLines = trinity.Tr2LineSet()
            self.axisLines.effect = trinity.Tr2Effect()
            self.axisLines.effect.effectFilePath = 'res:/Graphics/Effect/Managed/Utility/LinesWithZ.fx'
            self.clientToolsScene = self.GetClientToolsScene()
            self.clientToolsScene.primitives.append(self.axisLines)
            self._ChangeCamPos(cameraParent.translation)
            self.BuildGridAndAxes()
            uthread.new(self._UpdateFreelookCamera)
        else:
            self.ResetCamera()
            try:
                self.clientToolsScene.primitives.remove(self.axisLines)
            except ValueError:
                pass

            self.axisLines = None

    def IsDrawingAxis(self):
        return self.drawAxis

    def SetDrawAxis(self, enabled = True):
        self.drawAxis = enabled

    def IsGridEnabled(self):
        return self.gridEnabled

    def SetGridState(self, enabled = True):
        self.gridEnabled = enabled

    def GetGridSpacing(self):
        return self.gridSpacing

    def SetGridSpacing(self, spacing = 100.0):
        if self.gridLength / spacing > 200:
            spacing = self.gridLength / 200
        elif self.gridLength / spacing <= 1:
            spacing = self.gridLength / 20
        if spacing < 1.0:
            spacing = 1.0
        self.gridSpacing = spacing
        self.BuildGridAndAxes()

    def GetGridLength(self):
        return self.gridLength

    def SetGridLength(self, length = 100.0):
        if length / self.gridSpacing > 200:
            self.gridSpacing = length / 200
        elif length / self.gridSpacing <= 1:
            self.gridSpacing = length / 20
        if length < 1.0:
            length = 1.0
        self.gridLength = length
        self.BuildGridAndAxes()

    def BuildGridAndAxes(self):
        if self.axisLines is None:
            return
        self.axisLines.ClearLines()
        self.axisLines.SubmitChanges()
        if self.IsDrawingAxis():
            red = (1, 0, 0, 1)
            green = (0, 1, 0, 1)
            blue = (0, 0, 1, 1)
            xAxis = (100.0, 0.0, 0.0)
            yAxis = (0.0, 100.0, 0.0)
            zAxis = (0.0, 0.0, 100.0)
            origin = (0.0, 0.0, 0.0)
            self.axisLines.AddLine(origin, red, xAxis, red)
            self.axisLines.AddLine(origin, green, yAxis, green)
            self.axisLines.AddLine(origin, blue, zAxis, blue)
        if self.IsGridEnabled():
            grey = (0.4, 0.4, 0.4, 0.5)
            lightGrey = (0.5, 0.5, 0.5, 0.5)
            offWhite = (1, 1, 1, 0.8)
            minGridPos = -self.gridLength / 2.0
            maxGridPos = self.gridLength / 2.0
            halfNumSquares = int(self.gridLength / self.gridSpacing) / 2
            for i in xrange(-halfNumSquares, halfNumSquares + 1):
                color = grey
                if i % 10 == 0:
                    color = lightGrey
                if i % 20 == 0:
                    color = offWhite
                gridPos = i * self.gridSpacing
                startZ = (gridPos, 0.0, minGridPos)
                endZ = (gridPos, 0.0, maxGridPos)
                startX = (minGridPos, 0.0, gridPos)
                endX = (maxGridPos, 0.0, gridPos)
                if i != 0 or not self.drawAxis:
                    self.axisLines.AddLine(startZ, color, endZ, color)
                    self.axisLines.AddLine(startX, color, endX, color)
                else:
                    self.axisLines.AddLine(startZ, color, origin, color)
                    self.axisLines.AddLine(zAxis, color, endZ, color)
                    self.axisLines.AddLine(startX, color, origin, color)
                    self.axisLines.AddLine(xAxis, color, endX, color)

            color = offWhite
            startZ = (minGridPos, 0.0, minGridPos)
            endZ = (minGridPos, 0.0, maxGridPos)
            startX = (minGridPos, 0.0, minGridPos)
            endX = (maxGridPos, 0.0, minGridPos)
            self.axisLines.AddLine(startZ, color, endZ, color)
            self.axisLines.AddLine(startX, color, endX, color)
            startZ = (maxGridPos, 0.0, minGridPos)
            endZ = (maxGridPos, 0.0, maxGridPos)
            startX = (minGridPos, 0.0, maxGridPos)
            endX = (maxGridPos, 0.0, maxGridPos)
            self.axisLines.AddLine(startZ, color, endZ, color)
            self.axisLines.AddLine(startX, color, endX, color)
        self.axisLines.SubmitChanges()

    def _ChangeCamPos(self, vec):
        camParent = self.GetCameraParent()
        transl = camParent.translation
        camParent.translation = geo2.Vec3Add(transl, vec)

    def _UpdateFreelookCamera(self):
        lastTime = blue.os.GetSimTime()
        while self.IsFreeLook():
            camera = sm.GetService('sceneManager').GetRegisteredCamera(None, defaultOnActiveCamera=True)
            if camera is not None:
                delta = blue.os.TimeDiffInMs(lastTime, blue.os.GetSimTime())
                keyDown = uicore.uilib.Key
                if keyDown(uiconst.VK_CONTROL) and not keyDown(uiconst.VK_MENU) and not keyDown(uiconst.VK_SHIFT):
                    if keyDown(uiconst.VK_W):
                        self._ChangeCamPos(geo2.Vec3Scale(camera.viewVec, -delta))
                    if keyDown(uiconst.VK_S):
                        self._ChangeCamPos(geo2.Vec3Scale(camera.viewVec, delta))
                    if keyDown(uiconst.VK_A):
                        self._ChangeCamPos(geo2.Vec3Scale(camera.rightVec, -delta))
                    if keyDown(uiconst.VK_D):
                        self._ChangeCamPos(geo2.Vec3Scale(camera.rightVec, delta))
                    if keyDown(uiconst.VK_R):
                        self._ChangeCamPos(geo2.Vec3Scale(camera.upVec, delta))
                    if keyDown(uiconst.VK_F):
                        self._ChangeCamPos(geo2.Vec3Scale(camera.upVec, -delta))
                self.axisLines.localTransform = geo2.MatrixTranslation(*self.GetCameraParent().translation)
            lastTime = blue.os.GetSimTime()
            blue.synchro.Yield()

    def GetClientToolsScene(self):
        if self.clientToolsScene is not None:
            return self.clientToolsScene
        renderManager = sm.GetService('sceneManager')
        rj = renderManager.fisRenderJob
        scene = rj.GetClientToolsScene()
        if scene is not None:
            self.clientToolsScene = scene
            return self.clientToolsScene
        self.clientToolsScene = trinity.Tr2PrimitiveScene()
        rj.SetClientToolsScene(self.clientToolsScene)
        return self.clientToolsScene

    def ShakeCamera(self, magnitude, position):
        if not settings.user.ui.Get('cameraShakeEnabled', 1):
            return
        camera = sm.StartService('sceneManager').GetRegisteredCamera('default')
        timeFactor = pow(magnitude / 400.0, 0.7)
        noiseScaleCurve = trinity.TriScalarCurve()
        noiseScaleCurve.AddKey(0.0, 1.2, 0.0, 0.0, 3)
        noiseScaleCurve.AddKey(0.1, 0.1, 0.0, 0.0, 3)
        noiseScaleCurve.AddKey(1.5 * timeFactor, 0.13, 0.0, 0.0, 3)
        noiseScaleCurve.AddKey(2.0 * timeFactor, 0.0, 0.0, 0.0, 3)
        noiseScaleCurve.extrapolation = 1
        noiseDampCurve = trinity.TriScalarCurve()
        noiseDampCurve.AddKey(0.0, 80.0, 0.0, 0.0, 3)
        noiseDampCurve.AddKey(0.1, 20.0, 0.0, 0.0, 3)
        noiseDampCurve.AddKey(1.5 * timeFactor, 0.0, 0.0, 0.0, 3)
        noiseDampCurve.AddKey(2.0 * timeFactor, 0.0, 0.0, 0.0, 3)
        noiseDampCurve.extrapolation = 1
        newPos = geo2.Vec3Subtract(position, camera.pos)
        distance = geo2.Vec3Length(newPos)
        if isnan(distance):
            raise RuntimeError('Camera::ShakeCamera invalid(nan) distance from camera to shake position.')
        elif distance < 700.0:
            distance = 700.0
        elif distance > 2000000000:
            distance = 2000000000
        actualMagnitude = 0.7 * magnitude / pow(distance, 0.7)
        noiseScaleCurve.ScaleValue(actualMagnitude)
        noiseDampCurve.ScaleValue(actualMagnitude)
        if camera.noiseScaleCurve != None and camera.noiseScaleCurve.value > noiseScaleCurve.keys[1].value:
            return
        now = blue.os.GetSimTime()
        noiseScaleCurve.start = now
        noiseDampCurve.start = now
        camera.noise = 1
        camera.noiseScaleCurve = noiseScaleCurve
        camera.noiseDampCurve = noiseDampCurve