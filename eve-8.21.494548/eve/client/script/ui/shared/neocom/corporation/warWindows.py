#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/ui/shared/neocom/corporation/warWindows.py
import localization
import uiutil
import util
import uiconst
import uicls
import blue
import listentry
import form
import moniker
import warUtil
from collections import defaultdict
from service import ROLE_GMH

class NegotiationWnd(uicls.Window):
    __guid__ = 'form.NegotiationWnd'
    __notifyevents__ = []
    default_windowID = 'NegotiationWnd'
    default_width = 450
    default_height = 282
    default_minSize = (default_width, default_height)

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        self.war = war = attributes.war
        self.isRequest = attributes.Get('isRequest', False)
        self.isAllyRequest = attributes.Get('isAllyRequest', False)
        if self.isRequest:
            self.warID = war.warID
            self.attackerID = war.declaredByID
            self.defenderID = war.againstID
            self.requesterID = attributes.Get('requesterID', None)
        else:
            self.warNegotiation = sm.GetService('war').GetWarNegotiation(attributes.warNegotiationID)
            self.warID = self.warNegotiation.warID
            self.attackerID = self.warNegotiation.declaredByID
            self.defenderID = self.warNegotiation.againstID
            self.requesterID = self.warNegotiation.ownerID1
        self.SetTopparentHeight(0)
        self.HideClippedIcon()
        self.ConstructLayout()
        self.LoadNegotiation()

    def ConstructLayout(self):
        mainCont = uicls.Container(parent=self.sr.main, align=uiconst.TOALL, padding=const.defaultPadding)
        headerCont = uicls.Container(parent=mainCont, align=uiconst.TOTOP, height=45)
        self.warCont = uicls.Container(parent=mainCont, align=uiconst.TOTOP, height=40, padTop=6)
        self.requesterLabel = uicls.EveLabelMedium(text='', parent=self.warCont, padLeft=38, state=uiconst.UI_NORMAL, align=uiconst.TOTOP, top=2)
        self.offerLabel = uicls.EveLabelMedium(text='', parent=self.warCont, padLeft=38, align=uiconst.TOTOP)
        self.negotiationIcon = uicls.Icon(parent=headerCont, align=uiconst.TOPLEFT, pos=(0, 4, 32, 32), ignoreSize=True)
        self.windowTitle = uicls.EveCaptionSmall(text='', parent=headerCont, align=uiconst.TOTOP, padLeft=38)
        self.warLabel = uicls.EveLabelMedium(text='', parent=headerCont, align=uiconst.TOTOP, padLeft=38, state=uiconst.UI_NORMAL)
        self.btnGroup = uicls.ButtonGroup(parent=mainCont, btns=[], height=20)
        self.myCont = uicls.Container(parent=mainCont, align=uiconst.TOALL)
        self.offerAmount = uicls.SinglelineEdit(setvalue=self.GetBaseIskValue(), parent=self.myCont, align=uiconst.TOBOTTOM, floats=[0, 100000000000L, 0], hinttext=localization.GetByLabel('UI/Corporations/Wars/OfferInISK'))
        self.requestText = uicls.EditPlainText(setvalue='', parent=self.myCont, align=uiconst.TOALL, padBottom=4, hintText=localization.GetByLabel('UI/Corporations/Wars/Reasonforoffer'), maxLength=400)
        self.SetCaption(self.GetWndCaption())

    def LoadNegotiation(self):
        attackerName, attackerInfo = self.GetEntityInfo(self.attackerID)
        defenderName, defenderInfo = self.GetEntityInfo(self.defenderID)
        self.windowTitle.text = self.GetText()
        self.warLabel.text = localization.GetByLabel('UI/Corporations/Wars/InWarAvsB', attackerName=attackerName, attackerInfo=attackerInfo, defenderName=defenderName, defenderInfo=defenderInfo)
        offererLogo = uiutil.GetLogoIcon(itemID=self.requesterID, parent=self.warCont, acceptNone=False, align=uiconst.TOPLEFT, size=32, state=uiconst.UI_NORMAL, left=2, top=2)
        self.requesterLabel.text = self.GetRequesterText()
        if self.isRequest:
            self.requesterLabel.top = 8
            self.offerLabel.display = False
            self.btnGroup.AddButton((localization.GetByLabel('UI/Common/Buttons/Submit'),
             self.SubmitRequest,
             (),
             84,
             0,
             1,
             0))
            self.btnGroup.AddButton((localization.GetByLabel('UI/Common/Buttons/Cancel'),
             self.CloseByUser,
             (),
             84,
             0,
             0,
             0))
        else:
            offerDescription = self.warNegotiation.description
            self.requestText.SetValue(offerDescription)
            self.offerLabel.text = self.GetOfferText()
            self.offerAmount.display = False
            self.requestText.readonly = True
            entityID = session.allianceid or session.corpid
            if entityID == self.warNegotiation.ownerID1:
                self.btnGroup.AddButton((localization.GetByLabel('UI/Common/Buttons/Close'),
                 self.CloseByUser,
                 (),
                 84,
                 0,
                 1,
                 0))
            else:
                self.btnGroup.AddButton((localization.GetByLabel('UI/Corporations/Wars/AcceptOffer'),
                 self.AcceptOffer,
                 (),
                 84,
                 0,
                 1,
                 0))
                self.btnGroup.AddButton((localization.GetByLabel('UI/Corporations/Wars/DeclineOffer'),
                 self.DeclineOffer,
                 (),
                 84,
                 0,
                 0,
                 0))
        iconPath, iconID = self.GetWndIconAndPath()
        self.SetWndIcon(iconID)
        self.negotiationIcon.LoadIcon(iconPath)
        self.ShowButtons()

    def IsDefender(self):
        myID = session.corpid if session.allianceid is None else session.allianceid
        if self.defenderID == myID:
            return True
        return False

    def GetEntityInfo(self, entityID):
        entityName = cfg.eveowners.Get(entityID).name
        if util.IsCorporation(entityID):
            entityLinkType = const.typeCorporation
        else:
            entityLinkType = const.typeAlliance
        return (entityName, ('showinfo', entityLinkType, entityID))

    def GetWndIconAndPath(self):
        return ('res:/UI/Texture/Icons/Mercenary_64.png', 'ui_1337_64_4')

    def GetOfferAmountText(self):
        return localization.GetByLabel('UI/Corporations/Wars/MercenaryFee')

    def GetText(self):
        if self.isRequest:
            return localization.GetByLabel('UI/Corporations/Wars/OfferAssistance')
        else:
            return localization.GetByLabel('UI/Corporations/Wars/AllyOffer')

    def GetWndCaption(self):
        return localization.GetByLabel('UI/Corporations/Wars/Allies')

    def GetRequesterText(self):
        requesterName, requesterInfo = self.GetEntityInfo(self.requesterID)
        if self.requesterID in (self.attackerID, self.defenderID):
            return localization.GetByLabel('UI/Corporations/Wars/RequestsAnAlly', requesterName=requesterName, requesterInfo=requesterInfo)
        elif self.isRequest:
            return localization.GetByLabel('UI/Corporations/Wars/OffersToAlly', requesterName=requesterName, requesterInfo=requesterInfo)
        else:
            return localization.GetByLabel('UI/Contracts/ContractsWindow/ShowInfoLink', showInfoName=requesterName, info=requesterInfo)

    def GetOfferText(self):
        return localization.GetByLabel('UI/Corporations/Wars/OfferAmountInISK', amount=self.warNegotiation.iskValue)

    def SubmitRequest(self, *args):
        message = self.requestText.GetValue()
        iskValue = float(self.offerAmount.GetValue())
        try:
            self._SubmitRequest(iskValue, message)
        finally:
            self.CloseByUser()

    def _SubmitRequest(self, iskValue, message):
        sm.GetService('war').RequestAssistance(self.warID, message, iskValue)

    def AcceptOffer(self, *args):
        try:
            self._AcceptOffer()
        finally:
            self.CloseByUser()

    def ShowInfo(self, itemID, typeID, *args):
        sm.GetService('info').ShowInfo(typeID, itemID)

    def DeclineOffer(self, *args):
        try:
            self._DeclineOffer()
        finally:
            self.CloseByUser()

    def GetBaseIskValue(self):
        return 0.0


class WarSurrenderWnd(NegotiationWnd):
    __guid__ = 'form.WarSurrenderWnd'

    def GetWndIconAndPath(self):
        return ('res:/UI/Texture/Icons/Surrender_64.png', 'ui_1337_64_5')

    def _AcceptOffer(self, *args):
        if self.isRequest:
            sm.GetService('war').CreateSurrenderNegotiation(warID, float(self.offerAmount.GetValue()))
        else:
            sm.GetService('war').AcceptSurrender(self.warNegotiation.warNegotiationID)

    def _DeclineOffer(self, *args):
        sm.GetService('war').DeclineSurrender(self.warNegotiation.warNegotiationID)

    def GetOfferAmountText(self):
        return localization.GetByLabel('UI/Corporations/Wars/SurrenderFee')

    def GetWndCaption(self):
        return localization.GetByLabel('UI/Corporations/Wars/Surrender')

    def GetText(self):
        return localization.GetByLabel('UI/Corporations/Wars/SurrenderOffer')

    def _SubmitRequest(self, iskValue, message):
        sm.GetService('war').CreateSurrenderNegotiation(self.warID, iskValue, message)

    def GetRequesterText(self):
        requesterName, requesterInfo = self.GetEntityInfo(self.requesterID)
        return localization.GetByLabel('UI/Corporations/Wars/OffersSurrender', requesterName=requesterName, requesterInfo=requesterInfo)


class WarAssistanceOfferWnd(NegotiationWnd):
    __guid__ = 'form.WarAssistanceOfferWnd'
    __notifyevents__ = ['OnWarChanged']

    def ApplyAttributes(self, attributes):
        self.originalIskValue = attributes.get('iskValue', 0)
        NegotiationWnd.ApplyAttributes(self, attributes)
        sm.RegisterNotify(self)

    def OnWarChanged(self, war, ownerIDs, change):
        if war is not None and war.warID == self.warID:
            self.offerLabel.text = self.GetOfferText()

    def GetOfferText(self):
        entityID = session.allianceid or session.corpid
        if entityID == self.warNegotiation.ownerID2:
            war = sm.GetService('war').GetWars(self.defenderID)[self.warID]
            baseCostFunc = sm.GetService('corp').GetAllyBaseCost
            concordFee = warUtil.GetAllyCostToConcord(war, baseCostFunc)
            if concordFee > 0:
                totalIsk = concordFee + self.warNegotiation.iskValue
                return localization.GetByLabel('UI/Corporations/Wars/AllyOfferWithFee', concordFee=util.FmtISK(concordFee), iskTotal=util.FmtISK(totalIsk))
        return localization.GetByLabel('UI/Corporations/Wars/MercenaryOfferDetailed', amount=self.warNegotiation.iskValue)

    def GetBaseIskValue(self):
        return self.originalIskValue

    def _AcceptOffer(self, *args):
        if not self.isRequest:
            sm.GetService('war').AcceptAllyNegotiation(self.warNegotiation.warNegotiationID)

    def _SubmitRequest(self, iskValue, message):
        sm.GetService('war').CreateWarAllyOffer(self.warID, iskValue, self.defenderID, message)

    def _DeclineOffer(self, *args):
        sm.GetService('war').DeclineAllyOffer(self.warNegotiation.warNegotiationID)


class WarContainer(uicls.Container):
    __guid__ = 'uicls.WarContainer'
    __notifyevents__ = []
    default_height = 36
    default_align = uiconst.TOTOP

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        war = attributes.get('war', None)
        self.ConstructLayout()
        sm.RegisterNotify(self)

    def ConstructLayout(self):
        self.attackerlogoCont = uicls.Container(parent=self, align=uiconst.TOLEFT, state=uiconst.UI_PICKCHILDREN, width=32, padding=2)
        swordCont = uicls.Container(parent=self, align=uiconst.TOLEFT, state=uiconst.UI_PICKCHILDREN, width=24, padding=2)
        swordLogo = uicls.Icon(name='warIcon', parent=swordCont, align=uiconst.CENTER, size=16, ignoreSize=True, state=uiconst.UI_NORMAL)
        swordLogo.LoadIcon('res:/UI/Texture/Icons/swords.png')
        swordLogo.SetAlpha(0.7)
        swordLogo.hint = localization.GetByLabel('UI/Corporations/Wars/Vs')
        self.defenderlogoCont = uicls.Container(parent=self, align=uiconst.TOLEFT, state=uiconst.UI_PICKCHILDREN, width=32, padding=2)
        self.textCont = uicls.Container(parent=self, align=uiconst.TOALL, state=uiconst.UI_PICKCHILDREN)
        self.corpLabels = uicls.EveLabelMedium(text='', parent=self.textCont, left=5, top=2, state=uiconst.UI_NORMAL, maxLines=1)
        self.dateLabel = uicls.EveLabelMedium(text='', parent=self.textCont, left=5, top=17, state=uiconst.UI_DISABLED, maxLines=1)

    def LoadWarInfo(self, war):
        if hasattr(self, 'attackerLogo'):
            self.attackerLogo.Close()
        if hasattr(self, 'defenderLogo'):
            self.defenderLogo.Close()
        self.corpLabels.text = ''
        self.dateLabel.text = ''
        date = util.FmtDate(war.timeDeclared, 'sn') if war.timeDeclared else localization.GetByLabel('UI/Common/Unknown')
        attackerID = war.declaredByID
        self.attackerID = attackerID
        attackerName = cfg.eveowners.Get(war.declaredByID).name
        if util.IsCorporation(attackerID):
            attackerLinkType = const.typeCorporation
        else:
            attackerLinkType = const.typeAlliance
        defenderID = war.againstID
        defenderName = cfg.eveowners.Get(war.againstID).name
        if util.IsCorporation(defenderID):
            defenderLinkType = const.typeCorporation
        else:
            defenderLinkType = const.typeAlliance
        warFinished = util.FmtDate(war.timeFinished, 'sn') if war.timeFinished else None
        warRetracted = util.FmtDate(war.retracted, 'sn') if war.retracted is not None else None
        warMutual = war.mutual
        timeStarted = war.timeStarted if hasattr(war, 'timeStarted') else 0
        currentTime = blue.os.GetWallclockTime()
        if currentTime <= timeStarted:
            fightTime = util.FmtDate(war.timeStarted, 'ns')
            if util.FmtDate(war.timeStarted, 'xn') != util.FmtDate(currentTime, 'xn'):
                timeText = localization.GetByLabel('UI/Corporations/Wars/WarStartedCanFightPlusDay', date=date, time=fightTime)
            else:
                timeText = localization.GetByLabel('UI/Corporations/Wars/WarStartedCanFight', date=date, time=fightTime)
        elif warFinished:
            if currentTime < war.timeFinished:
                endTime = util.FmtDate(war.timeFinished, 'ns')
                if util.FmtDate(war.timeFinished, 'xn') != util.FmtDate(currentTime, 'xn'):
                    timeText = localization.GetByLabel('UI/Corporations/Wars/WarStartedEndsAtPlusDay', date=date, time=endTime)
                else:
                    timeText = localization.GetByLabel('UI/Corporations/Wars/WarStartedEndsAt', date=date, time=endTime)
            else:
                timeText = localization.GetByLabel('UI/Corporations/Wars/WarStartedAndFinished', startDate=date, finishDate=warFinished)
        elif warRetracted:
            timeText = localization.GetByLabel('UI/Corporations/Wars/WarStartedAndRetracted', startDate=date, retractDate=warRetracted)
        else:
            timeText = localization.GetByLabel('UI/Corporations/Wars/WarStarted', date=date)
        if warMutual:
            locText = 'UI/Corporations/Wars/WarMutual'
        else:
            locText = 'UI/Corporations/Wars/WarNotMutual'
        self.corpLabels.text = localization.GetByLabel(locText, attackerName=attackerName, attackerInfo=('showinfo', attackerLinkType, attackerID), defenderName=defenderName, defenderInfo=('showinfo', defenderLinkType, defenderID))
        self.dateLabel.text = timeText
        self.attackerLogo = uiutil.GetLogoIcon(itemID=attackerID, parent=self.attackerlogoCont, acceptNone=False, align=uiconst.TOLEFT, state=uiconst.UI_NORMAL)
        self.attackerLogo.SetSize(32, 32)
        self.attackerLogo.OnClick = (self.ShowInfo, attackerID, attackerLinkType)
        self.attackerLogo.hint = '%s<br>%s' % (cfg.eveowners.Get(attackerID).name, localization.GetByLabel('UI/Corporations/Wars/Offender'))
        self.defenderLogo = uiutil.GetLogoIcon(itemID=defenderID, parent=self.defenderlogoCont, acceptNone=False, align=uiconst.TOLEFT, state=uiconst.UI_NORMAL)
        self.defenderLogo.SetSize(32, 32)
        self.defenderLogo.OnClick = (self.ShowInfo, defenderID, defenderLinkType)
        self.defenderLogo.hint = '%s<br>%s' % (cfg.eveowners.Get(defenderID).name, localization.GetByLabel('UI/Corporations/Wars/Defender'))

    def ShowInfo(self, itemID, typeID, *args):
        sm.GetService('info').ShowInfo(typeID, itemID)


class AllyWnd(uicls.Window):
    __guid__ = 'form.AllyWnd'
    __notifyevents__ = []
    default_windowID = 'AllyWnd'
    default_width = 350
    default_height = 282
    default_minSize = (default_width, default_height)
    default_iconNum = 'ui_1337_64_4'

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        self.war = war = attributes.war
        self.allies = attributes.allies
        self.SetTopparentHeight(0)
        self.SetCaption(localization.GetByLabel('UI/Corporations/Wars/Allies'))
        self.HideClippedIcon()
        self.ConstructLayout()

    def ConstructLayout(self):
        topCont = uicls.Container(name='topCont', parent=self.sr.main, align=uiconst.TOTOP, height=48, padding=const.defaultPadding)
        alliesCont = uicls.Container(name='alliesCont', parent=self.sr.main, align=uiconst.TOALL, padding=(const.defaultPadding,
         const.defaultPadding,
         0,
         const.defaultPadding))
        allyIcon = uicls.Icon(parent=topCont, align=uiconst.TOPLEFT, pos=(0, 0, 46, 46), ignoreSize=True)
        allyIcon.LoadIcon('res:/UI/Texture/Icons/Mercenary_64.png')
        windowTitle = uicls.EveCaptionSmall(text=localization.GetByLabel('UI/Corporations/Wars/Allies'), parent=topCont, align=uiconst.TOTOP, height=22, padLeft=46, top=3)
        subTitle = uicls.EveLabelMedium(text='', parent=topCont, align=uiconst.TOTOP, padLeft=46)
        defenderName = cfg.eveowners.Get(self.war.declaredByID).name
        subTitle.text = localization.GetByLabel('UI/Corporations/Wars/InWarAgainst', defenderName=defenderName)
        self.allyScroll = uicls.Scroll(name='alliesScroll', parent=alliesCont, align=uiconst.TOALL)
        self.GetAllies()

    def IsOpenForAllies(self):
        return self.war.openForAllies

    def GetAllies(self):
        scrolllist = []
        if self.allies is None:
            warStatMon = moniker.GetWarStatistic(self.war.warID)
            warStatMon.Bind()
            baseInfo = warStatMon.GetBaseInfo()
            self.allies = baseInfo[-1]
        try:
            allies = self.allies.itervalues()
        except AttributeError:
            allies = self.allies

        currentTime = blue.os.GetWallclockTime()
        for ally in allies:
            if currentTime > ally.timeFinished:
                continue
            scrolllist.append(listentry.Get('AllyListEntry', {'warID': self.war.warID,
             'allyID': ally.allyID,
             'warNegotiationID': None,
             'allyRow': ally,
             'isAlly': True}))

        self.allyScroll.Load(contentList=scrolllist, noContentHint=localization.GetByLabel('UI/Corporations/Wars/NoAlliesInWar'))


class WarEntry(uicls.SE_BaseClassCore):
    __guid__ = 'listentry.WarEntry'
    __notifyevents__ = ['OnWarEntryChanged']
    isDragObject = True

    def ApplyAttributes(self, attributes):
        self.showAllyButton = False
        uicls.SE_BaseClassCore.ApplyAttributes(self, attributes)
        uicls.Line(parent=self, align=uiconst.TOTOP)
        self.hilite = uicls.Fill(parent=self, color=(1.0, 1.0, 1.0, 0.1))
        self.hilite.display = False
        self.buttonCont = uicls.Container(name='buttons', parent=self, align=uiconst.TORIGHT, width=30)
        warCont = uicls.Container(name='wars', parent=self, align=uiconst.TOALL, clipChildren=True, padRight=4)
        self.warNegotiationID = None
        self.warAllyNegotiationID = None
        self.allies = None
        self.noOfAllies = 0
        utilMenu = uicls.UtilMenu(menuAlign=uiconst.TOPRIGHT, parent=self.buttonCont, align=uiconst.CENTERRIGHT, GetUtilMenu=self.WarMenu, texturePath='res:/UI/Texture/Icons/73_16_50.png', left=const.defaultPadding)
        self.openForAllies = uicls.Icon(parent=self.buttonCont, align=uiconst.CENTERRIGHT, left=27, iconSize=20, size=20)
        self.openForAllies.LoadIcon('res:/UI/Texture/Icons/Mercenary_Add_64.png')
        self.openForAllies.display = False
        self.openForAllies.hint = localization.GetByLabel('UI/Corporations/Wars/DefenderOpenForAllies')
        self.surrenderNegotiation = uicls.Icon(parent=self.buttonCont, align=uiconst.CENTERRIGHT, left=52, iconSize=20, size=20)
        self.surrenderNegotiation.LoadIcon('res:/UI/Texture/Icons/Surrender_Attention_64.png')
        self.surrenderNegotiation.display = False
        self.surrenderNegotiation.hint = localization.GetByLabel('UI/Corporations/Wars/SurrenderPending')
        self.warCont = uicls.WarContainer(parent=warCont, top=2)
        sm.RegisterNotify(self)

    def Load(self, node):
        self.sr.node = node
        self.war = war = node.war
        self.myWars = node.myWars
        self.warID = war.warID
        self.attackerID = war.declaredByID
        self.defenderID = war.againstID
        self.warIsOpen = self.IsOpenForAllies()
        self.LoadEntry(war)

    def IsDirector(self):
        entityID = session.allianceid or session.corpid
        if session.corprole & const.corpRoleDirector == const.corpRoleDirector:
            return True
        return False

    def IsMyWar(self):
        entityID = session.allianceid or session.corpid
        if entityID in (self.attackerID, self.defenderID):
            return True
        return False

    def IsDefender(self):
        entityID = session.allianceid or session.corpid
        if entityID == self.defenderID:
            return True
        return False

    def IsAttacker(self):
        entityID = session.allianceid or session.corpid
        if entityID == self.attackerID:
            return True
        return False

    def IsNegotiating(self):
        allyNegotiationsByWarID = defaultdict(list)
        myID = session.allianceid or session.corpid
        for row in sm.GetService('war').GetAllyNegotiations():
            allyNegotiationsByWarID[self.warID].append(row)
            if self.warID in allyNegotiationsByWarID:
                for neg in allyNegotiationsByWarID[self.warID]:
                    if neg.negotiationState == const.warNegotiationDeclined:
                        continue
                    elif neg.negotiationState == const.warNegotiationNew and blue.os.GetWallclockTime() > neg.expiryTime:
                        continue
                    if neg.ownerID1 == myID and neg.warID == self.warID:
                        self.warAllyNegotiationID = neg.warNegotiationID
                        return True

        return False

    def IsRetracted(self):
        warRetracted = self.war.retracted
        if warRetracted is not None:
            return True
        return False

    def IsFinished(self):
        warFinished = self.war.timeFinished
        if warFinished:
            if blue.os.GetWallclockTime() >= warFinished:
                return True
        return False

    def SetOpenForAllies(self, open, *args):
        try:
            self.warIsOpen = open
            sm.GetService('war').SetOpenForAllies(self.war.warID, open)
            sm.ScatterEvent('OnWarEntryChanged', self.war.warID, self.war)
        except Exception:
            raise 

    def WarMenu(self, menuParent):
        isMutual = self.war.mutual
        if util.IsFaction(self.defenderID):
            menuParent.AddIconEntry(icon='res:/UI/Texture/Icons/FactionalWarfare_64.png', text=localization.GetByLabel('UI/Commands/OpenFactionalWarfare'), callback=sm.GetService('cmd').OpenMilitia)
            return
        if not isMutual:
            if self.IsMyWar() and self.IsDirector() and not self.IsFinished():
                if self.IsDefender():
                    if self.warIsOpen:
                        isOpen = True
                    else:
                        isOpen = False
                    menuParent.AddCheckBox(text=localization.GetByLabel('UI/Corporations/Wars/OpenForAllies'), checked=isOpen, callback=(self.SetOpenForAllies, not isOpen))
            if not self.IsMyWar() and self.IsDirector() and not self.IsAlly() and not self.IsFinished():
                if self.IsNegotiating():
                    menuParent.AddIconEntry(icon='res:/UI/Texture/Icons/Mercenary_Attention_64.png', text=localization.GetByLabel('UI/Corporations/Wars/ViewAssistanceOffer'), callback=self.ShowWarNegotiation)
                else:
                    menuParent.AddIconEntry(icon='res:/UI/Texture/Icons/Mercenary_Add_64.png', text=localization.GetByLabel('UI/Corporations/Wars/OfferAssistance'), callback=self.OpenRequestWindow)
            numAllies = self.GetNumAllies()
            if numAllies > 0:
                menuParent.AddIconEntry(icon='res:/UI/Texture/Icons/Mercenary_Ally_64.png', text=localization.GetByLabel('UI/Corporations/Wars/ViewNumAllies', num=numAllies), callback=self.OpenAllyWindow)
            else:
                menuParent.AddIconEntry(icon='res:/UI/Texture/Icons/Mercenary_Ally_64.png', text=localization.GetByLabel('UI/Corporations/Wars/ViewAllies'))
        if self.IsDefender() and self.IsInCharge() and not self.IsFinished():
            menuParent.AddCheckBox(text=localization.GetByLabel('UI/Corporations/CorporationWindow/Wars/DeclareMutualMenuOption'), checked=isMutual, callback=(self.ChangeMutualWarFlag, not isMutual))
        if self.IsMyWar() and self.IsDirector() and not self.IsFinished():
            if not self.IsRetracted():
                if self.warNegotiationID:
                    menuParent.AddIconEntry(icon='res:/UI/Texture/Icons/Surrender_Attention_64.png', text=localization.GetByLabel('UI/Corporations/Wars/ViewSurrenderOffer'), callback=self.SurrenderClick)
                else:
                    menuParent.AddIconEntry(icon='res:/UI/Texture/Icons/Surrender_64.png', text=localization.GetByLabel('UI/Corporations/Wars/SendSurrenderOffer'), callback=self.SurrenderClick)
                if getattr(self.war, 'canBeRetracted', None):
                    if self.war.canBeRetracted and not self.IsDefender():
                        menuParent.AddIconEntry(icon='res:/UI/Texture/Icons/Surrender_64.png', text=localization.GetByLabel('UI/Corporations/Wars/RetractWar'), callback=self.RetractWarClick)
        menuParent.AddIconEntry(icon='res:/UI/Texture/Icons/1337_64_2.png', text=localization.GetByLabel('UI/Corporations/Wars/OpenWarReport'), callback=self.OpenWarReport)

    def LoadEntry(self, war):
        if not util.IsFaction(self.attackerID) and not self.IsFinished():
            self.GetAllies()
            if self.IsOpenForAllies():
                self.buttonCont.width = 50
                self.openForAllies.display = True
            else:
                self.buttonCont.width = 30
                self.openForAllies.display = False
        if not self.war.mutual and not self.IsMyWar() and self.IsInCharge() and self.IsNegotiating() and not self.IsAlly():
            self.openForAllies.LoadIcon('res:/UI/Texture/Icons/Mercenary_Attention_64.png')
            self.openForAllies.display = True
            self.openForAllies.hint = localization.GetByLabel('UI/Corporations/Wars/YouOfferedHelp')
        if self.IsDirector() and self.IsMyWar() and war.retracted == None:
            self.GetSurrenderStatus()
        self.warCont.LoadWarInfo(war)
        self.warCont.corpLabels.OnMouseEnter = self.OnMouseEnter
        self.warCont.attackerLogo.OnMouseEnter = self.OnMouseEnter
        self.warCont.defenderLogo.OnMouseEnter = self.OnMouseEnter
        self.warCont.corpLabels.OnMouseExit = self.OnMouseExit
        self.warCont.attackerLogo.OnMouseExit = self.OnMouseExit
        self.warCont.defenderLogo.OnMouseExit = self.OnMouseExit

    def OnWarEntryChanged(self, warID, war, *args):
        if warID == self.warID:
            self.war = war
            self.LoadEntry(self.war)

    def GetNumAllies(self):
        return self.noOfAllies

    def IsOpenForAllies(self):
        if self.war.mutual:
            return False
        return self.war.openForAllies

    def IsAlly(self):
        return sm.GetService('war').IsAllyInWar(self.warID)

    def GetSurrenderStatus(self):
        surrenders = sm.GetService('war').GetSurrenderNegotiations(self.war.warID)
        self.surrenderNegotiation.display = False
        if len(surrenders):
            self.surrenderNegotiation.display = True
            if self.IsOpenForAllies():
                self.buttonCont.width = 74
                self.surrenderNegotiation.left = 52
            else:
                self.buttonCont.width = 50
                self.surrenderNegotiation.left = 27
            for surrender in surrenders:
                self.warNegotiationID = surrender.warNegotiationID

    def GetHeight(self, *args):
        node, width = args
        node.height = 40
        return node.height

    def ButtonMouseEnter(self, btn, *args):
        if not btn.enabled:
            return
        uicore.animations.FadeIn(btn.mouseEnterBG, duration=0.2)
        self.OnMouseEnter()

    def ButtonMouseExit(self, btn, *args):
        uicore.animations.FadeOut(btn.mouseEnterBG, duration=0.2)
        self.OnMouseExit()

    def OnMouseEnter(self, *args):
        mouseItem = uicore.uilib.mouseOver
        if mouseItem == self or uiutil.IsUnder(mouseItem, self):
            self.hilite.display = True

    def OnMouseExit(self, *args):
        mouseItem = uicore.uilib.mouseOver
        if uiutil.IsUnder(mouseItem, self):
            return
        self.hilite.display = False

    def AllyClick(self, *args):
        if self.war.retracted is not None:
            self.OpenAllyWindow()
        elif self.IsNegotiating() and self.IsDirector():
            self.ShowWarNegotiation()
        elif not self.IsDirector() or self.IsMyWar() or self.IsAlly():
            self.OpenAllyWindow()
        else:
            self.OpenRequestWindow()

    def GetAllies(self):
        try:
            allies = self.war.allies
            try:
                allies = allies.values()
            except AttributeError:
                pass

            self.noOfAllies = len([ ally for ally in allies if blue.os.GetWallclockTime() < ally.timeFinished ])
        except AttributeError:
            self.noOfAllies = self.war.noOfAllies

    def OpenAllyWindow(self):
        form.AllyWnd.CloseIfOpen()
        form.AllyWnd.Open(war=self.war, allies=self.allies)

    def OpenRequestWindow(self):
        form.WarAssistanceOfferWnd.Open(isRequest=True, warID=self.warID, war=self.war, attackerID=self.attackerID, defenderID=self.defenderID, requesterID=session.allianceid or session.corpid, iskValue=getattr(self.war, 'reward', 0))

    def ShowWarNegotiation(self):
        form.WarAssistanceOfferWnd.Open(isRequest=False, warNegotiationID=self.warAllyNegotiationID, requesterID=session.allianceid or session.corpid)

    def SurrenderClick(self, *args):
        if self.warNegotiationID:
            form.WarSurrenderWnd.CloseIfOpen()
            form.WarSurrenderWnd.Open(warNegotiationID=self.warNegotiationID, isRequest=False)
        else:
            form.WarSurrenderWnd.CloseIfOpen()
            requesterID = session.corpid if session.allianceid is None else session.allianceid
            form.WarSurrenderWnd.Open(war=self.war, requesterID=requesterID, isSurrender=True, isAllyRequest=False, isRequest=True)

    def RetractWarClick(self, *args):
        headerLabel = localization.GetByLabel('UI/Corporations/Wars/RetractWar')
        bodyLabel = localization.GetByLabel('UI/Corporations/Wars/RetractWarSure')
        ret = eve.Message('CustomQuestion', {'header': headerLabel,
         'question': bodyLabel}, uiconst.YESNO)
        if ret != uiconst.ID_YES:
            return
        warID = self.warID
        sm.GetService('war').RetractMutualWar(warID)

    def OpenWarReport(self):
        wnd = form.WarReportWnd.GetIfOpen()
        if wnd:
            wnd.LoadInfo(warID=self.warID)
            wnd.Maximize()
        else:
            form.WarReportWnd.Open(attackerID=self.attackerID, defenderID=self.defenderID, warID=self.warID)

    def OnDblClick(self, *args):
        if util.IsFaction(self.attackerID):
            sm.GetService('cmd').OpenMilitia()
        else:
            self.OpenWarReport()

    def GetMenu(self):
        warEntityID = session.allianceid or session.corpid
        menu = []
        subMenu = []
        war = self.war
        if session.role & ROLE_GMH == ROLE_GMH:
            subMenu.append(('Copy : %s' % war.warID, lambda : None))
        myWarEntityID = session.corpid if session.allianceid is None else session.allianceid
        if warEntityID not in (war.declaredByID, war.againstID):
            if session.role & ROLE_GMH == ROLE_GMH:
                if hasattr(war, 'allies') and myWarEntityID in war.allies:
                    subMenu.append(('Start Defending', self.GMActivateDefender, (war.warID, myWarEntityID)))
                else:
                    subMenu.append(('Join Defender', sm.GetService('war').GMJoinDefender, (war.warID, war.declaredByID)))
        elif session.role & ROLE_GMH == ROLE_GMH:
            if myWarEntityID in (war.againstID, war.declaredByID):
                subMenu.extend([('Set Start Time', self.GMSetStartTime, (war,)),
                 ('Set Finish Time', self.GMSetFinishTime, (war,)),
                 ('Force Finish War', self.GMForceFinishWar, (war,)),
                 ('Clear Forced Peace', self.GMClearForcedPeace, (war.warID,))])
        if subMenu:
            menu.append(['GM Tools', subMenu])
        return menu

    def GetDragData(self, *args):
        if util.IsFaction(self.attackerID):
            return []
        nodes = [self.sr.node]
        return nodes

    def IsInCharge(self):
        if session.allianceid is not None:
            return session.corpid == sm.GetService('alliance').GetAlliance().executorCorpID and session.corprole & const.corpRoleDirector == const.corpRoleDirector
        else:
            return sm.GetService('corp').UserIsActiveCEO()

    def ChangeMutualWarFlag(self, mutual, *args):
        warID = self.war.warID
        if not self.IsInCharge():
            if session.allianceid is not None:
                raise UserError('CrpAccessDenied', {'reason': localization.GetByLabel('UI/Corporations/CorporationWindow/Wars/AccessDeniedNotDirector')})
            else:
                raise UserError('CrpAccessDenied', {'reason': localization.GetByLabel('UI/Corporations/CorporationWindow/Wars/AccessDeniedNotCEO')})
        if eve.Message(['CrpConfirmUnmutualWar', 'CrpConfirmMutualWar2'][mutual], {}, uiconst.YESNO) == uiconst.ID_YES:
            if session.allianceid is not None:
                sm.GetService('alliance').ChangeMutualWarFlag(warID, mutual)
            else:
                sm.GetService('corp').ChangeMutualWarFlag(warID, mutual)

    def GMSetStartTime(self, war):
        ret = uiutil.NamePopup(caption='Set Start Time', label='Type in Start Time', setvalue=util.FmtDate(war.timeDeclared))
        if ret is None:
            return
        newTime = util.ParseDateTime(ret)
        sm.GetService('war').GMSetWarStartTime(war.warID, newTime)

    def GMSetFinishTime(self, war):
        ret = uiutil.NamePopup(caption='Set Finished Time', label='Type in Finished Time', setvalue=util.FmtDate(war.timeFinished))
        if ret is None:
            return
        newTime = util.ParseDateTime(ret)
        sm.GetService('war').GMSetWarFinishTime(war.warID, newTime)

    def GMForceFinishWar(self, war):
        sm.GetService('war').GMSetWarFinishTime(war.warID, blue.os.GetTime() - const.DAY)

    def GMActivateDefender(self, warID, allyID):
        sm.GetService('war').GMActivateDefender(warID, allyID)

    def GMClearForcedPeace(self, warID):
        sm.GetService('war').GMClearForcedPeace(warID)


class AllyEntry(uicls.SE_BaseClassCore):
    __guid__ = 'listentry.AllyEntry'

    def ApplyAttributes(self, attributes):
        uicls.SE_BaseClassCore.ApplyAttributes(self, attributes)
        self.hilite = uicls.Fill(parent=self, color=(1.0, 1.0, 1.0, 0.1))
        self.hilite.display = False
        self.iconCont = uicls.Container(name='iconCont', parent=self, align=uiconst.TOLEFT, width=98)
        self.textCont = uicls.Container(name='textCont', parent=self, align=uiconst.TOALL, padLeft=7, clipChildren=True, width=30)
        self.allyButton = uicls.ButtonIcon(name='allyButton', parent=self, align=uiconst.TORIGHT, width=24, iconSize=24, texturePath='res:/UI/Texture/Icons/Mercenary_64.png', left=2)
        self.allyNameLabel = uicls.EveLabelMedium(text='', parent=self.textCont, top=2, state=uiconst.UI_NORMAL, align=uiconst.CENTERLEFT)

    def Load(self, node):
        self.sr.node = node
        if node.allyRow is None:
            self.timeStarted = None
            self.timeFinished = None
        else:
            self.timeStarted = node.allyRow.timeStarted
            self.timeFinished = node.allyRow.timeFinished
        self.warNegotiation = node.warNegotiation
        self.LoadEntry(node.warID, node.allyID, node.isAlly)

    def LoadEntry(self, warID, allyID, isAlly):
        if hasattr(self, 'allyLogo'):
            self.allyLogo.Close()
        self.allyNameLabel.text = ''
        self.allyID = allyID
        self.isAlly = isAlly
        self.warID = warID
        if util.IsCorporation(self.allyID):
            allyLinkType = const.typeCorporation
        elif util.IsAlliance(self.allyID):
            allyLinkType = const.typeAlliance
        else:
            allyLinkType = const.typeFaction
        allyName = cfg.eveowners.Get(self.allyID).name
        self.allyLogo = uiutil.GetLogoIcon(itemID=self.allyID, parent=self.iconCont, acceptNone=False, align=uiconst.TOPRIGHT, size=32, state=uiconst.UI_NORMAL, top=2)
        self.allyLogo.OnClick = (self.ShowInfo, self.allyID, allyLinkType)
        self.allyLogo.hint = '%s<br>%s' % (allyName, localization.GetByLabel('UI/Corporations/Wars/Ally'))
        allyName = localization.GetByLabel('UI/Contracts/ContractsWindow/ShowInfoLink', showInfoName=allyName, info=('showinfo', allyLinkType, self.allyID))
        self.allyNameLabel.text = ''
        self.UpdateText()
        if not self.isAlly:
            allyTexturePath = 'res:/UI/Texture/Icons/Mercenary_Attention_64.png'
            allyHint = localization.GetByLabel('UI/Corporations/Wars/OfferedHelp')
            if self.IsDirector():
                self.allyButton.OnClick = self.AllyClick
                self.allyButton.Enable()
        else:
            allyTexturePath = 'res:/UI/Texture/Icons/Mercenary_Ally_64.png'
            allyHint = localization.GetByLabel('UI/Corporations/Wars/HelpAccepted')
            self.allyButton.Disable()
        self.allyButton.icon.LoadIcon(allyTexturePath)
        self.allyButton.hint = allyHint
        self.allyButton.OnMouseEnter = (self.ButtonMouseEnter, self.allyButton)
        self.allyButton.OnMouseExit = (self.ButtonMouseExit, self.allyButton)
        self.allyLogo.OnMouseEnter = self.OnMouseEnter
        self.allyLogo.OnMouseExit = self.OnMouseExit
        self.allyNameLabel.OnMouseEnter = self.OnMouseEnter
        self.allyNameLabel.OnMouseExit = self.OnMouseExit

    def UpdateText(self):
        if util.IsCorporation(self.allyID):
            allyLinkType = const.typeCorporation
        elif util.IsAlliance(self.allyID):
            allyLinkType = const.typeAlliance
        else:
            allyLinkType = const.typeFaction
        currentTime = blue.os.GetWallclockTime()
        allyName = cfg.eveowners.Get(self.allyID).ownerName
        if not self.isAlly:
            self.allyNameLabel.text = localization.GetByLabel('UI/Corporations/Wars/AllyEntryAssistanceOffered', allyID=self.allyID, info=('showinfo', allyLinkType, self.allyID), ally=cfg.eveowners.Get(self.allyID).ownerName)
            self.hint = localization.GetByLabel('UI/Corporations/Wars/AllyEntryAssistanceOfferedHint', ally=cfg.eveowners.Get(self.allyID).ownerName, description=self.warNegotiation.description, iskValue=self.warNegotiation.iskValue)
        if currentTime < self.timeStarted:
            self.allyNameLabel.text = localization.GetByLabel('UI/Corporations/Wars/AllyEntryNotStarted', allyID=self.allyID, info=('showinfo', allyLinkType, self.allyID), ally=cfg.eveowners.Get(self.allyID).ownerName, timeToFight=self.timeStarted - currentTime)
            self.hint = localization.GetByLabel('UI/Corporations/Wars/AllyEntryNotStartedHint', startTime=util.FmtDate(self.timeStarted, 'sn'), endTime=util.FmtDate(self.timeFinished, 'sn'))
        elif currentTime < self.timeFinished:
            self.allyNameLabel.text = localization.GetByLabel('UI/Contracts/ContractsWindow/ShowInfoLink', showInfoName=allyName, info=('showinfo', allyLinkType, self.allyID))
            self.hint = localization.GetByLabel('UI/Corporations/Wars/AllyEntryStartedHint', startTime=util.FmtDate(self.timeStarted, 'sn'), endTime=util.FmtDate(self.timeFinished, 'sn'))

    def GetHeight(self, *args):
        node, width = args
        node.height = 36
        return node.height

    def ButtonMouseEnter(self, btn, *args):
        if not btn.enabled:
            return
        uicore.animations.FadeIn(btn.mouseEnterBG, duration=0.2)
        self.OnMouseEnter()

    def ButtonMouseExit(self, btn, *args):
        uicore.animations.FadeOut(btn.mouseEnterBG, duration=0.2)
        self.OnMouseExit()

    def OnMouseEnter(self, *args):
        mouseItem = uicore.uilib.mouseOver
        if mouseItem == self or uiutil.IsUnder(mouseItem, self):
            self.hilite.display = True

    def OnMouseExit(self, *args):
        mouseItem = uicore.uilib.mouseOver
        if uiutil.IsUnder(mouseItem, self):
            return
        self.hilite.display = False

    def OnDblClick(self, *args):
        wnd = form.WarReportWnd.GetIfOpen()
        if wnd:
            wnd.LoadInfo(warID=self.warID)
            wnd.Maximize()
        else:
            form.WarReportWnd.Open(warID=self.warID)

    def AllyClick(self):
        if not self.isAlly:
            self.ShowWarNegotiation()

    def IsDirector(self):
        entityID = session.allianceid or session.corpid
        if session.corprole & const.corpRoleDirector == const.corpRoleDirector:
            return True
        return False

    def ShowWarNegotiation(self):
        form.WarAssistanceOfferWnd.Open(isRequest=False, warNegotiationID=self.sr.node.warNegotiation.warNegotiationID, requesterID=self.allyID)

    def ShowInfo(self, itemID, typeID, *args):
        sm.GetService('info').ShowInfo(typeID, itemID)

    def GetMenu(self, *args):
        menu = []
        if session.role & ROLE_GMH == ROLE_GMH:
            subMenu = []
            if self.isAlly:
                if self.timeStarted > blue.os.GetWallclockTime():
                    subMenu.append(('Start Defending', sm.GetService('war').GMActivateDefender, (self.warID, self.allyID)))
                else:
                    subMenu.append(('Extend Contract', sm.GetService('war').GMExtendAllyContract, (self.warID, self.allyID, const.WEEK)))
                    subMenu.append(('Finish Defending', sm.GetService('war').GMDeactivateDefender, (self.warID, self.allyID)))
                menu.append(('GM Tools', subMenu))
        return menu


class WarHeader(listentry.Header):
    __guid__ = 'listentry.WarHeader'

    def Startup(self, *args):
        listentry.Header.Startup(self, *args)
        self.sr.line.display = False


class HeaderClear(listentry.Header):
    __guid__ = 'listentry.HeaderClear'

    def Startup(self, *args):
        listentry.Header.Startup(self, *args)
        self.sr.line.display = False
        self.clearButton = uicls.ButtonIcon(name='removeButton', parent=self, align=uiconst.TORIGHT, width=16, iconSize=16, texturePath='res:/UI/Texture/Icons/73_16_210.png')

    def Load(self, node):
        listentry.Header.Load(self, node)
        self.clearButton.func = node.func


class AllyListEntry(AllyEntry):
    __guid__ = 'listentry.AllyListEntry'

    def ApplyAttributes(self, attributes):
        AllyEntry.ApplyAttributes(self, attributes)
        self.iconCont.width = 36

    def LoadEntry(self, warID, allyID, isAlly):
        AllyEntry.LoadEntry(self, warID, allyID, isAlly)
        self.allyLogo.left = 2