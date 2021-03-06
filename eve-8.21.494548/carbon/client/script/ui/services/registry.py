#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/client/script/ui/services/registry.py
import service
import uthread
import uicls
import uiutil
import uiconst
import log
import util
import blue
import localization

class RegistryService(service.Service):
    __guid__ = 'svc.registry'
    __servicename__ = 'registry'
    __startupdependencies__ = ['settings']

    def Run(self, memStream = None):
        service.Service.Run(self, memStream)
        self._focus = None
        self.toggleState = None
        self.Release()

    def Stop(self, stream):
        service.Service.Stop(self)
        self.Release()

    def Release(self):
        self.modals = []
        self.windows = []
        self.stacks = []
        self._blockConfirm = 0

    def ResetWindowSettings(self, *args):
        settings.char.Remove('windows')

    def GetRegisteredWindowState(self, windowID, statename, default = None):
        all = settings.char.windows.Get('%sWindows' % statename, {})
        if windowID in all:
            return all[windowID]
        return default

    def RegisterWindow(self, wnd):
        if wnd not in self.windows:
            self.windows.append(wnd)

    def UnregisterWindow(self, wnd):
        if wnd in self.windows:
            self.windows.remove(wnd)

    def GetWindows(self):
        return self.windows

    def GetWindow(self, windowID):
        for wnd in self.GetWindows():
            try:
                if getattr(wnd, 'windowID', wnd.name).lower() == windowID.lower():
                    return wnd
            except:
                if getattr(wnd, 'windowID', wnd.name) == windowID:
                    return wnd

    def GetStack(self, stackID, stackClass = None, useDefaultPos = False):
        if stackID.startswith('windowStack_'):
            stackName = stackID
        else:
            stackName = 'windowStack_%s' % stackID
        stack = self.GetWindow(stackName)
        if stack is not None and not stack.destroyed:
            return stack
        stackClass = stackClass or uicls.WindowStack
        return stackClass.Open(windowID=stackID, parent=uicore.layer.main, useDefaultPos=useDefaultPos)

    def GetTopLevelWindowAboveItem(self, item):
        checkPar = item.parent
        while checkPar:
            if self.IsTopLevelWindow(checkPar):
                return checkPar
            if checkPar.parent:
                checkPar = checkPar.parent
            else:
                break

        return uicore.desktop

    def IsTopLevelWindow(self, item):
        return getattr(item, 'isTopLevelWindow', False)

    def IsWindow(self, item):
        return isinstance(item, uicls.Window)

    def IsWindowStack(self, item):
        return isinstance(item, uicls.WindowStackCore)

    def GetValidWindows(self, getModals = 0, floatingOnly = False, getHidden = 0):
        validWnds = []
        for wnd in self.GetWindows():
            if not self.IsWindow(wnd) or wnd.sr.stack is not None or getattr(wnd, '_changing', 0):
                continue
            if not getHidden and not uiutil.IsVisible(wnd):
                continue
            if not getModals and (getattr(wnd, 'isModal', 0) or getattr(wnd, 'isDialog', 0)):
                continue
            if floatingOnly and wnd.GetAlign() != uiconst.RELATIVE:
                continue
            if getattr(wnd, 'parent', None) is None:
                log.LogError("Window without parent!; that shouldn't be possible. Window: %s" % repr(wnd))
                print "Window without parent!; that shouldn't be possible. Window: %s" % repr(wnd), wnd.name
                continue
            validWnds.append(wnd)

        return validWnds

    def CheckMoveActiveState(self, topLevelLeaving = None):
        modal = self.GetModalWindow(topLevelLeaving)
        if modal:
            self.SetFocus(modal)
        else:
            if topLevelLeaving is None or topLevelLeaving == self.GetActive():
                validWnds = self.GetValidWindows()
                if validWnds:
                    sortedByIndex = uiutil.SortListOfTuples([ (vwnd.parent.children.index(vwnd), vwnd) for vwnd in validWnds if not getattr(vwnd, 'isImplanted', False) ])
                    if sortedByIndex:
                        self.SetFocus(sortedByIndex[0])
                        return
            focus = self.GetFocus()
            if focus and topLevelLeaving:
                if uiutil.IsUnder(focus, topLevelLeaving):
                    focus = None
            if focus is None:
                topLevels = []

                def CrawlForTopLevelWindows(par):
                    if self.IsTopLevelWindow(par):
                        topLevels.append(par)
                    for child in par.children:
                        if hasattr(child, 'children') and child is not topLevelLeaving:
                            CrawlForTopLevelWindows(child)

                CrawlForTopLevelWindows(uicore.desktop)
                if topLevels:
                    for topLevel in topLevels:
                        self.SetFocus(topLevel)
                        focus = self.GetFocus()
                        if focus and uiutil.IsUnder(focus, topLevel):
                            break

    def GetModalWindow(self, exclude = None):
        if self.modals:
            mdl = self.modals[-1]
            if mdl is None or mdl.destroyed or exclude and mdl == exclude:
                self.modals.remove(mdl)
                return self.GetModalWindow()
            return mdl
        else:
            return

    def AddModalWindow(self, wnd):
        if wnd in self.modals:
            self.RemoveModalWindow(wnd)
        self.modals.append(wnd)

    def RemoveModalWindow(self, wnd):
        if wnd in self.modals:
            self.modals.remove(wnd)

    def GetActiveStackOrWindow(self, *args):
        all = self.GetValidWindows()
        active = self.GetActive()
        if active:
            for each in all:
                if each is active:
                    return each
                if uiutil.IsUnder(active, each):
                    return each

    def SetFocus(self, item):
        while item and getattr(item, 'isTabStop', 0) == 0:
            if self.IsTopLevelWindow(item):
                stackWnd = None
                current, tabstops = None, []
                if self.IsWindowStack(item):
                    stackWnd = item.GetActiveWindow()
                current, tabstops = self.CrawlForTabstops(stackWnd or item)
                if current:
                    item = current
                    break
                elif tabstops:
                    item = tabstops[0]
                    break
            if self.IsTopLevelWindow(item):
                break
            if not hasattr(item, 'parent') or item == uicore.desktop:
                break
            item = item.parent

        focus = self.GetFocus()
        if focus != item and hasattr(focus, 'OnKillFocus'):
            focus.OnKillFocus()
        if item:
            if self.IsTopLevelWindow(item):
                wndAbove = item
            else:
                wndAbove = self.GetTopLevelWindowAboveItem(item)
            item.SetFocus()
            self.__SetActive(wndAbove)
            self._focus = item
            self.RegisterFocusItem(item)
            if hasattr(item, 'OnSetFocus') and not item.destroyed:
                item.OnSetFocus()
        else:
            self._focus = None

    def __SetActive(self, wnd = None):
        while not self.IsTopLevelWindow(wnd):
            if wnd == uicore.desktop:
                break
            wnd = wnd.parent

        active = self.GetActive()
        if hasattr(active, 'OnSetInactive'):
            active.OnSetInactive()
        if self.IsWindowStack(wnd):
            wnd = wnd.GetActiveWindow()
        if not wnd or wnd.destroyed:
            wnd = uicore.desktop
        elif self.IsWindow(wnd):
            if wnd.sr.stack is not None:
                uiutil.SetOrder(wnd.sr.stack)
            elif wnd.parent and wnd.align == uiconst.TOPLEFT:
                uiutil.SetOrder(wnd, 0)
        if hasattr(wnd, 'SetActive'):
            wnd.SetActive()

    def RegisterFocusItem(self, item):
        if item and not item.destroyed and item != uicore.desktop:
            wndAbove = self.GetTopLevelWindowAboveItem(item)
            if wndAbove and wndAbove is not uicore.desktop:
                tabstops = [ ts for ts in wndAbove.Find('trinity.Tr2Sprite2dContainer') if getattr(ts, 'isTabStop', None) ]
                for tabstop in tabstops:
                    setattr(tabstop, 'hasFocus', 0)

                setattr(item, 'hasFocus', 1)

    def GetFocus(self, active = None):
        focus = self._focus
        if focus and not focus.destroyed:
            return focus

    def GetActive(self):
        focus = self.GetFocus()
        if focus and not focus.destroyed:
            if self.IsTopLevelWindow(focus):
                return focus
            return self.GetTopLevelWindowAboveItem(focus)

    def FindFocus(self, browse = 0):
        modal = self.GetModalWindow()
        if modal:
            active = modal
        else:
            active = self.GetActive()
        focus = self.GetFocus()
        if active is None:
            active = uicore.desktop
        if focus and hasattr(focus, 'CheckFocusChange'):
            usedFocusChange = focus.CheckFocusChange(browse)
            if usedFocusChange:
                return
        if focus and uiutil.IsUnder(focus, active) and uiutil.IsVisible(focus) and not browse:
            uthread.new(self.SetFocus, focus)
            return
        tabstops = []
        if active:
            current, tabstops = self.CrawlForTabstops(active)
        if browse and len(tabstops) > 1:
            current = current or focus
            idx = 0
            if current in tabstops:
                idx = browse + tabstops.index(current)
            if idx < 0:
                idx = len(tabstops) - 1
            elif idx >= len(tabstops):
                idx = 0
            self.SetFocus(tabstops[idx])
            return
        if len(tabstops) and focus != tabstops[0]:
            self.SetFocus(tabstops[0])
            return

    def CrawlForTabstops(self, fromwhere):
        blueTypeName = 'trinity.Tr2Sprite2dContainer'
        sorted = []
        current = []
        done = []
        tabstopgroups = [ wnd for wnd in fromwhere.Find(blueTypeName) if getattr(wnd, 'isTabOrderGroup', None) and uiutil.IsVisible(wnd) ]
        for tabstopgroup in tabstopgroups:
            tabstops = [ wnd for wnd in tabstopgroup.Find(blueTypeName) if getattr(wnd, 'isTabStop', None) ]
            gAbs = tabstopgroup.GetAbsolute()
            for tabstop in tabstops:
                if uiutil.IsClickable(tabstop):
                    if getattr(tabstop, 'hasFocus', None):
                        current.append(tabstop)
                    tAbs = tabstop.GetAbsolute()
                    sorted.append(([gAbs[1],
                      gAbs[0],
                      tAbs[1],
                      tAbs[0]], tabstop))
                    done.append(tabstop)

        tabstops = [ wnd for wnd in fromwhere.Find(blueTypeName) if getattr(wnd, 'isTabStop', None) ]
        for tabstop in tabstops:
            if tabstop not in done and uiutil.IsClickable(tabstop):
                if getattr(tabstop, 'hasFocus', None) == 1:
                    current.append(tabstop)
                tAbs = tabstop.GetAbsolute()
                sorted.append(([tAbs[1],
                  tAbs[0],
                  tAbs[1],
                  tAbs[0]], tabstop))
                done.append(tabstop)

        if current:
            current = current[0]
        return (current, uiutil.SortListOfTuples(sorted))

    def GetModalResult(self, default, funcname = 'btn_default'):
        result = None
        modal = self.GetModalWindow()
        if modal:
            result = default
            for wndType in ('trinity.Tr2Sprite2dContainer', 'trinity.Tr2Sprite2d'):
                for c in modal.Find(wndType):
                    if getattr(c, funcname, 0):
                        result = c.btn_modalresult
                        break

        return result

    def BlockConfirm(self):
        self._blockConfirm = 1

    def Confirm(self, starter = None):
        if self._blockConfirm:
            self._blockConfirm = 0
            return False
        if uicore.ime.IsVisible():
            return
        focus = self.GetFocus()
        active = self.GetActive()
        modal = self.GetModalWindow()
        if modal:
            if focus and uiutil.IsUnder(focus, modal):
                if hasattr(focus, 'Confirm') and focus != starter:
                    return uthread.new(focus.Confirm)
            if hasattr(modal, 'Confirm') and modal != starter:
                if not getattr(modal, 'blockconfirmonreturn', 0) or uicore.uilib.Key(uiconst.VK_CONTROL):
                    modal.Confirm()
                    return True
            else:
                result = self.GetModalResult(uiconst.ID_OK)
                modal.SetModalResult(result)
                return True
            return False
        if getattr(focus, 'Confirm', None) and focus != starter:
            uthread.new(focus.Confirm)
            return True
        if hasattr(active, 'IsCurrentDialog') and active.IsCurrentDialog():
            active.SetModalResult(uiconst.ID_OK)
            return True
        if getattr(active, 'Confirm', None) and active != starter:
            uthread.new(active.Confirm)
            return True
        if focus and focus.HasEventHandler('OnClick'):
            uthread.new(focus.OnClick, focus)
            return True
        if focus:
            searchFrom = self.GetTopLevelWindowAboveItem(focus)
        else:
            searchFrom = uicore.desktop
        if searchFrom:
            wnds = [ w for w in searchFrom.Find('trinity.Tr2Sprite2dContainer') + searchFrom.Find('trinity.Tr2Sprite2d') if getattr(w, 'btn_default', 0) == 1 ]
            if len(wnds):
                for wnd in wnds:
                    if starter and starter == wnd:
                        continue
                    if uiutil.IsVisible(wnd):
                        if wnd.HasEventHandler('OnClick'):
                            uthread.new(wnd.OnClick, wnd)
                        return True

        return False

    def AddToListGroup(self, listID_groupID, add):
        listID = unicode(listID_groupID[0])
        groupID = unicode(listID_groupID[1])
        groups = self.GetAllGroups()
        if listID in groups and groupID in groups[listID] and 'groupItems' in groups[listID][groupID] and add not in groups[listID][groupID]['groupItems']:
            groups[listID][groupID]['groupItems'].append(add)
        if hasattr(settings, 'char'):
            settings.char.WriteToDisk()

    def RemoveFromListGroup(self, listID_groupID, rem):
        listID = unicode(listID_groupID[0])
        groupID = unicode(listID_groupID[1])
        groups = self.GetAllGroups()
        if listID in groups and groupID in groups[listID] and 'groupItems' in groups[listID][groupID] and rem in groups[listID][groupID]['groupItems']:
            groups[listID][groupID]['groupItems'].remove(rem)
        self.ReloadGroupWindow(listID_groupID)
        if hasattr(settings, 'char'):
            settings.char.WriteToDisk()

    def ReloadGroupWindow(self, listID_groupID):
        wnd = self.GetWindow(unicode(listID_groupID))
        if wnd:
            wnd.LoadContent()

    def AddListGroup(self, listID, listgroupName = None):
        groupname = uiutil.AskName(localization.GetByLabel('/Carbon/UI/Common/TypeName'), localization.GetByLabel('/Carbon/UI/Common/TypeNameForFolder'))
        if not groupname:
            return
        if isinstance(groupname, dict):
            groupname = groupname['name']
        id = (listID, listgroupName or str(blue.os.GetWallclockTime()))
        group = self.GetListGroup(id)
        group['label'] = groupname
        group['id'] = id
        group['groupItems'] = []
        group['open'] = 0
        return group

    def GetLockedGroup(self, listID, listgroupName, label, openState = 0):
        id = (listID, listgroupName)
        group = self.GetListGroup(id)
        group['label'] = label
        group['id'] = id
        group['groupItems'] = []
        group['open'] = openState
        group['state'] = 'locked'
        return group

    def GetListGroup(self, listID_groupID):
        listID = unicode(listID_groupID[0])
        groupID = unicode(listID_groupID[1])
        if groupID in self.GetListGroups(listID):
            return self.GetListGroups(listID)[groupID]
        self.GetListGroups(listID)[groupID] = {}
        return self.GetListGroup(listID_groupID)

    def GetListGroups(self, listID):
        listID = unicode(listID)
        groups = self.GetAllGroups()
        if listID in groups:
            return groups[listID]
        groups[listID] = {}
        return self.GetListGroups(listID)

    def ChangeListGroupLabel(self, listID_groupID, newlabel):
        group = self.GetListGroup(listID_groupID)
        group['label'] = newlabel
        if hasattr(settings, 'char'):
            settings.char.WriteToDisk()

    def GetAllGroups(self):
        if hasattr(settings, 'char'):
            if settings.char.ui.Get('listgroups', None) is None:
                settings.char.ui.Set('listgroups', {})
            return settings.char.ui.Get('listgroups', {})
        return {}

    def DeleteListGroup(self, listID_groupID):
        listID = unicode(listID_groupID[0])
        groupID = unicode(listID_groupID[1])
        groups = self.GetAllGroups()
        if listID in groups and groupID in groups[listID]:
            del groups[listID][groupID]
        if hasattr(settings, 'char'):
            settings.char.WriteToDisk()

    def GetGroupIDFromItemID(self, listID, itemID):
        groups = self.GetAllGroups()
        if listID in groups:
            for groupID in groups[listID].iterkeys():
                if itemID in groups[listID][groupID]['groupItems']:
                    return (listID, groupID)

    def GetListGroupOpenState(self, listID_groupID, default = False):
        listID = unicode(listID_groupID[0])
        groupID = unicode(listID_groupID[1])
        groups = self.GetAllGroups()
        return groups.get(listID, {}).get(groupID, {}).get('open', default)

    def SetListGroupOpenState(self, listID_groupID, state):
        listID = unicode(listID_groupID[0])
        groupID = unicode(listID_groupID[1])
        groups = self.GetAllGroups()
        if listID not in groups:
            groups[listID] = {}
        if groupID not in groups[listID]:
            groups[listID][groupID] = {}
        if listID in groups and groupID in groups[listID]:
            groups[listID][groupID]['open'] = state
        if hasattr(settings, 'char'):
            settings.char.WriteToDisk()

    def ToggleCollapseAllWindows(self):
        if self.toggleState:
            for windowID in self.toggleState:
                wnd = self.GetWindow(windowID)
                if wnd and wnd.IsCollapsed():
                    wnd.Expand()

            self.toggleState = None
            return
        state = []
        wnds = self.GetValidWindows(floatingOnly=True)
        for wnd in wnds:
            if not getattr(wnd, 'windowID', None):
                continue
            if not wnd.IsCollapsed():
                windowID = wnd.windowID
                wnd.Collapse()
                state.append(windowID)

        if not state:
            for wnd in wnds:
                if wnd.IsCollapsed():
                    wnd.Expand()

        self.toggleState = state