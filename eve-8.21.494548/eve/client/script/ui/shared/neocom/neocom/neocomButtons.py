#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/ui/shared/neocom/neocom/neocomButtons.py
import uicls
import uiconst
import util
import uthread
import neocom
import form
import math
import blue
import log
import localization
import localizationUtil
import trinity
import uix
import uiutil

class ButtonBase(uicls.Container):
    __guid__ = 'neocom.ButtonBase'
    __notifyevents__ = ['OnNeocomBlinkPulse']
    default_name = 'ButtonBase'
    default_state = uiconst.UI_NORMAL
    default_align = uiconst.TOPLEFT
    default_isDraggable = True
    PADHORIZONTAL = 6
    PADVERTICAL = 2
    ACTIVEFILL_DEFAULTALPHA = 0.5
    ACTIVEFILL_HOVERALPHA = 0.8

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        self.btnData = attributes.btnData
        self.btnNum = attributes.btnNum
        self.width = attributes.width
        self._isDraggable = attributes.get('isDraggable', self.default_isDraggable)
        self._openNeocomPanel = None
        self.height = self.width
        self.top = self.height * self.btnNum
        self.panel = None
        self.blinkThread = None
        self.realTop = self.top
        self.dragEventCookie = None
        self.disableClick = False
        self.iconSize = self.height - 2 * self.PADVERTICAL
        self.iconTransform = uicls.Transform(name='iconTransform', parent=self, align=uiconst.TOALL, scalingCenter=(0.5, 0.5))
        self.iconLabelCont = None
        self.icon = uicls.Sprite(parent=self.iconTransform, name='icon', state=uiconst.UI_DISABLED, align=uiconst.CENTER, width=self.iconSize, height=self.iconSize)
        self.UpdateIcon()
        PAD = 1
        self.mouseHoverFrame = uicls.Sprite(bgParent=self, name='mouseHoverFrame', texturePath='res:/UI/Texture/classes/Neocom/buttonHover.png', state=uiconst.UI_HIDDEN)
        self.blinkSprite = uicls.Sprite(bgParent=self, name='blinkSprite', texturePath='res:/UI/Texture/classes/Neocom/buttonBlink.png', state=uiconst.UI_HIDDEN)
        self.mouseDownFrame = uicls.Frame(bgParent=self, name='mosueDownFrame', texturePath='res:/UI/Texture/classes/Neocom/buttonDown.png', cornerSize=5, state=uiconst.UI_HIDDEN)
        self.activeFrame = uicls.Frame(bgParent=self, name='hoverFill', texturePath='res:/UI/Texture/classes/Neocom/buttonActive.png', cornerSize=5, state=uiconst.UI_HIDDEN)
        self.CheckIfActive()
        self.dropFrame = uicls.Frame(parent=self, name='hoverFrame', color=util.Color.GetGrayRGBA(1.0, 0.5), state=uiconst.UI_HIDDEN)
        sm.RegisterNotify(self)

    def UpdateIcon(self):
        texturePath = self._GetPathFromIconNum(self.btnData.iconPath)
        self.icon.SetTexturePath(texturePath)

    def CheckIfActive(self):
        if self.btnData.isActive:
            self.activeFrame.Show()
        else:
            self.activeFrame.Hide()

    def GetIconPath(self):
        return self._GetPathFromIconNum(self.btnData.iconPath)

    def _GetPathFromIconNum(self, iconNum):
        parts = iconNum.split('_')
        if len(parts) == 2:
            sheet, iconNum = parts
            iconSize = uix.GetIconSize(sheet)
            return 'res:/ui/texture/icons/%s_%s_%s.png' % (int(sheet), int(iconSize), int(iconNum))
        elif len(parts) == 4:
            root, sheet, iconSize, iconNum = parts
            return 'res:/ui/texture/icons/%s_%s_%s.png' % (int(sheet), int(iconSize), int(iconNum))
        else:
            return 'res:/ui/texture/icons/105_64_45.png'

    def IsDraggable(self):
        return self._isDraggable

    def SetDraggable(self, isDraggable):
        self._isDraggable = isDraggable

    def GetMenu(self):
        return self.btnData.GetMenu()

    def GetHint(self, label = None):
        return self.btnData.GetHint(label)

    def OnMouseEnter(self, *args):
        self.btnData.SetBlinkingOff()
        uicore.animations.Tr2DScaleTo(self.iconTransform, self.iconTransform.scale, (1.05, 1.05), duration=0.2, curveType=uiconst.ANIM_OVERSHOT)
        self.mouseHoverFrame.Show()
        uicore.animations.SpMaskIn(self.mouseHoverFrame, duration=0.5)

    def OnMouseExit(self, *args):
        uicore.animations.SpMaskOut(self.mouseHoverFrame, duration=0.5, callback=self.mouseHoverFrame.Hide)
        uicore.animations.Tr2DScaleTo(self.iconTransform, self.iconTransform.scale, (1.0, 1.0), curveType=uiconst.ANIM_OVERSHOT)

    def OnMouseDown(self, *args):
        self.mouseDownFrame.Show()
        self.mouseHoverFrame.Hide()
        if not self.IsDraggable():
            return
        if not uicore.uilib.leftbtn:
            return
        self.isDragging = False
        self.mouseDownY = uicore.uilib.y
        if self.dragEventCookie is not None:
            uicore.event.UnregisterForTriuiEvents(self.dragEventCookie)
        self.dragEventCookie = uicore.event.RegisterForTriuiEvents(uiconst.UI_MOUSEMOVE, self.OnDrag)
        uicore.animations.Tr2DScaleTo(self.iconTransform, self.iconTransform.scale, (0.95, 0.95), duration=0.1)

    def OnMouseUp(self, *args):
        self.mouseDownFrame.Hide()
        if uicore.uilib.mouseOver == self:
            self.mouseHoverFrame.Show()
            uicore.animations.Tr2DScaleTo(self.iconTransform, self.iconTransform.scale, (1.05, 1.05), duration=0.1)
        if self.dragEventCookie is not None:
            uicore.event.UnregisterForTriuiEvents(self.dragEventCookie)
            self.dragEventCookie = None

    def OnDragEnd(self, *args):
        uicore.event.UnregisterForTriuiEvents(self.dragEventCookie)
        self.dragEventCookie = None
        self.isDragging = False
        sm.GetService('neocom').OnButtonDragEnd(self)
        if uicore.uilib.mouseOver == self:
            self.mouseHoverFrame.Show()
        self.CheckIfActive()

    def OnDrag(self, *args):
        if math.fabs(self.mouseDownY - uicore.uilib.y) > 5 or self.isDragging:
            if not self.isDragging:
                uicore.event.RegisterForTriuiEvents(uiconst.UI_MOUSEUP, self.OnDragEnd)
            self.disableClick = True
            self.isDragging = True
            self.mouseDownFrame.Hide()
            sm.GetService('neocom').OnButtonDragged(self)
        return True

    def OnClick(self, *args):
        if not self or self.destroyed:
            return
        self.btnData.CheckContinueBlinking()
        if not self.disableClick:
            self.OnClickCommand()
        if not self or self.destroyed:
            return
        self.disableClick = False
        if self.dragEventCookie:
            uicore.event.UnregisterForTriuiEvents(self.dragEventCookie)

    def OnDblClick(self, *args):
        pass

    def OnClickCommand(self):
        pass

    def OnSwitched(self):
        uicore.effect.MorphUIMassSpringDamper(item=self, attrname='opacity', float=1, newVal=1.0, minVal=0, maxVal=2.0, dampRatio=0.45, frequency=15.0, initSpeed=0, maxTime=4.0, callback=None, initVal=0.0)
        self.isDragging = False
        self.disableClick = False

    def GetDragData(self, *args):
        if self.btnData.isDraggable:
            return [self.btnData]

    def BlinkOnce(self, duration = 0.7):
        self.blinkSprite.Show()
        uicore.animations.SpSwoopBlink(self.blinkSprite, rotation=math.pi * 0.75, duration=duration)

    def OnNeocomBlinkPulse(self):
        if self.btnData.isBlinking:
            self.BlinkOnce()

    def OnDropData(self, source, dropData):
        if not sm.GetService('neocom').IsValidDropData(dropData):
            return
        index = self.btnData.parent.children.index(self.btnData)
        sm.GetService('neocom').OnBtnDataDropped(dropData[0], index)

    def OnDragEnter(self, panelEntry, dropData):
        if not sm.GetService('neocom').IsValidDropData(dropData):
            return
        sm.GetService('neocom').OnButtonDragEnter(self.btnData, dropData[0])
        uthread.new(self.ShowPanelOnMouseHoverThread)

    def OnDragExit(self, *args):
        sm.GetService('neocom').OnButtonDragExit(self.btnData, args)

    def ToggleNeocomPanel(self):
        isOpen = self._openNeocomPanel and not self._openNeocomPanel.destroyed
        sm.GetService('neocom').CloseAllPanels()
        if isOpen:
            self._openNeocomPanel = None
        else:
            self._openNeocomPanel = sm.GetService('neocom').ShowPanel(triggerCont=self, panelClass=self.GetPanelClass(), panelAlign=neocom.PANEL_SHOWONSIDE, parent=uicore.layer.abovemain, btnData=self.btnData)

    def ShowPanelOnMouseHoverThread(self):
        if len(self.btnData.children) <= 1:
            return
        blue.pyos.synchro.Sleep(500)
        if not self or self.destroyed:
            return
        if uicore.uilib.mouseOver == self:
            self.ToggleNeocomPanel()

    def GetPanelClass(self):
        return neocom.PanelGroup

    def SetAsActive(self):
        self.btnData.isActive = True
        self.activeFrame.state = uiconst.UI_DISABLED

    def SetAsInactive(self):
        self.btnData.isActive = False
        self.activeFrame.state = uiconst.UI_HIDDEN


class ButtonWindow(ButtonBase):
    __guid__ = 'neocom.ButtonWindow'
    default_name = 'ButtonWindow'

    def GetHint(self):
        label = None
        if self.IsSingleWindow():
            wnd = self.GetWindow()
            if not wnd.destroyed:
                label = wnd.GetCaption()
        elif self.btnData.children:
            label = self.btnData.children[0].wnd.GetNeocomGroupLabel()
        return ButtonBase.GetHint(self, label)

    def OnClickCommand(self):
        if self.IsSingleWindow():
            if not getattr(self.GetWindow(), 'isImplanted', False):
                uthread.new(self.GetWindow().ToggleMinimize)
            else:
                cmd = uicore.cmd.commandMap.GetCommandByName(self.btnData.cmdName)
                cmd.callback()
        elif self.btnData.children:
            self.ToggleNeocomPanel()
        elif hasattr(self.btnData, 'cmdName'):
            cmd = uicore.cmd.commandMap.GetCommandByName(self.btnData.cmdName)
            cmd.callback()

    def IsSingleWindow(self):
        return len(self.btnData.children) == 1

    def GetWindow(self):
        if self.btnData.children:
            btnData = self.btnData.children[0]
            return btnData.wnd

    def GetAllWindows(self):
        wnds = []
        for btnData in self.btnData.children:
            wnds.append(btnData.wnd)

        return wnds

    def GetMenu(self):
        if self.IsSingleWindow():
            wnd = self.GetWindow()
            if wnd and wnd.GetMenu:
                return wnd.GetMenu()
        else:
            if self.btnData.children:
                for wnd in self.GetAllWindows():
                    if not wnd.IsKillable():
                        return None

                return [(uiutil.MenuLabel('/Carbon/UI/Commands/CmdCloseAllWindows'), self.CloseAllWindows)]
            if self.btnData.btnType == neocom.BTNTYPE_CMD:
                return ButtonBase.GetMenu(self)

    def CloseAllWindows(self):
        for wnd in self.GetAllWindows():
            wnd.CloseByUser()

    def OnDragEnter(self, panelEntry, nodes):
        if sm.GetService('neocom').IsValidDropData(nodes):
            ButtonBase.OnDragEnter(self, panelEntry, nodes)
        elif self.btnData.btnType == neocom.BTNTYPE_WINDOW:
            self.dropFrame.state = uiconst.UI_DISABLED
            self.OnMouseEnter()
            uthread.new(self.ShowPanelOnMouseHoverThread)

    def OnDragExit(self, *args):
        self.dropFrame.state = uiconst.UI_HIDDEN
        self.OnMouseExit()

    def OnDropData(self, source, nodes):
        if sm.GetService('neocom').IsValidDropData(nodes):
            index = self.btnData.parent.children.index(self.btnData)
            sm.GetService('neocom').OnBtnDataDropped(nodes[0], index)
        elif self.IsSingleWindow():
            wnd = self.GetWindow()
            if hasattr(wnd, 'OnDropData'):
                if wnd.OnDropData(source, nodes):
                    self.BlinkOnce(0.3)
        elif not self.GetAllWindows():
            wndClsName = self.btnData.guid.split('.')[1]
            wndCls = getattr(form, wndClsName, None)
            if wndCls and hasattr(wndCls, 'OnDropDataCls'):
                if wndCls.OnDropDataCls(source, nodes):
                    self.BlinkOnce(0.3)
        self.dropFrame.state = uiconst.UI_HIDDEN

    def UpdateIcon(self):
        if self.iconLabelCont:
            self.iconLabelCont.Close()
        wnd = self.GetWindow()
        if not wnd:
            iconNum = self.btnData.iconPath
        elif self.IsSingleWindow():
            iconNum = wnd.iconNum
        else:
            wnds = self.GetAllWindows()
            iconNum = wnds[0].GetNeocomGroupIcon()
            self.iconLabelCont = uicls.Container(parent=self.iconTransform, align=uiconst.TOPRIGHT, pos=(1, 1, 13, 13), idx=0, bgColor=util.Color.GetGrayRGBA(0.7, 0.2))
            uicls.Label(parent=self.iconLabelCont, align=uiconst.CENTER, text='<b>%s' % len(wnds), fontsize=10, letterspace=-1)
        self.icon.SetTexturePath(self._GetPathFromIconNum(iconNum))


class ButtonInventory(ButtonWindow):
    __guid__ = 'neocom.ButtonInventory'
    default_name = 'ButtonInventory'

    def OnDragEnter(self, panelEntry, nodes):
        if not self._IsValidDropData(nodes):
            return
        self.dropFrame.state = uiconst.UI_DISABLED
        self.OnMouseEnter()

    def OnDragExit(self, *args):
        self.dropFrame.state = uiconst.UI_HIDDEN
        self.OnMouseExit()

    def OnDropData(self, source, nodes):
        if not self._IsValidDropData(nodes):
            return
        inv = []
        for node in nodes:
            if node.Get('__guid__', None) in ('xtriui.InvItem', 'listentry.InvItem'):
                inv.append(node.itemID)
                locationID = node.rec.locationID

        if inv:
            sm.GetService('invCache').GetInventoryFromId(self.btnData.invLocationID).MultiAdd(inv, locationID, flag=self.btnData.invFlagID)
        self.dropFrame.state = uiconst.UI_HIDDEN

    def _IsValidDropData(self, nodes):
        if not nodes:
            return False
        for node in nodes:
            if node.Get('__guid__', None) in ('xtriui.InvItem', 'listentry.InvItem'):
                return True

        return False


class ButtonGroup(ButtonBase):
    __guid__ = 'neocom.ButtonGroup'
    default_name = 'ButtonGroup'

    def ApplyAttributes(self, attributes):
        ButtonBase.ApplyAttributes(self, attributes)
        self.icon.color.SetRGB(*neocom.COLOR_GROUPDEFAULT)
        if self.btnData.labelAbbrev:
            label = uicls.Label(parent=self.iconTransform, align=uiconst.CENTER, text='<b><color=0xFF203d3d>' + self.btnData.labelAbbrev, fontsize=16, opacity=0.75, letterspace=-1, idx=0)

    def OnClickCommand(self):
        self.ToggleNeocomPanel()

    def OnMouseEnter(self, *args):
        uicore.animations.Tr2DScaleTo(self.iconTransform, self.iconTransform.scale, (1.05, 1.05), duration=0.2, curveType=uiconst.ANIM_OVERSHOT)
        self.mouseHoverFrame.Show()
        uicore.animations.SpMaskIn(self.mouseHoverFrame, duration=0.5)

    def OnDragEnter(self, source, dropData):
        if not sm.GetService('neocom').IsValidDropData(dropData):
            return
        self.dropFrame.state = uiconst.UI_DISABLED
        self.OnMouseEnter()
        uthread.new(self.ShowPanelOnMouseHoverThread)

    def OnDragExit(self, *args):
        self.dropFrame.state = uiconst.UI_HIDDEN
        self.OnMouseExit()

    def OnDropData(self, source, dropData):
        if not sm.GetService('neocom').IsValidDropData(dropData):
            return
        btnData = dropData[0]
        oldHeadNode = btnData.GetHeadNode()
        btnData.MoveTo(self.btnData)
        if oldHeadNode == sm.GetService('neocom').eveMenuBtnData:
            btnData.isRemovable = True
        sm.GetService('neocom').ResetEveMenuBtnData()


class ButtonChat(ButtonBase):
    __guid__ = 'neocom.ButtonChat'
    __notifyevents__ = ['OnNeocomBlinkPulse']
    default_name = 'ButtonChat'

    def ApplyAttributes(self, attributes):
        sm.RegisterNotify(self)
        ButtonBase.ApplyAttributes(self, attributes)
        self.activeFrame.state = uiconst.UI_DISABLED

    def OnClickCommand(self):
        uthread.new(self.ToggleNeocomPanel)

    def GetHint(self):
        return localization.GetByLabel('UI/Neocom/ChatBtn')

    def CheckIfActive(self):
        pass

    def SetAsInactive(self):
        pass


class ButtonBookmarks(ButtonBase):
    __guid__ = 'neocom.ButtonBookmarks'
    default_name = 'ButtonBookmarks'

    def OnClickCommand(self):
        self.ToggleNeocomPanel()


class OverflowButton(uicls.Container):
    __guid__ = 'neocom.OverflowButton'
    __notifyevents__ = ['OnNeocomPanelsClosed', 'OnNeocomBlinkPulse']
    default_state = uiconst.UI_HIDDEN
    default_name = 'overflowButtonCont'
    default_pos = (0, 0, 20, 0)

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        sm.RegisterNotify(self)
        self._openNeocomPanel = None
        self.isBlinking = False
        self.hoverSprite = uicls.Sprite(bgParent=self, align=uiconst.TOALL, texturePath='res:/UI/Texture/classes/Neocom/buttonHover.png', blendMode=trinity.TR2_SBM_ADD, state=uiconst.UI_HIDDEN)
        self.blinkSprite = uicls.Sprite(bgParent=self, name='blinkSprite', texturePath='res:/UI/Texture/classes/Neocom/buttonBlink.png', state=uiconst.UI_HIDDEN)
        self.icon = uicls.Sprite(parent=self, texturePath='res:/UI/Texture/classes/Neocom/arrowDown.png', width=7, height=7, align=uiconst.CENTER, state=uiconst.UI_DISABLED)
        self.UpdateIconRotation()

    def UpdateIconRotation(self):
        if settings.char.ui.Get('neocomAlign', uiconst.TOLEFT) == uiconst.TOLEFT:
            self.icon.rotation = math.pi / 2
        else:
            self.icon.rotation = -math.pi / 2

    def OnMouseEnter(self, *args):
        self.hoverSprite.state = uiconst.UI_DISABLED
        uicore.animations.SpMaskIn(self.hoverSprite, duration=0.5)

    def OnMouseExit(self, *args):
        uicore.animations.SpMaskOut(self.hoverSprite, duration=0.5)

    def OnMouseDown(self, *args):
        self.icon.opacity = 1.0

    def BlinkOnce(self):
        self.blinkSprite.state = uiconst.UI_DISABLED
        uicore.animations.FadeTo(self.blinkSprite, curveType=uiconst.ANIM_WAVE, duration=0.7)

    def OnClick(self, *args):
        self.ToggleNeocomPanel()

    def OnDblClick(self, *args):
        pass

    def ToggleNeocomPanel(self):
        isOpen = self._openNeocomPanel and not self._openNeocomPanel.destroyed
        sm.GetService('neocom').CloseAllPanels()
        if isOpen:
            self._openNeocomPanel = None
        else:
            self._openNeocomPanel = sm.GetService('neocom').ShowPanel(self, neocom.PanelOverflow, neocom.PANEL_SHOWONSIDE, parent=uicore.layer.abovemain, btnData=None)

    def BlinkOnce(self):
        self.blinkSprite.state = uiconst.UI_DISABLED
        uicore.animations.SpSwoopBlink(self.blinkSprite, rotation=math.pi, duration=0.7)

    def OnNeocomBlinkPulse(self):
        for btnData in sm.GetService('neocom').neocom.overflowButtons:
            if btnData.isBlinking:
                self.BlinkOnce()
                return


class WrapperButton(uicls.Container):
    __guid__ = 'neocom.WrapperButton'
    __notifyevents__ = ['OnNeocomBlinkPulse']
    default_name = 'WrapperButton'
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        sm.RegisterNotify(self)
        self.cmdName = attributes.cmdName
        self._openNeocomPanel = None
        self.cmd = uicore.cmd.commandMap.GetCommandByName(attributes.cmdName)
        self.blinkThread = None
        self.isBlinking = False
        self.mouseHoverSprite = uicls.Sprite(parent=self, name='mouseHoverSprite', align=uiconst.TOALL, texturePath='res:/UI/Texture/classes/Neocom/eveButtonBg.png', blendMode=trinity.TR2_SBM_ADD, state=uiconst.UI_HIDDEN)
        self.mouseHoverSprite.Hide()
        self.blinkSprite = uicls.Sprite(parent=self, name='blinkSprite', texturePath='res:/UI/Texture/classes/Neocom/buttonBlink.png', state=uiconst.UI_HIDDEN, align=uiconst.TOALL)

    def OnClick(self, *args):
        self.cmd.callback()
        self.DisableBlink()

    def OnDblClick(self, *args):
        pass

    def OnMouseEnter(self, *args):
        self.DisableBlink()
        self.mouseHoverSprite.state = uiconst.UI_DISABLED
        uicore.animations.SpMaskIn(self.mouseHoverSprite, duration=0.5)

    def OnMouseExit(self, *args):
        uicore.animations.SpMaskOut(self.mouseHoverSprite, duration=0.5, callback=self.mouseHoverSprite.Hide)

    def GetHint(self, *args):
        ret = self.cmd.GetDescription()
        shortcutStr = self.cmd.GetShortcutAsString()
        if shortcutStr:
            ret = localization.GetByLabel('UI/Neocom/NeocomBtnHintWithShortcut', btnDisplayName=ret, shortcut=shortcutStr)
        if self.cmdName == 'OpenCharactersheet':
            ret += '<br>' + cfg.eveowners.Get(session.charid).name
        elif self.cmdName == 'OpenCalendar':
            ret = localizationUtil.FormatDateTime(blue.os.GetTime(), dateFormat='full', timeFormat=None) + '<br>' + ret
        return ret

    def EnableBlink(self):
        self.isBlinking = True

    def DisableBlink(self):
        self.isBlinking = False

    def BlinkOnce(self):
        self.blinkSprite.state = uiconst.UI_DISABLED
        uicore.animations.SpSwoopBlink(self.blinkSprite, duration=0.7)

    def OnNeocomBlinkPulse(self):
        if self.isBlinking:
            self.BlinkOnce()

    def GetMenu(self):
        return sm.GetService('neocom').GetMenu()


class ButtonEveMenu(WrapperButton):
    __guid__ = 'neocom.ButtonEveMenu'

    def ApplyAttributes(self, attributes):
        WrapperButton.ApplyAttributes(self, attributes)
        self.btnData = attributes.btnData
        uicls.Sprite(parent=self, name='EVEMenuIcon', align=uiconst.CENTER, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/Icons/79_64_11.png', width=20, height=20, color=util.Color.GetGrayRGBA(1.0, 0.85), idx=0)
        uicls.Sprite(bgParent=self, align=uiconst.TOALL, texturePath='res:/UI/Texture/classes/Neocom/eveButtonBg.png', blendMode=trinity.TR2_SBM_ADD)

    def OnClick(self, *args):
        self.ToggleNeocomPanel()
        self.btnData.CheckContinueBlinking()

    def ToggleNeocomPanel(self):
        isOpen = self._openNeocomPanel and not self._openNeocomPanel.destroyed
        sm.GetService('neocom').CloseAllPanels()
        if isOpen:
            self._openNeocomPanel = None
        else:
            self._openNeocomPanel = sm.GetService('neocom').ShowEveMenu()

    def BlinkOnce(self):
        self.blinkSprite.state = uiconst.UI_DISABLED
        uicore.animations.SpSwoopBlink(self.blinkSprite, rotation=math.pi, duration=0.7)

    def OnNeocomBlinkPulse(self):
        if self.btnData.isBlinking:
            self.BlinkOnce()


def GetBtnClassByBtnType(btnType):
    btnsByTypeID = {neocom.BTNTYPE_CMD: ButtonWindow,
     neocom.BTNTYPE_WINDOW: ButtonWindow,
     neocom.BTNTYPE_GROUP: ButtonGroup,
     neocom.BTNTYPE_CHAT: ButtonChat,
     neocom.BTNTYPE_BOOKMARKS: ButtonBookmarks,
     neocom.BTNTYPE_INVENTORY: ButtonInventory}
    if btnType not in btnsByTypeID:
        log.LogError('No neocom button Class defined for button type')
    return btnsByTypeID[btnType]


exports = {'neocom.GetBtnClassByBtnType': GetBtnClassByBtnType}