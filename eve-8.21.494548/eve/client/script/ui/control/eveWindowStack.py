#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/ui/control/eveWindowStack.py
import uicls
import uiconst
import uthread
import uiutil

class WindowStack(uicls.WindowStackCore):
    __guid__ = 'uicls.WindowStack'

    def Check(self, updatewnd = 0, autoselecttab = 1, checknone = 0):
        if self is None or self.destroyed:
            return
        myWindows = self.GetWindows()
        if checknone and len(myWindows) == 0:
            self.Close()
            return
        self.SetMinWH()
        tabs = []
        label = ''
        allPinned = True
        allCompact = True
        for wnd in myWindows:
            if wnd is None or wnd.destroyed:
                continue
            tabs.append([wnd.GetCaption(),
             wnd,
             self,
             wnd])
            wnd.HideHeader()
            wnd.HideBackground()
            if not wnd.IsPinned():
                allPinned = False
            if not wnd.IsCompact():
                allCompact = False
            wnd.state = uiconst.UI_PICKCHILDREN
            label = label + wnd.GetCaption() + '-'

        self._SetPinned(allPinned)
        if allCompact:
            self.Compact()
        else:
            self.UnCompact()
        if len(tabs):
            if len(label):
                label = label[:-1]
            self.sr.tabs.Flush()
            maintabs = uicls.TabGroup(parent=self.sr.tabs, name='tabparent', groupID=self.name, tabs=tabs, autoselecttab=autoselecttab)
            maintabs.rightMargin = 80
            alltabs = maintabs.GetTabs()
            if alltabs:
                for i in xrange(len(alltabs)):
                    tab = alltabs[i]
                    wnd = myWindows[i]
                    tab.GetMenu = wnd.GetMenu
                    tab.SetIcon(wnd.headerIconNo, 14, getattr(wnd.sr.headerIcon, 'hint', ''), getattr(wnd.sr.headerIcon, 'GetMenu', None))
                    utilMenuFunc = wnd.GetUtilMenuFunc()
                    if utilMenuFunc is not None:
                        tab.SetUtilMenu(utilMenuFunc)
                    if wnd.isBlinking:
                        tab.Blink()

                self.SetCaption(label)

    def Pin(self, *args, **kwds):
        uicls.WindowStackCore.Pin(self, *args, **kwds)
        for wnd in self.GetWindows():
            if wnd is None or wnd.destroyed:
                continue
            wnd.Pin()
            wnd.HideHeader()
            wnd.HideBackground()

    def Unpin(self, *args, **kwds):
        uicls.WindowStackCore.Unpin(self, *args, **kwds)
        for wnd in self.GetWindows():
            if wnd is None or wnd.destroyed:
                continue
            wnd.Unpin()

    def RemoveWnd(self, wnd, grab, correctpos = 1, idx = 0, dragging = 0, check = 1):
        if wnd.parent != self.sr.content:
            return
        if hasattr(wnd, 'OnTabSelect'):
            uthread.worker('WindowStack::RemoveWnd', wnd.OnTabSelect)
        if self.IsPinned():
            sm.GetService('window').ToggleLiteWindowAppearance(wnd, True)
        wnd._detaching = True
        uiutil.Transplant(wnd, self.parent, idx)
        wnd.sr.stack = None
        wnd.sr.tab = None
        wnd.align = uiconst.RELATIVE
        wnd.state = uiconst.UI_NORMAL
        wnd.grab = grab
        wnd.width = wnd._fixedWidth or self.width
        wnd.height = wnd._fixedHeight or self.height
        wnd.RefreshHeaderButtonsIfVisible()
        if dragging:
            uicore.uilib.SetMouseCapture(wnd)
            uthread.new(wnd._BeginDrag)
            if wnd.height < wnd.GetMinHeight():
                wnd.height = wnd.GetMinHeight()
            if wnd.width < wnd.GetMinWidth():
                wnd.width = wnd.GetMinWidth()
        wnd.ShowHeader()
        wnd.ShowBackground()
        if correctpos:
            wnd.left = uicore.uilib.x - grab[0]
            wnd.top = uicore.uilib.y - grab[1]
        if check:
            self.Check()
        wnd.RegisterStackID()
        wnd._detaching = False
        wnd._dragging = dragging
        myWindows = self.GetWindows()
        if len(myWindows) == 1 and not self.IsCollapsed():
            w = myWindows[0]
            aL, aT, aW, aH = self.GetAbsolute()
            x, y = aL, aT
            self.RemoveWnd(w, (0, 0), 1, 1, check=0)
            w.left, w.top = x, y
            return
        if len(self.GetWindows()) == 0:
            self.sr.tabs.Close()
            self.Close()

    def GetCollapsedHeight(self):
        return self.sr.tabs.height + 4