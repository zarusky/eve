#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/ui/inflight/shipui.py
import sys
import blue
import telemetry
import uthread
import uix
import uiutil
import mathUtil
import xtriui
import form
import trinity
import util
import base
import math
import log
import lg
import destiny
import uicls
import uiconst
import localization
import localizationUtil
import invCtrl
import state
import shipSafetyButton
ICONSIZE = 32
CELLCOLOR = (0.9375, 0.3515625, 0.1953125)
groups = ('hardpoints', 'systems', 'structure')
LOW_HEAT_GAUGE_TEXTURES = ['res:/UI/Texture/classes/ShipUI/lowHeat_0.png',
 'res:/UI/Texture/classes/ShipUI/lowHeat_1.png',
 'res:/UI/Texture/classes/ShipUI/lowHeat_2.png',
 'res:/UI/Texture/classes/ShipUI/lowHeat_3.png',
 'res:/UI/Texture/classes/ShipUI/lowHeat_4.png']
MED_HEAT_GAUGE_TEXTURES = ['res:/UI/Texture/classes/ShipUI/medHeat_0.png',
 'res:/UI/Texture/classes/ShipUI/medHeat_1.png',
 'res:/UI/Texture/classes/ShipUI/medHeat_2.png',
 'res:/UI/Texture/classes/ShipUI/medHeat_3.png',
 'res:/UI/Texture/classes/ShipUI/medHeat_4.png']
HI_HEAT_GAUGE_TEXTURES = ['res:/UI/Texture/classes/ShipUI/hiHeat_0.png',
 'res:/UI/Texture/classes/ShipUI/hiHeat_1.png',
 'res:/UI/Texture/classes/ShipUI/hiHeat_2.png',
 'res:/UI/Texture/classes/ShipUI/hiHeat_3.png',
 'res:/UI/Texture/classes/ShipUI/hiHeat_4.png']

class ShipUI(uicls.LayerCore):
    __guid__ = 'form.ShipUI'
    __notifyevents__ = ['OnShipScanCompleted',
     'OnJamStart',
     'OnJamEnd',
     'OnCargoScanComplete',
     'ProcessShipEffect',
     'DoBallRemove',
     'DoBallClear',
     'OnAutoPilotOn',
     'OnAutoPilotOff',
     'OnAttributes',
     'ProcessRookieStateChange',
     'OnSetDevice',
     'OnMapShortcut',
     'OnRestoreDefaultShortcuts',
     'OnTacticalOverlayChange',
     'OnAssumeStructureControl',
     'OnRelinquishStructureControl',
     'OnWeaponGroupsChanged',
     'OnRefreshModuleBanks',
     'OnUIColorsChanged',
     'OnUIRefresh',
     'OnUIScalingChange',
     'ProcessActiveShipChanged',
     'ProcessPendingOverloadUpdate',
     'OnSafeLogoffTimerStarted',
     'OnSafeLogoffActivated',
     'OnSafeLogoffAborted',
     'OnSafeLogoffFailed']

    def ApplyAttributes(self, attributes):
        self.setupShipTasklet = None
        uicls.LayerCore.ApplyAttributes(self, attributes)
        self.ResetSelf()

    def OnUIColorsChanged(self, *args):
        if self.sr.wnd:
            mainShape = uiutil.GetChild(self.sr.wnd, 'shipuiMainShape')
            color, bgColor, comp, compsub = sm.GetService('window').GetWindowColors()
            r, g, b, a = color
            mainShape.SetRGB(r, g, b)

    def OnSetDevice(self):
        self.UpdatePosition()

    def OnUIScalingChange(self, *args):
        self.UpdatePosition()

    def OnUIRefresh(self):
        self.CloseView(recreate=False)
        self.OpenView()

    @telemetry.ZONE_METHOD
    def ResetSelf(self):
        self.powerCells = None
        self.sr.wnd = None
        self.sr.speedtimer = None
        self.sr.capacitortimer = None
        self.sr.cargotimer = None
        self.sr.modeTimer = None
        self.sr.gaugetimer = None
        self.sr.gaugeReadout = None
        self.sr.safetyButton = None
        self.sr.selectedcateg = 0
        self.sr.pendingreloads = []
        self.sr.reloadsByID = {}
        self.sr.rampTimers = {}
        self.sr.main = None
        self.sr.powercore = None
        self.sr.speedNeedle = None
        self.sr.speedReadout = None
        self.sr.autopilotBtn = None
        self.sr.tacticalBtn = None
        self.sr.powerblink = None
        self.sr.speed_ro = None
        self.sr.shield_ro = None
        self.sr.armor_ro = None
        self.sr.powercore_ro = None
        self.sr.structure_ro = None
        self.sr.module_ro = None
        self.sr.currentModeHeader = None
        self.sr.hudButtons = None
        self.myHarpointFlags = []
        self.capacity = None
        self.shieldcapacity = None
        self.lastsetcapacitor = None
        self.lastStructure = None
        self.lastArmor = None
        self.lastShield = None
        self.lastLowHeat = None
        self.lastMedHeat = None
        self.lastHiHeat = None
        self.wantedspeed = None
        self.capacitorDone = 0
        self.sr.modules = {}
        self.ball = None
        self.shipuiReady = False
        self.initing = None
        self.speedInited = 0
        self.jammers = {}
        self.speedupdatetimer = None
        self.genericupdatetimer = None
        self.groupAllIcon = None
        self.assumingcontrol = False
        self.assumingdelay = None
        self.checkingoverloadrackstate = 0
        self.totalSlaves = 0
        self.timerNames = {'propulsion': localization.GetByLabel('UI/Inflight/Scrambling'),
         'electronic': localization.GetByLabel('UI/Inflight/Jamming'),
         'unknown': localization.GetByLabel('UI/Inflight/Miscellaneous')}
        self.updatingGauges = False
        self.recreatingView = False
        if self.setupShipTasklet is not None:
            self.setupShipTasklet.kill()
        self.setupShipTasklet = None
        self.logoffTimer = None
        self.Flush()

    def CheckPendingReloads(self):
        if self.sr.pendingreloads:
            rl = self.sr.pendingreloads[0]
            while rl in self.sr.pendingreloads:
                self.sr.pendingreloads.remove(rl)

            module = self.GetModule(rl)
            if module:
                module.AutoReload()

    def CheckSession(self, change):
        if sm.GetService('autoPilot').GetState():
            self.OnAutoPilotOn()
        else:
            self.OnAutoPilotOff()

    @telemetry.ZONE_METHOD
    def UpdatePosition(self):
        self.sr.wnd.height = 195
        self.sr.wnd.width = uicore.desktop.width
        wndLeft = settings.char.windows.Get('shipuialignleft', 0)
        maxRight, minLeft = self.GetShipuiOffsetMinMax()
        if wndLeft > maxRight or wndLeft < minLeft:
            settings.char.windows.Set('shipuialignleft', 0)
            wndLeft = 0
        self.sr.wnd.left = wndLeft
        self.ewarCont.left = wndLeft
        self.sr.wnd.align = uiconst.ABSOLUTE
        if not settings.user.ui.Get('shipuialigntop', 0):
            self.sr.wnd.top = uicore.desktop.height - self.sr.wnd.height
            self.ewarCont.SetAlign(uiconst.CENTERBOTTOM)
        else:
            self.sr.wnd.top = 0
            self.ewarCont.SetAlign(uiconst.CENTERTOP)
        if self.sr.gaugeReadout:
            self.sr.gaugeReadout.top = self.GetGaugeTop()
        if settings.user.ui.Get('shipuialigntop', 0):
            self.sr.indicationContainer.top = 230
        else:
            self.sr.indicationContainer.top = -78

    def GetGaugeTop(self, *args):
        return 55

    def GetShipLayerAbsolutes(self):
        d = uicore.desktop
        wnd = uicore.layer.shipui
        if wnd and not wnd.state == uiconst.UI_HIDDEN:
            pl, pt, pw, ph = wnd.GetAbsolute()
        else:
            pl, pt, pw, ph = d.GetAbsolute()
        return (wnd,
         pl,
         pt,
         pw,
         ph)

    def GetShipUI(self, obj):
        return self.sr.wnd

    def OnShipMouseDown(self, wnd, btn, *args):
        if btn != 0:
            return
        self.dragging = True
        wnd = self.GetShipUI(wnd)
        if not wnd:
            return
        l, t, w, h = wnd.GetAbsolute()
        self.grab = [uicore.uilib.x - l, uicore.uilib.y - t]
        uthread.new(self.BeginDrag, wnd)

    def GetShipuiOffsetMinMax(self, *args):
        maxRight = uicore.desktop.width / 2 - self.sr.slotsContainer.width / 2
        minLeft = -(uicore.desktop.width / 2 - 180)
        return (maxRight, minLeft)

    def OnShipMouseUp(self, wnd, btn, *args):
        if btn != 0:
            return
        wnd = self.GetShipUI(wnd)
        if wnd:
            wndLeft = settings.char.windows.Set('shipuialignleft', wnd.left)
        sm.StartService('ui').ForceCursorUpdate()
        self.dragging = False

    def BeginDrag(self, wnd):
        wnd = self.GetShipUI(wnd)
        while not wnd.destroyed and getattr(self, 'dragging', 0):
            uicore.uilib.SetCursor(uiconst.UICURSOR_DIVIDERADJUST)
            maxRight, minLeft = self.GetShipuiOffsetMinMax()
            grabLocation = uicore.uilib.x - self.grab[0]
            wnd.left = max(minLeft, min(maxRight, grabLocation))
            self.ewarCont.left = wnd.left
            blue.pyos.synchro.SleepWallclock(1)

    @telemetry.ZONE_METHOD
    def OnOpenView(self):
        self.ResetSelf()
        self.state = uiconst.UI_HIDDEN
        self.sr.wnd = ShipUIContainer(parent=self)
        top = 177
        if settings.user.ui.Get('shipuialigntop', 0):
            top -= 6
        self.ewarCont = EwarUIContainer(parent=self, align=uiconst.CENTERBOTTOM, top=top, height=50, width=480)
        self.sr.timers = uicls.Container(name='timers', parent=self.sr.wnd, width=120, height=450, align=uiconst.CENTERBOTTOM, top=240)
        self.sr.mainContainer = uiutil.GetChild(self.sr.wnd, 'mainContainer')
        self.sr.subContainer = uiutil.GetChild(self.sr.wnd, 'subContainer')
        self.sr.slotsContainer = uiutil.GetChild(self.sr.wnd, 'slotsContainer')
        if settings.user.ui.Get('shipuialigntop', 0):
            top = 200
        else:
            top = -10
        self.sr.indicationContainer = uicls.Container(parent=self.sr.wnd, name='indicationContainer', align=uiconst.CENTERTOP, pos=(0,
         top,
         400,
         50))
        self.sr.safetyButton = shipSafetyButton.SafetyButton(parent=self.sr.mainContainer, left=50, top=56)
        showReadout = settings.user.ui.Get('showReadout', 0)
        if showReadout:
            self.InitGaugeReadout()
        self.sr.powercore = uiutil.GetChild(self.sr.wnd, 'powercore')
        self.sr.powercore.OnMouseDown = (self.OnShipMouseDown, self.sr.powercore)
        self.sr.powercore.OnMouseUp = (self.OnShipMouseUp, self.sr.powercore)
        self.sr.powercore.GetMenu = self.GetMenu
        mExpanded = settings.user.ui.Get('modulesExpanded', 1)
        self.sr.expandbtnleft = uiutil.GetChild(self.sr.wnd, 'expandBtnLeft')
        self.sr.expandbtnleft.OnClick = (self.ClickExpand, self.sr.expandbtnleft)
        self.sr.expandbtnleft.OnMouseDown = (self.OnExpandDown, self.sr.expandbtnleft)
        self.sr.expandbtnleft.OnMouseUp = (self.OnExpandUp, self.sr.expandbtnleft)
        self.sr.expandbtnleft.side = -1
        self.sr.expandbtnleft.hint = [localization.GetByLabel('UI/Inflight/ShowButtons'), localization.GetByLabel('UI/Inflight/HideButtons')][mExpanded]
        self.sr.expandbtnright = uiutil.GetChild(self.sr.wnd, 'expandBtnRight')
        self.sr.expandbtnright.OnClick = (self.ClickExpand, self.sr.expandbtnright)
        self.sr.expandbtnright.side = 1
        self.sr.expandbtnright.OnMouseDown = (self.OnExpandDown, self.sr.expandbtnright)
        self.sr.expandbtnright.OnMouseUp = (self.OnExpandUp, self.sr.expandbtnright)
        self.sr.expandbtnright.hint = [localization.GetByLabel('UI/Inflight/ShowModules'), localization.GetByLabel('UI/Inflight/HideModules')][mExpanded]
        optionsCont = self.sr.wnd.optionsCont
        self.settingsMenu = uicls.UtilMenu(menuAlign=uiconst.BOTTOMLEFT, parent=optionsCont, align=uiconst.TOPLEFT, GetUtilMenu=self.GetHUDOptionMenu, pos=(0, 0, 16, 16), texturePath='res:/UI/Texture/Icons/73_16_50.png', hint=localization.GetByLabel('UI/Inflight/Options'))
        underMain = uiutil.GetChild(self.sr.wnd, 'underMain')
        for typeName, deg in [('low', -22.5), ('med', -90.0), ('hi', -157.5)]:
            miniGauge = uicls.Transform(parent=underMain, name='%s_miniGauge' % typeName, pos=(-1, 0, 83, 12), align=uiconst.CENTER, rotation=mathUtil.DegToRad(deg), idx=0)
            needle = uicls.Sprite(parent=miniGauge, name='needle', pos=(0, 0, 12, 12), align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/ShipUI/heatGaugeNeedle.png')
            self.sr.Set('%sHeatGauge' % typeName, miniGauge)
            underlay = uiutil.FindChild(self.sr.wnd, 'heat%sUnderlay' % typeName.capitalize())
            if underlay:
                underlay.heatTextureIndex = None
                self.sr.Set('heat%sUnderlay' % typeName.capitalize(), underlay)

        self.sr.heatPick = uiutil.GetChild(self.sr.wnd, 'heatPick')
        self.structureGauge = uicls.Sprite(parent=underMain, pos=(0, 0, 148, 148), texturePath='res:/UI/Texture/classes/ShipUI/gauge3.png', align=uiconst.CENTER, spriteEffect=trinity.TR2_SFX_MODULATE, shadowOffset=(0, 1), pickRadius=54, name='structureGauge', glowColor=(0.25, 0.25, 0.25, 1.0), glowExpand=1.0)
        self.structureGauge.SetSecondaryTexturePath('res:/UI/Texture/classes/ShipUI/gaugeFill.png')
        self.structureGauge.textureSecondary.useTransform = True
        self.structureGauge.textureSecondary.rotation = 0.0
        self.armorGauge = uicls.Sprite(parent=underMain, pos=(0, 0, 148, 148), texturePath='res:/UI/Texture/classes/ShipUI/gauge2.png', align=uiconst.CENTER, spriteEffect=trinity.TR2_SFX_MODULATE, shadowOffset=(0, 1), pickRadius=64, name='armorGauge', glowColor=(0.25, 0.25, 0.25, 1.0), glowExpand=1.0)
        self.armorGauge.SetSecondaryTexturePath('res:/UI/Texture/classes/ShipUI/gaugeFill.png')
        self.armorGauge.textureSecondary.useTransform = True
        self.armorGauge.textureSecondary.rotation = 0.0
        self.shieldGauge = uicls.Sprite(parent=underMain, pos=(0, 0, 148, 148), texturePath='res:/UI/Texture/classes/ShipUI/gauge1.png', align=uiconst.CENTER, spriteEffect=trinity.TR2_SFX_MODULATE, shadowOffset=(0, 1), pickRadius=74, name='shieldGauge', glowColor=(0.25, 0.25, 0.25, 1.0), glowExpand=1.0)
        self.shieldGauge.SetSecondaryTexturePath('res:/UI/Texture/classes/ShipUI/gaugeFill.png')
        self.shieldGauge.textureSecondary.useTransform = True
        self.shieldGauge.textureSecondary.rotation = 0.0
        self.sr.wnd.state = uiconst.UI_PICKCHILDREN
        self.cookie = sm.GetService('inv').Register(self)
        self.UpdatePosition()
        self.shipuiReady = True
        self.SetupShip()

    def OptionsBtnMouseEnter(self, *args):
        self.options.SetAlpha(1.0)

    def OptionsBtnMouseExit(self, *args):
        self.options.SetAlpha(0.8)

    def CheckControl(self):
        control = sm.GetService('pwn').GetCurrentControl()
        if control:
            self.OnAssumeStructureControl()

    def SetButtonState(self):
        self.sr.slotsContainer.state = [uiconst.UI_HIDDEN, uiconst.UI_PICKCHILDREN][settings.user.ui.Get('modulesExpanded', 1)]
        self.sr.hudButtons.state = [uiconst.UI_HIDDEN, uiconst.UI_PICKCHILDREN][settings.user.ui.Get('hudButtonsExpanded', 1)]

    @telemetry.ZONE_METHOD
    def InitGaugeReadout(self):
        offset = 32
        self.sr.gaugeReadout = uicls.Container(name='gaugeReadout', parent=self.sr.mainContainer, left=self.sr.mainContainer.width / 2 + 100 - 18 + offset, top=self.GetGaugeTop(), width=200, align=uiconst.TOPRIGHT)
        top = 0
        for refName in ('shield', 'armor', 'structure'):
            t = uicls.EveLabelSmall(text='Xg', parent=self.sr.gaugeReadout, left=2, top=top, state=uiconst.UI_DISABLED, align=uiconst.TOPRIGHT)
            self.sr.gaugeReadout.sr.Set(refName, t)
            top += t.textheight
            uicls.Line(parent=self.sr.gaugeReadout, top=int(t.top + t.textheight / 2.0), width=-56 - offset, height=1, align=uiconst.TOPRIGHT)
            uicls.Line(parent=self.sr.gaugeReadout, top=int(t.top + t.textheight / 2.0 + 1), width=-56 - offset, height=1, left=-1, align=uiconst.TOPRIGHT, color=(0.1, 0.1, 0.1, 0.5))
            t.text = ''

        self.sr.gaugeReadout.height = top

    def OnMapShortcut(self, *blah):
        self.RefreshShortcuts()

    def OnRestoreDefaultShortcuts(self):
        self.RefreshShortcuts()

    def OnAssumeStructureControl(self, *args):
        now = blue.os.GetSimTime()
        self.assumingdelay = now
        uthread.new(self.DelayedOnAssumeStructureControl, now)

    def DelayedOnAssumeStructureControl(self, issueTime):
        blue.pyos.synchro.SleepSim(250)
        if self.assumingdelay is None:
            return
        issuedAt = self.assumingdelay
        if issuedAt != issueTime:
            return
        self.assumingdelay = None
        self.ShowStructureControl()

    def ShowStructureControl(self, *args):
        control = sm.GetService('pwn').GetCurrentControl()
        if control:
            for each in uicore.layer.shipui.children[0].children:
                if each.name in ('hudbuttons', 'slotsContainer'):
                    continue
                each.state = uiconst.UI_HIDDEN

            self.assumingcontrol = True
            self.initing = 1
            self.InitSlots()
            settings.user.ui.Set('modulesExpanded', 1)
            settings.user.ui.Set('hudButtonsExpanded', 1)
            self.InitButtons()
            self.initing = 0
            uicore.effect.MorphUI(self.sr.slotsContainer, 'left', -80, 500.0)
            uicore.effect.MorphUI(self.sr.hudButtons, 'left', 80, 500.0)

    def OnRelinquishStructureControl(self, *args):
        control = sm.GetService('pwn').GetCurrentControl()
        if not control:
            for each in uicore.layer.shipui.children[0].children:
                each.state = uiconst.UI_PICKCHILDREN

            self.assumingcontrol = False
            uicore.effect.MorphUI(self.sr.slotsContainer, 'left', 0, 500.0)
            uicore.effect.MorphUI(self.sr.hudButtons, 'left', 0, 500.0)
        self.SetupShip()

    def OnWeaponGroupsChanged(self):
        if self.destroyed:
            return
        uthread.new(self.InitSlots)

    def OnRefreshModuleBanks(self):
        if self.destroyed:
            return
        uthread.new(self.InitSlots)

    def RefreshShortcuts(self):
        for (r, i), slot in self.sr.slotsByOrder.iteritems():
            hiMedLo = ('High', 'Medium', 'Low')[r]
            slotno = i + 1
            txt = uicore.cmd.GetShortcutStringByFuncName('CmdActivate%sPowerSlot%i' % (hiMedLo, slotno))
            if not txt:
                txt = '_'
            slot.sr.shortcutHint.text = '<center>' + txt

    def BlinkButton(self, key):
        btn = self.sr.Get(key.lower(), None) or self.sr.Get('%sBtn' % key.lower(), None)
        if not btn:
            for each in self.sr.modules:
                if getattr(each, 'locationFlag', None) == util.LookupConstValue('flag%s' % key, 'no'):
                    btn = each
                    break

        if not btn:
            return
        if hasattr(btn.sr, 'icon'):
            sm.GetService('ui').BlinkSpriteA(btn.sr.icon, 1.0, 1000, None, passColor=0)
        else:
            sm.GetService('ui').BlinkSpriteA(btn, 1.0, 1000, None, passColor=0)

    def GetHUDOptionMenu(self, menuParent):
        showPassive = settings.user.ui.Get('showPassiveModules', 1)
        text = localization.GetByLabel('UI/Inflight/HUDOptions/DisplayPassiveModules')
        menuParent.AddCheckBox(text=text, checked=showPassive, callback=self.ToggleShowPassive)
        showEmpty = settings.user.ui.Get('showEmptySlots', 0)
        text = localization.GetByLabel('UI/Inflight/HUDOptions/DisplayEmptySlots')
        menuParent.AddCheckBox(text=text, checked=showEmpty, callback=self.ToggleShowEmpty)
        showReadout = settings.user.ui.Get('showReadout', 0)
        text = localization.GetByLabel('UI/Inflight/HUDOptions/DisplayReadout')
        menuParent.AddCheckBox(text=text, checked=showReadout, callback=self.ToggleReadout)
        readoutType = settings.user.ui.Get('readoutType', 1)
        text = localization.GetByLabel('UI/Inflight/HUDOptions/DisplayReadoutAsPercentage')
        if showReadout:
            callback = self.ToggleReadoutType
        else:
            callback = None
        menuParent.AddCheckBox(text=text, checked=readoutType, callback=callback)
        showZoomBtns = settings.user.ui.Get('showZoomBtns', 0)
        text = localization.GetByLabel('UI/Inflight/HUDOptions/DisplayZoomButtons')
        menuParent.AddCheckBox(text=text, checked=showZoomBtns, callback=self.ToggleShowZoomBtns)
        showTooltips = settings.user.ui.Get('showModuleTooltips', 1)
        text = localization.GetByLabel('UI/Inflight/HUDOptions/DisplayModuleTooltips')
        menuParent.AddCheckBox(text=text, checked=showTooltips, callback=self.ToggleShowModuleTooltips)
        lockModules = settings.user.ui.Get('lockModules', 0)
        text = localization.GetByLabel('UI/Inflight/HUDOptions/LockModulesInPlace')
        menuParent.AddCheckBox(text=text, checked=lockModules, callback=self.ToggleLockModules)
        lockOverload = settings.user.ui.Get('lockOverload', 0)
        text = localization.GetByLabel('UI/Inflight/HUDOptions/LockOverloadState')
        menuParent.AddCheckBox(text=text, checked=lockOverload, callback=self.ToggleOverloadLock)
        alignTop = settings.user.ui.Get('shipuialigntop', 0)
        text = localization.GetByLabel('UI/Inflight/HUDOptions/AlignHUDToTop')
        cb = menuParent.AddCheckBox(text=text, checked=alignTop, callback=self.ToggleAlign)
        cb.isToggleEntry = False
        menuParent.AddDivider()
        text = localization.GetByLabel('UI/Inflight/NotifyAudioAlert')
        iconPath = 'res:/UI/Texture/classes/UtilMenu/BulletIcon.png'
        menuParent.AddIconEntry(icon=iconPath, text=text, callback=self.ShowNotifySettingsWindow)
        if sm.GetService('logger').IsInDragMode():
            text = localization.GetByLabel('UI/Accessories/Log/ExitMessageMovingMode')
            enterArgs = False
        else:
            text = localization.GetByLabel('UI/Accessories/Log/EnterMessageMovingMode')
            enterArgs = True
        menuParent.AddIconEntry(icon='res:/UI/Texture/classes/UtilMenu/BulletIcon.png', text=text, callback=(sm.GetService('logger').MoveNotifications, enterArgs))

    def ShowNotifySettingsWindow(self):
        form.NotifySettingsWindow.Open()

    def ToggleAlign(self):
        settings.user.ui.Set('shipuialigntop', not settings.user.ui.Get('shipuialigntop', 0))
        self.UpdatePosition()
        for each in uicore.layer.abovemain.children[:]:
            if each.name == 'message':
                each.Close()
                break

        msg = getattr(uicore.layer.target, 'message', None)
        if msg:
            msg.Close()

    def ToggleReadout(self):
        current = not settings.user.ui.Get('showReadout', 0)
        settings.user.ui.Set('showReadout', current)
        if self.sr.gaugeReadout is None:
            self.InitGaugeReadout()
        self.sr.gaugeReadout.state = [uiconst.UI_HIDDEN, uiconst.UI_PICKCHILDREN][current]

    def ToggleReadoutType(self):
        current = settings.user.ui.Get('readoutType', 1)
        settings.user.ui.Set('readoutType', not current)

    def ToggleShowPassive(self):
        settings.user.ui.Set('showPassiveModules', not settings.user.ui.Get('showPassiveModules', 1))
        self.InitSlots()

    def ToggleShowZoomBtns(self):
        settings.user.ui.Set('showZoomBtns', not settings.user.ui.Get('showZoomBtns', 0))
        self.InitButtons()

    def ToggleShowEmpty(self):
        settings.user.ui.Set('showEmptySlots', not settings.user.ui.Get('showEmptySlots', 0))
        self.InitSlots()

    def ToggleLockModules(self):
        settings.user.ui.Set('lockModules', not settings.user.ui.Get('lockModules', 0))
        self.CheckGroupAllButton()

    def ToggleOverloadLock(self):
        settings.user.ui.Set('lockOverload', not settings.user.ui.Get('lockOverload', 0))

    def ToggleShowModuleTooltips(self):
        settings.user.ui.Set('showModuleTooltips', not settings.user.ui.Get('showModuleTooltips', 1))

    def ShowTimer(self, timerID, startTime, duration, label):
        check = self.GetTimer(timerID)
        if check:
            if check.endTime <= startTime + duration:
                check.Close()
            else:
                return
        timer = uicls.Container(name='%s' % timerID, parent=self.sr.timers, height=17, align=uiconst.TOBOTTOM, top=30)
        timer.endTime = startTime + duration
        uicls.EveLabelSmall(text=label, parent=timer, left=124, color=(1.0, 1.0, 1.0, 0.5), state=uiconst.UI_NORMAL)
        fpar = uicls.Container(parent=timer, align=uiconst.TOTOP, height=13)
        uicls.Frame(parent=fpar, color=(1.0, 1.0, 1.0, 0.5))
        t = uicls.EveLabelSmall(text='', parent=fpar, left=5, top=0, state=uiconst.UI_NORMAL)
        p = uicls.Fill(parent=fpar, align=uiconst.RELATIVE, width=118, height=11, left=1, top=1, color=(1.0, 1.0, 1.0, 0.25))
        duration = float(duration)
        totalTime = float(startTime + duration * 10000 - blue.os.GetSimTime()) / SEC
        while 1 and not timer.destroyed:
            now = blue.os.GetSimTime()
            dt = blue.os.TimeDiffInMs(startTime, now)
            timeLeft = (duration - dt) / 1000.0
            timer.timeLeft = timeLeft
            if timer.destroyed or dt > duration:
                t.text = localization.GetByLabel('UI/Commands/Done')
                p.width = 0
                break
            t.text = localization.GetByLabel('UI/Inflight/TimeLeft', timeleft=timeLeft)
            p.width = max(0, min(118, int(118 * (timeLeft / totalTime))))
            blue.pyos.synchro.Yield()

        if not timer.destroyed:
            blue.pyos.synchro.SleepWallclock(250)
            if not t.destroyed:
                t.text = ''
            blue.pyos.synchro.SleepWallclock(250)
            if not t.destroyed:
                t.text = localization.GetByLabel('UI/Commands/Done')
            blue.pyos.synchro.SleepWallclock(250)
            if not t.destroyed:
                t.text = ''
            blue.pyos.synchro.SleepWallclock(250)
            if not t.destroyed:
                t.text = localization.GetByLabel('UI/Commands/Done')
            blue.pyos.synchro.SleepWallclock(250)
            if not t.destroyed:
                t.text = ''
            if not timer.destroyed:
                timer.Close()

    def KillTimer(self, timerID):
        timer = self.GetTimer(timerID)
        if timer:
            timer.Close()

    def GetTimer(self, timerID):
        for each in self.sr.timers.children:
            if each.name == '%s' % timerID:
                return each

    def OnExpandDown(self, btn, *args):
        pass

    def OnExpandUp(self, btn, *args):
        pass

    def ClickExpand(self, btn, *args):
        if btn.side == -1:
            if self.sr.hudButtons:
                self.sr.hudButtons.state = [uiconst.UI_PICKCHILDREN, uiconst.UI_HIDDEN][self.sr.hudButtons.state == uiconst.UI_PICKCHILDREN]
            settings.user.ui.Set('hudButtonsExpanded', self.sr.hudButtons.state == uiconst.UI_PICKCHILDREN)
        else:
            if self.sr.slotsContainer:
                self.sr.slotsContainer.state = [uiconst.UI_PICKCHILDREN, uiconst.UI_HIDDEN][self.sr.slotsContainer.state == uiconst.UI_PICKCHILDREN]
            settings.user.ui.Set('modulesExpanded', self.sr.slotsContainer.state == uiconst.UI_PICKCHILDREN)
        sm.GetService('ui').StopBlink(btn)
        self.CheckExpandBtns()

    def CheckExpandBtns(self):
        if self.sr.Get('expandbtnright', None) and not self.sr.expandbtnright.destroyed:
            on = settings.user.ui.Get('modulesExpanded', 1)
            if on:
                self.sr.expandbtnright.LoadTexture('res:/UI/Texture/classes/ShipUI/expandBtnLeft.png')
            else:
                self.sr.expandbtnright.LoadTexture('res:/UI/Texture/classes/ShipUI/expandBtnRight.png')
            self.sr.expandbtnright.hint = [localization.GetByLabel('UI/Inflight/ShowModules'), localization.GetByLabel('UI/Inflight/HideModules')][on]
        else:
            return
        if self.sr.Get('expandbtnleft', None):
            on = settings.user.ui.Get('hudButtonsExpanded', 1)
            if on:
                self.sr.expandbtnleft.LoadTexture('res:/UI/Texture/classes/ShipUI/expandBtnRight.png')
            else:
                self.sr.expandbtnleft.LoadTexture('res:/UI/Texture/classes/ShipUI/expandBtnLeft.png')
            self.sr.expandbtnleft.hint = [localization.GetByLabel('UI/Inflight/ShowButtons'), localization.GetByLabel('UI/Inflight/HideButtons')][on]

    @telemetry.ZONE_METHOD
    def InitButtons(self):
        par = uiutil.FindChild(self.sr.wnd, 'hudbuttons')
        if not par:
            par = uicls.Container(name='hudbuttons', parent=self.sr.slotsContainer.parent, align=uiconst.CENTER, pos=(0, 0, 512, 256))
        par.Flush()
        grid = [[-1.0, -1.0], [-1.5, 0.0], [-1.0, 1.0]]
        BTNSIZE = 36
        w = par.width
        h = par.height
        centerX = (w - BTNSIZE) / 2
        centerY = (h - BTNSIZE) / 2
        yBaseLine = 94
        ystep = int(ICONSIZE * 1.06)
        xstep = int(ICONSIZE * 1.3)
        step = 20
        buttons = [(localization.GetByLabel('UI/Generic/Cargo'),
          'inFlightCargoBtn',
          self.Inventory,
          'ui_44_32_10',
          100,
          0.0,
          'OpenCargoHoldOfActiveShip'),
         (localization.GetByLabel('UI/Inflight/ResetCamera'),
          'inFlightResetCameraBtn',
          self.ResetCamera,
          'ui_44_32_46',
          128,
          1.5,
          ''),
         (localization.GetByLabel('UI/Generic/Scanner'),
          'inFlightScannerBtn',
          self.Scanner,
          'ui_44_32_41',
          100,
          1.0,
          'OpenScanner'),
         (localization.GetByLabel('UI/Generic/Tactical'),
          'inFlightTacticalBtn',
          self.Tactical,
          'ui_44_32_42',
          128,
          0.5,
          'CmdToggleTacticalOverlay'),
         (localization.GetByLabel('UI/Generic/Autopilot'),
          'inFlightAutopilotBtn',
          self.Autopilot,
          'ui_44_32_12',
          100,
          2.0,
          'CmdToggleAutopilot')]
        showZoomBtns = settings.user.ui.Get('showZoomBtns', 0)
        if showZoomBtns:
            buttons += [(localization.GetByLabel('UI/Inflight/ZoomIn'),
              'inFlightZoomInBtn',
              self.ZoomIn,
              '44_43',
              128,
              2.5,
              'CmdZoomIn'), (localization.GetByLabel('UI/Inflight/ZoomOut'),
              'inFlightZoomOutBtn',
              self.ZoomOut,
              '44_44',
              100,
              3.0,
              'CmdZoomOut')]
        for btnName, guiID, func, iconNum, rad, y, cmdName in buttons:
            if eve.rookieState and eve.rookieState < sm.GetService('tutorial').GetShipuiRookieFilter(btnName):
                continue
            slot = LeftSideButton(parent=par, iconNum=iconNum, btnName=btnName, pos=(int(centerX - rad),
             int(yBaseLine + y * 32),
             BTNSIZE,
             BTNSIZE), name=guiID, func=func, cmdName=cmdName)
            self.sr.Set(btnName.replace(' ', '').lower(), slot)
            if btnName == localization.GetByLabel('UI/Generic/Tactical'):
                self.sr.tacticalBtn = slot
                tActive = settings.user.overview.Get('viewTactical', 0)
                uiutil.GetChild(self.sr.tacticalBtn, 'busy').state = [uiconst.UI_HIDDEN, uiconst.UI_DISABLED][tActive]
                self.sr.tacticalBtn.hint = [localization.GetByLabel('UI/Inflight/ShowTacticalOverlay'), localization.GetByLabel('UI/Inflight/HideTacticalOverview')][tActive]
            elif btnName == localization.GetByLabel('UI/Generic/Autopilot'):
                self.sr.autopilotBtn = slot
                apActive = sm.GetService('autoPilot').GetState()
                uiutil.GetChild(self.sr.autopilotBtn, 'busy').state = [uiconst.UI_HIDDEN, uiconst.UI_DISABLED][apActive]
                hint = [localization.GetByLabel('UI/Inflight/ActivateAutopilot'), localization.GetByLabel('UI/Inflight/DeactivateAutopilot')][apActive]
                self.sr.autopilotBtn.hint = hint
            elif btnName == localization.GetByLabel('UI/Generic/Cargo'):
                slot.OnDropData = self.DropInCargo

        self.sr.hudButtons = par

    def _GetShortcutForCommand(self, cmdName):
        if cmdName:
            shortcut = uicore.cmd.GetShortcutStringByFuncName(cmdName)
            if shortcut:
                return localization.GetByLabel('UI/Inflight/ShortcutFormatter', shortcut=shortcut)
        return ''

    def DropInCargo(self, dragObj, nodes):
        invCtrl.ShipCargo().OnDropData(nodes)

    def AddBookmarks(self, bookmarkIDs):
        isMove = not uicore.uilib.Key(uiconst.VK_SHIFT)
        sm.GetService('invCache').GetInventoryFromId(session.shipid).AddBookmarks(bookmarkIDs, const.flagCargo, isMove)

    def Tactical(self, *args):
        sm.GetService('tactical').ToggleOnOff()
        tActive = settings.user.overview.Get('viewTactical', 0)
        uiutil.GetChild(self.sr.tacticalBtn, 'busy').state = [uiconst.UI_HIDDEN, uiconst.UI_DISABLED][tActive]
        self.sr.tacticalBtn.hint = [localization.GetByLabel('UI/Inflight/ShowTacticalOverlay'), localization.GetByLabel('UI/Inflight/HideTacticalOverview')][tActive]
        self.sr.tacticalBtn.hint += self._GetShortcutForCommand(self.sr.tacticalBtn.cmdName)

    def Autopilot(self, *args):
        self.AutoPilotOnOff(not sm.GetService('autoPilot').GetState())

    def ZoomIn(self, *args):
        uicore.cmd.CmdZoomIn()

    def ZoomOut(self, *args):
        uicore.cmd.CmdZoomOut()

    def ResetCamera(self, *args):
        sm.GetService('camera').ResetCamera()

    def Inventory(self, *args):
        shipID = util.GetActiveShip()
        if shipID is None:
            return
        form.Inventory.OpenOrShow(('ShipCargo', shipID), usePrimary=False, toggle=True)

    def Scanner(self, *args):
        self.ToggleScanner()

    def ToggleScanner(self):
        if session.solarsystemid:
            wnd = form.Scanner.GetIfOpen()
            if wnd is not None and not wnd.destroyed:
                if wnd.IsMinimized():
                    wnd.Maximize()
                elif wnd.IsCollapsed():
                    wnd.Expand()
                else:
                    wnd.CloseByUser()
            else:
                form.Scanner.Open()

    def InitStructureSlots(self):
        currentControl = sm.GetService('pwn').GetCurrentControl()
        shipmodules = []
        charges = {}
        if currentControl:
            for k, v in currentControl.iteritems():
                shipmodules.append(sm.services['godma'].GetItem(k))

        xstep = int(ICONSIZE * 2.0)
        ystep = int(ICONSIZE * 1.35)
        vgridrange = 1
        hgridrange = 5
        grid = [[1.0, 0.1]]
        myOrder = [0,
         1,
         2,
         3,
         4]
        for i, moduleInfo in enumerate(shipmodules):
            if moduleInfo is None:
                continue
            myOrder[i] = moduleInfo.itemID
            if currentControl.has_key(moduleInfo.itemID):
                item = sm.services['godma'].GetItem(moduleInfo.itemID)
                if item.groupID == const.groupMobileLaserSentry and len(item.modules):
                    charges[moduleInfo.itemID] = item.modules[0]
                elif len(item.sublocations):
                    charges[moduleInfo.itemID] = item.sublocations[0]

        self.InitDrawSlots(xstep, ystep, vgridrange, hgridrange, grid, myOrder, slotType='structure')
        for moduleInfo in shipmodules:
            if moduleInfo:
                self._FitStructureSlot(moduleInfo, charges)

        self.CheckButtonVisibility(3, ['hiSlots'], 5, myOrder)

    @telemetry.ZONE_METHOD
    def InitDrawSlots(self, xstep, ystep, vgridrange, hgridrange, grid, myOrder, slotType = None):
        w = self.sr.slotsContainer.width
        h = self.sr.slotsContainer.height
        centerX = (w - 64) / 2
        centerY = (h - 64) / 2
        for r in xrange(vgridrange):
            x, y = grid[r]
            for i in xrange(hgridrange):
                slotFlag = myOrder[r * hgridrange + i]
                if slotType == 'shipslot':
                    slot = ShipSlot(pos=(0,
                     int(centerY + ystep * y),
                     64,
                     64), name='slot', state=uiconst.UI_HIDDEN, align=uiconst.TOPLEFT)
                    self.sr.slotsContainer.children.insert(0, slot)
                else:
                    slot = uicls.Container(name='defenceslot', parent=self.sr.slotsContainer, width=64, height=128 + 60, align=uiconst.TOPLEFT, state=uiconst.UI_HIDDEN, top=166)
                slot.left = int(centerX + (x + i) * xstep) + 50
                slot.sr.module = None
                slot.sr.slotFlag = slotFlag
                slot.sr.slotPos = (r, i)
                self.sr.slotsByFlag[slotFlag] = slot
                self.sr.slotsByOrder[r, i] = slot
                slot.sr.shortcutHint = uicls.EveLabelSmall(text='<center>-', parent=slot, width=64, color=(1.0, 1.0, 1.0, 0.25), shadowOffset=(0, 0), state=uiconst.UI_DISABLED, idx=0)
                slot.sr.shortcutHint.top = 30
                if self.assumingcontrol:
                    slot.sr.shortcutHint.top -= 4

        self.RefreshShortcuts()

    def InitSlotsDelayed(self):
        self.initSlotsDelayedTimer = base.AutoTimer(200, self.InitSlots)

    @telemetry.ZONE_METHOD
    def InitSlots(self):
        self.initSlotsDelayedTimer = None
        if self.destroyed or not self.sr.slotsContainer:
            return
        self.sr.slotsContainer.Flush()
        self.sr.modules = {}
        self.sr.slotsByFlag = {}
        self.sr.slotsByOrder = {}
        self.totalSlaves = 0
        control = sm.GetService('pwn').GetCurrentControl()
        if control:
            self.assumingcontrol = True
        else:
            self.assumingcontrol = False
        ship = sm.GetService('godma').GetItem(session.shipid)
        if ship is None:
            raise RuntimeError('ShipUI being inited with no ship state!')
        self.passiveFiltered = []
        if self.assumingcontrol:
            self.InitStructureSlots()
        else:
            shipmodules = ship.modules
            charges = {}
            for sublocation in ship.sublocations:
                charges[sublocation.flagID] = sublocation
                if sublocation.stacksize == 0:
                    sm.services['godma'].LogError('InitSlots.no quantity', sublocation, sublocation.flagID)

            for module in shipmodules:
                if module.categoryID == const.categoryCharge:
                    charges[module.flagID] = module

            xstep = int(ICONSIZE * 1.6)
            ystep = int(ICONSIZE * 1.4)
            vgridrange = 3
            hgridrange = 8
            grid = [[1.0, -1.0], [1.5, 0.0], [1.0, 1.0]]
            myOrder = self.GetSlotOrder()
            self.InitDrawSlots(xstep, ystep, vgridrange, hgridrange, grid, myOrder, slotType='shipslot')
            self.InitOverloadBtns(grid, shipmodules)
            self.InitGroupAllButtons()
            dogmaLocation = sm.StartService('clientDogmaIM').GetDogmaLocation()
            IsSlave = lambda itemID: dogmaLocation.IsModuleSlave(itemID, session.shipid)
            for moduleInfo in shipmodules:
                if IsSlave(moduleInfo.itemID):
                    self.totalSlaves += 1
                    continue
                self._FitSlot(moduleInfo, charges)

            self.CheckButtonVisibility(0, ['hiSlots', 'medSlots', 'lowSlots'], None, myOrder)

    @telemetry.ZONE_METHOD
    def InitGroupAllButtons(self):
        w = self.sr.slotsContainer.width
        h = self.sr.slotsContainer.height
        centerX = (w - 20) / 2
        centerY = (h - 20) / 2
        self.groupAllIcon = ic = uicls.Icon(parent=self.sr.slotsContainer, state=uiconst.UI_HIDDEN, icon='ui_73_16_251', idx=0, name='groupAllIcon', pos=(centerX + 68,
         centerY - 57,
         16,
         16), hint='')
        ic.orgPos = ic.top
        ic.OnClick = self.OnGroupAllButtonClicked
        ic.OnMouseDown = (self.OverloadRackBtnMouseDown, ic)
        ic.OnMouseUp = (self.OverloadRackBtnMouseUp, ic)
        self.CheckGroupAllButton()

    def OnGroupAllButtonClicked(self, *args):
        if settings.user.ui.Get('lockModules', 0):
            return
        dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
        if dogmaLocation.CanGroupAll(session.shipid):
            dogmaLocation.LinkAllWeapons(session.shipid)
        else:
            dogmaLocation.UnlinkAllWeapons(session.shipid)

    @telemetry.ZONE_METHOD
    def InitOverloadBtns(self, grid, shipmodules):
        w = self.sr.slotsContainer.width
        h = self.sr.slotsContainer.height
        centerX = (w - 20) / 2
        centerY = (h - 20) / 2
        overloadEffectsByRack = {}
        modulesByRack = {}
        for module in shipmodules:
            for key in module.effects.iterkeys():
                effect = module.effects[key]
                if effect.effectID in (const.effectHiPower, const.effectMedPower, const.effectLoPower):
                    if effect.effectID not in modulesByRack:
                        modulesByRack[effect.effectID] = []
                    modulesByRack[effect.effectID].append(module)
                    for key in module.effects.iterkeys():
                        effect2 = module.effects[key]
                        if effect2.effectCategory == const.dgmEffOverload:
                            if effect.effectID not in overloadEffectsByRack:
                                overloadEffectsByRack[effect.effectID] = []
                            overloadEffectsByRack[effect.effectID].append(effect2)

        i = 0
        for each in ['Hi', 'Med', 'Lo']:
            x, y = grid[i]
            par = uicls.Container(parent=self.sr.slotsContainer, name='overloadBtn' + each, width=20, height=20, align=uiconst.TOPLEFT, left=0, top=0, state=uiconst.UI_NORMAL, pickRadius=8)
            icon = uicls.Sprite(parent=par, align=uiconst.TOALL, pos=(0, 0, 0, 0), state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/ShipUI/overloadBtn%sOff.png' % each)
            par.left = centerX + 67 + int(x * 14)
            par.top = centerY + int(y * 14)
            par.OnClick = (self.OverloadRackBtnClick, par)
            par.OnMouseDown = (self.OverloadRackBtnMouseDown, par)
            par.OnMouseUp = (self.OverloadRackBtnMouseUp, par)
            par.OnMouseExit = (self.OverloadRackBtnMouseExit, par)
            par.orgPos = par.top
            par.active = False
            par.powerEffectID = getattr(const, 'effect%sPower' % each, None)
            par.activationID = None
            i += 1

        self.CheckOverloadRackBtnState(shipmodules)

    def ToggleRackOverload(self, what):
        if what not in ('Hi', 'Med', 'Lo') or self.sr.slotsContainer.destroyed:
            return
        btn = uiutil.FindChild(self.sr.slotsContainer, 'overloadBtn' + what)
        if btn:
            if btn.activationID:
                uthread.new(self.OverloadRackBtnClick, btn)
            else:
                uthread.new(eve.Message, 'Disabled')

    def OverloadRackBtnClick(self, btn, *args):
        if settings.user.ui.Get('lockOverload', 0):
            eve.Message('error')
            eve.Message('LockedOverloadState')
            return
        if btn.active:
            eve.Message('click')
            sm.GetService('godma').StopOverloadRack(btn.activationID)
        else:
            eve.Message('click')
            sm.GetService('godma').OverloadRack(btn.activationID)

    def OverloadRackBtnMouseDown(self, btn, *args):
        btn.top = btn.orgPos + 1

    def OverloadRackBtnMouseUp(self, btn, *args):
        btn.top = btn.orgPos

    def OverloadRackBtnMouseExit(self, btn, *args):
        btn.top = btn.orgPos

    def ProcessPendingOverloadUpdate(self, moduleIDs):
        for moduleID in moduleIDs:
            moduleButton = self.sr.modules.get(moduleID, None)
            if moduleButton is not None:
                moduleButton.UpdateOverloadState()

    @telemetry.ZONE_METHOD
    def CheckOverloadRackBtnState(self, shipmodules = None):
        if self.assumingcontrol:
            return
        if self.destroyed or not self.sr.slotsContainer:
            return
        if self.checkingoverloadrackstate:
            self.checkingoverloadrackstate = 2
            return
        self.checkingoverloadrackstate = 1
        if shipmodules is None:
            ship = sm.GetService('godma').GetItem(session.shipid)
            if ship is None:
                return
            shipmodules = ship.modules
        overloadEffectsByRack = {}
        modulesByRack = {}
        for module in shipmodules:
            for key in module.effects.iterkeys():
                effect = module.effects[key]
                if effect.effectID in (const.effectHiPower, const.effectMedPower, const.effectLoPower):
                    if effect.effectID not in modulesByRack:
                        modulesByRack[effect.effectID] = []
                    modulesByRack[effect.effectID].append(module)
                    for key in module.effects.iterkeys():
                        effect2 = module.effects[key]
                        if effect2.effectCategory == const.dgmEffOverload:
                            if effect.effectID not in overloadEffectsByRack:
                                overloadEffectsByRack[effect.effectID] = []
                            overloadEffectsByRack[effect.effectID].append(effect2)

        i = 0
        for each in ['Hi', 'Med', 'Lo']:
            btn = uiutil.GetChild(self.sr.slotsContainer, 'overloadBtn' + each)
            btn.activationID = None
            btn.active = False
            btn.children[0].LoadTexture('res:/UI/Texture/classes/ShipUI/overloadBtn%sOff.png' % each)
            btn.hint = localization.GetByLabel('UI/Inflight/OverloadRack')
            btn.state = uiconst.UI_DISABLED
            if btn.powerEffectID in modulesByRack:
                btn.activationID = modulesByRack[btn.powerEffectID][0].itemID
            if btn.powerEffectID in overloadEffectsByRack:
                sumInactive = sum([ 1 for olEffect in overloadEffectsByRack[btn.powerEffectID] if not olEffect.isActive ])
                if not sumInactive:
                    btn.children[0].LoadTexture('res:/UI/Texture/classes/ShipUI/overloadBtn%sOn.png' % each)
                    btn.active = True
                    btn.hint = localization.GetByLabel('UI/Inflight/StopOverloadingRack')
            btn.state = uiconst.UI_NORMAL

        if self.checkingoverloadrackstate == 2:
            self.checkingoverloadrackstate = 0
            return self.CheckOverloadRackBtnState(shipmodules)
        self.checkingoverloadrackstate = 0

    def CheckGroupAllButton(self):
        if self.destroyed:
            return
        icon = self.groupAllIcon
        if icon is None or icon.destroyed:
            return
        dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
        for typeID, qty in dogmaLocation.GetGroupableTypes(session.shipid).iteritems():
            if qty > 1:
                break
        else:
            icon.state = uiconst.UI_HIDDEN
            return

        icon.state = uiconst.UI_NORMAL
        if dogmaLocation.CanGroupAll(session.shipid):
            icon.LoadIcon('ui_73_16_252')
            hint = localization.GetByLabel('UI/Inflight/GroupAllWeapons')
        else:
            icon.LoadIcon('ui_73_16_251')
            hint = localization.GetByLabel('UI/Inflight/UngroupAllWeapons')
        if settings.user.ui.Get('lockModules', False):
            hint = localization.GetByLabel('UI/Inflight/Locked', unit=hint)
        icon.hint = hint
        if getattr(self, 'updateGroupAllButtonThread', None):
            self.updateGroupAllButtonThread.kill()
        self.updateGroupAllButtonThread = uthread.new(self.UpdateGroupAllButton)

    def UpdateGroupAllButton(self):
        if self.destroyed:
            return
        GetOpacity = sm.GetService('clientDogmaIM').GetDogmaLocation().GetGroupAllOpacity
        if sm.GetService('clientDogmaIM').GetDogmaLocation().CanGroupAll(session.shipid):
            attributeName = 'lastGroupAllRequest'
        else:
            attributeName = 'lastUngroupAllRequest'
        icon = self.groupAllIcon
        if icon is None or icon.destroyed:
            return
        icon.state = uiconst.UI_DISABLED
        while True:
            opacity = GetOpacity(attributeName)
            if opacity > 0.999:
                break
            icon.color.a = 0.2 + opacity * 0.6
            blue.pyos.synchro.Yield()
            if self.destroyed:
                return

        icon.color.a = 1.0
        icon.state = uiconst.UI_NORMAL

    @telemetry.ZONE_METHOD
    def CheckButtonVisibility(self, gidx, sTypes, totalslot, myOrder):
        totalslots = totalslot
        ship = sm.GetService('godma').GetItem(session.shipid)
        lastType = ''
        showEmptySlots = settings.user.ui.Get('showEmptySlots', 0)
        totalHi = getattr(ship, 'hiSlots', 0)
        totalMed = getattr(ship, 'medSlots', 0)
        totalLow = getattr(ship, 'lowSlots', 0)
        slotUIID = 0
        for sType in sTypes:
            if totalslot is None:
                totalslots = int(getattr(ship, sType, 0))
            ignoredSlots = 0
            for sidx in xrange(totalslots):
                if sidx == 8:
                    break
                flagTypes = ['Hi',
                 'Med',
                 'Lo',
                 'Stuct']
                if not self.assumingcontrol:
                    if gidx < len(flagTypes):
                        slotFlag = getattr(const, 'flag%sSlot%s' % (flagTypes[gidx], sidx), None)
                    slot = self.sr.slotsByFlag.get(slotFlag, None)
                else:
                    slotFlag = myOrder[sidx]
                    slot = self.sr.slotsByFlag.get(slotFlag, None)
                typeNames = ['High',
                 'Medium',
                 'Low',
                 'Stuct']
                slotUIID += 1
                if gidx < len(typeNames):
                    currType = typeNames[gidx]
                    if currType != lastType:
                        slotUIID = 1
                    lastType = currType
                    if slot:
                        slot.name = 'inFlight%sSlot%s' % (typeNames[gidx], slotUIID)
                if showEmptySlots and not self.assumingcontrol:
                    if slot and slot.sr.module is None and slotFlag not in self.passiveFiltered:
                        slot.showAsEmpty = 1
                        if self.assumingcontrol:
                            slot.hint = localization.GetByLabel('UI/Inflight/EmptyStructureControlSlot')
                            slot.state = uiconst.UI_NORMAL
                        else:
                            if gidx == 0:
                                if ignoredSlots < self.totalSlaves:
                                    ignoredSlots += 1
                                    slot.ignored = 1
                                    continue
                            slot.hint = [localization.GetByLabel('UI/Inflight/EmptyHighSlot'), localization.GetByLabel('UI/Inflight/EmptyMediumSlot'), localization.GetByLabel('UI/Inflight/EmptyLowSlot')][gidx]
                            slot.state = uiconst.UI_NORMAL
                            iconpath = ['ui_8_64_11',
                             'ui_8_64_10',
                             'ui_8_64_9',
                             'ui_44_64_14'][gidx]
                            icon = uicls.Icon(icon=iconpath, parent=slot, pos=(13, 13, 24, 24), align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, idx=0, ignoreSize=True)
                            icon.left = (slot.width - icon.width) / 2
                            icon.color.a = 0.25

            gidx += 1

    def _FitStructureSlot(self, moduleInfo, charges):
        showPassive = settings.user.ui.Get('showPassiveModules', 1)
        if moduleInfo.categoryID != const.categoryStructure:
            return
        if not showPassive and self.GetDefaultEffect(moduleInfo) is None:
            self.passiveFiltered.append(moduleInfo.flagID)
            return
        slot = self.sr.slotsByFlag.get(moduleInfo.itemID, None)
        if slot is None:
            return
        if slot.sr.module is not None:
            return
        self.FitStructureSlot(slot, moduleInfo, charges.get(moduleInfo.itemID, None))

    @telemetry.ZONE_METHOD
    def _FitSlot(self, moduleInfo, charges, grey = 0, slotUIID = 'slot'):
        showPassive = settings.user.ui.Get('showPassiveModules', 1)
        if moduleInfo.categoryID == const.categoryCharge:
            return
        if not showPassive and self.GetDefaultEffect(moduleInfo) is None:
            self.passiveFiltered.append(moduleInfo.flagID)
            return
        slot = self.sr.slotsByFlag.get(moduleInfo.flagID, None)
        if slot is None:
            return
        if slot.sr.module is not None:
            return
        self.FitSlot(slot, moduleInfo, charges.get(moduleInfo.flagID, None), grey=grey, slotUIID=slotUIID)

    def GetDefaultEffect(self, moduleInfo):
        for key in moduleInfo.effects.iterkeys():
            effect = moduleInfo.effects[key]
            if self.IsEffectActivatible(effect):
                return effect

    def IsEffectActivatible(self, effect):
        return effect.isDefault and effect.effectName != 'online' and effect.effectCategory in (const.dgmEffActivation, const.dgmEffTarget)

    def ResetSwapMode(self):
        for each in self.sr.slotsContainer.children:
            each.opacity = 1.0
            if each.sr.get('module', -1) == -1:
                continue
            if each.sr.module is None and not getattr(each, 'showAsEmpty', 0) or getattr(each, 'ignored', 0):
                each.state = uiconst.UI_HIDDEN
            if getattr(each.sr, 'module', None):
                if getattr(each, 'linkDragging', None):
                    each.linkDragging = 0
                    each.sr.module.CheckOverload()
                    each.sr.module.CheckOnline()
                    each.sr.module.CheckMasterSlave()
                    each.sr.module.StopShowingGroupHighlight()
                    each.sr.module.CheckOnline()
                each.sr.module.blockClick = 0

    def StartDragMode(self, itemID, typeID):
        for each in self.sr.slotsContainer.children:
            if not hasattr(each, 'sr') or not hasattr(each.sr, 'module'):
                continue
            if each.name.startswith('overload') or each.name == 'groupAllIcon':
                continue
            if each.sr.module is None:
                each.opacity = 0.7
            each.state = uiconst.UI_NORMAL
            if typeID is None:
                continue
            if getattr(each.sr, 'module', None) is not None:
                moduleType = each.sr.module.GetModuleType()
                isGroupable = each.sr.module.sr.moduleInfo.groupID in const.dgmGroupableGroupIDs
                if isGroupable:
                    each.linkDragging = 1
                    if each.sr.module.sr.moduleInfo.itemID == itemID:
                        each.sr.module.icon.SetAlpha(0.2)
                        continue
                    elif moduleType and moduleType[0] == typeID:
                        each.sr.module.ShowGroupHighlight()

    def GetPosFromFlag(self, slotFlag):
        return self.sr.slotsByFlag[slotFlag].sr.slotPos

    def GetSlotOrder(self):
        defaultOrder = []
        for r in xrange(3):
            for i in xrange(8):
                slotFlag = getattr(const, 'flag%sSlot%s' % (['Hi', 'Med', 'Lo'][r], i), None)
                if slotFlag is not None:
                    defaultOrder.append(slotFlag)

        try:
            return settings.user.ui.Get('slotOrder', {}).get(session.shipid, defaultOrder)
        except:
            log.LogException()
            sys.exc_clear()
            return defaultOrder

    def ChangeSlots(self, toFlag, fromFlag):
        toModule = self.GetModuleType(toFlag)
        fromModule = self.GetModuleType(fromFlag)
        shift = uicore.uilib.Key(uiconst.VK_SHIFT)
        if toModule and fromModule and toModule[0] == fromModule[0]:
            self.LinkWeapons(toModule, fromModule, toFlag, fromFlag, merge=not shift)
            if not sm.GetService('clientDogmaIM').GetDogmaLocation().IsModuleMaster(toModule[1], session.shipid):
                self.SwapSlots(fromFlag, toFlag)
        else:
            self.SwapSlots(toFlag, fromFlag)

    def SwapSlots(self, slotFlag1, slotFlag2):
        module1 = self.GetModuleType(slotFlag1)
        module2 = self.GetModuleType(slotFlag2)
        shift = uicore.uilib.Key(uiconst.VK_SHIFT)
        if shift and module1 is None and module2 is not None:
            dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
            if dogmaLocation.IsInWeaponBank(session.shipid, module2[1]):
                moduleID = dogmaLocation.UngroupModule(session.shipid, module2[1])
                slotFlag2 = dogmaLocation.GetItem(moduleID).flagID
        current = self.GetSlotOrder()[:]
        flag1Idx = current.index(slotFlag1)
        flag2Idx = current.index(slotFlag2)
        current[flag1Idx] = slotFlag2
        current[flag2Idx] = slotFlag1
        all = settings.user.ui.Get('slotOrder', {})
        all[session.shipid] = current
        settings.user.ui.Set('slotOrder', all)
        self.InitSlots()

    def LinkWeapons(self, master, slave, slotFlag1, slotFlag2, merge = False):
        dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
        groupID = cfg.invtypes.Get(master[0]).groupID
        areTurrets = groupID in const.dgmGroupableGroupIDs
        slaves = dogmaLocation.GetSlaveModules(slave[1], session.shipid)
        swapSlots = 0
        if slaves:
            swapSlots = 1
        if not areTurrets:
            eve.Message('CustomNotify', {'notify': localization.GetByLabel('UI/Inflight/WeaponGroupingRule')})
            return
        weaponLinked = dogmaLocation.LinkWeapons(session.shipid, master[1], slave[1], merge=merge)
        if weaponLinked and swapSlots:
            self.SwapSlots(slotFlag1, slotFlag2)

    def GetModuleType(self, flag):
        if not self.sr.slotsByFlag.has_key(flag):
            return None
        module = self.sr.slotsByFlag[flag].sr.module
        if not module:
            return None
        return module.GetModuleType()

    def FitSlot(self, slot, moduleInfo, charge = None, grey = 0, slotUIID = 'slot'):
        pos = (slot.width - 48) / 2
        module = xtriui.ModuleButton(parent=slot, align=uiconst.TOPLEFT, width=48, height=48, top=pos, left=pos, idx=0, state=uiconst.UI_NORMAL)
        module.Setup(moduleInfo, grey=grey)
        self.sr.modules[moduleInfo.itemID] = module
        slot.sr.module = module
        slot.state = uiconst.UI_NORMAL
        slot.sr.shortcutHint.state = uiconst.UI_HIDDEN
        slot.name = slotUIID
        if charge:
            module.SetCharge(charge)
        if moduleInfo.flagID in [const.flagHiSlot0,
         const.flagHiSlot1,
         const.flagHiSlot2,
         const.flagHiSlot3,
         const.flagHiSlot4,
         const.flagHiSlot5,
         const.flagHiSlot6,
         const.flagHiSlot7]:
            self.myHarpointFlags.append(moduleInfo.flagID)

    def FitStructureSlot(self, slot, moduleInfo, charge = None):
        pos = (slot.width - 48) / 2
        module = xtriui.DefenceStructureButton(parent=slot, align=uiconst.TOPLEFT, width=64, height=250, top=0, left=0, idx=1, state=uiconst.UI_DISABLED)
        module.Setup(moduleInfo)
        self.sr.modules[moduleInfo.itemID] = module
        slot.sr.module = module
        slot.state = uiconst.UI_NORMAL
        if charge:
            module.SetCharge(charge)

    def GetModuleFromID(self, moduleID):
        return self.sr.modules.get(moduleID, None)

    def AutoPilotOnOff(self, onoff, *args):
        if onoff:
            sm.GetService('autoPilot').SetOn()
        else:
            sm.GetService('autoPilot').SetOff('toggled by shipUI')

    def OnAutoPilotOn(self):
        uiutil.GetChild(self.sr.autopilotBtn, 'busy').state = uiconst.UI_DISABLED
        self.sr.autopilotBtn.hint = localization.GetByLabel('UI/Inflight/DeactivateAutopilot')
        self.sr.autopilotBtn.hint += self._GetShortcutForCommand(self.sr.autopilotBtn.cmdName)

    def OnAutoPilotOff(self):
        uiutil.GetChild(self.sr.autopilotBtn, 'busy').state = uiconst.UI_HIDDEN
        self.sr.autopilotBtn.hint = localization.GetByLabel('UI/Inflight/ActivateAutopilot')
        self.sr.autopilotBtn.hint += self._GetShortcutForCommand(self.sr.autopilotBtn.cmdName)

    def OnTacticalOverlayChange(self, isOn):
        activeIndicator = uiutil.GetChild(self.sr.tacticalBtn, 'busy')
        if isOn:
            activeIndicator.state = uiconst.UI_DISABLED
            self.sr.tacticalBtn.sr.hint = localization.GetByLabel('UI/Inflight/HideTacticalOverview')
        else:
            activeIndicator.state = uiconst.UI_HIDDEN
            self.sr.tacticalBtn.sr.hint = localization.GetByLabel('UI/Inflight/ShowTacticalOverlay')

    def OnCloseView(self):
        self.ResetSelf()
        settings.user.ui.Set('selected_shipuicateg', self.sr.selectedcateg)
        if getattr(self, 'cookie', None):
            sm.GetService('inv').Unregister(self.cookie)
            self.cookie = None

    def IsItemHere(self, rec):
        return rec.locationID == session.shipid and rec.categoryID == const.categoryModule and rec.flagID not in (const.flagCargo, const.flagDroneBay)

    def OnInvChange(self, item, change):
        if const.ixFlag in change:
            if cfg.IsShipFittingFlag(item.flagID) or cfg.IsShipFittingFlag(change[const.ixFlag]):
                uthread.new(self.InitSlotsDelayed)

    def ProcessActiveShipChanged(self, *args):
        self.SetupShip()

    def DoBallRemove(self, ball, slimItem, terminal):
        if ball is None:
            return
        log.LogInfo('DoBallRemove::shipui', ball.id)
        if self.ball is not None and ball.id == self.ball.id:
            self.UnhookBall()
        uthread.new(self.UpdateJammersAfterBallRemoval, ball.id)

    def UpdateJammersAfterBallRemoval(self, ballID):
        jams = self.jammers.keys()
        checkJam = 0
        for jammingType in jams:
            jam = self.jammers[jammingType]
            for id in jam.keys():
                sourceBallID, moduleID, targetBallID = id
                if ballID == sourceBallID:
                    del self.jammers[jammingType][id]
                    checkJam = 1

        if checkJam:
            self.CheckJam()

    def DoBallClear(self, solItem):
        self.ball = None

    def ProcessShipEffect(self, godmaStm, effectState):
        dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
        masterID = dogmaLocation.IsInWeaponBank(session.shipid, effectState.itemID)
        if masterID:
            module = self.GetModule(masterID)
        else:
            module = self.GetModule(effectState.itemID)
        if module:
            uthread.new(module.Update, effectState)
            uthread.new(self.CheckOverloadRackBtnState)
        if effectState.error is not None:
            uthread.new(eve.Message, effectState.error[0], effectState.error[1])
        if effectState.effectName == 'online':
            self.UpdateGauges()

    def OnAttributes(self, ch):
        for each in ch:
            if each[0] == 'isOnline':
                self.CheckGroupAllButton()
            if each[0] != 'damage':
                continue
            masterID, damage = sm.GetService('godma').GetStateManager().GetMaxDamagedModuleInGroup(session.shipid, each[1].itemID)
            module = self.GetModule(masterID)
            if module is None:
                continue
            module.SetDamage(damage / module.sr.moduleInfo.hp)

    def ProcessRookieStateChange(self, state):
        if session.solarsystemid and self.sr.wnd:
            if not not (eve.rookieState and eve.rookieState < 21):
                self.state = uiconst.UI_HIDDEN
            else:
                self.state = uiconst.UI_PICKCHILDREN
                self.InitButtons()

    def OnJamStart(self, sourceBallID, moduleID, targetBallID, jammingType, startTime, duration):
        if jammingType not in self.jammers:
            self.jammers[jammingType] = {}
        self.jammers[jammingType][sourceBallID, moduleID, targetBallID] = (startTime, duration)
        self.CheckJam()

    def OnJamEnd(self, sourceBallID, moduleID, targetBallID, jammingType):
        if jammingType in self.jammers:
            id = (sourceBallID, moduleID, targetBallID)
            if id in self.jammers[jammingType]:
                del self.jammers[jammingType][id]
        self.CheckJam()

    def CheckJam(self):
        jams = self.jammers.keys()
        jams.sort()
        for jammingType in jams:
            jam = self.jammers[jammingType]
            sortList = []
            for id in jam.iterkeys():
                sourceBallID, moduleID, targetBallID = id
                if targetBallID == session.shipid:
                    startTime, duration = jam[id]
                    sortList.append((startTime + duration, (sourceBallID,
                      moduleID,
                      targetBallID,
                      jammingType,
                      startTime,
                      duration)))

            if sortList:
                sortList = uiutil.SortListOfTuples(sortList)
                sourceBallID, moduleID, targetBallID, jammingType, startTime, duration = sortList[-1]
                bracketName = sm.GetService('bracket').GetBracketName(sourceBallID)
                self.ShowTimer(jammingType, startTime, duration, localization.GetByLabel('UI/Inflight/JamInfo', bracketName=bracketName, jammingType=self.timerNames.get(jammingType, localization.GetByLabel('UI/Inflight/Nameless'))))
            else:
                self.KillTimer(jammingType)

    def OnShipScanCompleted(self, shipID, capacitorCharge, capacitorCapacity, hardwareList):
        bp = sm.GetService('michelle').GetBallpark()
        if not bp:
            return
        slimItem = bp.slimItems[shipID]
        wndName = localization.GetByLabel('UI/Inflight/ScanWindowName', itemName=uix.GetSlimItemName(slimItem), title=localization.GetByLabel('UI/Inflight/ScanResult'))
        form.ShipScan.CloseIfOpen(windowID=('shipscan', shipID))
        form.ShipScan.Open(windowID=('shipscan', shipID), caption=wndName, shipID=shipID, results=(capacitorCharge, capacitorCapacity, hardwareList))

    def OnCargoScanComplete(self, shipID, cargoList):
        bp = sm.GetService('michelle').GetBallpark()
        if not bp:
            return
        slimItem = bp.slimItems[shipID]
        windowID = ('cargoscanner', shipID)
        wnd = form.CargoScan.Open(windowID=windowID, shipID=shipID, cargoList=cargoList)
        if wnd:
            wnd.LoadResult(cargoList)

    def OnModify(self, op, rec, change):
        t = uthread.new(self.OnModify_thread, op, rec, change)
        t.context = 'ShipUI::OnModify'

    def OnModify_thread(self, op, rec, change):
        lg.Info('shipui', 'OnModify', op, change, rec)
        if not rec:
            return
        if cfg.invtypes.Get(rec.typeID).categoryID != const.categoryCharge:
            lg.Warn('shipui', 'OnModify: not a charge?')
            return
        haveThisCharge = 0
        for flag, slot in self.sr.slotsByFlag.iteritems():
            if slot and slot.sr.module.charge and slot.sr.module.charge.itemID == rec.itemID:
                haveThisCharge = 1
                break

        slot = self.sr.slotsByFlag.get(rec.flagID, None)
        if slot and slot.sr.module:
            if op == 'r' or rec.stacksize == 0:
                slot.sr.module.SetCharge(None)
            elif slot.sr.module.charge and slot.sr.module.charge.itemID and slot.sr.module.charge.itemID != rec.itemID:
                lg.Info('shipui', 'Residual update in parting missile-- ignoring')
            else:
                slot.sr.module.SetCharge(rec)
        elif haveThisCharge:
            self.sr.slotsByFlag[flag].SetCharge(None)

    def UnhookBall(self):
        self.ball = None

    def Init(self, ball = None):
        self.SetupShip(ball)

    def SetupShip(self, ball = None):
        if self.setupShipTasklet is not None:
            self.setupShipTasklet.kill()
        self.setupShipTasklet = uthread.new(self._SetupShip, ball)

    @telemetry.ZONE_METHOD
    def _SetupShip(self, ball = None):
        if self.destroyed or self.initing or not self.shipuiReady:
            return
        self.initing = True
        try:
            if ball is None:
                bp = sm.GetService('michelle').GetBallpark()
                if bp is None or session.shipid is None:
                    self.initing = False
                    return
                ball = bp.GetBall(session.shipid)
                if ball is None:
                    return
            dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
            if session.shipid is None or not dogmaLocation.IsItemLoaded(session.shipid):
                return
            ship = sm.GetService('godma').GetItem(session.shipid)
            if ship is None:
                raise RuntimeError('ShipUI being inited with no ship state!')
            self.ball = ball
            if not (eve.rookieState and eve.rookieState < 21) and not sm.GetService('viewState').IsViewActive('planet') and not (eve.hiddenUIState and 'shipui' in eve.hiddenUIState):
                self.state = uiconst.UI_PICKCHILDREN
            if not self.sr.gaugetimer:
                uthread.new(self.UpdateGauges)
            self.sr.rampTimers = {}
            self.InitSpeed()
            self.InitSlots()
            self.InitButtons()
            self.SetButtonState()
            self.CheckExpandBtns()
            self.CheckControl()
            blue.pyos.synchro.SleepWallclock(200)
        finally:
            self.initing = False

        self.invReady = True

    @telemetry.ZONE_METHOD
    def InitSpeed(self):
        if self.speedInited or not self.sr.wnd:
            return
        for btnname in ['stopButton', 'maxspeedButton']:
            newBtn = uiutil.GetChild(self.sr.wnd, btnname)
            newBtn.OnClick = (self.ClickSpeedBtn, newBtn)
            if btnname == 'maxspeedButton':
                newBtn.hint = localization.GetByLabel('UI/Inflight/SetFullSpeed', maxSpeed=self.FormatSpeed(self.ball.maxVelocity))
                newBtn.OnMouseEnter = self.CheckSpeedHint
            else:
                newBtn.hint = localization.GetByLabel('UI/Inflight/StopTheShip')
            self.sr.Set(btnname, newBtn)

        self.sr.speedGauge = self.sr.wnd.GetChild('speedNeedle')
        self.sr.speedGaugeParent = self.sr.wnd.GetChild('speedGaugeParent')
        self.sr.speedGaugeParent.OnClick = self.ClickSpeedoMeter
        self.sr.speedGaugeParent.OnMouseMove = self.CheckSpeedHint
        self.sr.speedStatus = uicls.EveLabelSmall(text='', parent=self.sr.speedGaugeParent.parent.parent, left=0, top=127, color=(0.0, 0.0, 0.0, 1.0), width=100, state=uiconst.UI_DISABLED, idx=0, shadowOffset=(0, 0), align=uiconst.CENTERTOP)
        self.speedInited = 1
        uthread.new(self.SetSpeed, self.ball.speedFraction, initing=1)
        if self.sr.speedtimer is None:
            self.lastSpeed = None
            self.sr.speedtimer = uthread.new(self.UpdateSpeedThread)

    def ClickSpeedBtn(self, btn, *args):
        if eve.rookieState and eve.rookieState < 22:
            return
        if btn.name == 'stopButton':
            self.StopShip()
        elif btn.name == 'maxspeedButton':
            bp = sm.GetService('michelle').GetBallpark()
            rbp = sm.GetService('michelle').GetRemotePark()
            if bp:
                ownBall = bp.GetBall(session.shipid)
                if ownBall and rbp is not None and ownBall.mode == destiny.DSTBALL_STOP:
                    if not sm.GetService('autoPilot').GetState():
                        direction = trinity.TriVector(0.0, 0.0, 1.0)
                        currentDirection = self.ball.GetQuaternionAt(blue.os.GetSimTime())
                        direction.TransformQuaternion(currentDirection)
                        rbp.CmdGotoDirection(direction.x, direction.y, direction.z)
            if rbp is not None:
                rbp.CmdSetSpeedFraction(1.0)
                sm.GetService('logger').AddText(localization.GetByLabel('UI/Inflight/SpeedChangedTo', speed=self.FormatSpeed(self.ball.maxVelocity)), 'notify')
                sm.GetService('gameui').Say(localization.GetByLabel('UI/Inflight/SpeedChangedTo', speed=self.FormatSpeed(self.ball.maxVelocity)))
                self.wantedspeed = 1.0
            else:
                self.wantedspeed = None

    def GetSpeedPortion(self):
        l, t, w, h = self.sr.wnd.GetAbsolute()
        centerX = l + w / 2
        centerY = t + h / 2
        y = float(uicore.uilib.y - centerY)
        x = float(uicore.uilib.x - centerX)
        if x and y:
            angle = math.atan(x / y)
            deg = angle / math.pi * 180.0
            factor = (45.0 + deg) / 90.0
            if factor < 0.05:
                return 0.0
            elif factor > 0.95:
                return 1.0
            else:
                return factor
        return 0.5

    def ClickSpeedoMeter(self, *args):
        uthread.new(self.SetSpeed, self.GetSpeedPortion())

    def CheckSpeedHint(self, *args):
        if not self.ball:
            return
        mo = uicore.uilib.mouseOver
        ms = self.sr.Get('maxspeedButton')
        if mo == self.sr.speedGaugeParent:
            portion = self.GetSpeedPortion()
            parent = self.sr.speedGaugeParent
            speed = self.ball.GetVectorDotAt(blue.os.GetSimTime()).Length()
            if self.ball.mode == destiny.DSTBALL_WARP:
                hint = localization.GetByLabel('UI/Inflight/ShowWarpSpeed', speed=util.FmtDist(speed, 2))
                hint += '<br>' + localization.GetByLabel('UI/Inflight/CanNotChangeSpeedWhileWarping')
            else:
                fmtSpeed = self.FormatSpeed(speed)
                hint = localization.GetByLabel('UI/Inflight/CurrentSpeed', speed=fmtSpeed)
                hint += '<br>' + localization.GetByLabel('UI/Inflight/ClickToSetSpeedTo', speed=self.FormatSpeed(portion * self.ball.maxVelocity))
            parent.hint = hint
            uicore.UpdateHint(parent)
        elif ms and not ms.destroyed and mo == ms:
            ms.hint = localization.GetByLabel('UI/Inflight/SetFullSpeed', maxSpeed=self.FormatSpeed(self.ball.maxVelocity))
            uicore.UpdateHint(ms)

    def FormatSpeed(self, speed):
        if speed < 100:
            return localization.GetByLabel('UI/Inflight/MetersPerSecond', speed=round(speed, 1))
        return localization.GetByLabel('UI/Inflight/MetersPerSecond', speed=int(speed))

    @telemetry.ZONE_FUNCTION
    def InitCapacitor(self, maxcap):
        self.capacitorDone = 0
        self.capacity = float(maxcap)
        self.lastsetcapacitor = None
        if self.sr.powercore is None:
            return
        self.sr.powercore.Flush()
        self.powerCells = []
        numcol = min(18, int(maxcap / 50))
        rotstep = 360.0 / max(1, numcol)
        colWidth = max(12, min(16, numcol and int(192 / numcol)))
        for i in range(numcol):
            powerColumn = uicls.Transform(parent=self.sr.powercore, name='powerColumn', pos=(0,
             0,
             colWidth,
             56), align=uiconst.CENTER, state=uiconst.UI_DISABLED, rotation=mathUtil.DegToRad(i * -rotstep), idx=0)
            for ci in xrange(4):
                newcell = uicls.Sprite(parent=powerColumn, name='pmark', pos=(0,
                 ci * 5,
                 10 - ci * 2,
                 7), align=uiconst.CENTERTOP, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/ShipUI/capacitorCell_2.png', color=(0, 0, 0, 0))
                self.powerCells.insert(0, newcell)

        self.capacitorDone = 1

    def GetModuleForFKey(self, key):
        slot = int(key[1:])
        gidx = (slot - 1) / 8
        sidx = (slot - 1) % 8
        slot = self.sr.slotsByOrder.get((gidx, sidx), None)
        if slot and slot.sr.module and slot.sr.module.state == uiconst.UI_NORMAL:
            return slot.sr.module

    def GetModule(self, moduleID):
        return self.sr.modules.get(moduleID, None)

    def Hide(self):
        self.state = uiconst.UI_HIDDEN

    def Show(self):
        if not (eve.rookieState and eve.rookieState < 21):
            self.state = uiconst.UI_PICKCHILDREN

    def OnMouseEnter(self, *args):
        uicore.layer.inflight.HideTargetingCursor()

    def FormatReadoutValue(self, portion, total):
        if settings.user.ui.Get('readoutType', 1):
            if total == 0:
                return '0.0%'
            return '%s%%' % util.FmtAmt(portion / total * 100.0, showFraction=1)
        else:
            return '%s/%s' % (util.FmtAmt(portion, showFraction=1), util.FmtAmt(total, showFraction=1))

    def GetMenu(self):
        if not hasattr(session, 'shipid'):
            return []
        return sm.GetService('menu').CelestialMenu(session.shipid)

    @telemetry.ZONE_FUNCTION
    def UpdateGauges(self):
        if self.updatingGauges or self.destroyed:
            return
        try:
            self.updatingGauges = True
            ship = sm.GetService('godma').GetItem(session.shipid)
            if not ship:
                return
            if self.destroyed:
                return
            if not hasattr(self, 'capacity'):
                return
            maxcap = ship.capacitorCapacity
            if self.capacity != maxcap:
                self.InitCapacitor(maxcap)
            self.SetPower(ship.charge, float(maxcap))
            structure = max(0.0, min(1.0, round(1.0 - ship.damage / ship.hp, 2)))
            armor = 0.0
            if ship.armorHP != 0:
                armor = max(0.0, min(1.0, round(1.0 - ship.armorDamage / ship.armorHP, 2)))
            shield = 0.0
            if ship.shieldCapacity != 0:
                shield = max(0.0, min(1.0, round(ship.shieldCharge / ship.shieldCapacity, 2)))
            heatLow = ship.heatLow / ship.heatCapacityLow
            heatMed = ship.heatMed / ship.heatCapacityMed
            heatHi = ship.heatHi / ship.heatCapacityHi
            try:
                self.structureGauge.hint = localization.GetByLabel('UI/Inflight/StructureStatus', portion=int(structure * 100), left=int(max(0, ship.hp - ship.damage)), max=int(ship.hp))
                self.armorGauge.hint = localization.GetByLabel('UI/Inflight/ArmorStatus', portion=int(armor * 100), left=int(max(0, ship.armorHP - ship.armorDamage)), max=int(ship.armorHP))
                self.shieldGauge.hint = localization.GetByLabel('UI/Inflight/ShieldStatus', portion=int(shield * 100), left=int(ship.shieldCharge), max=int(ship.shieldCapacity))
                self.sr.heatPick.hint = localization.GetByLabel('UI/Inflight/HeatStatus', low=heatLow * 100, med=heatMed * 100, high=heatHi * 100)
                mo = uicore.uilib.mouseOver
                if mo in (self.structureGauge,
                 self.armorGauge,
                 self.shieldGauge,
                 self.sr.powercore):
                    uicore.UpdateHint(mo)
                if self.sr.gaugeReadout and self.sr.gaugeReadout.state != uiconst.UI_HIDDEN:
                    if settings.user.ui.Get('readoutType', 1):
                        self.sr.gaugeReadout.sr.Get('shield').text = localization.GetByLabel('UI/Common/Formatting/Percentage', percentage=shield * 100)
                        self.sr.gaugeReadout.sr.Get('armor').text = localization.GetByLabel('UI/Common/Formatting/Percentage', percentage=armor * 100)
                        self.sr.gaugeReadout.sr.Get('structure').text = localization.GetByLabel('UI/Common/Formatting/Percentage', percentage=structure * 100)
                    else:
                        self.sr.gaugeReadout.sr.Get('shield').text = localization.GetByLabel('UI/Inflight/GaugeAbsolute', left=ship.shieldCharge, total=ship.shieldCapacity)
                        self.sr.gaugeReadout.sr.Get('armor').text = localization.GetByLabel('UI/Inflight/GaugeAbsolute', left=max(0, ship.armorHP - ship.armorDamage), total=ship.armorHP)
                        self.sr.gaugeReadout.sr.Get('structure').text = localization.GetByLabel('UI/Inflight/GaugeAbsolute', left=max(0, ship.hp - ship.damage), total=ship.hp)
                props = [(self.lastStructure,
                  structure,
                  self.UpdateShieldArmorStructureGauge,
                  (self.structureGauge,)),
                 (self.lastArmor,
                  armor,
                  self.UpdateShieldArmorStructureGauge,
                  (self.armorGauge,)),
                 (self.lastShield,
                  shield,
                  self.UpdateShieldArmorStructureGauge,
                  (self.shieldGauge,)),
                 (self.lastLowHeat,
                  heatLow,
                  self.UpdateLowHeatGauge,
                  ()),
                 (self.lastMedHeat,
                  heatMed,
                  self.UpdateMedHeatGauge,
                  ()),
                 (self.lastHiHeat,
                  heatHi,
                  self.UpdateHiHeatGauge,
                  ())]
            except Exception as e:
                log.LogWarn(e)
                sys.exc_clear()
                return

            start, ndt = blue.os.GetWallclockTime(), 0.0
            while ndt != 1.0:
                ndt = max(ndt, min(blue.os.TimeDiffInMs(start, blue.os.GetWallclockTime()) / 500.0, 1.0))
                for oldValue, newValue, updateFunc, functionArgs in props:
                    if oldValue is None:
                        lerped = newValue
                    elif oldValue == newValue:
                        continue
                    else:
                        lerped = mathUtil.Lerp(oldValue, newValue, ndt)
                    updateFunc(lerped, *functionArgs)

                blue.pyos.synchro.Yield()

            self.lastStructure = structure
            self.lastArmor = armor
            self.lastShield = shield
            self.lastLowHeat = heatLow
            self.lastMedHeat = heatMed
            self.lastHiHeat = heatHi
        finally:
            self.updatingGauges = False
            if self.shipuiReady and not self.sr.gaugetimer and hasattr(self, 'UpdateGauges'):
                self.sr.gaugetimer = base.AutoTimer(500, self.UpdateGauges)

    def UpdateShieldArmorStructureGauge(self, value, gauge, *args):
        gauge.textureSecondary.rotation = math.pi * (1.0 - value)

    def UpdateLowHeatGauge(self, value, *args):
        self.sr.lowHeatGauge.SetRotation(mathUtil.DegToRad(-2.0 - 56.0 * value))
        textureIndex = self.GetHeatGaugeTextureIndex(value)
        underlay = self.sr.heatLowUnderlay
        if underlay.heatTextureIndex != textureIndex:
            underlay.LoadTexture(LOW_HEAT_GAUGE_TEXTURES[textureIndex])
            underlay.heatTextureIndex = textureIndex

    def UpdateMedHeatGauge(self, value, *args):
        self.sr.medHeatGauge.SetRotation(mathUtil.DegToRad(-62.0 - 56.0 * value))
        textureIndex = self.GetHeatGaugeTextureIndex(value)
        underlay = self.sr.heatMedUnderlay
        if underlay.heatTextureIndex != textureIndex:
            underlay.LoadTexture(MED_HEAT_GAUGE_TEXTURES[textureIndex])
            underlay.heatTextureIndex = textureIndex

    def UpdateHiHeatGauge(self, value, *args):
        self.sr.hiHeatGauge.SetRotation(mathUtil.DegToRad(-122.0 - 56.0 * value))
        textureIndex = self.GetHeatGaugeTextureIndex(value)
        underlay = self.sr.heatHiUnderlay
        if underlay.heatTextureIndex != textureIndex:
            underlay.LoadTexture(HI_HEAT_GAUGE_TEXTURES[textureIndex])
            underlay.heatTextureIndex = textureIndex

    def GetHeatGaugeTextureIndex(self, value):
        if value <= 0.125:
            textureIndex = 0
        elif value <= 0.375:
            textureIndex = 1
        elif value <= 0.625:
            textureIndex = 2
        elif value <= 0.875:
            textureIndex = 3
        else:
            textureIndex = 4
        return textureIndex

    @telemetry.ZONE_FUNCTION
    def UpdateSpeedThread(self):
        intervalTime = 133
        while not self.destroyed:
            blue.synchro.Sleep(intervalTime)
            if self.ball and self.ball.ballpark and self.sr.speedGauge and not self.sr.speedGauge.destroyed:
                speed = self.ball.GetVectorDotAt(blue.os.GetSimTime()).Length()
                try:
                    realSpeed = max(0.0, min(1.0, speed / self.ball.maxVelocity))
                except:
                    sys.exc_clear()
                    realSpeed = 0.0

            else:
                continue
            speedGauge = self.sr.speedGauge
            lastSpeed = getattr(self, 'lastSpeed', None)
            degRot = 90.0 * realSpeed
            if lastSpeed != speed:
                speedGauge.SetRotation(mathUtil.DegToRad(45.0 + degRot))
                if not (self.ball and self.ball.ballpark):
                    continue
                if self.ball.mode == destiny.DSTBALL_WARP:
                    fmtSpeed = localization.GetByLabel('UI/Inflight/WarpSpeedNotification', warpingMessage=localization.GetByLabel('UI/Inflight/Scanner/Warping'))
                else:
                    fmtSpeed = '<center>' + self.FormatSpeed(speed)
                if self.sr.speedStatus.text != fmtSpeed:
                    self.sr.speedStatus.text = fmtSpeed
                self.CheckSpeedHint()
                self.lastSpeed = speed
                intervalTime = 66
            else:
                intervalTime = 133

        self.sr.speedtimer = None

    def StopShip(self, *args):
        uicore.cmd.CmdStopShip()
        self.wantedspeed = 0.0

    def SetSpeed(self, speed, initing = 0):
        if self.destroyed:
            return
        if eve.rookieState and eve.rookieState < 22:
            return
        if not isinstance(speed, float):
            log.LogWarn('SetSpeed() got called with something other than a float as the speed parameter. Ignoring...')
            return
        if (not self.ball or self.ball.mode == destiny.DSTBALL_WARP) and speed > 0:
            return
        if self.ball and self.ball.ballpark is None:
            self.UnhookBall()
            return
        if not initing and self.wantedspeed is not None and int(self.ball.speedFraction * 1000) == int(speed * 1000) == int(self.wantedspeed * 1000) and speed > 0:
            return
        if speed <= 0.0:
            self.StopShip()
        elif speed != self.wantedspeed:
            rbp = sm.GetService('michelle').GetRemotePark()
            bp = sm.GetService('michelle').GetBallpark()
            if bp and not initing:
                ownBall = bp.GetBall(session.shipid)
                if ownBall and rbp is not None and ownBall.mode == destiny.DSTBALL_STOP:
                    if not sm.GetService('autoPilot').GetState():
                        direction = trinity.TriVector(0.0, 0.0, 1.0)
                        currentDirection = self.ball.GetQuaternionAt(blue.os.GetSimTime())
                        direction.TransformQuaternion(currentDirection)
                        rbp.CmdGotoDirection(direction.x, direction.y, direction.z)
            if rbp is not None:
                rbp.CmdSetSpeedFraction(min(1.0, speed))
                if not initing and self.ball:
                    sm.GetService('logger').AddText(localization.GetByLabel('UI/Inflight/SpeedChangedTo', speed=self.FormatSpeed(speed * self.ball.maxVelocity)), 'notify')
                    sm.GetService('gameui').Say(localization.GetByLabel('UI/Inflight/SpeedChangedTo', speed=self.FormatSpeed(speed * self.ball.maxVelocity)))
        if not initing:
            self.wantedspeed = max(speed, 0.0)
        if not self.sr.speedtimer:
            self.sr.speedtimer = uthread.new(self.UpdateSpeedThread)

    @telemetry.ZONE_FUNCTION
    def SetPower(self, load, maxcap):
        if not self.sr.powercore or self.sr.powercore.destroyed:
            return
        if self.capacity is not None:
            portion = self.capacity * max(0.0, min(1.0, maxcap and float(load / maxcap) or maxcap))
            if portion:
                if self.sr.powercore and not self.sr.powercore.destroyed:
                    self.sr.powercore.hint = localization.GetByLabel('UI/Inflight/CapacitorStatus', portion=int(round(portion / self.capacity * 100)), left=int(portion), max=int(self.capacity))
        proportion = max(0.0, min(1.0, round(maxcap and load / maxcap or maxcap, 2)))
        if self.lastsetcapacitor == proportion:
            return
        sm.ScatterEvent('OnCapacitorChange', load, maxcap, proportion)
        good = trinity.TriColor(*CELLCOLOR)
        bad = trinity.TriColor(70 / 256.0, 26 / 256.0, 13.0 / 256.0)
        bad.Scale(1.0 - proportion)
        good.Scale(proportion)
        if self.capacity is not None and self.capacitorDone and self.powerCells:
            totalCells = len(self.powerCells)
            visible = max(0, min(totalCells, int(proportion * totalCells)))
            for ci, each in enumerate(self.powerCells):
                if ci >= visible:
                    each.SetRGB(0.5, 0.5, 0.5, 0.5)
                    each.glowColor = (0, 0, 0, 1)
                    each.glowFactor = 0.0
                    each.glowExpand = 0.1
                    each.shadowOffset = (0, 0)
                else:
                    each.SetRGB(0.125, 0.125, 0.125, 1)
                    each.glowColor = (bad.r + good.r,
                     bad.g + good.g,
                     bad.b + good.b,
                     1.0)
                    each.glowFactor = 0.0
                    each.glowExpand = 0.1
                    each.shadowOffset = (0, 1)

            if self.sr.powerblink is None:
                self.sr.powerblink = uicls.Sprite(parent=self, name='powerblink', state=uiconst.UI_HIDDEN, texturePath='res:/UI/Texture/classes/ShipUI/capacitorCellGlow.png', align=uiconst.CENTERTOP, blendMode=trinity.TR2_SBM_ADDX2, color=CELLCOLOR)
                r, g, b = CELLCOLOR
                uicore.effect.BlinkSpriteRGB(self.sr.powerblink, r, g, b, 750, None)
            if visible != 0 and visible < totalCells:
                active = self.powerCells[visible - 1]
                uiutil.Transplant(self.sr.powerblink, active.parent, 0)
                self.sr.powerblink.top = active.top
                self.sr.powerblink.width = active.width + 3
                self.sr.powerblink.height = active.height
                self.sr.powerblink.state = uiconst.UI_DISABLED
            else:
                self.sr.powerblink.state = uiconst.UI_HIDDEN
            self.lastsetcapacitor = proportion

    def OnF(self, sidx, gidx):
        slot = self.sr.slotsByOrder.get((gidx, sidx), None)
        if slot and slot.sr.module and slot.sr.module.state == uiconst.UI_NORMAL:
            uthread.new(slot.sr.module.Click)
        else:
            uthread.new(eve.Message, 'Disabled')

    def OnFKeyOverload(self, sidx, gidx):
        slot = self.sr.slotsByOrder.get((gidx, sidx), None)
        if slot and slot.sr.module and slot.sr.module.state == uiconst.UI_NORMAL:
            if hasattr(slot.sr.module, 'ToggleOverload'):
                uthread.new(slot.sr.module.ToggleOverload)
        else:
            uthread.new(eve.Message, 'Disabled')

    def OnReloadAmmo(self):
        modulesByCharge = {}
        for module in self.sr.modules.itervalues():
            if not cfg.IsChargeCompatible(module.sr.moduleInfo):
                continue
            chargeTypeID, chargeQuantity, roomForReload = module.GetChargeReloadInfo()
            if chargeTypeID in modulesByCharge:
                modulesByCharge[chargeTypeID].append(module)
            else:
                modulesByCharge[chargeTypeID] = [module]

        dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
        for chargeTypeID, modules in modulesByCharge.iteritems():
            ammoList = {}
            for typeID, ammoInfo in dogmaLocation.GetMatchingAmmo(session.shipid, modules[0].sr.moduleInfo.itemID).iteritems():
                if typeID != chargeTypeID:
                    continue
                for item in ammoInfo.singletons:
                    ammoList[item.itemID] = item.stacksize

                for item in ammoInfo.nonSingletons:
                    ammoList[item.itemID] = item.stacksize

            for module in modules:
                maxItemID = 0
                chargeTypeID, chargeQuantity, roomForReload = module.GetChargeReloadInfo()
                bestItemID = None
                for itemID, quant in ammoList.iteritems():
                    if quant >= roomForReload:
                        if not bestItemID or quant < ammoList[bestItemID]:
                            bestItemID = itemID
                    if not maxItemID or quant > ammoList[maxItemID]:
                        maxItemID = itemID

                bestItemID = bestItemID or maxItemID
                if bestItemID:
                    quant = min(roomForReload, ammoList[maxItemID])
                    uthread.new(module.AutoReload, 1, bestItemID, quant)
                    ammoList[bestItemID] -= quant

    def OnSafeLogoffTimerStarted(self, safeLogoffTime):
        if self.logoffTimer is not None:
            self.logoffTimer.Close()
        self.logoffTimer = uicls.SafeLogoffTimer(parent=uicore.layer.abovemain, logoffTime=safeLogoffTime)

    def OnSafeLogoffActivated(self):
        if self.logoffTimer is not None:
            self.logoffTimer.timer.SetText('0.0')
            self.logoffTimer.timer.SetTextColor(util.Color.GREEN)
        sm.GetService('clientStatsSvc').OnProcessExit()

    def OnSafeLogoffAborted(self, reasonCode):
        self.AbortSafeLogoffTimer()
        eve.Message('CustomNotify', {'notify': localization.GetByLabel(reasonCode)})

    def OnSafeLogoffFailed(self, failedConditions):
        self.AbortSafeLogoffTimer()
        eve.Message('CustomNotify', {'notify': '<br>'.join([localization.GetByLabel('UI/Inflight/SafeLogoff/ConditionsFailedHeader')] + [ localization.GetByLabel(error) for error in failedConditions ])})

    def AbortSafeLogoffTimer(self):
        if self.logoffTimer is not None:
            self.logoffTimer.AbortLogoff()
            self.logoffTimer = None

    def GetModuleGroupDamage(self, itemID, *args):
        dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
        moduleDamage = dogmaLocation.GetAccurateAttributeValue(itemID, const.attributeDamage)
        masterID = dogmaLocation.IsInWeaponBank(util.GetActiveShip(), itemID)
        if not masterID:
            return moduleDamage
        allModulesInBank = dogmaLocation.GetModulesInBank(util.GetActiveShip(), masterID)
        maxDamage = moduleDamage
        for slaveID in allModulesInBank:
            damage = dogmaLocation.GetAccurateAttributeValue(slaveID, const.attributeDamage)
            if damage > maxDamage:
                maxDamage = damage

        return maxDamage


class SafeLogoffTimer(uicls.Container):
    __guid__ = 'uicls.SafeLogoffTimer'
    default_align = uiconst.CENTERTOP
    default_state = uiconst.UI_NORMAL
    default_width = 300
    default_height = 130
    default_top = 300
    default_bgColor = (0.05, 0.05, 0.05, 0.75)

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        self.SetHint(localization.GetByLabel('UI/Inflight/SafeLogoffTimerHint'))
        uicls.Frame(parent=self)
        self.logoffTime = attributes.logoffTime
        topCont = uicls.Container(parent=self, align=uiconst.TOTOP, height=30)
        timerCont = uicls.Container(parent=self, align=uiconst.TOTOP, height=70)
        bottomCont = uicls.Container(parent=self, align=uiconst.TOALL)
        self.caption = uicls.Label(parent=topCont, fontsize=24, bold=True, align=uiconst.CENTERTOP, text=localization.GetByLabel('UI/Inflight/SafeLogoffTimerCaption'), top=4)
        self.timer = uicls.Label(parent=timerCont, align=uiconst.CENTER, fontsize=60, color=util.Color.YELLOW, bold=True)
        self.button = uicls.Button(parent=bottomCont, label=localization.GetByLabel('UI/Inflight/SafeLogoffAbortLogoffLabel'), align=uiconst.CENTER, func=self.AbortSafeLogoff)
        self.UpdateLogoffTime()
        uthread.new(self.UpdateLogoffTime_Thread)

    def UpdateLogoffTime(self):
        timeLeft = self.logoffTime - blue.os.GetSimTime()
        self.timer.text = '%.1f' % max(0.0, timeLeft / float(const.SEC))

    def UpdateLogoffTime_Thread(self):
        self.countingDown = True
        while self.countingDown:
            self.UpdateLogoffTime()
            blue.pyos.synchro.SleepSim(100)

    def AbortLogoff(self, *args):
        self.countingDown = False
        uthread.new(self.AbortLogoff_Thread)

    def AbortLogoff_Thread(self):
        blue.pyos.synchro.SleepSim(1000)
        uicore.animations.FadeOut(self, duration=1.0, sleep=True)
        self.Close()

    def AbortSafeLogoff(self, *args):
        shipAccess = sm.GetService('gameui').GetShipAccess()
        shipAccess.AbortSafeLogoff()
        self.AbortLogoff()

    def OnClose(self, *args):
        self.countingDown = False


class SpaceLayer(uicls.LayerCore):
    __guid__ = 'form.SpaceLayer'

    def OnCloseView(self):
        sm.GetService('tactical').CleanUp()
        sm.GetService('target').CleanUp()
        sm.GetService('bracket').CleanUp()

    def OnOpenView(self):
        pass


class NotifySettingsWindow(uicls.Window):
    __guid__ = 'form.NotifySettingsWindow'
    default_windowID = 'NotifySettingsWindow'
    default_fixedHeight = 170
    default_fixedWidth = 320

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        self.SetWndIcon(None)
        self.SetTopparentHeight(0)
        self.SetCaption(localization.GetByLabel('UI/Inflight/NotifyAudioAlert'))
        self.MakeUnResizeable()
        self.SetupUi()

    def SetupUi(self):
        notifydata = [{'checkboxLabel': localization.GetByLabel('UI/Inflight/NotifyShield'),
          'checkboxName': 'shieldNotification',
          'checkboxSetting': 'shieldNotificationEnabled',
          'checkboxDefault': 1,
          'sliderName': 'shield',
          'sliderSetting': ('shieldThreshold', ('user', 'notifications'), const.defaultShieldThreshold)},
         {'checkboxLabel': localization.GetByLabel('UI/Inflight/NotifyArmor'),
          'checkboxName': 'armourNotification',
          'checkboxSetting': 'armourNotificationEnabled',
          'checkboxDefault': 1,
          'sliderName': 'armour',
          'sliderSetting': ('armourThreshold', ('user', 'notifications'), const.defaultArmourThreshold)},
         {'checkboxLabel': localization.GetByLabel('UI/Inflight/NotifyHull'),
          'checkboxName': 'hullNotification',
          'checkboxDefault': 1,
          'checkboxSetting': 'hullNotificationEnabled',
          'sliderName': 'hull',
          'sliderSetting': ('hullThreshold', ('user', 'notifications'), const.defaultHullThreshold)},
         {'checkboxLabel': localization.GetByLabel('UI/Inflight/NotifyCapacitor'),
          'checkboxName': 'capacitorNotification',
          'checkboxDefault': 1,
          'checkboxSetting': 'capacitorNotificationEnabled',
          'sliderName': 'capacitor',
          'sliderSetting': ('capacitorThreshold', ('user', 'notifications'), const.defaultCapacitorThreshold)}]
        labelWidth = 150
        mainContainer = uicls.Container(name='mainContainer', parent=self.sr.main, align=uiconst.TOALL)
        for each in notifydata:
            notifytop = uicls.Container(name='notifytop', parent=mainContainer, align=uiconst.TOTOP, pos=(const.defaultPadding,
             const.defaultPadding,
             0,
             32))
            uicls.Checkbox(text=each['checkboxLabel'], parent=notifytop, configName=each['checkboxSetting'], retval=None, prefstype=('user', 'notifications'), checked=settings.user.notifications.Get(each['checkboxSetting'], each['checkboxDefault']), callback=self.CheckBoxChange, align=uiconst.TOLEFT, pos=(const.defaultPadding,
             0,
             labelWidth,
             0))
            _par = uicls.Container(name=each['sliderName'] + '_slider', align=uiconst.TORIGHT, width=labelWidth, parent=notifytop, pos=(10, 0, 160, 0))
            par = uicls.Container(name=each['sliderName'] + '_slider_sub', align=uiconst.TOTOP, parent=_par, pos=(0,
             const.defaultPadding,
             0,
             10))
            slider = xtriui.Slider(parent=par)
            lbl = uicls.EveLabelSmall(text='', parent=_par, align=uiconst.TOTOP, name='label', state=uiconst.UI_PICKCHILDREN, width=labelWidth, left=const.defaultPadding, top=1 + const.defaultPadding, tabs=[labelWidth - 22])
            lbl._tabMargin = 2
            slider.label = lbl
            slider.Startup(each['sliderName'], 0.0, 1.0, each['sliderSetting'], localization.GetByLabel('UI/Inflight/Threshold'))

    def CheckBoxChange(self, checkbox):
        if checkbox.name == 'shieldNotificationEnabled':
            settings.user.notifications.Set('shieldNotificationEnabled', checkbox.checked)
            if checkbox.checked:
                sm.GetService('audio').SendUIEvent(const.damageSoundNotifications[0])
        elif checkbox.name == 'armourNotificationEnabled':
            settings.user.notifications.Set('armourNotificationEnabled', checkbox.checked)
            if checkbox.checked:
                sm.GetService('audio').SendUIEvent(const.damageSoundNotifications[1])
        elif checkbox.name == 'hullNotificationEnabled':
            settings.user.notifications.Set('hullNotificationEnabled', checkbox.checked)
            if checkbox.checked:
                sm.GetService('audio').SendUIEvent(const.damageSoundNotifications[2])
        elif checkbox.name == 'capacitorNotificationEnabled':
            settings.user.notifications.Set('capacitorNotificationEnabled', checkbox.checked)
            if checkbox.checked:
                sm.GetService('audio').SendUIEvent(const.damageSoundNotifications[3])


class ShipUIContainer(uicls.Container):
    __guid__ = 'uicls.ShipUIContainer'
    default_left = 0
    default_top = 0
    default_width = 500
    default_height = 500
    default_name = 'shipui'
    default_align = uiconst.TOPLEFT
    default_state = uiconst.UI_PICKCHILDREN

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        overlayContainer = uicls.Container(parent=self, name='overlayContainer', pos=(0, 0, 256, 256), align=uiconst.CENTER, state=uiconst.UI_PICKCHILDREN)
        expandBtnRight = uicls.Sprite(parent=overlayContainer, name='expandBtnRight', pos=(170, 122, 28, 28), align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL, texturePath='res:/UI/Texture/classes/ShipUI/expandBtnRight.png')
        expandBtnLeft = uicls.Sprite(parent=overlayContainer, name='expandBtnLeft', pos=(56, 122, 28, 28), align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL, texturePath='res:/UI/Texture/classes/ShipUI/expandBtnLeft.png')
        self.optionsCont = uicls.Container(parent=overlayContainer, name='optionsCont', pos=(180, 180, 16, 16), align=uiconst.TOPLEFT, state=uiconst.UI_PICKCHILDREN)
        stopButton = uicls.Sprite(parent=overlayContainer, name='stopButton', pos=(75, 155, 12, 12), align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL, texturePath='res:/UI/Texture/classes/ShipUI/minus.png')
        maxspeedButton = uicls.Sprite(parent=overlayContainer, name='maxspeedButton', pos=(168, 155, 12, 12), align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL, texturePath='res:/UI/Texture/classes/ShipUI/plus.png')
        mainDot = uicls.Sprite(parent=self, name='mainDot', pos=(0, 0, 160, 160), align=uiconst.CENTER, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/ShipUI/mainDOT.png', spriteEffect=trinity.TR2_SFX_DOT, blendMode=trinity.TR2_SBM_ADD)
        mainContainer = uicls.Container(parent=self, name='mainContainer', pos=(0, 0, 256, 256), align=uiconst.CENTER, state=uiconst.UI_PICKCHILDREN)
        powercore = uicls.Container(parent=mainContainer, name='powercore', pos=(0, -1, 60, 60), align=uiconst.CENTER, state=uiconst.UI_NORMAL, pickRadius=30)
        subContainer = uicls.Container(parent=self, name='subContainer', pos=(0, 0, 160, 160), align=uiconst.CENTER, state=uiconst.UI_PICKCHILDREN)
        block_64 = uicls.Container(parent=subContainer, name='block_64', pos=(0, 0, 64, 64), align=uiconst.CENTER, state=uiconst.UI_NORMAL, pickRadius=32)
        circlepickclipper_92 = uicls.Container(parent=subContainer, name='circlepickclipper_92', pos=(0, 0, 92, 92), align=uiconst.CENTER, state=uiconst.UI_PICKCHILDREN, pickRadius=46)
        heatPick = uicls.Container(parent=circlepickclipper_92, name='heatPick', pos=(0, 0, 92, 46), align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL)
        subpar = uicls.Container(parent=circlepickclipper_92, name='subpar', pos=(0, 0, 60, 80), align=uiconst.CENTER, state=uiconst.UI_PICKCHILDREN)
        powerPick = uicls.Container(parent=subpar, name='powerPick', pos=(6, 55, 48, 20), align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL)
        cpuPick = uicls.Container(parent=subpar, name='cpuPick', pos=(0, 70, 60, 20), align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL)
        block_88 = uicls.Container(parent=subContainer, name='block_88', pos=(0, 0, 88, 88), align=uiconst.CENTER, state=uiconst.UI_NORMAL, pickRadius=44)
        color, bgColor, comp, compsub = sm.GetService('window').GetWindowColors()
        r, g, b, a = color
        mainShape = uicls.Sprite(parent=self, name='shipuiMainShape', pos=(0, 0, 160, 160), align=uiconst.CENTER, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/ShipUI/mainUnderlay.png', color=(r,
         g,
         b,
         1))
        underMain = uicls.Container(parent=self, name='underMain', pos=(0, 0, 160, 160), align=uiconst.CENTER, state=uiconst.UI_PICKCHILDREN)
        divider = uicls.Sprite(parent=underMain, name='divider', pos=(56, 42, 46, 12), align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/ShipUI/heatDivider.png')
        circlepickclipper_144 = uicls.Container(parent=underMain, name='circlepickclipper_144', pos=(8, 8, 144, 144), align=uiconst.TOPLEFT, state=uiconst.UI_PICKCHILDREN, pickRadius=-1)
        speedGaugeParent = uicls.Container(parent=circlepickclipper_144, name='speedGaugeParent', pos=(10, 72, 124, 68), align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL, clipChildren=True)
        speedNeedle = uicls.Transform(parent=speedGaugeParent, name='speedNeedle', pos=(-5, -6, 134, 12), align=uiconst.TOPLEFT, state=uiconst.UI_PICKCHILDREN, rotationCenter=(0.5, 0.5))
        needle = uicls.Sprite(parent=speedNeedle, name='needle', pos=(0, 0, 24, 12), align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/ShipUI/heatGaugeNeedle.png')
        speedGaugeSprite = uicls.Sprite(parent=speedNeedle, name='speedGaugeSprite', texturePath='res:/UI/Texture/classes/ShipUI/speedoOverlay.png', pos=(-8, -73, 79, 79), state=uiconst.UI_DISABLED)
        speedoUnderlay = uicls.Sprite(parent=underMain, name='speedoUnderlay', pos=(0, 48, 104, 44), align=uiconst.CENTER, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/ShipUI/speedoUnderlay.png')
        heatLowUnderlay = uicls.Sprite(parent=underMain, name='heatLowUnderlay', pos=(36, 42, 27, 38), align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/ShipUI/lowHeat_0.png')
        heatMedUnderlay = uicls.Sprite(parent=underMain, name='heatMedUnderlay', pos=(57, 36, 45, 18), align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/ShipUI/medHeat_0.png')
        heatHiUnderlay = uicls.Sprite(parent=underMain, name='heatHiUnderlay', pos=(95, 42, 27, 38), align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/ShipUI/hiHeat_0.png')
        slotsContainer = uicls.Container(parent=self, name='slotsContainer', pos=(0, 0, 1024, 512), align=uiconst.CENTER, state=uiconst.UI_PICKCHILDREN)


class ShipSlot(uicls.Container):
    default_pickRadius = 24

    def OnDropData(self, dragObj, nodes):
        flag1 = self.sr.slotFlag
        for node in nodes:
            decoClass = node.Get('__guid__', None)
            if decoClass == 'xtriui.ShipUIModule':
                flag2 = node.slotFlag
                if flag2 is not None:
                    uicore.layer.shipui.SwapSlots(flag1, node.slotFlag)
                break
            elif decoClass in ('xtriui.InvItem', 'listentry.InvItem'):
                item = node.rec
                if item.flagID == const.flagCargo and item.categoryID == const.categoryModule:
                    sm.GetService('invCache').GetInventoryFromId(session.shipid).Add(item.itemID, item.locationID, qty=None, flag=flag1)
                break

    @telemetry.ZONE_METHOD
    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        overloadBtn = uicls.Sprite(parent=self, name='overloadBtn', pos=(16, 6, 32, 16), align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL, texturePath='res:/UI/Texture/classes/ShipUI/slotOverloadDisabled.png')
        self.mainShape = uicls.Sprite(parent=self, name='mainshape', pos=(0, 0, 0, 0), align=uiconst.TOALL, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/ShipUI/slotMainCombined.png')


class LeftSideButton(uicls.Container):
    __guid__ = 'uicls.ShipUILeftSideButton'
    default_state = uiconst.UI_NORMAL
    default_align = uiconst.RELATIVE

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        self.btnName = attributes.btnName
        self.func = attributes.func
        self.cmdName = attributes.cmdName
        self.orgTop = None
        self.pickRadius = -1
        self.icon = uicls.Icon(parent=self, name='icon', pos=(0, 0, 32, 32), align=uiconst.CENTER, state=uiconst.UI_DISABLED, icon=attributes.iconNum)
        self.hilite = uicls.Sprite(parent=self, name='hilite', align=uiconst.TOALL, state=uiconst.UI_HIDDEN, texturePath='res:/UI/Texture/classes/ShipUI/utilBtnBaseAndShadow.png', color=(0.63, 0.63, 0.63, 1.0), blendMode=trinity.TR2_SBM_ADD)
        slot = uicls.Sprite(parent=self, name='slot', align=uiconst.TOALL, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/ShipUI/utilBtnBaseAndShadow.png')
        busy = uicls.Sprite(parent=self, name='busy', align=uiconst.TOALL, state=uiconst.UI_HIDDEN, texturePath='res:/UI/Texture/classes/ShipUI/utilBtnGlow.png', color=(0.27, 0.72, 1.0, 0.53))

    def OnClick(self, *args):
        self.func()
        sm.GetService('ui').StopBlink(self.icon)

    def OnMouseDown(self, btn, *args):
        if getattr(self, 'orgTop', None) is None:
            self.orgTop = self.top
        self.top = self.orgTop + 2

    def OnMouseUp(self, *args):
        if getattr(self, 'orgTop', None) is not None:
            self.top = self.orgTop

    def OnMouseEnter(self, *args):
        self.hilite.state = uiconst.UI_DISABLED

    def OnMouseExit(self, *args):
        self.hilite.state = uiconst.UI_HIDDEN
        if getattr(self, 'orgTop', None) is not None:
            self.top = self.orgTop

    def GetHint(self):
        ret = self.btnName
        if self.cmdName:
            shortcut = uicore.cmd.GetShortcutStringByFuncName(self.cmdName)
            if shortcut:
                ret += ' [%s]' % shortcut
        return ret


class EwarUIContainer(uicls.ContainerAutoSize):
    __guid__ = 'uicls.EwarUIContainer'
    default_width = 500
    default_height = 500
    default_name = 'ewarcont'
    default_state = uiconst.UI_PICKCHILDREN
    __notifyevents__ = ['OnEwarStartFromTactical', 'OnEwarEndFromTactical']
    MAXNUMBERINHINT = 6

    def ApplyAttributes(self, attributes):
        self.pending = False
        self.busyRefreshing = False
        uicls.Container.ApplyAttributes(self, attributes)
        self.ewarStates = {'warpScrambler': const.iconModuleWarpScrambler,
         'webify': const.iconModuleStasisWeb,
         'electronic': const.iconModuleECM,
         'ewRemoteSensorDamp': const.iconModuleSensorDamper,
         'ewTrackingDisrupt': const.iconModuleTrackingDisruptor,
         'ewTargetPaint': const.iconModuleTargetPainter,
         'ewEnergyVampire': const.iconModuleNosferatu,
         'ewEnergyNeut': const.iconModuleEnergyNeutralizer}
        self.ewarHints = {'warpScrambler': 'UI/Inflight/EwarHints/WarpScrambled',
         'webify': 'UI/Inflight/EwarHints/Webified',
         'electronic': 'UI/Inflight/EwarHints/Jammed',
         'ewRemoteSensorDamp': 'UI/Inflight/EwarHints/SensorDampened',
         'ewTrackingDisrupt': 'UI/Inflight/EwarHints/TrackingDisrupted',
         'ewTargetPaint': 'UI/Inflight/EwarHints/TargetPainted',
         'ewEnergyVampire': 'UI/Inflight/EwarHints/CapDrained',
         'ewEnergyNeut': 'UI/Inflight/EwarHints/CapNeutralized'}
        self.RefreshAllButtons()
        sm.RegisterNotify(self)

    def RefreshAllButtons(self):
        self.CreateAllButtons()
        self.RefreshAllButtonDisplay()

    def CreateAllButtons(self, *args):
        self.Flush()
        for key, value in self.ewarStates.iteritems():
            btn, btnPar = self.AddButton(key, value)
            btnPar.display = False

    def AddButton(self, jammingType, graphicID):
        iconSize = 40
        btnPar = uicls.Container(parent=self, align=uiconst.TOLEFT, width=iconSize + 8, name=jammingType)
        btnPar.fadingOut = False
        btn = EwarButton(parent=btnPar, name=jammingType, align=uiconst.CENTER, width=iconSize, height=iconSize, graphicID=graphicID, jammingType=jammingType)
        setattr(self, jammingType, btnPar)
        btnPar.btn = btn
        btn.GetMenu = (self.GetButtonMenu, btn)
        btn.GetButtonHint = self.GetButtonHint
        btn.OnClick = (self.OnButtonClick, btn)
        return (btn, btnPar)

    def OnEwarStartFromTactical(self, doAnimate = True, *args):
        self.RefreshAllButtonDisplay(doAnimate)

    def OnEwarEndFromTactical(self, doAnimate = True, *args):
        self.RefreshAllButtonDisplay(doAnimate)

    def ShowButton(self, jammingType, doAnimate = True):
        btnPar = getattr(self, jammingType, None)
        if btnPar:
            self.FadeButtonIn(btnPar, doAnimate)

    def HideButton(self, jammingType, doAnimate = True):
        btnPar = getattr(self, jammingType, None)
        if btnPar:
            self.FadeButtonOut(btnPar, doAnimate)

    def RefreshAllButtonDisplay(self, doAnimate = True):
        if self.busyRefreshing:
            self.pending = True
            return
        self.pending = False
        self.busyRefreshing = True
        try:
            jammersByType = sm.GetService('tactical').jammersByJammingType
            for jammingType in self.ewarStates.iterkeys():
                if not jammersByType.get(jammingType, set()):
                    self.HideButton(jammingType, doAnimate)
                else:
                    self.ShowButton(jammingType, doAnimate)

        finally:
            self.busyRefreshing = False

        if self.pending:
            self.RefreshAllButtonDisplay()

    def FadeButtonIn(self, btnPar, doAnimate = True):
        btn = btnPar.btn
        if not btnPar.display or btnPar.fadingOut:
            btnPar.fadingOut = False
            uiutil.SetOrder(btnPar, -1)
            btnPar.display = True
            if doAnimate:
                uicore.animations.FadeIn(btnPar)
                uicore.animations.MorphScalar(btnPar, 'width', startVal=0, endVal=40, duration=0.25)
            else:
                btnPar.opacity = 1.0
                btnPar.width = 40
        btnPar.btn.hint = None

    def FadeButtonOut(self, btnPar, doAnimate = True):
        if btnPar.display and not btnPar.fadingOut:
            btnPar.fadingOut = True
            btnPar.btn.hint = None
            if doAnimate:
                uicore.animations.MorphScalar(btnPar, 'width', startVal=40, endVal=0, duration=0.25)
                uicore.animations.FadeOut(btnPar, sleep=True)
                if btnPar.fadingOut:
                    btnPar.display = False
            else:
                btnPar.opacity = 0.0
                btnPar.width = 0

    def GetButtonHint(self, btn, jammingType, *args):
        if btn.hint is not None:
            return btn.hint
        attackers = self.FindWhoIsJammingMe(jammingType)
        hintList = []
        extraAttackers = 0
        for shipID, num in attackers.iteritems():
            if len(hintList) >= self.MAXNUMBERINHINT:
                extraAttackers = len(attackers) - len(hintList)
                break
            invItem = sm.StartService('michelle').GetBallpark().GetInvItem(shipID)
            if invItem:
                attackerShip = invItem.typeID
                if invItem.charID:
                    attackerID = invItem.charID
                    hintList.append(localization.GetByLabel('UI/Inflight/EwarAttacker', attackerID=attackerID, attackerShipID=attackerShip, num=num))
                else:
                    hintList.append(localization.GetByLabel('UI/Inflight/EwarAttackerNPC', attackerShipID=attackerShip, num=num))

        hintList = localizationUtil.Sort(hintList)
        if extraAttackers > 0:
            hintList.append(localization.GetByLabel('UI/Inflight/AndMorewarAttackers', num=extraAttackers))
        ewarHintPath = self.ewarHints.get(jammingType, None)
        if ewarHintPath is not None:
            ewarHint = localization.GetByLabel(ewarHintPath)
        else:
            ewarHint = ''
        hintList.insert(0, ewarHint)
        btn.hint = '<br>'.join(hintList)
        return btn.hint

    def GetButtonMenu(self, btn, *args):
        attackers = self.FindWhoIsJammingMe(btn.jammingType)
        m = []
        for shipID, num in attackers.iteritems():
            invItem = sm.StartService('michelle').GetBallpark().GetInvItem(shipID)
            if invItem:
                if invItem.charID:
                    attackerName = cfg.eveowners.Get(invItem.charID).name
                else:
                    attackerName = cfg.invtypes.Get(invItem.typeID).name
                m += [[attackerName, ('isDynamic', sm.GetService('menu').CelestialMenu, (invItem.itemID,
                    None,
                    invItem,
                    0,
                    invItem.typeID))]]

        m = localizationUtil.Sort(m, key=lambda x: x[0])
        return m

    def FindWhoIsJammingMe(self, jammingType):
        jammers = sm.GetService('tactical').jammersByJammingType.get(jammingType, set())
        if not jammers:
            return {}
        attackers = {}
        for jamInfo in jammers:
            sourceID, moduleID = jamInfo
            numberOfTimes = attackers.get(sourceID, 0)
            numberOfTimes += 1
            attackers[sourceID] = numberOfTimes

        return attackers

    def OnButtonClick(self, btn, *args):
        attackers = self.FindWhoIsJammingMe(btn.jammingType)
        michelle = sm.GetService('michelle')
        targets = []
        stateSvc = sm.GetService('state')
        targetStates = (state.targeted, state.targeting)
        if uicore.cmd.IsCombatCommandLoaded():
            targeting = uicore.cmd.combatCmdLoaded.name == 'CmdLockTargetItem'
            for sourceID in attackers:
                try:
                    if targeting and any(stateSvc.GetStates(sourceID, targetStates)):
                        continue
                    ball = michelle.GetBall(sourceID)
                    targets.append((ball.surfaceDist, sourceID))
                except:
                    pass

            if len(targets) > 0:
                targets.sort()
                itemID = targets[0][1]
                uicore.cmd.ExecuteCombatCommand(itemID, uiconst.UI_CLICK)


class EwarButton(uicls.Container):
    __guid__ = 'uicls.EwarButton'
    default_state = uiconst.UI_NORMAL
    default_align = uiconst.RELATIVE

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        self.btnName = attributes.btnName
        self.jammingType = attributes.jammingType
        self.orgTop = None
        self.pickRadius = -1
        graphicID = attributes.graphicID
        iconSize = self.height
        self.icon = uicls.Icon(parent=self, name='ewaricon', pos=(0,
         0,
         iconSize,
         iconSize), align=uiconst.CENTER, state=uiconst.UI_DISABLED, graphicID=graphicID, ignoreSize=1)
        self.hilite = uicls.Sprite(parent=self, name='hilite', align=uiconst.TOALL, state=uiconst.UI_HIDDEN, texturePath='res:/UI/Texture/classes/ShipUI/utilBtnBase.png', color=(0.63, 0.63, 0.63, 1.0), blendMode=trinity.TR2_SBM_ADD)
        slot = uicls.Sprite(parent=self, name='slot', align=uiconst.TOALL, state=uiconst.UI_DISABLED, color=(1.0, 0.0, 0.0, 2.5), texturePath='res:/UI/Texture/classes/ShipUI/utilBtnBase.png')

    def OnMouseEnter(self, *args):
        self.hilite.state = uiconst.UI_DISABLED

    def OnMouseExit(self, *args):
        self.hilite.state = uiconst.UI_HIDDEN
        if getattr(self, 'orgTop', None) is not None:
            self.top = self.orgTop

    def GetHint(self):
        self.GetButtonHint(self, self.jammingType)

    def GetButtonHint(self, btn, jammingType):
        pass