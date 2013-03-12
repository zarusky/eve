#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/ui/shared/neocom/charactersheet.py
import service
import blue
import uthread
import uix
import uiutil
import xtriui
import form
import util
import skillUtil
import listentry
import base
import uicls
import uiconst
import localization
import localizationUtil
import bluepy
import moniker
import telemetry
from service import ROLE_PROGRAMMER
MAXBIOLENGTH = 1000

class CharacterSheet(service.Service):
    __exportedcalls__ = {'Show': [],
     'SetHint': []}
    __update_on_reload__ = 0
    __guid__ = 'svc.charactersheet'
    __notifyevents__ = ['ProcessSessionChange',
     'OnGodmaSkillStartTraining',
     'OnGodmaSkillTrainingStopped',
     'OnGodmaSkillTrained',
     'OnGodmaItemChange',
     'OnAttribute',
     'OnAttributes',
     'OnRankChange',
     'OnCloneJumpUpdate',
     'OnKillNotification',
     'OnSessionChanged',
     'OnCertificateIssued',
     'OnCertVisibilityChange',
     'OnUpdatedMedalsAvailable',
     'OnUpdatedMedalStatusAvailable',
     'OnRespecInfoUpdated',
     'OnGodmaSkillTrainingSaved',
     'OnGodmaSkillInjected',
     'OnSkillStarted',
     'OnSkillQueueRefreshed',
     'OnCloneTypeUpdated',
     'OnFreeSkillPointsChanged_Local',
     'OnUIRefresh',
     'OnKillRightSold',
     'OnKillRightExpired',
     'OnKillRightSellCancel',
     'OnKillRightCreated',
     'OnKillRightUsed']
    __servicename__ = 'charactersheet'
    __displayname__ = 'Character Sheet Client Service'
    __dependencies__ = ['clonejump']
    __startupdependencies__ = ['settings', 'skills', 'neocom']

    def Run(self, memStream = None):
        self.LogInfo('Starting Character Sheet')
        sm.FavourMe(self.OnSessionChanged)
        self.Reset()
        if not sm.GetService('skills').SkillInTraining():
            sm.GetService('neocom').Blink('charactersheet')

    def Stop(self, memStream = None):
        self.entryTmpl = None
        self.bio = None
        wnd = self.GetWnd()
        if wnd is not None and not wnd.destroyed:
            wnd.Close()

    def OnUIRefresh(self, *args):
        wnd = form.CharacterSheet.GetIfOpen()
        if wnd:
            wnd.Close()
            self.Show()

    def ProcessSessionChange(self, isremote, session, change):
        if session.charid is None:
            self.Stop()
            self.Reset()

    def OnSessionChanged(self, isRemote, session, change):
        if 'corpid' in change:
            wnd = self.GetWnd()
            if wnd is not None and not wnd.destroyed:
                wnd.sr.employmentList = None
                selection = [ each for each in wnd.sr.nav.GetSelected() if each.key == 'employment' ]
                if selection:
                    self.showing = None
                    self.Load('employment')

    def OnRankChange(self, oldrank, newrank):
        if not session.warfactionid:
            return
        rankLabel, rankDescription = sm.GetService('facwar').GetRankLabel(session.warfactionid, newrank)
        if newrank > oldrank:
            blinkMsg = cfg.GetMessage('RankGained', {'rank': rankLabel}).text
        else:
            blinkMsg = cfg.GetMessage('RankLost', {'rank': rankLabel}).text
        self.ReloadMyRanks()
        sm.GetService('neocom').Blink('charactersheet', blinkMsg)

    def OnGodmaSkillStartTraining(self, *args):
        sm.GetService('neocom').BlinkOff('charactersheet')
        if self.showing == 'myskills_skills':
            self.ReloadMySkills()

    def OnGodmaSkillTrainingStopped(self, skillID, silent = 0, *args):
        if not silent:
            sm.GetService('neocom').Blink('charactersheet')
        if self.showing == 'myskills_skills':
            self.ReloadMySkills()

    def OnGodmaSkillTrained(self, skillID):
        sm.GetService('neocom').Blink('charactersheet')
        if self.showing == 'myskills_skills':
            self.ReloadMySkills()
        self.LoadGeneralInfo()

    def OnGodmaSkillTrainingSaved(self):
        if self.showing == 'myskills_skills':
            self.ReloadMySkills()

    def OnGodmaSkillInjected(self):
        if self.showing == 'myskills_skills':
            self.ReloadMySkills()

    def OnGodmaItemChange(self, item, change):
        if const.ixLocationID in change and item.categoryID == const.categoryImplant and item.flagID in [const.flagBooster, const.flagImplant]:
            sm.GetService('neocom').Blink('charactersheet')
            if self.showing == 'myimplants_boosters':
                self.ShowMyImplantsAndBoosters()
        elif const.ixFlag in change and item.categoryID == const.categorySkill:
            if self.showing == 'myskills_skills':
                self.ReloadMySkills()
        self.LoadGeneralInfo()

    def OnAttribute(self, attributeName, item, value):
        if attributeName == 'skillPoints' and self.showing == 'myskills_skills':
            self.ReloadMySkills()
        elif attributeName in ('memory', 'intelligence', 'willpower', 'perception', 'charisma') and self.showing == 'myattributes':
            self.UpdateMyAttributes(util.LookupConstValue('attribute%s' % attributeName.capitalize(), 0), value)

    def OnAttributes(self, changes):
        for attributeName, item, value in changes:
            self.OnAttribute(attributeName, item, value)

    def OnKillRightSold(self, killRightID):
        if self.showing == 'killrights':
            self.ShowKillRights()

    def OnKillRightExpired(self, killRightID):
        if self.showing == 'killrights':
            self.ShowKillRights()

    def OnKillRightSellCancel(self, killRightID):
        if self.showing == 'killrights':
            self.ShowKillRights()

    def OnKillRightCreated(self, killRightID, fromID, toID, expiryTime):
        if self.showing == 'killrights':
            self.ShowKillRights()

    def OnKillRightUsed(self, killRightID, toID):
        if self.showing == 'killrights':
            self.ShowKillRights()

    def OnCloneJumpUpdate(self):
        if self.showing == 'jumpclones':
            self.ShowJumpClones()

    def OnKillNotification(self):
        sm.StartService('objectCaching').InvalidateCachedMethodCall('charMgr', 'GetRecentShipKillsAndLosses', 25, None)

    def OnCertificateIssued(self, certificateID = None):
        if certificateID:
            certLabel, grade, certDescription = sm.GetService('certificates').GetCertificateLabel(certificateID)
            blinkMsg = cfg.GetMessage('CertAwarded', {'certificate': certLabel}).text
        else:
            blinkMsg = cfg.GetMessage('CertsAwarded').text
        sm.GetService('neocom').Blink('charactersheet', blinkMsg)
        if self.showing == 'mycertificates_certificates':
            self.ShowMyCerts()

    def OnUpdatedMedalsAvailable(self):
        sm.GetService('neocom').Blink('charactersheet')
        wnd = self.GetWnd()
        if wnd is None:
            return
        wnd.sr.decoMedalList = None
        if self.showing.startswith('mydecorations_'):
            self.ShowMyDecorations(self.showing)

    def OnUpdatedMedalStatusAvailable(self):
        wnd = self.GetWnd()
        if wnd is None or wnd.destroyed:
            return
        if self.showing.startswith('mydecorations_permissions'):
            wnd.sr.decoMedalList = None
            self.ShowMyDecorations(self.showing)

    def OnRespecInfoUpdated(self):
        if self.showing == 'myattributes':
            self.ShowMyAttributes()

    def OnSkillStarted(self, skillID = None, level = None):
        if self.showing == 'myskills_skills':
            self.ReloadMySkills()

    def OnSkillQueueRefreshed(self):
        if self.showing == 'myskills_skills':
            self.ReloadMySkills()

    def OnCloneTypeUpdated(self, newCloneType):
        sm.GetService('objectCaching').InvalidateCachedMethodCall('charMgr', 'GetCloneTypeID')
        self.LoadGeneralInfo()
        sm.ScatterEvent('OnCloneTypeUpdatedClient')

    def OnFreeSkillPointsChanged_Local(self):
        if self.showing == 'myskills_skills':
            self.ReloadMySkills()

    def Reset(self):
        self.panels = []
        self.standingsinited = 0
        self.mydecorationsinited = 0
        self.standingtabs = None
        self.mydecorationstabs = None
        self.skillsinited = 0
        self.skilltabs = None
        self.killsinited = 0
        self.killstabs = None
        self.killentries = 25
        self.showing = None
        self.skillTimer = None
        self.jumpClones = False
        self.jumpCloneImplants = False
        self.bio = None
        self.visibilityChanged = {}
        self.daysLeft = -1

    def Show(self):
        wnd = self.GetWnd(1)
        if wnd is not None and not wnd.destroyed:
            wnd.Maximize()
            return wnd

    def GetWnd(self, getnew = 0):
        if not getnew:
            return form.CharacterSheet.GetIfOpen()
        else:
            return form.CharacterSheet.ToggleOpenClose()

    def OnCertVisibilityChange(self, certID, flag, serverVisibility):
        wnd = self.GetWnd()
        if flag == serverVisibility:
            if certID in self.visibilityChanged:
                self.visibilityChanged.pop(certID)
        else:
            self.visibilityChanged[certID] = flag

    def OpenCertificateWindow(self, *args):
        sm.StartService('certificates').OpenCertificateWindow()

    def OpenSkillQueueWindow(self, *args):
        uicore.cmd.OpenSkillQueueWindow()

    @telemetry.ZONE_METHOD
    def GetNavEntries(self, wnd):
        nav = [[localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/NavScroll/Skills'),
          wnd.sr.scroll,
          'ui_50_64_13',
          'myskills',
          settings.user.ui.Get('charsheetorder_myskills', 0),
          'characterSheetMenuSkillsBtn'],
         [localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/NavScroll/Certificates'),
          wnd.sr.scroll,
          'ui_79_64_1',
          'mycertificates',
          settings.user.ui.Get('charsheetorder_mycertificates', 1),
          'characterSheetMenuCertificatesBtn'],
         [localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/NavScroll/Decorations'),
          wnd.sr.scroll,
          'ui_35_64_9',
          'mydecorations',
          settings.user.ui.Get('charsheetorder_mydecorations', 2),
          'characterSheetMenuDecorationsBtn'],
         [localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/NavScroll/Attributes'),
          wnd.sr.scroll,
          'ui_25_64_15',
          'myattributes',
          settings.user.ui.Get('charsheetorder_myattributes', 3),
          'characterSheetMenuAttributesBtn'],
         [localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/NavScroll/Augmentations'),
          wnd.sr.scroll,
          'ui_25_64_14',
          'myimplants_boosters',
          settings.user.ui.Get('charsheetorder_myimplants_boosters', 4),
          'characterSheetMenuImplantsBtn'],
         [localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/NavScroll/JumpClones'),
          wnd.sr.scroll,
          'ui_8_64_16',
          'jumpclones',
          settings.user.ui.Get('charsheetorder_jumpclones', 5),
          'characterSheetMenuJumpclonesBtn'],
         [localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/NavScroll/Bio'),
          wnd.sr.bioparent,
          'ui_7_64_8',
          'bio',
          settings.user.ui.Get('charsheetorder_bio', 6),
          'characterSheetMenuBioBtn'],
         [localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/NavScroll/EmploymentHistory'),
          wnd.sr.scroll,
          'ui_7_64_6',
          'employment',
          settings.user.ui.Get('charsheetorder_employment', 7),
          'characterSheetMenuEmploymentBtn'],
         [localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/NavScroll/Standings'),
          wnd.sr.scroll,
          'ui_25_64_10',
          'mystandings',
          settings.user.ui.Get('charsheetorder_mystandings', 8),
          'characterSheetMenuStandingBtn'],
         [localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/NavScroll/SecurityStatus'),
          wnd.sr.scroll,
          'ui_7_64_7',
          'securitystatus',
          settings.user.ui.Get('charsheetorder_securitystatus', 9),
          'characterSheetMenuSecurityStatusBtn'],
         [localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/NavScroll/KillRights'),
          wnd.sr.scroll,
          'ui_26_64_5',
          'killrights',
          settings.user.ui.Get('charsheetorder_killrights', 10),
          'characterSheetMenuKillRightsBtn'],
         [localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/NavScroll/CombatLog'),
          wnd.sr.scroll,
          'ui_50_64_15',
          'mykills',
          settings.user.ui.Get('charsheetorder_mykills', 11),
          'characterSheetMenuKillsBtn'],
         [localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/NavScroll/PilotLicense'),
          wnd.sr.scroll,
          'ui_57_64_3',
          'pilotlicense',
          settings.user.ui.Get('charsheetorder_pilotlicense', 12),
          'characterSheetMenuPilotLicenseBtn']]
        navEntries = []
        for each in nav:
            navEntries.append((each[4], each))

        navEntries = uiutil.SortListOfTuples(navEntries)
        return navEntries

    def SetHint(self, hintstr = None):
        wnd = self.GetWnd()
        if wnd is not None:
            wnd.sr.scroll.ShowHint(hintstr)

    def OnCloseWnd(self, wnd, *args):
        if self.showing == 'bio':
            self.AutoSaveBio()
        self.bioinited = 0
        self.showing = None
        settings.user.ui.Set('charsheetleftwidth', wnd.sr.leftSide.width)
        self.panels = []

    def OnSelectEntry(self, node):
        if node != []:
            self.Load(node[0].key)
            settings.char.ui.Set('charactersheetselection', node[0].idx)

    @telemetry.ZONE_METHOD
    def HideScrolls(self):
        wnd = self.GetWnd()
        for each in [wnd.sr.scroll, wnd.sr.bioparent]:
            each.state = uiconst.UI_HIDDEN

    def Load(self, key):
        wnd = self.GetWnd()
        if not wnd:
            return
        if getattr(self, 'loading', 0) or self.showing == key:
            return
        self.loading = 1
        if self.showing == 'bio':
            self.AutoSaveBio()
        self.HideScrolls()
        for uielement in ['standingtabs',
         'killstabs',
         'skilltabs',
         'btnContainer',
         'mydecorationstabs',
         'buttonParCert',
         'buttonParDeco',
         'certificatepanel',
         'certtabs',
         'skillpanel',
         'combatlogpanel']:
            e = getattr(wnd.sr, uielement, None)
            if e:
                e.state = uiconst.UI_HIDDEN

        if key.startswith('pilotlicense'):
            wnd.sr.scroll.Clear()
            wnd.sr.scroll.state = uiconst.UI_PICKCHILDREN
            if self.daysLeft == -1:
                charDetails = sm.RemoteSvc('charUnboundMgr').GetCharacterToSelect(eve.session.charid)
                self.daysLeft = getattr(charDetails, 'daysLeft', None)
            data = {'daysLeft': self.daysLeft,
             'buyPlexOnMarket': self.BuyPlexOnMarket,
             'buyPlexOnline': self.BuyPlexOnline}
            wnd.sr.pilotLicenceEntry = listentry.Get('PilotLicence', data)
            wnd.sr.scroll.Load(contentList=[wnd.sr.pilotLicenceEntry])
        elif key.startswith('mystandings'):
            wnd.sr.scroll.state = uiconst.UI_PICKCHILDREN
            if not wnd.sr.standingsinited:
                wnd.sr.standingsinited = 1
                tabs = uicls.TabGroup(name='tabparent', parent=wnd.sr.mainArea, idx=0, tabs=[[localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/StandingTabs/LikedBy'),
                  wnd.sr.scroll,
                  self,
                  'mystandings_to_positive'], [localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/StandingTabs/DislikeBy'),
                  wnd.sr.scroll,
                  self,
                  'mystandings_to_negative']], groupID='cs_standings')
                wnd.sr.standingtabs = tabs
                self.loading = 0
                wnd.sr.standingtabs.AutoSelect()
                return
            if getattr(wnd.sr, 'standingtabs', None):
                wnd.sr.standingtabs.state = uiconst.UI_NORMAL
            wnd.sr.standingtabs.state = uiconst.UI_NORMAL
            if key == 'mystandings':
                self.loading = 0
                wnd.sr.standingtabs.AutoSelect()
                return
            self.SetHint()
            if key == 'mystandings_to_positive':
                positive = True
            else:
                positive = False
            self.ShowStandings(positive)
        elif key.startswith('myskills'):
            wnd.sr.scroll.state = uiconst.UI_PICKCHILDREN
            if not wnd.sr.skillsinited:
                wnd.sr.skillsinited = 1
                tabs = uicls.TabGroup(name='tabparent', parent=wnd.sr.mainArea, idx=0, tabs=[[localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/Skills'),
                  wnd.sr.scroll,
                  self,
                  'myskills_skills'], [localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/History'),
                  wnd.sr.scroll,
                  self,
                  'myskills_skillhistory'], [localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/Settings'),
                  wnd.sr.scroll,
                  self,
                  'myskills_settings']], groupID='cs_skills', UIIDPrefix='characterSheetTab')
                wnd.sr.skilltabs = tabs
                self.loading = 0
                wnd.sr.skilltabs.AutoSelect()
                return
            if getattr(wnd.sr, 'skilltabs', None):
                wnd.sr.skilltabs.state = uiconst.UI_NORMAL
            if key == 'myskills':
                if self.showing == 'myskills_skills':
                    if getattr(wnd.sr, 'skillpanel', None):
                        wnd.sr.skillpanel.state = uiconst.UI_NORMAL
                self.loading = 0
                wnd.sr.skilltabs.AutoSelect()
                return
            self.SetHint()
            self.ShowSkills(key)
        elif key.startswith('mydecorations'):
            wnd.sr.scroll.state = uiconst.UI_PICKCHILDREN
            if not wnd.sr.mydecorationsinited:
                wnd.sr.mydecorationsinited = 1
                tabs = uicls.TabGroup(name='tabparent', parent=wnd.sr.mainArea, idx=0, tabs=[[localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/DecoTabs/Ranks'),
                  wnd.sr.scroll,
                  self,
                  'mydecorations_ranks'], [localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/DecoTabs/Medals'),
                  wnd.sr.scroll,
                  self,
                  'mydecorations_medals'], [localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/DecoTabs/Permissions'),
                  wnd.sr.scroll,
                  self,
                  'mydecorations_permissions']], groupID='cs_decorations')
                wnd.sr.mydecorationstabs = tabs
                self.loading = 0
                wnd.sr.mydecorationstabs.AutoSelect()
                return
            if getattr(wnd.sr, 'mydecorationstabs', None):
                wnd.sr.mydecorationstabs.state = uiconst.UI_NORMAL
            if key == 'mydecorations':
                self.loading = 0
                wnd.sr.mydecorationstabs.AutoSelect()
                if self.showing == 'mydecorations_permissions':
                    wnd.sr.buttonParDeco.state = uiconst.UI_NORMAL
                return
            self.SetHint()
            self.ShowMyDecorations(key)
        elif key.startswith('mykills'):
            wnd.sr.scroll.state = uiconst.UI_PICKCHILDREN
            if getattr(wnd.sr, 'combatlogpanel', None):
                wnd.sr.combatlogpanel.state = uiconst.UI_NORMAL
            if not wnd.sr.killsinited:
                wnd.sr.killsinited = 1
                btnContainer = uicls.Container(name='pageBtnContainer', parent=wnd.sr.mainArea, align=uiconst.TOBOTTOM, idx=0, padBottom=4)
                btn = uix.GetBigButton(size=22, where=btnContainer, left=4, top=0)
                btn.SetAlign(uiconst.CENTERRIGHT)
                btn.hint = localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/KillsTabs/ViewMore')
                btn.sr.icon.LoadIcon('ui_23_64_2')
                btn = uix.GetBigButton(size=22, where=btnContainer, left=4, top=0)
                btn.SetAlign(uiconst.CENTERLEFT)
                btn.hint = localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/KillsTabs/ViewPrevious')
                btn.sr.icon.LoadIcon('ui_23_64_1')
                btnContainer.height = max([ c.height for c in btnContainer.children ])
                wnd.sr.btnContainer = btnContainer
                self.ShowKills()
                self.showing = 'mykills'
                self.loading = 0
                return
            self.ShowKills()
        elif key.startswith('mycertificates'):
            wnd.sr.scroll.state = uiconst.UI_PICKCHILDREN
            if not wnd.sr.certsinited:
                wnd.sr.certsinited = 1
                tabs = uicls.TabGroup(name='tabparent', parent=wnd.sr.mainArea, idx=0, tabs=[[localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/CertTabs/Certificates'),
                  wnd.sr.scroll,
                  self,
                  'mycertificates_certificates'], [localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/CertTabs/Permissions'),
                  wnd.sr.scroll,
                  self,
                  'mycertificates_permissions'], [localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/CertTabs/Settings'),
                  wnd.sr.scroll,
                  self,
                  'mycertificates_settings']], groupID='cs_certificates')
                wnd.sr.certtabs = tabs
                self.loading = 0
                wnd.sr.certtabs.AutoSelect()
                return
            if hasattr(wnd.sr, 'certtabs'):
                wnd.sr.certtabs.state = uiconst.UI_NORMAL
            if key == 'mycertificates':
                self.loading = 0
                wnd.sr.certtabs.AutoSelect()
            else:
                self.SetHint()
                self.ShowCertificates(key)
        else:
            if wnd.sr.standingsinited:
                wnd.sr.standingtabs.state = uiconst.UI_HIDDEN
            if wnd.sr.skillsinited:
                wnd.sr.skilltabs.state = uiconst.UI_HIDDEN
            if wnd.sr.mydecorationsinited:
                wnd.sr.mydecorationstabs.state = uiconst.UI_HIDDEN
            if wnd.sr.certsinited:
                wnd.sr.certtabs.state = uiconst.UI_HIDDEN
            self.SetHint()
            if key == 'myattributes':
                self.ShowMyAttributes()
            elif key == 'myimplants_boosters':
                self.ShowMyImplantsAndBoosters()
            elif key == 'bio':
                self.ShowMyBio()
            elif key == 'securitystatus':
                self.ShowSecurityStatus()
            elif key == 'killrights':
                self.ShowKillRights()
            elif key == 'jumpclones':
                self.ShowJumpClones()
            elif key == 'employment':
                self.ShowEmploymentHistory()
            elif key == 'mysettings':
                self.ShowSettings()
        self.showing = key
        self.loading = 0

    def BuyPlexOnMarket(self, *args):
        uthread.new(sm.StartService('marketutils').ShowMarketDetails, const.typePilotLicence, None)

    def BuyPlexOnline(self, *args):
        self.GoTo(self.GetPlexUrl())

    def LoadGeneralInfo(self):
        if getattr(self, 'loadingGeneral', 0):
            return
        wnd = self.GetWnd()
        if wnd is None or wnd.destroyed:
            return
        self.loadingGeneral = 1
        uix.Flush(wnd.sr.topParent)
        characterName = cfg.eveowners.Get(eve.session.charid).name
        if not getattr(self, 'charMgr', None):
            self.charMgr = sm.RemoteSvc('charMgr')
        if not getattr(self, 'cc', None):
            self.charsvc = sm.GetService('cc')
        wnd.sr.charinfo = charinfo = self.charMgr.GetPublicInfo(eve.session.charid)
        if settings.user.ui.Get('charsheetExpanded', 1):
            uiutil.Update(self)
            parent = wnd.sr.topParent
            wnd.sr.picParent = uicls.Container(name='picpar', parent=parent, align=uiconst.TOPLEFT, width=200, height=200, left=const.defaultPadding, top=16)
            wnd.sr.pic = uicls.Sprite(parent=wnd.sr.picParent, align=uiconst.TOALL, left=1, top=1, height=1, width=1)
            wnd.sr.pic.OnClick = self.OpenPortraitWnd
            wnd.sr.pic.cursor = uiconst.UICURSOR_MAGNIFIER
            uicls.Frame(parent=wnd.sr.picParent)
            sm.GetService('photo').GetPortrait(eve.session.charid, 256, wnd.sr.pic)
            infoTextPadding = wnd.sr.picParent.width + const.defaultPadding * 4
            wnd.sr.nameText = uicls.EveCaptionMedium(text=characterName, parent=wnd.sr.topParent, left=infoTextPadding, top=12)
            wnd.sr.raceinfo = raceinfo = cfg.races.Get(charinfo.raceID)
            wnd.sr.bloodlineinfo = bloodlineinfo = cfg.bloodlines.Get(charinfo.bloodlineID)
            wnd.sr.schoolinfo = schoolinfo = self.charsvc.GetData('schools', ['schoolID', charinfo.schoolID])
            wnd.sr.ancestryinfo = ancestryinfo = self.charsvc.GetData('ancestries', ['ancestryID', charinfo.ancestryID])
            if wnd is None or wnd.destroyed:
                self.loadingGeneral = 0
                return
            securityStatus = sm.GetService('standing').GetMySecurityRating()
            roundedSecurityStatus = localizationUtil.FormatNumeric(securityStatus, decimalPlaces=1)
            cloneTypeID = self.GetCloneTypeID()
            godmaInfo = sm.GetService('godma').GetType(cloneTypeID)
            cloneLocation = sm.RemoteSvc('charMgr').GetHomeStation()
            if cloneLocation:
                cloneLocationInfo = sm.GetService('ui').GetStation(cloneLocation)
                if cloneLocationInfo:
                    systemID = cloneLocationInfo.solarSystemID
                    cloneLocationHint = localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/CloneLocationHint', locationId=cloneLocation, systemId=systemID)
                    cloneLocation = cfg.evelocations.Get(systemID).name
                else:
                    cloneLocationHint = cfg.evelocations.Get(cloneLocation).name
                    cloneLocation = localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/UnknownSystem')
            else:
                cloneLocation = localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/UnknownSystem')
                cloneLocationHint = ''
            alliance = ''
            if eve.session.allianceid:
                cfg.eveowners.Prime([eve.session.allianceid])
                alliance = (localization.GetByLabel('UI/Common/Alliance'), cfg.eveowners.Get(eve.session.allianceid).name, '')
            faction = ''
            if eve.session.warfactionid:
                fac = sm.StartService('facwar').GetFactionalWarStatus()
                faction = (localization.GetByLabel('UI/Common/Militia'), cfg.eveowners.Get(fac.factionID).name, '')
            bounty = ''
            bountyOwnerIDs = (session.charid, session.corpid, session.allianceid)
            bountyAmount = sm.GetService('bountySvc').GetBounty(*bountyOwnerIDs)
            bountyAmounts = sm.GetService('bountySvc').GetBounties(*bountyOwnerIDs)
            charBounty = 0
            corpBounty = 0
            allianceBounty = 0
            if len(bountyAmounts):
                for ownerID, value in bountyAmounts.iteritems():
                    if util.IsCharacter(ownerID):
                        charBounty = value
                    elif util.IsCorporation(ownerID):
                        corpBounty = value
                    elif util.IsAlliance(ownerID):
                        allianceBounty = value

            bountyHint = localization.GetByLabel('UI/Station/BountyOffice/BountyHint', charBounty=util.FmtISK(charBounty, 0), corpBounty=util.FmtISK(corpBounty, 0), allianceBounty=util.FmtISK(allianceBounty, 0))
            bounty = (localization.GetByLabel('UI/Station/BountyOffice/Bounty'), util.FmtISK(bountyAmount, 0), bountyHint)
            skillPoints = int(sm.GetService('skills').GetSkillPoints())
            textList = [(localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillPoints'), localizationUtil.FormatNumeric(skillPoints, useGrouping=True), ''),
             (localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/Clone'), localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/CloneInfo', cloneType=cloneTypeID, cloneSkillPoints=godmaInfo.skillPointsSaved), ''),
             (localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/HomeSystem'), cloneLocation, cloneLocationHint),
             (localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/CharacterBackground'), localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/CharacterBackgroundInformation', raceName=localization.GetByMessageID(raceinfo.raceNameID), bloodlineName=localization.GetByMessageID(bloodlineinfo.bloodlineNameID), ancestryName=localization.GetByMessageID(ancestryinfo.ancestryNameID)), localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/CharacterBackgroundHint')),
             (localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/DateOfBirth'), localizationUtil.FormatDateTime(charinfo.createDateTime, dateFormat='long', timeFormat='long'), ''),
             (localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/School'), localization.GetByMessageID(schoolinfo.schoolNameID), ''),
             (localization.GetByLabel('UI/Common/Corporation'), cfg.eveowners.Get(eve.session.corpid).name, ''),
             (localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SecurityStatus'), roundedSecurityStatus, localizationUtil.FormatNumeric(securityStatus, decimalPlaces=4))]
            if faction:
                textList.insert(len(textList) - 1, faction)
            if alliance:
                textList.insert(len(textList) - 1, alliance)
            if bounty:
                textList.insert(len(textList), bounty)
            numLines = len(textList) + 2
            mtext = 'Xg<br>' * numLines
            mtext = mtext[:-4]
            th = uix.GetTextHeight(mtext)
            topParentHeight = max(220, th + const.defaultPadding * 2 + 2)
            top = max(34, wnd.sr.nameText.top + wnd.sr.nameText.height)
            leftContainer = uicls.Container(parent=wnd.sr.topParent, left=infoTextPadding, top=top, align=uiconst.TOPLEFT)
            rightContainer = uicls.Container(parent=wnd.sr.topParent, top=top, align=uiconst.TOPLEFT)
            subTop = 0
            for label, value, hint in textList:
                label = uicls.EveLabelMedium(text=label, parent=leftContainer, idx=0, state=uiconst.UI_NORMAL, align=uiconst.TOPLEFT, top=subTop)
                label.hint = hint
                label._tabMargin = 0
                display = uicls.EveLabelMedium(text=value, parent=rightContainer, idx=0, state=uiconst.UI_NORMAL, align=uiconst.TOPLEFT, top=subTop)
                display.hint = hint
                display._tabMargin = 0
                subTop += label.height

            leftContainer.AutoFitToContent()
            rightContainer.left = leftContainer.left + leftContainer.width + 20
            rightContainer.AutoFitToContent()
            wnd.SetTopparentHeight(max(topParentHeight, rightContainer.height, leftContainer.height))
        else:
            wnd.SetTopparentHeight(18)
        charsheetExpanded = settings.user.ui.Get('charsheetExpanded', 1)
        if not charsheetExpanded:
            uicls.EveLabelMedium(text=characterName, parent=wnd.sr.topParent, left=8, top=1, state=uiconst.UI_DISABLED)
        expandOptions = [localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/Expand'), localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/Collapse')]
        a = uicls.EveLabelSmall(text=expandOptions[charsheetExpanded], parent=wnd.sr.topParent, left=18, top=3, state=uiconst.UI_NORMAL, align=uiconst.TOPRIGHT, bold=True)
        a.OnClick = self.ToggleGeneral
        expander = uicls.Sprite(parent=wnd.sr.topParent, pos=(6, 2, 11, 11), name='expandericon', state=uiconst.UI_NORMAL, texturePath=['res:/UI/Texture/Shared/expanderDown.png', 'res:/UI/Texture/Shared/expanderUp.png'][charsheetExpanded], align=uiconst.TOPRIGHT)
        expander.OnClick = self.ToggleGeneral
        self.loadingGeneral = 0

    def GetCloneTypeID(self):
        cloneTypeID = sm.RemoteSvc('charMgr').GetCloneTypeID()
        if not cloneTypeID:
            cloneTypeID = const.typeCloneGradeAlpha
        return cloneTypeID

    def OpenPortraitWnd(self, *args):
        form.PortraitWindow.CloseIfOpen()
        form.PortraitWindow.Open(charID=session.charid)

    def ToggleGeneral(self, *args):
        charsheetExpanded = not settings.user.ui.Get('charsheetExpanded', 1)
        settings.user.ui.Set('charsheetExpanded', charsheetExpanded)
        self.LoadGeneralInfo()

    def ShowSecurityStatus(self):
        data = sm.RemoteSvc('standing2').GetStandingTransactions(const.ownerCONCORD, eve.session.charid, 1, None, None, None)
        wnd = self.GetWnd()
        wnd.sr.scroll.state = uiconst.UI_PICKCHILDREN
        if not wnd:
            return
        wnd.sr.scroll.sr.id = 'charsheet_securitystatus'
        wnd.sr.scroll.Clear()
        scrolllist = []
        headers = []
        fromName = cfg.eveowners.Get(const.ownerCONCORD).name
        for each in data:
            when = util.FmtDate(each.eventDateTime, 'ls')
            subject, body = util.FmtStandingTransaction(each)
            text = when + '<t>'
            text += localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SecurityStatusScroll/Persentage', value=each.modification * 100.0, decimalPlaces=4) + '<t>'
            text += subject
            scrolllist.append(listentry.Get('StandingTransaction', {'sort_%s' % localization.GetByLabel('UI/Common/Date'): each.eventDateTime,
             'sort_%s' % localization.GetByLabel('UI/Common/Change'): each.modification,
             'line': 1,
             'text': text,
             'details': body,
             'isNPC': True}))

        if not wnd:
            return
        headers = [localization.GetByLabel('UI/Common/Date'), localization.GetByLabel('UI/Common/Change'), localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SecurityStatusScroll/Subject')]
        noChangesHint = localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SecurityStatusScroll/NoSecurityStatusChanges')
        wnd.sr.scroll.Load(contentList=scrolllist, headers=headers, noContentHint=noChangesHint)

    def ShowMyDecorations(self, key = None):
        wnd = self.GetWnd()
        if wnd is None:
            return
        wnd.sr.buttonParDeco.state = uiconst.UI_HIDDEN
        if key == 'mydecorations_ranks':
            self.ShowMyRanks()
        elif key == 'mydecorations_medals':
            self.ShowMyMedals()
        elif key == 'mydecorations_permissions':
            wnd.sr.buttonParDeco.state = uiconst.UI_NORMAL
            self.ShowMyDecorationPermissions()

    def ShowMyMedals(self, charID = None):
        wnd = self.GetWnd()
        wnd.sr.scroll.state = uiconst.UI_PICKCHILDREN
        if charID is None:
            charID = session.charid
        if wnd.sr.decoMedalList is None:
            wnd.sr.decoMedalList = self.GetMedalScroll(charID)
        wnd.sr.scroll.sr.id = 'charsheet_mymedals'
        wnd.sr.scroll.Load(contentList=wnd.sr.decoMedalList, noContentHint=localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/DecoTabs/NoMedals'))

    def GetMedalScroll(self, charID, noHeaders = False, publicOnly = False):
        scrolllist = []
        inDecoList = []
        publicDeco = (sm.StartService('medals').GetMedalsReceivedWithFlag(charID, [3]), localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/DecoTabs/Public'))
        privateDeco = (sm.StartService('medals').GetMedalsReceivedWithFlag(charID, [2]), localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/DecoTabs/Private'))
        characterMedals, characterMedalInfo = sm.StartService('medals').GetMedalsReceived(charID)
        if publicOnly:
            t = (publicDeco,)
        else:
            t = (publicDeco, privateDeco)
        for deco, hint in t:
            if deco and not noHeaders:
                scrolllist.append(listentry.Get('Header', {'label': hint}))
            for medalID, medalData in deco.iteritems():
                if medalID in inDecoList:
                    continue
                inDecoList.append(medalID)
                details = characterMedalInfo.Filter('medalID')
                if details and details.has_key(medalID):
                    details = details.get(medalID)
                entry = sm.StartService('info').GetMedalEntry(None, medalData, details, 0)
                if entry:
                    scrolllist.append(entry)

        return scrolllist

    def ShowMyRanks(self):
        wnd = self.GetWnd()
        wnd.sr.scroll.state = uiconst.UI_PICKCHILDREN
        if wnd.sr.decoRankList is None:
            scrolllist = []
            characterRanks = sm.StartService('facwar').GetCharacterRankOverview(session.charid)
            for characterRank in characterRanks:
                entry = sm.StartService('info').GetRankEntry(characterRank)
                if entry:
                    scrolllist.append(entry)

            wnd.sr.decoRankList = scrolllist[:]
        wnd.sr.scroll.sr.id = 'charsheet_myranks'
        wnd.sr.scroll.Load(contentList=wnd.sr.decoRankList, noContentHint=localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/DecoTabs/NoRanks'))

    def ShowEmploymentHistory(self):
        wnd = self.GetWnd()
        wnd.sr.scroll.state = uiconst.UI_PICKCHILDREN
        if wnd.sr.employmentList is None:
            wnd.sr.employmentList = sm.GetService('info').GetEmploymentHistorySubContent(eve.session.charid)
        wnd.sr.scroll.sr.id = 'charsheet_employmenthistory'
        wnd.sr.scroll.Load(contentList=wnd.sr.employmentList)

    def ShowKillRights(self):
        scrolllist = []
        killRights = sm.GetService('bountySvc').GetMyKillRights()
        currentTime = blue.os.GetWallclockTime()
        myKillRights = filter(lambda x: x.fromID == session.charid and currentTime < x.expiryTime, killRights)
        if myKillRights:
            scrolllist.append(listentry.Get('Header', {'label': localization.GetByLabel('UI/InfoWindow/CanKill'),
             'hideLines': True}))
            for killRight in myKillRights:
                scrolllist.append(listentry.Get('KillRightsEntry', {'charID': killRight.toID,
                 'expiryTime': killRight.expiryTime,
                 'killRight': killRight,
                 'isMine': True}))

        otherKillRights = filter(lambda x: x.toID == session.charid and currentTime < x.expiryTime, killRights)
        if otherKillRights:
            scrolllist.append(listentry.Get('Header', {'label': localization.GetByLabel('UI/InfoWindow/CanBeKilledBy'),
             'hideLines': True}))
            for killRight in otherKillRights:
                scrolllist.append(listentry.Get('KillRightsEntry', {'charID': killRight.fromID,
                 'expiryTime': killRight.expiryTime,
                 'killRight': killRight,
                 'isMine': False}))

        wnd = self.GetWnd()
        wnd.sr.scroll.state = uiconst.UI_PICKCHILDREN
        wnd.sr.scroll.sr.id = 'charsheet_killrights'
        wnd.sr.scroll.Load(contentList=scrolllist, noContentHint=localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/KillsTabs/NoKillRightsFound'))

    def ShowJumpClones(self):
        jumpCloneSvc = sm.GetService('clonejump')
        jumpClones = jumpCloneSvc.GetClones()
        scrolllist = []
        lastJump = jumpCloneSvc.LastCloneJumpTime()
        hoursLimit = const.limitCloneJumpHours
        if lastJump:
            jumpTime = lastJump + hoursLimit * const.HOUR
            nextJump = jumpTime > blue.os.GetWallclockTime()
        else:
            nextJump = False
        nextAvailableLabel = localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/JumpCloneScroll/NextCloneJump')
        availableNow = localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/JumpCloneScroll/Now')
        if nextJump:
            scrolllist.append(listentry.Get('TextTimer', {'line': 1,
             'label': nextAvailableLabel,
             'text': util.FmtDate(lastJump),
             'iconID': const.iconDuration,
             'countdownTime': jumpTime,
             'finalText': availableNow}))
        else:
            scrolllist.append(listentry.Get('TextTimer', {'line': 1,
             'label': nextAvailableLabel,
             'text': availableNow,
             'iconID': const.iconDuration,
             'countdownTime': 0}))
        if jumpClones:
            d = {}
            primeLocs = []
            for jc in jumpClones:
                jumpCloneID = jc.jumpCloneID
                locationID = jc.locationID
                primeLocs.append(locationID)
                label = 'station' if util.IsStation(locationID) else 'ship'
                if not d.has_key(label):
                    d[label] = {locationID: (jumpCloneID, locationID)}
                else:
                    d[label][locationID] = (jumpCloneID, locationID)

            cfg.evelocations.Prime(primeLocs)
            destroyedLocString = localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/JumpCloneScroll/CloneLocationDestroyed')
            destroyedLocName = localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/JumpCloneScroll/DestroyedLocation')
            for k in ('station', 'ship'):
                if d.has_key(k):
                    locIDs = d[k].keys()
                    locNames = []
                    for locID in locIDs:
                        if locID in cfg.evelocations:
                            locName = cfg.evelocations.Get(locID).name
                            locString = localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/JumpCloneScroll/CloneLocation', cloneLocation=locID)
                        else:
                            locName = destroyedLocName
                            locString = destroyedLocString
                        locNames.append((locName, locString, locID))

                    locName = localizationUtil.Sort(locNames, key=lambda x: x[0])
                    for locationName, locationString, locationID in locNames:
                        jumpCloneID = d[k][locationID]
                        groupID = d[k][locationID]
                        data = {'GetSubContent': self.GetCloneImplants,
                         'label': locationString,
                         'id': groupID,
                         'jumpCloneID': d[k][locationID][0],
                         'locationID': d[k][locationID][1],
                         'state': 'locked',
                         'iconMargin': 18,
                         'showicon': 'ui_8_64_16',
                         'sublevel': 0,
                         'MenuFunction': self.JumpCloneMenu,
                         'showlen': 0}
                        scrolllist.append(listentry.Get('Group', data))

        wnd = self.GetWnd()
        if wnd:
            wnd.sr.scroll.state = uiconst.UI_PICKCHILDREN
            wnd.sr.scroll.sr.id = 'charsheet_jumpclones'
            noClonesFoundHint = localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/JumpCloneScroll/NoJumpClonesFound')
            wnd.sr.scroll.Load(contentList=scrolllist, noContentHint=noClonesFoundHint)

    def GetCloneImplants(self, nodedata, *args):
        scrolllist = []
        godma = sm.GetService('godma')
        scrolllist.append(listentry.Get('CloneButtons', {'locationID': nodedata.locationID,
         'jumpCloneID': nodedata.jumpCloneID}))
        implants = uiutil.SortListOfTuples([ (getattr(godma.GetType(implant.typeID), 'implantness', None), implant) for implant in sm.GetService('clonejump').GetImplantsForClone(nodedata.jumpCloneID) ])
        if implants:
            for cloneImplantRow in implants:
                scrolllist.append(listentry.Get('ImplantEntry', {'implant_booster': cloneImplantRow,
                 'label': cfg.invtypes.Get(cloneImplantRow.typeID).name}))

        else:
            noImplantsString = localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/JumpCloneScroll/NoImplantsInstalled')
            scrolllist.append(listentry.Get('Text', {'label': noImplantsString,
             'text': noImplantsString}))
        return scrolllist

    def JumpCloneMenu(self, node):
        m = []
        validLocation = node.locationID in cfg.evelocations
        if eve.session.stationid and validLocation:
            m += [None]
            m += [(uiutil.MenuLabel('UI/CharacterSheet/CharacterSheetWindow/JumpCloneScroll/Jump'), sm.GetService('clonejump').CloneJump, (node.locationID,))]
        if validLocation:
            m.append((uiutil.MenuLabel('UI/CharacterSheet/CharacterSheetWindow/JumpCloneScroll/Destroy'), sm.GetService('clonejump').DestroyInstalledClone, (node.jumpCloneID,)))
        return m

    def ShowMyBio(self):
        wnd = self.GetWnd()
        if not wnd or wnd.destroyed:
            return
        wnd.sr.bioparent.state = uiconst.UI_PICKCHILDREN
        if not getattr(self, 'bioinited', 0):
            blue.pyos.synchro.Yield()
            wnd.sr.bio = uicls.EditPlainText(parent=wnd.sr.bioparent, maxLength=MAXBIOLENGTH, showattributepanel=1)
            wnd.sr.bio.sr.window = self
            wnd.sr.bioparent.OnTabDeselect = self.AutoSaveBio
            wnd.oldbio = ''
            if not self.bio:
                bio = sm.RemoteSvc('charMgr').GetCharacterDescription(eve.session.charid)
                if bio is not None:
                    self.bio = bio
                else:
                    self.bio = ''
            if not wnd or wnd.destroyed:
                return
            if self.bio:
                wnd.oldbio = self.bio
            self.bioinited = 1
        if wnd and not wnd.destroyed:
            wnd.sr.bio.SetValue(wnd.oldbio or localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/BioEdit/HereYouCanTypeBio'))

    def AutoSaveBio(self, edit = None, *args):
        wnd = self.GetWnd()
        if not wnd:
            return
        edit = edit or wnd.sr.bio
        if not edit:
            return
        newbio = edit.GetValue()
        defaultBioString = localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/BioEdit/HereYouCanTypeBio')
        newbio = newbio.replace(defaultBioString, '')
        if not len(uiutil.StripTags(newbio)):
            newbio = ''
        self.bio = newbio
        if wnd and newbio.strip() != wnd.oldbio:
            uthread.pool('CharaacterSheet::AutoSaveBio', self._AutoSaveBio, newbio)
            if wnd:
                wnd.oldbio = newbio

    def _AutoSaveBio(self, newbio):
        sm.RemoteSvc('charMgr').SetCharacterDescription(newbio)

    def ReloadMySkills(self):
        self.skillTimer = base.AutoTimer(1000, self.ShowMySkills)

    def ReloadMyStandings(self):
        wnd = self.GetWnd()
        if wnd is not None and not wnd.destroyed:
            selection = [ each for each in wnd.sr.nav.GetSelected() if each.key == 'mystandings' ]
            if selection:
                self.showing = None
                self.Load('mystandings')

    def ReloadMyRanks(self):
        wnd = self.GetWnd()
        if wnd is not None and not wnd.destroyed:
            wnd.sr.decoRankList = None
            selection = [ each for each in wnd.sr.nav.GetSelected() if each.key == 'mydecorations' ]
            if selection:
                self.showing = None
                self.Load('mydecorations')

    def ShowMySkillHistory(self):
        wnd = self.GetWnd()
        if not wnd:
            return

        def GetPts(lvl):
            return skillUtil.GetSPForLevelRaw(stc, lvl)

        wnd.sr.nav.DeselectAll()
        wnd.sr.scroll.sr.id = 'charsheet_skillhistory'
        wnd.sr.scroll.state = uiconst.UI_PICKCHILDREN
        rs = sm.GetService('skills').GetSkillHistory()
        scrolllist = []
        actions = {34: localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/SkillClonePenalty'),
         36: localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/SkillTrainingStarted'),
         37: localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/SkillTrainingComplete'),
         38: localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/SkillTrainingCanceled'),
         39: localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/GMGiveSkill'),
         53: localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/SkillTrainingComplete'),
         307: localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/SkillPointsApplied')}
        for r in rs:
            skill = sm.GetService('skills').HasSkill(r.skillTypeID)
            if skill:
                stc = skill.skillTimeConstant
                levels = [0,
                 GetPts(1),
                 GetPts(2),
                 GetPts(3),
                 GetPts(4),
                 GetPts(5)]
                level = 5
                spNext = levels[5]
                for i in range(len(levels)):
                    if levels[i] > r.absolutePoints:
                        level = i - 1
                        spNext = levels[i]
                        break

                data = util.KeyVal()
                data.label = util.FmtDate(r.logDate, 'ls') + '<t>'
                data.label += cfg.invtypes.Get(r.skillTypeID).name + '<t>'
                data.label += actions.get(r.eventTypeID, localization.GetByLabel('UI/Generic/Unknown')) + '<t>'
                data.label += localizationUtil.FormatNumeric(level)
                data.Set('sort_%s' % localization.GetByLabel('UI/Common/Date'), r.logDate)
                data.id = r.skillTypeID
                data.GetMenu = self.GetItemMenu
                data.MenuFunction = self.GetItemMenu
                data.OnDblClick = (self.DblClickShowInfo, data)
                addItem = listentry.Get('Generic', data=data)
                scrolllist.append(addItem)

        wnd.sr.scroll.Load(contentList=scrolllist, headers=[localization.GetByLabel('UI/Common/Date'),
         localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/Skill'),
         localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/Action'),
         localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/Level')], noContentHint=localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/NoRecordsFound'), reversesort=True)

    def GetItemMenu(self, entry, *args):
        return [(localization.GetByLabel('UI/Common/ShowInfo'), self.ShowInfo, (entry.sr.node.id, 1))]

    def DblClickShowInfo(self, otherSelf, nodeData):
        skillTypeID = getattr(nodeData, 'id', None)
        if skillTypeID is not None:
            self.ShowInfo(skillTypeID)

    def ShowInfo(self, *args):
        skillID = args[0]
        sm.StartService('info').ShowInfo(skillID, None)

    def GetCombatEntries(self, recent, isCorp = 0):
        primeInvTypes = {}
        primeEveOwners = {}
        primeEveLocations = {}
        headers = []
        ret = []
        unknownShipLabel = localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/KillsTabs/UnknownShip')
        unknownNameLabel = localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/KillsTabs/UnknownName')
        unknownCorporationLabel = localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/KillsTabs/UnknownCorporation')
        unknownAllianceLabel = localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/KillsTabs/UnknownAlliance')
        unknownFactionLabel = localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/KillsTabs/UnknownFaction')
        for kill in recent:
            primeEveLocations[kill.solarSystemID] = 1
            primeEveLocations[kill.moonID] = 1
            primeEveOwners[kill.victimCharacterID] = 1
            primeEveOwners[kill.victimCorporationID] = 1
            primeEveOwners[kill.victimAllianceID] = 1
            primeEveOwners[kill.victimFactionID] = 1
            primeInvTypes[kill.victimShipTypeID] = 1
            primeEveOwners[kill.finalCharacterID] = 1
            primeEveOwners[kill.finalCorporationID] = 1
            primeEveOwners[kill.finalAllianceID] = 1
            primeEveOwners[kill.finalFactionID] = 1
            primeInvTypes[kill.finalShipTypeID] = 1
            primeInvTypes[kill.finalWeaponTypeID] = 1
            if settings.user.ui.Get('charsheet_condensedcombatlog', 0) or isCorp:
                if not headers:
                    headers = [localization.GetByLabel('UI/Common/Date'),
                     localization.GetByLabel('UI/Common/Type'),
                     localization.GetByLabel('UI/Common/Name'),
                     localization.GetByLabel('UI/Common/Corporation'),
                     localization.GetByLabel('UI/Common/Alliance'),
                     localization.GetByLabel('UI/Common/Faction')]
                killShip = cfg.invtypes.GetIfExists(kill.victimShipTypeID)
                killChar = cfg.eveowners.GetIfExists(kill.victimCharacterID)
                killCorp = cfg.eveowners.GetIfExists(kill.victimCorporationID)
                killAlli = cfg.eveowners.GetIfExists(kill.victimAllianceID)
                killFact = cfg.eveowners.GetIfExists(kill.victimFactionID)
                data = util.KeyVal()
                timeOfKill = util.FmtDate(kill.killTime)
                shipOfCharacterKilled = getattr(killShip, 'name', False) or unknownShipLabel
                characterKilled = getattr(killChar, 'name', False) or unknownNameLabel
                corporationOfCharacterKilled = getattr(killCorp, 'name', False) or unknownCorporationLabel
                allianceOfCharacterKilled = getattr(killAlli, 'name', False) or unknownAllianceLabel
                factionOfCharacterKilled = getattr(killFact, 'name', False) or unknownFactionLabel
                data.label = timeOfKill + '<t>' + shipOfCharacterKilled + '<t>' + characterKilled + '<t>' + corporationOfCharacterKilled + '<t>' + allianceOfCharacterKilled + '<t>' + factionOfCharacterKilled
                data.GetMenu = self.GetCombatMenu
                data.OnDblClick = (self.GetCombatDblClick, data)
                data.kill = kill
                data.mail = kill
                ret.append(listentry.Get('KillMailCondensed', data=data))
            else:
                ret.append(listentry.Get('KillMail', {'mail': kill}))

        cfg.invtypes.Prime([ x for x in primeInvTypes.keys() if x is not None ])
        cfg.eveowners.Prime([ x for x in primeEveOwners.keys() if x is not None ])
        cfg.evelocations.Prime([ x for x in primeEveLocations.keys() if x is not None ])
        return (ret, headers)

    def GetCombatDblClick(self, entry, *args):
        kill = entry.sr.node.kill
        if kill is not None:
            wnd = form.KillReportWnd.GetIfOpen()
            if wnd:
                wnd.LoadInfo(killmail=kill)
                wnd.Maximize()
            else:
                form.KillReportWnd.Open(create=1, killmail=kill)

    def GetCombatMenu(self, entry, *args):
        m = [(uiutil.MenuLabel('UI/CharacterSheet/CharacterSheetWindow/KillsTabs/CopyKillInfo'), self.GetCombatText, (entry.sr.node.kill, 1))]
        return m

    def ShowKillsEx(self, recent, pagenum, func, combatType):
        if combatType == 'kills':
            prevType = self.prevKillIDs
        else:
            prevType = self.prevLossIDs
        wnd = self.GetWnd()
        if not wnd:
            return
        scrolllist, headers = self.GetCombatEntries(recent)
        for c in wnd.sr.btnContainer.children:
            c.state = uiconst.UI_HIDDEN

        wnd.sr.btnContainer.state = uiconst.UI_HIDDEN
        killIDs = [ k.killID for k in recent ]
        prevbtn = wnd.sr.btnContainer.children[1]
        nextbtn = wnd.sr.btnContainer.children[0]
        if pagenum > 0:
            wnd.sr.btnContainer.state = uiconst.UI_NORMAL
            prevbtn.state = uiconst.UI_NORMAL
            if combatType == 'kills':
                prevType = self.prevKillIDs[pagenum - 1]
            else:
                prevType = self.prevLossIDs[pagenum - 1]
            prevbtn.OnClick = (func, prevType, pagenum - 1)
        if len(recent) >= self.killentries:
            wnd.sr.btnContainer.state = uiconst.UI_NORMAL
            nextbtn.state = uiconst.UI_NORMAL
            nextbtn.OnClick = (func, min(killIDs), pagenum + 1)
            if combatType == 'kills':
                prevType = self.prevKillIDs.append(max(killIDs) + 1)
            else:
                prevType = self.prevLossIDs.append(max(killIDs) + 1)
        wnd.sr.scroll.state = uiconst.UI_PICKCHILDREN
        isCondensed = settings.user.ui.Get('charsheet_condensedcombatlog', 0)
        if isCondensed:
            wnd.sr.scroll.sr.id = 'charsheet_kills'
        else:
            wnd.sr.scroll.sr.id = 'charsheet_kills2'
        noContentHintText = ''
        if combatType == 'kills':
            noContentHintText = localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/KillsTabs/NoKillsFound')
        elif combatType == 'losses':
            noContentHintText = localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/KillsTabs/NoLossesFound')
        pos = wnd.sr.scroll.GetScrollProportion()
        wnd.sr.scroll.Load(contentList=scrolllist, headers=headers, scrollTo=pos, noContentHint=noContentHintText)

    def GetCombatText(self, kill, isCopy = 0):
        ret = util.CombatLog_CopyText(kill)
        if isCopy:
            blue.pyos.SetClipboardData(util.CleanKillMail(ret))
        else:
            return ret

    def OnCombatChange(self, *args):
        wnd = self.GetWnd()
        selected = wnd.sr.combatCombo.GetValue()
        selectedCombatType = settings.user.ui.Set('CombatLogCombo', selected)
        if selected == 0:
            self.ShowCombatKills()
        else:
            self.ShowCombatLosses()

    def ShowCombatKills(self, startFrom = None, *args):
        recent = sm.GetService('info').GetKillsRecentKills(self.killentries, startFrom)
        page = 0
        if len(args):
            page = args[0]
        self.ShowKillsEx(recent, page, self.ShowCombatKills, 'kills')

    def ShowCombatLosses(self, startFrom = None, *args):
        recent = sm.GetService('info').GetKillsRecentLosses(self.killentries, startFrom)
        page = 0
        if len(args):
            page = args[0]
        self.ShowKillsEx(recent, page, self.ShowCombatLosses, 'losses')

    def ShowKills(self):
        self.prevKillIDs = []
        self.prevLossIDs = []
        selectedCombatType = settings.user.ui.Get('CombatLogCombo', 0)
        if selectedCombatType == 0:
            self.ShowCombatKills()
        else:
            self.ShowCombatLosses()

    @telemetry.ZONE_METHOD
    def ShowSkills(self, key):
        if key == 'myskills_skills':
            self.ShowMySkills(force=True)
        elif key == 'myskills_skillhistory':
            self.ShowMySkillHistory()
        elif key == 'myskills_settings':
            self.ShowMySkillSettings()

    def ShowCertificates(self, key):
        wnd = self.GetWnd()
        if wnd is None:
            return
        wnd.sr.buttonParCert.state = uiconst.UI_HIDDEN
        if key == 'mycertificates_certificates':
            self.ShowMyCerts()
        elif key == 'mycertificates_permissions':
            wnd.sr.buttonParCert.state = uiconst.UI_NORMAL
            self.ShowMyCertificatePermissions()
        elif key == 'mycertificates_settings':
            self.ShowMyCertificateSettings()

    def ShowMyCerts(self):
        wnd = self.GetWnd()
        if not wnd:
            return
        if getattr(wnd.sr, 'certificatepanel', None):
            wnd.sr.certificatepanel.state = uiconst.UI_NORMAL
        wnd.sr.scroll.state = uiconst.UI_PICKCHILDREN
        self.SetHint()
        scrolllist = []
        self.myCerts = sm.StartService('certificates').GetMyCertificates()
        myCertsInfo = {}
        for certID in self.myCerts.iterkeys():
            cert = cfg.certificates.GetIfExists(certID)
            if cert is None:
                self.LogInfo('ShowMyCerts - Skipping certificate', certID, '- does not exist')
                continue
            myCertsInfo[certID] = cert

        categoryData = sm.RemoteSvc('certificateMgr').GetCertificateCategories()
        allCategories = sm.StartService('certificates').GetCategories(myCertsInfo)
        for category, value in allCategories.iteritems():
            categoryObj = categoryData[category]
            data = {'GetSubContent': self.GetCertSubContent,
             'label': localization.GetByMessageID(categoryObj.categoryNameID),
             'groupItems': value,
             'id': ('charsheetGroups_cat', category),
             'sublevel': 0,
             'showlen': 0,
             'showicon': 'hide',
             'cat': category,
             'state': 'locked'}
            scrolllist.append(listentry.Get('Group', data))

        scrolllist = localizationUtil.Sort(scrolllist, key=lambda x: x.label)
        wnd.sr.scroll.sr.id = 'charsheet_mycerts'
        contentHint = localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/CertTabs/NoCertificatesFound')
        wnd.sr.scroll.Load(contentList=scrolllist, noContentHint=contentHint)

    def GetCertSubContent(self, dataX, *args):
        scrolllist = []
        wnd = self.GetWnd()
        toggleGroups = settings.user.ui.Get('charsheet_toggleOneCertGroupAtATime', 1)
        if toggleGroups:
            dataWnd = uicls.Window.GetIfOpen(windowID=unicode(dataX.id))
            if not dataWnd:
                for entry in wnd.sr.scroll.GetNodes():
                    if entry.__guid__ != 'listentry.Group' or entry.id == dataX.id:
                        continue
                    if entry.open:
                        if entry.panel:
                            entry.panel.Toggle()
                        else:
                            uicore.registry.SetListGroupOpenState(entry.id, 0)
                            entry.scroll.PrepareSubContent(entry)

        entries = self.GetEntries(dataX)
        return entries

    def GetEntries(self, data, *args):
        scrolllist = []
        highestEntries = sm.StartService('certificates').GetHighestLevelOfClass(data.groupItems)
        for each in highestEntries:
            entry = self.CreateEntry(each)
            scrolllist.append(entry)

        return localizationUtil.Sort(scrolllist, key=lambda x: x.label)

    def CreateEntry(self, data, *args):
        scrolllist = []
        certID = data.certificateID
        label, grade, descr = sm.GetService('certificates').GetCertificateLabel(certID)
        cert = self.myCerts.get(certID)
        visibility = cert.visibilityFlags
        entry = {'line': 1,
         'label': label,
         'grade': data.grade,
         'certID': certID,
         'icon': 'ui_79_64_%s' % (data.grade + 1),
         'visibility': visibility}
        return listentry.Get('CertEntry', entry)

    @telemetry.ZONE_METHOD
    def ShowMySkills(self, force = False):
        if not force and self.showing != 'myskills_skills':
            return
        self.skillTimer = None
        wnd = self.GetWnd()
        if not wnd:
            return
        if getattr(wnd.sr, 'skillpanel', None):
            wnd.sr.skillpanel.state = uiconst.UI_NORMAL
        wnd.sr.scroll.state = uiconst.UI_PICKCHILDREN
        advancedView = settings.user.ui.Get('charsheet_showSkills', 'trained') in ('mytrainable', 'alltrainable')
        groups = sm.GetService('skills').GetSkillGroups(advancedView)
        scrolllist = []
        skillCount = sm.GetService('skills').GetSkillCount()
        skillPoints = sm.StartService('skills').GetFreeSkillPoints()
        if skillPoints > 0:
            text = '<color=0xFF00FF00>' + localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/UnAllocatedSkillPoints', skillPoints=skillPoints) + '</color>'
            hint = localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/ApplySkillHint')
            scrolllist.append(listentry.Get('Text', {'text': text,
             'hint': hint}))
        currentSkillPoints = 0
        for group, skills, untrained, intraining, inqueue, points in groups:
            currentSkillPoints += points

        skillText = localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/YouCurrentlyHaveSkills', numSkills=skillCount, currentSkillPoints=currentSkillPoints)
        scrolllist.append(listentry.Get('Text', {'text': skillText}))

        @telemetry.ZONE_METHOD
        def Published(skill):
            return cfg.invtypes.Get(skill.typeID).published

        for group, skills, untrained, intraining, inqueue, points in groups:
            untrained = filter(Published, untrained)
            if not len(skills) and not advancedView:
                continue
            tempList = []
            if advancedView and settings.user.ui.Get('charsheet_showSkills', 'trained') == 'mytrainable':
                for utrained in untrained[:]:
                    if self.MeetSkillRequirements(utrained.typeID):
                        tempList.append(utrained)

                combinedSkills = skills[:] + tempList[:]
                if not len(skills) and tempList == []:
                    continue
            if settings.user.ui.Get('charsheet_showSkills', 'trained') == 'alltrainable':
                combinedSkills = skills[:] + untrained[:]
            numInQueueLabel = ''
            label = None
            if len(inqueue):
                if len(intraining):
                    labelPath = 'UI/CharacterSheet/CharacterSheetWindow/SkillTabs/SkillsInQueueTraining'
                else:
                    labelPath = 'UI/CharacterSheet/CharacterSheetWindow/SkillTabs/SkillsInQueue'
                numInQueueLabel = localization.GetByLabel(labelPath, skillsInQueue=len(inqueue))
            if advancedView:
                label = localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/SkillGroupOverviewAdvanced', groupName=group.groupName, skills=len(skills), totalSkills=len(combinedSkills), points=points, skillsInQueue=numInQueueLabel)
            else:
                label = localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/SkillGroupOverviewSimple', groupName=group.groupName, skills=len(skills), points=points, skillsInQueue=numInQueueLabel)
                combinedSkills = skills[:]
            myFilter = wnd.quickFilter.GetValue()
            if len(myFilter):
                combinedSkills = uiutil.NiceFilter(wnd.quickFilter.QuickFilter, combinedSkills)
            if len(combinedSkills) == 0:
                continue
            data = {'GetSubContent': self.GetSubContent,
             'DragEnterCallback': self.OnGroupDragEnter,
             'DeleteCallback': self.OnGroupDeleted,
             'MenuFunction': self.GetMenu,
             'label': label,
             'groupItems': combinedSkills,
             'inqueue': inqueue,
             'id': ('myskills', group.groupID),
             'tabs': [],
             'state': 'locked',
             'showicon': 'hide',
             'showlen': 0}
            scrolllist.append(listentry.Get('Group', data))

        scrolllist.append(listentry.Get('Space', {'height': 64}))
        pos = wnd.sr.scroll.GetScrollProportion()
        wnd.sr.scroll.sr.id = 'charsheet_myskills'
        wnd.sr.scroll.Load(contentList=scrolllist, headers=[], scrollTo=pos)

    def MeetSkillRequirements(self, typeID):
        mine = sm.GetService('skills').MySkillLevelsByID()
        requiredSkills = sm.GetService('info').GetRequiredSkills(typeID)
        haveSkills = 1
        if requiredSkills:
            for skillID, level in requiredSkills:
                if skillID not in mine or mine[skillID] < level:
                    haveSkills = 0
                    break

        return haveSkills

    @telemetry.ZONE_METHOD
    def GetSubContent(self, data, *args):
        scrolllist = []
        wnd = self.GetWnd()
        if not wnd:
            return
        skillqueue = sm.GetService('skillqueue').GetServerQueue()
        skillsInQueue = data.inqueue
        toggleGroups = settings.user.ui.Get('charsheet_toggleOneSkillGroupAtATime', 1)
        if toggleGroups:
            dataWnd = uicls.Window.GetIfOpen(unicode(data.id))
            if not dataWnd:
                for entry in wnd.sr.scroll.GetNodes():
                    if entry.__guid__ != 'listentry.Group' or entry.id == data.id:
                        continue
                    if entry.open:
                        if entry.panel:
                            entry.panel.Toggle()
                        else:
                            uicore.registry.SetListGroupOpenState(entry.id, 0)
                            entry.scroll.PrepareSubContent(entry)

        skillsInGroup = localizationUtil.Sort(data.groupItems, key=lambda x: cfg.invtypes.Get(x.typeID).name)
        for skill in skillsInGroup:
            inQueue = None
            if skill.typeID in skillsInQueue:
                for i in xrange(5, skill.skillLevel, -1):
                    if (skill.typeID, i) in skillqueue:
                        inQueue = i
                        break

            inTraining = 0
            if hasattr(skill, 'flagID') and skill.flagID == const.flagSkillInTraining:
                inTraining = 1
            data = {}
            data['invtype'] = cfg.invtypes.Get(skill.typeID)
            data['skill'] = skill
            data['trained'] = skill.itemID != None
            data['plannedInQueue'] = inQueue
            data['skillID'] = skill.typeID
            data['inTraining'] = inTraining
            scrolllist.append(listentry.Get('SkillEntry', data))
            if inTraining:
                sm.StartService('godma').GetStateManager().GetEndOfTraining(skill.itemID)

        return scrolllist

    def OnGroupDeleted(self, ids):
        pass

    def OnGroupDragEnter(self, group, drag):
        pass

    def GetMenu(self, *args):
        return []

    def ShowStandings(self, positive):
        wnd = self.GetWnd()
        if not wnd:
            return
        self.SetHint()
        scrolllist = sm.GetService('standing').GetStandingEntries(positive, eve.session.charid)
        wnd.sr.scroll.sr.id = 'charsheet_standings'
        wnd.sr.scroll.Load(contentList=scrolllist)

    def UpdateMyAttributes(self, attributeID, value):
        wnd = self.GetWnd()
        if not wnd:
            return
        for entry in wnd.sr.scroll.GetNodes():
            if entry.attributeID == attributeID:
                entry.text = localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/Attributes/Points', skillPoints=value)
                if entry.panel:
                    entry.panel.sr.text.text = entry.text
                    entry.panel.hint = entry.text.replace('<t>', '  ')

    def ShowMyAttributes(self):
        wnd = self.GetWnd()
        if not wnd:
            return
        wnd.sr.scroll.state = uiconst.UI_PICKCHILDREN
        self.SetHint()
        scrollList = []
        sm.GetService('info').GetAttrItemInfo(eve.session.charid, const.typeCharacterAmarr, scrollList, [const.attributeIntelligence,
         const.attributePerception,
         const.attributeCharisma,
         const.attributeWillpower,
         const.attributeMemory])
        respecInfo = sm.GetService('skills').GetRespecInfo()
        self.respecEntry = listentry.Get('AttributeRespec', data=util.KeyVal(nextTimedRespec=respecInfo['nextTimedRespec'], freeRespecs=respecInfo['freeRespecs']))
        scrollList.append(self.respecEntry)
        wnd.sr.scroll.sr.id = 'charsheet_myattributes'
        wnd.sr.scroll.Load(fixedEntryHeight=32, contentList=scrollList, noContentHint=localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/Attributes/NoAttributesFound'))

    def ShowMySkillSettings(self):
        wnd = self.GetWnd()
        wnd.sr.scroll.state = uiconst.UI_PICKCHILDREN
        self.SetHint()
        scrolllist = []
        for cfgname, value, label, checked, group in [['charsheet_showSkills',
          'trained',
          localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/ShowOnlyCurrentSkills'),
          settings.user.ui.Get('charsheet_showSkills', 'trained') == 'trained',
          'trainable'],
         ['charsheet_showSkills',
          'mytrainable',
          localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/ShowOnlyTrainableSkills'),
          settings.user.ui.Get('charsheet_showSkills', 'trained') == 'mytrainable',
          'trainable'],
         ['charsheet_showSkills',
          'alltrainable',
          localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/ShowAllSkills'),
          settings.user.ui.Get('charsheet_showSkills', 'trained') == 'alltrainable',
          'trainable'],
         ['charsheet_hilitePartiallyTrainedSkills',
          None,
          localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/HighlightPartiallyTrainedSkills'),
          settings.user.ui.Get('charsheet_hilitePartiallyTrainedSkills', 0),
          None],
         ['charsheet_toggleOneSkillGroupAtATime',
          None,
          localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/ToggleOneSkillGroupAtATime'),
          settings.user.ui.Get('charsheet_toggleOneSkillGroupAtATime', 1),
          None]]:
            data = util.KeyVal()
            data.label = label
            data.checked = checked
            data.cfgname = cfgname
            data.retval = value
            data.group = group
            data.OnChange = self.CheckBoxChange
            scrolllist.append(listentry.Get('Checkbox', data=data))

        wnd.sr.scroll.sr.id = 'charsheet_skillsettings'
        wnd.sr.scroll.Load(contentList=scrolllist)

    def CheckBoxChange(self, checkbox):
        if checkbox.name == 'charsheet_condensedcombatlog':
            settings.user.ui.Set('charsheet_condensedcombatlog', checkbox.checked)
            self.ShowKills()
        elif checkbox.data.has_key('key'):
            key = checkbox.data['key']
            if key == 'charsheet_showSkills':
                if checkbox.data['retval'] is None:
                    settings.user.ui.Set(key, checkbox.checked)
                else:
                    settings.user.ui.Set(key, checkbox.data['retval'])
            else:
                settings.user.ui.Set(key, checkbox.checked)

    def ShowMyImplantsAndBoosters(self):
        wnd = self.GetWnd()
        if not wnd:
            return
        wnd.sr.scroll.state = uiconst.UI_PICKCHILDREN
        self.SetHint()
        mygodma = self.GetMyGodmaItem(eve.session.charid)
        if not mygodma:
            return
        implants = mygodma.implants
        boosters = mygodma.boosters
        godma = sm.GetService('godma')
        implants = uiutil.SortListOfTuples([ (getattr(godma.GetType(implant.typeID), 'implantness', None), implant) for implant in implants ])
        boosters = uiutil.SortListOfTuples([ (getattr(godma.GetType(booster.typeID), 'boosterness', None), booster) for booster in boosters ])
        scrolllist = []
        if implants:
            scrolllist.append(listentry.Get('Header', {'label': localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/Augmentations/Implants', implantCount=len(implants))}))
            for each in implants:
                scrolllist.append(listentry.Get('ImplantEntry', {'implant_booster': each,
                 'label': cfg.invtypes.Get(each.typeID).name}))

            if boosters:
                scrolllist.append(listentry.Get('Divider'))
        dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
        if boosters:
            scrolllist.append(listentry.Get('Header', {'label': localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/Augmentations/Boosters', boosterCount=len(boosters))}))
            for each in boosters:
                scrolllist.append(listentry.Get('ImplantEntry', {'implant_booster': each,
                 'label': cfg.invtypes.Get(each.typeID).name}))
                boosterEffect = self.GetMyGodmaItem(each.itemID)
                try:
                    effectIDs = dogmaLocation.GetDogmaItem(each.itemID).activeEffects
                except KeyError:
                    for effect in boosterEffect.effects.values():
                        if effect.isActive:
                            eff = cfg.dgmeffects.Get(effect.effectID)
                            scrolllist.append(listentry.Get('IconEntry', {'line': 1,
                             'hint': eff.displayName,
                             'text': None,
                             'label': eff.displayName,
                             'icon': util.IconFile(eff.iconID),
                             'selectable': 0,
                             'iconoffset': 32,
                             'iconsize': 22,
                             'linecolor': (1.0, 1.0, 1.0, 0.125)}))

                else:
                    for effectID in effectIDs:
                        eff = cfg.dgmeffects.Get(effectID)
                        if eff.fittingUsageChanceAttributeID is None:
                            continue
                        scrolllist.append(listentry.Get('IconEntry', {'line': 1,
                         'hint': eff.displayName,
                         'text': None,
                         'label': eff.displayName,
                         'icon': util.IconFile(eff.iconID),
                         'selectable': 0,
                         'iconoffset': 32,
                         'iconsize': 22,
                         'linecolor': (1.0, 1.0, 1.0, 0.125)}))

                scrolllist.append(listentry.Get('Divider'))

        wnd.sr.scroll.sr.id = 'charsheet_implantandboosters'
        wnd.sr.scroll.Load(fixedEntryHeight=32, contentList=scrolllist, noContentHint=localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/Augmentations/NoImplantOrBoosterInEffect'))

    def GetMyGodmaItem(self, itemID):
        ret = sm.GetService('godma').GetItem(itemID)
        while ret is None and not getattr(getattr(self, 'wnd', None), 'destroyed', 1):
            self.LogWarn('godma item not ready yet. sleeping for it...')
            blue.pyos.synchro.SleepWallclock(500)
            ret = sm.GetService('godma').GetItem(itemID)

        return ret

    def GetBoosterSubContent(self, nodedata):
        scrolllist = []
        for each in nodedata.groupItems:
            entry = listentry.Get('LabelTextTop', {'line': 1,
             'label': each[0],
             'text': each[1],
             'iconID': each[2]})
            scrolllist.append(entry)

        return localizationUtil.Sort(scrolllist, key=lambda x: x.label)

    def GoTo(self, URL, data = None, args = {}, scrollTo = None):
        URL = URL.encode('cp1252', 'replace')
        if URL.startswith('showinfo:') or URL.startswith('evemail:') or URL.startswith('evemailto:'):
            self.output.GoTo(self, URL, data, args)
        else:
            uicore.cmd.OpenBrowser(URL, data=data, args=args)

    def ShowMyDecorationPermissions(self):
        scrollHeaders = [localization.GetByLabel('UI/CharacterCreation/FirstName'),
         localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/DecoTabs/Private'),
         localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/DecoTabs/Public'),
         localization.GetByLabel('UI/PI/Common/Remove')]
        wnd = self.GetWnd()
        if not wnd:
            return
        wnd.sr.scroll.sr.fixedColumns = {localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/DecoTabs/Private'): 60,
         localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/DecoTabs/Public'): 60}
        wnd.sr.scroll.sr.id = 'charsheet_decopermissions'
        wnd.sr.scroll.Load(contentList=[], headers=scrollHeaders)
        wnd.sr.scroll.OnColumnChanged = self.OnDecorationPermissionsColumnChanged
        publicDeco = sm.StartService('medals').GetMedalsReceivedWithFlag(session.charid, [3])
        privateDeco = sm.StartService('medals').GetMedalsReceivedWithFlag(session.charid, [2])
        ppKeys = [ each for each in publicDeco.keys() + privateDeco.keys() ]
        scrolllist = []
        inMedalList = []
        characterMedals, characterMedalInfo = sm.StartService('medals').GetMedalsReceived(session.charid)
        for characterMedal in characterMedals:
            medalID = characterMedal.medalID
            if medalID not in ppKeys:
                continue
            if medalID in inMedalList:
                continue
            inMedalList.append(medalID)
            details = characterMedalInfo.Filter('medalID')
            if details and details.has_key(medalID):
                details = details.get(medalID)
            entry = self.CreateDecorationPermissionsEntry(characterMedal)
            if entry:
                scrolllist.append(entry)

        wnd.sr.scroll.Load(contentList=scrolllist, headers=scrollHeaders, noContentHint=localization.GetByLabel('UI/Common/NothingFound'))
        self.OnDecorationPermissionsColumnChanged()

    def ShowMyCertificatePermissions(self):
        scrollHeaders = [localization.GetByLabel('UI/CharacterCreation/FirstName'), localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/DecoTabs/Private'), localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/DecoTabs/Public')]
        certsvc = sm.StartService('certificates')
        wnd = self.GetWnd()
        if not wnd:
            return
        wnd.sr.scroll.sr.fixedColumns = {localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/DecoTabs/Private'): 60,
         localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/DecoTabs/Public'): 60}
        wnd.sr.scroll.sr.id = 'charsheet_certpermissions'
        wnd.sr.scroll.Load(contentList=[], headers=scrollHeaders)
        wnd.sr.scroll.OnColumnChanged = self.OnCertificatePermissionsColumnChanged
        myCertIDs = certsvc.GetMyCertificates()
        myCerts = {}
        for certID in myCertIDs:
            cert = cfg.certificates.GetIfExists(certID)
            if cert is None:
                self.LogInfo('Certificate Permissions - Skipping certificate', certID, '- does not exist')
                continue
            myCerts[certID] = cert

        categoryData = sm.RemoteSvc('certificateMgr').GetCertificateCategories()
        myCategories = certsvc.GetCategories(myCerts)
        scrolllist = []
        for category, value in myCategories.iteritems():
            value = certsvc.GetHighestLevelOfClass(value)
            categoryObj = categoryData[category]
            data = {'GetSubContent': self.GetCertificatePermissionsEntries,
             'label': localization.GetByMessageID(categoryObj.categoryNameID),
             'groupItems': value,
             'id': ('certGroups_cat', category),
             'sublevel': 0,
             'showlen': 0,
             'showicon': 'hide',
             'cat': category,
             'state': 'locked',
             'BlockOpenWindow': 1}
            scrolllist.append(listentry.Get('Group', data))

        scrolllist = localizationUtil.Sort(scrolllist, key=lambda x: x.label)
        wnd.sr.scroll.Load(contentList=scrolllist, headers=scrollHeaders, noContentHint=localization.GetByLabel('UI/Common/NothingFound'))
        self.OnCertificatePermissionsColumnChanged()

    def GetCertificatePermissionsEntries(self, data, *args):
        wnd = self.GetWnd()
        if wnd is None:
            return
        toggleGroups = settings.user.ui.Get('charsheet_toggleOneCertPermsGroupAtATime', 1)
        if toggleGroups:
            dataWnd = uicls.Window.GetIfOpen(unicode(data.id))
            if not dataWnd:
                for entry in wnd.sr.scroll.GetNodes():
                    if entry.__guid__ != 'listentry.Group' or entry.id == data.id:
                        continue
                    if entry.open:
                        if entry.panel:
                            entry.panel.Toggle()
                        else:
                            uicore.registry.SetListGroupOpenState(entry.id, 0)
                            entry.scroll.PrepareSubContent(entry)

        scrolllist = []
        for each in data.groupItems:
            entry = self.CreateCertificatePermissionsEntry(each)
            scrolllist.append(entry)

        return localizationUtil.Sort(scrolllist, key=lambda x: x.label)

    def CreateCertificatePermissionsEntry(self, data):
        certID = data.certificateID
        myCerts = sm.StartService('certificates').GetMyCertificates()
        certObj = myCerts.get(certID)
        visibilityFlags = 0
        if certObj is not None:
            visibilityFlags = certObj.visibilityFlags
        tempFlag = self.visibilityChanged.get(certID, None)
        func = sm.StartService('charactersheet').OnCertVisibilityChange
        label, grade, descr = sm.GetService('certificates').GetCertificateLabel(certID)
        entry = {'line': 1,
         'label': localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/CertTabs/CertificatePermission', certificationLabel=label, grade=grade) + '<t><t>',
         'itemID': certID,
         'visibilityFlags': visibilityFlags,
         'tempFlag': tempFlag,
         'indent': 3,
         'selectable': 0,
         'func': func}
        return listentry.Get('CertificatePermissions', entry)

    def CreateDecorationPermissionsEntry(self, data):
        entry = {'line': 1,
         'label': data.title + '<t><t><t>',
         'itemID': data.medalID,
         'visibilityFlags': data.status,
         'indent': 3,
         'selectable': 0}
        return listentry.Get('DecorationPermissions', entry)

    def OnCertificatePermissionsColumnChanged(self, *args, **kwargs):
        wnd = self.GetWnd()
        if not wnd:
            return
        for entry in wnd.sr.scroll.GetNodes():
            if entry.panel and getattr(entry.panel, 'OnColumnChanged', None):
                entry.panel.OnColumnChanged()

    def OnDecorationPermissionsColumnChanged(self, *args, **kwargs):
        wnd = self.GetWnd()
        if not wnd:
            return
        for entry in wnd.sr.scroll.GetNodes():
            if entry.panel and getattr(entry.panel, 'OnColumnChanged', None):
                entry.panel.OnColumnChanged()

    def SaveDecorationPermissionsChanges(self):
        wnd = self.GetWnd()
        if not wnd:
            return
        promptForDelete = False
        changes = {}
        for entry in wnd.sr.scroll.GetNodes():
            if entry.panel and hasattr(entry.panel, 'flag'):
                if entry.panel.HasChanged():
                    if entry.panel.flag == 1:
                        promptForDelete = True
                    changes[entry.panel.sr.node.itemID] = entry.panel.flag

        if promptForDelete == False or eve.Message('DeleteMedalConfirmation', {}, uiconst.YESNO) == uiconst.ID_YES:
            if len(changes) > 0:
                sm.StartService('medals').SetMedalStatus(changes)
        wnd.sr.decoMedalList = None

    def SetAllDecorationPermissions(self):
        wnd = self.GetWnd()
        if not wnd:
            return
        permissionList = [(localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/DecoTabs/Private'), 2), (localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/DecoTabs/Public'), 3)]
        pickedPermission = uix.ListWnd(permissionList, 'generic', localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/DecoTabs/SetAllDecorationPermissions'), localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/PilotLicense/SaveAllChangesImmediately'), windowName='permissionPickerWnd')
        if not pickedPermission:
            return
        permissionID = pickedPermission[1]
        m, i = sm.StartService('medals').GetMedalsReceived(session.charid)
        myDecos = []
        for each in m:
            if each.status != 1:
                myDecos.append(each.medalID)

        myDecos = list(set(myDecos))
        updateDict = {}
        for decoID in myDecos:
            updateDict[decoID] = permissionID

        if len(updateDict) > 0:
            sm.StartService('medals').SetMedalStatus(updateDict)
            wnd.sr.decoMedalList = None
            self.ShowMyDecorations('mydecorations_permissions')

    def SaveCertificatePermissionsChanges(self):
        wnd = self.GetWnd()
        if not wnd:
            return
        if len(self.visibilityChanged) > 0:
            sm.StartService('certificates').ChangeVisibilityFlag(self.visibilityChanged)
        self.visibilityChanged = {}

    def ShowMyCertificateSettings(self):
        wnd = self.GetWnd()
        wnd.sr.scroll.state = uiconst.UI_PICKCHILDREN
        self.SetHint()
        scrolllist = []
        for cfgname, value, label, checked, group in [['charsheet_toggleOneCertGroupAtATime',
          None,
          localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/CertTabs/ToggleOneCertificationGroupAtATime'),
          settings.user.ui.Get('charsheet_toggleOneCertGroupAtATime', 1),
          None], ['charsheet_toggleOneCertPermsGroupAtATime',
          None,
          localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/CertTabs/ToggleOnePermissionGroupAtATime'),
          settings.user.ui.Get('charsheet_toggleOneCertPermsGroupAtATime', 1),
          None]]:
            data = util.KeyVal()
            data.label = label
            data.checked = checked
            data.cfgname = cfgname
            data.retval = value
            data.group = group
            data.OnChange = self.CheckBoxChange
            scrolllist.append(listentry.Get('Checkbox', data=data))

        wnd.sr.scroll.sr.id = 'charsheet_certsettings'
        wnd.sr.scroll.Load(contentList=scrolllist)

    def SetAllCertificatePermissions(self):
        permissionList = [(localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/DecoTabs/Private'), 0), (localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/DecoTabs/Public'), 1)]
        pickedPermission = uix.ListWnd(permissionList, 'generic', localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/DecoTabs/SetAllDecorationPermissions'), localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/PilotLicense/SaveAllChangesImmediately'), windowName='permissionPickerWnd')
        if not pickedPermission:
            return
        permissionID = pickedPermission[1]
        certsvc = sm.StartService('certificates')
        myCerts = certsvc.GetMyCertificates()
        updateDict = {}
        for certID in myCerts.iterkeys():
            updateDict[certID] = permissionID

        if len(updateDict) > 0:
            certsvc.ChangeVisibilityFlag(updateDict)
            self.ShowCertificates('mycertificates_permissions')
            self.visibilityChanged = {}

    def GetPlexUrl(self):
        if boot.region == 'optic':
            return 'http://eve.tiancity.com/client/evemall.html'
        else:
            return 'https://secure.eveonline.com/PLEX.aspx'


class CharacterSheetWindow(uicls.Window):
    __guid__ = 'form.CharacterSheet'
    default_width = 497
    default_height = 456
    default_minSize = (497, 456)
    default_left = 0
    default_top = 32
    default_windowID = 'charactersheet'

    def OnUIRefresh(self):
        pass

    @telemetry.ZONE_METHOD
    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        self.characterSheetSvc = sm.GetService('charactersheet')
        self.sr.standingsinited = 0
        self.sr.skillsinited = 0
        self.sr.killsinited = 0
        self.sr.mydecorationsinited = 0
        self.sr.certsinited = 0
        self.sr.pilotlicenceinited = 0
        self.SetScope('station_inflight')
        self.SetCaption(localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/CharacterSheetCaption'))
        self.IsBrowser = 1
        self.GoTo = self.characterSheetSvc.GoTo
        self.SetWndIcon('ui_2_64_16')
        self.HideMainIcon()
        leftSide = uicls.Container(name='leftSide', parent=self.sr.main, align=uiconst.TOLEFT, left=const.defaultPadding, width=settings.user.ui.Get('charsheetleftwidth', 200), idx=0)
        self.sr.leftSide = leftSide
        self.sr.nav = uicls.Scroll(name='senderlist', parent=leftSide, padTop=const.defaultPadding, padBottom=const.defaultPadding)
        self.sr.nav.OnSelectionChange = self.characterSheetSvc.OnSelectEntry
        mainArea = uicls.Container(name='mainArea', parent=self.sr.main, align=uiconst.TOALL)
        self.sr.buttonParCert = uicls.Container(name='buttonParCert', align=uiconst.TOBOTTOM, height=25, parent=mainArea, state=uiconst.UI_HIDDEN)
        self.sr.buttonParDeco = uicls.Container(name='buttonParDeco', align=uiconst.TOBOTTOM, height=25, parent=mainArea, state=uiconst.UI_HIDDEN)
        buttonCert = uicls.Container(name='buttonCert', align=uiconst.TOBOTTOM, height=15, parent=self.sr.buttonParCert, padBottom=5)
        buttonDeco = uicls.Container(name='buttonDeco', align=uiconst.TOBOTTOM, height=15, parent=self.sr.buttonParDeco, padBottom=5)
        mainArea2 = uicls.Container(name='mainArea2', parent=mainArea, align=uiconst.TOALL)
        divider = xtriui.Divider(name='divider', align=uiconst.TOLEFT, width=const.defaultPadding - 1, parent=mainArea2, state=uiconst.UI_NORMAL)
        divider.Startup(leftSide, 'width', 'x', 84, 220)
        self.sr.divider = divider
        uicls.Container(name='push', parent=mainArea2, state=uiconst.UI_PICKCHILDREN, width=const.defaultPadding, align=uiconst.TORIGHT)
        self.sr.skillpanel = uicls.Container(name='skillpanel', parent=mainArea2, align=uiconst.TOTOP, state=uiconst.UI_HIDDEN, padTop=2)
        self.sr.certificatepanel = uicls.Container(name='certificatepanel', parent=mainArea2, align=uiconst.TOTOP, state=uiconst.UI_HIDDEN, padTop=2)
        self.sr.combatlogpanel = uicls.Container(name='combatlogpanel', parent=mainArea2, align=uiconst.TOTOP, state=uiconst.UI_HIDDEN, padTop=const.defaultPadding)
        combatValues = ((localization.GetByLabel('UI/Corporations/Wars/Killmails/ShowKills'), 0), (localization.GetByLabel('UI/Corporations/Wars/Killmails/ShowLosses'), 1))
        selectedCombatType = settings.user.ui.Get('CombatLogCombo', 0)
        self.sr.combatCombo = uicls.Combo(parent=self.sr.combatlogpanel, name='combo', select=selectedCombatType, align=uiconst.TOPLEFT, callback=self.characterSheetSvc.OnCombatChange, options=combatValues, idx=0, adjustWidth=True)
        self.sr.combatSetting = uicls.Checkbox(parent=self.sr.combatlogpanel, align=uiconst.TOPLEFT, left=self.sr.combatCombo.width + 4, top=const.defaultPadding, height=14, width=300, configName='charsheet_condensedcombatlog', text=localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/KillsTabs/CondensedCombatLog'), checked=settings.user.ui.Get('charsheet_condensedcombatlog', 0), callback=self.characterSheetSvc.CheckBoxChange)
        self.sr.combatlogpanel.height = max(self.sr.combatCombo.height, self.sr.combatSetting.height)
        btn = uicls.Button(parent=self.sr.certificatepanel, label=localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/CertTabs/OpenCertificatePlanner'), func=self.characterSheetSvc.OpenCertificateWindow, alwaysLite=True, align=uiconst.CENTERRIGHT)
        self.quickFilter = uicls.QuickFilterEdit(parent=self.sr.skillpanel, align=uiconst.CENTERLEFT, width=70)
        self.quickFilter.ReloadFunction = self.characterSheetSvc.ReloadMySkills
        btn = uicls.Button(parent=self.sr.skillpanel, label=localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/OpenTrainingQueue'), func=self.characterSheetSvc.OpenSkillQueueWindow, alwaysLite=True, align=uiconst.CENTERRIGHT, name='characterSheetOpenTrainingQueue')
        self.sr.skillpanel.height = max(self.quickFilter.height, btn.height)
        self.sr.certificatepanel.height = btn.height
        btns = [(localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/DecoTabs/SaveDecorationPermissionChanges'),
          self.characterSheetSvc.SaveDecorationPermissionsChanges,
          (),
          64), (localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/DecoTabs/SetAllDecorationPermissions'),
          self.characterSheetSvc.SetAllDecorationPermissions,
          (),
          64)]
        uicls.ButtonGroup(btns=btns, parent=buttonDeco)
        btns = [(localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/CertTabs/SaveCertificatePermissionChanges'),
          self.characterSheetSvc.SaveCertificatePermissionsChanges,
          (),
          64), (localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/CertTabs/SetAllCertificatePermissions'),
          self.characterSheetSvc.SetAllCertificatePermissions,
          (),
          64)]
        uicls.ButtonGroup(btns=btns, parent=buttonCert)
        self.sr.scroll = uicls.Scroll(parent=mainArea2, padding=(0,
         const.defaultPadding,
         0,
         const.defaultPadding))
        self.sr.scroll.sr.id = 'charactersheetscroll'
        self.sr.hint = None
        self.sr.employmentList = None
        self.sr.decoRankList = None
        self.sr.decoMedalList = None
        self.sr.mainArea = mainArea
        self.sr.bioparent = uicls.Container(name='bio', parent=mainArea2, state=uiconst.UI_HIDDEN, padding=(0,
         const.defaultPadding,
         0,
         const.defaultPadding))
        self.characterSheetSvc.LoadGeneralInfo()
        navEntries = self.characterSheetSvc.GetNavEntries(self)
        scrolllist = []
        for label, panel, icon, key, order, UIName in navEntries:
            data = util.KeyVal()
            data.text = label
            data.label = label
            data.icon = icon
            data.key = key
            data.hint = label
            data.name = UIName
            scrolllist.append(listentry.Get('IconEntry', data=data))

        self.sr.nav.Load(contentList=scrolllist)
        self.sr.nav.SetSelected(min(len(navEntries) - 1, settings.char.ui.Get('charactersheetselection', 0)))
        self.characterSheetSvc.visibilityChanged = {}
        self._CheckShowT3ShipLossMessage()

    @telemetry.ZONE_METHOD
    def _CheckShowT3ShipLossMessage(self):
        recentT3ShipLoss = settings.char.generic.Get('skillLossNotification', None)
        if recentT3ShipLoss is not None:
            eve.Message('RecentSkillLossDueToT3Ship', {'skillTypeID': (TYPEID, recentT3ShipLoss.skillTypeID),
             'skillPoints': recentT3ShipLoss.skillPoints,
             'shipTypeID': (TYPEID, recentT3ShipLoss.shipTypeID)})
            settings.char.generic.Set('skillLossNotification', None)

    def Close(self, *args, **kwds):
        sm.GetService('charactersheet').OnCloseWnd(self)
        uicls.Window.Close(self, *args, **kwds)


class PilotLicence(uicls.SE_BaseClassCore):
    __guid__ = 'listentry.PilotLicence'
    __params__ = ['daysLeft', 'buyPlexOnMarket', 'buyPlexOnline']
    BUTTON_HEIGHT = 40

    def Load(self, node):
        if node.loaded:
            return
        self.Setup(node.daysLeft, node.buyPlexOnMarket, node.buyPlexOnline)

    def Setup(self, daysLeft, buyPlexOnMarket, buyPlexOnline):
        if daysLeft:
            text = localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/PilotLicense/DaysLeft', daysLeft=daysLeft)
            r, g, b = (1.0, 0.0, 0.0)
        else:
            r, g, b = (1.0, 1.0, 1.0)
            text = localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/PilotLicense/Fine')
        statebox = uicls.Container(name='statebox', align=uiconst.TOTOP, parent=self, state=uiconst.UI_DISABLED, padding=(10, 10, 5, 0))
        uicls.Fill(parent=statebox, color=(r,
         g,
         b,
         0.07))
        uicls.Frame(parent=statebox, state=uiconst.UI_DISABLED, color=(r,
         g,
         b,
         0.4), idx=1)
        stateTextCtr = uicls.Container(name='statectr', align=uiconst.CENTERTOP, parent=statebox, state=uiconst.UI_DISABLED, width=280, padding=(10, 0, 10, 0))
        uicls.Icon(align=uiconst.TOPLEFT, parent=stateTextCtr, icon='ui_57_64_3', pos=(0, 0, 55, 55), ignoreSize=True, idx=0)
        self.licenseStateLabel = uicls.EveLabelMedium(name='licensestate', align=uiconst.TOALL, text=text, parent=stateTextCtr, state=uiconst.UI_DISABLED, padding=(65, 10, 0, 0))
        self.plexdesctext = uicls.EveLabelMedium(name='plexdesc', text=localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/PilotLicense/About'), parent=self, padding=(12, 10, 0, 0), align=uiconst.TOTOP, state=uiconst.UI_NORMAL)
        statebox.height = stateTextCtr.height = self.licenseStateLabel.textheight + 20
        buttonbox = uicls.Container(name='buttonbox', align=uiconst.TOALL, parent=self, padding=(10, 15, 0, 0))
        btn = uix.GetBigButton(50, buttonbox, width=180, height=PilotLicence.BUTTON_HEIGHT)
        btn.SetSmallCaption(localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/PilotLicense/BuyOnEveMarket'), inside=1)
        btn.OnClick = buyPlexOnMarket
        btn.SetAlign(uiconst.CENTERTOP)
        btn = uix.GetBigButton(50, buttonbox, top=PilotLicence.BUTTON_HEIGHT + 15, width=180, height=PilotLicence.BUTTON_HEIGHT)
        btn.SetSmallCaption(localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/PilotLicense/BuyOnline'), inside=1)
        btn.SetAlign(uiconst.CENTERTOP)
        btn.OnClick = buyPlexOnline
        self.sr.node.loaded = True

    def GetDynamicHeight(node, width):
        plexTextHeight = sm.GetService('font').GetTextHeight(localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/PilotLicense/About'), width=width - 10)
        padding = 50
        buttons = 2 * (PilotLicence.BUTTON_HEIGHT + 15)
        return plexTextHeight + buttons + padding + 60


class CloneButtons(uicls.SE_BaseClassCore):
    __guid__ = 'listentry.CloneButtons'

    def Startup(self, args):
        uicls.Line(parent=self, align=uiconst.TOBOTTOM)
        self.sr.JumpBtn = uicls.Button(parent=self, label=localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/JumpCloneScroll/Jump'), align=uiconst.CENTER, func=self.OnClickJump)
        destroyLabel = localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/JumpCloneScroll/Destroy')
        self.sr.DecomissionBtn = uicls.Button(parent=self, label=destroyLabel, align=uiconst.CENTER, func=self.OnClickDecomission)

    def Load(self, node):
        self.sr.node = node
        self.locationID = node.locationID
        self.jumpCloneID = node.jumpCloneID
        self.sr.JumpBtn.width = self.sr.DecomissionBtn.width = max(self.sr.JumpBtn.width, self.sr.DecomissionBtn.width)
        self.sr.JumpBtn.left = -self.sr.JumpBtn.width / 2
        self.sr.DecomissionBtn.left = self.sr.DecomissionBtn.width / 2
        self.sr.JumpBtn.Disable()
        self.sr.DecomissionBtn.Disable()
        validLocation = self.locationID in cfg.evelocations
        if validLocation:
            self.sr.DecomissionBtn.Enable()
            if session.stationid:
                self.sr.JumpBtn.Enable()

    def GetHeight(self, *args):
        node, width = args
        node.height = 32
        return node.height

    def OnClickJump(self, *args):
        sm.GetService('clonejump').CloneJump(self.locationID)

    def OnClickDecomission(self, *args):
        sm.GetService('clonejump').DestroyInstalledClone(self.jumpCloneID)


class CombatDetailsWnd(uicls.Window):
    __guid__ = 'form.CombatDetailsWnd'
    default_windowID = 'CombatDetails'

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        self.SetCaption(localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/KillsTabs'))
        self.HideMainIcon()
        self.SetTopparentHeight(0)
        ret = attributes.ret
        uicls.ButtonGroup(btns=[[localization.GetByLabel('UI/Common/Buttons/Close'),
          self.CloseByUser,
          None,
          81]], parent=self.sr.main)
        self.edit = uicls.Edit(parent=self.sr.main, align=uiconst.TOALL, readonly=True)
        self.UpdateDetails(ret)

    def UpdateDetails(self, ret = ''):
        self.edit.SetValue(ret)