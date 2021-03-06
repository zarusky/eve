#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/client/script/ui/maingame/charControl.py
import uiconst
import uicls

class CoreCharControl(uicls.LayerCore):
    __guid__ = 'uicls.CharControlCore'

    def ApplyAttributes(self, *args, **kw):
        uicls.LayerCore.ApplyAttributes(self, *args, **kw)
        self.opened = 0
        self.cursor = uiconst.UICURSOR_CROSS

    def GetConfigValue(self, data, name, default):
        return default

    def OnOpenView(self):
        self.isTabStop = True
        self.state = uiconst.UI_NORMAL
        self.OnSetFocus()

    def OnCloseView(self):
        self.OnKillFocus()
        self.isTabStop = False

    def OnKillFocus(self, *args):
        nav = sm.GetService('navigation')
        nav.controlLayer = None
        nav.hasFocus = False
        nav.RecreatePlayerMovement()

    def OnSetFocus(self, *args):
        nav = sm.GetService('navigation')
        nav.controlLayer = self
        nav.hasFocus = True
        nav.RecreatePlayerMovement()