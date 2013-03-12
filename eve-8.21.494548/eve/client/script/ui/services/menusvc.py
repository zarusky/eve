#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/ui/services/menusvc.py
import sys
import uix
import uiutil
import uthread
import util
import dbutil
import log
import blue
import menu
import form
import xtriui
import moniker
import service
import destiny
import chat
import types
import state
import trinity
import base
import fleetcommon
import math
import uiconst
import copy
import pos
import uicls
import entities
import login
import localization
import invCtrl
from collections import defaultdict
import telemetry
import foo
import geo2
import random
import spaceObject
import crimewatchConst
UNLOAD_MINIBALLS = 0
SHOW_RUNTIME_MINIBALL_DATA = 1
SHOW_EDITOR_MINIBALL_DATA = 2
SHOW_DESTINY_BALL = 3
SHOW_MODEL_SPHERE = 4
SHOW_BOUNDING_SPHERE = 5

def CreateMiniballObject(name, miniballs):
    t = trinity.EveRootTransform()
    sphere = blue.resMan.LoadObject('res:/Model/Global/Miniball.red')
    if len(miniballs) > 0:
        for miniball in miniballs:
            mball = sphere.CopyTo()
            mball.translation = (miniball.x, miniball.y, miniball.z)
            r = miniball.radius * 2
            mball.scaling = (r, r, r)
            t.children.append(mball)

    t.name = name
    return t


def CreateRadiusObject(name, radius):
    t = trinity.EveRootTransform()
    t.name = name
    s = blue.resMan.LoadObject('res:/model/global/gridSphere.red')
    radius = radius * 2
    s.scaling = (radius, radius, radius)
    t.children.append(s)
    return t


class MenuSvc(service.Service):
    __guid__ = 'svc.menu'
    __update_on_reload__ = 0
    __dependencies__ = ['account',
     'addressbook',
     'pvptrade',
     'LSC',
     'fleet',
     'pwn',
     'godma',
     'michelle',
     'faction',
     'manufacturing',
     'invCache',
     'viewState',
     'crimewatchSvc']
    __notifyevents__ = ['DoBallRemove', 'OnSessionChanged']
    __startupdependencies__ = ['settings']

    def Run(self, memStream = None):
        self.primedMoons = {}
        self.multiFunctions = ['UI/Inventory/ItemActions/Repackage',
         'UI/Contracts/BreakContract',
         'UI/Inventory/ItemActions/Refine',
         'UI/Inventory/ItemActions/Reprocess',
         'UI/Drones/LaunchDrones',
         'UI/Inventory/ItemActions/TrashIt',
         'UI/Inventory/ItemActions/SplitStack',
         'UI/Inventory/ItemActions/ToHangarAndRefine',
         'UI/SkillQueue/AddSkillMenu/TrainNowToLevel1',
         'UI/SkillQueue/InjectSkill',
         'UI/Inventory/ItemActions/PlugInImplant',
         'UI/Inventory/ItemActions/AssembleContainer',
         'UI/Inventory/ItemActions/OpenContainer',
         'UI/Inventory/ItemActions/AssembleShip',
         'UI/Inventory/ItemActions/FitToActiveShip',
         'UI/Commands/OpenDroneBay',
         'UI/Commands/OpenCargoHold',
         'UI/Inventory/ItemActions/LaunchForSelf',
         'UI/Inventory/ItemActions/LaunchForCorp',
         'UI/Inventory/ItemActions/Jettison',
         'take out trash',
         'UI/Drones/EngageTarget',
         'UI/Drones/MineWithDrone',
         'UI/Drones/MineRepeatedly',
         'UI/Drones/ReturnDroneAndOrbit',
         'UI/Drones/ReturnDroneToBay',
         'UI/Drones/DelegateDroneControl',
         'UI/Drones/DroneAssist',
         'UI/Drones/DroneGuard',
         'UI/Drones/ReturnDroneControl',
         'UI/Drones/AbandonDrone',
         'UI/Drones/ScoopDroneToBay',
         'UI/Inventory/ItemActions/LockItem',
         'UI/Inventory/ItemActions/UnlockItem',
         'UI/Drones/MoveToDroneBay',
         'UI/Corporations/CorporationWindow/Members/CorpMember',
         'UI/Inventory/ItemActions/CreateContract',
         'UI/Corporations/Common/AwardCorpMemberDecoration',
         'UI/EVEMail/SendPilotEVEMail',
         'UI/PeopleAndPlaces/RemoveFromAddressbook',
         'UI/PeopleAndPlaces/AddToAddressbook',
         'UI/Fleet/FormFleetWith',
         'UI/Commands/CapturePortrait',
         'UI/Inventory/ItemActions/LaunchShip',
         'UI/Inventory/ItemActions/LaunchShipFromBay',
         'UI/Inventory/ItemActions/GetRepairQuote']
        self.allReasonsDict = self.GetReasonsDict()
        self.multiFunctionFunctions = [self.DeliverToCorpHangarFolder]
        uicore.uilib.RegisterForTriuiEvents([uiconst.UI_MOUSEDOWN], self.OnGlobalMouseDown)

    def GetReasonsDict(self):
        dict = {'notInSpace': 'UI/Menusvc/MenuHints/YouAreNotInSpace',
         'notInSystem': 'UI/Menusvc/MenuHints/LocationNotInSystem',
         'notInApproachRange': 'UI/Menusvc/MenuHints/NotInApproachRange',
         'cantKeepInRange': 'UI/Menusvc/MenuHints/CannotKeepInRange',
         'notStation': 'UI/Menusvc/MenuHints/IsNotStation',
         'notStargate': 'UI/Menusvc/MenuHints/IsNotStargate',
         'notWithinMaxJumpDist': 'UI/Menusvc/MenuHints/NotWithingMaxJumpDist',
         'severalJumpDest': 'UI/Menusvc/MenuHints/SeveralJumpDestinations',
         'cantUseGate': 'UI/Menusvc/MenuHints/ShipNotAllowedToUseGate',
         'notWarpGate': 'UI/Menusvc/MenuHints/NotAccelerationGate',
         'notCloseEnoughToWH': 'UI/Menusvc/MenuHints/NotCloseEnoughToEnterWormhole',
         'notInLookingRange': 'UI/Menusvc/MenuHints/OutsideLookingRange',
         'notWithinMaxTransferRange': 'UI/Menusvc/MenuHints/NotWithinMaxTranferDistance',
         'notInTargetingRange': 'UI/Menusvc/MenuHints/NotInTargetRange',
         'notSpacePig': 'UI/Menusvc/MenuHints/IsNotAnAgent',
         'cantScoopDrone': 'UI/Menusvc/MenuHints/DroneCannotBeScooped',
         'droneNotInScooopRange': 'UI/Menusvc/MenuHints/DroneOutsideScoopRange',
         'notWithinMaxConfigRange': 'UI/Menusvc/MenuHints/NotWithinMaxConfigDist',
         'notOwnedByYouOrCorpOrAlliance': 'UI/Corporations/Common/NotOwnedByYouOrCorpOrAlliance',
         'dontControlDrone': 'UI/Menusvc/MenuHints/DoNotControlDrone',
         'droneIncapacitated': 'UI/Menusvc/MenuHints/DroneIncapacitated',
         'dontOwnDrone': 'UI/Menusvc/MenuHints/DoNotOwnDrone',
         'notInWarpRange': 'UI/Menusvc/MenuHints/NotInWarpRange',
         'inCapsule': 'UI/Menusvc/MenuHints/YouAreInCapsule',
         'inWarp': 'UI/Menusvc/MenuHints/YouAreInWarp',
         'pilotInShip': 'UI/Menusvc/MenuHints/ShipAlreadyPiloted',
         'inWarpRange': 'UI/Menusvc/MenuHints/InWarpRange',
         'beingTargeted': 'UI/Menusvc/MenuHints/BeingTargeted',
         'isMyShip': 'UI/Menusvc/MenuHints/IsYourShip',
         'isNotMyShip': 'UI/Menusvc/MenuHints/NotYourShip',
         'autopilotActive': 'UI/Menusvc/MenuHints/AutopilotActive',
         'autopilotNotActive': 'UI/Menusvc/MenuHints/AutopilotNotActive',
         'isLookingAtItem': 'UI/Menusvc/MenuHints/AlreadyLookingAtItem',
         'notLookingAtItem': 'UI/Menusvc/MenuHints/NotLookingAtItem',
         'alreadyTargeted': 'UI/Menusvc/MenuHints/AlreadyTargeted',
         'notInTargets': 'UI/Menusvc/MenuHints/NotInTargets',
         'badGroup': 'UI/Menusvc/MenuHints/BadGroupForAction',
         'thisIsNot': 'UI/Menusvc/MenuHints/ThisIsNot'}
        return dict

    def OnGlobalMouseDown(self, object, *args):
        if not uiutil.IsUnder(object, uicore.layer.menu):
            uiutil.Flush(uicore.layer.menu)
        return True

    def Stop(self, *args):
        self.expandTimer = None

    def OnSessionChanged(self, isremote, session, change):
        self.expandTimer = None
        menu.KillAllMenus()
        if 'solarsystemid' in change:
            self.PrimeMoons()

    def DoBallRemove(self, ball, slimItem, terminal):
        if ball is None:
            return
        self.LogInfo('DoBallRemove::menusvc', ball.id)
        if sm.GetService('camera').LookingAt() == ball.id and ball.id != session.shipid:
            if terminal:
                uthread.new(self.ResetCameraDelayed, ball.id)
            else:
                sm.GetService('camera').LookAt(session.shipid)

    def ResetCameraDelayed(self, id):
        blue.pyos.synchro.SleepWallclock(5000)
        if sm.GetService('camera').LookingAt() == id:
            sm.GetService('camera').LookAt(session.shipid)

    def TryExpandActionMenu(self, *args):
        if uicore.uilib.Key(uiconst.VK_MENU) or uicore.uilib.Key(uiconst.VK_CONTROL):
            return 0
        wantedBtn = settings.user.ui.Get('actionmenuBtn', 0)
        if not uicore.uilib.rightbtn and (uicore.uilib.leftbtn and wantedBtn == 0 or uicore.uilib.midbtn and wantedBtn == 2):
            self.expandTimer = base.AutoTimer(settings.user.ui.Get('actionMenuExpandTime', 150), self._TryExpandActionMenu, *args)
            return 1
        return 0

    def _TryExpandActionMenu(self, itemID, x, y, wnd):
        self.expandTimer = None
        if wnd.destroyed:
            return
        v = trinity.TriVector(float(uicore.uilib.x - x), float(uicore.uilib.y - y), 0.0)
        if int(v.Length() > 12):
            return
        slimItem = uix.GetBallparkRecord(itemID)
        if not slimItem:
            return
        self.ExpandActionMenu(slimItem)

    def ExpandActionMenu(self, slimItem, centerItem = None):
        uix.Flush(uicore.layer.menu)
        menu = xtriui.ActionMenu(name='actionMenu', parent=uicore.layer.menu, state=uiconst.UI_HIDDEN, align=uiconst.TOPLEFT)
        uicore.uilib.SetMouseCapture(menu)
        menu.expandTime = blue.os.GetWallclockTime()
        menu.Load(slimItem, centerItem)
        if not (uicore.uilib.leftbtn or uicore.uilib.midbtn):
            sm.StartService('state').SetState(slimItem.itemID, state.selected, 1)
            menu.Close()
            return
        sm.StartService('state').SetState(slimItem.itemID, state.mouseOver, 0)
        menu.state = uiconst.UI_NORMAL
        uicls.Container(name='blocker', parent=uicore.layer.menu, state=uiconst.UI_NORMAL, align=uiconst.TOALL, pos=(0, 0, 0, 0))
        if slimItem.itemID == session.shipid:
            displayName = localization.GetByLabel('UI/Inflight/ActionButtonsYourShipWithCategory', categoryOfYourShip=cfg.invgroups.Get(slimItem.groupID).name)
        else:
            displayName = uix.GetSlimItemName(slimItem)
            bp = sm.StartService('michelle').GetBallpark()
            if bp:
                ball = bp.GetBall(slimItem.itemID)
                if ball:
                    displayName += ' ' + util.FmtDist(ball.surfaceDist)
        self.AddHint(displayName, menu)

    def AddHint(self, hint, where):
        hintobj = uicls.Container(parent=where, name='hint', align=uiconst.TOPLEFT, width=200, height=16, idx=0, state=uiconst.UI_DISABLED)
        hintobj.hinttext = uicls.EveHeaderSmall(text=hint, parent=hintobj, top=4, state=uiconst.UI_DISABLED)
        border = uicls.Frame(parent=hintobj, frameConst=uiconst.FRAME_BORDER1_CORNER5, state=uiconst.UI_DISABLED, color=(1.0, 1.0, 1.0, 0.25))
        frame = uicls.Frame(parent=hintobj, color=(0.0, 0.0, 0.0, 0.75), frameConst=uiconst.FRAME_FILLED_CORNER4, state=uiconst.UI_DISABLED)
        if hintobj.hinttext.textwidth > 200:
            hintobj.hinttext.width = 200
            hintobj.hinttext.text = '<center>' + hint + '</center>'
        hintobj.width = max(56, hintobj.hinttext.textwidth + 16)
        hintobj.height = max(16, hintobj.hinttext.textheight + hintobj.hinttext.top * 2)
        hintobj.left = (where.width - hintobj.width) / 2
        hintobj.top = -hintobj.height - 4
        hintobj.hinttext.left = (hintobj.width - hintobj.hinttext.textwidth) / 2

    def MapMenu(self, itemIDs, unparsed = 0):
        if type(itemIDs) == list:
            menus = []
            for itemID in itemIDs:
                menus.append(self._MapMenu(itemID, unparsed))

            return self.MergeMenus(menus)
        else:
            return self._MapMenu(itemIDs, unparsed)

    def _MapMenu(self, itemID, unparsed = 0):
        menuEntries = []
        if util.IsSolarSystem(itemID) or util.IsStation(itemID):
            waypoints = sm.StartService('starmap').GetWaypoints()
            uni, regionID, constellationID, _sol, _item = sm.StartService('map').GetParentLocationID(itemID, gethierarchy=1)
            checkInWaypoints = itemID in waypoints
            menuEntries += [None]
            menuEntries += [[uiutil.MenuLabel('UI/Inflight/SetDestination'), sm.StartService('starmap').SetWaypoint, (itemID, 1)]]
            if checkInWaypoints:
                menuEntries += [[uiutil.MenuLabel('UI/Inflight/RemoveWaypoint'), sm.StartService('starmap').ClearWaypoints, (itemID,)]]
            else:
                menuEntries += [[uiutil.MenuLabel('UI/Inflight/AddWaypoint'), sm.StartService('starmap').SetWaypoint, (itemID,)]]
            menuEntries += [[uiutil.MenuLabel('UI/Inflight/BookmarkLocation'), self.Bookmark, (itemID, const.typeSolarSystem, constellationID)]]
        else:
            return []
        if unparsed:
            return menuEntries
        return self.ParseMenu(menuEntries)

    def InvItemMenu(self, invItems, viewOnly = 0, voucher = None, unparsed = 0, filterFunc = None):
        if type(invItems) == list:
            menus = []
            for invItem, viewOnly, voucher in invItems:
                menus.append(self._InvItemMenu(invItem, viewOnly, voucher, unparsed, len(invItems) > 1, filterFunc, allInvItems=invItems))

            return self.MergeMenus(menus)
        else:
            return self.MergeMenus([self._InvItemMenu(invItems, viewOnly, voucher, unparsed, filterFunc=filterFunc, allInvItems=None)])

    def _InvItemMenu(self, invItem, viewOnly, voucher, unparsed = 0, multi = 0, filterFunc = None, allInvItems = None):
        if invItem.groupID == const.groupMoney:
            return []
        godmaSM = self.godma.GetStateManager()
        invType = cfg.invtypes.Get(invItem.typeID)
        groupID = invType.groupID
        invGroup = cfg.invgroups.Get(groupID)
        categoryID = invGroup.categoryID
        invCategory = cfg.invcategories.Get(categoryID)
        serviceMask = None
        if session.stationid:
            serviceMask = eve.stationItem.serviceMask
        checkIfInSpace = self.GetCheckInSpace()
        checkIfInStation = self.GetCheckInStation()
        checkIfDrone = categoryID == const.categoryDrone
        checkIfInDroneBay = invItem.flagID == const.flagDroneBay
        checkIfInHangar = invItem.flagID == const.flagHangar
        checkIfInCargo = invItem.flagID == const.flagCargo
        checkIfInOreHold = invItem.flagID == const.flagSpecializedOreHold
        locationItem = checkIfInSpace and self.michelle.GetItem(invItem.locationID) or None
        checkIfDBLessAmmo = type(invItem.itemID) is tuple and locationItem is not None and locationItem.categoryID == const.categoryStructure
        checkIfInShipMA = locationItem is not None and locationItem.groupID in (const.groupShipMaintenanceArray, const.groupAssemblyArray)
        checkIfInShipMAShip = locationItem is not None and locationItem.categoryID == const.categoryShip and godmaSM.GetType(locationItem.typeID).hasShipMaintenanceBay and invItem.flagID == const.flagShipHangar
        checkIfInShipMAShip2 = locationItem is not None and locationItem.categoryID == const.categoryShip and godmaSM.GetType(locationItem.typeID).hasShipMaintenanceBay and invItem.flagID == const.flagShipHangar and invItem.locationID != session.shipid
        checkIfShipMAShip = categoryID == const.categoryShip and bool(godmaSM.GetType(invItem.typeID).hasShipMaintenanceBay)
        checkIfShipFHShip = categoryID == const.categoryShip and bool(godmaSM.GetType(invItem.typeID).hasFleetHangars)
        checkIfShipCloneShip = bool(godmaSM.GetType(invItem.typeID).canReceiveCloneJumps)
        checkMAInRange = self.CheckMAInRange(const.maxConfigureDistance)
        checkIfShipFuelBay = categoryID == const.categoryShip and bool(godmaSM.GetType(invItem.typeID).specialFuelBayCapacity)
        checkIfShipOreHold = categoryID == const.categoryShip and bool(godmaSM.GetType(invItem.typeID).specialOreHoldCapacity)
        checkIfShipGasHold = categoryID == const.categoryShip and bool(godmaSM.GetType(invItem.typeID).specialGasHoldCapacity)
        checkIfShipMineralHold = categoryID == const.categoryShip and bool(godmaSM.GetType(invItem.typeID).specialMineralHoldCapacity)
        checkIfShipSalvageHold = categoryID == const.categoryShip and bool(godmaSM.GetType(invItem.typeID).specialSalvageHoldCapacity)
        checkIfShipShipHold = categoryID == const.categoryShip and bool(godmaSM.GetType(invItem.typeID).specialShipHoldCapacity)
        checkIfShipSmallShipHold = categoryID == const.categoryShip and bool(godmaSM.GetType(invItem.typeID).specialSmallShipHoldCapacity)
        checkIfShipMediumShipHold = categoryID == const.categoryShip and bool(godmaSM.GetType(invItem.typeID).specialMediumShipHoldCapacity)
        checkIfShipLargeShipHold = categoryID == const.categoryShip and bool(godmaSM.GetType(invItem.typeID).specialLargeShipHoldCapacity)
        checkIfShipIndustrialShipHold = categoryID == const.categoryShip and bool(godmaSM.GetType(invItem.typeID).specialIndustrialShipHoldCapacity)
        checkIfShipAmmoHold = categoryID == const.categoryShip and bool(godmaSM.GetType(invItem.typeID).specialAmmoHoldCapacity)
        checkIfShipCommandCenterHold = categoryID == const.categoryShip and bool(godmaSM.GetType(invItem.typeID).specialCommandCenterHoldCapacity)
        checkIfShipPlanetaryCommoditiesHold = categoryID == const.categoryShip and bool(godmaSM.GetType(invItem.typeID).specialPlanetaryCommoditiesHoldCapacity)
        checkIfShipHasQuafeBay = categoryID == const.categoryShip and bool(godmaSM.GetType(invItem.typeID).specialQuafeHoldCapacity)
        checkIfShipHasDroneBay = categoryID == const.categoryShip and bool(godmaSM.GetType(invItem.typeID).droneCapacity or godmaSM.GetType(invItem.typeID).techLevel == 3)
        checkViewOnly = bool(viewOnly)
        checkIfAtStation = util.IsStation(invItem.locationID)
        checkIfActiveShip = invItem.itemID == util.GetActiveShip()
        checkIfInHangarAtStation = not (bool(checkIfInHangar) and invItem.locationID != session.stationid)
        checkContainer = invItem.groupID in (const.groupWreck,
         const.groupCargoContainer,
         const.groupSecureCargoContainer,
         const.groupAuditLogSecureContainer,
         const.groupFreightContainer,
         const.groupMissionContainer)
        checkCanBeJettisoned = not (invItem.categoryID == const.categoryShip or int(self.godma.GetTypeAttribute2(invItem.typeID, const.attributeCanBeJettisoned)) == 0 and checkContainer)
        checkCanContain = cfg.IsContainer(invItem)
        checkSingleton = bool(invItem.singleton)
        checkBPSingleton = bool(invItem.singleton) and invItem.categoryID == const.categoryBlueprint
        checkPlasticWrap = invItem.typeID == const.typePlasticWrap
        checkIsStation = util.IsStation(invItem.itemID)
        checkIfMineOrCorps = invItem.ownerID in [session.corpid, session.charid]
        checkIfImInStation = bool(session.stationid2)
        checkIfIsMine = invItem.ownerID == session.charid
        checkIfIsShip = invItem.categoryID == const.categoryShip
        checkIfIsCapsule = invItem.groupID == const.groupCapsule
        checkIfIsMyCorps = invItem.ownerID == session.corpid
        checkIfIsStructure = invItem.categoryID == const.categoryStructure
        checkIfIsSovStructure = categoryID == const.categorySovereigntyStructure
        checkIfOrbital = categoryID == const.categoryOrbital
        checkIfIsHardware = invCategory.IsHardware()
        checkActiveShip = util.GetActiveShip() is not None
        checkIsOrbital = util.IsOrbital(invItem.categoryID)
        checkIfRepackable = categoryID in const.repackableCategorys or groupID in const.repackableGroups
        checkIfNoneLocation = invItem.flagID == const.flagNone
        checkIfAnchorable = invGroup.anchorable
        checkConstructionPF = groupID in (const.groupConstructionPlatform, const.groupStationUpgradePlatform, const.groupStationImprovementPlatform)
        checkMineable = categoryID == const.categoryAsteroid or groupID == const.groupHarvestableCloud
        checkRefining = bool(session.stationid) and bool(serviceMask & const.stationServiceRefinery or serviceMask & const.stationServiceReprocessingPlant)
        checkRefinable = bool(checkRefining) and sm.StartService('reprocessing').GetOptionsForItemTypes({invItem.typeID: 0})[invItem.typeID].isRefinable
        checkRecyclable = bool(checkRefining) and sm.StartService('reprocessing').GetOptionsForItemTypes({invItem.typeID: 0})[invItem.typeID].isRecyclable
        checkSkill = categoryID == const.categorySkill
        checkImplant = categoryID == const.categoryImplant and bool(godmaSM.GetType(invItem.typeID).implantness)
        checkPilotLicence = invItem.typeID == const.typePilotLicence
        checkAurumToken = invItem.groupID == const.groupGameTime
        checkReverseRedeemable = invItem.groupID in const.reverseRedeemingLegalGroups
        checkBooster = groupID == const.groupBooster and bool(godmaSM.GetType(invItem.typeID).boosterness)
        checkSecContainer = groupID in (const.groupSecureCargoContainer, const.groupAuditLogSecureContainer)
        checkIfInQuickBar = invItem.typeID in settings.user.ui.Get('marketquickbar', [])
        checkMultiSelection = bool(multi)
        checkAuditLogSecureContainer = groupID == const.groupAuditLogSecureContainer
        checkIfLockedInALSC = invItem.flagID == const.flagLocked
        checkIfUnlockedInALSC = invItem.flagID == const.flagUnlocked
        checkSameLocation = self.CheckSameLocation(invItem)
        checkSameStation = self.CheckSameStation(invItem)
        checkHasMarketGroup = cfg.invtypes.Get(invItem.typeID).marketGroupID is not None
        checkIsPublished = cfg.invtypes.Get(invItem.typeID).published
        checkRepairService = bool(session.stationid) and bool(serviceMask & const.stationServiceRepairFacilities)
        checkIfRepairable = util.IsItemOfRepairableType(invItem)
        checkLocationInSpace = locationItem is not None
        checkLocationCorpHangarArrayEquivalent = locationItem is not None and locationItem.groupID in (const.groupCorporateHangarArray, const.groupAssemblyArray)
        checkShipInStructure = locationItem is not None and locationItem.categoryID == const.categoryStructure and invItem.categoryID == const.categoryShip
        checkInControlTower = locationItem is not None and locationItem.groupID == const.groupControlTower
        checkIfInHighSec = checkIfInSpace and sm.GetService('map').GetSecurityClass(session.solarsystemid) >= const.securityClassHighSec
        checkIfInHangarOrCorpHangarAndCanTake = self.CheckIfInHangarOrCorpHangarAndCanTake(invItem)
        checkIfInDeliveries = invItem.flagID == const.flagCorpMarket
        checkIfInHangarOrCorpHangarOrDeliveriesAndCanTake = checkIfInHangarOrCorpHangarAndCanTake or checkIfInDeliveries
        checkIsRamInstallable = sm.StartService('manufacturing').IsRamInstallable(invItem)
        checkIsReverseEngineering = sm.StartService('manufacturing').IsReverseEngineering(invItem)
        checkIfLockableBlueprint = self.CheckIfLockableBlueprint(invItem)
        checkIfUnlockableBlueprint = self.CheckIfUnlockableBlueprint(invItem)
        checkIfIAmDirector = session.corprole & const.corpRoleDirector > 0
        checkItemIsInSpace = bool(const.minSolarSystem <= invItem.locationID <= const.maxSolarSystem)
        checkStack = invItem.stacksize > 1
        checkIfQueueOpen = sm.GetService('skillqueue').IsQueueWndOpen()
        checkMultStations = False
        if allInvItems and len(allInvItems) > 0:
            checkIsMultipleStations = False
            locationIDCompare = allInvItems[0][0].locationID
            for item in allInvItems:
                item = item[0]
                if item.locationID != locationIDCompare:
                    checkIsMultipleStations = True
                    break

            checkMultStations = checkIsMultipleStations
        menuEntries = MenuList()
        if checkIfActiveShip:
            menuEntries += self.RigSlotMenu(invItem.itemID)
        if not checkMultiSelection:
            menuEntries += [[uiutil.MenuLabel('UI/Commands/ShowInfo'), self.ShowInfo, (invItem.typeID,
               invItem.itemID,
               0,
               invItem,
               None)]]
        if checkIfInSpace and checkIfDrone and checkIfInDroneBay and not checkViewOnly:
            menuEntries += [[uiutil.MenuLabel('UI/Drones/LaunchDrones'), self.LaunchDrones, [invItem]]]
        else:
            prereqs = [('notInSpace', checkIfInSpace, True), ('badGroup',
              checkIfDrone,
              True,
              {'groupName': invCategory.name})]
            reason = self.FindReasonNotAvailable(prereqs)
            if reason:
                menuEntries.reasonsWhyNotAvailable['UI/Drones/LaunchDrones'] = reason
        if checkStack and not checkIfInDeliveries and checkIfIsMyCorps and checkIfInHangarOrCorpHangarAndCanTake and checkIfInStation:
            menuEntries += [[uiutil.MenuLabel('UI/Inventory/ItemActions/SplitStack'), self.SplitStack, [invItem]]]
        menuEntries += [None]
        if checkIfInStation and checkRefining and not checkViewOnly and not checkIfInDeliveries:
            if checkMineable and checkRefinable and checkIfAtStation and checkIfInHangarAtStation:
                menuEntries += [[uiutil.MenuLabel('UI/Inventory/ItemActions/Refine'), self.Refine, [invItem]]]
            if checkSameLocation and checkRecyclable and checkIfAtStation and not checkIfActiveShip:
                menuEntries += [[uiutil.MenuLabel('UI/Inventory/ItemActions/Reprocess'), self.Refine, [invItem]]]
            if checkMineable and not checkIfAtStation and checkRefinable:
                menuEntries += [[uiutil.MenuLabel('UI/Inventory/ItemActions/ToHangarAndRefine'), self.RefineToHangar, [invItem]]]
        menuEntries += [None]
        if not checkViewOnly:
            if checkSameLocation:
                if checkSkill and not checkIfQueueOpen:
                    menuEntries += [[uiutil.MenuLabel('UI/SkillQueue/AddSkillMenu/TrainNowToLevel1'), self.TrainNow, [invItem]]]
                if checkSkill:
                    menuEntries += [[uiutil.MenuLabel('UI/SkillQueue/InjectSkill'), self.InjectSkillIntoBrain, [invItem]]]
                if checkImplant:
                    menuEntries += [[uiutil.MenuLabel('UI/Inventory/ItemActions/PlugInImplant'), self.PlugInImplant, [invItem]]]
                if checkBooster:
                    menuEntries += [[uiutil.MenuLabel('UI/Inventory/ItemActions/ConsumeBooster'), self.ConsumeBooster, [invItem]]]
            if checkPilotLicence and not checkMultiSelection:
                menuEntries += [[uiutil.MenuLabel('UI/Commands/AddGameTimeToAccount'), self.ApplyPilotLicence, (invItem.itemID,)]]
            if checkReverseRedeemable and not checkMultiSelection:
                menuEntries += [[uiutil.MenuLabel('UI/Inventory/ItemActions/ReverseRedeem'), sm.GetService('redeem').ReverseRedeem, (invItem,)]]
            if checkAurumToken and checkIfInStation and checkSameLocation and not checkMultiSelection:
                menuEntries += [[uiutil.MenuLabel('UI/Inventory/ItemActions/RedeemForAurum'), self.ApplyAurumToken, (invItem, invItem.stacksize)]]
        menuEntries += [None]
        if not checkViewOnly and checkSameLocation and not checkMultiSelection and checkSingleton:
            if checkSecContainer and checkIfInStation:
                desc = localization.GetByLabel('UI/Menusvc/SetNewPasswordForContainerDesc')
                menuEntries += [[uiutil.MenuLabel('UI/Inventory/ItemActions/SetNewPasswordForContainer'), self.AskNewContainerPwd, ([invItem], desc, const.SCCPasswordTypeGeneral)]]
            if checkAuditLogSecureContainer and checkIfInStation:
                desc = localization.GetByLabel('UI/Menusvc/SetNewPasswordForContainerDesc')
                menuEntries += [[uiutil.MenuLabel('UI/Inventory/ItemActions/SetNewConfigPasswordForContainer'), self.AskNewContainerPwd, ([invItem], desc, const.SCCPasswordTypeConfig)]]
            if checkAuditLogSecureContainer and checkIfMineOrCorps:
                menuEntries += [[uiutil.MenuLabel('UI/Inventory/ItemActions/ViewLog'), self.ViewAuditLogForALSC, (invItem.itemID,)]]
            if checkAuditLogSecureContainer and checkIfMineOrCorps:
                menuEntries += [[uiutil.MenuLabel('UI/Inventory/ItemActions/ConfigureALSContainer'), self.ConfigureALSC, (invItem.itemID,)]]
            if checkAuditLogSecureContainer and checkIfMineOrCorps:
                menuEntries += [[uiutil.MenuLabel('UI/Commands/RetrievePassword'), self.RetrievePasswordALSC, (invItem.itemID,)]]
            if checkContainer and not checkIsOrbital:
                menuEntries += [[uiutil.MenuLabel('UI/Commands/SetName'), self.SetName, (invItem,)]]
        if checkContainer and checkIfInStation and not checkSingleton and not checkViewOnly and checkSameLocation:
            menuEntries += [[uiutil.MenuLabel('UI/Inventory/ItemActions/AssembleContainer'), self.AssembleContainer, [invItem]]]
        menuEntries += [None]
        if checkConstructionPF and not checkViewOnly and checkSingleton and not checkMultiSelection:
            desc1 = localization.GetByLabel('UI/Menusvc/SetAccessPasswordOnPlatformDesc')
            desc2 = localization.GetByLabel('UI/Menusvc/SetBuildPasswordOnPlatformDesc')
            menuEntries += [[uiutil.MenuLabel('UI/Inflight/POS/SetPlatformAccessPassword'), self.AskNewContainerPwd, ([invItem], desc1, const.SCCPasswordTypeGeneral)]]
            menuEntries += [[uiutil.MenuLabel('UI/Inflight/POS/SetPlatformBuildPassword'), self.AskNewContainerPwd, ([invItem], desc2, const.SCCPasswordTypeConfig)]]
        if checkIfInSpace and checkIfDBLessAmmo and not checkMultiSelection:
            menuEntries += [[uiutil.MenuLabel('UI/Inventory/ItemActions/TransferAmmoToCarbo'), self.TransferToCargo, (invItem.itemID,)]]
        menuEntries += [None]
        if checkIfUnlockedInALSC:
            menuEntries += [[uiutil.MenuLabel('UI/Inventory/ItemActions/LockItem'), self.ALSCLock, [invItem]]]
        if checkIfLockedInALSC:
            menuEntries += [[uiutil.MenuLabel('UI/Inventory/ItemActions/UnlockItem'), self.ALSCUnlock, [invItem]]]
        if checkIfLockableBlueprint:
            menuEntries += [[uiutil.MenuLabel('UI/Inventory/ItemActions/ProposeBlueprintLockdownVote'), self.LockDownBlueprint, (invItem,)]]
        if checkIfUnlockableBlueprint:
            menuEntries += [[uiutil.MenuLabel('UI/Inventory/ItemActions/ProposeBlueprintUnlockVote'), self.UnlockBlueprint, (invItem,)]]
        if checkSameStation and checkIfIsShip and checkIfImInStation and checkIfAtStation and checkIfInHangar and checkIfIsMine and not checkMultiSelection:
            if invItem.itemID == util.GetActiveShip():
                if self.viewState.IsViewActive('station'):
                    menuEntries += [[uiutil.MenuLabel('UI/Commands/EnterHangar'), self.EnterHangar, [invItem]]]
                elif self.viewState.IsViewActive('hangar') and settings.public.device.Get('loadstationenv2', 1):
                    menuEntries += [[uiutil.MenuLabel('UI/Neocom/CqBtn'), self.EnterCQ, [invItem]]]
        if checkIfInStation and checkRepairService and checkIfRepairable and checkIfAtStation and checkSameLocation and checkIfIsMine:
            menuEntries += [[uiutil.MenuLabel('UI/Inventory/ItemActions/GetRepairQuote'), self.RepairItems, [invItem]]]
        if checkHasMarketGroup and not checkMultiSelection and not checkIsStation:
            menuEntries += [[uiutil.MenuLabel('UI/Inventory/ItemActions/ViewTypesMarketDetails'), self.ShowMarketDetails, (invItem,)]]
            if checkIfMineOrCorps and not checkIfActiveShip and checkIfInHangarOrCorpHangarAndCanTake and not checkBPSingleton:
                menuEntries += [[uiutil.MenuLabel('UI/Inventory/ItemActions/SellThisItem'), self.QuickSell, (invItem,)]]
            menuEntries += [[uiutil.MenuLabel('UI/Inventory/ItemActions/BuyThisType'), self.QuickBuy, (invItem.typeID,)]]
        if not checkIsStation and checkIfMineOrCorps and not checkIfActiveShip and not checkMultStations and checkIfInHangarOrCorpHangarOrDeliveriesAndCanTake:
            menuEntries += [[uiutil.MenuLabel('UI/Inventory/ItemActions/CreateContract'), self.QuickContract, [invItem]]]
        if checkIsPublished and not checkMultiSelection and not checkIsStation:
            menuEntries += [[uiutil.MenuLabel('UI/Inventory/ItemActions/FindInContracts'), sm.GetService('contracts').FindRelated, (invItem.typeID,
               None,
               None,
               None,
               None,
               None)]]
        if not checkIfInQuickBar and not checkMultiSelection and not checkIsStation:
            menuEntries += [[uiutil.MenuLabel('UI/Inventory/ItemActions/AddTypeToMarketQuickbar'), self.AddToQuickBar, (invItem.typeID,)]]
        if checkIfInQuickBar and not checkMultiSelection:
            menuEntries += [[uiutil.MenuLabel('UI/Inventory/ItemActions/RemoveTypeFromMarketQuickbar'), self.RemoveFromQuickBar, (invItem,)]]
        if checkIfInHangar and checkIfAtStation and checkIfIsMine and checkCanContain:
            menuEntries += [[uiutil.MenuLabel('UI/Inventory/ItemActions/ViewContents'), self.GetContainerContents, [invItem]]]
        if not checkViewOnly and checkSingleton:
            if checkSameLocation and checkContainer and not checkIfInDeliveries:
                menuEntries += [[uiutil.MenuLabel('UI/Inventory/ItemActions/OpenContainer'), self.OpenCargoContainer, [invItem]]]
                if checkIfAtStation and checkIfInHangar and checkPlasticWrap:
                    menuEntries += [[uiutil.MenuLabel('UI/Contracts/BreakContract'), self.Break, [invItem]]]
                    menuEntries += [[uiutil.MenuLabel('UI/Inventory/ItemActions/ContractsDelieverCourierPackage'), self.DeliverCourierContract, [invItem]]]
            if checkSameStation and checkIfIsShip and checkIfImInStation and checkIfAtStation and checkIfInHangar and checkIfIsMine and not checkMultiSelection:
                if not checkIfActiveShip and checkIfMineOrCorps:
                    menuEntries += [[uiutil.MenuLabel('UI/Inventory/ItemActions/MakeShipActive'), self.ActivateShip, (invItem,)]]
                if checkIfActiveShip and checkIfMineOrCorps and not checkIfIsCapsule:
                    menuEntries += [[uiutil.MenuLabel('UI/Inventory/ItemActions/LeaveShip'), self.LeaveShip, (invItem,)]]
                if not checkIfIsCapsule:
                    menuEntries += [[uiutil.MenuLabel('UI/Inventory/ItemActions/StripFitting'), self.StripFitting, [invItem]]]
        if checkContainer and checkPlasticWrap:
            menuEntries += [[uiutil.MenuLabel('UI/Inventory/ItemActions/FindContract'), self.FindCourierContract, [invItem]]]
        menuEntries += [None]
        if checkIsRamInstallable:
            for actID, labelPath in sm.GetService('manufacturing').GetActivities():
                if actID != const.activityNone:
                    text = uiutil.MenuLabel(labelPath)
                    menuEntries += [[text, self.Manufacture, [invItem, actID]]]

        if checkIsReverseEngineering:
            for actID, labelPath in sm.GetService('manufacturing').GetActivities():
                if actID == const.activityReverseEngineering:
                    text = uiutil.MenuLabel(labelPath)
                    menuEntries += [[text, self.Manufacture, [invItem, actID]]]

        menuEntries += [None]
        if not checkViewOnly:
            if checkIfIsShip and checkSameLocation and checkIfImInStation and checkIfAtStation and checkIfInHangar and checkIfIsMine and not checkSingleton:
                menuEntries += [[uiutil.MenuLabel('UI/Inventory/ItemActions/AssembleShip'), self.AssembleShip, [invItem]]]
            if checkIfIsShip and checkIfInSpace and checkIfInCargo and checkIfIsMine and not checkSingleton:
                menuEntries += [[uiutil.MenuLabel('UI/Inventory/ItemActions/AssembleShip'), self.AssembleShip, [invItem]]]
            if checkIfIsShip and checkIfInSpace and checkLocationCorpHangarArrayEquivalent and checkLocationInSpace and not checkSingleton:
                menuEntries += [[uiutil.MenuLabel('UI/Inventory/ItemActions/AssembleShip'), self.AssembleShip, [invItem]]]
            if checkIfImInStation and checkIfIsHardware and checkActiveShip and checkSameStation and not checkImplant and not checkBooster:
                menuEntries += [[uiutil.MenuLabel('UI/Inventory/ItemActions/FitToActiveShip'), self.TryFit, [invItem]]]
            if checkIfInSpace and not checkIfInDroneBay and checkIfDrone and checkMAInRange:
                menuEntries += [[uiutil.MenuLabel('UI/Drones/MoveToDroneBay'), self.FitDrone, [invItem]]]
        menuEntries += [None]
        if checkIfImInStation and checkIfInHangar and checkIfIsShip and checkSingleton and checkSameStation:
            if checkIfActiveShip and checkIfShipCloneShip:
                menuEntries += [[uiutil.MenuLabel('UI/Commands/ConfigureShipCloneFacility'), self.ShipCloneConfig, (invItem.itemID,)]]
            menuEntries += [[uiutil.MenuLabel('UI/Commands/OpenCargoHold'), self.OpenShipHangarCargo, [invItem.itemID]]]
            if checkIfShipHasDroneBay:
                menuEntries += [[uiutil.MenuLabel('UI/Commands/OpenDroneBay'), self.OpenDroneBay, [invItem.itemID]]]
            if checkIfShipMAShip:
                menuEntries += [[uiutil.MenuLabel('UI/Commands/OpenShipMaintenanceBay'), self.OpenShipMaintenanceBayShip, (invItem.itemID, localization.GetByLabel('UI/Commands/OpenShipMaintenanceBayError'))]]
            if checkIfShipFHShip:
                menuEntries += [[uiutil.MenuLabel('UI/Commands/OpenFleetHangar'), self.OpenFleetHangar, (invItem.itemID,)]]
            if checkIfShipFuelBay:
                menuEntries += [[uiutil.MenuLabel('UI/Commands/OpenFuelBay'), self.OpenFuelBay, [invItem.itemID]]]
            if checkIfShipOreHold:
                menuEntries += [[uiutil.MenuLabel('UI/Commands/OpenOreHold'), self.OpenOreHold, [invItem.itemID]]]
            if checkIfShipGasHold:
                menuEntries += [[uiutil.MenuLabel('UI/Commands/OpenGasHold'), self.OpenGasHold, [invItem.itemID]]]
            if checkIfShipMineralHold:
                menuEntries += [[uiutil.MenuLabel('UI/Commands/OpenMineralHold'), self.OpenMineralHold, [invItem.itemID]]]
            if checkIfShipSalvageHold:
                menuEntries += [[uiutil.MenuLabel('UI/Commands/OpenSalvageHold'), self.OpenSalvageHold, [invItem.itemID]]]
            if checkIfShipShipHold:
                menuEntries += [[uiutil.MenuLabel('UI/Commands/OpenShipHold'), self.OpenShipHold, [invItem.itemID]]]
            if checkIfShipSmallShipHold:
                menuEntries += [[uiutil.MenuLabel('UI/Commands/OpenSmallShipHold'), self.OpenSmallShipHold, [invItem.itemID]]]
            if checkIfShipMediumShipHold:
                menuEntries += [[uiutil.MenuLabel('UI/Commands/OpenMediumShipHold'), self.OpenMediumShipHold, [invItem.itemID]]]
            if checkIfShipLargeShipHold:
                menuEntries += [[uiutil.MenuLabel('UI/Commands/OpenLargeShipHold'), self.OpenLargeShipHold, [invItem.itemID]]]
            if checkIfShipIndustrialShipHold:
                menuEntries += [[uiutil.MenuLabel('UI/Commands/OpenIndustrialShipHold'), self.OpenIndustrialShipHold, [invItem.itemID]]]
            if checkIfShipAmmoHold:
                menuEntries += [[uiutil.MenuLabel('UI/Commands/OpenAmmoHold'), self.OpenAmmoHold, [invItem.itemID]]]
            if checkIfShipCommandCenterHold:
                menuEntries += [[uiutil.MenuLabel('UI/Commands/OpenCommandCenterHold'), self.OpenCommandCenterHold, [invItem.itemID]]]
            if checkIfShipPlanetaryCommoditiesHold:
                menuEntries += [[uiutil.MenuLabel('UI/PI/Common/OpenPlanetaryCommoditiesHold'), self.OpenPlanetaryCommoditiesHold, [invItem.itemID]]]
            if checkIfShipHasQuafeBay:
                menuEntries += [[uiutil.MenuLabel('UI/Commands/OpenQuafeBay'), self.OpenQuafeHold, [invItem.itemID]]]
        menuEntries += [None]
        if checkSameStation and checkIfImInStation and checkIfInHangar and checkIfIsShip and checkIfIsMine and checkSingleton and not checkMultiSelection and not checkViewOnly:
            menuEntries += [[uiutil.MenuLabel('UI/Commands/ChangeName'), self.SetName, (invItem,)]]
        if not checkIsStation and not checkLocationInSpace and checkSingleton and checkIfInHangarOrCorpHangarAndCanTake and checkIfMineOrCorps and not checkIfActiveShip and checkIfRepackable:
            menuEntries += [[uiutil.MenuLabel('UI/Inventory/ItemActions/Repackage'), self.Repackage, [invItem]]]
        menuEntries += [None]
        if checkIfInSpace and not checkViewOnly:
            if checkCanBeJettisoned:
                if checkIfInCargo and checkIfAnchorable and not checkConstructionPF and not checkIfIsStructure and not checkIfIsSovStructure and not checkIfOrbital:
                    menuEntries += [[uiutil.MenuLabel('UI/Inventory/ItemActions/LaunchForSelf'), self.LaunchForSelf, [invItem]]]
                if checkIfInCargo and checkIfAnchorable and not (checkIfOrbital and checkIfInHighSec):
                    menuEntries += [[uiutil.MenuLabel('UI/Inventory/ItemActions/LaunchForCorp'), self.LaunchForCorp, [invItem]]]
                if (checkIfInCargo or checkIfInOreHold) and not checkPlasticWrap:
                    menuEntries += [[uiutil.MenuLabel('UI/Inventory/ItemActions/Jettison'), self.Jettison, [invItem]]]
            if checkIfIsShip:
                if checkIfInShipMA:
                    menuEntries += [[uiutil.MenuLabel('UI/Inventory/ItemActions/LaunchShip'), self.LaunchSMAContents, [invItem]]]
                    menuEntries += [[uiutil.MenuLabel('UI/Inflight/BoardShip'), self.BoardSMAShip, (invItem.locationID, invItem.itemID)]]
                if checkIfInShipMAShip:
                    menuEntries += [[uiutil.MenuLabel('UI/Inventory/ItemActions/LaunchShipFromBay'), self.LaunchSMAContents, [invItem]]]
                if checkIfInShipMAShip2:
                    menuEntries += [[uiutil.MenuLabel('UI/Inflight/POS/BoardShipFromBay'), self.BoardSMAShip, (invItem.locationID, invItem.itemID)]]
        if checkIfImInStation and checkSameStation and checkIfIsShip and checkIfActiveShip:
            menuEntries += [[uiutil.MenuLabel('UI/Commands/UndockFromStation'), self.ExitStation, (invItem,)]]
        if not util.IsNPC(session.corpid) and checkIfIsMyCorps:
            deliverToMenu = []
            divisions = sm.GetService('corp').GetDivisionNames()
            deliverToCorpHangarMenu = [(divisions[1], self.DeliverToCorpHangarFolder, [[invItem, const.flagHangar]]),
             (divisions[2], self.DeliverToCorpHangarFolder, [[invItem, const.flagCorpSAG2]]),
             (divisions[3], self.DeliverToCorpHangarFolder, [[invItem, const.flagCorpSAG3]]),
             (divisions[4], self.DeliverToCorpHangarFolder, [[invItem, const.flagCorpSAG4]]),
             (divisions[5], self.DeliverToCorpHangarFolder, [[invItem, const.flagCorpSAG5]]),
             (divisions[6], self.DeliverToCorpHangarFolder, [[invItem, const.flagCorpSAG6]]),
             (divisions[7], self.DeliverToCorpHangarFolder, [[invItem, const.flagCorpSAG7]])]
            deliverToMenu.append([uiutil.MenuLabel('UI/Corporations/CorpHangarSubmenu'), deliverToCorpHangarMenu])
            deliverToMenu.append((uiutil.MenuLabel('UI/Corporations/CorporationWindow/Members/CorpMember'), self.DeliverToCorpMember, [invItem]))
            if not checkIfNoneLocation and not checkLocationCorpHangarArrayEquivalent and checkIfInHangarOrCorpHangarOrDeliveriesAndCanTake:
                menuEntries += [None]
                menuEntries += [[uiutil.MenuLabel('UI/Corporations/DeliverCorpStuffTo'), deliverToMenu]]
        menuEntries += [None]
        if not checkIfActiveShip and not checkPilotLicence:
            if checkIfInHangar and checkIfAtStation and checkIfIsMine and not checkAurumToken:
                menuEntries += [[uiutil.MenuLabel('UI/Inventory/ItemActions/TrashIt'), self.TrashInvItems, [invItem]]]
            if checkIfIsMyCorps and checkIfIAmDirector and not checkItemIsInSpace and not checkShipInStructure and not checkInControlTower and checkIfInHangarOrCorpHangarAndCanTake:
                menuEntries += [[uiutil.MenuLabel('UI/Inventory/ItemActions/TrashIt'), self.TrashInvItems, [invItem]]]
        checkCanConfigureOrbital = invItem and invItem.groupID != const.groupOrbitalConstructionPlatforms
        checkIsOrbital = util.IsOrbital(invItem.categoryID)
        if checkIsOrbital and checkCanConfigureOrbital:
            menuEntries += [[uiutil.MenuLabel('UI/DustLink/ConfigureOrbital'), self.ConfigureOrbital, (invItem,)]]
        if unparsed:
            return menuEntries
        m = []
        if not (filterFunc and 'GM / WM Extras' in filterFunc) and session.role & (service.ROLE_GML | service.ROLE_WORLDMOD):
            m = [('GM / WM Extras', ('isDynamic', self.GetGMMenu, (invItem.itemID,
                None,
                None,
                invItem,
                None)))]
        return m + self.ParseMenu(menuEntries, filterFunc)

    def CheckItemsInSamePlace(self, invItems):
        if len(invItems) == 0:
            return
        locationID = invItems[0].locationID
        flag = invItems[0].flagID
        ownerID = invItems[0].ownerID
        for item in invItems:
            if item.locationID != locationID or item.flagID != flag or item.ownerID != ownerID:
                raise UserError('ItemsMustBeInSameHangar')
            locationID = item.locationID
            ownerID = item.ownerID
            flag = item.flagID
            locationID = item.locationID

    def InvalidateItemLocation(self, ownerID, stationID, flag):
        if ownerID == session.corpid:
            which = 'offices'
            if flag == const.flagCorpMarket:
                which = 'deliveries'
            sm.services['objectCaching'].InvalidateCachedMethodCall('corpmgr', 'GetAssetInventoryForLocation', session.corpid, stationID, which)
        else:
            sm.services['objectCaching'].InvalidateCachedMethodCall('stationSvc', 'GetStation', stationID)
            self.invCache.GetInventory(const.containerGlobal).InvalidateStationItemsCache(stationID)

    def DeliverToCorpHangarFolder(self, invItemAndFlagList):
        if len(invItemAndFlagList) == 0:
            return
        invItems = []
        itemIDs = []
        for item in invItemAndFlagList:
            invItems.append(item[0])
            itemIDs.append(item[0].itemID)

        self.CheckItemsInSamePlace(invItems)
        fromID = invItems[0].locationID
        doSplit = bool(uicore.uilib.Key(uiconst.VK_SHIFT) and len(invItemAndFlagList) == 1 and invItemAndFlagList[0][0].stacksize > 1)
        stationID = self.invCache.GetStationIDOfItem(invItems[0])
        if stationID is None:
            raise UserError('CanOnlyDoInStations')
        ownerID = invItems[0].ownerID
        flag = invItems[0].flagID
        deliverToFlag = invItemAndFlagList[0][1]
        qty = None
        if doSplit:
            invItem = invItems[0]
            ret = uix.QtyPopup(invItem.stacksize, 1, 1, None, localization.GetByLabel('UI/Inventory/ItemActions/DivideItemStack'))
            if ret is not None:
                qty = ret['qty']
        self.invCache.GetInventoryMgr().DeliverToCorpHangar(fromID, stationID, itemIDs, qty, ownerID, deliverToFlag)
        self.InvalidateItemLocation(ownerID, stationID, flag)
        if ownerID == session.corpid:
            sm.ScatterEvent('OnCorpAssetChange', invItems, stationID)

    def DeliverToCorpMember(self, invItems):
        if len(invItems) == 0:
            return
        self.CheckItemsInSamePlace(invItems)
        corpMemberIDs = sm.GetService('corp').GetMemberIDs()
        cfg.eveowners.Prime(corpMemberIDs)
        memberslist = []
        for memberID in corpMemberIDs:
            if util.IsDustCharacter(memberID):
                continue
            who = cfg.eveowners.Get(memberID)
            memberslist.append([who.ownerName, memberID, who.typeID])

        doSplit = uicore.uilib.Key(uiconst.VK_SHIFT) and len(invItems) == 1 and invItems[0].stacksize > 1
        stationID = self.invCache.GetStationIDOfItem(invItems[0])
        if stationID is None:
            raise UserError('CanOnlyDoInStations')
        ownerID = invItems[0].ownerID
        flagID = invItems[0].flagID
        locationID = invItems[0].locationID
        itemIDs = [ item.itemID for item in invItems ]
        res = uix.ListWnd(memberslist, 'character', localization.GetByLabel('UI/Corporations/Common/SelectCorpMember'), localization.GetByLabel('UI/Corporations/Common/SelectCorpMemberToDeliverTo'), 1)
        if res:
            corporationMemberID = res[1]
            qty = None
            if doSplit:
                invItem = invItems[0]
                ret = uix.QtyPopup(invItem.stacksize, 1, 1, None, localization.GetByLabel('UI/Inventory/ItemActions/DivideItemStack'))
                if ret is not None:
                    qty = ret['qty']
            self.invCache.GetInventoryMgr().DeliverToCorpMember(corporationMemberID, stationID, itemIDs, qty, ownerID, flagID)
            self.InvalidateItemLocation(ownerID, stationID, flagID)
            if ownerID == session.corpid:
                sm.ScatterEvent('OnCorpAssetChange', invItems, stationID)

    def SplitStack(self, invItems):
        if len(invItems) != 1:
            raise UserError('CannotPerformOnMultipleItems')
        invItem = invItems[0]
        ret = uix.QtyPopup(invItem.stacksize, 1, 1, None, localization.GetByLabel('UI/Inventory/ItemActions/DivideItemStack'))
        if ret is not None:
            qty = ret['qty']
            stationID = self.invCache.GetStationIDOfItem(invItem)
            if stationID is None:
                raise UserError('CanOnlyDoInStations')
            flag = invItem.flagID
            self.invCache.GetInventoryMgr().SplitStack(stationID, invItem.itemID, qty, invItem.ownerID)
            self.InvalidateItemLocation(invItem.ownerID, stationID, flag)
            if invItem.ownerID == session.corpid:
                invItem.quantity = invItem.quantity - qty
                sm.ScatterEvent('OnCorpAssetChange', [invItem], stationID)

    def GetDroneMenu(self, data):
        return self.DroneMenu(data, unmerged=0)

    def DroneMenu(self, data, unmerged = 0):
        menu = self.GetGroupSpecificDroneMenu(data, unmerged=unmerged)
        menu += self.GetCommonDroneMenu(data, unmerged=unmerged)
        return menu

    def GetGroupSpecificDroneMenu(self, data, unmerged = 0):
        menuEntries = MenuList()
        targetID = sm.GetService('target').GetActiveTargetID()
        for droneID, groupID, ownerID in data:
            droneState = sm.StartService('michelle').GetDroneState(droneID)
            if droneState:
                ownerID = droneState.ownerID
                controllerID = droneState.controllerID
                groupID = cfg.invtypes.Get(droneState.typeID).groupID
            else:
                controllerID = None
            groupName = cfg.invgroups.Get(groupID).name
            bp = sm.StartService('michelle').GetBallpark()
            if not bp:
                return []
            checkMiningDrone = groupID == const.groupMiningDrone
            checkSalvageDrone = groupID == const.groupSalvageDrone
            checkFighterDrone = groupID == const.groupFighterDrone
            checkCombatDrone = groupID == const.groupCombatDrone
            checkUnanchoringDrone = groupID == const.groupUnanchoringDrone
            checkOtherDrone = not (checkMiningDrone or checkUnanchoringDrone or checkSalvageDrone)
            checkOwner = ownerID == session.charid
            checkController = controllerID == session.shipid
            checkDroneState = droneState is not None
            checkFleet = bool(session.fleetid)
            m = []
            if checkController and checkDroneState:
                if checkOtherDrone:
                    droneIDs = [droneID]
                    crimewatchSvc = sm.GetService('crimewatchSvc')
                    requiredSafetyLevel = crimewatchSvc.GetRequiredSafetyLevelForEngagingDrones(droneIDs, targetID)
                    menuClass = None
                    if crimewatchSvc.CheckUnsafe(requiredSafetyLevel):
                        if requiredSafetyLevel == const.shipSafetyLevelNone:
                            menuClass = uicls.CriminalMenuEntryView
                        else:
                            menuClass = uicls.SuspectMenuEntryView
                    m += [[uiutil.MenuLabel('UI/Drones/EngageTarget'),
                      self.EngageTarget,
                      droneIDs,
                      None,
                      menuClass]]
                else:
                    reason = self.FindReasonNotAvailable([('thisIsNot',
                      checkOtherDrone,
                      True,
                      {'groupName': groupName})])
                    if reason:
                        menuEntries.reasonsWhyNotAvailable['UI/Drones/EngageTarget'] = reason
                if checkMiningDrone:
                    m += [[uiutil.MenuLabel('UI/Drones/MineWithDrone'), self.Mine, [droneID]]]
                    m += [[uiutil.MenuLabel('UI/Drones/MineRepeatedly'), self.MineRepeatedly, [droneID]]]
                elif checkSalvageDrone:
                    m += [[uiutil.MenuLabel('UI/Drones/Salvage'), self.Salvage, [[droneID]]]]
                else:
                    reason = self.FindReasonNotAvailable([('thisIsNot',
                      checkMiningDrone,
                      True,
                      {'groupName': groupName})])
                    if reason:
                        menuEntries.reasonsWhyNotAvailable['UI/Drones/MineWithDrone'] = reason
                        menuEntries.reasonsWhyNotAvailable['UI/Drones/MineRepeatedly'] = reason
            else:
                prereqs = [('dontControlDrone', checkController, True), ('droneIncapacitated', checkDroneState, True)]
                reason = self.FindReasonNotAvailable(prereqs)
                if reason:
                    menuEntries.reasonsWhyNotAvailable['UI/Drones/EngageTarget'] = reason
                    menuEntries.reasonsWhyNotAvailable['UI/Drones/MineWithDrone'] = reason
                    menuEntries.reasonsWhyNotAvailable['UI/Drones/MineRepeatedly'] = reason
            if checkOwner and checkController and checkFleet and checkDroneState:
                if checkFighterDrone:
                    m += [[uiutil.MenuLabel('UI/Drones/DelegateDroneControl'), ('isDynamic', self.GetFleetMemberMenu, (self.DelegateControl,)), [droneID]]]
                elif checkCombatDrone:
                    m += [[uiutil.MenuLabel('UI/Drones/DroneAssist'), ('isDynamic', self.GetFleetMemberMenu, (self.Assist,)), [droneID]]]
                    m += [[uiutil.MenuLabel('UI/Drones/DroneGuard'), ('isDynamic', self.GetFleetMemberMenu, (self.Guard,)), [droneID]]]
            if not checkOwner and checkController and checkFighterDrone and checkDroneState:
                m += [[uiutil.MenuLabel('UI/Drones/ReturnDroneControl'), self.ReturnControl, [droneID]]]
            if checkController and checkUnanchoringDrone and checkDroneState:
                m += [[uiutil.MenuLabel('UI/Inflight/UnanchorObject'), self.DroneUnanchor, [droneID]]]
            else:
                prereqs = [('dontControlDrone', checkController, True), ('thisIsNot',
                  checkUnanchoringDrone,
                  True,
                  {'groupName': groupName}), ('droneIncapacitated', checkDroneState, True)]
                reason = self.FindReasonNotAvailable(prereqs)
                if reason:
                    menuEntries.reasonsWhyNotAvailable['UI/Inflight/UnanchorObject'] = reason
            if unmerged:
                menuEntries.append(m)
            else:
                menuEntries.append(self.ParseMenu(m))
                menuEntries.reasonsWhyNotAvailable = getattr(self, 'reasonsWhyNotAvailable', {})

        if unmerged:
            return menuEntries
        merged = self.MergeMenus(menuEntries)
        return merged

    def GetCommonDroneMenu(self, data, unmerged = 0):
        menuEntries = MenuList()
        for droneID, groupID, ownerID in data:
            droneState = sm.StartService('michelle').GetDroneState(droneID)
            if droneState:
                ownerID = droneState.ownerID
                controllerID = droneState.controllerID
            else:
                controllerID = None
            bp = sm.StartService('michelle').GetBallpark()
            if not bp:
                return []
            droneBall = bp.GetBall(droneID)
            checkOwner = ownerID == session.charid
            checkController = controllerID == session.shipid
            checkDroneState = droneState is not None
            dist = droneBall and max(0, droneBall.surfaceDist)
            checkScoopable = droneState is None or ownerID == session.charid
            checkScoopDist = dist is not None and dist < const.maxCargoContainerTransferDistance
            checkWarpDist = dist > const.minWarpDistance
            checkOwnerOrController = checkOwner or checkController
            m = []
            if checkOwnerOrController and checkDroneState:
                m += [[uiutil.MenuLabel('UI/Drones/ReturnDroneAndOrbit'), self.ReturnAndOrbit, [droneID]]]
            else:
                prereqs = [('dontControlDrone', checkOwnerOrController, True), ('droneIncapacitated', checkDroneState, True)]
                reason = self.FindReasonNotAvailable(prereqs)
                if reason:
                    menuEntries.reasonsWhyNotAvailable['UI/Drones/ReturnDroneAndOrbit'] = reason
            if checkOwner and checkDroneState:
                m += [[uiutil.MenuLabel('UI/Drones/ReturnDroneToBay'), self.ReturnToDroneBay, [droneID]]]
            else:
                prereqs = [('dontOwnDrone', checkOwner, True), ('droneIncapacitated', checkDroneState, True)]
                reason = self.FindReasonNotAvailable(prereqs)
                if reason:
                    menuEntries.reasonsWhyNotAvailable['UI/Drones/ReturnDroneToBay'] = reason
            if not checkWarpDist and checkScoopable:
                m += [[uiutil.MenuLabel('UI/Drones/ScoopDroneToBay'), self.ScoopToDroneBay, [droneID]]]
            else:
                prereqs = [('cantScoopDrone', checkScoopable, True), ('droneNotInScooopRange', checkScoopDist, True)]
                reason = self.FindReasonNotAvailable(prereqs)
                if reason:
                    menuEntries.reasonsWhyNotAvailable['UI/Drones/ScoopDroneToBay'] = reason
            m += [None]
            if checkOwner and checkDroneState:
                m += [[uiutil.MenuLabel('UI/Drones/AbandonDrone'), self.AbandonDrone, [droneID]]]
            if unmerged:
                menuEntries.append(m)
            else:
                menuEntries.append(self.ParseMenu(m))

        if unmerged:
            return menuEntries
        merged = self.MergeMenus(menuEntries)
        return merged

    def CharacterMenu(self, charid, charIDs = [], corpid = None, unparsed = 0, filterFunc = None, **kwargs):
        if type(charid) == list:
            menus = []
            for chid, coid in charid:
                menus.append(self._CharacterMenu(chid, coid, unparsed, filterFunc, len(charid) > 1), **kwargs)

            return self.MergeMenus(menus)
        else:
            return self._CharacterMenu(charid, corpid, unparsed, filterFunc, **kwargs)

    def _CharacterMenu(self, charid, corpid, unparsed = 0, filterFunc = None, multi = 0, **kwargs):
        if not charid:
            return []
        addressBookSvc = sm.GetService('addressbook')
        checkIsNPC = util.IsNPC(charid)
        checkIsAgent = sm.GetService('agents').IsAgent(charid)
        checkInStation = bool(session.stationid)
        checkInAddressbook = bool(addressBookSvc.IsInAddressBook(charid, 'contact'))
        checkInCorpAddressbook = bool(addressBookSvc.IsInAddressBook(charid, 'corpcontact'))
        checkInAllianceAddressbook = bool(addressBookSvc.IsInAddressBook(charid, 'alliancecontact'))
        checkIfBlocked = addressBookSvc.IsBlocked(charid)
        checkIfGuest = session.stationid and sm.StartService('station').IsGuest(charid)
        checkIfMe = charid == session.charid
        checkHaveCloneBay = sm.GetService('clonejump').HasCloneReceivingBay()
        checkIfExecCorp = session.allianceid and sm.GetService('alliance').GetAlliance(session.allianceid).executorCorpID == session.corpid
        checkIAmDiplomat = (const.corpRoleDirector | const.corpRoleDiplomat) & session.corprole != 0
        checkIfEmpireSpace = sm.GetService('map').GetSecurityClass(session.solarsystemid2) != const.securityClassZeroSec
        checkIfDustCharacter = util.IsDustCharacter(charid)
        checkMultiSelection = bool(multi)
        menuEntries = MenuList()
        doShowInfo = True
        if checkIsAgent:
            agentInfo = sm.GetService('agents').GetAgentByID(charid)
            if agentInfo and agentInfo.agentTypeID == const.agentTypeAura:
                doShowInfo = False
        if doShowInfo:
            menuEntries += [(uiutil.MenuLabel('UI/Commands/ShowInfo'), self.ShowInfo, (cfg.eveowners.Get(charid).typeID, charid))]
        if not checkMultiSelection and not checkIfMe and not checkIsNPC:
            isRecruiting = None
            if 'isRecruiting' in kwargs:
                isRecruiting = kwargs['isRecruiting']
            menuEntries += [[uiutil.MenuLabel('UI/Chat/StartConversation'), sm.StartService('LSC').Invite, (charid, None, isRecruiting)]]
        else:
            prereqs = [('checkMultiSelection', checkMultiSelection, False), ('checkIfMe', checkIfMe, False), ('checkIsNPC', checkIsNPC, False)]
            reason = self.FindReasonNotAvailable(prereqs)
            if reason:
                menuEntries.reasonsWhyNotAvailable['UI/Chat/StartConversation'] = reason
        if not checkMultiSelection and not checkIfMe and checkIsNPC and checkIsAgent:
            menuEntries += [[uiutil.MenuLabel('UI/Chat/StartConversationAgent'), sm.StartService('agents').InteractWith, (charid,)]]
        else:
            prereqs = [('checkMultiSelection', checkMultiSelection, False),
             ('checkIfMe', checkIfMe, False),
             ('checkIsNPC', checkIsNPC, True),
             ('checkIsAgent', checkIsAgent, True)]
            reason = self.FindReasonNotAvailable(prereqs)
            if reason:
                menuEntries.reasonsWhyNotAvailable['UI/Chat/StartConversation'] = reason
        if not checkIfMe:
            if not checkInAddressbook and checkIsNPC and checkIsAgent:
                menuEntries += [[uiutil.MenuLabel('UI/PeopleAndPlaces/AddToAddressbook'), addressBookSvc.AddToPersonalMulti, [charid]]]
            if not checkIsNPC:
                if not checkMultiSelection:
                    menuEntries += [[uiutil.MenuLabel('UI/Chat/InviteToChat'), ('isDynamic', self.__GetInviteMenu, (charid,))]]
                menuEntries += [[uiutil.MenuLabel('UI/EVEMail/SendPilotEVEMail'), sm.StartService('mailSvc').SendMsgDlg, ([charid], None, None)]]
                if not checkMultiSelection and not checkInAddressbook:
                    menuEntries += [[uiutil.MenuLabel('UI/PeopleAndPlaces/AddContact'), addressBookSvc.AddToPersonalMulti, [charid, 'contact']]]
                if not checkMultiSelection and checkInAddressbook:
                    menuEntries += [[uiutil.MenuLabel('UI/PeopleAndPlaces/EditContact'), addressBookSvc.AddToPersonalMulti, [charid, 'contact', True]]]
                if not checkMultiSelection and checkInAddressbook:
                    menuEntries += [[uiutil.MenuLabel('UI/PeopleAndPlaces/RemoveContact'), addressBookSvc.DeleteEntryMulti, [[charid], 'contact']]]
            if checkInAddressbook and checkIsNPC and checkIsAgent:
                menuEntries += [[uiutil.MenuLabel('UI/PeopleAndPlaces/RemoveFromAddressbook'), addressBookSvc.DeleteEntryMulti, [charid]]]
            if not checkMultiSelection and checkIfBlocked:
                menuEntries += [[uiutil.MenuLabel('UI/PeopleAndPlaces/UnblockContact'), addressBookSvc.UnblockOwner, ([charid],)]]
            if not checkMultiSelection and not checkIsNPC and not checkIfBlocked:
                menuEntries += [[uiutil.MenuLabel('UI/PeopleAndPlaces/BlockContact'), addressBookSvc.BlockOwner, (charid,)]]
        if not checkIsNPC and checkIAmDiplomat:
            if not checkInCorpAddressbook:
                menuEntries += [[uiutil.MenuLabel('UI/PeopleAndPlaces/AddCorpContact'), addressBookSvc.AddToPersonalMulti, [charid, 'corpcontact']]]
            else:
                menuEntries += [[uiutil.MenuLabel('UI/PeopleAndPlaces/EditCorpContact'), addressBookSvc.AddToPersonalMulti, [charid, 'corpcontact', True]]]
                menuEntries += [[uiutil.MenuLabel('UI/PeopleAndPlaces/RemoveCorpContact'), addressBookSvc.DeleteEntryMulti, [[charid], 'corpcontact']]]
            if checkIfExecCorp and not checkIfDustCharacter:
                if not checkInAllianceAddressbook:
                    menuEntries += [[uiutil.MenuLabel('UI/PeopleAndPlaces/AddAllianceContact'), addressBookSvc.AddToPersonalMulti, [charid, 'alliancecontact']]]
                else:
                    menuEntries += [[uiutil.MenuLabel('UI/PeopleAndPlaces/EditAllianceContact'), addressBookSvc.AddToPersonalMulti, [charid, 'alliancecontact', True]]]
                    menuEntries += [[uiutil.MenuLabel('UI/PeopleAndPlaces/RemoveAllianceContact'), addressBookSvc.DeleteEntryMulti, [[charid], 'alliancecontact']]]
        if not checkMultiSelection and not checkIfMe and not checkIsNPC and not checkIfDustCharacter:
            menuEntries += [[uiutil.MenuLabel('UI/Commands/GiveMoney'), sm.StartService('wallet').TransferMoney, (session.charid,
               None,
               charid,
               None)]]
            if checkHaveCloneBay and not checkIfDustCharacter:
                menuEntries += [[uiutil.MenuLabel('UI/CloneJump/OfferCloneInstallation'), sm.StartService('clonejump').OfferShipCloneInstallation, (charid,)]]
        if not multi:
            agentInfo = sm.StartService('agents').GetAgentByID(charid)
            if agentInfo:
                if agentInfo.solarsystemID and agentInfo.solarsystemID != session.solarsystemid2:
                    menuEntries += [None]
                    menuEntries += self.MapMenu(agentInfo.stationID, unparsed=1)
        if not checkMultiSelection and not checkIfMe and checkInStation and not checkIsNPC and checkIfGuest and not checkIfDustCharacter:
            menuEntries += [[uiutil.MenuLabel('UI/Market/TradeWithCharacter'), sm.StartService('pvptrade').StartTradeSession, (charid,)]]
        if not checkMultiSelection and not checkIsNPC and not checkIfDustCharacter:
            menuEntries += [[uiutil.MenuLabel('UI/Station/BountyOffice/PlaceBounty'), self.OpenBountyOffice, (charid,)]]
        if not checkIsNPC and not util.IsDustCharacter(charid):
            menuEntries += [[uiutil.MenuLabel('UI/Commands/CapturePortrait'), sm.StartService('photo').SavePortraits, [charid]]]
        if not checkIsNPC and not checkIfDustCharacter:
            if session.fleetid is not None:
                fleetSvc = sm.GetService('fleet')
                members = fleetSvc.GetMembers()
                checkIfImLeader = self.ImFleetLeaderOrCommander()
                member = members.get(charid, None)
                if member is None:
                    if not checkMultiSelection and checkIfImLeader:
                        menuEntries += [[uiutil.MenuLabel('UI/Fleet/InvitePilotToFleet'), self.FleetInviteMenu(charid)]]
                elif not checkMultiSelection:
                    menuEntries += [[uiutil.MenuLabel('UI/Fleet/Fleet'), ('isDynamic', self.FleetMenu, (charid, False))]]
            else:
                menuEntries += [[uiutil.MenuLabel('UI/Fleet/FormFleetWith'), self.InviteToFleet, [charid]]]
        if checkIfEmpireSpace and not (checkIsNPC or checkIfMe or checkIfDustCharacter or checkMultiSelection):
            if not self.crimewatchSvc.HasLimitedEngagmentWith(charid):
                menuEntries += [[uiutil.MenuLabel('UI/Crimewatch/Duel/DuelMenuEntry'), self.crimewatchSvc.StartDuel, (charid,)]]
        if not checkIsNPC:
            menuEntries += self.CorpMemberMenu(charid, multi)
        if unparsed:
            return menuEntries
        m = []
        if not (filterFunc and 'GM / WM Extras' in filterFunc) and session.role & (service.ROLE_GML | service.ROLE_WORLDMOD | service.ROLE_LEGIONEER):
            m = [('GM / WM Extras', ('isDynamic', self.GetGMMenu, (None,
                None,
                charid,
                None,
                None)))]
        return m + self.ParseMenu(menuEntries, filterFunc)

    def GetCheckInSpace(self):
        return bool(session.solarsystemid)

    def GetCheckInStation(self):
        return bool(session.stationid)

    def CheckIfLockableBlueprint(self, invItem):
        isLockable = False
        if invItem.categoryID == const.categoryBlueprint:
            if invItem.singleton:
                if invItem.ownerID == session.corpid:
                    if session.corprole & const.corpRoleDirector == const.corpRoleDirector:
                        if invItem.flagID in [const.flagHangar,
                         const.flagCorpSAG2,
                         const.flagCorpSAG3,
                         const.flagCorpSAG4,
                         const.flagCorpSAG5,
                         const.flagCorpSAG6,
                         const.flagCorpSAG7]:
                            rows = sm.StartService('corp').GetMyCorporationsOffices().SelectByUniqueColumnValues('officeID', [invItem.locationID])
                            if rows and len(rows) and rows[0].officeID == invItem.locationID:
                                if not sm.GetService('corp').IsItemLocked(invItem):
                                    isLockable = True
        return bool(isLockable)

    def CheckIfUnlockableBlueprint(self, invItem):
        isUnlockable = False
        if invItem.categoryID == const.categoryBlueprint:
            if invItem.singleton:
                if invItem.ownerID == session.corpid:
                    if session.corprole & const.corpRoleDirector == const.corpRoleDirector:
                        if invItem.flagID in [const.flagHangar,
                         const.flagCorpSAG2,
                         const.flagCorpSAG3,
                         const.flagCorpSAG4,
                         const.flagCorpSAG5,
                         const.flagCorpSAG6,
                         const.flagCorpSAG7]:
                            rows = sm.StartService('corp').GetMyCorporationsOffices().SelectByUniqueColumnValues('officeID', [invItem.locationID])
                            if rows and len(rows) and rows[0].officeID == invItem.locationID:
                                if sm.GetService('corp').IsItemLocked(invItem):
                                    isUnlockable = True
        return bool(isUnlockable)

    def CheckIfInHangarOrCorpHangarAndCanTake(self, invItem):
        canTake = False
        corpMember = False
        stationID = None
        bp = sm.StartService('michelle').GetBallpark()
        if invItem.ownerID == session.charid:
            if util.IsStation(invItem.locationID) and invItem.flagID == const.flagHangar:
                canTake = True
        elif session.solarsystemid and bp is not None and invItem.locationID in bp.slimItems and invItem.ownerID == bp.slimItems[invItem.locationID].ownerID:
            corpMember = True
        elif invItem.ownerID == session.corpid and not util.IsNPC(invItem.ownerID):
            stationID = None
            rows = sm.StartService('corp').GetMyCorporationsOffices().SelectByUniqueColumnValues('officeID', [invItem.locationID])
            if rows and len(rows):
                for row in rows:
                    if invItem.locationID == row.officeID:
                        stationID = row.stationID
                        break

        if stationID is not None or corpMember:
            flags = [const.flagHangar,
             const.flagCorpSAG2,
             const.flagCorpSAG3,
             const.flagCorpSAG4,
             const.flagCorpSAG5,
             const.flagCorpSAG6,
             const.flagCorpSAG7]
            if invItem.flagID in flags:
                roles = 0
                if stationID == session.hqID:
                    roles = session.rolesAtHQ
                elif stationID == session.baseID:
                    roles = session.rolesAtBase
                else:
                    roles = session.rolesAtOther
                if invItem.ownerID == session.corpid or corpMember:
                    rolesByFlag = {const.flagHangar: const.corpRoleHangarCanTake1,
                     const.flagCorpSAG2: const.corpRoleHangarCanTake2,
                     const.flagCorpSAG3: const.corpRoleHangarCanTake3,
                     const.flagCorpSAG4: const.corpRoleHangarCanTake4,
                     const.flagCorpSAG5: const.corpRoleHangarCanTake5,
                     const.flagCorpSAG6: const.corpRoleHangarCanTake6,
                     const.flagCorpSAG7: const.corpRoleHangarCanTake7}
                    roleRequired = rolesByFlag[invItem.flagID]
                    if roleRequired & roles == roleRequired:
                        canTake = True
        return bool(canTake)

    def CheckSameStation(self, invItem):
        inSameLocation = 0
        if session.stationid2:
            if invItem.locationID == session.stationid2:
                inSameLocation = 1
            elif util.IsPlayerItem(invItem.locationID):
                inSameLocation = 1
            else:
                office = sm.StartService('corp').GetOffice_NoWireTrip()
                if office is not None:
                    if invItem.locationID == office.itemID:
                        inSameLocation = 1
        return inSameLocation

    def CheckSameLocation(self, invItem):
        inSameLocation = 0
        if session.stationid:
            if invItem.locationID == session.stationid:
                inSameLocation = 1
            elif util.IsPlayerItem(invItem.locationID):
                inSameLocation = 1
            else:
                office = sm.StartService('corp').GetOffice_NoWireTrip()
                if office is not None:
                    if invItem.locationID == office.itemID:
                        inSameLocation = 1
        if invItem.locationID == session.shipid and invItem.flagID != const.flagShipHangar:
            inSameLocation = 1
        elif session.solarsystemid and invItem.locationID == session.solarsystemid:
            inSameLocation = 1
        return inSameLocation

    def CheckMAInRange(self, useRange):
        if not session.solarsystemid:
            return False
        bp = sm.StartService('michelle').GetBallpark()
        if not bp:
            return False
        godmaSM = self.godma.GetStateManager()
        for slimItem in bp.slimItems.itervalues():
            if slimItem.groupID == const.groupShipMaintenanceArray or slimItem.categoryID == const.categoryShip and godmaSM.GetType(slimItem.typeID).hasShipMaintenanceBay:
                otherBall = bp.GetBall(slimItem.itemID)
                if otherBall:
                    if otherBall.surfaceDist < useRange:
                        return True

        return False

    def ImFleetLeaderOrCommander(self):
        return sm.GetService('fleet').IsBoss() or session.fleetrole in (const.fleetRoleLeader, const.fleetRoleWingCmdr, const.fleetRoleSquadCmdr)

    def ImFleetCommander(self):
        return session.fleetrole in (const.fleetRoleLeader, const.fleetRoleWingCmdr, const.fleetRoleSquadCmdr)

    def CheckImFleetLeaderOrBoss(self):
        return sm.GetService('fleet').IsBoss() or session.fleetrole == const.fleetRoleLeader

    def CheckImFleetLeader(self):
        return session.fleetrole == const.fleetRoleLeader

    def CheckImWingCmdr(self):
        return session.fleetrole == const.fleetRoleWingCmdr

    def CheckImSquadCmdr(self):
        return session.fleetrole == const.fleetRoleSquadCmdr

    def FleetMenu(self, charID, unparsed = True):

        def ParsedMaybe(menuEntries):
            if unparsed:
                return menuEntries
            else:
                return self.ParseMenu(menuEntries, None)

        if session.fleetid is None:
            return []
        fleetSvc = sm.GetService('fleet')
        vivox = sm.GetService('vivox')
        members = fleetSvc.GetMembers()
        shipItem = util.SlimItemFromCharID(charID)
        bp = sm.StartService('michelle').GetBallpark()
        otherBall = bp and shipItem and bp.GetBall(shipItem.itemID) or None
        me = members[session.charid]
        checkIfImLeader = self.ImFleetLeaderOrCommander()
        checkIfImWingCommanderOrHigher = self.CheckImFleetLeaderOrBoss() or self.CheckImWingCmdr()
        member = members.get(charID)
        char = cfg.eveowners.Get(charID)
        if member is None:
            menuEntries = [[uiutil.MenuLabel('UI/Commands/ShowInfo'), self.ShowInfo, (int(char.Type()),
               charID,
               0,
               None,
               None)]]
            return menuEntries
        isTitan = False
        isJumpDrive = False
        if session.solarsystemid and session.shipid:
            ship = sm.StartService('godma').GetItem(session.shipid)
            if ship.canJump:
                isJumpDrive = True
            if ship.groupID in [const.groupTitan, const.groupBlackOps]:
                isTitan = True
        checkImCreator = bool(me.job & const.fleetJobCreator)
        checkIfMe = charID == session.charid
        checkIfInSpace = self.GetCheckInSpace()
        checkIfActiveBeacon = fleetSvc.HasActiveBeacon(charID)
        checkIsTitan = isTitan
        checkIsJumpDrive = isJumpDrive
        checkBoosterFleet = bool(member.roleBooster == const.fleetBoosterFleet)
        checkBoosterWing = bool(member.roleBooster == const.fleetBoosterWing)
        checkBoosterSquad = bool(member.roleBooster == const.fleetBoosterSquad)
        checkBoosterAny = bool(checkBoosterFleet or checkBoosterWing or checkBoosterSquad)
        checkSubordinate = self.CheckImFleetLeaderOrBoss() or me.role == const.fleetRoleWingCmdr and member.wingID == me.wingID or me.role == const.fleetRoleSquadCmdr and member.squadID == me.squadID
        checkBoss = member.job & const.fleetJobCreator
        checkWingCommander = member.role == const.fleetRoleWingCmdr
        checkFleetCommander = member.role == const.fleetRoleLeader
        checkBoosterSubordinate = checkBoosterAny and (checkImCreator or me.role == const.fleetRoleLeader) or (checkBoosterWing or checkBoosterSquad) and me.role == const.fleetRoleWingCmdr or checkBoosterSquad and me.role == const.fleetRoleSquadCmdr
        checkBoosterSubordinateOrSelf = checkBoosterSubordinate or checkBoosterAny and checkIfMe
        checkIfFavorite = fleetSvc.IsFavorite(charID)
        checkIfIsBubble = shipItem is not None
        checkMultiSelection = False
        dist = sys.maxint
        if otherBall:
            dist = max(0, otherBall.surfaceDist)
        checkWarpDist = dist > const.minWarpDistance
        checkIsVoiceEnabled = sm.StartService('vivox').Enabled()
        checkCanMute = fleetSvc.CanIMuteOrUnmuteCharInMyChannel(charID) > 0
        checkCanUnmute = fleetSvc.CanIMuteOrUnmuteCharInMyChannel(charID) < 0
        checkIfPrivateMuted = charID in vivox.GetMutedParticipants()
        if session.fleetrole == const.fleetRoleWingCmdr:
            muteString = uiutil.MenuLabel('UI/Fleet/MuteFromWingChannel')
            unmuteString = uiutil.MenuLabel('UI/Fleet/UnmuteFromWingChannel')
        elif session.fleetrole == const.fleetRoleSquadCmdr:
            muteString = uiutil.MenuLabel('UI/Fleet/MuteFromSquadChannel')
            unmuteString = uiutil.MenuLabel('UI/Fleet/UnmuteFromSquadChannel')
        else:
            muteString = uiutil.MenuLabel('UI/Fleet/MuteFromFleetChannel')
            unmuteString = uiutil.MenuLabel('UI/Fleet/UnmuteFromFleetChannel')
        defaultWarpDist = sm.GetService('menu').GetDefaultActionDistance('WarpTo')
        menuEntries = []
        if not checkMultiSelection:
            menuEntries += [[uiutil.MenuLabel('UI/Commands/ShowInfo'), self.ShowInfo, (int(char.Type()),
               charID,
               0,
               None,
               None)]]
        menuEntries += [None]
        if checkSubordinate and not checkIfMe and not checkBoss:
            menuEntries += [[uiutil.MenuLabel('UI/Fleet/KickFleetMember'), self.ConfirmMenu(lambda *x: fleetSvc.KickMember(charID))]]
        if not checkIfMe and checkImCreator:
            menuEntries += [[uiutil.MenuLabel('UI/Fleet/MakeFleetLeader'), fleetSvc.MakeLeader, (charID,)]]
        if not checkMultiSelection and not checkIfFavorite and not checkIfMe:
            menuEntries += [[uiutil.MenuLabel('UI/Fleet/AddPilotToWatchlist'), fleetSvc.AddFavorite, (charID,)]]
        if self.CheckImFleetLeaderOrBoss() and not checkBoosterAny and checkSubordinate:
            menuEntries += [[uiutil.MenuLabel('UI/Fleet/SetFleetBooster'), fleetSvc.SetBooster, (charID, const.fleetBoosterFleet)]]
        if checkIfImWingCommanderOrHigher and not checkBoosterAny and not checkFleetCommander and checkSubordinate:
            menuEntries += [[uiutil.MenuLabel('UI/Fleet/SetWingBooster'), fleetSvc.SetBooster, (charID, const.fleetBoosterWing)]]
        if not checkBoosterAny and not checkWingCommander and not checkFleetCommander and checkSubordinate:
            menuEntries += [[uiutil.MenuLabel('UI/Fleet/SetSquadBooster'), fleetSvc.SetBooster, (charID, const.fleetBoosterSquad)]]
        if checkBoosterSubordinateOrSelf:
            menuEntries += [[uiutil.MenuLabel('UI/Fleet/RevokeFleetBooster'), fleetSvc.SetBooster, (charID, const.fleetBoosterNone)]]
        if checkIfImLeader and checkIfMe:
            label = uiutil.MenuLabel('UI/Fleet/FleetBroadcast/Commands/BroadcastTravelToMe')
            menuEntries += [[label, sm.GetService('fleet').SendBroadcast_TravelTo, (session.solarsystemid2,)]]
        if checkWarpDist and checkIfInSpace and not checkIfMe:
            menuEntries += [[uiutil.MenuLabel('UI/Fleet/WarpToMember'), self.WarpToMember, (charID, float(defaultWarpDist))]]
            menuEntries += [[uiutil.MenuLabel('UI/Fleet/WarpToMemberSubmenuOption'), self.WarpToMenu(self.WarpToMember, charID)]]
            if self.CheckImFleetLeader():
                menuEntries += [[uiutil.MenuLabel('UI/Fleet/WarpFleetToMember'), self.WarpFleetToMember, (charID, float(defaultWarpDist))]]
                menuEntries += [[uiutil.MenuLabel('UI/Fleet/FleetSubmenus/WarpFleetToMember'), self.WarpToMenu(self.WarpFleetToMember, charID)]]
            if self.CheckImWingCmdr():
                menuEntries += [[uiutil.MenuLabel('UI/Fleet/WarpWingToMember'), self.WarpFleetToMember, (charID, float(defaultWarpDist))]]
                menuEntries += [[uiutil.MenuLabel('UI/Fleet/FleetSubmenus/WarpWingToMember'), self.WarpToMenu(self.WarpFleetToMember, charID)]]
            if self.CheckImSquadCmdr():
                menuEntries += [[uiutil.MenuLabel('UI/Fleet/WarpSquadToMember'), self.WarpFleetToMember, (charID, float(defaultWarpDist))]]
                menuEntries += [[uiutil.MenuLabel('UI/Fleet/FleetSubmenus/WarpSquadToMember'), self.WarpToMenu(self.WarpFleetToMember, charID)]]
        if not checkIfIsBubble and checkIfInSpace and not checkIfMe and checkIfActiveBeacon:
            if checkIsJumpDrive:
                menuEntries += [[uiutil.MenuLabel('UI/Inflight/JumpToFleetMember'), self.JumpToMember, (charID,)]]
            if checkIsTitan:
                menuEntries += [[uiutil.MenuLabel('UI/Fleet/BridgeToMember'), self.BridgeToMember, (charID,)]]
        if not checkMultiSelection and checkIfFavorite:
            menuEntries += [[uiutil.MenuLabel('UI/Fleet/RemovePilotFromWatchlist'), fleetSvc.RemoveFavorite, (charID,)]]
        if not checkIfMe and checkCanMute:
            menuEntries += [[muteString, fleetSvc.AddToVoiceMute, (charID,)]]
        if checkCanUnmute:
            menuEntries += [[unmuteString, fleetSvc.ExcludeFromVoiceMute, (charID,)]]
        if checkIsVoiceEnabled and not checkIfPrivateMuted and not checkIfMe:
            menuEntries += [[uiutil.MenuLabel('UI/Fleet/MuteFleetMemberVoice'), vivox.MuteParticipantForMe, (charID, 1)]]
        if checkIsVoiceEnabled and checkIfPrivateMuted and not checkIfMe:
            menuEntries += [[uiutil.MenuLabel('UI/Fleet/FleetUnmuteVoice'), vivox.MuteParticipantForMe, (charID, 0)]]
        if checkIfMe:
            menuEntries += [[uiutil.MenuLabel('UI/Fleet/LeaveMyFleet'), self.ConfirmMenu(fleetSvc.LeaveFleet)]]
        menuEntries = ParsedMaybe(menuEntries)
        moveMenu = self.GetFleetMemberMenu2(charID, fleetSvc.MoveMember, True)
        if moveMenu:
            menuEntries.extend([[uiutil.MenuLabel('UI/Fleet/FleetSubmenus/MoveFleetMember'), moveMenu]])
        return menuEntries

    def FleetInviteMenu(self, charID):
        return self.GetFleetMemberMenu2(charID, lambda *args: self.DoInviteToFleet(*args))

    def GetFleetMemberMenu2(self, charID, callback, isMove = False):
        if session.fleetid is None:
            return []
        wings = sm.GetService('fleet').GetWings()
        members = sm.GetService('fleet').GetMembers()
        hasFleetCommander = bool([ 1 for guy in members.itervalues() if guy.role == const.fleetRoleLeader ])
        wingsWithCommanders = set([ guy.wingID for guy in members.itervalues() if guy.role == const.fleetRoleWingCmdr ])
        squadsWithCommanders = set([ guy.squadID for guy in members.itervalues() if guy.role == const.fleetRoleSquadCmdr ])
        squads = {}
        for guy in members.itervalues():
            if guy.squadID not in (None, -1):
                squads.setdefault(guy.squadID, []).append(guy)

        myself = members[session.charid]
        member = members.get(charID, None)
        canMoveSquad = myself.role == const.fleetRoleSquadCmdr
        canMoveWing = myself.role == const.fleetRoleWingCmdr
        canMoveAll = myself.role == const.fleetRoleLeader or myself.job & const.fleetJobCreator
        isFreeMove = False
        if sm.GetService('fleet').GetOptions().isFreeMove and charID == session.charid:
            isFreeMove = True
        wingMenu = []
        if canMoveAll or canMoveWing or canMoveSquad or isFreeMove:
            sortedWings = wings.items()
            sortedWings.sort()
            sortedSquads = []
            for w in wings.itervalues():
                sortedSquads.extend(w.squads.iterkeys())

            sortedSquads.sort()
            if canMoveAll or isFreeMove:
                if not hasFleetCommander and canMoveAll:
                    wingMenu.append([uiutil.MenuLabel('UI/Fleet/Ranks/FleetCommander'), callback, (charID,
                      None,
                      None,
                      const.fleetRoleLeader)])
                if canMoveAll and member and member.role in [const.fleetRoleMember, const.fleetRoleSquadCmdr] and member.wingID not in wingsWithCommanders:
                    wingMenu.append([uiutil.MenuLabel('UI/Fleet/Ranks/WingCommander'), callback, (charID,
                      member.wingID,
                      None,
                      const.fleetRoleWingCmdr)])
                if member and member.role == const.fleetRoleMember and member.squadID not in squadsWithCommanders:
                    wingMenu.append([uiutil.MenuLabel('UI/Fleet/Ranks/SquadCommander'), callback, (charID,
                      member.wingID,
                      member.squadID,
                      const.fleetRoleSquadCmdr)])
                if member and member.role == const.fleetRoleSquadCmdr:
                    wingMenu.append([uiutil.MenuLabel('UI/Fleet/Ranks/SquadMember'), callback, (charID,
                      member.wingID,
                      member.squadID,
                      const.fleetRoleMember)])
            if not isMove:
                wingMenu.append([uiutil.MenuLabel('UI/Fleet/Ranks/SquadMember'), callback, (charID,
                  None,
                  None,
                  None)])
            for wi, (wid, w) in enumerate(sortedWings):
                if not (canMoveAll or isFreeMove) and wid != myself.wingID:
                    continue
                if (canMoveWing or canMoveAll) and wid not in wingsWithCommanders:
                    subsquads = [[uiutil.MenuLabel('UI/Fleet/Ranks/WingCommander'), callback, (charID,
                       wid,
                       None,
                       const.fleetRoleWingCmdr)]]
                else:
                    subsquads = []
                for sid, s in w.squads.iteritems():
                    if canMoveSquad and not canMoveAll and sid != myself.squadID:
                        continue
                    nMembers = len(squads.get(sid, ()))
                    if nMembers >= fleetcommon.MAX_MEMBERS_IN_SQUAD and (not member or member.squadID != sid):
                        continue
                    si = sortedSquads.index(sid) + 1
                    submembers = []
                    if sid not in squadsWithCommanders:
                        submembers.append([uiutil.MenuLabel('UI/Fleet/Ranks/SquadCommander'), callback, (charID,
                          wid,
                          sid,
                          const.fleetRoleSquadCmdr)])
                    if member is None or member.squadID != sid or member.role == const.fleetRoleSquadCmdr:
                        submembers.append([uiutil.MenuLabel('UI/Fleet/Ranks/SquadMember'), callback, (charID,
                          wid,
                          sid,
                          const.fleetRoleMember)])
                    if submembers:
                        name = s.name
                        if name == '':
                            name = localization.GetByLabel('UI/Fleet/FleetSubmenus/SquadX', squadNumber=si)
                        label = uiutil.MenuLabel('UI/Fleet/FleetSubmenus/SquadNameWithNumMembers', {'squadName': name,
                         'numMembers': nMembers})
                        subsquads.append([label, submembers])

                if subsquads:
                    name = w.name
                    if name == '':
                        name = uiutil.MenuLabel('UI/Fleet/FleetSubmenus/WingX', {'wingNumber': wi + 1})
                    wingMenu.append([name, subsquads])

        return wingMenu

    def DoInviteToFleet(self, charID, wingID, squadID, role):
        sm.GetService('fleet').Invite(charID, wingID, squadID, role)

    def CorpMemberMenu(self, charID, multi = 0):
        checkInSameCorp = charID in sm.StartService('corp').GetMemberIDs()
        checkIAmDirector = const.corpRoleDirector & session.corprole == const.corpRoleDirector
        checkICanKickThem = session.charid == charID or const.corpRoleDirector & session.corprole == const.corpRoleDirector
        checkIAmCEO = sm.StartService('corp').UserIsCEO()
        checkIAmAccountant = const.corpRoleAccountant & session.corprole == const.corpRoleAccountant
        checkIBlockRoles = sm.StartService('corp').UserBlocksRoles()
        checkIsMe = session.charid == charID
        checkIAmPersonnelMgr = const.corpRolePersonnelManager & session.corprole == const.corpRolePersonnelManager
        checkIsNPC = util.IsNPC(charID)
        checkIAmInNPCCorp = util.IsNPC(session.corpid)
        checkMultiSelection = bool(multi)
        checkIsDustChar = util.IsDustCharacter(charID)
        quitCorpMenu = [[uiutil.MenuLabel('UI/Corporations/Common/RemoveAllCorpRoles'), sm.StartService('corp').RemoveAllRoles, ()], [uiutil.MenuLabel('UI/Corporations/Common/ConfirmQuitCorp'), sm.StartService('corp').KickOut, (charID,)]]
        allowRolesMenu = [[uiutil.MenuLabel('UI/Corporations/Common/ConfirmAllowCorpRoles'), sm.StartService('corp').UpdateMember, (session.charid,
           None,
           None,
           None,
           None,
           None,
           None,
           None,
           None,
           None,
           None,
           None,
           None,
           None,
           0)]]
        expelMenu = [[uiutil.MenuLabel('UI/Corporations/Common/ConfirmExpelMember'), sm.StartService('corp').KickOut, (charID,)]]
        resignMenu = [[uiutil.MenuLabel('UI/Corporations/Common/ConfirmResignAsCEO'), sm.StartService('corp').ResignFromCEO, ()]]
        menuEntries = [None]
        if not checkMultiSelection and checkInSameCorp:
            if not checkIAmDirector:
                menuEntries += [[uiutil.MenuLabel('UI/Corporations/Common/ViewCorpMemberDetails'), self.ShowCorpMemberDetails, (charID,)]]
            else:
                menuEntries += [[uiutil.MenuLabel('UI/Corporations/Common/EditCorpMember'), self.ShowCorpMemberDetails, (charID,)]]
            if checkIsMe and checkIBlockRoles:
                menuEntries += [[uiutil.MenuLabel('UI/Corporations/Common/AllowCorpRoles'), allowRolesMenu]]
        if not checkMultiSelection and checkIAmAccountant and not checkIsNPC and not checkIsDustChar:
            menuEntries += [[uiutil.MenuLabel('UI/Corporations/Common/TransferCorpCash'), sm.StartService('wallet').TransferMoney, (session.corpid,
               None,
               charID,
               None)]]
        if checkInSameCorp:
            if checkICanKickThem and checkIsMe and not checkIAmInNPCCorp and not checkIAmCEO:
                menuEntries += [[uiutil.MenuLabel('UI/Corporations/Common/QuitCorp'), quitCorpMenu]]
            if checkICanKickThem and not checkIsMe:
                menuEntries += [[uiutil.MenuLabel('UI/Corporations/Common/ExpelCorpMember'), expelMenu]]
            if checkIsMe and checkIAmCEO:
                menuEntries += [[uiutil.MenuLabel('UI/Corporations/Common/ResignAsCEO'), resignMenu]]
            if checkIAmPersonnelMgr and not checkIsNPC and not checkIsDustChar:
                menuEntries += [[uiutil.MenuLabel('UI/Corporations/Common/AwardCorpMemberDecoration'), self.AwardDecoration, [charID]]]
        return menuEntries

    def AwardDecoration(self, charIDs):
        if not charIDs:
            return
        if not type(charIDs) == list:
            charIDs = [charIDs]
        info, graphics = sm.GetService('medals').GetAllCorpMedals(session.corpid)
        options = [ (medal.title, medal.medalID) for medal in info ]
        if len(options) <= 0:
            raise UserError('MedalCreateToAward')
        cfg.eveowners.Prime(charIDs)
        hintLen = 5
        hint = ', '.join([ cfg.eveowners.Get(charID).name for charID in charIDs[:hintLen] ])
        if len(charIDs) > hintLen:
            hint += ', ...'
        ret = uix.ListWnd(options, 'generic', localization.GetByLabel('UI/Corporations/Common/AwardCorpMemberDecoration'), isModal=1, ordered=1, scrollHeaders=[localization.GetByLabel('UI/Inventory/InvItemNameShort')], hint=hint)
        if ret:
            medalID = ret[1]
            sm.StartService('medals').GiveMedalToCharacters(medalID, charIDs)

    def ShowCorpMemberDetails(self, charID):
        form.CorpMembers().MemberDetails(charID)

    def __GetInviteMenu(self, charID, submenu = None):

        def Invite(charID, channelID):
            sm.StartService('LSC').Invite(charID, channelID)

        inviteMenu = []
        submenus = {}
        for channel in sm.StartService('LSC').GetChannels():
            if sm.StartService('LSC').IsJoined(channel.channelID) and type(channel.channelID) == types.IntType:
                members = sm.StartService('LSC').GetMembers(channel.channelID)
                if members and charID not in members:
                    t = chat.GetDisplayName(channel.channelID).split('\\')
                    if submenu and len(t) == 2 and submenu == t[0] or not submenu and len(t) != 2:
                        inviteMenu += [[t[-1], Invite, (charID, channel.channelID)]]
                    elif not submenu and len(t) == 2:
                        submenus[t[0]] = 1

        for each in submenus.iterkeys():
            inviteMenu += [[each, ('isDynamic', self.__GetInviteMenu, (charID, each))]]

        inviteMenu.sort()
        inviteMenu = [[uiutil.MenuLabel('UI/Chat/StartConversation'), Invite, (charID, None)]] + inviteMenu
        return inviteMenu

    def SlashCmd(self, cmd):
        try:
            sm.RemoteSvc('slash').SlashCmd(cmd)
        except RuntimeError:
            sm.GetService('gameui').MessageBox('This only works on items at your current location.', 'Oops!', buttons=uiconst.OK)

    def GetGMTypeMenu(self, typeID, itemID = None, divs = False, unload = False):
        if not session.role & (service.ROLE_GML | service.ROLE_WORLDMOD):
            return []

        def _wrapMulti(command, what = None, maxValue = 2147483647):
            if uicore.uilib.Key(uiconst.VK_SHIFT):
                if not what:
                    what = command.split(' ', 1)[0]
                result = uix.QtyPopup(maxvalue=maxValue, minvalue=1, caption=what, label=localization.GetByLabel('UI/Common/Quantity'), hint='')
                if result:
                    qty = result['qty']
                else:
                    return
            else:
                qty = 1
            return sm.GetService('slash').SlashCmd(command % qty)

        item = cfg.invtypes.Get(typeID)
        cat = item.categoryID
        if unload:
            if type(itemID) is tuple:
                for row in self.invCache.GetInventoryFromId(itemID[0]).ListHardwareModules():
                    if row.flagID == itemID[1]:
                        itemID = row.itemID
                        break
                else:
                    itemID = None

            else:
                charge = self.godma.GetItem(itemID)
                if charge.categoryID == const.categoryCharge:
                    for row in self.invCache.GetInventoryFromId(charge.locationID).ListHardwareModules():
                        if row.flagID == charge.flagID and row.itemID != itemID:
                            itemID = row.itemID
                            break
                    else:
                        itemID = None

        gm = []
        if divs:
            gm.append(None)
        if session.role & (service.ROLE_WORLDMOD | service.ROLE_SPAWN):
            if not session.stationid:
                if cat == const.categoryShip:
                    gm.append(('WM: /Spawn this type', lambda *x: _wrapMulti('/spawnN %%d 4000 %d' % item.typeID, '/Spawn', 50)))
                    gm.append(('WM: /Unspawn this ship', lambda *x: sm.RemoteSvc('slash').SlashCmd('/unspawn %d' % itemID)))
                if cat == const.categoryEntity:
                    gm.append(('WM: /Entity deploy this type', lambda *x: _wrapMulti('/entity deploy %%d %d' % item.typeID, '/Entity', 100)))
        if item.typeID != const.typeSolarSystem and cat not in [const.categoryStation, const.categoryOwner]:
            if session.role & service.ROLE_WORLDMOD:
                gm.append(('WM: /create this type', lambda *x: _wrapMulti('/create %d %%d' % item.typeID)))
            gm.append(('GM: /load me this type', lambda *x: _wrapMulti('/load me %d %%d' % item.typeID)))
            graphicID = cfg.invtypes.Get(item.typeID).graphicID
            graphicFile = util.GraphicFile(graphicID)
            if graphicFile is '':
                graphicFile = None
            gm.append(('res', [('typeID: ' + str(item.typeID), blue.pyos.SetClipboardData, (str(item.typeID),)), ('graphicID: ' + str(graphicID), blue.pyos.SetClipboardData, (str(graphicID),)), ('graphicFile: ' + str(graphicFile), blue.pyos.SetClipboardData, (str(graphicFile),))]))
        if cfg.IsFittableCategory(cat):
            gm.append(('GM: /fit me this type', lambda *x: _wrapMulti('/loop %%d /fit me %d' % item.typeID, '/Fit', 8)))
            if unload:
                if itemID:
                    gm.append(('GM: /unload me this item', lambda *x: sm.RemoteSvc('slash').SlashCmd('/unload me %d' % itemID)))
                gm.append(('GM: /unload me this type', lambda *x: sm.RemoteSvc('slash').SlashCmd('/unload me %d' % item.typeID)))
                if itemID and self.godma.GetItem(itemID).damage:
                    gm.append(('GM: Repair this module', lambda *x: sm.RemoteSvc('slash').SlashCmd('/heal %d' % itemID)))
        if itemID:
            gm.append(('GM: Inspect Attributes', self.InspectAttributes, (itemID, typeID)))
        if session.role & service.ROLE_PROGRAMMER:
            gm.append(('PROG: Modify Attributes', ('isDynamic', self.AttributeMenu, (itemID, typeID))))
        if divs:
            gm.append(None)
        return gm

    def InspectAttributes(self, itemID, typeID):
        form.AttributeInspector.Open(itemID=itemID, typeID=typeID)

    def NPCInfoMenu(self, item):
        lst = []
        action = 'gd/type.py?action=Type&typeID=' + str(item.typeID)
        lst.append(('Overview', self.GetFromESP, (action,)))
        action = 'gd/type.py?action=TypeDogma&typeID=' + str(item.typeID)
        lst.append(('Dogma Attributes', self.GetFromESP, (action,)))
        action = 'gd/npc.py?action=GetNPCInfo&shipID=' + str(item.itemID) + '&solarSystemID=' + str(session.solarsystemid)
        lst.append(('Info', self.GetFromESP, (action,)))
        return lst

    def AttributeMenu(self, itemID, typeID):
        d = sm.StartService('info').GetAttrDict(typeID)
        statemgr = sm.StartService('godma').GetStateManager()
        a = statemgr.attributesByID
        lst = []
        for id, baseValue in d.iteritems():
            attrName = a[id].attributeName
            try:
                actualValue = statemgr.GetAttribute(itemID, attrName)
            except:
                sys.exc_clear()
                actualValue = baseValue

            lst.append(('%s - %s' % (attrName, actualValue), self.SetDogmaAttribute, (itemID, attrName, actualValue)))

        lst.sort(lambda x, y: cmp(x[0], y[0]))
        return lst

    def SetDogmaAttribute(self, itemID, attrName, actualValue):
        ret = uix.QtyPopup(None, None, actualValue, 'Set Dogma Attribute for <b>%s</b>' % attrName, 'Set Dogma Attribute', digits=5)
        if ret:
            cmd = '/dogma %s %s = %s' % (itemID, attrName, ret['qty'])
            self.SlashCmd(cmd)

    def GagPopup(self, charID, numMinutes):
        reason = 'Gagged for Spamming'
        ret = uiutil.NamePopup('Gag User', 'Enter Reason', reason)
        if ret:
            self.SlashCmd('/gag %s "%s" %s' % (charID, ret, numMinutes))

    def ReportISKSpammer(self, charID, channelID):
        if eve.Message('ConfirmReportISKSpammer', {'name': cfg.eveowners.Get(charID).name}, uiconst.YESNO) != uiconst.ID_YES:
            return
        if charID == session.charid:
            raise UserError('ReportISKSpammerCannotReportYourself')
        lscSvc = sm.GetService('LSC')
        c = lscSvc.GetChannelWindow(channelID)
        entries = copy.copy(c.output.GetNodes())
        spamEntries = []
        for e in entries:
            if e.charid == charID:
                who, txt, charid, time, colorkey = e.msg
                spamEntries.append('[%s] %s > %s' % (util.FmtDate(time, 'nl'), who, txt))

        if len(spamEntries) == 0:
            raise UserError('ReportISKSpammerNoEntries')
        spamEntries.reverse()
        spamEntries = spamEntries[:10]
        spammers = getattr(lscSvc, 'spammerList', set())
        if charID in spammers:
            return
        spammers.add(charID)
        lscSvc.spammerList = spammers
        c.LoadMessages()
        channel = lscSvc.channels.get(channelID, None)
        if channel and channel.info:
            channelID = channel.info.displayName
        sm.RemoteSvc('userSvc').ReportISKSpammer(charID, channelID, spamEntries)

    def BanIskSpammer(self, charID):
        if eve.Message('ConfirmBanIskSpammer', {'name': cfg.eveowners.Get(charID).name}, uiconst.YESNO) != uiconst.ID_YES:
            return
        self.SlashCmd('/baniskspammer %s' % charID)

    def GagIskSpammer(self, charID):
        if eve.Message('ConfirmGagIskSpammer', {'name': cfg.eveowners.Get(charID).name}, uiconst.YESNO) != uiconst.ID_YES:
            return
        self.SlashCmd('/gagiskspammer %s' % charID)

    def GetFromESP(self, action):
        espaddy = login.GetServerInfo().espUrl
        blue.os.ShellExecute('http://%s/%s' % (espaddy, action))

    def GetGMMenu(self, itemID = None, slimItem = None, charID = None, invItem = None, mapItem = None, typeID = None):
        if not session.role & (service.ROLE_GML | service.ROLE_WORLDMOD):
            if charID and session.role & service.ROLE_LEGIONEER:
                return [('Gag ISK Spammer', self.GagIskSpammer, (charID,))]
            return []
        gm = [(str(itemID or charID), blue.pyos.SetClipboardData, (str(itemID or charID),))]
        if mapItem and not slimItem:
            gm.append(('TR me here!', sm.RemoteSvc('slash').SlashCmd, ('/tr me ' + str(mapItem.itemID),)))
            gm.append(None)
        elif charID:
            gm.append(('TR me to %s' % cfg.eveowners.Get(charID).name, sm.RemoteSvc('slash').SlashCmd, ('/tr me ' + str(charID),)))
            gm.append(None)
        elif slimItem:
            gm.append(('TR me here!', sm.RemoteSvc('slash').SlashCmd, ('/tr me ' + str(itemID),)))
            gm.append(None)
        elif itemID:
            gm.append(('TR me here!', sm.RemoteSvc('slash').SlashCmd, ('/tr me ' + str(itemID),)))
            gm.append(None)
        if invItem:
            gm += [('Copy ID/Qty', self.CopyItemIDAndMaybeQuantityToClipboard, (invItem,))]
            typeText = 'copy typeID (%s)' % invItem.typeID
            gm += [(typeText, blue.pyos.SetClipboardData, (str(invItem.typeID),))]
            gm.append(('Edit', self.GetAdamEditType, [invItem.typeID]))
            gm.append(None)
            typeID = invItem.typeID
            gm.append(('typeID: ' + str(typeID) + ' (%s)' % cfg.invtypes.Get(typeID).name, blue.pyos.SetClipboardData, (str(typeID),)))
            invType = cfg.invtypes.Get(typeID)
            group = invType.groupID
            gm.append(('groupID: ' + str(group) + ' (%s)' % invType.Group().name, blue.pyos.SetClipboardData, (str(group),)))
            category = invType.categoryID
            categoryName = cfg.invcategories.Get(category).name
            gm.append(('categID: ' + str(category) + ' (%s)' % categoryName, blue.pyos.SetClipboardData, (str(category),)))
            graphic = invType.Graphic()
            if graphic is not None:
                gm.append(('graphicID: ' + str(invType.graphicID), blue.pyos.SetClipboardData, (str(invType.graphicID),)))
                if hasattr(graphic, 'graphicFile'):
                    gm.append(('graphicFile: ' + str(graphic.graphicFile), blue.pyos.SetClipboardData, (str(graphic.graphicFile),)))
        if charID and not util.IsNPC(charID):
            action = 'gm/character.py?action=Character&characterID=' + str(charID)
            gm.append(('Show in ESP', self.GetFromESP, (action,)))
            gm.append(None)
            gm.append(('Gag ISK Spammer', self.GagIskSpammer, (charID,)))
            gm.append(('Ban ISK Spammer', self.BanIskSpammer, (charID,)))
            action = 'gm/users.py?action=BanUserByCharacterID&characterID=' + str(charID)
            gm.append(('Ban User (ESP)', self.GetFromESP, (action,)))
            gm += [('Gag User', [('30 minutes', self.GagPopup, (charID, 30)),
               ('1 hour', self.GagPopup, (charID, 60)),
               ('6 hours', self.GagPopup, (charID, 360)),
               ('24 hours', self.GagPopup, (charID, 1440)),
               None,
               ('Ungag', lambda *x: self.SlashCmd('/ungag %s' % charID))])]
        gm.append(None)
        item = slimItem or invItem
        if item:
            if item.categoryID == const.categoryShip and (item.singleton or not session.stationid):
                import dna
                if item.ownerID in [session.corpid, session.charid] or session.role & service.ROLE_WORLDMOD:
                    try:
                        menu = dna.Ship().ImportFromShip(shipID=item.itemID, ownerID=item.ownerID, deferred=True).GetMenuInline(spiffy=False, fit=item.itemID != session.shipid)
                        gm.append(('Copycat', menu))
                    except RuntimeError:
                        pass

                gm += [('/Online modules', lambda shipID = item.itemID: self.SlashCmd('/online %d' % shipID))]
            gm += self.GetGMTypeMenu(item.typeID, itemID=item.itemID)
            if getattr(slimItem, 'categoryID', None) == const.categoryEntity or getattr(slimItem, 'groupID', None) == const.groupWreck:
                gm.append(('NPC Info', ('isDynamic', self.NPCInfoMenu, (item,))))
            gm.append(None)
        elif typeID:
            gm += self.GetGMTypeMenu(typeID)
        if session.role & service.ROLE_CONTENT:
            if slimItem:
                if getattr(slimItem, 'dunObjectID', None) != None:
                    if not sm.StartService('scenario').IsSelected(itemID):
                        gm.append(('Add to Selection', sm.StartService('scenario').AddSelected, (itemID,)))
                    else:
                        gm.append(('Remove from Selection', sm.StartService('scenario').RemoveSelected, (itemID,)))
        if slimItem:
            itemID = slimItem.itemID
            graphicID = cfg.invtypes.Get(slimItem.typeID).graphicID
            graphicFile = util.GraphicFile(graphicID)
            if graphicFile is '':
                graphicFile = None
            g = cfg.graphics.GetIfExists(graphicID)
            raceID = getattr(g, 'gfxRaceID', None)
            raceName = spaceObject.BOOSTER_GFX_SND_RESPATHS.get(raceID, ('empty', 'empty'))[1]
            ball = sm.StartService('michelle').GetBallpark().GetBall(slimItem.itemID)
            subMenu = self.GetGMStructureStateMenu(itemID, slimItem, charID, invItem, mapItem)
            if len(subMenu) > 0:
                gm += [('Change State', subMenu)]
            gm += self.GetGMBallsAndBoxesMenu(itemID, slimItem, charID, invItem, mapItem)
            currentLODstr = 'INVALID'
            if ball is not None:
                if hasattr(ball, 'model'):
                    if ball.model is not None:
                        if hasattr(ball.model, 'mesh'):
                            if ball.model.mesh is not None:
                                currentLODstr = ball.model.mesh.geometryResPath
            gm.append(None)
            gm.append(('charID: ' + self.GetOwnerLabel(slimItem.charID), blue.pyos.SetClipboardData, (str(slimItem.charID),)))
            gm.append(('ownerID: ' + self.GetOwnerLabel(slimItem.ownerID), blue.pyos.SetClipboardData, (str(slimItem.ownerID),)))
            gm.append(('corpID: ' + self.GetOwnerLabel(slimItem.corpID), blue.pyos.SetClipboardData, (str(slimItem.corpID),)))
            gm.append(('allianceID: ' + self.GetOwnerLabel(slimItem.allianceID), blue.pyos.SetClipboardData, (str(slimItem.allianceID),)))
            if hasattr(slimItem, 'districtID'):
                gm.append(('districtID: ' + str(slimItem.districtID), blue.pyos.SetClipboardData, (str(slimItem.districtID),)))
            gm.append(None)
            gm.append(('typeID: ' + str(slimItem.typeID) + ' (%s)' % cfg.invtypes.Get(slimItem.typeID).name, blue.pyos.SetClipboardData, (str(slimItem.typeID),)))
            gm.append(('groupID: ' + str(slimItem.groupID) + ' (%s)' % cfg.invgroups.Get(slimItem.groupID).name, blue.pyos.SetClipboardData, (str(slimItem.groupID),)))
            gm.append(('categID: ' + str(slimItem.categoryID) + ' (%s)' % cfg.invcategories.Get(slimItem.categoryID).name, blue.pyos.SetClipboardData, (str(slimItem.categoryID),)))
            gm.append(('res', [('graphicID: ' + str(graphicID), blue.pyos.SetClipboardData, (str(graphicID),)),
              ('graphicFile: ' + str(graphicFile), blue.pyos.SetClipboardData, (str(graphicFile),)),
              ('gfxRaceID: ' + str(raceName), blue.pyos.SetClipboardData, (str(raceName),)),
              ('current LOD: ' + currentLODstr, blue.pyos.SetClipboardData, (currentLODstr,)),
              ('Save red file', self.SaveRedFile, (ball, graphicFile))]))
            if slimItem.groupID == const.groupPlanet:
                if ball is not None:
                    if ball.typeID == const.typePlanetEarthlike:
                        gm.append(('DUST', [('current: ' + str(len(ball.districts)), blue.pyos.SetClipboardData, (str(len(ball.districts)),)),
                          None,
                          ('+1 district', self.DustAddDistricts, (1, ball)),
                          ('+10 district', self.DustAddDistricts, (10, ball)),
                          ('+50 district', self.DustAddDistricts, (50, ball)),
                          ('clear districts', self.DustClearDistricts, (ball,)),
                          None,
                          ('start battles', self.DustEnableBattles, (True, ball)),
                          ('stop battles', self.DustEnableBattles, (False, ball)),
                          None,
                          ('BOOM!', self.DustStartExplosions, (True, ball)),
                          ('Stop BOOM!', self.DustStartExplosions, (False, ball))]))
            if slimItem.groupID == const.groupSatellite:
                gm.append(('Orbital Strike', [('Request Strike', sm.RemoteSvc('slash').SlashCmd, ('/osrequest ' + str(slimItem.districtID),)), ('Cancel Strike', sm.RemoteSvc('slash').SlashCmd, ('/oscancel ' + str(slimItem.districtID),))]))
            gm.append(None)
            gm.append(('Copy Coordinates', self.CopyCoordinates, (itemID,)))
            gm.append(None)
            try:
                state = slimItem.orbitalState
                if state in (entities.STATE_UNANCHORING,
                 entities.STATE_ONLINING,
                 entities.STATE_ANCHORING,
                 entities.STATE_OPERATING,
                 entities.STATE_OFFLINING,
                 entities.STATE_SHIELD_REINFORCE):
                    stateText = localization.GetByLabel(pos.DISPLAY_NAMES[pos.Entity2DB(state)])
                    gm.append(('End orbital state change (%s)' % stateText, self.CompleteOrbitalStateChange, (itemID,)))
                elif state == entities.STATE_ANCHORED:
                    upgradeType = sm.GetService('godma').GetTypeAttribute2(slimItem.typeID, const.attributeConstructionType)
                    if upgradeType is not None:
                        gm.append(('Upgrade to %s' % cfg.invtypes.Get(upgradeType).typeName, self.GMUpgradeOrbital, (itemID,)))
                gm.append(('GM: Take Control', self.TakeOrbitalOwnership, (itemID, slimItem.planetID)))
            except ValueError:
                pass

        gm.append(None)
        dict = {'CHARID': charID,
         'ITEMID': itemID,
         'ID': charID or itemID}
        for i in range(20):
            item = prefs.GetValue('gmmenuslash%d' % i, None)
            if item:
                for k, v in dict.iteritems():
                    if ' %s ' % k in item and v:
                        item = item.replace(k, str(v))
                        break
                else:
                    continue

                gm.append((item, sm.RemoteSvc('slash').SlashCmd, (item,)))

        return gm

    def SaveRedFile(self, ball, graphicFile):
        dlgRes = uix.GetFileDialog(multiSelect=False, selectionType=uix.SEL_FOLDERS)
        if dlgRes is not None:
            path = dlgRes.Get('folders')[0]
            graphicFile = graphicFile.split('/')[-1]
            graphicFile = graphicFile.replace('.blue', '.red')
            savePath = path + '\\' + graphicFile
            trinity.Save(ball.model, savePath)
            log.LogError('GM menu: Saved object as:', savePath)

    def DustAddDistricts(self, count, ball):
        for each in range(0, count):
            randomCenterNormal = geo2.Vec3Normalize((random.uniform(-1.0, 1.0), random.uniform(-1.0, 1.0), random.uniform(-1.0, 1.0)))
            ball.AddDistrict('unique' + str(len(ball.districts)), randomCenterNormal, 0.1, False)

    def DustClearDistricts(self, ball):
        ball.DelAllDistricts()

    def DustEnableBattles(self, enable, ball):
        for key, value in ball.districts.iteritems():
            ball.EnableBattleForDistrict(key, enable)

    def DustStartExplosions(self, enable, ball):

        def TriggerExplosions():
            while True:
                for key, value in ball.districts.iteritems():
                    availableFX = [spaceObject.Planet.ORBBOMB_IMPACT_FX_EM, spaceObject.Planet.ORBBOMB_IMPACT_FX_HYBRID, spaceObject.Planet.ORBBOMB_IMPACT_FX_LASER]
                    fxID = random.randint(0, len(availableFX) - 1)
                    ball.AddExplosion(key, availableFX[fxID], 0.4)

                blue.synchro.SleepSim(10000.0)

        if enable:
            if getattr(self, 'triggerExplosionThreadObj', None) is None:
                self.triggerExplosionThreadObj = uthread.new(TriggerExplosions)
        elif getattr(self, 'triggerExplosionThreadObj', None) is not None:
            self.triggerExplosionThreadObj.kill()
            self.triggerExplosionThreadObj = None

    def GetGMStructureStateMenu(self, itemID = None, slimItem = None, charID = None, invItem = None, mapItem = None):
        subMenu = []
        if hasattr(slimItem, 'posState') and slimItem.posState is not None:
            currentState = slimItem.posState
            if currentState not in pos.ONLINE_STABLE_STATES:
                if currentState == pos.STRUCTURE_ANCHORED:
                    subMenu.append(('Online', sm.RemoteSvc('slash').SlashCmd, ('/pos online ' + str(itemID),)))
                    subMenu.append(('Unanchor', sm.RemoteSvc('slash').SlashCmd, ('/pos unanchor ' + str(itemID),)))
                elif currentState == pos.STRUCTURE_UNANCHORED:
                    subMenu.append(('Anchor', sm.RemoteSvc('slash').SlashCmd, ('/pos anchor ' + str(itemID),)))
            else:
                if getattr(slimItem, 'posTimestamp', None) is not None:
                    subMenu.append(('Complete State', sm.RemoteSvc('slash').SlashCmd, ('/sov complete ' + str(itemID),)))
                subMenu.append(('Offline', sm.RemoteSvc('slash').SlashCmd, ('/pos offline ' + str(itemID),)))
        if hasattr(slimItem, 'structureState') and slimItem.structureState != None and slimItem.structureState in [pos.STRUCTURE_SHIELD_REINFORCE, pos.STRUCTURE_ARMOR_REINFORCE]:
            subMenu.append(('Complete State', sm.RemoteSvc('slash').SlashCmd, ('/sov complete ' + str(itemID),)))
        return subMenu

    def GetGMBallsAndBoxesMenu(self, itemID = None, slimItem = None, charID = None, invItem = None, mapItem = None):
        spaceMgr = sm.StartService('space')
        partMenu = [('Stop partition box display ', spaceMgr.StopPartitionDisplayTimer, ()),
         None,
         ('Start partition box display limit = 0', spaceMgr.StartPartitionDisplayTimer, (0,)),
         ('Start partition box display limit = 1', spaceMgr.StartPartitionDisplayTimer, (1,)),
         ('Start partition box display limit = 2', spaceMgr.StartPartitionDisplayTimer, (2,)),
         ('Start partition box display limit = 3', spaceMgr.StartPartitionDisplayTimer, (3,)),
         ('Start partition box display limit = 4', spaceMgr.StartPartitionDisplayTimer, (4,)),
         ('Start partition box display limit = 5', spaceMgr.StartPartitionDisplayTimer, (5,)),
         ('Start partition box display limit = 6', spaceMgr.StartPartitionDisplayTimer, (6,)),
         ('Start partition box display limit = 7', spaceMgr.StartPartitionDisplayTimer, (7,)),
         None,
         ('Show single level', self.ChangePartitionLevel, (0,)),
         ('Show selected level and up', self.ChangePartitionLevel, (1,))]
        subMenu = [('Balls & Boxes', [('Hide ball info', self.ShowDestinyBalls, (itemID, UNLOAD_MINIBALLS)),
           ('Show Miniball Runtime Data', self.ShowDestinyBalls, (itemID, SHOW_RUNTIME_MINIBALL_DATA)),
           ('Show Miniball Editor Data', self.ShowDestinyBalls, (itemID, SHOW_EDITOR_MINIBALL_DATA)),
           None,
           ('Wireframe Destiny Ball', self.ShowDestinyBalls, (itemID, SHOW_DESTINY_BALL)),
           ('Wireframe BoundingSphere', self.ShowDestinyBalls, (itemID, SHOW_BOUNDING_SPHERE)),
           None,
           ('Partition', partMenu)]), ('Damage Locators', [('Toggle damage locators', self.ShowDamageLocators, (itemID,))])]
        return subMenu

    def GetOwnerLabel(self, ownerID):
        name = ''
        if ownerID != None:
            try:
                name = ' (' + cfg.eveowners.Get(ownerID).name + ')    '
            except:
                sys.exc_clear()

        return str(ownerID) + name

    def GetAdamEditType(self, typeID):
        uthread.new(self.ClickURL, 'http://adam:50001/gd/type.py?action=EditTypeDogmaForm&typeID=%s' % typeID)

    def ClickURL(self, url, *args):
        blue.os.ShellExecute(url)

    def SolarsystemScanMenu(self, scanResultID):
        warptoLabel = self.DefaultWarpToLabel()
        defaultWarpDist = self.GetDefaultActionDistance('WarpTo')
        ret = [(warptoLabel, self.WarpToScanResult, (scanResultID, defaultWarpDist)), (uiutil.MenuLabel('UI/Inflight/Submenus/WarpToWithin'), self.WarpToMenu(self.WarpToScanResult, scanResultID))]
        if self.CheckImFleetLeader():
            ret.extend([(uiutil.MenuLabel('UI/Fleet/WarpFleet'), self.WarpFleetToScanResult, (scanResultID, float(defaultWarpDist))), (uiutil.MenuLabel('UI/Fleet/FleetSubmenus/WarpFleetToWithin'), self.WarpToMenu(self.WarpFleetToScanResult, scanResultID))])
        elif self.CheckImWingCmdr():
            ret.extend([(uiutil.MenuLabel('UI/Fleet/WarpWing'), self.WarpFleetToScanResult, (scanResultID, float(defaultWarpDist))), (uiutil.MenuLabel('UI/Fleet/FleetSubmenus/WarpWingToWithin'), self.WarpToMenu(self.WarpFleetToScanResult, scanResultID))])
        elif self.CheckImSquadCmdr():
            ret.extend([(uiutil.MenuLabel('UI/Fleet/WarpSquad'), self.WarpFleetToScanResult, (scanResultID, float(defaultWarpDist))), (uiutil.MenuLabel('UI/Fleet/FleetSubmenus/WarpSquadToWithin'), self.WarpToMenu(self.WarpFleetToScanResult, scanResultID))])
        return ret

    def WarpToScanResult(self, scanResultID, minRange = None):
        self._WarpXToScanResult(scanResultID, minRange)

    def WarpFleetToScanResult(self, scanResultID, minRange = None):
        self._WarpXToScanResult(scanResultID, minRange, fleet=True)

    def _WarpXToScanResult(self, scanResultID, minRange = None, fleet = False):
        bp = sm.StartService('michelle').GetRemotePark()
        if bp is not None:
            if not sm.GetService('machoNet').GetGlobalConfig().get('newAutoNavigationKillSwitch', False):
                sm.GetService('autoPilot').CancelSystemNavigation()
            bp.CmdWarpToStuff('scan', scanResultID, minRange=minRange, fleet=fleet)
            sm.StartService('space').WarpDestination(scanResultID, None, None)

    @telemetry.ZONE_METHOD
    def CelestialMenu(self, itemID, mapItem = None, slimItem = None, noTrace = 0, typeID = None, parentID = None, bookmark = None, itemIDs = [], ignoreTypeCheck = 0, ignoreDroneMenu = 0, filterFunc = None, hint = None, ignoreMarketDetails = 1, ignoreShipConfig = True):
        if type(itemID) == list:
            menus = []
            for data in itemID:
                m = self._CelestialMenu(data, ignoreTypeCheck, ignoreDroneMenu, filterFunc, hint, ignoreMarketDetails, len(itemID) > 1, ignoreShipConfig=ignoreShipConfig)
                menus.append(m)

            return self.MergeMenus(menus)
        else:
            ret = self._CelestialMenu((itemID,
             mapItem,
             slimItem,
             noTrace,
             typeID,
             parentID,
             bookmark), ignoreTypeCheck, ignoreDroneMenu, filterFunc, hint, ignoreMarketDetails)
            return self.MergeMenus([ret])

    @telemetry.ZONE_METHOD
    def _CelestialMenu(self, data, ignoreTypeCheck = 0, ignoreDroneMenu = 0, filterFunc = None, hint = None, ignoreMarketDetails = 1, multi = 0, ignoreShipConfig = False):
        itemID, mapItem, slimItem, noTrace, typeID, parentID, bookmark = data
        categoryID = None
        bp = sm.StartService('michelle').GetBallpark()
        fleetSvc = sm.GetService('fleet')
        if bp:
            slimItem = slimItem or bp.GetInvItem(itemID)
        if slimItem:
            typeID = slimItem.typeID
            parentID = sm.StartService('map').GetParent(itemID) or session.solarsystemid
            categoryID = slimItem.categoryID
        mapItemID = None
        if bookmark:
            typeID = bookmark.typeID
            parentID = bookmark.locationID
            itemID = itemID or bookmark.locationID
        else:
            mapItem = mapItem or sm.StartService('map').GetItem(itemID)
            if mapItem:
                typeID = mapItem.typeID
                parentID = getattr(mapItem, 'locationID', None) or const.locationUniverse
                if typeID == const.groupSolarSystem:
                    mapItemID = mapItem.itemID
        if typeID is None or categoryID and categoryID == const.categoryCharge:
            return []
        invType = cfg.invtypes.Get(typeID)
        groupID = invType.groupID
        invGroup = cfg.invgroups.Get(groupID)
        groupName = invGroup.name
        categoryID = categoryID or invGroup.categoryID
        godmaSM = self.godma.GetStateManager()
        shipItem = self.godma.GetStateManager().GetItem(session.shipid)
        isMyShip = itemID == session.shipid
        otherBall = bp and bp.GetBall(itemID) or None
        ownBall = bp and bp.GetBall(session.shipid) or None
        dist = otherBall and max(0, otherBall.surfaceDist)
        otherCharID = slimItem and (slimItem.charID or slimItem.ownerID) or None
        if parentID is None and groupID == const.groupStation and itemID:
            tmp = sm.StartService('ui').GetStation(itemID)
            if tmp is not None:
                parentID = tmp.solarSystemID
        dist = self.FindDist(dist, bookmark, ownBall, bp)
        checkMultiCategs1 = categoryID in (const.categoryEntity, const.categoryDrone, const.categoryShip)
        niceRange = dist and util.FmtDist(dist) or localization.GetByLabel('UI/Inflight/NoDistanceAvailable')
        checkIsMine = bool(slimItem) and slimItem.ownerID == session.charid
        checkIsMyCorps = bool(slimItem) and slimItem.ownerID == session.corpid
        checkIsMineOrCorps = bool(slimItem) and (slimItem.ownerID == session.charid or slimItem.ownerID == session.corpid)
        checkIsMineOrCorpsOrAlliances = bool(slimItem) and (slimItem.ownerID == session.charid or slimItem.ownerID == session.corpid or session.allianceid and slimItem.allianceID == session.allianceid)
        checkIsFree = bool(otherBall) and otherBall.isFree
        checkBP = bool(bp)
        checkMyShip = isMyShip
        checkInCapsule = itemID == session.shipid and groupID == const.groupCapsule
        checkShipBusy = bool(otherBall) and otherBall.isInteractive
        checkInSpace = bool(session.solarsystemid)
        checkInSystem = dist is not None and (bp and itemID in bp.balls or parentID == session.solarsystemid)
        checkIsObserving = sm.GetService('target').IsObserving()
        checkStation = groupID == const.groupStation
        checkPlanetCustomsOffice = groupID == const.groupPlanetaryCustomsOffices
        checkPlanet = groupID == const.groupPlanet
        checkMoon = groupID == const.groupMoon
        checkThisPlanetOpen = sm.GetService('viewState').IsViewActive('planet') and sm.GetService('planetUI').planetID == itemID
        checkStargate = bool(slimItem) and groupID == const.groupStargate
        checkWarpgate = groupID == const.groupWarpGate
        checkWormhole = groupID == const.groupWormhole
        checkControlTower = groupID == const.groupControlTower
        checkSentry = groupID in (const.groupMobileMissileSentry, const.groupMobileProjectileSentry, const.groupMobileHybridSentry)
        checkLaserSentry = groupID == const.groupMobileLaserSentry
        checkShipMaintainer = groupID == const.groupShipMaintenanceArray
        checkCorpHangarArray = groupID == const.groupCorporateHangarArray
        checkAssemblyArray = groupID == const.groupAssemblyArray
        checkMobileLaboratory = groupID == const.groupMobileLaboratory
        checkSilo = groupID == const.groupSilo
        checkReactor = groupID == const.groupMobileReactor
        checkRefinery = groupID == const.groupRefiningArray
        checkContainer = groupID in (const.groupWreck,
         const.groupCargoContainer,
         const.groupSpawnContainer,
         const.groupSecureCargoContainer,
         const.groupAuditLogSecureContainer,
         const.groupFreightContainer,
         const.groupDeadspaceOverseersBelongings,
         const.groupMissionContainer)
        checkCynoField = typeID == const.typeCynosuralFieldI
        checkConstructionPf = groupID in (const.groupConstructionPlatform, const.groupStationUpgradePlatform, const.groupStationImprovementPlatform)
        checkShip = categoryID == const.categoryShip
        checkSpacePig = (groupID == const.groupAgentsinSpace or groupID == const.groupDestructibleAgentsInSpace) and bool(sm.StartService('godma').GetType(typeID).agentID)
        checkIfShipMAShip = slimItem and categoryID == const.categoryShip and bool(godmaSM.GetType(typeID).hasShipMaintenanceBay)
        checkIfShipFHShip = slimItem and categoryID == const.categoryShip and bool(godmaSM.GetType(typeID).hasFleetHangars)
        checkIfShipCloneShip = slimItem and bool(godmaSM.GetType(typeID).canReceiveCloneJumps)
        checkSolarSystem = groupID == const.groupSolarSystem
        checkWreck = groupID == const.groupWreck
        checkZeroSecSpace = checkInSpace and sm.StartService('map').GetSecurityClass(session.solarsystemid) == const.securityClassZeroSec
        checkIfShipDroneBay = slimItem and categoryID == const.categoryShip and bool(godmaSM.GetType(typeID).droneCapacity or godmaSM.GetType(typeID).techLevel == 3)
        checkIfShipFuelBay = slimItem and categoryID == const.categoryShip and bool(godmaSM.GetType(typeID).specialFuelBayCapacity)
        checkIfShipOreHold = slimItem and categoryID == const.categoryShip and bool(godmaSM.GetType(typeID).specialOreHoldCapacity)
        checkIfShipGasHold = slimItem and categoryID == const.categoryShip and bool(godmaSM.GetType(typeID).specialGasHoldCapacity)
        checkIfShipMineralHold = slimItem and categoryID == const.categoryShip and bool(godmaSM.GetType(typeID).specialMineralHoldCapacity)
        checkIfShipSalvageHold = slimItem and categoryID == const.categoryShip and bool(godmaSM.GetType(typeID).specialSalvageHoldCapacity)
        checkIfShipShipHold = slimItem and categoryID == const.categoryShip and bool(godmaSM.GetType(typeID).specialShipHoldCapacity)
        checkIfShipSmallShipHold = slimItem and categoryID == const.categoryShip and bool(godmaSM.GetType(typeID).specialSmallShipHoldCapacity)
        checkIfShipMediumShipHold = slimItem and categoryID == const.categoryShip and bool(godmaSM.GetType(typeID).specialMediumShipHoldCapacity)
        checkIfShipLargeShipHold = slimItem and categoryID == const.categoryShip and bool(godmaSM.GetType(typeID).specialLargeShipHoldCapacity)
        checkIfShipIndustrialShipHold = slimItem and categoryID == const.categoryShip and bool(godmaSM.GetType(typeID).specialIndustrialShipHoldCapacity)
        checkIfShipAmmoHold = slimItem and categoryID == const.categoryShip and bool(godmaSM.GetType(typeID).specialAmmoHoldCapacity)
        checkIfShipCommandCenterHold = slimItem and categoryID == const.categoryShip and bool(godmaSM.GetType(typeID).specialCommandCenterHoldCapacity)
        checkIfShipPlanetaryCommoditiesHold = slimItem and categoryID == const.categoryShip and bool(godmaSM.GetType(typeID).specialPlanetaryCommoditiesHoldCapacity)
        checkIfShipHasQuafeBay = slimItem and categoryID == const.categoryShip and bool(godmaSM.GetType(typeID).specialQuafeHoldCapacity)
        checkIfMaterialsHold = slimItem and bool(godmaSM.GetType(typeID).specialMaterialBayCapacity)
        checkIfCanUpgrade = slimItem and categoryID == const.categoryOrbital and slimItem.orbitalState == entities.STATE_ANCHORED
        maxTransferDistance = max(getattr(godmaSM.GetType(typeID), 'maxOperationalDistance', 0), const.maxCargoContainerTransferDistance)
        maxLookatDist = sm.GetService('camera').maxLookatRange
        checkWarpDist = dist is not None and dist > const.minWarpDistance
        checkApproachDist = dist is not None and dist < const.minWarpDistance
        checkAlignTo = dist is not None and dist > const.minWarpDistance
        checkJumpDist = dist is not None and dist < const.maxStargateJumpingDistance
        checkWormholeDist = dist is not None and dist < const.maxWormholeEnterDistance
        checkTransferDist = dist is not None and dist < maxTransferDistance
        checkConfigDist = dist is not None and dist < const.maxConfigureDistance
        checkLookatDist = dist is not None and (dist < maxLookatDist or checkIsObserving)
        checkTargetingRange = dist is not None and shipItem is not None and shipItem and dist < shipItem.maxTargetRange
        checkSpacePigDist = dist is not None and dist < sm.StartService('godma').GetType(typeID).agentCommRange
        checkDistNone = dist is None
        checkWarpActive = ownBall and ownBall.mode == destiny.DSTBALL_WARP
        checkCanUseGate = slimItem and shipItem is not None and not shipItem.canNotUseStargates
        checkJumpThrough = slimItem and sm.GetService('fleet').CanJumpThrough(slimItem)
        checkWreckViewed = checkWreck and sm.GetService('wreck').IsViewedWreck(itemID)
        checkFleet = bool(session.fleetid)
        checkIfImCommander = self.ImFleetCommander()
        checkEnemySpotted = sm.GetService('fleet').CurrentFleetBroadcastOnItem(itemID, state.gbEnemySpotted)
        checkHasMarketGroup = cfg.invtypes.Get(typeID).marketGroupID is not None and not ignoreMarketDetails
        checkIsPublished = cfg.invtypes.Get(typeID).published
        checkMultiSelection = bool(multi)
        checkIfLandmark = itemID and itemID < 0
        checkIfAgentBookmark = bookmark and getattr(bookmark, 'agentID', 0) and hasattr(bookmark, 'locationNumber')
        checkIfReadonlyBookmark = bookmark and type(getattr(bookmark, 'bookmarkID', 0)) == types.TupleType
        menuEntries = MenuList()
        defaultWarpDist = sm.GetService('menu').GetDefaultActionDistance('WarpTo')
        m = MenuList()
        if groupID == const.groupOrbitalTarget:
            return [[uiutil.MenuLabel('UI/Commands/ShowInfo'), self.ShowInfo, (typeID,
               itemID,
               0,
               None,
               parentID)]]
        if bookmark:
            checkBookmarkWarpTo = dist is not None and (itemID == session.solarsystemid or parentID == session.solarsystemid)
            checkBookmarkDeadspace = bool(getattr(bookmark, 'deadspace', 0))
            if slimItem:
                if not checkMultiSelection:
                    menuEntries += [[uiutil.MenuLabel('UI/Commands/ShowInfo'), self.ShowInfo, (slimItem.typeID,
                       slimItem.itemID,
                       0,
                       None,
                       None)]]
            if checkInSpace and not checkWarpActive:
                if checkInSystem and checkApproachDist:
                    menuEntries += [[uiutil.MenuLabel('UI/Inflight/ApproachLocationActionGroup'), self.ApproachLocation, (bookmark,)]]
                if checkBookmarkWarpTo and checkWarpDist:
                    if not checkBookmarkDeadspace:
                        label = uiutil.MenuLabel('UI/Inflight/WarpToBookmarkWithinDistance', {'warpToDistance': util.FmtDist(float(defaultWarpDist))})
                        menuEntries += [[label, self.WarpToBookmark, (bookmark, float(defaultWarpDist))]]
                        menuEntries += [[uiutil.MenuLabel('UI/Inflight/WarpToBookmark'), self.WarpToMenu(self.WarpToBookmark, bookmark)]]
                        if checkFleet:
                            if self.CheckImFleetLeader():
                                label = uiutil.MenuLabel('UI/Fleet/WarpFleetToLocationWithinDistance', {'warpToDistance': util.FmtDist(float(defaultWarpDist))})
                                menuEntries += [[label, self.WarpToBookmark, (bookmark, float(defaultWarpDist), True)]]
                                menuEntries += [[uiutil.MenuLabel('UI/Fleet/FleetSubmenus/WarpFleetToWithin'), self.WarpToMenu(self.WarpFleetToBookmark, bookmark)]]
                            if self.CheckImWingCmdr():
                                label = uiutil.MenuLabel('UI/Fleet/WarpWingToLocationWithinDistance', {'warpToDistance': util.FmtDist(float(defaultWarpDist))})
                                menuEntries += [[label, self.WarpToBookmark, (bookmark, float(defaultWarpDist), True)]]
                                menuEntries += [[uiutil.MenuLabel('UI/Fleet/FleetSubmenus/WarpWingToWithin'), self.WarpToMenu(self.WarpFleetToBookmark, bookmark)]]
                            if self.CheckImSquadCmdr():
                                label = uiutil.MenuLabel('UI/Fleet/WarpSquadToLocationWithinDistance', {'warpToDistance': util.FmtDist(float(defaultWarpDist))})
                                menuEntries += [[label, self.WarpToBookmark, (bookmark, float(defaultWarpDist), True)]]
                                menuEntries += [[uiutil.MenuLabel('UI/Fleet/FleetSubmenus/WarpSquadToWithin'), self.WarpToMenu(self.WarpFleetToBookmark, bookmark)]]
                    if checkBookmarkDeadspace:
                        menuEntries += [[uiutil.MenuLabel('UI/Inflight/WarpToBookmark'), self.WarpToBookmark, (bookmark, float(defaultWarpDist))]]
                        if checkFleet:
                            if self.CheckImFleetLeader():
                                menuEntries += [[uiutil.MenuLabel('UI/Fleet/WarpFleetToLocation'), self.WarpToBookmark, (bookmark, float(defaultWarpDist), True)]]
                                menuEntries += [[uiutil.MenuLabel('UI/Fleet/FleetSubmenus/WarpFleetToWithin'), self.WarpToMenu(self.WarpFleetToBookmark, bookmark)]]
                            if self.CheckImWingCmdr():
                                menuEntries += [[uiutil.MenuLabel('UI/Fleet/WarpWingToLocation'), self.WarpToBookmark, (bookmark, float(defaultWarpDist), True)]]
                                menuEntries += [[uiutil.MenuLabel('UI/Fleet/FleetSubmenus/WarpWingToWithin'), self.WarpToMenu(self.WarpFleetToBookmark, bookmark)]]
                            if self.CheckImSquadCmdr():
                                menuEntries += [[uiutil.MenuLabel('UI/Fleet/WarpSquadToLocation'), self.WarpToBookmark, (bookmark, float(defaultWarpDist), True)]]
                                menuEntries += [[uiutil.MenuLabel('UI/Fleet/FleetSubmenus/WarpSquadToWithin'), self.WarpToMenu(self.WarpFleetToBookmark, bookmark)]]
            if checkInSystem and not checkMyShip and checkAlignTo and not checkWarpActive and not checkIfAgentBookmark:
                menuEntries += [[uiutil.MenuLabel('UI/Inflight/AlignTo'), self.AlignToBookmark, (getattr(bookmark, 'bookmarkID', None),)]]
            if not checkIfAgentBookmark and not checkIfReadonlyBookmark:
                menuEntries += [[uiutil.MenuLabel('UI/Inflight/RemoveBookmark'), sm.GetService('addressbook').DeleteBookmarks, ([getattr(bookmark, 'bookmarkID', None)],)]]
            if ignoreTypeCheck or checkStation is True:
                menuEntries += [None]
                if checkBP and checkInSystem and checkStation and not checkWarpActive:
                    menuEntries += [[uiutil.MenuLabel('UI/Inflight/DockInStation'), self.Dock, (itemID,)]]
                else:
                    prereqs = [('checkBP', checkBP, True),
                     ('notInSystem', checkInSystem, True),
                     ('notStation', checkStation, True),
                     ('inWarp', checkWarpActive, False)]
                    reason = self.FindReasonNotAvailable(prereqs)
                    if reason:
                        menuEntries.reasonsWhyNotAvailable['UI/Inflight/DockInStation'] = reason
        elif bp and itemID is not None:
            checkBillboard = groupID == const.groupBillboard
            checkStructure = categoryID in (const.categoryStructure, const.categorySovereigntyStructure)
            checkSovStructure = categoryID == const.categorySovereigntyStructure
            checkControlTower = groupID == const.groupControlTower
            checkContainer = groupID in (const.groupWreck,
             const.groupCargoContainer,
             const.groupSpawnContainer,
             const.groupSecureCargoContainer,
             const.groupAuditLogSecureContainer,
             const.groupFreightContainer,
             const.groupDeadspaceOverseersBelongings,
             const.groupMissionContainer)
            checkMyWreck = groupID == const.groupWreck and bp.HaveLootRight(itemID)
            checkMyCargo = groupID == const.groupCargoContainer and bp.HaveLootRight(itemID)
            checkNotAbandoned = not bp.IsAbandoned(itemID)
            checkCorpHangarArray = groupID == const.groupCorporateHangarArray
            checkAssemblyArray = groupID == const.groupAssemblyArray
            checkMobileLaboratory = groupID == const.groupMobileLaboratory
            checkRefinery = groupID == const.groupRefiningArray
            checkSilo = groupID == const.groupSilo
            checkConstructionPf = groupID in (const.groupConstructionPlatform, const.groupStationUpgradePlatform, const.groupStationImprovementPlatform)
            checkJumpPortalArray = groupID == const.groupJumpPortalArray
            checkPMA = groupID in (const.groupPlanet, const.groupMoon, const.groupAsteroidBelt)
            checkMultiGroups1 = groupID in (const.groupSecureCargoContainer, const.groupAuditLogSecureContainer)
            checkMultiGroups2 = categoryID == const.categoryDrone or groupID == const.groupBiomass
            checkAnchorDrop = godmaSM.TypeHasEffect(typeID, const.effectAnchorDrop)
            checkAnchorLift = godmaSM.TypeHasEffect(typeID, const.effectAnchorLift)
            checkAutoPilot = bool(sm.StartService('autoPilot').GetState())
            checkCanRename = checkIsMine or bool(checkIsMyCorps and session.corprole & const.corpRoleEquipmentConfig and categoryID != const.categorySovereigntyStructure) or session.role & service.ROLE_WORLDMOD
            checkAnchorable = invGroup.anchorable
            checkRenameable = not (groupID == const.groupStation and godmaSM.GetType(typeID).isPlayerOwnable == 1)
            checkInTargets = itemID in sm.StartService('target').GetTargets()
            checkBeingTargeted = sm.StartService('target').BeingTargeted(itemID)
            checkOrbital = categoryID == const.categoryOrbital
            camera = sm.GetService('sceneManager').GetRegisteredCamera('default')

            def CheckScoopable(shipItem, groupID, categoryID, typeID):
                if groupID == const.groupBiomass or categoryID == const.categoryDrone:
                    return True
                if shipItem is None:
                    return False
                isAnchorable = checkAnchorable and checkIsFree
                if shipItem.groupID in (const.groupFreighter, const.groupJumpFreighter):
                    if groupID == const.groupFreightContainer:
                        return True
                    if isAnchorable and groupID not in (const.groupCargoContainer, const.groupAuditLogSecureContainer, const.groupSecureCargoContainer):
                        return True
                    return False
                if isAnchorable or groupID in (const.groupCargoContainer, const.groupFreightContainer) and typeID not in (const.typeCargoContainer, const.typePlanetaryLaunchContainer):
                    return True
                return False

            checkScoopable = CheckScoopable(shipItem, groupID, categoryID, typeID)
            checkScoopableSMA = categoryID == const.categoryShip and groupID != const.groupCapsule and not isMyShip and shipItem is not None and shipItem.hasShipMaintenanceBay
            checkKeepRangeGroups = categoryID != const.categoryAsteroid and groupID not in (const.groupHarvestableCloud,
             const.groupMiningDrone,
             const.groupCargoContainer,
             const.groupSecureCargoContainer,
             const.groupAuditLogSecureContainer,
             const.groupStation,
             const.groupStargate,
             const.groupFreightContainer,
             const.groupWreck)
            checkLookingAtItem = bool(sm.GetService('camera').LookingAt() == itemID)
            checkInterest = bool(util.GetAttrs(camera, 'interest', 'translationCurve', 'id') == itemID)
            advancedCamera = bool(settings.user.ui.Get('advancedCamera', 0))
            checkHasConsumables = checkStructure and godmaSM.GetType(typeID).consumptionType != 0
            checkAuditLogSecureContainer = groupID == const.groupAuditLogSecureContainer
            checkShipJumpDrive = slimItem and shipItem is not None and shipItem.canJump
            checkShipJumpPortalGenerator = slimItem and shipItem is not None and shipItem.groupID in [const.groupTitan, const.groupBlackOps] and len([ each for each in godmaSM.GetItem(session.shipid).modules if each.groupID == const.groupJumpPortalGenerator ]) > 0
            structureShipBridge = sm.services['pwn'].GetActiveBridgeForShip(itemID)
            checkShipHasBridge = structureShipBridge is not None
            if structureShipBridge is not None:
                structureShipBridgeLabel = uiutil.MenuLabel('UI/Fleet/JumpThroughToSystem', {'solarsystem': structureShipBridge[0]})
            else:
                structureShipBridgeLabel = uiutil.MenuLabel('UI/Inflight/JumpThroughError')
            keepRangeranges = [500,
             1000,
             2500,
             5000,
             7500,
             10000,
             15000,
             20000,
             25000,
             30000]
            defMenuKeepRangeOptions = [ (util.FmtDist(rnge), self.SetDefaultKeepAtRangeDist, (rnge,)) for rnge in keepRangeranges ]
            keepRangeMenu = [ (util.FmtDist(rnge), self.KeepAtRange, (itemID, rnge)) for rnge in keepRangeranges ]
            keepRangeMenu += [(uiutil.MenuLabel('UI/Inflight/KeepAtCurrentRange', {'currentDistance': niceRange}), self.KeepAtRange, (itemID, dist)), None, (uiutil.MenuLabel('UI/Inflight/Submenus/SetDefaultWarpRange'), defMenuKeepRangeOptions)]
            orbitranges = [500,
             1000,
             2500,
             5000,
             7500,
             10000,
             15000,
             20000,
             25000,
             30000]
            defMenuOrbitOptions = [ (util.FmtDist(rnge), self.SetDefaultOrbitDist, (rnge,)) for rnge in orbitranges ]
            orbitMenu = [ (util.FmtDist(rnge), self.Orbit, (itemID, rnge)) for rnge in orbitranges ]
            orbitMenu += [(uiutil.MenuLabel('UI/Inflight/OrbitAtCurrentRange', {'currentDistance': niceRange}), self.Orbit, (itemID, dist)), None, (uiutil.MenuLabel('UI/Inflight/Submenus/SetDefaultWarpRange'), defMenuOrbitOptions)]
            if checkEnemySpotted:
                senderID, = checkEnemySpotted
                label = uiutil.MenuLabel('UI/Fleet/FleetSubmenus/BroadCastEnemySpotted', {'character': senderID})
                menuEntries += [[label, ('isDynamic', self.CharacterMenu, (senderID,))]]
            if ignoreTypeCheck or checkShip is True:
                checkCanStoreVessel = shipItem is not None and slimItem is not None and shipItem.groupID != const.groupCapsule and slimItem.itemID != shipItem.itemID
                checkInSameCorp = bool(slimItem) and slimItem.ownerID in sm.StartService('corp').GetMemberIDs()
                checkInSameFleet = bool(slimItem) and session.fleetid and slimItem.ownerID in sm.GetService('fleet').GetMembers()

                @util.Memoized
                def GetShipConfig(shipID):
                    return sm.GetService('shipConfig').GetShipConfig(shipID)

                def CanUseShipServices(serviceFlag, ignoreShipConfig):
                    if checkMyShip or checkIsMine:
                        return True
                    if ignoreShipConfig:
                        return False
                    if not (checkInSameCorp or checkInSameFleet):
                        return False
                    config = GetShipConfig(slimItem.itemID)
                    if serviceFlag == const.flagFleetHangar:
                        if config['FleetHangar_AllowCorpAccess'] and checkInSameCorp or config['FleetHangar_AllowFleetAccess'] and checkInSameFleet:
                            return True
                    if serviceFlag == const.flagShipHangar:
                        if config['SMB_AllowCorpAccess'] and checkInSameCorp or config['SMB_AllowFleetAccess'] and checkInSameFleet:
                            return True
                    return False

                if groupID == const.groupCapsule:
                    stopLabelPath = 'UI/Inflight/StopMyCapsule'
                else:
                    stopLabelPath = 'UI/Inflight/StopMyShip'
                stopText = uiutil.MenuLabel(stopLabelPath)
                if checkShip and checkMyShip:
                    menuEntries += [[stopText, self.StopMyShip]]
                else:
                    prereqs = [('checkShip', checkShip, True), ('isNotMyShip', checkMyShip, True)]
                    reason = self.FindReasonNotAvailable(prereqs)
                    if reason:
                        menuEntries.reasonsWhyNotAvailable[stopLabelPath] = reason
                        menuEntries.reasonsWhyNotAvailable['UI/Commands/OpenMyCargo'] = reason
                if checkShip and checkIfShipMAShip and CanUseShipServices(const.flagShipHangar, ignoreShipConfig):
                    menuEntries += [[uiutil.MenuLabel('UI/Commands/OpenShipMaintenanceBay'), self.OpenShipMaintenanceBayShip, (itemID, localization.GetByLabel('UI/Commands/OpenShipMaintenanceBayError'))]]
                if checkShip and checkIfShipFHShip and CanUseShipServices(const.flagFleetHangar, ignoreShipConfig):
                    menuEntries += [[uiutil.MenuLabel('UI/Commands/OpenFleetHangar'), self.OpenFleetHangar, (itemID,)]]
                if checkShip and checkMyShip and not checkInCapsule:
                    menuEntries += [[uiutil.MenuLabel('UI/Commands/OpenCargoHold'), self.OpenShipHangarCargo, [itemID]]]
                    if checkIfShipDroneBay:
                        menuEntries += [[uiutil.MenuLabel('UI/Commands/OpenDroneBay'), self.OpenDroneBay, [itemID]]]
                    if checkIfShipFuelBay:
                        menuEntries += [[uiutil.MenuLabel('UI/Commands/OpenFuelBay'), self.OpenFuelBay, [itemID]]]
                    if checkIfShipOreHold:
                        menuEntries += [[uiutil.MenuLabel('UI/Commands/OpenOreHold'), self.OpenOreHold, [itemID]]]
                    if checkIfShipGasHold:
                        menuEntries += [[uiutil.MenuLabel('UI/Commands/OpenGasHold'), self.OpenGasHold, [itemID]]]
                    if checkIfShipMineralHold:
                        menuEntries += [[uiutil.MenuLabel('UI/Commands/OpenMineralHold'), self.OpenMineralHold, [itemID]]]
                    if checkIfShipSalvageHold:
                        menuEntries += [[uiutil.MenuLabel('UI/Commands/OpenSalvageHold'), self.OpenSalvageHold, [itemID]]]
                    if checkIfShipShipHold:
                        menuEntries += [[uiutil.MenuLabel('UI/Commands/OpenShipHold'), self.OpenShipHold, [itemID]]]
                    if checkIfShipSmallShipHold:
                        menuEntries += [[uiutil.MenuLabel('UI/Commands/OpenSmallShipHold'), self.OpenSmallShipHold, [itemID]]]
                    if checkIfShipMediumShipHold:
                        menuEntries += [[uiutil.MenuLabel('UI/Commands/OpenMediumShipHold'), self.OpenMediumShipHold, [itemID]]]
                    if checkIfShipLargeShipHold:
                        menuEntries += [[uiutil.MenuLabel('UI/Commands/OpenLargeShipHold'), self.OpenLargeShipHold, [itemID]]]
                    if checkIfShipIndustrialShipHold:
                        menuEntries += [[uiutil.MenuLabel('UI/Commands/OpenIndustrialShipHold'), self.OpenIndustrialShipHold, [itemID]]]
                    if checkIfShipAmmoHold:
                        menuEntries += [[uiutil.MenuLabel('UI/Commands/OpenAmmoHold'), self.OpenAmmoHold, [itemID]]]
                    if checkIfShipCommandCenterHold:
                        menuEntries += [[uiutil.MenuLabel('UI/Commands/OpenCommandCenterHold'), self.OpenCommandCenterHold, [itemID]]]
                    if checkIfShipPlanetaryCommoditiesHold:
                        menuEntries += [[uiutil.MenuLabel('UI/PI/Common/OpenPlanetaryCommoditiesHold'), self.OpenPlanetaryCommoditiesHold, [itemID]]]
                    if checkIfShipHasQuafeBay:
                        menuEntries += [[uiutil.MenuLabel('UI/Commands/OpenQuafeBay'), self.OpenQuafeHold, [itemID]]]
                if checkConfigDist and checkIfShipMAShip and checkCanStoreVessel and CanUseShipServices(const.flagShipHangar, ignoreShipConfig):
                    menuEntries += [[uiutil.MenuLabel('UI/Inflight/POS/StoreVesselInSMA'), self.StoreVessel, (itemID, session.shipid)]]
                if checkShip and checkMyShip and checkIfShipCloneShip:
                    menuEntries += [[uiutil.MenuLabel('UI/Commands/ConfigureShipCloneFacility'), self.ShipCloneConfig, (itemID,)]]
                if checkShip and checkMyShip and not checkInCapsule and not checkWarpActive:
                    menuEntries += [[uiutil.MenuLabel('UI/Inflight/EjectFromShip'), self.Eject]]
                else:
                    prereqs = [('checkShip', checkShip, True),
                     ('isNotMyShip', checkMyShip, True),
                     ('inCapsule', checkInCapsule, False),
                     ('inWarp', checkWarpActive, False)]
                    reason = self.FindReasonNotAvailable(prereqs)
                    if reason:
                        menuEntries.reasonsWhyNotAvailable['UI/Inflight/EjectFromShip'] = reason
                if checkMyShip and not checkWarpActive:
                    menuEntries += [[uiutil.MenuLabel('UI/Commands/ReconnectToLostDrones'), self.ReconnectToDrones]]
                if checkMyShip and not checkWarpActive:
                    menuEntries += [[uiutil.MenuLabel('UI/Inflight/SafeLogoff'), self.SafeLogoff]]
                if checkMyShip and not checkWarpActive:
                    menuEntries += [[uiutil.MenuLabel('UI/Inflight/SelfDestructShipOrPod'), self.SelfDestructShip, (itemID,)]]
                else:
                    prereqs = [('isNotMyShip', checkMyShip, True), ('inWarp', checkWarpActive, False)]
                    reason = self.FindReasonNotAvailable(prereqs)
                    if reason:
                        menuEntries.reasonsWhyNotAvailable['UI/Inflight/SelfDestructShipOrPod'] = reason
                if checkShip and not checkMyShip and not checkWarpActive and not checkShipBusy and not checkDistNone:
                    menuEntries += [[uiutil.MenuLabel('UI/Inflight/BoardShip'), self.Board, (itemID,)]]
                else:
                    prereqs = [('checkShip', checkShip, True),
                     ('isMyShip', checkMyShip, False),
                     ('inWarp', checkWarpActive, False),
                     ('pilotInShip', checkShipBusy, False)]
                    reason = self.FindReasonNotAvailable(prereqs)
                    if reason:
                        menuEntries.reasonsWhyNotAvailable['UI/Inflight/BoardShip'] = reason
                if checkShip and checkMyShip:
                    menuEntries += [[uiutil.MenuLabel('UI/Inflight/POS/EnterStarbasePassword'), self.EnterPOSPassword]]
                if checkShip and checkMyShip and checkAutoPilot:
                    menuEntries += [[uiutil.MenuLabel('UI/Inflight/DeactivateAutopilot'), self.ToggleAutopilot, (0,)]]
                else:
                    prereqs = [('checkShip', checkShip, True), ('isNotMyShip', checkMyShip, True), ('autopilotNotActive', checkAutoPilot, True)]
                    reason = self.FindReasonNotAvailable(prereqs)
                    if reason:
                        menuEntries.reasonsWhyNotAvailable['UI/Inflight/DeactivateAutopilot'] = reason
                if checkShip and checkMyShip and not checkAutoPilot:
                    menuEntries += [[uiutil.MenuLabel('UI/Inflight/ActivateAutopilot'), self.ToggleAutopilot, (1,)]]
                else:
                    prereqs = [('checkShip', checkShip, True), ('isNotMyShip', checkMyShip, True), ('autopilotActive', checkAutoPilot, False)]
                    reason = self.FindReasonNotAvailable(prereqs)
                    if reason:
                        menuEntries.reasonsWhyNotAvailable['UI/Inflight/ActivateAutopilot'] = reason
                menuEntries += [None]
                if checkMyShip and not checkInCapsule and checkShipJumpDrive:
                    menuEntries += [[uiutil.MenuLabel('UI/Inflight/Submenus/JumpTo'), ('isDynamic', self.GetHybridBeaconJumpMenu, [])]]
                    if checkShipJumpPortalGenerator:
                        menuEntries += [[uiutil.MenuLabel('UI/Inflight/Submenus/BridgeTo'), ('isDynamic', self.GetHybridBridgeMenu, [])]]
                if not checkMyShip and checkShipHasBridge:
                    menuEntries += [[structureShipBridgeLabel, self.JumpThroughAlliance, (itemID,)]]
                menuEntries += [None]
                if checkShip and checkIfShipMAShip and (checkInSameCorp or checkInSameFleet):
                    menuEntries += [[uiutil.MenuLabel('UI/Fitting/UseFittingService'), uicore.cmd.OpenFitting, ()]]
            if ignoreTypeCheck or checkPMA is False:
                checkDrone = groupID == const.groupMiningDrone
                menuEntries += [None]
                if checkInSystem and not checkMyShip and not checkPMA:
                    if checkApproachDist:
                        menuEntries += [[uiutil.MenuLabel('UI/Inflight/ApproachObject'), self.Approach, (itemID, 50)]]
                    else:
                        reason = self.FindReasonNotAvailable([('notInApproachRange', checkApproachDist, True)])
                        if reason:
                            menuEntries.reasonsWhyNotAvailable['UI/Inflight/ApproachObject'] = reason
                    if not checkWarpDist:
                        menuEntries += [[uiutil.MenuLabel('UI/Inflight/OrbitObject'), orbitMenu]]
                    else:
                        reason = self.FindReasonNotAvailable([('inWarpRange', checkWarpDist, False)])
                        if reason:
                            menuEntries.reasonsWhyNotAvailable['UI/Inflight/OrbitObject'] = reason
                    if not checkDrone and checkKeepRangeGroups and not checkWarpDist:
                        menuEntries += [[uiutil.MenuLabel('UI/Inflight/Submenus/KeepAtRange'), keepRangeMenu]]
                    else:
                        prereqs = [('cantKeepInRange',
                          checkKeepRangeGroups,
                          True,
                          {'groupName': groupName}), ('inWarpRange', checkWarpDist, False)]
                        reason = self.FindReasonNotAvailable(prereqs)
                        if reason:
                            menuEntries.reasonsWhyNotAvailable['UI/Inflight/Submenus/KeepAtRange'] = reason
                else:
                    prereqs = [('notInSystem', checkInSystem, True), ('isMyShip', checkMyShip, False), ('badGroup',
                      checkPMA,
                      False,
                      {'groupName': groupName})]
                    reason = self.FindReasonNotAvailable(prereqs)
                    if reason:
                        menuEntries.reasonsWhyNotAvailable['UI/Inflight/ApproachObject'] = reason
                        menuEntries.reasonsWhyNotAvailable['UI/Inflight/OrbitObject'] = reason
                        menuEntries.reasonsWhyNotAvailable['UI/Inflight/Submenus/KeepAtRange'] = reason
            warpRange = None
            if checkShip and slimItem and slimItem.charID:
                warpFn = self.WarpToMember
                warpFleetFn = self.WarpFleetToMember
                warpID = slimItem.charID
                warpRange = float(defaultWarpDist)
            else:
                warpFn = self.WarpToItem
                warpFleetFn = self.WarpFleet
                warpID = itemID
            if checkInSystem and not checkWarpActive and not checkMyShip and checkWarpDist:
                menuEntries += [[self.DefaultWarpToLabel(), warpFn, (warpID, warpRange)]]
            else:
                prereqs = [('notInSystem', checkInSystem, True),
                 ('inWarp', checkWarpActive, False),
                 ('isMyShip', checkMyShip, False),
                 ('notInWarpRange', checkWarpDist, True)]
                reason = self.FindReasonNotAvailable(prereqs)
                if reason:
                    menuEntries.reasonsWhyNotAvailable[self.DefaultWarpToLabel()[0]] = reason
            if checkInSystem and not checkMyShip:
                if checkWarpDist and not checkWarpActive:
                    menuEntries += [[uiutil.MenuLabel('UI/Inflight/Submenus/WarpToWithin'), self.WarpToMenu(warpFn, warpID)]]
                    if checkFleet:
                        if self.CheckImFleetLeader():
                            menuEntries += [[uiutil.MenuLabel('UI/Fleet/WarpFleet'), warpFleetFn, (warpID, float(defaultWarpDist))]]
                        if self.CheckImFleetLeader():
                            menuEntries += [[uiutil.MenuLabel('UI/Fleet/FleetSubmenus/WarpFleetToWithin'), self.WarpToMenu(warpFleetFn, warpID)]]
                        if self.CheckImWingCmdr():
                            menuEntries += [[uiutil.MenuLabel('UI/Fleet/WarpWing'), warpFleetFn, (warpID, float(defaultWarpDist))]]
                        if self.CheckImWingCmdr():
                            menuEntries += [[uiutil.MenuLabel('UI/Fleet/FleetSubmenus/WarpWingToWithin'), self.WarpToMenu(warpFleetFn, warpID)]]
                        if self.CheckImSquadCmdr():
                            menuEntries += [[uiutil.MenuLabel('UI/Fleet/WarpSquad'), warpFleetFn, (warpID, float(defaultWarpDist))]]
                        if self.CheckImSquadCmdr():
                            menuEntries += [[uiutil.MenuLabel('UI/Fleet/FleetSubmenus/WarpSquadToWithin'), self.WarpToMenu(warpFleetFn, warpID)]]
                if checkAlignTo and not checkWarpActive:
                    menuEntries += [[uiutil.MenuLabel('UI/Inflight/AlignTo'), self.AlignTo, (itemID,)]]
                if checkFleet and checkApproachDist:
                    menuEntries += [[uiutil.MenuLabel('UI/Fleet/FleetBroadcast/Commands/BroadcastTarget'), sm.GetService('fleet').SendBroadcast_Target, (itemID,)]]
            if checkInSystem and checkFleet:
                if not checkMultiCategs1:
                    menuEntries += [[uiutil.MenuLabel('UI/Fleet/FleetBroadcast/Commands/BroadcastWarpTo'), sm.GetService('fleet').SendBroadcast_WarpTo, (itemID, typeID)]]
                    menuEntries += [[uiutil.MenuLabel('UI/Fleet/FleetBroadcast/Commands/BroadcastAlignTo'), sm.GetService('fleet').SendBroadcast_AlignTo, (itemID, typeID)]]
                if checkStargate:
                    menuEntries += [[uiutil.MenuLabel('UI/Fleet/FleetBroadcast/Commands/BroadcastJumpTo'), sm.GetService('fleet').SendBroadcast_JumpTo, (itemID, typeID)]]
            if ignoreTypeCheck or checkJumpThrough:
                throughSystemID = sm.GetService('fleet').CanJumpThrough(slimItem)
                menuEntries += [None]
                if checkInSystem and checkJumpDist and not checkWarpActive:
                    menuEntries += [[uiutil.MenuLabel('UI/Fleet/JumpThroughToSystem', {'solarsystem': throughSystemID}), self.JumpThroughFleet, (otherCharID, itemID)]]
            if ignoreTypeCheck or checkStation is True:
                menuEntries += [None]
                if checkInSystem and checkStation and not checkWarpActive:
                    menuEntries += [[uiutil.MenuLabel('UI/Inflight/DockInStation'), self.Dock, (itemID,)]]
                else:
                    prereqs = [('notInSystem', checkInSystem, True), ('notStation', checkStation, True), ('inWarp', checkWarpActive, False)]
                    reason = self.FindReasonNotAvailable(prereqs)
                    if reason:
                        menuEntries.reasonsWhyNotAvailable['UI/Inflight/DockInStation'] = reason
            if ignoreTypeCheck or checkStargate:
                dests = []
                locs = []
                for each in slimItem.jumps:
                    if each.locationID not in locs:
                        locs.append(each.locationID)
                    if each.toCelestialID not in locs:
                        locs.append(each.toCelestialID)

                if len(locs):
                    cfg.evelocations.Prime(locs)
                for each in slimItem.jumps:
                    name = uiutil.MenuLabel('UI/Menusvc/MenuHints/DestinationNameInSystem', {'destination': each.toCelestialID,
                     'solarsystem': each.locationID})
                    dests.append((name, self.StargateJump, (itemID, each.toCelestialID, each.locationID)))

                if not dests:
                    dests = [('None', None, None)]
                checkSingleJumpDest = len(dests) == 1
                if dests:
                    currentWarpTarget = sm.GetService('space').warpDestinationCache[0]
                    checkInWarpToGate = itemID == currentWarpTarget
                    if checkStargate and checkSingleJumpDest and checkCanUseGate and (not checkWarpActive or checkInWarpToGate):
                        menuEntries += [[uiutil.MenuLabel('UI/Inflight/Jump'), dests[0][1], dests[0][2]]]
                    else:
                        prereqs = [('inWarp', checkWarpActive, False),
                         ('notStargate', checkStargate, True),
                         ('cantUseGate', checkCanUseGate, True),
                         ('notWithinMaxJumpDist', checkJumpDist, True),
                         ('severalJumpDest', checkSingleJumpDest, True)]
                        reason = self.FindReasonNotAvailable(prereqs)
                        if reason:
                            menuEntries.reasonsWhyNotAvailable['UI/Inflight/Jump'] = reason
                    if checkStargate and checkJumpDist and not checkSingleJumpDest and checkCanUseGate:
                        menuEntries += [[uiutil.MenuLabel('UI/Inflight/Submenus/JumpTo'), dests]]
                    if dests[0][2]:
                        waypoints = sm.StartService('starmap').GetWaypoints()
                        checkInWaypoints = dests[0][2][2] in waypoints
                        if checkSingleJumpDest and checkStargate and checkCanUseGate and not checkInWaypoints:
                            menuEntries += [[uiutil.MenuLabel('UI/Inflight/AddFirstWaypoint'), sm.StartService('starmap').SetWaypoint, (dests[0][2][2], 0, 1)]]
            if slimItem and (ignoreTypeCheck or checkWarpgate is True):
                checkOneTwo = 1
                if checkWarpgate and checkOneTwo and not checkWarpActive:
                    menuEntries += [[uiutil.MenuLabel('UI/Inflight/ActivateGate'), self.ActivateAccelerationGate, (itemID,)]]
                else:
                    prereqs = [('notWarpGate', checkWarpgate, True),
                     ('severalJumpDest', checkOneTwo, True),
                     ('notWithinMaxJumpDist', checkJumpDist, True),
                     ('inWarp', checkWarpActive, False)]
                    reason = self.FindReasonNotAvailable(prereqs)
                    if reason:
                        menuEntries.reasonsWhyNotAvailable['UI/Inflight/ActivateGate'] = reason
            if slimItem and (ignoreTypeCheck or checkWormhole is True):
                if checkWormhole and not checkWarpActive:
                    menuEntries += [[uiutil.MenuLabel('UI/Inflight/EnterWormhole'), self.EnterWormhole, (itemID,)]]
                else:
                    prereqs = [('notCloseEnoughToWH', checkWormholeDist, True), ('inWarp', checkWarpActive, False)]
                    reason = self.FindReasonNotAvailable(prereqs)
                    if reason:
                        menuEntries.reasonsWhyNotAvailable['UI/Inflight/EnterWormhole'] = reason
            menuEntries += [None]
            if not checkWarpActive and checkLookatDist:
                if not checkLookingAtItem and not checkPlanet and not checkMoon:
                    menuEntries += [[uiutil.MenuLabel('UI/Inflight/LookAtObject'), sm.GetService('camera').LookAt, (itemID,)]]
                else:
                    prereqs = [('isLookingAtItem', checkLookingAtItem, False)]
                    reason = self.FindReasonNotAvailable(prereqs)
                    if reason:
                        menuEntries.reasonsWhyNotAvailable['UI/Inflight/LookAtObject'] = reason
                if not checkLookingAtItem and advancedCamera:
                    menuEntries += [[uiutil.MenuLabel('UI/Inflight/SetAsCameraParent'), self.SetParent, (itemID,)]]
                if not checkInterest and advancedCamera:
                    menuEntries += [[uiutil.MenuLabel('UI/Inflight/SetAsCameraInterest'), self.SetInterest, (itemID,)]]
            else:
                prereqs = [('inWarp', checkWarpActive, False), ('notInLookingRange', checkLookatDist, True)]
                reason = self.FindReasonNotAvailable(prereqs)
                if reason:
                    menuEntries.reasonsWhyNotAvailable['UI/Inflight/LookAtObject'] = reason
            if checkLookingAtItem:
                menuEntries += [[uiutil.MenuLabel('UI/Inflight/ResetCamera'), sm.GetService('camera').ResetCamera]]
            else:
                reason = self.FindReasonNotAvailable([('notLookingAtItem', checkLookingAtItem, True)])
                if reason:
                    menuEntries.reasonsWhyNotAvailable['UI/Inflight/ResetCamera'] = reason
            if ignoreTypeCheck or checkBillboard is True:
                newsURL = 'http://www.eveonline.com/mb2/news.asp'
                if boot.region == 'optic':
                    newsURL = 'http://eve.tiancity.com/client/news.html'
                menuEntries += [None]
                if checkBillboard:
                    menuEntries += [[uiutil.MenuLabel('UI/Commands/ReadNews'), uicore.cmd.OpenBrowser, (newsURL, 'browser')]]
            if ignoreTypeCheck or checkContainer is True:
                menuEntries += [None]
                if checkContainer and otherBall:
                    menuEntries += [[uiutil.MenuLabel('UI/Commands/OpenCargo'), self.OpenCargo, [itemID]]]
                else:
                    prereqs = [('notWithinMaxTransferRange', checkTransferDist, True)]
                    reason = self.FindReasonNotAvailable(prereqs)
                    if reason:
                        menuEntries.reasonsWhyNotAvailable['UI/Commands/OpenCargo'] = reason
            if ignoreTypeCheck or checkPlanetCustomsOffice is True:
                menuEntries += [None]
                menuEntries += [[uiutil.MenuLabel('UI/PI/Common/AccessCustomOffice'), self.OpenPlanetCustomsOfficeImportWindow, [itemID]]]
            if checkIfMaterialsHold and checkTransferDist and checkIsMineOrCorps and checkIfCanUpgrade and checkInSystem and (groupID == const.groupOrbitalConstructionPlatforms or checkZeroSecSpace):
                menuEntries += [[uiutil.MenuLabel('UI/DustLink/OpenUpgradeHold'), self.OpenUpgradeWindow, [itemID]]]
            if ignoreTypeCheck or checkMyWreck is True or checkMyCargo is True:
                if checkNotAbandoned:
                    if checkMyWreck:
                        menuEntries += [[uiutil.MenuLabel('UI/Inflight/AbandonWreack'), self.AbandonLoot, [itemID]]]
                        menuEntries += [[uiutil.MenuLabel('UI/Inflight/AbandonAllWrecks'), self.AbandonAllLoot, [itemID]]]
                    if checkMyCargo:
                        menuEntries += [[uiutil.MenuLabel('UI/Inflight/AbandonCargo'), self.AbandonLoot, [itemID]]]
                        menuEntries += [[uiutil.MenuLabel('UI/Inflight/AbandonAllCargo'), self.AbandonAllLoot, [itemID]]]
            if checkScoopable and slimItem is not None:
                menuEntries += [[uiutil.MenuLabel('UI/Inflight/ScoopToCargoHold'), self.Scoop, (itemID, typeID)]]
            if checkScoopableSMA:
                menuEntries += [[uiutil.MenuLabel('UI/Inflight/POS/ScoopToShipMaintenanceBay'), self.ScoopSMA, (itemID,)]]
            if checkConstructionPf is True:
                menuEntries += [None]
                if checkTransferDist:
                    menuEntries += [[uiutil.MenuLabel('UI/Inflight/POS/AccessPOSResources'), self.OpenConstructionPlatform, (itemID, localization.GetByLabel('UI/Inflight/POS/AccessPOSResourcesOpenConstructionPlatformError'))]]
                    menuEntries += [[uiutil.MenuLabel('UI/Inflight/POS/BuildConstructionPlatform'), self.BuildConstructionPlatform, (itemID,)]]
            if checkAnchorable and checkConfigDist and checkIsMineOrCorps and checkAnchorDrop and checkIsFree:
                menuEntries += [[uiutil.MenuLabel('UI/Inflight/POS/AnchorObject'), self.AnchorObject, (itemID, 1)]]
            if checkAnchorable and checkConfigDist and checkIsMineOrCorps and checkAnchorLift and not checkIsFree:
                menuEntries += [[uiutil.MenuLabel('UI/Inflight/UnanchorObject'), self.AnchorObject, (itemID, 0)]]
            else:
                prereqs = [('notWithinMaxConfigRange', checkConfigDist, True), ('checkIsMineOrCorps', checkIsMineOrCorps, True)]
                reason = self.FindReasonNotAvailable(prereqs)
                if reason:
                    menuEntries.reasonsWhyNotAvailable['UI/Inflight/UnanchorObject'] = reason
            structureEntries = []
            if checkJumpPortalArray is True:
                structureBridge = sm.services['pwn'].GetActiveBridgeForStructure(itemID)
                checkStructureHasBridge = structureBridge is not None
                if structureBridge is not None:
                    bridgeJumpLabel = uiutil.MenuLabel('UI/Fleet/JumpThroughToSystem', {'solarsystem': structureBridge[1]})
                    bridgeUnlinkLabel = uiutil.MenuLabel('UI/Inflight/UnbridgeFromSolarsystem', {'solarsystem': structureBridge[1]})
                else:
                    bridgeJumpLabel = uiutil.MenuLabel('UI/Inflight/JumpThroughError')
                    bridgeUnlinkLabel = uiutil.MenuLabel('UI/Inflight/JumpThroughError')
                checkStructureFullyOnline = sm.services['pwn'].IsStructureFullyOnline(itemID)
                checkStructureFullyAnchored = sm.services['pwn'].IsStructureFullyAnchored(itemID)
                if not checkInCapsule and checkIsMyCorps and checkStructureFullyAnchored and not checkStructureHasBridge:
                    structureEntries += [[uiutil.MenuLabel('UI/Inflight/Submenus/BridgeTo'), self.JumpPortalBridgeMenu, (itemID,)]]
                if not checkInCapsule and checkIsMyCorps and checkStructureHasBridge and checkStructureFullyAnchored:
                    structureEntries += [[bridgeUnlinkLabel, self.UnbridgePortal, (itemID,)]]
                if not checkInCapsule and checkStructureHasBridge and checkStructureFullyOnline and checkJumpDist:
                    structureEntries += [[bridgeJumpLabel, self.JumpThroughPortal, (itemID,)]]
                if checkAnchorable and checkConfigDist and checkIsMineOrCorpsOrAlliances and not checkIsFree and checkTransferDist:
                    structureEntries += [[uiutil.MenuLabel('UI/Inflight/POS/AccessPOSResources'), self.OpenPOSJumpBridge, (itemID, localization.GetByLabel('UI/Inflight/POS/AccessPOSResourcesError'))]]
            if checkAnchorable and checkConfigDist and checkIsMineOrCorpsOrAlliances and not checkIsFree:
                if checkControlTower:
                    structureEntries += [[uiutil.MenuLabel('UI/Inflight/POS/AccessPOSFuelBay'), self.OpenPOSFuelBay, (itemID, localization.GetByLabel('UI/Inflight/POS/AccessPOSFuelBayError'))]]
                    structureEntries += [[uiutil.MenuLabel('UI/Inflight/POS/AccessPOSStrontiumBay'), self.OpenStrontiumBay, (itemID, localization.GetByLabel('UI/Inflight/POS/AccessPOSStrontiumBayError'))]]
                if checkSentry:
                    structureEntries += [[uiutil.MenuLabel('UI/Inflight/POS/AccessPOSAmmo'), self.OpenPOSStructureCharges, (itemID, localization.GetByLabel('UI/Inflight/POS/AccessPOSAmmoError'), True)]]
                if checkLaserSentry:
                    structureEntries += [[uiutil.MenuLabel('UI/Inflight/POS/AccessPOSActiveCrystal'), self.OpenPOSStructureCharges, (itemID, localization.GetByLabel('UI/Inflight/POS/AccessPOSActiveCrystalError'), False)]]
                    structureEntries += [[uiutil.MenuLabel('UI/Inflight/POS/AccessPOSCrystalStorage'), self.OpenPOSStructureChargesStorage, (itemID, localization.GetByLabel('UI/Inflight/POS/AccessPOSCrystalStorageError'))]]
                checkCanStoreVessel = shipItem is not None and shipItem.groupID != const.groupCapsule
                if checkCanStoreVessel and checkShipMaintainer:
                    structureEntries += [[uiutil.MenuLabel('UI/Inflight/POS/StoreVesselInSMA'), self.StoreVessel, (itemID, session.shipid)]]
                if checkShipMaintainer:
                    structureEntries += [[uiutil.MenuLabel('UI/Fitting/UseFittingService'), uicore.cmd.OpenFitting, ()]]
                if checkAssemblyArray:
                    structureEntries += [[uiutil.MenuLabel('UI/Inflight/POS/AccessPOSStorage'), self.OpenCorpHangarArray, (itemID, localization.GetByLabel('UI/Inflight/POS/AccessPOSStorageAssemblyArrayError'))]]
                if checkMobileLaboratory:
                    structureEntries += [[uiutil.MenuLabel('UI/Inflight/POS/AccessPOSStorage'), self.OpenCorpHangarArray, (itemID, localization.GetByLabel('UI/Inflight/POS/AccessPOSStorageIndustrialCorpHangarError'))]]
            if checkAnchorable and not checkIsFree:
                if checkIsMineOrCorps and checkControlTower:
                    structureEntries += [[uiutil.MenuLabel('UI/Inflight/POS/ManageControlTower'), self.ManageControlTower, (slimItem,)]]
                    if checkConfigDist:
                        structureEntries += [[uiutil.MenuLabel('UI/Inflight/POS/SetNewPasswordForForceField'), self.EnterForceFieldPassword, (itemID,)]]
                if checkTransferDist and checkIsMineOrCorpsOrAlliances and checkShipMaintainer:
                    structureEntries += [[uiutil.MenuLabel('UI/Inflight/POS/AccessPOSVessels'), self.OpenPOSShipMaintenanceArray, (itemID, localization.GetByLabel('UI/Inflight/POS/AccessPOSVesselsShipMaintenanceArrayError'))]]
                    structureEntries += [None]
                else:
                    prereqs = [('notWithinMaxTransferRange', checkTransferDist, True), ('notOwnedByYouOrCorpOrAlliance', checkIsMineOrCorpsOrAlliances, True)]
                    reason = self.FindReasonNotAvailable(prereqs)
                    if reason:
                        menuEntries.reasonsWhyNotAvailable['UI/Inflight/POS/AccessPOSVessels'] = reason
                if checkTransferDist and checkIsMineOrCorpsOrAlliances:
                    if checkCorpHangarArray:
                        structureEntries += [[uiutil.MenuLabel('UI/Inflight/POS/AccessPOSStorage'), self.OpenCorpHangarArray, (itemID, localization.GetByLabel('UI/Inflight/POS/AccessPOSStorageCorpHangarArrayError'))]]
                    if checkRenameable and (checkAssemblyArray or checkMobileLaboratory):
                        structureEntries += [[uiutil.MenuLabel('UI/Commands/SetName'), self.SetName, (slimItem,)]]
                    if checkSilo:
                        structureEntries += [[uiutil.MenuLabel('UI/Inflight/POS/AccessPOSStorage'), self.OpenPOSSilo, (itemID, localization.GetByLabel('UI/Inflight/POS/AccessPOSStorageSiloError'))]]
                    if checkReactor:
                        structureEntries += [[uiutil.MenuLabel('UI/Inflight/POS/AccessPOSStorage'), self.OpenPOSMobileReactor, (itemID, localization.GetByLabel('UI/Inflight/POS/AccessPOSStorageOpenStructureError'))]]
                else:
                    prereqs = [('notWithinMaxTransferRange', checkTransferDist, True), ('notOwnedByYouOrCorpOrAlliance', checkIsMineOrCorpsOrAlliances, True)]
                    reason = self.FindReasonNotAvailable(prereqs)
                    if reason:
                        menuEntries.reasonsWhyNotAvailable['UI/Inflight/POS/AccessPOSVessels'] = reason
                        menuEntries.reasonsWhyNotAvailable['UI/Inflight/POS/AccessPOSStorage'] = reason
            checkRefineryState = otherBall and not otherBall.isFree
            if checkRefinery and checkRefineryState and checkTransferDist:
                structureEntries += [[uiutil.MenuLabel('UI/Inflight/POS/AccessPOSRefinery'), self.OpenPOSRefinery, (itemID, localization.GetByLabel('UI/Inflight/POS/AccessPOSRefineryProcessingAreaError'))]]
            else:
                prereqs = [('notWithinMaxTransferRange', checkTransferDist, True)]
                reason = self.FindReasonNotAvailable(prereqs)
                if reason:
                    menuEntries.reasonsWhyNotAvailable['UI/Inflight/POS/AccessPOSRefinery'] = reason
            if checkRefinery and checkTransferDist:
                structureEntries += [[uiutil.MenuLabel('UI/ScienceAndIndustry/RunRefiningProcess'), self.RunRefiningProcess, (itemID,)]]
            if groupID == const.groupControlBunker:
                structureEntries += [[uiutil.MenuLabel('UI/FactionWarfare/IHub/OpenInfrastructureHubPanel'), self.OpenInfrastructureHubPanel, (itemID,)]]
            if checkStructure is True:
                checkIsSovereigntyClaimMarker = categoryID == const.categorySovereigntyStructure and groupID == const.groupSovereigntyClaimMarkers
                checkIsSovereigntyDisruptor = categoryID == const.categorySovereigntyStructure and groupID == const.groupSovereigntyDisruptionStructures
                checkCanAnchorStructure = bool(slimItem) and self.pwn.CanAnchorStructure(itemID)
                checkCanUnanchorStructure = bool(slimItem) and self.pwn.CanUnanchorStructure(itemID)
                checkCanOnlineStructure = bool(slimItem) and self.pwn.CanOnlineStructure(itemID)
                checkCanOfflineStructure = bool(slimItem) and self.pwn.CanOfflineStructure(itemID)
                checkCanAssumeControlStructure = bool(slimItem) and self.pwn.CanAssumeControlStructure(itemID)
                checkHasControlStructureTarget = bool(slimItem) and self.pwn.GetCurrentTarget(itemID) is not None
                checkHasControl = bool(slimItem) and slimItem.controllerID is not None
                checkHasMyControl = bool(slimItem) and slimItem.controllerID is not None and slimItem.controllerID == session.charid
                checkIsMineOrCorpsOrAlliancesOrOrphaned = bool(slimItem) and (self.pwn.StructureIsOrphan(itemID) or checkIsMineOrCorpsOrAlliances)
                checkIfIAmDirector = session.corprole & const.corpRoleDirector > 0
                checkInfrastructureHub = groupID == const.groupInfrastructureHub
                checkStructureFullyOnline = self.pwn.IsStructureFullyOnline(itemID)
                checkInPlanetMode = sm.GetService('viewState').IsViewActive('planet')
                if checkAnchorable and checkConfigDist and checkStructure:
                    if checkIsMineOrCorpsOrAlliances and checkCanAnchorStructure:
                        structureEntries += [[uiutil.MenuLabel('UI/Inflight/POS/AnchorStructure'), sm.StartService('posAnchor').StartAnchorPosSelect, (itemID,)]]
                    if checkIsMineOrCorpsOrAlliancesOrOrphaned and checkCanUnanchorStructure:
                        structureEntries += [[uiutil.MenuLabel('UI/Inflight/POS/UnanchorStructure'), self.AnchorStructure, (itemID, 0)]]
                    if checkIsMineOrCorpsOrAlliances and checkCanOnlineStructure and not checkIsSovereigntyDisruptor:
                        structureEntries += [[uiutil.MenuLabel('UI/Inflight/PutStructureOnline'), self.ToggleObjectOnline, (itemID, 1)]]
                    if checkIsMineOrCorpsOrAlliances and checkCanOfflineStructure:
                        structureEntries += [[uiutil.MenuLabel('UI/Inflight/PutStructureOffline'), self.ToggleObjectOnline, (itemID, 0)]]
                    if checkIsSovereigntyDisruptor and checkCanOnlineStructure:
                        structureEntries += [[uiutil.MenuLabel('UI/Inflight/PutStructureOnline'), self.ToggleObjectOnline, (itemID, 1)]]
                if checkAnchorable and checkIsMineOrCorpsOrAlliances and checkCanAssumeControlStructure and checkCanOfflineStructure and checkStructure and not checkSovStructure and not checkInPlanetMode:
                    if checkHasMyControl:
                        structureEntries += [[uiutil.MenuLabel('UI/Inflight/POS/RelinquishPOSControl'), self.pwn.RelinquishStructureControl, (slimItem,)]]
                    if not checkHasControl:
                        structureEntries += [[uiutil.MenuLabel('UI/Inflight/POS/AssumeStructureControl'), self.pwn.AssumeStructureControl, (slimItem,)]]
                if checkAnchorable and checkIsMineOrCorpsOrAlliances and checkCanAssumeControlStructure and checkStructure and checkHasMyControl and checkHasControlStructureTarget and not checkSovStructure:
                    structureEntries += [[uiutil.MenuLabel('UI/Inflight/POS/UnlcokSTructureTarget'), self.pwn.UnlockStructureTarget, (itemID,)]]
                if checkAnchorable and checkConfigDist and checkIsMyCorps and checkCanOfflineStructure and checkStructure and checkSovStructure and checkIfIAmDirector and checkIsSovereigntyClaimMarker:
                    structureEntries += [[uiutil.MenuLabel('UI/Inflight/POS/TransferSovStructureOwnership'), self.TransferOwnership, (itemID,)]]
                if checkConfigDist and checkIsMyCorps and checkInfrastructureHub and checkStructure and checkStructureFullyOnline:
                    structureEntries += [[uiutil.MenuLabel('UI/Menusvc/OpenHubManager'), sm.GetService('sov').GetInfrastructureHubWnd, (itemID,)]]
            if slimItem and (checkOrbital or checkPlanetCustomsOffice):
                checkCanAnchorOrbital = slimItem and slimItem.orbitalState in (None, entities.STATE_UNANCHORED)
                checkIsOrbitalAnchored = slimItem and slimItem.orbitalState == entities.STATE_ANCHORED
                checkCanUnanchorOrbital = slimItem and slimItem.groupID == const.groupOrbitalConstructionPlatforms
                checkCanConfigureOrbital = slimItem and slimItem.groupID != const.groupOrbitalConstructionPlatforms
                checkIsStationManager = session.corprole & const.corpRoleStationManager == const.corpRoleStationManager
                checkIfIAmDirector = session.corprole & const.corpRoleDirector > 0
                if checkBP and checkAnchorable and checkCanAnchorOrbital and checkIsMyCorps:
                    structureEntries += [[uiutil.MenuLabel('UI/Inflight/POS/AnchorObject'), self.AnchorOrbital, (itemID,)]]
                if checkBP and checkAnchorable and checkIsOrbitalAnchored and checkCanUnanchorOrbital and checkIsMyCorps:
                    structureEntries += [[uiutil.MenuLabel('UI/Inflight/UnanchorObject'), self.UnanchorOrbital, (itemID,)]]
                if checkBP and checkIsOrbitalAnchored and checkCanConfigureOrbital and checkIsMyCorps and checkIsStationManager:
                    structureEntries += [[uiutil.MenuLabel('UI/DustLink/ConfigureOrbital'), self.ConfigureOrbital, (slimItem,)]]
                if checkBP and checkIsOrbitalAnchored and checkCanConfigureOrbital and checkIsMyCorps and checkIfIAmDirector:
                    structureEntries += [[uiutil.MenuLabel('UI/Inflight/POS/TransferSovStructureOwnership'), self.TransferCorporationOwnership, (itemID,)]]
            if len(structureEntries):
                menuEntries.append(None)
                menuEntries.extend(structureEntries)
            if checkWreck:
                if checkWreckViewed:
                    menuEntries += [[uiutil.MenuLabel('UI/Inflight/MarkWreckNotViewed'), sm.GetService('wreck').MarkViewed, (itemID, False)]]
                else:
                    menuEntries += [[uiutil.MenuLabel('UI/Inflight/MarkWreckViewed'), sm.GetService('wreck').MarkViewed, (itemID, True)]]
            if slimItem and (ignoreTypeCheck or checkMultiGroups2 is False):
                menuEntries += [None]
                checkIsOrbital = slimItem and util.IsOrbital(slimItem.categoryID)
                if not checkMultiGroups2 and not checkCynoField and not checkIsOrbital and checkCanRename and checkRenameable:
                    menuEntries += [[uiutil.MenuLabel('UI/Commands/SetName'), self.SetName, (slimItem,)]]
            tagItemMenu = [(uiutil.MenuLabel('UI/Fleet/FleetTagNumber'), [ (' ' + str(i), self.TagItem, (itemID, str(i))) for i in xrange(10) ])]
            tagItemMenu += [(uiutil.MenuLabel('UI/Fleet/FleetTagLetter'), [ (' ' + str(i), self.TagItem, (itemID, str(i))) for i in 'ABCDEFGHIJXYZ' ])]
            menuEntries += [None]
            if checkInTargets and not checkBeingTargeted:
                menuEntries += [[uiutil.MenuLabel('UI/Inflight/UnlockTarget'), self.UnlockTarget, (itemID,)]]
            else:
                prereqs = [('notInTargets', checkInTargets, True), ('beingTargeted', checkBeingTargeted, False)]
                reason = self.FindReasonNotAvailable(prereqs)
                if reason:
                    menuEntries.reasonsWhyNotAvailable['UI/Inflight/UnlockTarget'] = reason
            if not checkMyShip and not checkInTargets and not checkBeingTargeted and not checkPMA and checkTargetingRange:
                menuEntries += [[uiutil.MenuLabel('UI/Inflight/LockTarget'), self.LockTarget, (itemID,)]]
            else:
                prereqs = [('isMyShip', checkMyShip, False),
                 ('alreadyTargeted', checkInTargets, False),
                 ('checkBeingTargeted', checkBeingTargeted, False),
                 ('badGroup',
                  checkPMA,
                  False,
                  {'groupName': groupName}),
                 ('notInTargetingRange', checkTargetingRange, True)]
                reason = self.FindReasonNotAvailable(prereqs)
                if reason:
                    menuEntries.reasonsWhyNotAvailable['UI/Inflight/LockTarget'] = reason
            if not checkMyShip and not checkPMA and checkFleet and checkIfImCommander:
                menuEntries += [[uiutil.MenuLabel('UI/Fleet/FleetSubmenus/FleetTagItem'), tagItemMenu]]
            if checkSpacePig and checkSpacePigDist:
                menuEntries += [[uiutil.MenuLabel('UI/Chat/StartConversation'), sm.StartService('agents').InteractWith, (sm.StartService('godma').GetType(typeID).agentID,)]]
            else:
                prereqs = [('notSpacePig', checkSpacePig, True)]
                reason = self.FindReasonNotAvailable(prereqs)
                if reason:
                    menuEntries.reasonsWhyNotAvailable['UI/Chat/StartConversation'] = reason
            menuEntries += [None]
            if ignoreTypeCheck or checkMultiGroups1 is True:
                menuEntries += [None]
                if checkMultiGroups1:
                    desc = localization.GetByLabel('UI/Menusvc/SetNewPasswordForContainerDesc')
                    menuEntries += [[uiutil.MenuLabel('UI/Inventory/ItemActions/SetNewPasswordForContainer'), self.AskNewContainerPassword, (itemID, desc, const.SCCPasswordTypeGeneral)]]
                if checkAuditLogSecureContainer:
                    desc = localization.GetByLabel('UI/Menusvc/SetNewConfigPasswordForContainer')
                    menuEntries += [[uiutil.MenuLabel('UI/Inventory/ItemActions/SetNewConfigPasswordForContainer'), self.AskNewContainerPassword, (itemID, desc, const.SCCPasswordTypeConfig)]]
                if checkIsMineOrCorps:
                    if checkAuditLogSecureContainer:
                        menuEntries += [[uiutil.MenuLabel('UI/Inventory/ItemActions/ViewLog'), self.ViewAuditLogForALSC, (itemID,)]]
                    if checkAuditLogSecureContainer:
                        menuEntries += [[uiutil.MenuLabel('UI/Inventory/ItemActions/ConfigureALSContainer'), self.ConfigureALSC, (itemID,)]]
                    if checkAuditLogSecureContainer:
                        menuEntries += [[uiutil.MenuLabel('UI/Commands/RetrievePassword'), self.RetrievePasswordALSC, (itemID,)]]
        checkInTactical = sm.StartService('tactical').CheckIfGroupIDActive(groupID)
        mapTypeID = typeID
        mapFunctionID = itemID
        if groupID in [const.groupSolarSystem, const.groupConstellation, const.groupRegion] and parentID != session.solarsystemid and not (bookmark and bookmark.itemID == bookmark.locationID and bookmark.x and bookmark.y and bookmark.z):
            mapFunctionID = mapItemID or itemID
        elif bookmark:
            if groupID != const.groupStation:
                mapFunctionID = bookmark.locationID
                parentBookmarkItem = sm.GetService('map').GetItem(mapFunctionID)
                if parentBookmarkItem and parentBookmarkItem.groupID == const.groupSolarSystem:
                    mapTypeID = parentBookmarkItem.typeID
        checkSameSolarSystemID = mapFunctionID and mapFunctionID == session.solarsystemid2
        checkCanBeWaypoint = mapTypeID == const.typeSolarSystem or groupID == const.groupStation
        if checkCanBeWaypoint:
            waypoints = sm.GetService('starmap').GetWaypoints()
            checkInWaypoints = mapFunctionID in waypoints
            if util.IsSolarSystem(mapFunctionID):
                solarSystemID = mapFunctionID
            elif util.IsStation(mapFunctionID):
                solarSystemID = cfg.stations.Get(mapFunctionID).solarSystemID
            else:
                log.LogError('mapFunctionID is not a solarsystem or a station, this will probably end up in a strange menu behaviour.', mapFunctionID)
                solarSystemID = mapFunctionID
            checkCanJump = session.solarsystemid is not None and solarSystemID in sm.GetService('map').GetNeighbors(session.solarsystemid)
            menuEntries += [None]
            if checkCanJump:

                def FindStargateAndRequestJump():
                    michelle = sm.GetService('michelle')
                    solarSystemItems = cfg.GetLocationsLocalBySystem(session.solarsystemid)
                    stargates = [ michelle.GetItem(x.itemID) for x in solarSystemItems if x.groupID == const.groupStargate ]
                    localStargate = [ x for x in stargates if solarSystemID == x.jumps[0].locationID ][0]
                    destSolarSystemID = localStargate.jumps[0].locationID
                    destStargateID = localStargate.jumps[0].toCelestialID
                    localStargateID = localStargate.itemID
                    self.StargateJump(localStargateID, destStargateID, destSolarSystemID)

                menuEntries += [[uiutil.MenuLabel('UI/Inflight/JumpThroughStargate'), FindStargateAndRequestJump, tuple()]]
            if mapFunctionID:
                if not checkSameSolarSystemID:
                    menuEntries += [[uiutil.MenuLabel('UI/Inflight/SetDestination'), sm.StartService('starmap').SetWaypoint, (mapFunctionID, True)]]
                if checkInWaypoints:
                    menuEntries += [[uiutil.MenuLabel('UI/Inflight/RemoveWaypoint'), sm.StartService('starmap').ClearWaypoints, (mapFunctionID,)]]
                else:
                    menuEntries += [[uiutil.MenuLabel('UI/Inflight/AddWaypoint'), sm.StartService('starmap').SetWaypoint, (mapFunctionID,)]]
                if checkFleet and (checkSolarSystem or checkStation):
                    menuEntries += [None]
                    menuEntries += [[uiutil.MenuLabel('UI/Fleet/FleetBroadcast/Commands/BroadcastTravelTo'), sm.GetService('fleet').SendBroadcast_TravelTo, (mapFunctionID,)]]
        elif checkStation and itemID and itemID != session.solarsystemid2:
            menuEntries += [None]
            menuEntries += [[uiutil.MenuLabel('UI/Inflight/SetDestination'), sm.StartService('starmap').SetWaypoint, (itemID, True)]]
        if session.solarsystemid and not checkIfLandmark:
            if checkInTactical == True:
                label = uiutil.MenuLabel('UI/Overview/RemoveGroupFromOverview', {'groupName': groupName})
                menuEntries += [[label, sm.StartService('tactical').ChangeSettings, ('groups', groupID, 0)]]
            elif checkInTactical == False:
                label = uiutil.MenuLabel('UI/Overview/AddGroupToOverview', {'groupName': groupName})
                menuEntries += [[label, sm.StartService('tactical').ChangeSettings, ('groups', groupID, 1)]]
        if not bookmark and checkMultiCategs1 is False:
            if groupID == const.groupBeacon:
                beacon = sm.StartService('michelle').GetItem(itemID)
                if beacon and hasattr(beacon, 'dunDescriptionID') and beacon.dunDescriptionID:
                    hint = localization.GetByMessageID(beacon.dunDescriptionID)
            if itemID and parentID:
                menuEntries += [None]
                if not checkMultiCategs1 and not checkIfLandmark:
                    menuEntries += [[uiutil.MenuLabel('UI/Inflight/BookmarkLocation'), self.Bookmark, (itemID,
                       typeID,
                       parentID,
                       hint)]]
        if ignoreTypeCheck or mapFunctionID is not None:
            if groupID in [const.groupSolarSystem, const.groupConstellation, const.groupRegion]:
                checkMultiGroups3 = mapFunctionID is not None
                menuEntries += [None]
                if checkMultiGroups3:
                    menuEntries += [[uiutil.MenuLabel('UI/Commands/ShowLocationOnMap'), self.ShowInMap, (mapFunctionID,)]]
                    label = uiutil.MenuLabel('UI/Inflight/ShowInMapBrowser', {'locationType': groupName})
                    menuEntries += [[label, self.ShowInMapBrowser, (mapFunctionID,)]]
                    if mapFunctionID not in sm.StartService('pathfinder').GetAvoidanceItems():
                        label = uiutil.MenuLabel('UI/Inflight/AvoidLocation', {'theLocation': mapFunctionID,
                         'locationType': groupName})
                        menuEntries += [[label, sm.StartService('pathfinder').AddAvoidanceItem, (mapFunctionID,)]]
                    else:
                        label = uiutil.MenuLabel('UI/Inflight/StopAvoidingLocation', {'theLocation': mapFunctionID,
                         'locationType': groupName})
                        menuEntries += [[label, sm.StartService('pathfinder').RemoveAvoidanceItem, (mapFunctionID,)]]
        if checkPlanet and itemID is not None:
            if checkPlanet and not checkThisPlanetOpen:
                openPlanet = lambda planetID: sm.GetService('viewState').ActivateView('planet', planetID=planetID)
                menuEntries += [[uiutil.MenuLabel('UI/PI/Common/ViewInPlanetMode'), openPlanet, (itemID,)]]
            if checkPlanet and checkThisPlanetOpen:
                menuEntries += [[uiutil.MenuLabel('UI/PI/Common/ExitPlanetMode'), sm.GetService('viewState').CloseSecondaryView, ()]]
        if not ignoreDroneMenu and slimItem and categoryID == const.categoryDrone:
            newMenuEntries = MenuList([None])
            for me in self.DroneMenu([[itemID, groupID, slimItem.ownerID]], 1):
                newMenuEntries.extend(me)

            newMenuEntries.extend(menuEntries)
            menuEntries = newMenuEntries
        if not (filterFunc and uiutil.MenuLabel('UI/Commands/ShowInfo') in filterFunc):
            if not checkMultiSelection:
                menuEntries += [[uiutil.MenuLabel('UI/Commands/ShowInfo'), self.ShowInfo, (typeID,
                   itemID,
                   0,
                   None,
                   parentID)]]
        m += self.ParseMenu(menuEntries, filterFunc)
        m.reasonsWhyNotAvailable.update(getattr(menuEntries, 'reasonsWhyNotAvailable', None))
        if groupID == const.groupPlanet:
            moons = self.GetPrimedMoons(itemID)
            if moons:
                m.append((uiutil.MenuLabel('UI/Menusvc/MoonsMenuOption'), ('isDynamic', self.GetMoons, (itemID, moons))))
            if checkBP and checkInSystem:
                customsOfficeIDs = sm.GetService('planetInfo').GetOrbitalsForPlanet(itemID, const.groupPlanetaryCustomsOffices)
                if customsOfficeIDs is not None and len(customsOfficeIDs) > 0:
                    for customsOfficeID in customsOfficeIDs:
                        customsOfficeBall = bp.GetBall(customsOfficeID)
                        if customsOfficeBall:
                            m.append((uiutil.MenuLabel('UI/PI/Common/CustomsOffice'), ('isDynamic', self.GetCustomsOfficeMenu, (customsOfficeID,))))
                        break

            districts = sm.GetService('district').GetDistrictByPlanet(itemID)
            if len(districts):
                m.append((uiutil.MenuLabel('UI/Menusvc/DistrictsMenuOption'), ('isDynamic', self.GetDistricts, (itemID, districts))))
        if checkShip is True and slimItem:
            m += [None] + [(uiutil.MenuLabel('UI/Common/Pilot'), ('isDynamic', self.CharacterMenu, (slimItem.charID or slimItem.ownerID,
                [],
                slimItem.corpID,
                0,
                ['GM / WM Extras'])))]
        if not (filterFunc and 'UI/Inventory/ItemActions/ViewTypesMarketDetails' in filterFunc) and checkHasMarketGroup:
            m += [(uiutil.MenuLabel('UI/Inventory/ItemActions/ViewTypesMarketDetails'), self.ShowMarketDetails, (util.KeyVal(typeID=typeID),))]
        if not (filterFunc and 'UI/Inventory/ItemActions/FindInContracts' in filterFunc) and checkIsPublished and not ignoreMarketDetails:
            m += [(uiutil.MenuLabel('UI/Inventory/ItemActions/FindInContracts'), sm.GetService('contracts').FindRelated, (typeID,
               None,
               None,
               None,
               None,
               None))]
        if not (filterFunc and 'GM / WM Extras' in filterFunc) and session.role & (service.ROLE_GML | service.ROLE_WORLDMOD):
            m.insert(0, ('GM / WM Extras', ('isDynamic', self.GetGMMenu, (itemID,
               slimItem,
               None,
               None,
               mapItem,
               typeID))))
        return m

    def FindDist(self, currentDist, bookmark, ownBall, bp, *args):
        dist = currentDist
        if bookmark and bookmark.locationID and bookmark.locationID == session.solarsystemid:
            if ownBall:
                myLoc = foo.Vector3(ownBall.x, ownBall.y, ownBall.z)
            else:
                myLoc = None
            if (bookmark.typeID == const.typeSolarSystem or bookmark.itemID == bookmark.locationID) and bookmark.x is not None:
                location = None
                if hasattr(bookmark, 'locationType') and bookmark.locationType in ('agenthomebase', 'objective'):
                    entryPoint = sm.GetService('agents').GetAgentMoniker(bookmark.agentID).GetEntryPoint()
                    if entryPoint is not None:
                        location = foo.Vector3(*entryPoint)
                if location is None:
                    location = foo.Vector3(bookmark.x, bookmark.y, bookmark.z)
                if myLoc and location:
                    dist = (myLoc - location).Length()
                else:
                    dist = 0
            else:
                dist = 0.0
                if bookmark.itemID in bp.balls:
                    b = bp.balls[bookmark.itemID]
                    dist = b.surfaceDist
        return dist

    def JumpPortalBridgeMenu(self, itemID):
        l = []
        fromSystem = cfg.evelocations.Get(session.solarsystemid)
        for solarSystemID, structureID in sm.RemoteSvc('map').GetLinkableJumpArrays():
            if solarSystemID == session.solarsystemid:
                continue
            toSystem = cfg.evelocations.Get(solarSystemID)
            dist = uix.GetLightYearDistance(fromSystem, toSystem)
            l.append(('%s<t>%.1f ly' % (toSystem.name, dist), (solarSystemID, structureID)))

        pick = uix.ListWnd(l, 'generic', localization.GetByLabel('UI/Inflight/PickDestination'), isModal=1, scrollHeaders=[localization.GetByLabel('UI/Common/LocationTypes/SolarSystem'), localization.GetByLabel('UI/Common/Distance')])
        if pick:
            remoteSolarSystemID, remoteItemID = pick[1]
            self.BridgePortals(itemID, remoteSolarSystemID, remoteItemID)

    def BridgePortals(self, localItemID, remoteSolarSystemID, remoteItemID):
        posLocation = util.Moniker('posMgr', session.solarsystemid)
        posLocation.InstallJumpBridgeLink(localItemID, remoteSolarSystemID, remoteItemID)

    def UnbridgePortal(self, itemID):
        posLocation = util.Moniker('posMgr', session.solarsystemid)
        posLocation.UninstallJumpBridgeLink(itemID)

    def JumpThroughPortal(self, itemID):
        bp = sm.StartService('michelle').GetRemotePark()
        if bp is None:
            return
        slim = sm.services['michelle'].GetItem(itemID)
        remoteStructureID = slim.remoteStructureID
        if not remoteStructureID:
            return
        remoteSystemID = slim.remoteSystemID
        self.LogNotice('Jump Through Portal', itemID, remoteStructureID, remoteSystemID)
        sm.StartService('sessionMgr').PerformSessionChange('jump', bp.CmdJumpThroughCorporationStructure, itemID, remoteStructureID, remoteSystemID)

    def GetFuelConsumptionOfJumpBridgeForMyShip(self, fromSystem, toSystem, toStructureType):
        if not session.shipid:
            return
        myShip = sm.services['godma'].GetItem(session.shipid)
        if myShip is None:
            return
        distance = uix.GetLightYearDistance(fromSystem, toSystem, False)
        if distance is None:
            return
        attrDict = sm.GetService('info').GetAttrDict(toStructureType)
        if const.attributeJumpDriveConsumptionAmount in attrDict:
            consumptionRate = attrDict[const.attributeJumpDriveConsumptionAmount]
        else:
            consumptionRate = 1
        shipMass = getattr(myShip, 'mass', None)
        if shipMass is None:
            shipMass = 1
        if const.attributeJumpPortalConsumptionMassFactor in attrDict:
            massFactor = shipMass * attrDict[const.attributeJumpPortalConsumptionMassFactor]
        return (pos.GetJumpFuelConsumption(distance, consumptionRate, massFactor), attrDict.get(const.attributeJumpDriveConsumptionType, None))

    def GetHybridBeaconJumpMenu(self):
        fleetMenu = []
        allianceMenu = []
        menuSize = 20
        if session.fleetid:
            beacons = sm.GetService('fleet').GetActiveBeacons()
            for charID, beaconArgs in beacons.iteritems():
                solarSystemID, itemID = beaconArgs
                if solarSystemID != session.solarsystemid:
                    character = cfg.eveowners.Get(charID)
                    charName = uiutil.MenuLabel('UI/Menusvc/BeaconLabel', {'name': character.name,
                     'system': solarSystemID})
                    fleetMenu.append((character.name, (charID, beaconArgs, charName)))

            fleetMenu = uiutil.SortListOfTuples(fleetMenu)
        if session.allianceid:
            beacons = sm.RemoteSvc('map').GetAllianceBeacons()
            for solarSystemID, structureID, structureTypeID in beacons:
                if solarSystemID != session.solarsystemid:
                    solarsystem = cfg.evelocations.Get(solarSystemID)
                    invType = cfg.invtypes.Get(structureTypeID)
                    structureName = uiutil.MenuLabel('UI/Menusvc/BeaconLabel', {'name': invType.name,
                     'system': solarSystemID})
                    allianceMenu.append((solarsystem.name, (solarSystemID, structureID, structureName)))

            allianceMenu = uiutil.SortListOfTuples(allianceMenu)
        fullMenu = []
        if len(fleetMenu) > 0:
            for charID, beaconArgs, charName in fleetMenu:
                fullMenu.append([charName, self.JumpToBeaconFleet, (charID, beaconArgs)])

        if len(allianceMenu) > 0:
            if len(fullMenu) > 0:
                fullMenu.append(None)
            am = []
            for solarSystemID, structureID, structureName in allianceMenu:
                systemName = cfg.evelocations.Get(solarSystemID).name
                am.append([structureName,
                 self.JumpToBeaconAlliance,
                 (solarSystemID, structureID),
                 systemName])

            fullMenu.extend(self.CreateSubMenusForLongMenus(am, menuSize, subMenuFunc=self.GetJumpSubMenu))
        if len(fullMenu) > 0:
            return fullMenu
        else:
            return ([uiutil.MenuLabel('UI/Inflight/NoDestination'), self.DoNothing],)

    def OpenCapitalNavigation(self, *args):
        if util.GetActiveShip():
            form.CapitalNav.Open()

    def OpenBountyOffice(self, charID, *args):
        wnd = form.BountyWindow.GetIfOpen()
        if not wnd:
            wnd = form.BountyWindow.Open()
        wnd.ownerID = charID
        wnd.ShowResult(charID)

    def GetHybridBridgeMenu(self):
        fleetMenu = []
        allianceMenu = []
        menuSize = 20
        if session.fleetid:
            menu = []
            beacons = sm.GetService('fleet').GetActiveBeacons()
            for charID, beaconArgs in beacons.iteritems():
                solarSystemID, itemID = beaconArgs
                if solarSystemID != session.solarsystemid:
                    character = cfg.eveowners.Get(charID)
                    charName = uiutil.MenuLabel('UI/Menusvc/BeaconLabel', {'name': character.name,
                     'system': solarSystemID})
                    menu.append((character.name, (charID, beaconArgs, charName)))

            menu = uiutil.SortListOfTuples(menu)
            fleetMenu = [ (charName, self.BridgeToBeacon, (charID, beaconArgs)) for charID, beaconArgs, charName in menu ]
        if session.allianceid:
            menu = []
            datas = sm.RemoteSvc('map').GetAllianceBeacons()
            for solarSystemID, structureID, structureTypeID in datas:
                if solarSystemID != session.solarsystemid:
                    solarsystem = cfg.evelocations.Get(solarSystemID)
                    invtype = cfg.invtypes.Get(structureTypeID)
                    structureName = uiutil.MenuLabel('UI/Menusvc/BeaconLabel', {'name': invtype.name,
                     'system': solarSystemID})
                    menu.append((solarsystem.name, (solarSystemID, structureID, structureName)))

            menu = uiutil.SortListOfTuples(menu)
            am = [ (structureName,
             self.BridgeToBeaconAlliance,
             (solarSystemID, structureID),
             cfg.evelocations.Get(solarSystemID).name) for solarSystemID, structureID, structureName in menu ]
            allianceMenu = self.CreateSubMenusForLongMenus(am, menuSize, subMenuFunc=self.GetAllianceBeaconSubMenu)
        if len(fleetMenu) > 0 and len(allianceMenu) > 0:
            fleetMenu.append(None)
        fleetMenu.extend(allianceMenu)
        if len(fleetMenu) == 0:
            return ([uiutil.MenuLabel('UI/Inflight/NoDestination'), self.DoNothing],)
        else:
            return fleetMenu

    def CreateSubMenusForLongMenus(self, menuList, menuSize, subMenuFunc, *args):
        allMenuItems = []
        menuListLeft = menuList[:]
        while len(menuListLeft) > menuSize:
            allMenuItems.append(menuListLeft[:menuSize])
            menuListLeft = menuListLeft[menuSize:]

        if menuListLeft:
            allMenuItems.append(menuListLeft)
        if not allMenuItems:
            m = allMenuItems
        if len(allMenuItems) == 1:
            m = subMenuFunc(allMenuItems[0])
        else:
            m = []
            for sub in allMenuItems:
                firstItem = sub[0]
                lastItem = sub[-1]
                if firstItem:
                    firstLetter = firstItem[3][0]
                else:
                    firstLetter = '0'
                if lastItem:
                    lastLetter = lastItem[3][0]
                else:
                    lastLetter = '-1'
                m.append(('%s ... %s' % (firstLetter, lastLetter), ('isDynamic', subMenuFunc, [sub])))

        return m

    def GetJumpSubMenu(self, subMenuItems, *args):
        m = []
        for menuItem in subMenuItems:
            if menuItem is None:
                m.append(None)
                continue
            name, eachFunc, eachArgs, systemName = menuItem
            m.append([name, eachFunc, eachArgs])

        return m

    def GetAllianceBeaconSubMenu(self, structureIDs):
        m = []
        for menuItem in structureIDs:
            if menuItem is None:
                m.append(None)
                continue
            structureName, eachFunc, eachArgs, systemName = menuItem
            solarSystemID, structureID = eachArgs
            m.append([structureName, eachFunc, eachArgs])

        return m

    def RigSlotMenu(self, itemID):
        menu = []
        if itemID == session.shipid:
            ship = sm.GetService('godma').GetItem(session.shipid)
            for module in ship.modules:
                rigslots = [ getattr(const, 'flagRigSlot%s' % i, None) for i in xrange(8) ]
                if module.flagID in rigslots:
                    menu.append([module.name + ' (Slot %s)' % rigslots.index(module.flagID),
                     [(uiutil.MenuLabel('UI/Commands/ShowInfo'), self.ShowInfo, (module.typeID, module.itemID))],
                     None,
                     ()])

        if not menu:
            return []
        return [(uiutil.MenuLabel('UI/Fitting/RigsMenuOption'), menu)]

    def RemoveRig(self, moduleID, shipID):
        if session.stationid:
            self.invCache.GetInventory(const.containerHangar).Add(moduleID, shipID)

    def RigFittingCheck(self, invItem):
        moduleEffects = cfg.dgmtypeeffects.get(invItem.typeID, [])
        for mEff in moduleEffects:
            if mEff.effectID == const.effectRigSlot:
                if eve.Message('RigFittingInfo', {}, uiconst.OKCANCEL) != uiconst.ID_OK:
                    return 0

        return 1

    def ConfirmMenu(self, func):
        m = [(uiutil.MenuLabel('UI/Menusvc/ConfirmMenuOption'), func)]
        return m

    def WarpToMenu(self, func, ID):
        ranges = [const.minWarpEndDistance,
         (const.minWarpEndDistance / 10000 + 1) * 10000,
         (const.minWarpEndDistance / 10000 + 2) * 10000,
         (const.minWarpEndDistance / 10000 + 3) * 10000,
         (const.minWarpEndDistance / 10000 + 5) * 10000,
         (const.minWarpEndDistance / 10000 + 7) * 10000,
         const.maxWarpEndDistance]
        defMenuWarpOptions = [ (util.FmtDist(rnge), self.SetDefaultWarpToDist, (rnge,)) for rnge in ranges ]
        warpDistMenu = [(uiutil.MenuLabel('UI/Inflight/WarpToWithin', {'distance': util.FmtDist(ranges[0])}), func, (ID, float(ranges[0]))),
         (uiutil.MenuLabel('UI/Inflight/WarpToWithin', {'distance': util.FmtDist(ranges[1])}), func, (ID, float(ranges[1]))),
         (uiutil.MenuLabel('UI/Inflight/WarpToWithin', {'distance': util.FmtDist(ranges[2])}), func, (ID, float(ranges[2]))),
         (uiutil.MenuLabel('UI/Inflight/WarpToWithin', {'distance': util.FmtDist(ranges[3])}), func, (ID, float(ranges[3]))),
         (uiutil.MenuLabel('UI/Inflight/WarpToWithin', {'distance': util.FmtDist(ranges[4])}), func, (ID, float(ranges[4]))),
         (uiutil.MenuLabel('UI/Inflight/WarpToWithin', {'distance': util.FmtDist(ranges[5])}), func, (ID, float(ranges[5]))),
         (uiutil.MenuLabel('UI/Inflight/WarpToWithin', {'distance': util.FmtDist(ranges[6])}), func, (ID, float(ranges[6]))),
         None,
         (uiutil.MenuLabel('UI/Inflight/Submenus/SetDefaultWarpRange'), defMenuWarpOptions)]
        return warpDistMenu

    def MergeMenus(self, menus):
        if not menus:
            return []
        allCaptions = []
        allEntries = []
        allReasons = {}
        for menu in menus:
            i = 0
            if getattr(menu, 'reasonsWhyNotAvailable', {}):
                allReasons.update(menu.reasonsWhyNotAvailable)
            for each in menu:
                if each is None:
                    if len(allEntries) <= i:
                        allEntries.append(None)
                    else:
                        while allEntries[i] != None:
                            i += 1
                            if i == len(allEntries):
                                allEntries.append(None)
                                break

                else:
                    if isinstance(each[0], uiutil.MenuLabel):
                        eachCaption = each[0][0]
                        kwords = each[0][1]
                    else:
                        eachCaption = each[0]
                        kwords = {}
                    if (eachCaption, kwords) not in allCaptions:
                        allEntries.insert(i, each[0])
                        allCaptions.append((eachCaption, kwords))
                i += 1

        menus = filter(None, [ filter(None, each) for each in menus ])
        ret = MenuList()
        ret.reasonsWhyNotAvailable = allReasons
        for eachEntry in allEntries:
            if eachEntry is None:
                ret.append(None)
                continue
            keywords = {}
            if isinstance(eachEntry, uiutil.MenuLabel):
                caption = eachEntry[0]
                keywords = eachEntry[1]
            else:
                caption = eachEntry
            lst = []
            isList = None
            broken = 0
            for menu in menus:
                for entry in menu:
                    entryKeywords = {}
                    if isinstance(eachEntry, uiutil.MenuLabel):
                        entryCaption = entry[0][0]
                        entryKeywords = entry[0][1]
                    else:
                        entryCaption = entry[0]
                    if entryCaption == caption and entryKeywords == keywords:
                        if type(entry[1]) in (str, unicode):
                            ret.append((eachEntry, entry[1]))
                            broken = 1
                            break
                        if type(entry[1]) == tuple and entry[1][0] == 'isDynamic' and len(entry) == 2:
                            ret.append((eachEntry, entry[1]))
                            broken = 1
                            break
                        if isList is None:
                            isList = type(entry[1]) == list
                        if isList != (type(entry[1]) == list):
                            broken = 1
                        elif isList:
                            lst.append(entry[1])
                        else:
                            lst.append(entry[1:])
                        break

                if broken:
                    break

            if not broken:
                if isList:
                    ret.append((eachEntry, self.MergeMenus(lst)))
                elif self.CaptionIsInMultiFunctions(caption) or len(lst) and len(lst[0]) and lst[0][0] in self.multiFunctionFunctions:
                    mergedArgs = []
                    rest = []
                    for entry in lst:
                        _func = entry[0]
                        args = entry[1]
                        rest = entry[2:]
                        if type(args) == type([]):
                            mergedArgs += args
                        else:
                            log.LogWarn('unsupported format of arguments for MergeMenu, function label: ', caption)

                    if isinstance(rest, tuple):
                        rest = list(rest)
                    if mergedArgs:
                        if type(lst[0][0]) == tuple and lst[0][0][0] == 'isDynamic':
                            ret.append([eachEntry, ('isDynamic', lst[0][0][1], lst[0][0][2] + (mergedArgs,))] + rest)
                        else:
                            ret.append([eachEntry, self.CheckLocked, (lst[0][0], mergedArgs)] + rest)
                else:
                    ret.append((eachEntry, self.ExecMulti, lst))

        return ret

    def CaptionIsInMultiFunctions(self, caption):
        if isinstance(caption, uiutil.MenuLabel):
            functionName = caption[0]
        else:
            functionName = caption
        return functionName in self.multiFunctions

    def ExecMulti(self, *actions):
        for each in actions:
            uthread.new(self.ExecAction, each)

    def ExecAction(self, action):
        apply(*action)

    def GetMenuFormItemIDTypeID(self, itemID, typeID, bookmark = None, filterFunc = None, invItem = None, ignoreMarketDetails = 1, **kwargs):
        if typeID is None:
            return []
        elif invItem:
            return self.InvItemMenu(invItem, filterFunc=filterFunc)
        else:
            typeinfo = cfg.invtypes.Get(typeID)
            groupinfo = typeinfo.Group()
            if typeinfo.groupID in (const.groupCharacter,):
                return self.CharacterMenu(itemID, filterFunc=filterFunc, **kwargs)
            elif groupinfo.categoryID in (const.categoryCelestial,
             const.categoryStructure,
             const.categoryStation,
             const.categoryShip,
             const.categoryEntity,
             const.categoryDrone,
             const.categoryAsteroid):
                return self.CelestialMenu(itemID, typeID=typeID, bookmark=bookmark, filterFunc=filterFunc, ignoreMarketDetails=ignoreMarketDetails)
            m = []
            if not (filterFunc and 'UI/Commands/ShowInfo' in filterFunc):
                m += [(uiutil.MenuLabel('UI/Commands/ShowInfo'), self.ShowInfo, (typeID,
                   itemID,
                   0,
                   None,
                   None))]
            if typeinfo.groupID == const.groupCorporation and util.IsCorporation(itemID) and not util.IsNPC(itemID):
                m += [(uiutil.MenuLabel('UI/Commands/GiveMoney'), sm.StartService('wallet').TransferMoney, (session.charid,
                   None,
                   itemID,
                   None))]
            if typeinfo.groupID in [const.groupCorporation, const.groupAlliance, const.groupFaction]:
                addressBookSvc = sm.GetService('addressbook')
                inAddressbook = addressBookSvc.IsInAddressBook(itemID, 'contact')
                isBlocked = addressBookSvc.IsBlocked(itemID)
                isNPC = util.IsNPC(itemID)
                if inAddressbook:
                    m += ((uiutil.MenuLabel('UI/PeopleAndPlaces/EditContact'), addressBookSvc.AddToPersonalMulti, [itemID, 'contact', True]),)
                    m += ((uiutil.MenuLabel('UI/PeopleAndPlaces/RemoveContact'), addressBookSvc.DeleteEntryMulti, [[itemID], 'contact']),)
                else:
                    m += ((uiutil.MenuLabel('UI/PeopleAndPlaces/AddContact'), addressBookSvc.AddToPersonalMulti, [itemID, 'contact']),)
                if not isNPC:
                    if isBlocked:
                        m += ((uiutil.MenuLabel('UI/PeopleAndPlaces/UnblockContact'), addressBookSvc.UnblockOwner, [[itemID]]),)
                    else:
                        m += ((uiutil.MenuLabel('UI/PeopleAndPlaces/BlockContact'), addressBookSvc.BlockOwner, [itemID]),)
                iAmDiplomat = (const.corpRoleDirector | const.corpRoleDiplomat) & session.corprole != 0
                if iAmDiplomat:
                    inCorpAddressbook = addressBookSvc.IsInAddressBook(itemID, 'corpcontact')
                    if inCorpAddressbook:
                        m += ((uiutil.MenuLabel('UI/PeopleAndPlaces/EditCorpContact'), addressBookSvc.AddToPersonalMulti, [itemID, 'corpcontact', True]),)
                        m += ((uiutil.MenuLabel('UI/PeopleAndPlaces/RemoveCorpContact'), addressBookSvc.DeleteEntryMulti, [[itemID], 'corpcontact']),)
                    else:
                        m += ((uiutil.MenuLabel('UI/PeopleAndPlaces/AddCorpContact'), addressBookSvc.AddToPersonalMulti, [itemID, 'corpcontact']),)
                    if session.allianceid and not util.IsDustCharacter(itemID):
                        execCorp = sm.GetService('alliance').GetAlliance(session.allianceid).executorCorpID == session.corpid
                        if execCorp:
                            inAllianceAddressbook = addressBookSvc.IsInAddressBook(itemID, 'alliancecontact')
                            if inAllianceAddressbook:
                                m += ((uiutil.MenuLabel('UI/PeopleAndPlaces/EditAllianceContact'), addressBookSvc.AddToPersonalMulti, [itemID, 'alliancecontact', True]),)
                                m += ((uiutil.MenuLabel('UI/PeopleAndPlaces/RemoveAllianceContact'), addressBookSvc.DeleteEntryMulti, [[itemID], 'alliancecontact']),)
                            else:
                                m += ((uiutil.MenuLabel('UI/PeopleAndPlaces/AddAllianceContact'), addressBookSvc.AddToPersonalMulti, [itemID, 'alliancecontact']),)
                if session.corprole & const.corpRoleDirector == const.corpRoleDirector and typeinfo.groupID in (const.groupCorporation, const.groupAlliance):
                    if itemID not in (session.corpid, session.allianceid) and not util.IsNPC(itemID):
                        m += ((uiutil.MenuLabel('UI/Corporations/CorporationWindow/Alliances/Rankings/DeclareWar'), self.DeclareWarAgainst, [itemID]),)
            if not (filterFunc and 'UI/Inventory/ItemActions/ViewTypesMarketDetails' in filterFunc) and not ignoreMarketDetails:
                if session.charid:
                    if cfg.invtypes.Get(typeID).marketGroupID is not None:
                        m += [(uiutil.MenuLabel('UI/Inventory/ItemActions/ViewTypesMarketDetails'), self.ShowMarketDetails, (util.KeyVal(typeID=typeID),))]
                    if cfg.invtypes.Get(typeID).published:
                        m += [(uiutil.MenuLabel('UI/Inventory/ItemActions/FindInContracts'), sm.GetService('contracts').FindRelated, (typeID,
                           None,
                           None,
                           None,
                           None,
                           None))]
            return m

    def ParseMenu(self, menuEntries, filterFunc = None):
        m = MenuList()
        for menuProps in menuEntries:
            if menuProps is None:
                m += [None]
                continue
            label = menuProps[0]
            if len(menuProps) == 3:
                label, func, test = menuProps
                if test == None:
                    log.LogTraceback('Someone still using None as args')
            if filterFunc and label in filterFunc:
                continue
            m += [menuProps]

        m.reasonsWhyNotAvailable = getattr(menuEntries, 'reasonsWhyNotAvailable', {})
        return m

    def ChangePartitionLevel(self, level):
        settings.user.ui.Set('partition_box_showall', level)

    def GetPrimedMoons(self, planetID):
        if session.solarsystemid2 not in self.primedMoons:
            self.PrimeMoons()
        return self.primedMoons[session.solarsystemid2].get(planetID, [])

    def PrimeMoons(self):
        if session.solarsystemid2 not in self.primedMoons:
            solarsystemitems = sm.GetService('map').GetSolarsystemItems(session.solarsystemid2)
            moonsByPlanets = {}
            for item in solarsystemitems:
                if item.groupID != const.groupMoon:
                    continue
                moonsByPlanets.setdefault(item.orbitID, []).append(item)

            self.primedMoons[session.solarsystemid2] = moonsByPlanets

    def GetMoons(self, planetID, moons, *args):
        if len(moons):
            moons = uiutil.SortListOfTuples([ (moon.orbitIndex, moon) for moon in moons ])
            moonmenu = []
            for moon in moons:
                label = uiutil.MenuLabel('UI/Inflight/Submenus/MoonX', {'moonNumber': moon.orbitIndex})
                moonmenu.append((label, ('isDynamic', self.ExpandMoon, (moon.itemID, moon))))

            return moonmenu
        return [(uiutil.MenuLabel('UI/Menusvc/PlanetHasNoMoons'), self.DoNothing)]

    def GetDistricts(self, planetID, districts, *args):
        menu = []
        for district in districts:
            label = uiutil.MenuLabel('UI/Inflight/Submenus/DistrictX', {'districtIndex': district['index']})
            menu.append((label, ('isDynamic', self.ExpandDistrict, (district,))))

        return menu

    def ExpandDistrict(self, district):
        defaultLabel = self.DefaultWarpToLabel()
        defaultDistance = float(self.GetDefaultActionDistance('WarpTo'))
        menu = [(defaultLabel, self.WarpToDistrict, (district['districtID'], defaultDistance)), (uiutil.MenuLabel('UI/Inflight/Submenus/WarpToWithin'), self.WarpToMenu(self.WarpToDistrict, district['districtID']))]
        if session.role & (service.ROLE_GML | service.ROLE_WORLDMOD):
            menu.insert(0, ('GM / WM Extras', ('isDynamic', self.GetGMMenu, (district['districtID'],
               None,
               None,
               None,
               None))))
        return menu

    def ShowDistrictInfo(self, district):
        pass

    def GetCustomsOfficeMenu(self, customsOfficeID, *args):
        return sm.StartService('menu').CelestialMenu(customsOfficeID)

    def TransferToCargo(self, itemKey):
        structure = self.invCache.GetInventoryFromId(itemKey[0])
        structure.RemoveChargeToCargo(itemKey)

    def DoNothing(self, *args):
        pass

    def ExpandMoon(self, itemID, moon):
        return sm.StartService('menu').CelestialMenu(itemID, moon)

    def Activate(self, slimItem):
        if eve.rookieState and eve.rookieState < 22:
            return
        itemID, groupID, categoryID = slimItem.itemID, slimItem.groupID, slimItem.categoryID
        if itemID == session.shipid:
            myship = sm.StartService('godma').GetItem(session.shipid)
            if myship.groupID == const.groupCapsule:
                bp = sm.StartService('michelle').GetRemotePark()
                if bp is not None:
                    bp.CmdStop()
            else:
                uicore.cmd.OpenCargoHoldOfActiveShip()
            return
        bp = sm.StartService('michelle').GetBallpark()
        if bp:
            ownBall = bp.GetBall(session.shipid)
            otherBall = bp.GetBall(itemID)
            dist = None
            if ownBall and otherBall:
                dist = bp.GetSurfaceDist(ownBall.id, otherBall.id)
            if dist < const.minWarpDistance:
                if groupID == const.groupStation and dist < const.maxDockingDistance:
                    self.Dock(itemID)
                elif groupID == const.groupControlBunker:
                    self.OpenInfrastructureHubPanel(otherBall.id)
                elif groupID in (const.groupWreck,
                 const.groupCargoContainer,
                 const.groupSecureCargoContainer,
                 const.groupAuditLogSecureContainer,
                 const.groupFreightContainer,
                 const.groupSpawnContainer,
                 const.groupDeadspaceOverseersBelongings):
                    self.OpenCargo(itemID, 'SomeCargo')
                else:
                    self.Approach(itemID, 50)

    def SetDefaultWarpToDist(self, newRange):
        util.UpdateRangeSetting('WarpTo', newRange)

    def SetDefaultOrbitDist(self, newRange, *args):
        util.UpdateRangeSetting('Orbit', newRange)

    def SetDefaultKeepAtRangeDist(self, newRange, *args):
        util.UpdateRangeSetting('KeepAtRange', newRange)

    def FindReasonNotAvailable(self, prereqs):
        for each in prereqs:
            d = {}
            if len(each) == 4:
                label, value, expected, d = each
            else:
                label, value, expected = each
            if value == expected:
                continue
            if label not in self.allReasonsDict:
                continue
            reasonPath = self.allReasonsDict[label]
            reason = localization.GetByLabel(reasonPath, **d)
            return reason

    def ShowDamageLocators(self, itemID):
        ball = sm.StartService('michelle').GetBallpark().GetBall(itemID)
        ship = ball.model
        if ship:
            if getattr(ball, 'visualizingDamageLocators', False):
                toRemove = []
                for child in ship.children:
                    if child.name == 'DamageLocatorVisualization':
                        toRemove.append(child)
                    elif child.name == 'ImpactDirectionVisualization':
                        toRemove.append(child)

                for tr in toRemove:
                    ship.children.remove(tr)

                setattr(ball, 'visualizingDamageLocators', False)
            else:
                scale = ship.boundingSphereRadius / 10
                for i in range(len(ship.damageLocators)):
                    damageLocator = ship.damageLocators[i]
                    sphere = trinity.Load('res:/model/global/damageLocator.red')
                    sphere.translation = damageLocator[0]
                    sphere.scaling = [scale, scale, scale]
                    ship.children.append(sphere)
                    impacDir = damageLocator[1]
                    direction = trinity.Load('res:/model/global/impactDirection.red')
                    direction.translation = damageLocator[0]
                    direction.scaling = [scale, scale, scale]
                    direction.rotation = impacDir
                    ship.children.append(direction)

                setattr(ball, 'visualizingDamageLocators', True)

    def ShowDestinyBalls(self, itemID, showType):
        miniballObject = None
        scene = sm.GetService('sceneManager').GetRegisteredScene('default')
        nameOfMiniballs = 'miniballs_of_' + str(itemID)
        for each in scene.objects:
            if each.name == nameOfMiniballs:
                miniballObject = each
                break

        if miniballObject is not None:
            scene.objects.remove(miniballObject)
        if miniballObject and showType == UNLOAD_MINIBALLS:
            return
        ballpark = sm.StartService('michelle').GetBallpark()
        ball = ballpark.GetBall(itemID)
        typeID = ballpark.GetInvItem(itemID).typeID
        if showType == SHOW_RUNTIME_MINIBALL_DATA:
            graphicObject = CreateMiniballObject(nameOfMiniballs, ball.miniBalls)
            graphicObject.translationCurve = ball
            graphicObject.rotationCurve = ball
            scene.objects.append(graphicObject)
        elif showType == SHOW_DESTINY_BALL:
            graphicObject = CreateRadiusObject(nameOfMiniballs, ball.radius)
            graphicObject.translationCurve = ball
            scene.objects.append(graphicObject)
        elif showType == SHOW_BOUNDING_SPHERE:
            graphicObject = CreateRadiusObject(nameOfMiniballs, ball.model.GetBoundingSphereRadius())
            pos = ball.model.GetBoundingSphereCenter()
            graphicObject.translation = (pos[0], pos[1], pos[2])
            graphicObject.translationCurve = ball
            scene.objects.append(graphicObject)

    def ShowBallPartition(self, itemID):
        ball = sm.StartService('michelle').GetBallpark().GetBall(itemID)
        ball.showBoxes = 1

    def AnchorObject(self, itemID, anchorFlag):
        dogmaLM = self.godma.GetDogmaLM()
        if dogmaLM:
            typeID = sm.StartService('michelle').GetItem(itemID).typeID
            anchoringDelay = self.godma.GetType(typeID).anchoringDelay
            if anchorFlag:
                dogmaLM.Activate(itemID, const.effectAnchorDrop)
                eve.Message('AnchoringObject', {'delay': anchoringDelay / 1000.0})
            else:
                dogmaLM.Activate(itemID, const.effectAnchorLift)
                eve.Message('UnanchoringObject', {'delay': anchoringDelay / 1000.0})

    def AnchorStructure(self, itemID, anchorFlag):
        dogmaLM = self.godma.GetDogmaLM()
        if dogmaLM:
            item = sm.StartService('michelle').GetItem(itemID)
            typeID = item.typeID
            if anchorFlag:
                anchoringDelay = self.godma.GetType(typeID).anchoringDelay
                ball = sm.StartService('michelle').GetBallpark().GetBall(itemID)
                sm.StartService('pwn').Anchor(itemID, (ball.x, ball.y, ball.z))
                eve.Message('AnchoringObject', {'delay': anchoringDelay / 1000.0})
            else:
                orphaned = self.pwn.StructureIsOrphan(itemID)
                item = sm.StartService('michelle').GetItem(itemID)
                if orphaned:
                    msgName = 'ConfirmOrphanStructureUnanchor'
                elif item.groupID == const.groupInfrastructureHub:
                    msgName = 'ConfirmInfrastructureHubUnanchor'
                elif item.groupID == const.groupAssemblyArray:
                    msgName = 'ConfirmAssemblyArrayUnanchor'
                else:
                    msgName = 'ConfirmStructureUnanchor'
                if eve.Message(msgName, {'item': item.typeID}, uiconst.YESNO, suppress=uiconst.ID_YES) != uiconst.ID_YES:
                    return
                unanchoringDelay = self.godma.GetType(typeID).unanchoringDelay
                dogmaLM.Activate(itemID, const.effectAnchorLiftForStructures)
                eve.Message('UnanchoringObject', {'delay': unanchoringDelay / 1000.0})

    def ToggleObjectOnline(self, itemID, onlineFlag):
        dogmaLM = self.godma.GetDogmaLM()
        if dogmaLM:
            item = sm.StartService('michelle').GetItem(itemID)
            if onlineFlag:
                if item.groupID in (const.groupSovereigntyClaimMarkers,):
                    if eve.Message('ConfirmSovStructureOnline', {}, uiconst.YESNO, suppress=uiconst.ID_YES) != uiconst.ID_YES:
                        return
                dogmaLM.Activate(itemID, const.effectOnlineForStructures)
            else:
                if item.groupID == const.groupControlTower:
                    msgName = 'ConfirmTowerOffline'
                elif item.groupID == const.groupSovereigntyClaimMarkers:
                    msgName = 'ConfirmSovereigntyClaimMarkerOffline'
                else:
                    msgName = 'ConfirmStructureOffline'
                if eve.Message(msgName, {'item': (TYPEID, item.typeID)}, uiconst.YESNO, suppress=uiconst.ID_YES) != uiconst.ID_YES:
                    return
                dogmaLM.Deactivate(itemID, const.effectOnlineForStructures)

    def DeclareWar(self):
        dlg = form.CorporationOrAlliancePickerDailog.Open(warableEntitysOnly=True)
        dlg.ShowModal()
        againstID = dlg.ownerID
        if not againstID:
            return
        self.DeclareWarAgainst(againstID)

    def DeclareWarAgainst(self, againstID):
        cost = sm.GetService('war').GetCostOfWarAgainst(againstID)
        allianceLabel = localization.GetByLabel('UI/Common/Alliance')
        svc = sm.GetService('alliance') if session.allianceid else sm.GetService('corp')
        messageName = 'WarDeclareConfirmAlliance' if session.allianceid is not None else 'WarDeclareConfirmCorporation'
        if eve.Message(messageName, {'against': cfg.eveowners.Get(againstID).ownerName,
         'price': util.FmtISK(cost, showFractionsAlways=0)}, uiconst.YESNO) == uiconst.ID_YES:
            svc.DeclareWarAgainst(againstID, cost)

    def TransferOwnership(self, itemID):
        members = sm.GetService('alliance').GetMembers()
        twit = sm.GetService('michelle')
        remotePark = twit.GetRemotePark()
        localPark = twit.GetBallpark()
        if itemID not in localPark.slimItems:
            return
        oldOwnerID = localPark.slimItems[itemID].ownerID
        owners = {member.corporationID for member in members.itervalues()}
        if len(owners):
            cfg.eveowners.Prime(owners)
        tmplist = []
        for member in members.itervalues():
            if oldOwnerID != member.corporationID:
                tmplist.append((cfg.eveowners.Get(member.corporationID).ownerName, member.corporationID))

        ret = uix.ListWnd(tmplist, 'generic', localization.GetByLabel('UI/Corporations/Common/SelectCorporation'), None, 1)
        if ret is not None and len(ret):
            newOwnerID = ret[1]
            if remotePark is not None:
                remotePark.CmdChangeStructureOwner(itemID, oldOwnerID, newOwnerID)

    def TransferCorporationOwnership(self, itemID):
        michelle = sm.GetService('michelle')
        remotePark = michelle.GetRemotePark()
        localPark = michelle.GetBallpark()
        if itemID not in localPark.slimItems or remotePark is None:
            return
        oldOwnerID = localPark.slimItems[itemID].ownerID
        name = uiutil.NamePopup(localization.GetByLabel('UI/Corporations/Common/TransferOwnership'), localization.GetByLabel('UI/Corporations/Common/TransferOwnershipLabel'))
        if name is None:
            return
        owner = uix.SearchOwners(searchStr=name, groupIDs=[const.groupCorporation], hideNPC=True, notifyOneMatch=True, searchWndName='AddToBlockSearch')
        if owner is None or owner == oldOwnerID:
            return
        remotePark.CmdChangeStructureOwner(itemID, oldOwnerID, owner)

    def ConfigureObject(self, itemID):
        self.pwn.ConfigureSentryGun(itemID)

    def AskNewContainerPassword(self, id_, desc, which = 1, setnew = '', setold = ''):
        container = self.invCache.GetInventoryFromId(id_)
        format = []
        if container.HasExistingPasswordSet(which):
            format.append({'type': 'edit',
             'setvalue': setold or '',
             'labelwidth': 48,
             'label': localization.GetByLabel('UI/Menusvc/OldPassword'),
             'key': 'oldpassword',
             'maxlength': 16,
             'setfocus': 1,
             'passwordChar': '*'})
        format.append({'type': 'edit',
         'setvalue': setnew or '',
         'labelwidth': 48,
         'label': localization.GetByLabel('UI/Menusvc/NewPassword'),
         'key': 'newpassword',
         'maxlength': 16,
         'passwordChar': '*'})
        format.append({'type': 'edit',
         'setvalue': '',
         'labelwidth': 48,
         'label': localization.GetByLabel('UI/Menusvc/ConfirmPassword'),
         'key': 'conpassword',
         'maxlength': 16,
         'passwordChar': '*'})
        retval = uix.HybridWnd(format, desc, icon=uiconst.QUESTION, minW=300, minH=75)
        if retval:
            old = retval['oldpassword'] or None if 'oldpassword' in retval else None
            new = retval['newpassword'] or None
            con = retval['conpassword'] or None
            if new is None or len(new) < 3:
                eve.Message('MinThreeLetters')
                return self.AskNewContainerPassword(id_, desc, which, new, old)
            if new != con:
                eve.Message('NewPasswordMismatch')
                return self.AskNewContainerPassword(id_, desc, which, new, old)
            container.SetPassword(which, old, new)

    def LockDownBlueprint(self, invItem):
        dlg = form.VoteWizardDialog.Open()
        stationID = self.invCache.GetStationIDOfItem(invItem)
        blueprints = self.invCache.GetInventory(const.containerGlobal).ListStationBlueprintItems(invItem.locationID, stationID, True)
        description = None
        for blueprint in blueprints:
            if blueprint.itemID != invItem.itemID:
                continue
            description = localization.GetByLabel('UI/Corporations/Votes/ProposeLockdownDescription', blueprintLocation=stationID, efficiencyLevel=blueprint.materialLevel, productivityLevel=blueprint.productivityLevel)
            break

        dlg.voteType = const.voteItemLockdown
        dlg.voteTitle = localization.GetByLabel('UI/Corporations/Votes/LockdownItem', blueprint=invItem.typeID)
        dlg.voteDescription = description or dlg.voteTitle
        dlg.voteDays = 1
        dlg.itemID = invItem.itemID
        dlg.typeID = invItem.typeID
        dlg.flagInput = invItem.flagID
        dlg.locationID = stationID
        dlg.GoToStep(len(dlg.steps))
        dlg.ShowModal()

    def UnlockBlueprint(self, invItem):
        voteCases = sm.GetService('corp').GetVoteCasesByCorporation(session.corpid, 2)
        voteCaseIDByItemToUnlockID = {}
        if voteCases and len(voteCases):
            for voteCase in voteCases.itervalues():
                if voteCase.voteType in [const.voteItemUnlock] and voteCase.endDateTime > blue.os.GetWallclockTime() - DAY:
                    options = sm.GetService('corp').GetVoteCaseOptions(voteCase.voteCaseID, voteCase.corporationID)
                    if len(options):
                        for option in options.itervalues():
                            if option.parameter:
                                voteCaseIDByItemToUnlockID[option.parameter] = voteCase.voteCaseID

        if voteCaseIDByItemToUnlockID.has_key(invItem.itemID):
            raise UserError('CustomInfo', {'info': localization.GetByLabel('UI/Corporations/Common/UnlockCorpVoteAlreadyExists')})
        sanctionedActionsInEffect = sm.GetService('corp').GetSanctionedActionsByCorporation(session.corpid, 1)
        sanctionedActionsByLockedItemID = dbutil.CIndexedRowset(sanctionedActionsInEffect.header, 'parameter')
        for sanctionedActionInEffect in sanctionedActionsInEffect.itervalues():
            if sanctionedActionInEffect.voteType in [const.voteItemLockdown] and sanctionedActionInEffect.parameter and sanctionedActionInEffect.inEffect:
                sanctionedActionsByLockedItemID[sanctionedActionInEffect.parameter] = sanctionedActionInEffect

        if invItem.itemID not in sanctionedActionsByLockedItemID:
            raise UserError('CustomInfo', {'info': localization.GetByLabel('UI/Corporations/Common/CannotUnlockNoLockdownSanctionedAction')})
        dlg = form.VoteWizardDialog.Open()
        stationID = self.invCache.GetStationIDOfItem(invItem)
        blueprints = self.invCache.GetInventory(const.containerGlobal).ListStationBlueprintItems(invItem.locationID, stationID, True)
        description = None
        for blueprint in blueprints:
            if blueprint.itemID != invItem.itemID:
                continue
            description = localization.GetByLabel('UI/Corporations/Votes/ProposeLockdownDescription', blueprintLocation=stationID, efficiencyLevel=blueprint.materialLevel, productivityLevel=blueprint.productivityLevel)
            break

        dlg.voteType = const.voteItemUnlock
        dlg.voteTitle = localization.GetByLabel('UI/Corporations/Votes/UnlockItem', blueprint=invItem.typeID)
        dlg.voteDescription = description or dlg.voteTitle
        dlg.voteDays = 1
        dlg.itemID = invItem.itemID
        dlg.typeID = invItem.typeID
        dlg.flagInput = invItem.flagID
        dlg.locationID = stationID
        dlg.GoToStep(len(dlg.steps))
        dlg.ShowModal()

    def ALSCLock(self, invItems):
        if len(invItems) < 1:
            return
        container = self.invCache.GetInventoryFromId(invItems[0].locationID)
        container.ALSCLockItems([ i.itemID for i in invItems ])

    def ALSCUnlock(self, invItems):
        if len(invItems) < 1:
            return
        container = self.invCache.GetInventoryFromId(invItems[0].locationID)
        container.ALSCUnlockItems([ i.itemID for i in invItems ])

    def ViewAuditLogForALSC(self, itemID):
        form.AuditLogSecureContainerLogViewer.CloseIfOpen()
        form.AuditLogSecureContainerLogViewer.Open(itemID=itemID)

    def ConfigureALSC(self, itemID):
        container = self.invCache.GetInventoryFromId(itemID)
        config = container.ALSCConfigGet()
        defaultLock = bool(config & const.ALSCLockAddedItems)
        containerOwnerID = container.GetItem().ownerID
        if util.IsCorporation(containerOwnerID):
            if charsession.corprole & const.corpRoleEquipmentConfig == 0:
                raise UserError('PermissionDeniedNeedEquipRole', {'corp': (OWNERID, containerOwnerID)})
        else:
            userDefaultLock = settings.user.ui.Get('defaultContainerLock_%s' % itemID, None)
            if userDefaultLock:
                defaultLock = True if userDefaultLock == const.flagLocked else False
        configSettings = [(const.ALSCPasswordNeededToOpen, localization.GetByLabel('UI/Menusvc/ContainerPasswordForOpening')),
         (const.ALSCPasswordNeededToLock, localization.GetByLabel('UI/Menusvc/ContainerPasswordForLocking')),
         (const.ALSCPasswordNeededToUnlock, localization.GetByLabel('UI/Menusvc/ContainerPasswordForUnlocking')),
         (const.ALSCPasswordNeededToViewAuditLog, localization.GetByLabel('UI/Menusvc/ContainerPasswordForViewingLog'))]
        format = []
        format.append({'type': 'header',
         'text': localization.GetByLabel('UI/Menusvc/ContainerDefaultLocked'),
         'frame': 1})
        format.append({'type': 'checkbox',
         'setvalue': defaultLock,
         'key': const.ALSCLockAddedItems,
         'label': '',
         'text': localization.GetByLabel('UI/Menusvc/ALSCLocked'),
         'frame': 1})
        format.append({'type': 'btline'})
        format.append({'type': 'push'})
        format.append({'type': 'header',
         'text': localization.GetByLabel('UI/Menusvc/ContainerPasswordRequiredFor'),
         'frame': 1})
        for value, settingName in configSettings:
            format.append({'type': 'checkbox',
             'setvalue': value & config == value,
             'key': value,
             'label': '',
             'text': settingName,
             'frame': 1})

        format.append({'type': 'btline'})
        format.append({'type': 'push'})
        retval = uix.HybridWnd(format, localization.GetByLabel('UI/Menusvc/ContainerConfigurationHeader'), 1, None, uiconst.OKCANCEL, unresizeAble=1, minW=300)
        if retval is None:
            return
        settings.user.ui.Delete('defaultContainerLock_%s' % itemID)
        newconfig = 0
        for k, v in retval.iteritems():
            newconfig |= k * v

        if config != newconfig:
            container.ALSCConfigSet(newconfig)

    def RetrievePasswordALSC(self, itemID):
        container = self.invCache.GetInventoryFromId(itemID)
        format = []
        format.append({'type': 'header',
         'text': localization.GetByLabel('UI/Menusvc/RetrieveWhichPassword'),
         'frame': 1})
        format.append({'type': 'push'})
        format.append({'type': 'btline'})
        configSettings = [[const.SCCPasswordTypeGeneral, localization.GetByLabel('UI/Menusvc/GeneralPassword')], [const.SCCPasswordTypeConfig, localization.GetByLabel('UI/Menusvc/RetrievePasswordConfiguration')]]
        for value, settingName in configSettings:
            format.append({'type': 'checkbox',
             'setvalue': value & const.SCCPasswordTypeGeneral == value,
             'key': value,
             'label': '',
             'text': settingName,
             'frame': 1,
             'group': 'which_password'})

        format.append({'type': 'btline'})
        retval = uix.HybridWnd(format, localization.GetByLabel('UI/Commands/RetrievePassword'), 1, None, uiconst.OKCANCEL)
        if retval is None:
            return
        container.RetrievePassword(retval['which_password'])

    def GetFleetMemberMenu(self, func, args):
        menuSize = 20
        fleet = []
        for member in sm.GetService('fleet').GetMembers().itervalues():
            if member.charID == session.charid:
                continue
            data = cfg.eveowners.Get(member.charID)
            fleet.append((data.name.lower(), (member.charID, data.name)))

        fleet = uiutil.SortListOfTuples(fleet)
        all = []
        while len(fleet) > menuSize:
            all.append(fleet[:menuSize])
            fleet = fleet[menuSize:]

        if fleet:
            all.append(fleet)
        if not all:
            return []
        elif len(all) == 1:
            return self.GetSubFleetMemberMenu(all[0], func, args)
        else:
            return [ ('%c ... %c' % (sub[0][1][0], sub[-1][1][0]), ('isDynamic', self.GetSubFleetMemberMenu, (sub, func, args))) for sub in all ]

    def GetSubFleetMemberMenu(self, memberIDs, func, args):
        return [ [name, func, (charID, args)] for charID, name in memberIDs ]

    def BridgeToMember(self, charID):
        beaconStuff = sm.GetService('fleet').GetActiveBeaconForChar(charID)
        if beaconStuff is None:
            return
        self.BridgeToBeacon(charID, beaconStuff)

    def BridgeToBeaconAlliance(self, solarSystemID, beaconID):
        bp = sm.StartService('michelle').GetRemotePark()
        if bp is None:
            return
        bp.CmdBridgeToStructure(beaconID, solarSystemID)

    def BridgeToBeacon(self, charID, beacon):
        solarsystemID, beaconID = beacon
        bp = sm.StartService('michelle').GetRemotePark()
        if bp is None:
            return
        bp.CmdBridgeToMember(charID, beaconID, solarsystemID)

    def JumpThroughFleet(self, otherCharID, otherShipID):
        bp = sm.StartService('michelle').GetRemotePark()
        if bp is None:
            return
        bridge = sm.GetService('fleet').GetActiveBridgeForShip(otherShipID)
        if bridge is None:
            return
        solarsystemID, beaconID = bridge
        self.LogNotice('Jump Through Fleet', otherCharID, otherShipID, beaconID, solarsystemID)
        sm.StartService('sessionMgr').PerformSessionChange('jump', bp.CmdJumpThroughFleet, otherCharID, otherShipID, beaconID, solarsystemID)

    def JumpThroughAlliance(self, otherShipID):
        bp = sm.StartService('michelle').GetRemotePark()
        if bp is None:
            return
        bridge = sm.StartService('pwn').GetActiveBridgeForShip(otherShipID)
        if bridge is None:
            return
        solarsystemID, beaconID = bridge
        self.LogNotice('Jump Through Alliance', otherShipID, beaconID, solarsystemID)
        sm.StartService('sessionMgr').PerformSessionChange('jump', bp.CmdJumpThroughAlliance, otherShipID, beaconID, solarsystemID)

    def JumpToMember(self, charid):
        beaconStuff = sm.GetService('fleet').GetActiveBeaconForChar(charid)
        if beaconStuff is None:
            return
        self.JumpToBeaconFleet(charid, beaconStuff)

    def JumpToBeaconFleet(self, charid, beacon):
        solarsystemID, beaconID = beacon
        bp = sm.StartService('michelle').GetRemotePark()
        if bp is None:
            return
        self.LogNotice('Jump To Beacon Fleet', charid, beaconID, solarsystemID)
        sm.StartService('sessionMgr').PerformSessionChange('jump', bp.CmdBeaconJumpFleet, charid, beaconID, solarsystemID)

    def JumpToBeaconAlliance(self, solarSystemID, beaconID):
        bp = sm.StartService('michelle').GetRemotePark()
        if bp is None:
            return
        self.LogNotice('Jump To Beacon Alliance', beaconID, solarSystemID)
        sm.StartService('sessionMgr').PerformSessionChange('jump', bp.CmdBeaconJumpAlliance, beaconID, solarSystemID)

    def ActivateGridSmartBomb(self, charid, effect):
        beaconStuff = sm.GetService('fleet').GetActiveBeaconForChar(charid)
        if beaconStuff is None:
            return
        solarsystemID, beaconID = beaconStuff
        bp = sm.StartService('michelle').GetRemotePark()
        if bp is None:
            return
        effect.Activate(beaconID, False)

    def LeaveFleet(self):
        sm.GetService('fleet').LeaveFleet()

    def MakeLeader(self, charid):
        sm.GetService('fleet').MakeLeader(charid)

    def KickMember(self, charid):
        sm.GetService('fleet').KickMember(charid)

    def DisbandFleet(self):
        sm.GetService('fleet').DisbandFleet()

    def InviteToFleet(self, charIDs, ignoreWars = 0):
        if type(charIDs) != list:
            charIDs = [charIDs]
        charErrors = {}
        for charID in charIDs:
            try:
                sm.GetService('fleet').Invite(charID, None, None, None)
            except UserError as ue:
                charErrors[charID] = ue
                sys.exc_clear()

        if len(charErrors) == 1:
            raise charErrors.values()[0]
        elif len(charErrors) > 1:
            charNames = None
            for charID in charErrors.iterkeys():
                if charNames is not None:
                    charNames += ', %s' % cfg.eveowners.Get(charID).name
                else:
                    charNames = cfg.eveowners.Get(charID).name

            raise UserError('FleetInviteMultipleErrors', {'namelist': charNames})

    def Regroup(self, *args):
        bp = sm.StartService('michelle').GetRemotePark()
        if bp is not None:
            bp.CmdFleetRegroup()

    def WarpFleet(self, id, warpRange = None):
        bp = sm.StartService('michelle').GetRemotePark()
        if bp is not None:
            if not sm.GetService('machoNet').GetGlobalConfig().get('newAutoNavigationKillSwitch', False):
                sm.GetService('autoPilot').CancelSystemNavigation()
            bp.CmdWarpToStuff('item', id, minRange=warpRange, fleet=True)
            sm.StartService('space').WarpDestination(id, None, None)

    def WarpToMember(self, charID, warpRange = None):
        bp = sm.StartService('michelle').GetRemotePark()
        if bp is not None:
            if not sm.GetService('machoNet').GetGlobalConfig().get('newAutoNavigationKillSwitch', False):
                sm.GetService('autoPilot').CancelSystemNavigation()
            bp.CmdWarpToStuff('char', charID, minRange=warpRange)
            sm.StartService('space').WarpDestination(None, None, charID)

    def WarpFleetToMember(self, charID, warpRange = None):
        bp = sm.StartService('michelle').GetRemotePark()
        if bp is not None:
            if not sm.GetService('machoNet').GetGlobalConfig().get('newAutoNavigationKillSwitch', False):
                sm.GetService('autoPilot').CancelSystemNavigation()
            bp.CmdWarpToStuff('char', charID, minRange=warpRange, fleet=True)
            sm.StartService('space').WarpDestination(None, None, charID)

    def TacticalItemClicked(self, itemID):
        isTargeted = sm.GetService('target').IsTarget(itemID)
        if isTargeted:
            sm.GetService('state').SetState(itemID, state.activeTarget, 1)
        uicore.cmd.ExecuteCombatCommand(itemID, uiconst.UI_CLICK)

    def KeepAtRange(self, id, range = None):
        if id == session.shipid:
            return
        if range is None:
            range = self.GetDefaultDist('KeepAtRange', id, minDist=50)
        bp = sm.StartService('michelle').GetRemotePark()
        if bp is not None and range is not None:
            name = sm.GetService('space').GetWarpDestinationName(id)
            eve.Message('CustomNotify', {'notify': localization.GetByLabel('UI/Inflight/KeepingAtRange', name=name, range=int(range))})
            bp.CmdFollowBall(id, range)
            if not sm.GetService('machoNet').GetGlobalConfig().get('newAutoNavigationKillSwitch', False):
                sm.GetService('autoPilot').CancelSystemNavigation()

    def Approach(self, itemID, approachRange = 50, cancelAutoNavigation = True):
        if itemID == session.shipid:
            return
        autoPilot = sm.GetService('autoPilot')
        if not sm.GetService('machoNet').GetGlobalConfig().get('newAutoNavigationKillSwitch', False):
            if cancelAutoNavigation:
                autoPilot.CancelSystemNavigation()
        else:
            autoPilot.AbortWarpAndTryCommand()
            autoPilot.AbortApproachAndTryCommand(itemID)
        bp = self.michelle.GetRemotePark()
        if bp is not None:
            shipBall = self.michelle.GetBall(session.shipid)
            if shipBall is not None:
                if shipBall.mode != destiny.DSTBALL_FOLLOW or shipBall.followId != itemID or shipBall.followRange != approachRange:
                    name = sm.GetService('space').GetWarpDestinationName(itemID)
                    eve.Message('CustomNotify', {'notify': localization.GetByLabel('UI/Inflight/ApproachingItem', name=name)})
                    bp.CmdFollowBall(itemID, approachRange)

    def AlignTo(self, id):
        if id == session.shipid:
            return
        bp = sm.StartService('michelle').GetRemotePark()
        if bp is not None:
            name = sm.GetService('space').GetWarpDestinationName(id)
            eve.Message('CustomNotify', {'notify': localization.GetByLabel('UI/Inflight/AligningTo', name=name)})
            bp.CmdAlignTo(id)
            if not sm.GetService('machoNet').GetGlobalConfig().get('newAutoNavigationKillSwitch', False):
                sm.GetService('autoPilot').CancelSystemNavigation()

    def AlignToBookmark(self, id):
        bp = sm.StartService('michelle').GetRemotePark()
        if bp is not None:
            bp.CmdAlignTo(bookmarkID=id)
            if not sm.GetService('machoNet').GetGlobalConfig().get('newAutoNavigationKillSwitch', False):
                sm.GetService('autoPilot').CancelSystemNavigation()

    def Orbit(self, id, range = None):
        if id == session.shipid:
            return
        if range is None:
            range = self.GetDefaultDist('Orbit')
        bp = sm.StartService('michelle').GetRemotePark()
        if bp is not None and range is not None:
            name = sm.GetService('space').GetWarpDestinationName(id)
            range = float(range) if range < 10.0 else int(range)
            eve.Message('CustomNotify', {'notify': localization.GetByLabel('UI/Inflight/Orbiting', name=name, range=range)})
            bp.CmdOrbit(id, range)
            if not sm.GetService('machoNet').GetGlobalConfig().get('newAutoNavigationKillSwitch', False):
                sm.GetService('autoPilot').CancelSystemNavigation()

    def TagItem(self, itemID, tag):
        bp = sm.StartService('michelle').GetRemotePark()
        if bp:
            bp.CmdFleetTagTarget(itemID, tag)

    def LockTarget(self, id):
        sm.StartService('target').TryLockTarget(id)

    def UnlockTarget(self, id):
        sm.StartService('target').UnlockTarget(id)

    def ShowInfo(self, typeID, itemID = None, new = 0, rec = None, parentID = None, *args):
        sm.StartService('info').ShowInfo(typeID, itemID, new, rec, parentID)

    def ShowInfoForItem(self, itemID):
        bp = sm.StartService('michelle').GetBallpark()
        if bp:
            itemTypeID = bp.GetInvItem(itemID).typeID
            sm.GetService('info').ShowInfo(itemTypeID, itemID)

    def DockOrJumpOrActivateGate(self, itemID):
        bp = sm.StartService('michelle').GetBallpark()
        menuSvc = sm.GetService('menu')
        if bp:
            groupID = bp.GetInvItem(itemID).groupID
            if groupID == const.groupStation:
                menuSvc.Dock(itemID)
            if groupID == const.groupStargate:
                bp = sm.StartService('michelle').GetBallpark()
                slimItem = bp.slimItems.get(itemID)
                if slimItem:
                    jump = slimItem.jumps[0]
                    if not jump:
                        return
                    menuSvc.StargateJump(itemID, jump.toCelestialID, jump.locationID)
            elif groupID == const.groupWarpGate:
                menuSvc.ActivateAccelerationGate(itemID)

    def PreviewType(self, typeID):
        sm.GetService('preview').PreviewType(typeID)

    def GetDefaultDist(self, key, itemID = None, minDist = 500, maxDist = 1000000):
        drange = sm.GetService('menu').GetDefaultActionDistance(key)
        if drange is None:
            dist = ''
            if itemID:
                bp = sm.StartService('michelle').GetBallpark()
                if not bp:
                    return
                ball = bp.GetBall(itemID)
                if not ball:
                    return
                dist = long(max(minDist, min(maxDist, ball.surfaceDist)))
            fromDist = util.FmtAmt(minDist)
            toDist = util.FmtAmt(maxDist)
            if key == 'KeepAtRange':
                hint = localization.GetByLabel('UI/Inflight/SetDefaultKeepAtRangeDistanceHint', fromDist=fromDist, toDist=toDist)
                caption = localization.GetByLabel('UI/Inflight/SetDefaultKeepAtRangeDistance')
            elif key == 'Orbit':
                hint = localization.GetByLabel('UI/Inflight/SetDefaultOrbitDistanceHint', fromDist=fromDist, toDist=toDist)
                caption = localization.GetByLabel('UI/Inflight/SetDefaultOrbitDistance')
            elif key == 'WarpTo':
                hint = localization.GetByLabel('UI/Inflight/SetDefaultWarpWithinDistanceHint', fromDist=fromDist, toDist=toDist)
                caption = localization.GetByLabel('UI/Inflight/SetDefaultWarpWithinDistance')
            else:
                hint = ''
                caption = ''
            r = uix.QtyPopup(maxvalue=maxDist, minvalue=minDist, setvalue=dist, hint=hint, caption=caption, label=None, digits=0)
            if r:
                newRange = max(minDist, min(maxDist, r['qty']))
                util.UpdateRangeSetting(key, newRange)
            else:
                return
        return drange

    def ApproachLocation(self, bookmark):
        bp = sm.StartService('michelle').GetRemotePark()
        if bp:
            if getattr(bookmark, 'agentID', 0) and hasattr(bookmark, 'locationNumber'):
                referringAgentID = getattr(bookmark, 'referringAgentID', None)
                sm.StartService('agents').GetAgentMoniker(bookmark.agentID).GotoLocation(bookmark.locationType, bookmark.locationNumber, referringAgentID)
            else:
                bp.CmdGotoBookmark(bookmark.bookmarkID)

    def WarpToBookmark(self, bookmark, warpRange = 20000.0, fleet = False):
        bp = sm.StartService('michelle').GetRemotePark()
        if bp:
            if getattr(bookmark, 'agentID', 0) and hasattr(bookmark, 'locationNumber'):
                referringAgentID = getattr(bookmark, 'referringAgentID', None)
                sm.StartService('agents').GetAgentMoniker(bookmark.agentID).WarpToLocation(bookmark.locationType, bookmark.locationNumber, warpRange, fleet, referringAgentID)
            else:
                if not sm.GetService('machoNet').GetGlobalConfig().get('newAutoNavigationKillSwitch', False):
                    sm.GetService('autoPilot').CancelSystemNavigation()
                bp.CmdWarpToStuff('bookmark', bookmark.bookmarkID, minRange=warpRange, fleet=fleet)
                sm.StartService('space').WarpDestination(None, bookmark.bookmarkID, None)

    def WarpFleetToBookmark(self, bookmark, warpRange = 20000.0, fleet = True):
        bp = sm.StartService('michelle').GetRemotePark()
        if bp:
            if getattr(bookmark, 'agentID', 0) and hasattr(bookmark, 'locationNumber'):
                referringAgentID = getattr(bookmark, 'referringAgentID', None)
                sm.StartService('agents').GetAgentMoniker(bookmark.agentID).WarpToLocation(bookmark.locationType, bookmark.locationNumber, warpRange, fleet, referringAgentID)
            else:
                if not sm.GetService('machoNet').GetGlobalConfig().get('newAutoNavigationKillSwitch', False):
                    sm.GetService('autoPilot').CancelSystemNavigation()
                bp.CmdWarpToStuff('bookmark', bookmark.bookmarkID, minRange=warpRange, fleet=fleet)

    def WarpToItem(self, id, warpRange = None, cancelAutoNavigation = True):
        if id == session.shipid:
            return
        if warpRange is None:
            warprange = sm.GetService('menu').GetDefaultActionDistance('WarpTo')
        else:
            warprange = warpRange
        bp = sm.StartService('michelle').GetRemotePark()
        if bp is not None and sm.StartService('space').CanWarp(id):
            if not sm.GetService('machoNet').GetGlobalConfig().get('newAutoNavigationKillSwitch', False):
                if cancelAutoNavigation:
                    sm.GetService('autoPilot').CancelSystemNavigation()
            else:
                sm.GetService('autoPilot').AbortWarpAndTryCommand(id)
                sm.GetService('autoPilot').AbortApproachAndTryCommand()
            bp.CmdWarpToStuff('item', id, minRange=warprange)
            sm.StartService('space').WarpDestination(id, None, None)

    def WarpToDistrict(self, districtID, warpRange = None, cancelAutoNavigation = True):
        if warpRange is None:
            warprange = sm.GetService('menu').GetDefaultActionDistance('WarpTo')
        else:
            warprange = warpRange
        bp = sm.StartService('michelle').GetRemotePark()
        if bp is not None and sm.StartService('space').CanWarp(id):
            if not sm.GetService('machoNet').GetGlobalConfig().get('newAutoNavigationKillSwitch', False):
                if cancelAutoNavigation:
                    sm.GetService('autoPilot').CancelSystemNavigation()
            else:
                sm.GetService('autoPilot').AbortWarpAndTryCommand(id)
                sm.GetService('autoPilot').AbortApproachAndTryCommand()
            bp.CmdWarpToStuff('district', districtID, minRange=warprange)

    def StoreVessel(self, destID, shipID):
        if shipID != session.shipid:
            return
        shipItem = self.godma.GetStateManager().GetItem(shipID)
        if shipItem.groupID == const.groupCapsule:
            return
        destItem = uix.GetBallparkRecord(destID)
        if destItem.categoryID == const.categoryShip:
            msgName = 'ConfirmStoreVesselInShip'
        else:
            msgName = 'ConfirmStoreVesselInStructure'
        if eve.Message(msgName, {'dest': destItem.typeID}, uiconst.YESNO, suppress=uiconst.ID_YES) != uiconst.ID_YES:
            return
        if shipID != session.shipid:
            return
        shipItem = self.godma.GetStateManager().GetItem(shipID)
        if shipItem.groupID == const.groupCapsule:
            return
        ship = sm.StartService('gameui').GetShipAccess()
        if ship:
            sm.ScatterEvent('OnBeforeActiveShipChanged', shipID, util.GetActiveShip())
            sm.StartService('sessionMgr').PerformSessionChange('storeVessel', ship.StoreVessel, destID)

    def OpenCorpHangarArray(self, itemID, name):
        form.Inventory.OpenOrShow(invID=('POSCorpHangars', itemID))

    def OpenPOSSilo(self, itemID, name):
        form.Inventory.OpenOrShow(invID=('POSSilo', itemID))

    def OpenPOSMobileReactor(self, itemID, name):
        form.Inventory.OpenOrShow(invID=('POSMobileReactor', itemID))

    def OpenPOSShipMaintenanceArray(self, itemID, name):
        form.Inventory.OpenOrShow(invID=('POSShipMaintenanceArray', itemID))

    def OpenPOSStructureChargesStorage(self, itemID, name):
        form.Inventory.OpenOrShow(invID=('POSStructureChargesStorage', itemID))

    def OpenPOSFuelBay(self, itemID, name):
        form.Inventory.OpenOrShow(invID=('POSFuelBay', itemID))

    def OpenPOSJumpBridge(self, itemID, name):
        form.Inventory.OpenOrShow(invID=('POSJumpBridge', itemID))

    def OpenPOSRefinery(self, itemID, name):
        form.Inventory.OpenOrShow(invID=('POSRefinery', itemID))

    def OpenPOSStructureCharges(self, itemID, name, showCapacity = 0):
        form.Inventory.OpenOrShow(invID=('POSStructureCharges', itemID))

    def OpenStrontiumBay(self, itemID, name):
        form.Inventory.OpenOrShow(invID=('POSStrontiumBay', itemID))

    def ManageControlTower(self, itemID):
        uthread.new(self._ManageControlTower, itemID)

    def _ManageControlTower(self, itemID):
        uicore.cmd.OpenMoonMining(itemID)

    def OpenConstructionPlatform(self, itemID, name):
        invID = ('POSConstructionPlatform', itemID)
        form.Inventory.OpenOrShow(invID=invID)

    def OpenFuelBay(self, itemID):
        self._OpenShipBay(invID=('ShipFuelBay', itemID))

    def OpenOreHold(self, itemID):
        self._OpenShipBay(invID=('ShipOreHold', itemID))

    def OpenGasHold(self, itemID):
        self._OpenShipBay(invID=('ShipGasHold', itemID))

    def OpenMineralHold(self, itemID):
        self._OpenShipBay(invID=('ShipMineralHold', itemID))

    def OpenSalvageHold(self, itemID):
        self._OpenShipBay(invID=('ShipSalvageHold', itemID))

    def OpenShipHold(self, itemID):
        self._OpenShipBay(invID=('ShipShipHold', itemID))

    def OpenSmallShipHold(self, itemID):
        self._OpenShipBay(invID=('ShipSmallShipHold', itemID))

    def OpenMediumShipHold(self, itemID):
        self._OpenShipBay(invID=('ShipMediumShipHold', itemID))

    def OpenLargeShipHold(self, itemID):
        self._OpenShipBay(invID=('ShipLargeShipHold', itemID))

    def OpenIndustrialShipHold(self, itemID):
        self._OpenShipBay(invID=('ShipIndustrialShipHold', itemID))

    def OpenAmmoHold(self, itemID):
        self._OpenShipBay(invID=('ShipAmmoHold', itemID))

    def OpenCommandCenterHold(self, itemID):
        self._OpenShipBay(invID=('ShipCommandCenterHold', itemID))

    def OpenPlanetaryCommoditiesHold(self, itemID):
        self._OpenShipBay(invID=('ShipPlanetaryCommoditiesHold', itemID))

    def OpenQuafeHold(self, itemID):
        self._OpenShipBay(invID=('ShipQuafeHold', itemID))

    def _OpenShipBay(self, invID):
        form.Inventory.OpenOrShow(invID=invID, openFromWnd=uicore.registry.GetActive())

    def BuildConstructionPlatform(self, id):
        if getattr(self, '_buildingPlatform', 0):
            return
        self._buildingPlatform = 1
        uthread.new(self._BuildConstructionPlatform, id)

    def _BuildConstructionPlatform(self, id):
        try:
            securityCode = None
            shell = self.invCache.GetInventoryFromId(id)
            while 1:
                try:
                    if securityCode is None:
                        shell.Build()
                    else:
                        shell.Build(securityCode=securityCode)
                    break
                except UserError as what:
                    if what.args[0] == 'PermissionDenied':
                        if securityCode:
                            caption = localization.GetByLabel('UI/Menusvc/IncorrectPassword')
                            label = localization.GetByLabel('UI/Menusvc/PleaseTryEnteringPasswordAgain')
                        else:
                            caption = localization.GetByLabel('UI/Menusvc/PasswordRequired')
                            label = localization.GetByLabel('UI/Menusvc/PleaseEnterPassword')
                        passw = uiutil.NamePopup(caption=caption, label=label, setvalue='', maxLength=50, passwordChar='*')
                        if passw is None:
                            raise UserError('IgnoreToTop')
                        else:
                            securityCode = passw
                    else:
                        raise 
                    sys.exc_clear()

        finally:
            self._buildingPlatform = 0

    def Bookmark(self, itemID, typeID, parentID, note = None):
        sm.StartService('addressbook').BookmarkLocationPopup(itemID, typeID, parentID, note)

    def ShowInMapBrowser(self, itemID, *args):
        uicore.cmd.OpenMapBrowser(itemID)

    def ShowInMap(self, itemID, *args):
        sm.GetService('viewState').ActivateView('starmap', interestID=itemID)

    def Dock(self, id):
        bp = sm.StartService('michelle').GetBallpark()
        if not bp:
            return
        self.GetCloseAndTryCommand(id, self.RealDock, (id,))

    def RealDock(self, id):
        bp = sm.StartService('michelle').GetBallpark()
        if not bp:
            return
        if sm.GetService('viewState').HasActiveTransition():
            return
        eve.Message('OnDockingRequest')
        eve.Message('CustomNotify', {'notify': localization.GetByLabel('UI/Inflight/RequestToDockAt', station=id)})
        paymentRequired = 0
        try:
            bp = sm.GetService('michelle').GetRemotePark()
            if bp is not None:
                self.LogNotice('Docking', id)
                if uicore.uilib.Key(uiconst.VK_CONTROL) and uicore.uilib.Key(uiconst.VK_SHIFT) and uicore.uilib.Key(uiconst.VK_MENU) and session.role & service.ROLE_GML:
                    success = sm.GetService('sessionMgr').PerformSessionChange('dock', bp.CmdTurboDock, id)
                else:
                    success = sm.GetService('sessionMgr').PerformSessionChange('dock', bp.CmdDock, id, session.shipid)
        except UserError as e:
            if e.msg == 'DockingRequestDeniedPaymentRequired':
                sys.exc_clear()
                paymentRequired = e.args[1]['amount']
            else:
                raise 
        except Exception as e:
            raise 

        if paymentRequired:
            try:
                if eve.Message('AskPayDockingFee', {'cost': paymentRequired}, uiconst.YESNO) == uiconst.ID_YES:
                    bp = sm.GetService('michelle').GetRemotePark()
                    if bp is not None:
                        session.ResetSessionChangeTimer('Retrying with docking payment')
                        if uicore.uilib.Key(uiconst.VK_CONTROL) and session.role & service.ROLE_GML:
                            success = sm.GetService('sessionMgr').PerformSessionChange('dock', bp.CmdTurboDock, id, paymentRequired)
                        else:
                            success = sm.GetService('sessionMgr').PerformSessionChange('dock', bp.CmdDock, id, session.shipid, paymentRequired)
            except Exception as e:
                raise 

    def DefaultWarpToLabel(self):
        defaultWarpDist = sm.GetService('menu').GetDefaultActionDistance('WarpTo')
        label = uiutil.MenuLabel('UI/Inflight/WarpToWithinDistance', {'distance': util.FmtDist(float(defaultWarpDist))})
        return label

    def GetIllegality(self, itemID, typeID = None, solarSystemID = None):
        if solarSystemID is None:
            solarSystemID = session.solarsystemid
        toFactionID = sm.StartService('faction').GetFactionOfSolarSystem(solarSystemID)
        if typeID is not None and cfg.invtypes.Get(typeID).groupID not in (const.groupCargoContainer,
         const.groupSecureCargoContainer,
         const.groupAuditLogSecureContainer,
         const.groupFreightContainer):
            if cfg.invtypes.Get(typeID).Illegality(toFactionID):
                return cfg.invtypes.Get(typeID).name
            return ''
        stuff = ''
        invItem = self.invCache.GetInventoryFromId(itemID)
        for item in invItem.List():
            try:
                illegality = cfg.invtypes.Get(item.typeID).Illegality(toFactionID)
                if illegality:
                    stuff += cfg.invtypes.Get(item.typeID).name + ', '
                if cfg.invtypes.Get(item.typeID).groupID in (const.groupCargoContainer,
                 const.groupSecureCargoContainer,
                 const.groupAuditLogSecureContainer,
                 const.groupFreightContainer):
                    sublegality = self.GetIllegality(item.itemID, solarSystemID=solarSystemID)
                    if sublegality:
                        stuff += sublegality + ', '
            except:
                log.LogTraceback('bork in illegality check 2')
                sys.exc_clear()

        return stuff[:-2]

    def StargateJump(self, id, beaconID = None, solarSystemID = None):
        if beaconID:
            self.GetCloseAndTryCommand(id, self.RealStargateJump, (id, beaconID, solarSystemID), interactionRange=const.maxStargateJumpingDistance)

    def RealStargateJump(self, id, beaconID, solarSystemID):
        if beaconID:
            bp = sm.StartService('michelle').GetRemotePark()
            if bp is not None:
                if solarSystemID is not None:
                    fromFactionID = sm.StartService('faction').GetFactionOfSolarSystem(session.solarsystemid)
                    toFactionID = sm.StartService('faction').GetFactionOfSolarSystem(solarSystemID)
                    if toFactionID and fromFactionID != toFactionID:
                        stuff = self.GetIllegality(session.shipid, solarSystemID=solarSystemID)
                        if stuff and eve.Message('ConfirmJumpWithIllicitGoods', {'faction': cfg.eveowners.Get(toFactionID).name,
                         'stuff': stuff}, uiconst.YESNO, suppress=uiconst.ID_YES) != uiconst.ID_YES:
                            return
                    sec = sm.StartService('map').GetSecurityStatus(solarSystemID)
                    toSecClass = sm.StartService('map').GetSecurityClass(solarSystemID)
                    fromSecClass = sm.StartService('map').GetSecurityClass(session.solarsystemid)
                    if toSecClass <= const.securityClassLowSec:
                        if fromSecClass >= const.securityClassHighSec and eve.Message('ConfirmJumpToUnsafeSS', {'ss': sec}, uiconst.OKCANCEL) != uiconst.ID_OK:
                            return
                    elif fromSecClass <= const.securityClassLowSec and self.crimewatchSvc.IsCriminal(session.charid):
                        if eve.Message('JumpCriminalConfirm', {}, uiconst.YESNO) != uiconst.ID_YES:
                            return
                self.LogNotice('Stargate Jump from', session.solarsystemid2, 'to', id)
                sm.StartService('sessionMgr').PerformSessionChange(localization.GetByLabel('UI/Inflight/Jump'), bp.CmdStargateJump, id, beaconID, session.shipid)

    def ActivateAccelerationGate(self, id):
        self.GetCloseAndTryCommand(id, self.RealActivateAccelerationGate, (id,), interactionRange=const.maxStargateJumpingDistance)

    def RealActivateAccelerationGate(self, id):
        if eve.rookieState and not sm.StartService('tutorial').CheckAccelerationGateActivation():
            return
        sm.StartService('sessionMgr').PerformSessionChange(localization.GetByLabel('UI/Inflight/ActivateGate'), sm.RemoteSvc('keeper').ActivateAccelerationGate, id, violateSafetyTimer=1)
        self.LogNotice('Acceleration Gate activated to ', id)

    def EnterWormhole(self, itemID):
        self.GetCloseAndTryCommand(itemID, self.RealEnterWormhole, (itemID,), interactionRange=const.maxWormholeEnterDistance)

    def RealEnterWormhole(self, itemID):
        fromSecClass = sm.StartService('map').GetSecurityClass(session.solarsystemid)
        if fromSecClass == const.securityClassHighSec and eve.Message('WormholeJumpingFromHiSec', {}, uiconst.YESNO, suppress=uiconst.ID_YES) != uiconst.ID_YES:
            return
        probes = sm.StartService('scanSvc').GetProbeData()
        if probes is not None and len(probes) > 0:
            if eve.Message('WormholeLeaveProbesConfirm', {'probes': len(probes)}, uiconst.YESNO) != uiconst.ID_YES:
                return
        self.LogNotice('Wormhole Jump from', session.solarsystemid2, 'to', itemID)
        sm.StartService('sessionMgr').PerformSessionChange(localization.GetByLabel('UI/Inflight/EnterWormhole'), sm.RemoteSvc('wormholeMgr').WormholeJump, itemID)

    def CopyItemIDToClipboard(self, itemID):
        blue.pyos.SetClipboardData(str(itemID))

    def StopMyShip(self):
        uicore.cmd.CmdStopShip()

    def OpenCargo(self, id, *args):
        self.GetCloseAndTryCommand(id, self.RealOpenCargo, (id,))

    def RealOpenCargo(self, id, *args):
        if getattr(self, '_openingCargo', 0):
            return
        self._openingCargo = 1
        uthread.new(self._OpenCargo, id)

    def _OpenCargo(self, _id):
        if type(_id) != types.ListType:
            _id = [_id]
        for itemID in _id:
            try:
                if itemID == util.GetActiveShip():
                    uicore.cmd.OpenCargoHoldOfActiveShip()
                else:
                    slim = sm.GetService('michelle').GetItem(itemID)
                    if slim and slim.groupID == const.groupWreck:
                        invID = ('ItemWreck', itemID)
                    else:
                        invID = ('ItemFloatingCargo', itemID)
                    invCtrl.GetInvCtrlFromInvID(invID).GetItems()
                    sm.GetService('inv').AddTemporaryInvLocation(invID)
                    wnd = form.Inventory.OpenOrShow(invID=invID)
            finally:
                self._openingCargo = 0

    def OpenShipHangarCargo(self, itemIDs):
        usePrimary = len(itemIDs) == 1
        openFromWnd = uicore.registry.GetActive() if usePrimary else None
        for itemID in itemIDs:
            invID = ('ShipCargo', itemID)
            form.Inventory.OpenOrShow(invID=invID, usePrimary=usePrimary, openFromWnd=openFromWnd)

    def OpenDroneBay(self, itemIDs):
        usePrimary = len(itemIDs) == 1
        openFromWnd = uicore.registry.GetActive() if usePrimary else None
        for itemID in itemIDs:
            invID = ('ShipDroneBay', itemID)
            invCtrl.ShipDroneBay(itemID).GetItems()
            form.Inventory.OpenOrShow(invID=invID, usePrimary=usePrimary, openFromWnd=openFromWnd)

    def OpenPlanetCustomsOfficeImportWindow(self, customsOfficeID):
        sm.GetService('planetUI').OpenPlanetCustomsOfficeImportWindow(customsOfficeID)

    def OpenUpgradeWindow(self, orbitalID):
        sm.GetService('planetUI').OpenUpgradeWindow(orbitalID)

    def AbandonLoot(self, wreckID, *args):
        twit = sm.GetService('michelle')
        localPark = twit.GetBallpark()
        allowedGroup = None
        if wreckID in localPark.slimItems:
            allowedGroup = localPark.slimItems[wreckID].groupID
        if eve.Message('ConfirmAbandonLoot', {'type': (GROUPID, allowedGroup)}, uiconst.YESNO, suppress=uiconst.ID_YES) != uiconst.ID_YES:
            return
        remotePark = sm.GetService('michelle').GetRemotePark()
        if remotePark is not None:
            remotePark.CmdAbandonLoot([wreckID])

    def AbandonAllLoot(self, wreckID, *args):
        twit = sm.GetService('michelle')
        localPark = twit.GetBallpark()
        remotePark = twit.GetRemotePark()
        if remotePark is None:
            return
        wrecks = []
        allowedGroup = None
        if wreckID in localPark.slimItems:
            allowedGroup = localPark.slimItems[wreckID].groupID
        if eve.Message('ConfirmAbandonLootAll', {'type': (GROUPID, allowedGroup)}, uiconst.YESNO, suppress=uiconst.ID_YES) != uiconst.ID_YES:
            return
        bp = sm.GetService('michelle').GetBallpark()
        fleetSvc = sm.GetService('fleet')
        for itemID, slimItem in localPark.slimItems.iteritems():
            if slimItem.groupID == allowedGroup:
                if bp.HaveLootRight(itemID) and not bp.IsAbandoned(itemID):
                    wrecks.append(itemID)

        if remotePark is not None:
            remotePark.CmdAbandonLoot(wrecks)

    def OpenShipMaintenanceBayShip(self, itemID, name):
        invID = ('ShipMaintenanceBay', itemID)
        if itemID != util.GetActiveShip() and not session.stationid2:
            invCtrl.ShipMaintenanceBay(itemID).GetItems()
            sm.GetService('inv').AddTemporaryInvLocation(invID)
        form.Inventory.OpenOrShow(invID=invID)

    def OpenFleetHangar(self, itemID):
        invID = ('ShipFleetHangar', itemID)
        if itemID != util.GetActiveShip() and not session.stationid2:
            invCtrl.ShipFleetHangar(itemID).GetItems()
            sm.GetService('inv').AddTemporaryInvLocation(invID)
        form.Inventory.OpenOrShow(invID=invID)

    def ShipCloneConfig(self, id = None):
        if id == util.GetActiveShip():
            uthread.new(self._ShipCloneConfig)

    def _ShipCloneConfig(self):
        uicore.cmd.OpenShipConfig()

    def RunRefiningProcess(self, refineryID):
        self.invCache.GetInventoryFromId(refineryID).RunRefiningProcess()

    def EnterPOSPassword(self):
        sm.StartService('pwn').EnterShipPassword()

    def EnterForceFieldPassword(self, towerID):
        sm.StartService('pwn').EnterTowerPassword(towerID)

    def Eject(self):
        if eve.Message('ConfirmEject', {}, uiconst.YESNO) == uiconst.ID_YES:
            ship = sm.StartService('gameui').GetShipAccess()
            if ship:
                if session.stationid:
                    eve.Message('NoEjectingToSpaceInStation')
                else:
                    self.LogNotice('Ejecting from ship', session.shipid)
                    sm.ScatterEvent('OnBeforeActiveShipChanged', None, util.GetActiveShip())
                    sm.StartService('sessionMgr').PerformSessionChange('eject', ship.Eject)

    def Board(self, id):
        ship = sm.StartService('gameui').GetShipAccess()
        if ship:
            self.LogNotice('Boarding ship', id)
            sm.ScatterEvent('OnBeforeActiveShipChanged', id, util.GetActiveShip())
            sm.StartService('sessionMgr').PerformSessionChange('board', ship.Board, id, session.shipid or session.stationid)
            shipItem = sm.StartService('godma').GetItem(session.shipid)
            if shipItem and shipItem.groupID != const.groupRookieship:
                sm.StartService('tutorial').OpenTutorialSequence_Check(uix.insuranceTutorial)

    def BoardSMAShip(self, structureID, shipID):
        ship = sm.StartService('gameui').GetShipAccess()
        if ship:
            self.LogNotice('Boarding SMA ship', structureID, shipID)
            sm.ScatterEvent('OnBeforeActiveShipChanged', shipID, util.GetActiveShip())
            sm.StartService('sessionMgr').PerformSessionChange('board', ship.BoardStoredShip, structureID, shipID)
            shipItem = sm.StartService('godma').GetItem(session.shipid)
            if shipItem and shipItem.groupID != const.groupRookieship:
                sm.StartService('tutorial').OpenTutorialSequence_Check(uix.insuranceTutorial)

    def ToggleAutopilot(self, on):
        if on:
            sm.StartService('autoPilot').SetOn()
        else:
            sm.StartService('autoPilot').SetOff('toggled through menu')

    def SelfDestructShip(self, pickid):
        if eve.Message('ConfirmSelfDestruct', {}, uiconst.YESNO) == uiconst.ID_YES:
            ship = sm.StartService('gameui').GetShipAccess()
            if ship and not session.stationid:
                self.LogNotice('Self Destruct for', session.shipid)
                sm.StartService('sessionMgr').PerformSessionChange('selfdestruct', ship.SelfDestruct, pickid)

    def SafeLogoff(self):
        shipAccess = sm.GetService('gameui').GetShipAccess()
        failedConditions = shipAccess.SafeLogoff()
        if failedConditions:
            eve.Message('CustomNotify', {'notify': '<br>'.join([localization.GetByLabel('UI/Inflight/SafeLogoff/ConditionsFailedHeader')] + [ localization.GetByLabel(error) for error in failedConditions ])})

    def SetParent(self, pickid):
        sm.GetService('camera').SetCameraParent(pickid)

    def SetInterest(self, pickid):
        sm.GetService('camera').SetCameraInterest(pickid)

    def TryLookAt(self, itemID):
        slimItem = uix.GetBallparkRecord(itemID)
        if not slimItem:
            return
        try:
            sm.GetService('camera').LookAt(itemID)
        except Exception as e:
            sys.exc_clear()

    def ToggleLookAt(self, itemID):
        bp = sm.GetService('michelle').GetBallpark()
        if bp:
            ball = bp.GetBall(session.shipid)
            if ball and ball.mode == destiny.DSTBALL_WARP:
                return
        if sm.GetService('camera').LookingAt() == itemID and itemID != session.shipid:
            self.TryLookAt(session.shipid)
        else:
            self.TryLookAt(itemID)

    def Scoop(self, objectID, typeID, password = None):
        self.GetCloseAndTryCommand(objectID, self.RealScoop, (objectID, typeID, password))

    def RealScoop(self, objectID, typeID, password = None):
        ship = sm.StartService('gameui').GetShipAccess()
        if ship:
            toFactionID = sm.StartService('faction').GetFactionOfSolarSystem(session.solarsystemid)
            stuff = self.GetIllegality(objectID, typeID)
            if stuff and eve.Message('ConfirmScoopWithIllicitGoods', {'faction': cfg.eveowners.Get(toFactionID).name}, uiconst.YESNO, suppress=uiconst.ID_YES) != uiconst.ID_YES:
                return
            try:
                if password is None:
                    ship.Scoop(objectID)
                else:
                    ship.Scoop(objectID, password)
            except UserError as what:
                if what.args[0] == 'ShpScoopSecureCC':
                    if password:
                        caption = localization.GetByLabel('UI/Menusvc/IncorrectPassword')
                        label = localization.GetByLabel('UI/Menusvc/PleaseTryEnteringPasswordAgain')
                    else:
                        caption = localization.GetByLabel('UI/Menusvc/PasswordRequired')
                        label = localization.GetByLabel('UI/Menusvc/PleaseEnterPassword')
                    passw = uiutil.NamePopup(caption=caption, label=label, setvalue='', maxLength=50, passwordChar='*')
                    if passw:
                        self.Scoop(objectID, password=passw)
                else:
                    raise 
                sys.exc_clear()

    def ScoopSMA(self, objectID):
        self.GetCloseAndTryCommand(objectID, self.RealScoopSMA, (objectID,))

    def RealScoopSMA(self, objectID):
        ship = sm.StartService('gameui').GetShipAccess()
        if ship:
            ship.ScoopToSMA(objectID)

    def InteractWithAgent(self, agentID, *args):
        sm.StartService('agents').InteractWith(agentID)

    def QuickBuy(self, typeID):
        sm.StartService('marketutils').Buy(typeID)

    def QuickSell(self, invItem):
        sm.StartService('marketutils').Sell(invItem.typeID, invItem=invItem)

    def QuickContract(self, invItems, *args):
        sm.GetService('contracts').OpenCreateContract(items=invItems)

    def ShowMarketDetails(self, invItem):
        uthread.new(sm.StartService('marketutils').ShowMarketDetails, invItem.typeID, None)

    def GetContainerContents(self, invItem):
        hasFlag = invItem.categoryID == const.categoryShip
        name = cfg.invtypes.Get(invItem.typeID).name
        stationID = self.invCache.GetStationIDOfItem(invItem)
        self.DoGetContainerContents(invItem.itemID, stationID, hasFlag, name)

    def DoGetContainerContents(self, itemID, stationID, hasFlag, name):
        contents = self.invCache.GetInventoryMgr().GetContainerContents(itemID, stationID)
        t = ''
        lst = []
        for c in contents:
            locationName = ''
            flag = c.flagID
            if flag == const.flagPilot:
                continue
            locationName = util.GetShipFlagLocationName(flag)
            t = cfg.invtypes.Get(c.typeID)
            if hasFlag:
                txt = '%s<t>%s<t>%s<t>%s' % (t.name,
                 cfg.invgroups.Get(t.groupID).name,
                 locationName,
                 c.stacksize)
            else:
                txt = '%s<t>%s<t>%s' % (t.name, cfg.invgroups.Get(t.groupID).name, c.stacksize)
            lst.append([txt, c.itemID, c.typeID])

        if hasFlag:
            hdr = [localization.GetByLabel('UI/Inventory/InvItemNameShort'),
             localization.GetByLabel('UI/Inventory/ItemGroup'),
             localization.GetByLabel('UI/Common/Location'),
             localization.GetByLabel('UI/Common/Quantity')]
        else:
            hdr = [localization.GetByLabel('UI/Inventory/InvItemNameShort'), localization.GetByLabel('UI/Inventory/ItemGroup'), localization.GetByLabel('UI/Common/Quantity')]
        hint1 = localization.GetByLabel('UI/Menusvc/ItemsInContainerHint')
        hint2 = localization.GetByLabel('UI/Menusvc/ItemsInContainerHint2', containerName=name)
        uix.ListWnd(lst, 'item', hint1, hint=hint2, isModal=0, minChoices=0, scrollHeaders=hdr, minw=500, windowName='containerContents')

    def AddToQuickBar(self, typeID, parent = 0):
        sm.GetService('marketutils').AddTypeToQuickBar(typeID, parent)

    def RemoveFromQuickBar(self, node):
        current = settings.user.ui.Get('quickbar', {})
        parent = node.parent
        typeID = node.typeID
        toDelete = None
        for id, data in current.items():
            if parent == data.parent and type(data.label) == types.IntType:
                if data.label == typeID:
                    toDelete = id
                    break

        if toDelete:
            del current[id]
        settings.user.ui.Set('quickbar', current)
        sm.ScatterEvent('OnMarketQuickbarChange')

    def GetAndvancedMarket(self, typeID):
        pass

    def ActivateShip(self, invItem):
        if invItem.singleton and not uicore.uilib.Key(uiconst.VK_CONTROL):
            sm.StartService('station').TryActivateShip(invItem)

    def LeaveShip(self, invItem):
        if invItem.singleton and not uicore.uilib.Key(uiconst.VK_CONTROL):
            sm.StartService('station').TryLeaveShip(invItem)

    def EnterHangar(self, invItem):
        uicore.cmd.CmdEnterHangar()

    def EnterCQ(self, invItem):
        uicore.cmd.CmdEnterCQ()

    def StripFitting(self, invItem):
        if eve.Message('AskStripShip', None, uiconst.YESNO, suppress=uiconst.ID_YES) == uiconst.ID_YES:
            shipID = invItem.itemID
            self.invCache.GetInventoryFromId(shipID).StripFitting()

    def ExitStation(self, invItem):
        uicore.cmd.CmdExitStation()

    def CheckLocked(self, func, invItemsOrIDs):
        if not len(invItemsOrIDs):
            return
        if type(invItemsOrIDs[0]) == int or not hasattr(invItemsOrIDs[0], 'itemID'):
            ret = func(invItemsOrIDs)
        else:
            lockedItems = []
            try:
                for item in invItemsOrIDs:
                    if self.invCache.IsItemLocked(item.itemID):
                        continue
                    if self.invCache.TryLockItem(item.itemID):
                        lockedItems.append(item)

                if not len(lockedItems):
                    eve.Message('BusyItems')
                    return
                ret = func(lockedItems)
            finally:
                for invItem in lockedItems:
                    self.invCache.UnlockItem(invItem.itemID)

        return ret

    def Repackage(self, invItems):
        if eve.Message('ConfirmRepackageItem', {}, uiconst.YESNO) != uiconst.ID_YES:
            return
        validIDsByStationID = defaultdict(list)
        insuranceQ_OK = 0
        insuranceContracts = None
        checksToSkip = set()
        godma = sm.GetService('godma')
        for invItem in invItems:
            skipThis = False
            itemState = godma.GetItem(invItem.itemID)
            if itemState and (itemState.damage or invItem.categoryID in (const.categoryShip, const.categoryDrone) and itemState.armorDamage):
                eve.Message('CantRepackageDamagedItem')
                continue
            if invItem.categoryID == const.categoryShip:
                if insuranceContracts is None:
                    insuranceContracts = sm.StartService('insurance').GetContracts()
                if not insuranceQ_OK and invItem.itemID in insuranceContracts:
                    if eve.Message('RepairUnassembleVoidsContract', {}, uiconst.YESNO) != uiconst.ID_YES:
                        continue
                    insuranceQ_OK = 1
                if self.invCache.IsInventoryPrimedAndListed(invItem.itemID):
                    inv = self.invCache.GetInventoryFromId(invItem.itemID)
                    dogmaStaticMgr = sm.GetService('clientDogmaStaticSvc')
                    for item in [ i for i in inv.List() if cfg.IsShipFittingFlag(i.flagID) ]:
                        if dogmaStaticMgr.TypeHasEffect(item.typeID, const.effectRigSlot):
                            if eve.Message('ConfirmRepackageSomethingWithUpgrades', {'what': (LOCID, invItem.itemID)}, uiconst.YESNO, suppress=uiconst.ID_YES) == uiconst.ID_YES:
                                checksToSkip.add('ConfirmRepackageSomethingWithUpgrades')
                            else:
                                skipThis = True
                                break

                    if skipThis:
                        continue
            stationID = self.invCache.GetStationIDOfItem(invItem)
            if stationID is not None:
                validIDsByStationID[stationID].append((invItem.itemID, invItem.locationID))

        if len(validIDsByStationID) == 0:
            return
        try:
            sm.RemoteSvc('repairSvc').DisassembleItems(dict(validIDsByStationID), list(checksToSkip))
        except UserError as e:
            if cfg.messages[e.msg].messageType == 'question' and eve.Message(e.msg, e.dict, uiconst.YESNO, suppress=uiconst.ID_YES) == uiconst.ID_YES:
                checksToSkip.add(e.msg)
                return sm.RemoteSvc('repairSvc').DisassembleItems(dict(validIDsByStationID), list(checksToSkip))
            raise 

    def Break(self, invItems):
        ok = 0
        validIDs = []
        for invItem in invItems:
            if ok or eve.Message('ConfirmBreakCourierPackage', {}, uiconst.OKCANCEL) == uiconst.ID_OK:
                validIDs.append(invItem.itemID)
                ok = 1

        for itemID in validIDs:
            self.invCache.GetInventoryFromId(itemID).BreakPlasticWrap()

    def DeliverCourierContract(self, invItem):
        sm.GetService('contracts').DeliverCourierContractFromItemID(invItem.itemID)

    def FindCourierContract(self, invItem):
        sm.GetService('contracts').FindCourierContractFromItemID(invItem.itemID)

    def FitShip(self, invItem):
        wnd = form.FittingWindow.GetIfOpen()
        if wnd is not None:
            wnd.CloseByUser()
        form.FittingWindow.Open(shipID=invItem.itemID)

    def LaunchDrones(self, invItems, *args):
        sm.GetService('godma').GetStateManager().SendDroneSettings()
        util.LaunchFromShip(invItems)

    def LaunchForSelf(self, invItems):
        util.LaunchFromShip(invItems, session.charid)

    def LaunchForCorp(self, invItems, ignoreWarning = False):
        util.LaunchFromShip(invItems, session.corpid, ignoreWarning)

    def LaunchSMAContents(self, invItems):
        if type(invItems) is not list:
            invItems = [invItems]
        structureID = None
        bp = sm.StartService('michelle').GetBallpark()
        myShipBall = bp.GetBall(session.shipid)
        if myShipBall and myShipBall.mode == destiny.DSTBALL_WARP:
            raise UserError('ShipInWarp')
        ids = []
        for invItem in invItems:
            structureID = invItem.locationID
            ids += [invItem.itemID] * invItem.stacksize

        sm.StartService('gameui').GetShipAccess().LaunchFromContainer(structureID, ids)

    def Jettison(self, invItems):
        if eve.Message('ConfirmJettison', {}, uiconst.YESNO, suppress=uiconst.ID_YES) != uiconst.ID_YES:
            return
        ids = []
        for invItem in invItems:
            ids += [invItem.itemID]

        ship = sm.StartService('gameui').GetShipAccess()
        if ship:
            ship.Jettison(ids)

    def TrashInvItems(self, invItems):
        if len(invItems) == 0:
            return
        self.CheckItemsInSamePlace(invItems)
        if len(invItems) == 1:
            question = 'ConfirmTrashingSin'
            itemWithQuantity = cfg.FormatConvert(TYPEIDANDQUANTITY, invItems[0].typeID, invItems[0].stacksize)
            args = {'itemWithQuantity': itemWithQuantity}
        else:
            question = 'ConfirmTrashingPlu'
            report = ''
            for item in invItems:
                report += '<t>- %s<br>' % cfg.FormatConvert(TYPEIDANDQUANTITY, item.typeID, item.stacksize)

            args = {'items': report}
        if eve.Message(question, args, uiconst.YESNO) != uiconst.ID_YES:
            return
        stationID = self.invCache.GetStationIDOfItem(invItems[0])
        windows = ['sma',
         'corpHangar',
         'drones',
         'shipCargo']
        for item in invItems:
            isShip = False
            if hasattr(item, 'categoryID'):
                isShip = item.categoryID == const.categoryShip
            else:
                isShip = cfg.invtypes.Get(item.typeID).categoryID == const.categoryShip
            if isShip:
                for window in windows:
                    uicls.Window.CloseIfOpen(windowID='%s_%s' % (window, item.itemID))

        errors = self.invCache.GetInventoryMgr().TrashItems([ item.itemID for item in invItems ], stationID if stationID else invItems[0].locationID)
        if errors:
            for e in errors:
                eve.Message(e)

            return
        isCorp = invItems[0].ownerID == session.corpid
        self.InvalidateItemLocation([session.charid, session.corpid][isCorp], stationID, invItems[0].flagID)
        if isCorp:
            sm.ScatterEvent('OnCorpAssetChange', invItems, stationID)

    def Refine(self, invItems):
        if not session.stationid:
            return
        if len(invItems) == 1:
            item = invItems[0]
            ty = cfg.invtypes.Get(item.typeID)
            if item.stacksize < ty.portionSize:
                eve.Message('QuantityLessThanMinimumPortion', {'typename': ty.name,
                 'portion': ty.portionSize})
                return
        sm.StartService('reprocessing').ReprocessDlg(invItems)

    def RefineToHangar(self, invItems):
        if not session.stationid:
            return
        ownerID, flag = invItems[0].ownerID, invItems[0].flagID
        if flag not in (const.flagHangar,
         const.flagCorpSAG2,
         const.flagCorpSAG3,
         const.flagCorpSAG4,
         const.flagCorpSAG5,
         const.flagCorpSAG6,
         const.flagCorpSAG7):
            flag = const.flagHangar
        if flag != const.flagHangar and ownerID != session.corpid:
            ownerID = session.corpid
        if ownerID not in (session.charid, session.corpid):
            ownerID = session.charid
        sm.StartService('reprocessing').ReprocessDlg(invItems, ownerID, flag)

    def TrainNow(self, invItems):
        if len(invItems) > 1:
            eve.Message('TrainMoreTheOne')
            return
        self.InjectSkillIntoBrain(invItems)
        blue.pyos.synchro.SleepWallclock(500)
        sm.GetService('skillqueue').TrainSkillNow(invItems[0].typeID, 1)

    def InjectSkillIntoBrain(self, invItems):
        sm.StartService('skills').InjectSkillIntoBrain(invItems)

    def PlugInImplant(self, invItems):
        if eve.Message('ConfirmPlugInImplant', {}, uiconst.OKCANCEL) != uiconst.ID_OK:
            return
        for invItem in invItems:
            sm.StartService('godma').GetSkillHandler().CharAddImplant(invItem.itemID)

    def ApplyPilotLicence(self, itemID):
        try:
            sm.RemoteSvc('userSvc').ApplyPilotLicence(itemID, justQuery=True)
        except UserError as e:
            if e.msg == '28DaysConfirmApplyServer':
                if eve.Message(e.msg, e.dict, uiconst.YESNO) != uiconst.ID_YES:
                    return
                sm.RemoteSvc('userSvc').ApplyPilotLicence(itemID, justQuery=False)
            else:
                raise 

    def ApplyAurumToken(self, item, qty):
        if item.typeID == const.typePilotLicence and boot.region == 'optic':
            conversionRate = const.chinaPlex2AurExchangeRatio
        else:
            conversionRate = sm.GetService('clientDogmaStaticSvc').GetTypeAttribute2(item.typeID, const.attributeAurumConversionRate)
        totalAurum = conversionRate * qty
        headerLabel = localization.GetByLabel('UI/Menusvc/ConvertAurumQuestionHeader')
        bodyLabel = localization.GetByLabel('UI/Menusvc/ConvertAurumQuestionBody', typeName=cfg.invtypes.Get(item.typeID).typeName, quantity=qty, totalAurum=totalAurum)
        if eve.Message('CustomQuestion', {'header': headerLabel,
         'question': bodyLabel}, uiconst.YESNO, suppress=uiconst.ID_YES) != uiconst.ID_YES:
            return
        sm.GetService('invCache').GetInventoryMgr().ConvertAurTokenToCurrency([item.itemID], qty)

    def ConsumeBooster(self, invItems):
        if type(invItems) is not list:
            invItems = [invItems]
        for invItem in invItems:
            sm.StartService('godma').GetSkillHandler().CharUseBooster(invItem.itemID, invItem.locationID)

    def AssembleContainer(self, invItems):
        invMgr = self.invCache.GetInventoryMgr()
        for invItem in invItems:
            invMgr.AssembleCargoContainer(invItem.itemID, None, 0.0)

    def OpenInfrastructureHubPanel(self, itemID):
        occupierID = sm.GetService('facwar').GetSystemOccupier(session.solarsystemid)
        if occupierID == session.warfactionid:
            bp = sm.GetService('michelle').GetBallpark()
            distance = bp.GetSurfaceDist(session.shipid, itemID)
            if distance < const.facwarIHubInteractDist:
                form.FWInfrastructureHub.Open(itemID=itemID)
            else:
                uicore.Message('InfrastructureHubCannotOpenDistance')
        else:
            uicore.Message('InfrastructureHubCannotOpenFaction', {'factionName': cfg.eveowners.Get(occupierID).name})

    def OpenCargoContainer(self, invItems):
        usePrimary = len(invItems) == 1
        openFromWnd = uicore.registry.GetActive() if usePrimary else None
        for item in invItems:
            if item.ownerID not in (session.charid, session.corpid):
                eve.Message('CantDoThatWithSomeoneElsesStuff')
                return
            invID = ('StationContainer', item.itemID)
            form.Inventory.OpenOrShow(invID=invID, usePrimary=usePrimary, openFromWnd=openFromWnd)

    def Manufacture(self, invItems, activityID):
        sm.StartService('manufacturing').CreateJob(invItems, None, activityID)

    @base.ThrottlePerSecond()
    def AssembleShip(self, invItems):
        itemIDs = []
        for item in invItems:
            techLevel = sm.StartService('godma').GetTypeAttribute(invItems[0].typeID, const.attributeTechLevel)
            if techLevel is None:
                techLevel = 1
            else:
                techLevel = int(techLevel)
            if techLevel == 3:
                if session.stationid is None:
                    eve.Message('CantAssembleModularShipInSpace')
                    return
                wndName = 'assembleWindow_%s' % item.itemID
                wnd = form.AssembleShip.GetIfOpen(windowID=wndName)
                if wnd is None:
                    wnd = form.AssembleShip.Open(windowID=wndName, ship=invItems[0])
                else:
                    wnd.Maximize()
                return
            itemIDs.append(item.itemID)

        sm.StartService('gameui').GetShipAccess().AssembleShip(itemIDs)

    def TryFit(self, invItems, shipID = None):
        if not shipID:
            shipID = util.GetActiveShip()
            if not shipID:
                return
        godma = sm.services['godma']
        shipInv = self.invCache.GetInventoryFromId(shipID, locationID=session.stationid2)
        dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
        godmaSM = godma.GetStateManager()
        useRigs = None
        charges = set()
        drones = []
        for invItem in invItems[:]:
            dogmaLocation.CheckSkillRequirementsForType(invItem.typeID, 'FittingHasSkillPrerequisites')
            if invItem.categoryID == const.categoryModule:
                moduleEffects = cfg.dgmtypeeffects.get(invItem.typeID, [])
                for mEff in moduleEffects:
                    if mEff.effectID == const.effectRigSlot:
                        if useRigs is None:
                            useRigs = True if self.RigFittingCheck(invItem) else False
                        if not useRigs:
                            invItems.remove(invItem)
                            self.invCache.UnlockItem(invItem.itemID)
                            break

            elif invItem.categoryID == const.categoryCharge:
                charges.add(invItem)
                invItems.remove(invItem)
            elif invItem.categoryID == const.categoryDrone:
                drones.append(invItem)
                invItems.remove(invItem)

        if len(invItems) > 0:
            shipInv.moniker.MultiAdd([ invItem.itemID for invItem in invItems ], invItems[0].locationID, flag=const.flagAutoFit)
        if charges:
            shipStuff = shipInv.List()
            shipStuff.sort(key=lambda r: (r.flagID, isinstance(r.itemID, tuple)))
            loadedSlots = set()
        if drones:
            invCtrl.ShipDroneBay(shipID or util.GetActiveShip()).AddItems(drones)
        dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
        shipDogmaItem = dogmaLocation.dogmaItems.get(shipID, None)
        loadedSomething = False
        for DBRowInvItem in charges:
            invItem = util.KeyVal(DBRowInvItem)
            chargeDgmType = godmaSM.GetType(invItem.typeID)
            isCrystalOrScript = invItem.groupID in cfg.GetCrystalGroups()
            for row in shipStuff:
                if row in loadedSlots:
                    continue
                if not cfg.IsShipFittingFlag(row.flagID):
                    continue
                if dogmaLocation.IsInWeaponBank(row.locationID, row.itemID) and dogmaLocation.IsModuleSlave(row.itemID, row.locationID):
                    continue
                if row.categoryID == const.categoryCharge:
                    continue
                moduleDgmType = godmaSM.GetType(row.typeID)
                desiredSize = getattr(moduleDgmType, 'chargeSize', None)
                for x in xrange(1, 5):
                    chargeGroup = getattr(moduleDgmType, 'chargeGroup%d' % x, False)
                    if not chargeGroup:
                        continue
                    if chargeDgmType.groupID != chargeGroup:
                        continue
                    if desiredSize and getattr(chargeDgmType, 'chargeSize', -1) != desiredSize:
                        continue
                    leftOvers = False
                    for i, squatter in enumerate([ i for i in shipStuff if i.flagID == row.flagID ]):
                        if isCrystalOrScript and i > 0:
                            break
                        if shipDogmaItem is None:
                            continue
                        subLocation = dogmaLocation.GetSubLocation(shipID, squatter.flagID)
                        if subLocation is None:
                            continue
                        chargeVolume = chargeDgmType.volume * dogmaLocation.GetAttributeValue(subLocation, const.attributeQuantity)
                        if godmaSM.GetType(row.typeID).capacity <= chargeVolume:
                            break
                    else:
                        moduleCapacity = godmaSM.GetType(row.typeID).capacity
                        numCharges = moduleCapacity / chargeDgmType.volume
                        subLocation = dogmaLocation.GetSubLocation(shipID, row.flagID)
                        if subLocation:
                            numCharges -= dogmaLocation.GetAttributeValue(subLocation, const.attributeQuantity)
                        dogmaLocation.LoadAmmoToModules(shipID, [row.itemID], invItem.typeID, invItem.itemID, invItem.locationID)
                        loadedSomething = True
                        invItem.stacksize -= numCharges
                        loadedSlots.add(row)
                        blue.pyos.synchro.SleepWallclock(100)
                        break

                else:
                    continue

                if invItem.stacksize <= 0:
                    break
            else:
                if not loadedSomething:
                    eve.Message('NoSuitableModules')

    def HandleMultipleCallError(self, droneID, ret, messageName):
        if not len(ret):
            return
        if len(droneID) == 1:
            pick = droneID[0]
            raise UserError(ret[pick][0], ret[pick][1])
        elif len(droneID) >= len(ret):
            lastError = ''
            for error in ret.itervalues():
                if error[0] != lastError and lastError != '':
                    raise UserError(messageName, {'succeeded': len(droneID) - len(ret),
                     'failed': len(ret),
                     'total': len(droneID)})
                lastError = error[0]
            else:
                pick = ret.items()[0][1]
                raise UserError(pick[0], pick[1])

    def EngageTarget(self, droneIDs):
        michelle = sm.StartService('michelle')
        dronesRemoved = []
        for droneID in droneIDs:
            item = michelle.GetItem(droneID)
            if not item:
                dronesRemoved.append(droneID)

        for droneID in dronesRemoved:
            droneIDs.remove(droneID)

        targetID = sm.GetService('target').GetActiveTargetID()
        if targetID is None:
            raise UserError('DroneCommandRequiresActiveTarget')
        crimewatchSvc = sm.GetService('crimewatchSvc')
        requiredSafetyLevel = crimewatchSvc.GetRequiredSafetyLevelForEngagingDrones(droneIDs, targetID)
        if crimewatchSvc.CheckUnsafe(requiredSafetyLevel):
            crimewatchSvc.SafetyActivated(requiredSafetyLevel)
            return
        entity = moniker.GetEntityAccess()
        if entity:
            ret = entity.CmdEngage(droneIDs, targetID)
            self.HandleMultipleCallError(droneIDs, ret, 'MultiDroneCmdResult')
            if droneIDs:
                name = sm.GetService('space').GetWarpDestinationName(targetID)
                eve.Message('CustomNotify', {'notify': localization.GetByLabel('UI/Inflight/DronesEngaging', name=name)})

    def ReturnControl(self, droneIDs):
        michelle = sm.StartService('michelle')
        dronesByOwner = {}
        for droneID in droneIDs:
            ownerID = michelle.GetDroneState(droneID).ownerID
            if dronesByOwner.has_key(ownerID):
                dronesByOwner[ownerID].append(droneID)
            else:
                dronesByOwner[ownerID] = [droneID]

        entity = moniker.GetEntityAccess()
        if entity:
            for ownerID, IDs in dronesByOwner.iteritems():
                ret = entity.CmdRelinquishControl(IDs)
                self.HandleMultipleCallError(droneIDs, ret, 'MultiDroneCmdResult')

    def DelegateControl(self, charID, droneIDs):
        if charID is None:
            targetID = sm.StartService('target').GetActiveTargetID()
            if targetID is None:
                raise UserError('DroneCommandRequiresActiveTarget')
            michelle = sm.StartService('michelle')
            targetItem = michelle.GetItem(targetID)
            if targetItem.categoryID != const.categoryShip or targetItem.groupID == const.groupCapsule:
                raise UserError('DroneCommandRequiresShipButNotCapsule')
            targetBall = michelle.GetBall(targetID)
            if not targetBall.isInteractive or not sm.GetService('fleet').IsMember(targetItem.ownerID):
                raise UserError('DroneCommandRequiresShipPilotedFleetMember')
            controllerID = targetItem.ownerID
        else:
            controllerID = charID
        entity = moniker.GetEntityAccess()
        if entity:
            ret = entity.CmdDelegateControl(droneIDs, controllerID)
            self.HandleMultipleCallError(droneIDs, ret, 'MultiDroneCmdResult')

    def Assist(self, charID, droneIDs):
        if charID is None:
            targetID = sm.StartService('target').GetActiveTargetID()
            if targetID is None:
                raise UserError('DroneCommandRequiresActiveTarget')
            michelle = sm.StartService('michelle')
            targetItem = michelle.GetItem(targetID)
            if targetItem.categoryID != const.categoryShip or targetItem.groupID == const.groupCapsule:
                raise UserError('DroneCommandRequiresShipButNotCapsule')
            targetBall = michelle.GetBall(targetID)
            if not targetBall.isInteractive or not sm.GetService('fleet').IsMember(targetItem.ownerID):
                raise UserError('DroneCommandRequiresShipPilotedFleetMember')
            assistID = targetItem.ownerID
        else:
            assistID = charID
        entity = moniker.GetEntityAccess()
        if entity:
            ret = entity.CmdAssist(assistID, droneIDs)
            self.HandleMultipleCallError(droneIDs, ret, 'MultiDroneCmdResult')

    def Guard(self, charID, droneIDs):
        if charID is None:
            targetID = sm.StartService('target').GetActiveTargetID()
            if targetID is None:
                raise UserError('DroneCommandRequiresActiveTarget')
            michelle = sm.StartService('michelle')
            targetItem = michelle.GetItem(targetID)
            if targetItem.categoryID != const.categoryShip or targetItem.groupID == const.groupCapsule:
                raise UserError('DroneCommandRequiresShipButNotCapsule')
            targetBall = michelle.GetBall(targetID)
            if not targetBall.isInteractive or not sm.GetService('fleet').IsMember(targetItem.ownerID):
                raise UserError('DroneCommandRequiresShipPilotedFleetMember')
            guardID = targetItem.ownerID
        else:
            guardID = charID
        entity = moniker.GetEntityAccess()
        if entity:
            ret = entity.CmdGuard(guardID, droneIDs)
            self.HandleMultipleCallError(droneIDs, ret, 'MultiDroneCmdResult')

    def Mine(self, droneIDs):
        targetID = sm.StartService('target').GetActiveTargetID()
        if targetID is None:
            raise UserError('DroneCommandRequiresActiveTarget')
        entity = moniker.GetEntityAccess()
        if entity:
            ret = entity.CmdMine(droneIDs, targetID)
            self.HandleMultipleCallError(droneIDs, ret, 'MultiDroneCmdResult')

    def MineRepeatedly(self, droneIDs):
        targetID = sm.StartService('target').GetActiveTargetID()
        if targetID is None:
            raise UserError('DroneCommandRequiresActiveTarget')
        entity = moniker.GetEntityAccess()
        if entity:
            ret = entity.CmdMineRepeatedly(droneIDs, targetID)
            self.HandleMultipleCallError(droneIDs, ret, 'MultiDroneCmdResult')

    def Salvage(self, droneIDs):
        targetID = sm.GetService('target').GetActiveTargetID()
        entity = moniker.GetEntityAccess()
        if entity:
            ret = entity.CmdSalvage(droneIDs, targetID)
            self.HandleMultipleCallError(droneIDs, ret, 'MultiDroneCmdResult')

    def DroneUnanchor(self, droneIDs):
        targetID = sm.StartService('target').GetActiveTargetID()
        if targetID is None:
            raise UserError('DroneCommandRequiresActiveTarget')
        entity = moniker.GetEntityAccess()
        if entity:
            ret = entity.CmdUnanchor(droneIDs, targetID)
            self.HandleMultipleCallError(droneIDs, ret, 'MultiDroneCmdResult')

    def ReturnAndOrbit(self, droneIDs):
        entity = moniker.GetEntityAccess()
        if entity:
            ret = entity.CmdReturnHome(droneIDs)
            self.HandleMultipleCallError(droneIDs, ret, 'MultiDroneCmdResult')

    def ReturnToDroneBay(self, droneIDs):
        entity = moniker.GetEntityAccess()
        if entity:
            ret = entity.CmdReturnBay(droneIDs)
            self.HandleMultipleCallError(droneIDs, ret, 'MultiDroneCmdResult')

    def ScoopToDroneBay(self, objectIDs):
        if len(objectIDs) == 1:
            self.GetCloseAndTryCommand(objectIDs[0], self.RealScoopToDroneBay, (objectIDs,))
        else:
            self.RealScoopToDroneBay(objectIDs)

    def RealScoopToDroneBay(self, objectIDs):
        ship = sm.StartService('gameui').GetShipAccess()
        if ship:
            ret = ship.ScoopDrone(objectIDs)
            self.HandleMultipleCallError(objectIDs, ret, 'MultiDroneCmdResult')

    def FitDrone(self, invItems):
        if type(invItems) is not list:
            invItems = [invItems]
        itemIDs = [ node.itemID for node in invItems ]
        if session.shipid:
            for itemID in itemIDs:
                self.invCache.UnlockItem(itemID)

            self.invCache.GetInventoryFromId(session.shipid).MultiAdd(itemIDs, invItems[0].locationID, flag=const.flagDroneBay)

    def AbandonDrone(self, droneIDs):
        if eve.Message('ConfirmAbandonDrone', {}, uiconst.YESNO, suppress=uiconst.ID_YES) != uiconst.ID_YES:
            return
        entity = moniker.GetEntityAccess()
        if entity:
            ret = entity.CmdAbandonDrone(droneIDs)
            self.HandleMultipleCallError(droneIDs, ret, 'MultDroneCmdResult')

    def CopyItemIDAndMaybeQuantityToClipboard(self, invItem):
        txt = str(invItem.itemID)
        if invItem.stacksize > 1:
            txt = uiutil.MenuLabel('UI/Menusvc/ItemAndQuantityForClipboard', {'itemID': str(invItem.itemID),
             'quantity': invItem.stacksize})
        blue.pyos.SetClipboardData(txt)

    def SetName(self, invOrSlimItem):
        self.invCache.TryLockItem(invOrSlimItem.itemID, 'lockItemRenaming', {'itemType': invOrSlimItem.typeID}, 1)
        try:
            cfg.evelocations.Prime([invOrSlimItem.itemID])
            try:
                setval = cfg.evelocations.Get(invOrSlimItem.itemID).name
            except:
                setval = ''
                sys.exc_clear()

            maxLength = 100
            categoryID = cfg.invtypes.Get(invOrSlimItem.typeID).Group().Category().id
            if categoryID == const.categoryShip:
                maxLength = 20
            elif categoryID == const.categoryStructure:
                maxLength = 32
            nameRet = uiutil.NamePopup(localization.GetByLabel('UI/Menusvc/SetName'), localization.GetByLabel('UI/Menusvc/TypeInNewName'), setvalue=setval, maxLength=maxLength)
            if nameRet:
                self.invCache.GetInventoryMgr().SetLabel(invOrSlimItem.itemID, nameRet.replace('\n', ' '))
                sm.ScatterEvent('OnItemNameChange')
        finally:
            self.invCache.UnlockItem(invOrSlimItem.itemID)

    def AskNewContainerPwd(self, invItems, desc, which = 1):
        for invItem in invItems:
            self.AskNewContainerPassword(invItem.itemID, desc, which)

    def GetGlobalActiveItemKeyName(self, forWhat):
        key = None
        actions = ['UI/Inflight/OrbitObject', 'UI/Inflight/Submenus/KeepAtRange', self.DefaultWarpToLabel()[0]]
        if forWhat in actions:
            idx = actions.index(forWhat)
            key = ['Orbit', 'KeepAtRange', 'WarpTo'][idx]
        return key

    def GetDefaultActionDistance(self, key):
        return util.FetchRangeSetting(key)

    def CopyCoordinates(self, itemID):
        ball = self.michelle.GetBall(itemID)
        if ball:
            blue.pyos.SetClipboardData(str((ball.x, ball.y, ball.z)))

    def RepairItems(self, items):
        if items is None or len(items) < 1:
            return
        wnd = form.RepairShopWindow.Open()
        if wnd and not wnd.destroyed:
            wnd.DisplayRepairQuote(items)

    def AnchorOrbital(self, itemID):
        posMgr = util.Moniker('posMgr', session.solarsystemid)
        posMgr.AnchorOrbital(itemID)

    def UnanchorOrbital(self, itemID):
        posMgr = util.Moniker('posMgr', session.solarsystemid)
        posMgr.UnanchorOrbital(itemID)

    def ConfigureOrbital(self, item):
        sm.GetService('planetUI').OpenConfigureWindow(item)

    def CompleteOrbitalStateChange(self, itemID):
        posMgr = util.Moniker('posMgr', session.solarsystemid)
        posMgr.CompleteOrbitalStateChange(itemID)

    def GMUpgradeOrbital(self, itemID):
        posMgr = util.Moniker('posMgr', session.solarsystemid)
        posMgr.GMUpgradeOrbital(itemID)

    def TakeOrbitalOwnership(self, itemID, planetID):
        registry = moniker.GetPlanetOrbitalRegistry(session.solarsystemid)
        registry.GMChangeSpaceObjectOwner(itemID, session.corpid)

    def GetCloseAndTryCommand(self, itemID, cmdMethod, args, interactionRange = 2500):
        if not sm.GetService('machoNet').GetGlobalConfig().get('newAutoNavigationKillSwitch', False):
            sm.GetService('autoPilot').NavigateSystemTo(itemID, interactionRange, cmdMethod, *args)
        else:
            self.GetCloseAndTryCommand_Old(itemID, cmdMethod, args, interactionRange)

    def GetCloseAndTryCommand_Old(self, id, cmdMethod, args, interactionRange = 2500):
        bp = sm.StartService('michelle').GetBallpark()
        if not bp:
            return
        ball = bp.GetBall(id)
        ball.GetVectorAt(blue.os.GetSimTime())
        if ball.surfaceDist >= const.minWarpDistance:
            sm.GetService('autoPilot').WarpAndTryCommand(id, cmdMethod, args, interactionRange=interactionRange)
        elif ball.surfaceDist > interactionRange:
            sm.GetService('autoPilot').ApproachAndTryCommand(id, cmdMethod, args, interactionRange=interactionRange)
        else:
            cmdMethod(*args)

    def ReconnectToDrones(self):
        ret = {}
        bp = sm.GetService('michelle').GetBallpark()
        if not bp:
            return ret
        shipBall = bp.GetBall(session.shipid)
        if not shipBall:
            return ret
        drones = sm.GetService('michelle').GetDrones()
        droneCandidates = []
        for ball, slimItem in bp.GetBallsAndItems():
            if slimItem and slimItem.categoryID == const.categoryDrone:
                if slimItem.ownerID == session.charid and ball.id not in drones:
                    droneCandidates.append(ball.id)
                    if len(droneCandidates) >= const.MAX_DRONE_RECONNECTS:
                        break

        if droneCandidates:
            eve.Message('CustomNotify', {'notify': localization.GetByLabel('UI/Messages/ReconnectFoundDrones')})
            self._ReconnectToDroneCandidates(droneCandidates)
        else:
            eve.Message('CustomNotify', {'notify': localization.GetByLabel('UI/Messages/ReconnectFoundNoDrones')})
        return ret

    def _ReconnectToDroneCandidates(self, droneCandidates):
        ret = {}
        if droneCandidates:
            entity = moniker.GetEntityAccess()
            if entity:

                def SpewError(*args):
                    raise UserError(*args)

                ret = entity.CmdReconnectToDrones(droneCandidates)
                for errStr, dicty in ret.iteritems():
                    uthread.new(SpewError, errStr, dicty)
                    blue.pyos.synchro.Sleep(5000)


class ActionMenu(uicls.Container):
    __guid__ = 'xtriui.ActionMenu'

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        self.actionMenuOptions = {'UI/Commands/ShowInfo': ('ui_44_32_24', 0, 0, 0, 0),
         'UI/Inflight/LockTarget': ('ui_44_32_17', 0, 0, 0, 0),
         'UI/Inflight/UnlockTarget': ('ui_44_32_17', 0, 0, 0, 1),
         'UI/Inflight/ApproachObject': ('ui_44_32_23', 0, 0, 0, 0),
         'UI/Inflight/LookAtObject': ('ui_44_32_20', 0, 0, 0, 0),
         'UI/Inflight/ResetCamera': ('ui_44_32_20', 0, 0, 0, 1),
         'UI/Inflight/Submenus/KeepAtRange': ('ui_44_32_22', 0, 0, 1, 0),
         'UI/Inflight/OrbitObject': ('ui_44_32_21', 0, 0, 1, 0),
         'UI/Inflight/DockInStation': ('ui_44_32_9', 0, 0, 0, 0),
         'UI/Chat/StartConversation': ('ui_44_32_33', 0, 0, 0, 0),
         'UI/Commands/OpenCargo': ('ui_44_32_35', 0, 0, 0, 0),
         'UI/Commands/OpenMyCargo': ('ui_44_32_35', 0, 0, 0, 0),
         'UI/PI/Common/AccessCustomOffice': ('ui_44_32_35', 0, 0, 0, 0),
         'UI/Inflight/StopMyShip': ('ui_44_32_38', 0, 0, 0, 0),
         'UI/Inflight/StopMyCapsule': ('ui_44_32_38', 0, 0, 0, 0),
         'UI/Inflight/ActivateAutopilot': ('ui_44_32_12', 0, 0, 0, 0),
         'UI/Inflight/DeactivateAutopilot': ('ui_44_32_12', 0, 0, 0, 1),
         'UI/Inflight/EjectFromShip': ('ui_44_32_36', 0, 0, 0, 0),
         'UI/Inflight/SelfDestructShipOrPod': ('ui_44_32_37', 0, 0, 0, 0),
         'UI/Inflight/BoardShip': ('ui_44_32_40', 0, 0, 0, 0),
         'UI/Inflight/Jump': ('ui_44_32_39', 0, 0, 0, 0),
         'UI/Inflight/EnterWormhole': ('ui_44_32_39', 0, 0, 0, 0),
         'UI/Inflight/ActivateGate': ('ui_44_32_39', 0, 0, 0, 0),
         'UI/Drones/ScoopDroneToBay': ('ui_44_32_1', 0, 0, 0, 0),
         'UI/Commands/ReadNews': ('ui_44_32_47', 0, 0, 0, 0)}
        self.lastActionSerial = None
        self.sr.actionTimer = None
        self.itemID = None
        self.width = 134
        self.height = 134
        self.pickRadius = -1
        self.oldx = self.oldy = None
        uicore.event.RegisterForTriuiEvents(uiconst.UI_MOUSEUP, self.OnGlobalUp)
        self.mouseMoveCookie = uicore.event.RegisterForTriuiEvents(uiconst.UI_MOUSEMOVE, self.OnGlobalMove)

    def Load(self, slimItem, centerItem = None, setposition = 1):
        if not (uicore.uilib.leftbtn or uicore.uilib.midbtn):
            return
        actions = sm.StartService('menu').CelestialMenu(slimItem.itemID, slimItem=slimItem, ignoreTypeCheck=1)
        reasonsWhyNotAvailable = getattr(actions, 'reasonsWhyNotAvailable', {})
        if not (uicore.uilib.leftbtn or uicore.uilib.midbtn):
            return
        self.itemID = slimItem.itemID
        warptoLabel = sm.GetService('menu').DefaultWarpToLabel()[0]
        warpops = {warptoLabel: ('ui_44_32_18', 0, 0, 1, 0)}
        self.actionMenuOptions.update(warpops)
        serial = ''
        valid = {}
        inactive = None
        for each in actions:
            if each:
                if isinstance(each[0], tuple):
                    name = each[0][0]
                else:
                    name = each[0]
                if name in self.actionMenuOptions:
                    valid[name] = each
                    if type(each[1]) not in (str, unicode):
                        serial += '%s_' % name

        if not (uicore.uilib.leftbtn or uicore.uilib.midbtn):
            return
        if serial != self.lastActionSerial:
            uix.Flush(self)
            i = 0
            order = ['UI/Commands/ShowInfo',
             ['UI/Inflight/LockTarget', 'UI/Inflight/UnlockTarget'],
             ['UI/Inflight/ApproachObject', warptoLabel],
             'UI/Inflight/OrbitObject',
             'UI/Inflight/Submenus/KeepAtRange']
            default = [None, ['UI/Inflight/LookAtObject', 'UI/Inflight/ResetCamera'], None]
            lookAtString = 'UI/Inflight/LookAtObject'
            resetCameraString = 'UI/Inflight/ResetCamera'
            openCargoString = 'UI/Commands/OpenCargo'
            groups = {const.groupStation: [None, [lookAtString, resetCameraString], 'UI/Inflight/DockInStation'],
             const.groupCargoContainer: [None, [lookAtString, resetCameraString], openCargoString],
             const.groupMissionContainer: [None, [lookAtString, resetCameraString], openCargoString],
             const.groupSecureCargoContainer: [None, [lookAtString, resetCameraString], openCargoString],
             const.groupAuditLogSecureContainer: [None, [lookAtString, resetCameraString], openCargoString],
             const.groupFreightContainer: [None, [lookAtString, resetCameraString], openCargoString],
             const.groupSpawnContainer: [None, [lookAtString, resetCameraString], openCargoString],
             const.groupDeadspaceOverseersBelongings: [None, [lookAtString, resetCameraString], openCargoString],
             const.groupWreck: [None, [lookAtString, resetCameraString], openCargoString],
             const.groupStargate: [None, [lookAtString, resetCameraString], 'UI/Inflight/Jump'],
             const.groupWormhole: [None, [lookAtString, resetCameraString], 'UI/Inflight/EnterWormhole'],
             const.groupWarpGate: [None, [lookAtString, resetCameraString], 'UI/Inflight/ActivateGate'],
             const.groupBillboard: [None, [lookAtString, resetCameraString], 'UI/Commands/ReadNews'],
             const.groupAgentsinSpace: ['UI/Chat/StartConversation', [lookAtString, resetCameraString], None],
             const.groupDestructibleAgentsInSpace: ['UI/Chat/StartConversation', [lookAtString, resetCameraString], None],
             const.groupPlanetaryCustomsOffices: [None, [lookAtString, resetCameraString], 'UI/PI/Common/AccessCustomOffice']}
            categories = {const.categoryShip: ['UI/Chat/StartConversation', [lookAtString, resetCameraString], 'UI/Inflight/BoardShip'],
             const.categoryDrone: [None, [lookAtString, resetCameraString], 'UI/Drones/ScoopDroneToBay']}
            if slimItem.itemID == session.shipid:
                order = ['UI/Commands/ShowInfo',
                 'UI/Inflight/EjectFromShip',
                 ['UI/Inflight/StopMyShip', 'UI/Inflight/StopMyCapsule'],
                 ['UI/Inflight/ActivateAutopilot', 'UI/Inflight/DeactivateAutopilot'],
                 [lookAtString, resetCameraString]]
            elif slimItem.groupID in groups:
                order += groups[slimItem.groupID]
            elif slimItem.categoryID in categories:
                order += categories[slimItem.categoryID]
            else:
                order += default
            step = 360.0 / 8
            rad = 48
            angle = 180.0
            for actionName in order:
                if actionName is None:
                    angle += step
                    i += 1
                    continue
                if type(actionName) == list:
                    action = None
                    for each in actionName:
                        tryaction = valid.get(each, None)
                        if tryaction and type(tryaction[1]) not in (str, unicode):
                            actionName = each
                            action = tryaction
                            break

                    if action is None:
                        actionName = actionName[0]
                        if actionName in valid:
                            action = valid.get(actionName)
                        elif actionName in reasonsWhyNotAvailable:
                            action = (actionName, reasonsWhyNotAvailable.get(actionName))
                        else:
                            action = (actionName, localization.GetByLabel('UI/Menusvc/MenuHints/NoReasonGiven'))
                elif actionName in valid:
                    action = valid.get(actionName)
                elif actionName in reasonsWhyNotAvailable:
                    action = (actionName, reasonsWhyNotAvailable.get(actionName))
                else:
                    action = (actionName, localization.GetByLabel('UI/Menusvc/MenuHints/NoReasonGiven'))
                disabled = type(action[1]) in (str, unicode)
                props = self.actionMenuOptions[actionName]
                btnpar = uicls.Container(parent=self, align=uiconst.TOPLEFT, width=40, height=40, state=uiconst.UI_NORMAL)
                btnpar.left = int(rad * math.cos(angle * math.pi / 180.0)) + (self.width - btnpar.width) / 2
                btnpar.top = int(rad * math.sin(angle * math.pi / 180.0)) + (self.height - btnpar.height) / 2
                btn = uicls.Sprite(parent=btnpar, name='hudBtn', pos=(0, 0, 40, 40), state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/Shared/actionMenuBtn.png')
                btnpar.actionID = actionName
                btnpar.name = actionName
                btnpar.action = action
                btnpar.itemIDs = [slimItem.itemID]
                btnpar.killsub = props[3]
                btnpar.pickRadius = -1
                icon = uicls.Icon(icon=props[0], parent=btnpar, pos=(4, 4, 0, 0), align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, idx=0)
                if disabled:
                    icon.color.a = 0.5
                    btn.color.a = 0.1
                if props[4]:
                    icon = uicls.Icon(icon='ui_44_32_8', parent=btnpar, pos=(5, 5, 0, 0), align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, idx=0)
                angle += step
                i += 1

            self.lastActionSerial = serial
            if self.sr.actionTimer is None:
                self.sr.actionTimer = base.AutoTimer(1000, self.Load, slimItem, None, 0)
        if centerItem:
            self.left = max(0, min(uicore.desktop.width - self.width, centerItem.absoluteLeft - (self.width - centerItem.width) / 2))
            self.top = max(0, min(uicore.desktop.height - self.height, centerItem.absoluteTop - (self.height - centerItem.height) / 2))
        elif setposition:
            self.left = max(0, min(uicore.desktop.width - self.width, uicore.uilib.x - self.width / 2))
            self.top = max(0, min(uicore.desktop.height - self.height, uicore.uilib.y - self.height / 2))

    def OnGlobalUp(self, *args):
        if not self or self.destroyed:
            return
        if self.itemID and blue.os.TimeDiffInMs(self.expandTime, blue.os.GetWallclockTime()) < 100:
            sm.StartService('state').SetState(self.itemID, state.selected, 1)
        self.sr.actionTimer = None
        self.sr.updateAngle = None
        mo = uicore.uilib.mouseOver
        self.state = uiconst.UI_HIDDEN
        self.lastActionSerial = None
        if mo in self.children:
            uthread.new(self.OnBtnparClicked, mo)
        else:
            uicore.layer.menu.Flush()
        if not self.destroyed:
            uicore.event.UnregisterForTriuiEvents(self.mouseMoveCookie)

    def OnBtnparClicked(self, btnpar):
        sm.StartService('ui').StopBlink(btnpar)
        if btnpar.destroyed:
            uicore.layer.menu.Flush()
            return
        if btnpar.killsub and isinstance(btnpar.action[1], list):
            uthread.new(btnpar.action[1][0][2][0][0], btnpar.action[1][0][2][0][1][0])
            uicore.layer.menu.Flush()
            return
        if isinstance(btnpar.action[1], basestring):
            sm.StartService('gameui').Say(btnpar.action[1])
        else:
            try:
                apply(*btnpar.action[1:])
            except Exception as e:
                log.LogError(e, 'Failed executing action:', btnpar.action)
                log.LogException()
                sys.exc_clear()

        uicore.layer.menu.Flush()

    def OnGlobalMove(self, *args):
        mo = uicore.uilib.mouseOver
        lib = uicore.uilib
        for c in self.children:
            c.opacity = 1.0

        if mo in self.children:
            mo.opacity = 0.7
        if not lib.leftbtn:
            self.oldx = self.oldy = None
            return
        if self.oldx and self.oldy:
            dx, dy = self.oldx - lib.x, self.oldy - lib.y
            camera = sm.GetService('sceneManager').GetRegisteredCamera('default')
            if mo.name == 'blocker' and not lib.rightbtn:
                fov = camera.fieldOfView
                camera.OrbitParent(dx * fov * 0.2, -dy * fov * 0.2)
            elif lib.rightbtn:
                uicore.layer.inflight.zoomlooking = 1
                uicore.layer.menu.Flush()
        if hasattr(self, 'oldx') and hasattr(self, 'oldy'):
            self.oldx, self.oldy = lib.x, lib.y
        return 1

    def OnMouseWheel(self, *args):
        camera = sm.GetService('sceneManager').GetRegisteredCamera('default')
        if camera.__typename__ == 'EveCamera':
            camera.Dolly(uicore.uilib.dz * 0.001 * abs(camera.translationFromParent))
            camera.translationFromParent = sm.StartService('camera').CheckTranslationFromParent(camera.translationFromParent)
        return 1


class Action(uicls.Container):
    __guid__ = 'xtriui.Action'
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        self.actionID = None
        self.disabled = attributes.get('disabled', False)
        self.Prepare_(icon=attributes.icon)

    def Prepare_(self, icon = None):
        self.icon = uicls.Icon(parent=self, align=uiconst.TOALL, icon=icon, state=uiconst.UI_DISABLED)
        self.sr.fill = uicls.Fill(parent=self, state=uiconst.UI_HIDDEN)
        if self.disabled:
            frameColor = (1.0, 1.0, 1.0, 0.25)
        else:
            frameColor = (1.0, 1.0, 1.0, 0.5)
        self.frame = uicls.Frame(parent=self, color=frameColor)

    def PrepareHint(self, fromWhere = ''):
        if self and not self.destroyed:
            shortcutString = ''
            reasonString = ''
            distString = ''
            labelPath = 'UI/Menusvc/MenuHints/SelectedItemAction'
            keywords = {}
            if isinstance(self.action[1], basestring):
                labelPath = 'UI/Menusvc/MenuHints/SelectedItemActionWithReason'
                reasonString = self.action[1]
                if self.actionID == 'UI/Inflight/WarpToWithinDistance':
                    keywords['distance'] = sm.GetService('menu').GetDefaultActionDistance('WarpTo')
            else:
                if isinstance(self.action[0], uiutil.MenuLabel):
                    actionNamePath, keywords = self.action[0]
                if self.actionID in ('UI/Inflight/OrbitObject', 'UI/Inflight/Submenus/KeepAtRange'):
                    labelPath = 'UI/Menusvc/MenuHints/SelectedItemActionWithDist'
                    key = sm.GetService('menu').GetGlobalActiveItemKeyName(actionNamePath)
                    current = sm.GetService('menu').GetDefaultActionDistance(key)
                    if current is not None:
                        distString = util.FmtDist(current)
                    else:
                        distString = localization.GetByLabel('UI/Menusvc/MenuHints/NoDistanceSet')
            if hasattr(self, 'cmdName'):
                shortcutString = uicore.cmd.GetShortcutStringByFuncName(self.cmdName)
                labelPath = '%s%s' % (labelPath, 'WithShortcut')
            actionName = localization.GetByLabel(self.actionID, **keywords)
            hint = localization.GetByLabel(labelPath, actionName=actionName, reasonString=reasonString, distanceString=distString, shortcutString=shortcutString)
            self.sr.hint = hint
            return self.sr.hint

    def GetHint(self):
        return self.PrepareHint()

    def GetMenu(self):
        m = []
        label = ''
        key = sm.GetService('menu').GetGlobalActiveItemKeyName(self.actionID)
        if key == 'Orbit':
            label = uiutil.MenuLabel('UI/Inflight/SetDefaultOrbitDistance', {'typeName': self.actionID})
        elif key == 'KeepAtRange':
            label = uiutil.MenuLabel('UI/Inflight/SetDefaultKeepAtRangeDistance', {'typeName': self.actionID})
        elif key == 'WarpTo':
            label = uiutil.MenuLabel('UI/Inflight/SetDefaultWarpWithinDistance', {'typeName': self.actionID})
        if len(label) > 0:
            m.append((label, self.SetDefaultDist, (key,)))
        return m

    def OnMouseEnter(self, *args):
        if self.sr.Get('fill', None):
            if 'EngageTarget' in self.action[0][0]:
                crimewatchSvc = sm.GetService('crimewatchSvc')
                droneIDs = self.action[2][1]
                targetID = sm.GetService('target').GetActiveTargetID()
                requiredSafetyLevel = crimewatchSvc.GetRequiredSafetyLevelForEngagingDrones(droneIDs, targetID)
                if crimewatchSvc.CheckUnsafe(requiredSafetyLevel):
                    if requiredSafetyLevel == const.shipSafetyLevelNone:
                        color = crimewatchConst.Colors.Criminal.GetRGBA()
                    else:
                        color = crimewatchConst.Colors.Suspect.GetRGBA()
                    self.sr.fill.color.SetRGB(*color[:3])
            self.sr.fill.state = uiconst.UI_DISABLED
            self.sr.fill.color.a = 0.25

    def OnMouseExit(self, *args):
        if self.sr.Get('fill', None):
            self.sr.fill.color.SetRGBA(1, 1, 1, 1)
            self.sr.fill.state = uiconst.UI_HIDDEN

    def OnMouseDown(self, *args):
        if self.sr.Get('fill', None):
            self.sr.fill.color.a = 0.5

    def OnMouseUp(self, *args):
        if self.sr.Get('fill', None):
            self.sr.fill.color.a = 0.25

    def SetDefaultDist(self, key):
        if not key:
            return
        minDist, maxDist = {'Orbit': (500, 1000000),
         'KeepAtRange': (50, 1000000),
         'WarpTo': (const.minWarpEndDistance, const.maxWarpEndDistance)}.get(key, (500, 1000000))
        current = sm.GetService('menu').GetDefaultActionDistance(key)
        current = current or ''
        fromDist = util.FmtAmt(minDist)
        toDist = util.FmtAmt(maxDist)
        if key == 'KeepAtRange':
            hint = localization.GetByLabel('UI/Inflight/SetDefaultKeepAtRangeDistanceHint', fromDist=fromDist, toDist=toDist)
            caption = localization.GetByLabel('UI/Inflight/SetDefaultKeepAtRangeDistance')
        elif key == 'Orbit':
            hint = localization.GetByLabel('UI/Inflight/SetDefaultOrbitDistanceHint', fromDist=fromDist, toDist=toDist)
            caption = localization.GetByLabel('UI/Inflight/SetDefaultOrbitDistance')
        elif key == 'WarpTo':
            hint = localization.GetByLabel('UI/Inflight/SetDefaultWarpWithinDistanceHint', fromDist=fromDist, toDist=toDist)
            caption = localization.GetByLabel('UI/Inflight/SetDefaultWarpWithinDistance')
        else:
            hint = ''
            caption = ''
        r = uix.QtyPopup(maxvalue=maxDist, minvalue=minDist, setvalue=current, hint=hint, caption=caption, label=None, digits=0)
        if r:
            newRange = max(minDist, min(maxDist, r['qty']))
            util.UpdateRangeSetting(key, newRange)

    def OnMouseMove(self, *args):
        self.PrepareHint()

    def OnClick(self, *args):
        sm.StartService('ui').StopBlink(self)
        if self.destroyed:
            uicore.layer.menu.Flush()
            return
        if self.killsub and isinstance(self.action[1], list):
            uthread.new(self.action[1][0][2][0][0], self.action[1][0][2][0][1][0])
            uicore.layer.menu.Flush()
            return
        if isinstance(self.action[1], basestring):
            sm.StartService('gameui').Say(self.action[1])
        else:
            try:
                apply(*self.action[1:3])
            except Exception as e:
                log.LogError(e, 'Failed executing action:', self.action)
                log.LogException()
                sys.exc_clear()

        uicore.layer.menu.Flush()


class MenuList(list):
    reasonsWhyNotAvailable = {}