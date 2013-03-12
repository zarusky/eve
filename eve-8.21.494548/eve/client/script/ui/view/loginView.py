#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/ui/view/loginView.py
from viewstate import View
from form import LoginII
import uthread

class LoginView(View):
    __guid__ = 'viewstate.LoginView'
    __notifyevents__ = []
    __dependencies__ = []
    __layerClass__ = LoginII
    __progressText__ = None

    def __init__(self):
        View.__init__(self)

    def UnloadView(self):
        View.UnloadView(self)