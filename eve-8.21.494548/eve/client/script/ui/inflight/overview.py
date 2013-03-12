#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/ui/inflight/overview.py
import base
import blue
import const
import form
import listentry
import state
import uix
import uthread
import util
import xtriui
import uiutil
import uiconst
import uicls
import localization
import localizationUtil
import eveLocalization
import fontConst
import telemetry
import geo2
import log
import sys
import bracketUtils
import _weakref
import trinity
import const
import fleetbr
import bisect
import locks
import re
from collections import defaultdict
import stackless
ScrollListLock = locks.RLock()
HTML_ENTITIES = '&gt;|&lt;|&amp;|&GT;|&LT;|&AMP;'
HTML_ENTITY_REPLACEMENTS = {'&gt;': u'>',
 '&lt;': u'<',
 '&amp;': u'&',
 '&GT;': u'>',
 '&LT;': u'<',
 '&AMP;': u'&'}
COLUMN_VELOCITY = 'VELOCITY'
COLUMN_RADIALVELOCITY = 'RADIALVELOCITY'
COLUMN_ANGULARVELOCITY = 'ANGULARVELOCITY'
COLUMN_TRANSVERSALVELOCITY = 'TRANSVERSALVELOCITY'
COLUMN_DISTANCE = 'DISTANCE'
COLUMN_SIZE = 'SIZE'
COLUMN_MILITIA = 'MILITIA'
COLUMN_FACTION = 'FACTION'
COLUMN_CORPORATION = 'CORPORATION'
COLUMN_TAG = 'TAG'
COLUMN_TYPE = 'TYPE'
COLUMN_NAME = 'NAME'
COLUMN_ICON = 'ICON'
COLUMN_ALLIANCE = 'ALLIANCE'
COLUMNFADESIZE = 20
COLUMNMARGIN = 4
COLUMNMINSIZE = 24
COLUMNMINDEFAULTSIZE = 80
FIXEDCOLUMNS = {COLUMN_ICON: 22}
ALLCOLUMNS = [COLUMN_VELOCITY,
 COLUMN_RADIALVELOCITY,
 COLUMN_ANGULARVELOCITY,
 COLUMN_TRANSVERSALVELOCITY,
 COLUMN_DISTANCE,
 COLUMN_SIZE,
 COLUMN_MILITIA,
 COLUMN_FACTION,
 COLUMN_CORPORATION,
 COLUMN_TAG,
 COLUMN_TYPE,
 COLUMN_NAME,
 COLUMN_ICON,
 COLUMN_ALLIANCE]
RIGHTALIGNEDCOLUMNS = [COLUMN_DISTANCE,
 COLUMN_SIZE,
 COLUMN_VELOCITY,
 COLUMN_RADIALVELOCITY,
 COLUMN_ANGULARVELOCITY,
 COLUMN_TRANSVERSALVELOCITY]
FMTFUNCTION = localizationUtil.FormatNumeric
CURVE_HOSTILE = 2
CURVE_ATTACKING = 3
FMT_M = None
FMT_KM = None
FMT_AU = None
FMT_VELOCITY = None

class OverView(form.ActionPanel):
    __guid__ = 'form.OverView'
    __notifyevents__ = ['OnDestinationSet',
     'OnOverviewTabChanged',
     'OnEwarStart',
     'OnEwarEnd',
     'OnStateSetupChance',
     'OnSessionChanged',
     'OnFleetJoin_Local',
     'OnFleetLeave_Local',
     'OnPostCfgDataChanged',
     'OnTacticalPresetChange',
     'OnFleetStateChange',
     'OnStateChange',
     'DoBallsAdded',
     'DoBallRemove',
     'OnUIScalingChange',
     'OnSlimItemChange',
     'OnContactChange',
     'OnTutorialHighlightItem',
     'ProcessBountyInfoUpdated']
    default_pinned = True
    default_windowID = 'overview'
    default_height = 300
    default_open = True
    sortingFrozen = False

    @staticmethod
    def default_top(*args):
        topRight_TopOffset = uicls.Window.GetTopRight_TopOffset()
        if topRight_TopOffset is not None:
            return topRight_TopOffset
        return 16

    @staticmethod
    def default_left(*args):
        return uicore.desktop.width - form.OverView.default_width - 16

    @telemetry.ZONE_METHOD
    def ApplyAttributes(self, attributes):
        global FMT_VELOCITY
        global FMT_M
        global FMT_AU
        global FMT_KM
        self.overviewUpdateThread = None
        self._freezeOverview = False
        self._ballparkDirty = True
        self._scrollEntriesDirty = True
        self._scrollNodesByItemID = {}
        attributes.showActions = False
        form.ActionPanel.ApplyAttributes(self, attributes)
        self.cursor = uiconst.UICURSOR_HASMENU
        self.jammers = {}
        self.ewarTypes = sm.GetService('state').GetEwarTypes()
        self.ewarHintsByGraphicID = {}
        for jamType, (flag, graphicID) in self.ewarTypes:
            self.ewarHintsByGraphicID[graphicID] = sm.GetService('state').GetEwarHint(jamType)

        self.minUpdateSleep = int(sm.GetService('machoNet').GetGlobalConfig().get('overviewMinUpdateSleep', 500))
        self.maxUpdateSleep = int(sm.GetService('machoNet').GetGlobalConfig().get('overviewMaxUpdateSleep', 1000))
        self.prevMouseCoords = trinity.GetCursorPos()
        self.lastMovementTime = blue.os.GetWallclockTime()
        self.mouseMovementTimeout = int(sm.GetService('machoNet').GetGlobalConfig().get('overviewMouseMovementTimeout', 0))
        languageID = localizationUtil.GetLanguageID()
        FMT_M = eveLocalization.GetMessageByID(234383, languageID)
        FMT_KM = eveLocalization.GetMessageByID(234384, languageID)
        FMT_AU = eveLocalization.GetMessageByID(234385, languageID)
        FMT_VELOCITY = eveLocalization.GetMessageByID(239583, languageID)

    def Close(self):
        form.ActionPanel.Close(self)

    def DoBallRemove(self, ball, slimItem, terminal):
        if ball is None:
            return
        itemID = slimItem.itemID
        node = self._scrollNodesByItemID.get(itemID, None)
        if node:
            node.leavingOverview = True
            if node.panel:
                node.panel.opacity = 0.25
                node.panel.state = uiconst.UI_DISABLED
            if node.itemID in self._scrollNodesByItemID:
                del self._scrollNodesByItemID[node.itemID]

    def DoBallsAdded(self, lst, *args, **kw):
        uthread.new(self._DoBallsAdded, lst, *args, **kw)

    @telemetry.ZONE_METHOD
    def _DoBallsAdded(self, lst, *args, **kw):
        tacticalSvc = sm.GetService('tactical')
        stateSvc = sm.GetService('state')
        fleetSvc = sm.GetService('fleet')
        CheckIfFilterItem = stateSvc.CheckIfFilterItem
        CheckFiltered = tacticalSvc.CheckFiltered
        CheckIfUpdateItem = stateSvc.CheckIfUpdateItem
        filterGroups = tacticalSvc.GetValidGroups()
        filteredStates = tacticalSvc.GetFilteredStatesFunctionNames()
        columns = tacticalSvc.GetColumns()
        if self.sortHeaders.GetCurrentColumns() != columns:
            self.sortHeaders.CreateColumns(columns, fixedColumns=FIXEDCOLUMNS)
        now = blue.os.GetSimTime()
        with ScrollListLock:
            newEntries = []
            for ball, slimItem in lst:
                if slimItem.itemID in self._scrollNodesByItemID:
                    continue
                if slimItem.groupID in filterGroups and slimItem.itemID != eve.session.shipid:
                    if CheckIfFilterItem(slimItem) and CheckFiltered(slimItem, filteredStates):
                        continue
                    updateItem = CheckIfUpdateItem(slimItem)
                    data = {'itemID': slimItem.itemID,
                     'updateItem': updateItem}
                    newNode = listentry.Get('OverviewScrollEntry', data)
                    newNode.ball = _weakref.ref(ball)
                    newNode.slimItem = _weakref.ref(slimItem)
                    if updateItem:
                        newNode.ewarGraphicIDs = self.GetEwarDataForNode(newNode)
                    newNode.ewarHints = self.ewarHintsByGraphicID
                    newEntries.append(newNode)

            if newEntries:
                self.UpdateStaticDataForNodes(newEntries)
                self.UpdateDynamicDataForNodes(newEntries)
                currentActive, currentDirection = self.sortHeaders.GetCurrentActive()
                broadcastsToTop = settings.user.overview.Get('overviewBroadcastsToTop', False)
                fleetBroadcasts = fleetSvc.GetCurrentFleetBroadcasts()

                def GetSortValue(_node):
                    if broadcastsToTop:
                        if _node.itemID in fleetBroadcasts:
                            return (1, _node.sortValue)
                        else:
                            return (2, _node.sortValue)
                    return _node.sortValue

                self.sr.scroll.ShowHint()
                if self.sortingFrozen:
                    newEntries.sort(key=lambda x: GetSortValue(x), reverse=not currentDirection)
                    self.sr.scroll.AddNodes(-1, newEntries)
                else:
                    sortValues = [ GetSortValue(x) for x in self.sr.scroll.sr.nodes ]
                    entriesAtIdx = defaultdict(list)
                    for entry in newEntries:
                        insertionIndex = bisect.bisect(sortValues, GetSortValue(entry))
                        entriesAtIdx[insertionIndex].append(entry)

                    insertionPoints = sorted(entriesAtIdx.keys(), reverse=True)
                    for insertionIdx in insertionPoints:
                        sortedGroup = sorted(entriesAtIdx[insertionIdx], key=GetSortValue, reverse=not currentDirection)
                        self.sr.scroll.AddNodes(insertionIdx, sortedGroup)

    def OnUIScalingChange(self, *args):
        self.FullReload()

    def OnStateChange(self, itemID, flag, newState, *args):
        node = self._scrollNodesByItemID.get(itemID, None)
        if node and node.panel:
            node.panel.OnStateChange(itemID, flag, newState, *args)

    def OnFleetStateChange(self, fleetState):
        if fleetState:
            for itemID, tag in fleetState.targetTags.iteritems():
                node = self._scrollNodesByItemID.get(itemID, None)
                if node is None:
                    continue
                node.display_TAG = tag
                if node.sortTagIndex is not None:
                    if tag:
                        node.sortValue[node.sortTagIndex] = tag.lower()
                    else:
                        node.sortValue[node.sortTagIndex] = 0

    def OnSlimItemChange(self, oldSlim, newSlim):
        node = self._scrollNodesByItemID.get(oldSlim.itemID, None)
        if node:
            node.slimItem = _weakref.ref(newSlim)
            node.iconColor = None
            self.PrimeDisplayName(node)
            self.UpdateIconAndBackgroundFlagsOnNode(node)

    def ProcessBountyInfoUpdated(self, itemIDs):
        for itemID in itemIDs:
            node = self._scrollNodesByItemID.get(itemID, None)
            if node is not None:
                self.UpdateIconAndBackgroundFlagsOnNode(node)

    def FlushEwarStates(self):
        if self.jammers:
            currentSourceIDs = self.jammers.keys()
            self.jammers = {}
            for sourceBallID in currentSourceIDs:
                self.UpdateEwarStateOnItemID(sourceBallID)

    def OnEwarStart(self, sourceBallID, moduleID, targetBallID, jammingType):
        if targetBallID != session.shipid:
            return
        if not jammingType:
            return
        if not hasattr(self, 'jammers'):
            self.jammers = {}
        jammingID = sm.StartService('state').GetEwarGraphicID(jammingType)
        if not self.jammers.has_key(sourceBallID):
            self.jammers[sourceBallID] = {}
        if not self.jammers[sourceBallID].has_key(jammingID):
            self.jammers[sourceBallID][jammingID] = {}
        self.jammers[sourceBallID][jammingID][moduleID] = True
        self.UpdateEwarStateOnItemID(sourceBallID)

    def OnEwarEnd(self, sourceBallID, moduleID, targetBallID, jammingType):
        if targetBallID != session.shipid:
            return
        if not jammingType:
            return
        if not hasattr(self, 'jammers'):
            return
        jammingID = sm.StartService('state').GetEwarGraphicID(jammingType)
        if not self.jammers.has_key(sourceBallID) or not self.jammers[sourceBallID].has_key(jammingID) or not self.jammers[sourceBallID][jammingID].has_key(moduleID):
            return
        del self.jammers[sourceBallID][jammingID][moduleID]
        if self.jammers[sourceBallID][jammingID] == {}:
            del self.jammers[sourceBallID][jammingID]
        self.UpdateEwarStateOnItemID(sourceBallID)

    def UpdateEwarStateOnItemID(self, itemID):
        node = self._scrollNodesByItemID.get(itemID, None)
        if node is None:
            return
        node.ewarGraphicIDs = self.GetEwarDataForNode(node)
        if node.panel:
            node.panel.UpdateEwar()

    def GetEwarDataForNode(self, node):
        if node.itemID not in self.jammers:
            return
        jammersOnItem = self.jammers.get(node.itemID, None)
        if not jammersOnItem:
            return
        ewarFilters = sm.GetService('tactical').GetEwarFiltered()
        ret = []
        for jamType, (flag, graphicID) in self.ewarTypes:
            if jamType in ewarFilters:
                continue
            if graphicID in jammersOnItem:
                ret.append(graphicID)

        return ret

    def OnTacticalPresetChange(self, label, preset):
        if label == 'ccp_notsaved':
            label = localization.GetByLabel('UI/Overview/NotSaved')
        overviewName = sm.GetService('overviewPresetSvc').GetDefaultOverviewName(label)
        if overviewName is not None:
            label = overviewName
        self.sr.presetMenu.hint = label
        self.SetCaption(localization.GetByLabel('UI/Tactical/OverviewCaption', preset=label))
        self.FlagScrollEntriesAndBallparkDirty_InstantUpdate('OnTacticalPresetChange')

    def OnPostCfgDataChanged(self, what, data):
        if what == 'evelocations':
            itemID = data[0]
            if itemID in self._scrollNodesByItemID:
                node = self._scrollNodesByItemID[itemID]
                self.PrimeDisplayName(node)

    def PrimeDisplayName(self, node):
        slimItem = node.slimItem()
        if not slimItem:
            return
        name = uix.GetSlimItemName(slimItem)
        if slimItem.groupID == const.groupStation:
            name = uix.EditStationName(name, usename=0)
        if node.usingLocalizationTooltips:
            name, hint = self.PrepareLocalizationTooltip(name)
            node.hint_NAME = hint
        node.display_NAME = self.Encode(name)
        if node.sortNameIndex is not None:
            node.sortValue[node.sortNameIndex] = name.lower()

    def Encode(self, text):
        return re.sub(HTML_ENTITIES, lambda match: HTML_ENTITY_REPLACEMENTS[match.group()], text)

    def PrepareLocalizationTooltip(self, text):
        localizedTags = uicls.Label.ExtractLocalizedTags(text)
        if localizedTags:
            hint = localizedTags[0].get('hint', None)
            text = uiutil.StripTags(text)
        else:
            hint = None
        return (text, hint)

    def OnDestinationSet(self, *etc):
        for node in self.sr.scroll.sr.nodes:
            slimItem = node.slimItem()
            if not slimItem or slimItem.groupID not in (const.groupStargate, const.groupStation):
                continue
            node.iconColor = None

    def OnContactChange(self, contactIDs, contactType = None):
        self.FlagBallparkDirty()

    def OnFleetJoin_Local(self, member, *args):
        self.UpdateFleetMemberOrFlagDirty(member)
        self.FlagBallparkDirty()

    def OnFleetLeave_Local(self, member, *args):
        self.UpdateFleetMemberOrFlagDirty(member)
        self.FlagBallparkDirty()

    def UpdateFleetMemberOrFlagDirty(self, member):
        if member.charID == session.charid:
            self.FlagScrollEntriesDirty('UpdateFleetMemberOrFlagDirty')
        else:
            slimItem = self.GetSlimItemForCharID(member.charID)
            if slimItem and slimItem.itemID in self._scrollNodesByItemID:
                node = self._scrollNodesByItemID[slimItem.itemID]
                self.UpdateIconAndBackgroundFlagsOnNode(node)

    @telemetry.ZONE_METHOD
    def UpdateAllIconAndBackgroundFlags(self):
        stateSvc = sm.GetService('state')
        for node in self.sr.scroll.sr.nodes:
            if node.updateItem:
                self.UpdateIconAndBackgroundFlagsOnNode(node)
            else:
                slimItem = node.slimItem()
                if slimItem is not None:
                    if slimItem.groupID in const.containerGroupIDs:
                        node.iconColor = None
                        if node.panel is not None:
                            node.panel.UpdateIconColor()

    @telemetry.ZONE_METHOD
    def UpdateIconAndBackgroundFlagsOnNode(self, node):
        slimItem = node.slimItem()
        if slimItem is None:
            return
        iconFlag, backgroundFlag = (0, 0)
        if node.updateItem:
            iconFlag, backgroundFlag = sm.GetService('state').GetIconAndBackgroundFlags(slimItem)
        node.iconAndBackgroundFlags = (iconFlag, backgroundFlag)
        if node.sortIconIndex is not None:
            iconFlag, backgroundFlag = node.iconAndBackgroundFlags
            node.iconColor, colorSortValue = bracketUtils.GetIconColor(slimItem, getSortValue=True)
            node.sortValue[node.sortIconIndex] = [iconFlag,
             colorSortValue,
             backgroundFlag,
             slimItem.categoryID,
             slimItem.groupID,
             slimItem.typeID]
        if node.panel:
            node.panel.UpdateFlagAndBackground(slimItem)

    def OnOverviewTabChanged(self, tabsettings, oldtabsettings):
        if tabsettings == None:
            tabsettings = settings.user.overview.Get('tabsettings', {})
        newtabsettings = {}
        for key, setting in tabsettings.iteritems():
            newtabsettings[key] = setting

        settings.user.overview.Set('tabsettings', newtabsettings)
        presets = settings.user.overview.Get('overviewPresets', {})
        tabs = []
        if len(tabsettings.keys()) == 0:
            overviewPreset = settings.user.overview.Get('activeOverviewPreset', None)
            if not overviewPreset:
                overviewPreset = 'default'
            tabs.append([localization.GetByLabel('UI/Generic/Default'),
             self.sr.scroll,
             self,
             (overviewPreset,
              None,
              localization.GetByLabel('UI/Generic/Default'),
              0),
             self.sr.scroll])
            if not tabsettings:
                settings.user.overview.Set('tabsettings', {0: {'overview': overviewPreset,
                     'bracket': None,
                     'name': localization.GetByLabel('UI/Generic/Default')}})
        else:
            for key in tabsettings.keys():
                bracketSettings = tabsettings[key].get('bracket', None)
                overviewSettings = tabsettings[key].get('overview', None)
                tabName = tabsettings[key].get('name', None)
                tabs.append([tabsettings[key]['name'],
                 self.sr.scroll,
                 self,
                 (overviewSettings,
                  bracketSettings,
                  tabName,
                  key),
                 self.sr.scroll])

        if getattr(self, 'maintabs', None):
            self.maintabs.Close()
        self.maintabs = uicls.TabGroup(name='tabparent', align=uiconst.TOTOP, parent=self.sr.main, tabs=tabs, groupID='overviewTabs', idx=0)

    def OnStateSetupChance(self, reason = None):
        self.FlagScrollEntriesDirty('OnStateSetupChance')

    def GetSlimItemForCharID(self, charID):
        ballpark = sm.GetService('michelle').GetBallpark()
        if ballpark:
            for rec in ballpark.slimItems.itervalues():
                if rec.charID == charID:
                    return rec

    def GetTabMenu(self, tab, *args):
        presets = settings.user.overview.Get('overviewPresets', {}).keys()
        overviewm = []
        bracketm = []
        ret = []
        isSelected = tab.IsSelected()
        tabName = tab.sr.args[2]
        tabKey = tab.sr.args[3]
        bracketm.append(('', (localization.GetByLabel('UI/Overview/ShowAllBrackets'), self.ChangeBracketInTab, (None, isSelected, tabKey))))
        for key in presets:
            label = key
            if key == 'ccp_notsaved':
                overviewm.append(('', (localization.GetByLabel('UI/Overview/NotSaved'), self.ChangeOverviewInTab, (key, isSelected, tabKey))))
                bracketm.append((' ', (localization.GetByLabel('UI/Overview/NotSaved'), self.ChangeBracketInTab, (key, isSelected, tabKey))))
            else:
                overviewName = sm.GetService('overviewPresetSvc').GetDefaultOverviewName(label)
                lowerLabel = label.lower()
                if overviewName is not None:
                    overviewm.append((lowerLabel, (overviewName, self.ChangeOverviewInTab, (key, isSelected, tabKey))))
                    bracketm.append((lowerLabel, (overviewName, self.ChangeBracketInTab, (key, isSelected, tabKey))))
                else:
                    overviewm.append((lowerLabel, (label, self.ChangeOverviewInTab, (key, isSelected, tabKey))))
                    bracketm.append((lowerLabel, (label, self.ChangeBracketInTab, (key, isSelected, tabKey))))

        overviewm = [ x[1] for x in localizationUtil.Sort(overviewm, key=lambda x: x[0]) ]
        bracketm = [ x[1] for x in localizationUtil.Sort(bracketm, key=lambda x: x[0]) ]
        ret = []
        ret.append((localization.GetByLabel('/Carbon/UI/Controls/ScrollEntries/ChangeLabel'), self.ChangeTabName, (tabName, tabKey)))
        ret.append((localization.GetByLabel('UI/Overview/LoadOverviewProfile'), overviewm))
        ret.append((localization.GetByLabel('UI/Overview/LoadBracketProfile'), bracketm))
        ret.append((localization.GetByLabel('UI/Overview/DeleteTab'), self.DeleteTab, (tabKey, isSelected)))
        ret.append((localization.GetByLabel('UI/Overview/AddTab'), self.AddTab))
        return ret

    def ChangeTabName(self, tabName, tabKey):
        ret = uiutil.NamePopup(localization.GetByLabel('/Carbon/UI/Controls/ScrollEntries/ChangeLabel'), localization.GetByLabel('UI/Overview/TypeInLabel'), tabName, maxLength=30)
        if not ret:
            return
        tabsettings = settings.user.overview.Get('tabsettings', {})
        newTabName = ret
        if tabsettings.has_key(tabKey):
            oldtabsettings = tabsettings
            tabsettings[tabKey]['name'] = newTabName
            self.OnOverviewTabChanged(tabsettings, oldtabsettings)

    def ChangeOverviewInTab(self, overviewLabel, isSelected, tabKey):
        tabsettings = settings.user.overview.Get('tabsettings', {})
        if tabsettings.has_key(tabKey):
            oldtabsettings = tabsettings
            tabsettings[tabKey]['overview'] = overviewLabel
            self.OnOverviewTabChanged(tabsettings, oldtabsettings)
            if isSelected:
                sm.GetService('tactical').LoadPreset(overviewLabel, False)

    def ChangeBracketInTab(self, bracketLabel, isSelected, tabKey):
        tabsettings = settings.user.overview.Get('tabsettings', {})
        if tabsettings.has_key(tabKey):
            oldtabsettings = tabsettings
            tabsettings[tabKey]['bracket'] = bracketLabel
            self.OnOverviewTabChanged(tabsettings, oldtabsettings)
            if isSelected:
                sm.GetService('tactical').LoadBracketPreset(bracketLabel)

    def DeleteTab(self, tabKey, isSelected):
        oldtabsettings = settings.user.overview.Get('tabsettings', {})
        if not oldtabsettings.has_key(tabKey):
            return
        newtabsettings = {}
        i = 0
        for key, dictItem in oldtabsettings.iteritems():
            if key == tabKey:
                continue
            newtabsettings[i] = dictItem
            i += 1

        self.OnOverviewTabChanged(newtabsettings, oldtabsettings)

    def AddTab(self):
        ret = uiutil.NamePopup(localization.GetByLabel('UI/Overview/AddTab'), localization.GetByLabel('UI/Overview/TypeInLabel'), maxLength=15)
        if not ret:
            return
        numTabs = 5
        tabsettings = settings.user.overview.Get('tabsettings', {})
        if len(tabsettings) >= numTabs:
            eve.Message('TooManyTabs', {'numTabs': numTabs})
            return
        if len(tabsettings) == 0:
            newKey = 0
        else:
            newKey = max(tabsettings.keys()) + 1
        oldtabsettings = tabsettings
        tabsettings[newKey] = {'name': ret,
         'overview': None,
         'bracket': None}
        if self.destroyed:
            return
        self.OnOverviewTabChanged(tabsettings, oldtabsettings)

    def PostStartup(self):
        self.SetHeaderIcon()
        hicon = self.sr.headerIcon
        hicon.GetMenu = self.GetPresetsMenu
        hicon.expandOnLeft = 1
        hicon.hint = localization.GetByLabel('UI/Overview/OverviewTypePresets')
        hicon.name = 'overviewHeaderIcon'
        self.sr.presetMenu = hicon
        main = self.GetMainArea()
        main.padding = 0
        scroll = uicls.BasicDynamicScroll(name='overviewscroll2', align=uiconst.TOALL, parent=main, multiSelect=False, padding=4, autoPurgeHiddenEntries=False)
        scroll.OnSelectionChange = self.OnScrollSelectionChange
        scroll.OnChar = self.OnChar
        scroll.OnKeyUp = self.OnKeyUp
        self.columnHilites = []
        sortHeaders = uicls.SortHeaders(parent=scroll.sr.maincontainer, settingsID='overviewScroll2', idx=0)
        sortHeaders.SetDefaultColumn(COLUMN_DISTANCE, True)
        sortHeaders.OnColumnSizeChange = self.OnColumnSizeChanged
        sortHeaders.OnSortingChange = self.OnSortingChange
        sortHeaders.OnColumnSizeReset = self.OnColumnSizeReset
        self.sortHeaders = sortHeaders
        self.sr.scroll = scroll
        self.OnOverviewTabChanged(None, {})

    def OnSetActive_(self, *args):
        selected = self.sr.scroll.GetSelected()
        if selected is None:
            self.sr.scroll.SetSelected(0)

    def OnKeyUp(self, *args):
        selected = self.sr.scroll.GetSelected()
        if not selected:
            return
        uicore.cmd.ExecuteCombatCommand(selected[0].itemID, uiconst.UI_CLICK)

    def OnChar(self, *args):
        return False

    def LoadTabPanel(self, args, panel, tabgroup):
        tactical = sm.GetService('tactical')
        if len(args) > 2:
            tactical.LoadPreset(args[0], False)
            tabsettings = settings.user.overview.Get('tabsettings', {}).get(args[3], {})
            showSpecials = tabsettings.get('showSpecials', False)
            if tabsettings.get('showAll', False):
                bracketShowState = 1
            elif tabsettings.get('showNone', False):
                bracketShowState = -1
            else:
                bracketShowState = 0
            tactical.LoadBracketPreset(args[1], showSpecials=showSpecials, bracketShowState=bracketShowState)

    def UpdateColumnHilite(self):
        currentActive, currentDirection = self.sortHeaders.GetCurrentActive()
        if currentActive:
            columnWidths = self.sortHeaders.GetCurrentSizes()
            currentColumns = self.sortHeaders.GetCurrentColumns()
            for each in self.columnHilites[:len(currentColumns)]:
                each.Close()
                self.columnHilites.remove(each)

            prevline = None
            left = 0
            for columnIndex, columnID in enumerate(currentColumns):
                if len(self.columnHilites) > columnIndex:
                    hilite = self.columnHilites[columnIndex]
                else:
                    hilite = uicls.Fill(parent=self.sr.scroll.sr.clipper, align=uiconst.TOLEFT_NOPUSH, color=(1, 1, 1, 0.125))
                    self.columnHilites.append(hilite)
                columnWidth = columnWidths[columnID]
                left += columnWidth
                hilite.left = left - 1
                hilite.width = 1
                if columnID == currentActive:
                    hilite.left -= columnWidth
                    hilite.width = columnWidth + 1
                    if prevline:
                        prevline.state = uiconst.UI_HIDDEN
                prevline = hilite

        else:
            for each in self.columnHilites:
                each.Close()

            self.columnHilites = []

    def OnColumnSizeReset(self, columnID):
        useSmallText = settings.user.overview.Get('useSmallText', 0)
        if useSmallText:
            fontSize = fontConst.EVE_SMALL_FONTSIZE
        else:
            fontSize = fontConst.EVE_MEDIUM_FONTSIZE
        labelClass = uicls.OverviewLabel
        widths = [COLUMNMINSIZE - COLUMNMARGIN * 2]
        for node in self.sr.scroll.sr.nodes:
            displayValue = OverviewScrollEntry.GetColumnDisplayValue(node, columnID)
            if displayValue:
                textWidth, textHeight = labelClass.MeasureTextSize(displayValue, fontSize=fontSize)
                widths.append(textWidth)

        self.sortHeaders.SetColumnSize(columnID, max(widths) + COLUMNMARGIN * 2)
        self.TriggerInstantUpdate('OnColumnSizeReset')

    def OnColumnSizeChanged(self, columnID, headerWidth, currentSizes, *args):
        self.UpdateColumnHilite()
        self.TriggerInstantUpdate('OnColumnSizeChanged')

    def OnSortingChange(self, oldColumnID, columnID, oldSortDirection, sortDirection):
        if oldColumnID == columnID and oldSortDirection != sortDirection:
            self.TriggerInstantUpdate('OnSortingChange')
        else:
            self.FlagScrollEntriesDirty_InstantUpdate('OnSortingChange')

    def OnScrollSelectionChange(self, nodes, *args):
        if not nodes:
            return
        node = nodes[0]
        if node and node.itemID:
            sm.GetService('state').SetState(node.itemID, state.selected, 1)
            if sm.GetService('target').IsTarget(node.itemID):
                sm.GetService('state').SetState(node.itemID, state.activeTarget, 1)

    def GetPresetsMenu(self):
        return sm.GetService('tactical').GetPresetsMenu()

    def Cleanup(self):
        pass

    @telemetry.ZONE_METHOD
    def UpdateAll(self, *args, **kwds):
        pass

    @telemetry.ZONE_METHOD
    def FullReload(self):
        self.StopOverviewUpdate()
        self.sr.scroll.Clear()
        self._scrollNodesByItemID = {}
        self.FlagScrollEntriesAndBallparkDirty_InstantUpdate()

    def StopOverviewUpdate(self):
        if self.overviewUpdateThread:
            self.overviewUpdateThread.kill()
            self.overviewUpdateThread = None

    def TriggerInstantUpdate(self, fromFunction = None):
        self.StopOverviewUpdate()
        if self.IsCollapsed() or self.IsMinimized():
            return
        self.UpdateOverview()

    def FlagBallparkDirty(self, fromFunction = None):
        self._ballparkDirty = True
        if self.IsCollapsed() or self.IsMinimized():
            self.StopOverviewUpdate()
            return
        if not self.overviewUpdateThread:
            self.overviewUpdateThread = uthread.new(self.UpdateOverview)

    def FlagScrollEntriesAndBallparkDirty_InstantUpdate(self, fromFunction = None):
        self._ballparkDirty = True
        self._scrollEntriesDirty = True
        self.TriggerInstantUpdate('FlagScrollEntriesDirtyDirty_InstantUpdate')

    def FlagScrollEntriesDirty_InstantUpdate(self, fromFunction = None):
        self._scrollEntriesDirty = True
        self.TriggerInstantUpdate('FlagScrollEntriesDirtyDirty_InstantUpdate')

    def FlagScrollEntriesDirty(self, fromFunction = None):
        self._scrollEntriesDirty = True
        if self.IsCollapsed() or self.IsMinimized():
            self.StopOverviewUpdate()
            return
        if not self.overviewUpdateThread:
            self.overviewUpdateThread = uthread.new(self.UpdateOverview)

    @telemetry.ZONE_METHOD
    def UpdateStaticDataForNodes(self, nodeList):
        tacticalSvc = sm.GetService('tactical')
        fleetSvc = sm.GetService('fleet')
        factionSvc = sm.GetService('faction')
        stateSvc = sm.GetService('state')
        IsNPC = util.IsNPC
        usingLocalizationTooltips = localization.UseImportantTooltip()
        useSmallColorTags = settings.user.overview.Get('useSmallColorTags', 0)
        useSmallText = settings.user.overview.Get('useSmallText', 0)
        if useSmallText:
            entryHeight = 17
            fontSize = fontConst.EVE_SMALL_FONTSIZE
        else:
            entryHeight = 19
            fontSize = fontConst.EVE_MEDIUM_FONTSIZE
        labelClass = uicls.OverviewLabel
        columns = tacticalSvc.GetColumns()
        columnWidths = self.sortHeaders.GetCurrentSizes()
        currentActive, currentDirection = self.sortHeaders.GetCurrentActive()
        if currentActive:
            sortKeys = columns[columns.index(currentActive):]
        else:
            sortKeys = []
        columnSettings = {}
        for columnID in ALLCOLUMNS:
            if columnID in columns:
                if columnID in sortKeys:
                    columnSettings[columnID] = (True, sortKeys.index(columnID))
                else:
                    columnSettings[columnID] = (True, None)
            else:
                columnSettings[columnID] = (False, None)

        showIcon, sortIconIndex = columnSettings[COLUMN_ICON]
        showName, sortNameIndex = columnSettings[COLUMN_NAME]
        showDistance, sortDistanceIndex = columnSettings[COLUMN_DISTANCE]
        showSize, sortSizeIndex = columnSettings[COLUMN_SIZE]
        showAlliance, sortAllianceIndex = columnSettings[COLUMN_ALLIANCE]
        showType, sortTypeIndex = columnSettings[COLUMN_TYPE]
        showTag, sortTagIndex = columnSettings[COLUMN_TAG]
        showCorporation, sortCorporationIndex = columnSettings[COLUMN_CORPORATION]
        showFaction, sortFactionIndex = columnSettings[COLUMN_FACTION]
        showMilitia, sortMilitiaIndex = columnSettings[COLUMN_MILITIA]
        showVelocity, sortVelocityIndex = columnSettings[COLUMN_VELOCITY]
        showRadialVelocity, sortRadialVelocityIndex = columnSettings[COLUMN_RADIALVELOCITY]
        showAngularVelocity, sortAngularVelocityIndex = columnSettings[COLUMN_ANGULARVELOCITY]
        showTransversalVelocity, sortTransversalVelocityIndex = columnSettings[COLUMN_TRANSVERSALVELOCITY]
        showVelocityCombined = showVelocity or showRadialVelocity or showAngularVelocity or showTransversalVelocity
        defaultSortValue = [ 0 for each in sortKeys ]
        inFleet = bool(session.fleetid)
        for node in nodeList:
            slimItem = node.slimItem()
            ball = node.ball()
            if not (ball and slimItem):
                node.leavingOverview = True
                if node.itemID in self._scrollNodesByItemID:
                    del self._scrollNodesByItemID[node.itemID]
                continue
            self._scrollNodesByItemID[node.itemID] = node
            node.usingLocalizationTooltips = usingLocalizationTooltips
            node.useSmallText = useSmallText
            node.useSmallColorTags = useSmallColorTags
            node.decoClass.ENTRYHEIGHT = entryHeight
            node.fontSize = fontSize
            node.columns = columns
            node.columnWidths = columnWidths
            node.sortNameIndex = sortNameIndex
            node.sortDistanceIndex = sortDistanceIndex
            node.sortIconIndex = sortIconIndex
            node.sortTagIndex = sortTagIndex
            node.sortVelocityIndex = sortVelocityIndex
            node.sortRadialVelocityIndex = sortRadialVelocityIndex
            node.sortAngularVelocityIndex = sortAngularVelocityIndex
            node.sortTransversalVelocityIndex = sortTransversalVelocityIndex
            sortValue = defaultSortValue[:]
            node.sortValue = sortValue
            if node.display_NAME is None:
                self.PrimeDisplayName(node)
            elif sortNameIndex is not None:
                sortValue[sortNameIndex] = node.display_NAME.lower()
            if showType and slimItem.typeID:
                if node.display_TYPE is None:
                    typeName = cfg.invtypes.Get(slimItem.typeID).typeName
                    if usingLocalizationTooltips:
                        typeName, hint = self.PrepareLocalizationTooltip(typeName)
                        node.hint_TYPE = hint
                    node.display_TYPE = typeName
                if sortTypeIndex is not None:
                    sortValue[sortTypeIndex] = node.display_TYPE.lower()
            if showSize:
                size = ball.radius * 2
                if node.display_SIZE is None:
                    node.display_SIZE = util.FmtDist(size)
                if sortSizeIndex is not None:
                    sortValue[sortSizeIndex] = size
            if showTag:
                if inFleet:
                    if node.display_TAG is None:
                        node.display_TAG = fleetSvc.GetTargetTag(node.itemID)
                else:
                    node.display_TAG = ''
                if sortTagIndex is not None:
                    tag = node.display_TAG
                    if tag:
                        sortValue[sortTagIndex] = tag.lower()
                    else:
                        sortValue[sortTagIndex] = 0
            if showCorporation and slimItem.corpID:
                node.display_CORPORATION = corpTag = '[' + cfg.corptickernames.Get(slimItem.corpID).tickerName + ']'
                if sortCorporationIndex is not None:
                    sortValue[sortCorporationIndex] = corpTag.lower()
            if showMilitia and slimItem.warFactionID:
                militia = cfg.eveowners.Get(slimItem.warFactionID).name
                if usingLocalizationTooltips:
                    militia, hint = self.PrepareLocalizationTooltip(militia)
                    node.hint_MILITIA = hint
                node.display_MILITIA = militia
                if sortMilitiaIndex is not None:
                    sortValue[sortMilitiaIndex] = militia.lower()
            if showAlliance and slimItem.allianceID:
                node.display_ALLIANCE = alliance = '[' + cfg.allianceshortnames.Get(slimItem.allianceID).shortName + ']'
                if sortAllianceIndex is not None:
                    sortValue[sortAllianceIndex] = alliance.lower()
            if showFaction:
                if slimItem.ownerID and IsNPC(slimItem.ownerID) or slimItem.charID and IsNPC(slimItem.charID):
                    factionID = factionSvc.GetFaction(slimItem.ownerID or slimItem.charID)
                    if factionID:
                        faction = cfg.eveowners.Get(factionID).name
                        if usingLocalizationTooltips:
                            faction, hint = self.PrepareLocalizationTooltip(faction)
                            node.hint_FACTION = hint
                        node.display_FACTION = faction
                        if sortFactionIndex is not None:
                            sortValue[sortFactionIndex] = faction.lower()
            if node.iconAndBackgroundFlags is None:
                iconFlag, backgroundFlag = (0, 0)
                if node.updateItem:
                    iconFlag, backgroundFlag = stateSvc.GetIconAndBackgroundFlags(slimItem)
                node.iconAndBackgroundFlags = (iconFlag, backgroundFlag)
            if sortIconIndex is not None:
                iconFlag, backgroundFlag = node.iconAndBackgroundFlags
                node.iconColor, colorSortValue = bracketUtils.GetIconColor(slimItem, getSortValue=True)
                sortValue[sortIconIndex] = [iconFlag,
                 colorSortValue,
                 backgroundFlag,
                 slimItem.categoryID,
                 slimItem.groupID,
                 slimItem.typeID]

    @telemetry.ZONE_METHOD
    def UpdateDynamicDataForNodes(self, nodeList, doYield = False):
        tacticalSvc = sm.GetService('tactical')
        bp = sm.GetService('michelle').GetBallpark(doWait=True)
        if not bp:
            self.FlagBallparkDirty('DoBallsAdded')
            return
        myBall = bp.GetBall(eve.session.shipid)
        GetInvItem = bp.GetInvItem
        UpdateVelocityData = self.UpdateVelocityData
        columns = tacticalSvc.GetColumns()
        showVelocityCombined = False
        showDistance = COLUMN_DISTANCE in columns
        showIcon = COLUMN_ICON in columns
        calculateRadialVelocity = False
        calculateCombinedVelocity = False
        calculateRadialNormal = False
        calculateTransveralVelocity = False
        calculateAngularVelocity = False
        calculateVelocity = False
        if COLUMN_VELOCITY in columns:
            calculateVelocity = True
            showVelocityCombined = True
        if COLUMN_ANGULARVELOCITY in columns:
            calculateRadialVelocity = True
            calculateCombinedVelocity = True
            calculateRadialNormal = True
            calculateTransveralVelocity = True
            calculateAngularVelocity = True
            showVelocityCombined = True
        if COLUMN_TRANSVERSALVELOCITY in columns:
            calculateRadialVelocity = True
            calculateCombinedVelocity = True
            calculateRadialNormal = True
            calculateTransveralVelocity = True
            showVelocityCombined = True
        if COLUMN_RADIALVELOCITY in columns:
            calculateRadialVelocity = True
            calculateCombinedVelocity = True
            calculateRadialNormal = True
            showVelocityCombined = True
        now = blue.os.GetSimTime()
        counter = 0
        for node in nodeList:
            ball = node.ball()
            slimItem = node.slimItem()
            if not slimItem:
                slimItem = GetInvItem(node.itemID)
                if slimItem:
                    node.slimItem = _weakref.ref(slimItem)
                    node.iconColor = None
                    self.PrimeDisplayName(node)
                    if node.panel:
                        if showIcon:
                            node.panel.UpdateIcon()
                            node.panel.UpdateIconColor()
                    self.UpdateIconAndBackgroundFlagsOnNode(node)
            if ball:
                if showDistance:
                    ball.GetVectorAt(now)
                    node.rawDistance = rawDistance = max(ball.surfaceDist, 0)
                    if node.sortDistanceIndex is not None:
                        node.sortValue[node.sortDistanceIndex] = rawDistance
                if showVelocityCombined and node.updateItem and ball.isFree and myBall:
                    ball.GetVectorAt(now)
                    UpdateVelocityData(node, ball, myBall, calculateVelocity, calculateRadialVelocity, calculateCombinedVelocity, calculateRadialNormal, calculateTransveralVelocity, calculateAngularVelocity)
            if doYield:
                counter += 1
                if counter == 20:
                    blue.pyos.BeNice(100)
                    if self.destroyed:
                        self.StopOverviewUpdate()
                        return
                    counter = 0

    @telemetry.ZONE_METHOD
    def CheckForNewEntriesAndRefreshScrollSetup(self):
        ballpark = sm.GetService('michelle').GetBallpark(doWait=True)
        if ballpark is None:
            return
        tacticalSvc = sm.GetService('tactical')
        columns = tacticalSvc.GetColumns()
        self.sortHeaders.CreateColumns(columns, fixedColumns=FIXEDCOLUMNS)
        self.UpdateColumnHilite()
        newEntries = []
        currentNotWanted = set()
        with ScrollListLock:
            if self._ballparkDirty:
                factionSvc = sm.GetService('faction')
                stateSvc = sm.GetService('state')
                filterGroups = tacticalSvc.GetValidGroups()
                filteredStates = tacticalSvc.GetFilteredStatesFunctionNames()
                CheckIfFilterItem = stateSvc.CheckIfFilterItem
                CheckFiltered = tacticalSvc.CheckFiltered
                CheckIfUpdateItem = stateSvc.CheckIfUpdateItem
                GetInvItem = ballpark.GetInvItem
                GetBall = ballpark.GetBall
                currentItemIDs = self._scrollNodesByItemID
                log.LogInfo('Overview - Checking ballpark for new entries')
                for itemID in ballpark.balls.keys():
                    slimItem = GetInvItem(itemID)
                    if not slimItem or slimItem.groupID not in filterGroups or itemID == eve.session.shipid or CheckIfFilterItem(slimItem) and CheckFiltered(slimItem, filteredStates):
                        if itemID in currentItemIDs:
                            currentNotWanted.add(itemID)
                            if itemID in self._scrollNodesByItemID:
                                node = self._scrollNodesByItemID[itemID]
                                node.leavingOverview = True
                                del self._scrollNodesByItemID[itemID]
                        continue
                    if itemID not in currentItemIDs:
                        updateItem = CheckIfUpdateItem(slimItem)
                        data = {'itemID': itemID,
                         'updateItem': updateItem}
                        newNode = listentry.Get('OverviewScrollEntry', data)
                        ball = GetBall(itemID)
                        newNode.ball = _weakref.ref(ball)
                        newNode.slimItem = _weakref.ref(slimItem)
                        if updateItem:
                            newNode.ewarGraphicIDs = self.GetEwarDataForNode(newNode)
                            newNode.ewarHints = self.ewarHintsByGraphicID
                        newEntries.append(newNode)

            nodeList = newEntries[:]
            if self._scrollEntriesDirty:
                log.LogInfo('Overview - Update static data on current overview entries')
                nodeList.extend([ node for node in self.sr.scroll.sr.nodes if node.itemID not in currentNotWanted ])
            self.UpdateStaticDataForNodes(nodeList)
            self.sr.scroll.PurgeInvisibleEntries()
            self.overviewSorted = False
            if newEntries:
                self.sr.scroll.ShowHint()
                self.sr.scroll.AddNodes(-1, newEntries)
        return newEntries

    @telemetry.ZONE_METHOD
    def UpdateOverview(self, doYield = False):
        if self.destroyed:
            return
        if self._ballparkDirty or self._scrollEntriesDirty:
            newEntries = self.CheckForNewEntriesAndRefreshScrollSetup()
            if newEntries:
                doYield = False
            self._ballparkDirty = False
            self._scrollEntriesDirty = False
        updateStartTime = blue.os.GetWallclockTimeNow()
        try:
            if not eve.session.solarsystemid:
                self.StopOverviewUpdate()
                return
            if self.IsCollapsed() or self.IsMinimized():
                self.StopOverviewUpdate()
                return
            if self.destroyed:
                return
            bp = sm.GetService('michelle').GetBallpark(doWait=True)
            if not bp:
                self.StopOverviewUpdate()
                return
            tacticalSvc = sm.GetService('tactical')
            stateSvc = sm.StartService('state')
            fleetSvc = sm.GetService('fleet')
            columns = tacticalSvc.GetColumns()
            columnWidths = self.sortHeaders.GetCurrentSizes()
            UpdateVelocityData = self.UpdateVelocityData
            myBall = bp.GetBall(eve.session.shipid)
            showIcon = COLUMN_ICON in columns
            broadcastsToTop = settings.user.overview.Get('overviewBroadcastsToTop', False)
            fleetBroadcasts = fleetSvc.GetCurrentFleetBroadcasts()
            mouseCoords = trinity.GetCursorPos()
            if mouseCoords != self.prevMouseCoords:
                self.lastMovementTime = blue.os.GetWallclockTime()
                self.prevMouseCoords = mouseCoords
            insider = uiutil.IsUnder(uicore.uilib.mouseOver, self.sr.scroll.GetContentContainer()) or uicore.uilib.mouseOver is self.sr.scroll.GetContentContainer()
            mouseMoving = blue.os.TimeDiffInMs(self.lastMovementTime, blue.os.GetWallclockTime()) > self.mouseMovementTimeout
            mouseInsideApp = mouseCoords[0] > 0 and mouseCoords[0] < trinity.app.width and mouseCoords[1] > 0 and mouseCoords[1] < trinity.app.height
            sortingFrozen = self.sortingFrozen = insider and mouseInsideApp and not mouseMoving or self._freezeOverview
            if sortingFrozen:
                updateList = self.sr.scroll.GetVisibleNodes()
                self.sortHeaders.SetSortIcon('res:/UI/Texture/classes/Overview/columnLock.png')
            else:
                updateList = self.sr.scroll.sr.nodes
                self.sortHeaders.SetSortIcon(None)

            def GetSortValue(_node):
                if broadcastsToTop:
                    if _node.itemID in fleetBroadcasts:
                        return (1, _node.sortValue)
                    else:
                        return (2, _node.sortValue)
                return _node.sortValue

            ballpark = sm.GetService('michelle').GetBallpark(doWait=True)
            if ballpark is None:
                return
            GetInvItem = ballpark.GetInvItem
            self.UpdateDynamicDataForNodes(updateList, doYield=doYield)
            counter = 0
            nodesToRemove = []
            for node in updateList:
                node.columnWidths = columnWidths
                if node.leavingOverview:
                    if node.panel:
                        node.panel.opacity = 0.25
                        node.panel.state = uiconst.UI_DISABLED
                    nodesToRemove.append(node)
                    continue
                ball = node.ball()
                slimItem = node.slimItem()
                if not (slimItem and ball):
                    node.leavingOverview = True
                    if node.itemID in self._scrollNodesByItemID:
                        del self._scrollNodesByItemID[node.itemID]
                    if node.panel:
                        node.panel.opacity = 0.25
                        node.panel.state = uiconst.UI_DISABLED
                    nodesToRemove.append(node)
                    continue
                if doYield:
                    counter += 1
                    if counter == 20:
                        blue.pyos.BeNice(100)
                        if self.destroyed:
                            self.StopOverviewUpdate()
                            return
                        counter = 0

            if doYield:
                blue.synchro.Yield()
                if self.destroyed:
                    self.StopOverviewUpdate()
                    return
            if not sortingFrozen:
                if nodesToRemove:
                    self.sr.scroll.RemoveNodes(nodesToRemove)
                currentActive, currentDirection = self.sortHeaders.GetCurrentActive()
                with ScrollListLock:
                    sortlist = sorted(self.sr.scroll.sr.nodes, key=GetSortValue, reverse=not currentDirection)
                    self.sr.scroll.SetOrderedNodes(sortlist, loadNodes=False)
                self.overviewSorted = True
            else:
                self.overviewSorted = False
            counter = 0
            for node in self.sr.scroll.GetVisibleNodes():
                if node.panel and node.panel.state != uiconst.UI_HIDDEN:
                    node.panel.Load(node)
                    counter += 1
                    if counter == 10:
                        blue.pyos.BeNice(100)
                        if self.destroyed:
                            self.StopOverviewUpdate()
                            return
                        counter = 0

            if not self.sr.scroll.sr.nodes:
                self.sr.scroll.ShowHint(localization.GetByLabel('UI/Common/NothingFound'))
            else:
                self.sr.scroll.ShowHint()
        except Exception:
            log.LogException(extraText='Error updating inflight overview')
            sys.exc_clear()

        if doYield:
            diff = blue.os.TimeDiffInMs(updateStartTime, blue.os.GetWallclockTimeNow())
            sleep = max(self.minUpdateSleep, self.maxUpdateSleep - diff)
            blue.pyos.synchro.SleepWallclock(sleep)
        if not self.destroyed and (not self.overviewUpdateThread or self.overviewUpdateThread == stackless.getcurrent()):
            self.overviewUpdateThread = uthread.new(self.UpdateOverview, doYield=True)

    def SetFreezeOverview(self, freeze = True):
        triggerUpdate = False
        if not freeze and freeze != self._freezeOverview:
            triggerUpdate = True
        self._freezeOverview = freeze
        if triggerUpdate and getattr(self, 'overviewSorted', False) is False:
            self.TriggerInstantUpdate('SetFreezeOverview')

    def UpdateForOneCharacter(self, charID, *args):
        pass

    def OnExpanded(self, *args):
        self.TriggerInstantUpdate('OnExpanded')

    def OnCollapsed(self, *args):
        self.StopOverviewUpdate()
        self.cachedScrollPos = self.sr.scroll.GetScrollProportion()

    def OnEndMaximize_(self, *args):
        self.TriggerInstantUpdate('OnEndMaximize_')

    def OnEndMinimize_(self, *args):
        self.StopOverviewUpdate()
        self.cachedScrollPos = self.sr.scroll.GetScrollProportion()

    @telemetry.ZONE_METHOD
    def UpdateVelocityData(self, node, ball, myBall, calculateVelocity, calculateRadialVelocity, calculateCombinedVelocity, calculateRadialNormal, calculateTransveralVelocity, calculateAngularVelocity):
        surfaceDist = max(ball.surfaceDist, 0)
        velocity = None
        radialVelocity = None
        angularVelocity = None
        transveralVelocity = None
        if calculateCombinedVelocity:
            CombVel4 = (ball.vx - myBall.vx, ball.vy - myBall.vy, ball.vz - myBall.vz)
        if calculateRadialNormal:
            RadNorm4 = geo2.Vec3Normalize((ball.x - myBall.x, ball.y - myBall.y, ball.z - myBall.z))
        if calculateVelocity:
            velocity = ball.GetVectorDotAt(blue.os.GetSimTime()).Length()
        if calculateRadialVelocity:
            radialVelocity = geo2.Vec3Dot(CombVel4, RadNorm4)
        if calculateTransveralVelocity:
            transveralVelocity = geo2.Vec3Length(geo2.Vec3Subtract(CombVel4, geo2.Vec3Scale(RadNorm4, radialVelocity)))
        if calculateAngularVelocity:
            angularVelocity = transveralVelocity / max(1.0, surfaceDist)
        node.rawVelocity = velocity
        node.rawRadialVelocity = radialVelocity
        node.rawAngularVelocity = angularVelocity
        node.rawTransveralVelocity = transveralVelocity
        if node.sortVelocityIndex is not None:
            node.sortValue[node.sortVelocityIndex] = velocity
        if node.sortRadialVelocityIndex is not None:
            node.sortValue[node.sortRadialVelocityIndex] = radialVelocity
        if node.sortAngularVelocityIndex is not None:
            node.sortValue[node.sortAngularVelocityIndex] = angularVelocity
        if node.sortTransversalVelocityIndex is not None:
            node.sortValue[node.sortTransversalVelocityIndex] = transveralVelocity

    def GetSelectedTabArgs(self):
        if hasattr(self, 'maintabs'):
            return self.maintabs.GetSelectedArgs()

    def GetSelectedTabKey(self):
        if hasattr(self, 'maintabs'):
            selectedArgs = self.maintabs.GetSelectedArgs()
            if selectedArgs is None:
                return
            else:
                return selectedArgs[3]

    def OnSessionChanged(self, isRemote, session, change):
        if self.destroyed:
            return
        if 'solarsystemid' in change:
            self.sr.scroll.Clear()
            self._scrollNodesByItemID = {}
        if 'shipid' in change:
            self.FlagBallparkDirty('OnSessionChanged')

    def OnTutorialHighlightItem(self, itemID, isActive):
        node = self._scrollNodesByItemID.get(itemID, None)
        if node is None:
            return
        if node.panel:
            node.panel.UpdateTutorialHighlight(isActive)


class OverviewLabel(uicls.VisibleBase):
    __guid__ = 'uicls.OverviewLabel'
    __renderObject__ = trinity.Tr2Sprite2dTextObject
    default_name = 'OverviewLabel'
    default_color = None
    _text = None
    _columnWidth = None
    _columnPosition = 0
    _globalMaxWidth = None
    _columnWidthDirty = False

    def ApplyAttributes(self, attributes):
        uicls.VisibleBase.ApplyAttributes(self, attributes)
        self.fadeSize = self.ScaleDpi(COLUMNFADESIZE)
        self.rightAligned = False
        measurer = trinity.Tr2FontMeasurer()
        measurer.limit = 0
        measurer.fontSize = uicore.ScaleDpi(uicore.fontSizeFactor * attributes.fontSize)
        measurer.font = str(uicore.font.GetFontDefault())
        measurer.letterSpace = 0
        self.renderObject.fontMeasurer = measurer
        self.renderObject.shadowOffset = (0, 1)
        self.measurer = measurer

    def UpdateFade(self):
        measurer = self.measurer
        columnWidth = self.columnWidth
        if columnWidth:
            globalFade = False
            globalMaxWidth = self.globalMaxWidth
            if globalMaxWidth and globalMaxWidth - self.left < columnWidth:
                scaledMaxWidth = max(0, self.ScaleDpi(globalMaxWidth - self.left))
                globalFade = True
            elif self.rightAligned:
                scaledMaxWidth = measurer.cursorX
            else:
                scaledMaxWidth = self.ScaleDpi(columnWidth)
            if measurer.cursorX > scaledMaxWidth:
                maxFade = max(2, measurer.cursorX - scaledMaxWidth)
                if globalFade:
                    measurer.fadeRightStart = max(0, scaledMaxWidth - min(maxFade, self.fadeSize))
                    measurer.fadeRightEnd = scaledMaxWidth
                else:
                    measurer.fadeRightStart = measurer.cursorX + 1
                    measurer.fadeRightEnd = measurer.cursorX + 1
            else:
                measurer.fadeRightStart = measurer.cursorX + 1
                measurer.fadeRightEnd = measurer.cursorX + 1

    @apply
    def left():

        def fget(self):
            return self._left

        def fset(self, value):
            if value < 1.0:
                adjustedValue = value
            else:
                adjustedValue = int(round(value))
            if adjustedValue != self._left:
                self._left = adjustedValue
                self.FlagAlignmentDirty()
                self.UpdateFade()

        return property(**locals())

    @apply
    def width():

        def fget(self):
            return self._width

        def fset(self, value):
            if value < 1.0:
                adjustedValue = value
            else:
                adjustedValue = int(round(value))
            if adjustedValue != self._width:
                self._width = adjustedValue
                if self.rightAligned:
                    self.left = self.columnPosition + self.columnWidth - adjustedValue
                self.FlagAlignmentDirty()
                self.UpdateFade()

        return property(**locals())

    @apply
    def text():

        def fget(self):
            return self._text

        def fset(self, value):
            if self._text != value or self._columnWidthDirty:
                self._columnWidthDirty = False
                self._text = value
                if not value:
                    self.texture = None
                    self.spriteEffect = trinity.TR2_SFX_NONE
                    return
                measurer = self.measurer
                measurer.Reset()
                measurer.color = -1073741825
                if self.columnWidth:
                    measurer.limit = self.ScaleDpi(self.columnWidth)
                added = measurer.AddText(unicode(value))
                measurer.CommitText(0, measurer.ascender)
                if self.columnWidth:
                    self.width = min(self.columnWidth, self.ReverseScaleDpi(measurer.cursorX + 0.5))
                    self.renderObject.textWidth = min(self.ScaleDpi(self.columnWidth), measurer.cursorX)
                else:
                    self.width = self.ReverseScaleDpi(measurer.cursorX + 0.5)
                    self.renderObject.textWidth = measurer.cursorX
                self.height = self.ReverseScaleDpi(measurer.ascender - measurer.descender)
                self.renderObject.textHeight = measurer.ascender - measurer.descender

        return property(**locals())

    @apply
    def columnWidth():

        def fget(self):
            return self._columnWidth

        def fset(self, value):
            if self._columnWidth != value:
                self._columnWidth = value
                self._columnWidthDirty = True
                measurer = self.measurer
                self.width = min(value, self.ReverseScaleDpi(measurer.cursorX + 0.5))
                self.renderObject.textWidth = min(self.ScaleDpi(value), measurer.cursorX)
                if self.rightAligned:
                    self.left = self.columnPosition + value - self.width

        return property(**locals())

    @apply
    def columnPosition():

        def fget(self):
            return self._columnPosition

        def fset(self, value):
            if self._columnPosition != value:
                self._columnPosition = value
                if self.rightAligned:
                    self.left = value + self.columnWidth - self.width
                else:
                    self.left = value

        return property(**locals())

    @apply
    def globalMaxWidth():

        def fget(self):
            return self._globalMaxWidth

        def fset(self, value):
            if self._globalMaxWidth != value:
                self._globalMaxWidth = value
                self.UpdateFade()

        return property(**locals())

    @classmethod
    def MeasureTextSize(cls, text, **customAttributes):
        customAttributes['parent'] = None
        customAttributes['align'] = uiconst.TOPLEFT
        label = cls(**customAttributes)
        label.text = text
        return (label.width, label.height)

    def GetMenu(self):
        parent = self.parent
        if parent and hasattr(parent, 'GetMenu'):
            return parent.GetMenu()

    def OnMouseEnter(self, *args, **kwds):
        parent = self.parent
        if parent and parent.OnMouseEnter.im_func != uicls.Base.OnMouseEnter.im_func:
            return parent.OnMouseEnter(*args, **kwds)

    def OnMouseExit(self, *args, **kwds):
        parent = self.parent
        if parent and parent.OnMouseExit.im_func != uicls.Base.OnMouseExit.im_func:
            return parent.OnMouseExit(*args, **kwds)

    def OnMouseDown(self, *args, **kwds):
        parent = self.parent
        if parent and parent.OnMouseDown.im_func != uicls.Base.OnMouseDown.im_func:
            return parent.OnMouseDown(*args, **kwds)

    def OnMouseUp(self, *args, **kwds):
        parent = self.parent
        if parent and parent.OnMouseUp.im_func != uicls.Base.OnMouseUp.im_func:
            return parent.OnMouseUp(*args, **kwds)

    def OnClick(self, *args, **kwds):
        parent = self.parent
        if parent and parent.OnClick.im_func != uicls.Base.OnClick.im_func:
            return parent.OnClick(*args, **kwds)

    def OnDblClick(self, *args, **kwds):
        parent = self.parent
        if parent and hasattr(parent, 'OnDblClick'):
            return parent.OnDblClick(*args, **kwds)


class SortHeaders(uicls.Container):
    __guid__ = 'uicls.SortHeaders'
    default_name = 'SortHeaders'
    default_align = uiconst.TOTOP
    default_height = 16
    default_state = uiconst.UI_PICKCHILDREN
    default_clipChildren = True
    default_padBottom = 0

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        uicls.Line(parent=self, align=uiconst.TOBOTTOM, color=(1, 1, 1, 0.33))
        self.headerContainer = uicls.Container(parent=self)
        self.settingsID = attributes.settingsID
        self.customSortIcon = None
        self.columnIDs = []
        self.fixedColumns = None
        self.defaultColumn = None

    def SetDefaultColumn(self, columnID, direction):
        self.defaultColumn = (columnID, direction)

    def CreateColumns(self, columns, fixedColumns = None):
        self.headerContainer.Flush()
        self.columnIDs = columns
        self.fixedColumns = fixedColumns
        if columns:
            sizes = self.GetCurrentSizes()
            for columnID in columns:
                header = uicls.Container(parent=self.headerContainer, align=uiconst.TOLEFT, state=uiconst.UI_NORMAL)
                header.OnClick = (self.ClickHeader, header)
                header.OnDblClick = (self.DblClickHeader, header)
                header.columnID = columnID
                header.sortTriangle = None
                headerDivider = uicls.Line(parent=header, align=uiconst.TORIGHT, color=(1, 1, 1, 0.25))
                if columnID not in fixedColumns:
                    scaler = uicls.Container(parent=header, align=uiconst.TOPRIGHT, width=4, height=self.height - 1, state=uiconst.UI_NORMAL)
                    scaler.OnMouseDown = (self.StartHeaderScale, header)
                    scaler.OnMouseEnter = (self.OnHeaderMouseEnter, header)
                    scaler.OnMouseExit = (self.OnHeaderMouseExit, header)
                    header.OnMouseEnter = (self.OnHeaderMouseEnter, header)
                    header.OnMouseExit = (self.OnHeaderMouseExit, header)
                    scaler.cursor = 16
                label = uicls.EveLabelSmall(parent=header, text=sm.GetService('tactical').GetColumnLabel(columnID), align=uiconst.CENTERLEFT, left=6, state=uiconst.UI_DISABLED, maxLines=1)
                header.label = label
                if fixedColumns and columnID in fixedColumns:
                    header.width = fixedColumns[columnID]
                    if header.width <= 32:
                        label.Hide()
                elif columnID in sizes:
                    header.width = max(COLUMNMINSIZE, sizes[columnID])
                else:
                    header.width = max(COLUMNMINSIZE, max(COLUMNMINDEFAULTSIZE, label.textwidth + 24))
                header.fill = uicls.Fill(parent=header, color=(1, 1, 1, 0.125), padLeft=-1, padRight=-1)

            self.UpdateActiveState()

    def SetSortIcon(self, texturePath):
        if self.customSortIcon != texturePath:
            self.customSortIcon = texturePath
            self.UpdateActiveState()

    def UpdateActiveState(self):
        currentActive, currentDirection = self.GetCurrentActive()
        for each in self.headerContainer.children:
            if hasattr(each, 'columnID'):
                if each.columnID == currentActive:
                    if not each.sortTriangle:
                        each.sortTriangle = uicls.Icon(align=uiconst.CENTERRIGHT, pos=(3, -1, 16, 16), parent=each, name='directionIcon', idx=0)
                    if self.customSortIcon:
                        each.sortTriangle.LoadTexture(self.customSortIcon)
                    elif currentDirection:
                        each.sortTriangle.LoadIcon('ui_1_16_16')
                    else:
                        each.sortTriangle.LoadIcon('ui_1_16_15')
                    each.sortTriangle.state = uiconst.UI_DISABLED
                    each.fill.Show()
                    rightMargin = 20
                else:
                    each.fill.Hide()
                    if each.sortTriangle:
                        each.sortTriangle.Hide()
                    rightMargin = 6
                each.label.width = each.width - each.label.left - 4
                if each.sortTriangle and each.sortTriangle.display:
                    each.label.SetRightAlphaFade(each.width - rightMargin - each.label.left, uiconst.SCROLL_COLUMN_FADEWIDTH)
                else:
                    each.label.SetRightAlphaFade()
                if each.width <= 32 or each.width - each.label.left - rightMargin - 6 < each.label.textwidth:
                    each.hint = each.label.text
                else:
                    each.hint = None

    def GetCurrentColumns(self):
        return self.columnIDs

    @telemetry.ZONE_METHOD
    def GetCurrentActive(self):
        all = settings.char.ui.Get('SortHeadersSettings', {})
        currentActive, currentDirection = None, True
        if self.settingsID in all:
            currentActive, currentDirection = all[self.settingsID]
            if currentActive not in self.columnIDs:
                if self.columnIDs:
                    currentActive, currentDirection = self.columnIDs[0], True
                return (None, True)
            return (currentActive, currentDirection)
        if self.defaultColumn is not None:
            columnID, direction = self.defaultColumn
            if columnID in self.columnIDs:
                return self.defaultColumn
        if self.columnIDs:
            currentActive, currentDirection = self.columnIDs[0], True
        return (currentActive, currentDirection)

    def SetCurrentActive(self, columnID, doCallback = True):
        currentActive, currentDirection = self.GetCurrentActive()
        if currentActive == columnID:
            sortDirection = not currentDirection
        else:
            sortDirection = currentDirection
        all = settings.char.ui.Get('SortHeadersSettings', {})
        all[self.settingsID] = (columnID, sortDirection)
        settings.char.ui.Set('SortHeadersSettings', all)
        self.UpdateActiveState()
        if doCallback:
            self.OnSortingChange(currentActive, columnID, currentDirection, sortDirection)

    def DblClickHeader(self, header):
        if not self.ColumnIsFixed(header.columnID):
            self.SetCurrentActive(header.columnID, doCallback=False)
            self.OnColumnSizeReset(header.columnID)

    def ClickHeader(self, header):
        self.SetCurrentActive(header.columnID)

    def StartHeaderScale(self, header, mouseButton, *args):
        if mouseButton == uiconst.MOUSELEFT:
            self.startScaleX = uicore.uilib.x
            self.startScaleWidth = header.width
            uthread.new(self.ScaleHeader, header)

    def OnHeaderMouseEnter(self, header):
        pass

    def OnHeaderMouseExit(self, header):
        pass

    def ScaleHeader(self, header):
        while not self.destroyed and uicore.uilib.leftbtn:
            diff = self.startScaleX - uicore.uilib.x
            header.width = max(COLUMNMINSIZE, self.startScaleWidth - diff)
            self.UpdateActiveState()
            blue.pyos.synchro.Yield()

        currentSizes = self.RegisterCurrentSizes()
        self.UpdateActiveState()
        self.OnColumnSizeChange(header.columnID, header.width, currentSizes)

    def GetCurrentSizes(self):
        current = settings.char.ui.Get('SortHeadersSizes', {}).get(self.settingsID, {})
        if self.fixedColumns:
            current.update(self.fixedColumns)
        for each in self.headerContainer.children:
            if hasattr(each, 'columnID') and each.columnID not in current:
                current[each.columnID] = each.width

        return current

    def ColumnIsFixed(self, columnID):
        return columnID in self.fixedColumns

    def SetColumnSize(self, columnID, size):
        if columnID in self.fixedColumns:
            return
        for each in self.headerContainer.children:
            if hasattr(each, 'columnID') and each.columnID == columnID:
                each.width = max(COLUMNMINSIZE, size)
                break

        self.UpdateActiveState()
        currentSizes = self.RegisterCurrentSizes()
        self.OnColumnSizeChange(columnID, max(COLUMNMINSIZE, size), currentSizes)

    def RegisterCurrentSizes(self):
        sizes = {}
        for each in self.headerContainer.children:
            if hasattr(each, 'columnID'):
                sizes[each.columnID] = each.width

        all = settings.char.ui.Get('SortHeadersSizes', {})
        all[self.settingsID] = sizes
        settings.char.ui.Set('SortHeadersSizes', all)
        return sizes

    def OnSortingChange(self, oldColumnID, columnID, oldSortDirection, sortDirection):
        pass

    def OnColumnSizeChange(self, columnID, newSize, currentSizes):
        pass

    def OnColumnSizeReset(self, columnID):
        pass


FMT_RADPERSEC = u'{value} rad/sec'
KILOMETERS10 = 10000.0
KILOMETERS10000000 = 10000000000.0

class OverviewScrollEntry(uicls.SE_BaseClassCore):
    __guid__ = 'listentry.OverviewScrollEntry'
    __notifyevents__ = []
    ENTRYHEIGHT = 19
    hostileIndicator = None
    attackingMeIndicator = None
    targetedByMeIndicator = None
    myActiveTargetIndicator = None
    targetingIndicator = None
    flagIcon = None
    flagIconBackground = None
    flagBackground = None
    fleetBroadcastIcon = None
    fleetBroadcastID = None
    loadedIconAndBackgroundFlags = None
    loadedEwarGraphicIDs = None
    rightAlignedIconContainer = None
    selectionSprite = None
    globalMaxWidth = None

    @telemetry.ZONE_METHOD
    def Startup(self, *args):
        uicls.Line(parent=self, align=uiconst.TOBOTTOM, color=(1, 1, 1, 0.06))
        self.sr.flag = None
        self.sr.bgColor = None
        self.sr.hilite = None
        self.columnLabels = []
        self.ewarIcons = {}
        node = self.sr.node
        self.updateItem = node.updateItem
        self.itemID = node.itemID
        self.stateItemID = node.itemID
        slimItem = node.slimItem()
        self.iconContainer = uicls.Container(parent=self, name='iconContainer', align=uiconst.CENTERLEFT, width=16, height=16)
        self.mainIcon = uicls.Icon(parent=self.iconContainer, name='mainIcon', state=uiconst.UI_DISABLED)
        self.UpdateIcon()
        selected, hilited, attacking, hostile, targeting, targeted, activeTarget = sm.GetService('state').GetStates(self.stateItemID, [state.selected,
         state.mouseOver,
         state.threatAttackingMe,
         state.threatTargetsMe,
         state.targeting,
         state.targeted,
         state.activeTarget])
        if selected:
            self.ShowSelected()
        if hilited:
            self.CreateHiliteSprite().state = uiconst.UI_DISABLED
        elif uicore.uilib.mouseOver is not self and self.sr.hilite:
            self.sr.hilite.state = uiconst.UI_HIDDEN
        if targeted:
            self.Targeted(targeted)
        if activeTarget:
            self.ActiveTarget(activeTarget)
        if not activeTarget:
            self.Targeting(targeting)
            if not targeting and slimItem is not None:
                targeted, = sm.GetService('state').GetStates(slimItem.itemID, [state.targeted])
                self.Targeted(targeted)
        if self.updateItem:
            if attacking:
                self.Attacking(True)
            elif hostile:
                self.Hostile(True)
        self.UpdateFleetBroadcast()

    @telemetry.ZONE_METHOD
    def Load(self, node):
        with util.ExceptionEater("Exception during overview's Load"):
            self.UpdateColumns()
            if (node.iconAndBackgroundFlags, node.useSmallColorTags) != self.loadedIconAndBackgroundFlags:
                slimItem = node.slimItem()
                if not slimItem:
                    return
                self.UpdateFlagAndBackground(slimItem)
            if node.ewarGraphicIDs != self.loadedEwarGraphicIDs:
                self.UpdateEwar()

    def _OnSizeChange_NoBlock(self, displayWidth, displayHeight):
        self.SetGlobalMaxWidth()

    def SetGlobalMaxWidth(self):
        if self.rightAlignedIconContainer and self.rightAlignedIconContainer.width:
            globalMaxWidth = self.width - self.rightAlignedIconContainer.width - 6
        else:
            globalMaxWidth = None
        self.globalMaxWidth = globalMaxWidth
        for each in self.columnLabels:
            each.globalMaxWidth = globalMaxWidth

    def CreateRightAlignedIconContainer(self):
        if self.rightAlignedIconContainer is None:
            self.rightAlignedIconContainer = uicls.Container(parent=self, name='rightAlignedIconContainer', align=uiconst.CENTERRIGHT, width=200, height=16, state=uiconst.UI_PICKCHILDREN, idx=0)
        return self.rightAlignedIconContainer

    def UpdateRightAlignedIconContainerSize(self):
        if self.rightAlignedIconContainer:
            preWidth = self.rightAlignedIconContainer.width
            self.rightAlignedIconContainer.width = newWidth = sum([ each.width for each in self.rightAlignedIconContainer.children if each.display ])
            if preWidth != newWidth:
                self.SetGlobalMaxWidth()

    def CreateHiliteSprite(self):
        if not self.sr.hilite:
            self.sr.hilite = uicls.Fill(parent=self, color=(1.0, 1.0, 1.0, 0.125), state=uiconst.UI_HIDDEN)
        return self.sr.hilite

    def CreateSelectionSprite(self):
        if not self.selectionSprite:
            self.selectionSprite = uicls.Fill(parent=self, padTop=-1, padBottom=-1, color=(1.0, 1.0, 1.0, 0.25))
        return self.selectionSprite

    @telemetry.ZONE_METHOD
    def UpdateFleetBroadcast(self):
        broadcastID, broadcastFlag, broadcastData = sm.GetService('fleet').GetCurrentFleetBroadcastOnItem(self.itemID)
        if broadcastID != self.fleetBroadcastID:
            if broadcastID is None:
                if self.fleetBroadcastIcon:
                    self.fleetBroadcastIcon.Close()
                    self.fleetBroadcastIcon = None
                    self.UpdateRightAlignedIconContainerSize()
                self.fleetBroadcastType = self.fleetBroadcastID = None
                return
            broadcastType = fleetbr.flagToName[broadcastFlag]
            if broadcastType in ('EnemySpotted', 'NeedBackup', 'InPosition', 'HoldPosition'):
                inBubble = util.InBubble(self.itemID)
                if not inBubble:
                    if self.fleetBroadcastID is not None:
                        if self.fleetBroadcastIcon:
                            self.fleetBroadcastIcon.Close()
                            self.fleetBroadcastIcon = None
                        self.fleetBroadcastType = self.fleetBroadcastID = None
                    return
            self.fleetBroadcastType = broadcastType
            self.fleetBroadcastID = broadcastID
            if not self.fleetBroadcastIcon:
                self.fleetBroadcastIcon = uicls.Icon(name='fleetBroadcastIcon', parent=self.CreateRightAlignedIconContainer(), align=uiconst.TORIGHT, pos=(0, 0, 16, 16), state=uiconst.UI_DISABLED)
            icon = fleetbr.types[broadcastType]['smallIcon']
            self.fleetBroadcastIcon.LoadIcon(icon)
            self.UpdateRightAlignedIconContainerSize()

    @telemetry.ZONE_METHOD
    def UpdateFlagAndBackground(self, slimItem, *args):
        if self.destroyed or not self.updateItem or slimItem is None:
            return
        node = self.sr.node
        self.loadedIconAndBackgroundFlags = (node.iconAndBackgroundFlags, node.useSmallColorTags)
        try:
            if slimItem.groupID != const.groupAgentsinSpace and (slimItem.ownerID and util.IsNPC(slimItem.ownerID) or slimItem.charID and util.IsNPC(slimItem.charID)):
                if self.flagIcon:
                    self.flagIcon.Close()
                    self.flagIcon = None
                if self.flagIconBackground:
                    self.flagIconBackground.Close()
                    self.flagIconBackground = None
                if self.flagBackground:
                    self.flagBackground.Close()
                    self.flagBackground = None
            else:
                node = self.sr.node
                stateSvc = sm.GetService('state')
                iconFlag, backgroundFlag = node.iconAndBackgroundFlags
                if iconFlag and iconFlag != -1 and self.iconContainer.display:
                    if self.flagIcon is None:
                        self.flagIcon = uicls.Sprite(parent=self.iconContainer, name='flagIcon', pos=(-3, -2, 10, 10), state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/Bracket/flagIcons.png', align=uiconst.BOTTOMRIGHT, idx=0)
                        self.flagIcon.rectWidth = 10
                        self.flagIcon.rectHeight = 10
                        self.flagIconBackground = uicls.Fill(parent=self.iconContainer, name='flagIconBackground', pos=(-2, -1, 10, 10), state=uiconst.UI_DISABLED, align=uiconst.BOTTOMRIGHT, idx=1)
                    props = stateSvc.GetStateProps(iconFlag)
                    col = stateSvc.GetStateFlagColor(iconFlag)
                    blink = stateSvc.GetStateFlagBlink(iconFlag)
                    self.flagIconBackground.color.SetRGB(*col)
                    self.flagIcon.color.SetRGB(*props.iconColor)
                    if blink:
                        if not self.flagIcon.HasAnimation('color'):
                            uicore.animations.FadeTo(self.flagIcon, startVal=0.0, endVal=1.0, duration=0.5, loops=uiconst.ANIM_REPEAT, curveType=uiconst.ANIM_WAVE)
                            uicore.animations.FadeTo(self.flagIconBackground, startVal=0.0, endVal=1.0, duration=0.5, loops=uiconst.ANIM_REPEAT, curveType=uiconst.ANIM_WAVE)
                    else:
                        self.flagIcon.StopAnimations()
                        self.flagIcon.color.a = 1.0
                        self.flagIconBackground.StopAnimations()
                        self.flagIconBackground.color.a = 1.0
                    if node.useSmallColorTags:
                        self.flagIcon.display = False
                        self.flagIconBackground.width = self.flagIconBackground.height = 5
                    else:
                        iconNum = props.iconIndex + 1
                        self.flagIcon.display = True
                        self.flagIcon.rectLeft = iconNum * 10
                        self.flagIconBackground.width = self.flagIconBackground.height = 10
                elif self.flagIcon:
                    self.flagIcon.Close()
                    self.flagIcon = None
                    self.flagIconBackground.Close()
                    self.flagIconBackground = None
                if backgroundFlag and backgroundFlag != -1:
                    r, g, b, a = stateSvc.GetStateBackgroundColor(backgroundFlag)
                    a = a * 0.5
                    if not self.flagBackground:
                        self.flagBackground = uicls.Fill(name='bgColor', parent=self, state=uiconst.UI_DISABLED, color=(r,
                         g,
                         b,
                         a))
                    else:
                        self.flagBackground.SetRGBA(r, g, b, a)
                    blink = stateSvc.GetStateBackgroundBlink(backgroundFlag)
                    if blink:
                        if not self.flagBackground.HasAnimation('color'):
                            uicore.animations.FadeTo(self.flagBackground, startVal=0.0, endVal=a, duration=0.75, loops=uiconst.ANIM_REPEAT, curveType=uiconst.ANIM_WAVE)
                    else:
                        self.flagBackground.StopAnimations()
                elif self.flagBackground:
                    self.flagBackground.Close()
                    self.flagBackground = None
        except AttributeError:
            if not self.destroyed:
                raise 

    def CreateFlagMarker(self):
        pass

    @telemetry.ZONE_METHOD
    def UpdateFlagPositions(self, *args, **kwds):
        pass

    @telemetry.ZONE_METHOD
    def UpdateColumns(self):
        node = self.sr.node
        haveIcon = False
        currentLabels = []
        columnOffset = 0
        currentColumns = node.columns
        for columnID in currentColumns:
            columnWidth = node.columnWidths[columnID]
            if columnID == COLUMN_ICON:
                self.iconContainer.left = columnOffset + 3
                self.UpdateIconColor()
                self.iconContainer.state = uiconst.UI_PICKCHILDREN
                columnOffset += columnWidth
                haveIcon = True
                continue
            displayValue = self.GetColumnDisplayValue(node, columnID)
            if not displayValue:
                columnOffset += columnWidth
                continue
            label = None
            if self.columnLabels:
                label = self.columnLabels.pop(0)
                if label.destroyed:
                    label = None
            if not label:
                label = OverviewLabel(parent=self, align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED, idx=0, fontSize=node.fontSize)
            columnHint = node.get('hint_' + columnID, None)
            if columnHint:
                label.state = uiconst.UI_NORMAL
            else:
                label.state = uiconst.UI_DISABLED
            label.columnWidth = columnWidth - COLUMNMARGIN * 2
            label.text = displayValue
            label.rightAligned = columnID in RIGHTALIGNEDCOLUMNS
            label.columnPosition = columnOffset + COLUMNMARGIN
            label.globalMaxWidth = self.globalMaxWidth
            label.hint = columnHint
            columnOffset += columnWidth
            currentLabels.append(label)

        if not haveIcon:
            self.iconContainer.state = uiconst.UI_HIDDEN
        if self.columnLabels:
            while self.columnLabels:
                label = self.columnLabels.pop()
                label.Close()

        self.columnLabels = currentLabels

    @classmethod
    def GetColumnDisplayValue(cls, node, columnID):
        if columnID == COLUMN_DISTANCE:
            surfaceDist = node.rawDistance
            if surfaceDist is None:
                return u''
            if surfaceDist < KILOMETERS10:
                currentDist = int(surfaceDist)
                if currentDist != node.lastFormattedDistance:
                    node.display_DISTANCE = FMT_M.format(distance=FMTFUNCTION(currentDist, useGrouping=True))
                    node.lastFormattedDistance = currentDist
            elif surfaceDist < KILOMETERS10000000:
                currentDist = long(surfaceDist / 1000)
                if currentDist != node.lastFormattedDistance:
                    node.display_DISTANCE = FMT_KM.format(distance=FMTFUNCTION(currentDist, useGrouping=True))
                    node.lastFormattedDistance = currentDist
            else:
                currentDist = round(surfaceDist / const.AU, 1)
                if currentDist != node.lastFormattedDistance:
                    node.display_DISTANCE = FMT_AU.format(distance=FMTFUNCTION(currentDist, useGrouping=True, decimalPlaces=1))
                    node.lastFormattedDistance = currentDist
            return node.display_DISTANCE or u''
        if columnID == COLUMN_ANGULARVELOCITY:
            sortValue = node.rawAngularVelocity
            if sortValue is not None:
                currentAngularVelocity = round(sortValue, 7)
                if currentAngularVelocity != node.lastFormattedAngularVelocity:
                    displayValue = localization.GetByLabel('UI/Overview/AngularVelocityValue', value=sortValue)
                    node.display_ANGULARVELOCITY = FMT_RADPERSEC.format(value=FMTFUNCTION(currentAngularVelocity, useGrouping=True, decimalPlaces=7))
                    node.lastFormattedAngularVelocity = currentAngularVelocity
                return node.display_ANGULARVELOCITY or u'-'
        elif columnID == COLUMN_VELOCITY:
            sortValue = node.rawVelocity
            if sortValue is not None:
                currentVelocity = int(sortValue)
                if currentVelocity != node.lastFormattedVelocity:
                    node.display_VELOCITY = FMT_VELOCITY.format(velocity=FMTFUNCTION(currentVelocity, useGrouping=True))
                    node.lastFormattedVelocity = currentVelocity
                return node.display_VELOCITY or u'-'
        elif columnID == COLUMN_RADIALVELOCITY:
            sortValue = node.rawRadialVelocity
            if sortValue is not None:
                currentRadialVelocity = int(sortValue)
                if currentRadialVelocity != node.lastFormattedRadialVelocity:
                    node.display_RADIALVELOCITY = FMT_VELOCITY.format(velocity=FMTFUNCTION(currentRadialVelocity, useGrouping=True))
                    node.lastFormattedRadialVelocity = currentRadialVelocity
                return node.display_RADIALVELOCITY or u'-'
        elif columnID == COLUMN_TRANSVERSALVELOCITY:
            sortValue = node.rawTransveralVelocity
            if sortValue is not None:
                currentTransveralVelocity = int(sortValue)
                if currentTransveralVelocity != node.lastFormattedTransveralVelocity:
                    node.display_TRANSVERSALVELOCITY = FMT_VELOCITY.format(velocity=FMTFUNCTION(currentTransveralVelocity, useGrouping=True))
                    node.lastFormattedTransveralVelocity = currentTransveralVelocity
                return node.display_TRANSVERSALVELOCITY or u'-'
        return node.Get('display_' + columnID, None)

    @telemetry.ZONE_METHOD
    def UpdateEwar(self):
        node = self.sr.node
        ewarGraphicIDs = node.ewarGraphicIDs
        self.loadedEwarGraphicIDs = ewarGraphicIDs
        for graphicID, icon in self.ewarIcons.iteritems():
            if not ewarGraphicIDs or graphicID not in ewarGraphicIDs:
                icon.state = uiconst.UI_HIDDEN

        if ewarGraphicIDs:
            for graphicID in ewarGraphicIDs:
                if graphicID in self.ewarIcons:
                    self.ewarIcons[graphicID].state = uiconst.UI_NORMAL
                else:
                    icon = uicls.Icon(parent=self.CreateRightAlignedIconContainer(), align=uiconst.TORIGHT, state=uiconst.UI_NORMAL, width=16, hint=node.ewarHints[graphicID], graphicID=graphicID, ignoreSize=True)
                    self.ewarIcons[graphicID] = icon

        self.UpdateRightAlignedIconContainerSize()

    def OnStateChange(self, itemID, flag, status, *args):
        if self.stateItemID != itemID:
            return
        if flag == state.mouseOver:
            self.Hilite(status)
        elif flag == state.selected:
            if status:
                self.ShowSelected()
            else:
                self.ShowDeselected()
        elif flag == state.threatTargetsMe:
            attacking, = sm.StartService('state').GetStates(itemID, [state.threatAttackingMe])
            if attacking:
                self.Attacking(True)
            else:
                self.Hostile(status)
        elif flag == state.threatAttackingMe:
            self.Attacking(status)
            if not status:
                hostile, = sm.StartService('state').GetStates(itemID, [state.threatTargetsMe])
                self.Hostile(hostile)
        elif flag == state.targeted:
            self.Targeted(status)
        elif flag == state.targeting:
            self.Targeting(status)
        elif flag == state.activeTarget:
            self.ActiveTarget(status)
        elif flag == state.flagWreckAlreadyOpened:
            self.UpdateIconColor()
        elif flag == state.flagWreckEmpty:
            self.UpdateIcon()
        else:
            broadcastDataName = fleetbr.flagToName.get(flag, None)
            if broadcastDataName is not None:
                self.UpdateFleetBroadcast()

    @telemetry.ZONE_METHOD
    def Hostile(self, state, *args, **kwds):
        if state and self.iconContainer.display:
            if not self.hostileIndicator:
                self.hostileIndicator = uicls.BlinkingSpriteOnSharedCurve(parent=self.iconContainer, name='hostile', pos=(-1, -1, 18, 18), state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/Bracket/hostileBracket.png', align=uiconst.TOPLEFT, color=(1.0, 0.8, 0.0, 0.3), curveSetName='sharedHostileCurveSet')
        elif self.hostileIndicator:
            self.hostileIndicator.Close()
            self.hostileIndicator = None

    def Attacking(self, state):
        if state and self.iconContainer.display:
            if not self.attackingMeIndicator:
                self.attackingMeIndicator = uicls.BlinkingSpriteOnSharedCurve(parent=self.iconContainer, name='attackingMe', pos=(-1, -1, 18, 18), state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/Bracket/hostileBracket.png', align=uiconst.TOPLEFT, idx=0, color=(0.8, 0.0, 0.0, 0.3), curveSetName='sharedHostileCurveSet')
            if self.hostileIndicator:
                self.hostileIndicator.Close()
                self.hostileIndicator = None
        elif self.attackingMeIndicator:
            self.attackingMeIndicator.Close()
            self.attackingMeIndicator = None

    @telemetry.ZONE_METHOD
    def Targeting(self, state):
        if state and self.iconContainer.display:
            if not self.targetingIndicator:
                par = uicls.Container(name='targeting', align=uiconst.CENTER, width=28, height=28, parent=self.iconContainer)
                self.targetingIndicator = par
                uicls.Fill(parent=par, align=uiconst.TOPLEFT, left=0, top=3, width=5, height=2, color=(1.0, 1.0, 1.0, 0.5))
                uicls.Fill(parent=par, align=uiconst.TOPRIGHT, left=0, top=3, width=5, height=2, color=(1.0, 1.0, 1.0, 0.5))
                uicls.Fill(parent=par, align=uiconst.BOTTOMLEFT, left=0, top=3, width=5, height=2, color=(1.0, 1.0, 1.0, 0.5))
                uicls.Fill(parent=par, align=uiconst.BOTTOMRIGHT, left=0, top=3, width=5, height=2, color=(1.0, 1.0, 1.0, 0.5))
                uicls.Fill(parent=par, align=uiconst.TOPLEFT, left=3, top=0, width=2, height=3, color=(1.0, 1.0, 1.0, 0.5))
                uicls.Fill(parent=par, align=uiconst.TOPRIGHT, left=3, top=0, width=2, height=3, color=(1.0, 1.0, 1.0, 0.5))
                uicls.Fill(parent=par, align=uiconst.BOTTOMLEFT, left=3, top=0, width=2, height=3, color=(1.0, 1.0, 1.0, 0.5))
                uicls.Fill(parent=par, align=uiconst.BOTTOMRIGHT, left=3, top=0, width=2, height=3, color=(1.0, 1.0, 1.0, 0.5))
                uthread.pool('Tactical::Targeting', self.AnimateTargeting, par)
        elif self.targetingIndicator:
            self.targetingIndicator.Close()
            self.targetingIndicator = None

    def AnimateTargeting(self, par):
        while par and not par.destroyed:
            p = par.children[0]
            for i in xrange(1, 8):
                par.width = par.height = 28 - i * 2
                blue.pyos.synchro.SleepSim(50)

    def Targeted(self, activestate, *args, **kwds):
        if activestate and self.iconContainer.display:
            if self.targetingIndicator:
                self.targetingIndicator.Close()
                self.targetingIndicator = None
            if not self.targetedByMeIndicator:
                self.targetedByMeIndicator = uicls.Sprite(parent=self.iconContainer, name='targetedByMeIndicator', pos=(-1, -1, 18, 18), state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/Bracket/activeTarget.png', align=uiconst.TOPLEFT, color=(1.0, 1.0, 1.0, 0.66), idx=0)
        elif self.targetedByMeIndicator:
            self.targetedByMeIndicator.Close()
            self.targetedByMeIndicator = None

    def ActiveTarget(self, activestate):
        if activestate and self.iconContainer.display:
            if self.targetingIndicator:
                self.targetingIndicator.Close()
                self.targetingIndicator = None
            if not self.myActiveTargetIndicator:
                self.myActiveTargetIndicator = uicls.Sprite(parent=self.iconContainer, name='myActiveTargetIndicator', pos=(-1, -1, 18, 18), state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/Bracket/activeTarget.png', align=uiconst.TOPLEFT, idx=0)
        elif self.myActiveTargetIndicator:
            self.myActiveTargetIndicator.Close()
            self.myActiveTargetIndicator = None

    def Hilite(self, state):
        if state:
            self.CreateHiliteSprite().state = uiconst.UI_DISABLED
        elif self.sr.hilite:
            self.sr.hilite.state = uiconst.UI_HIDDEN

    def Select(self, *args):
        pass

    def Deselect(self, *args):
        pass

    def ShowSelected(self, *args):
        self.CreateSelectionSprite().state = uiconst.UI_DISABLED

    def ShowDeselected(self, *args):
        if self.selectionSprite:
            self.selectionSprite.state = uiconst.UI_HIDDEN

    @telemetry.ZONE_METHOD
    def UpdateIcon(self):
        node = self.sr.node
        slimItem = node.slimItem()
        if not slimItem:
            return None
        if slimItem.groupID == const.groupWreck:
            if slimItem.isEmpty:
                iconNo = 'ui_38_16_29'
            else:
                iconNo = 'ui_38_16_28'
        else:
            iconNo, _dockType, _minDist, _maxDist, _iconOffset, _logflag = sm.GetService('bracket').GetBracketProps(slimItem, node.ball())
        self.mainIcon.LoadIcon(iconNo)

    @telemetry.ZONE_METHOD
    def UpdateIconColor(self):
        if self.destroyed:
            return
        node = self.sr.node
        slimItem = node.slimItem()
        if not slimItem:
            return
        if node.iconColor:
            iconColor = node.iconColor
        else:
            iconColor, colorSortValue = bracketUtils.GetIconColor(slimItem, getSortValue=True)
            if node.sortIconIndex is not None:
                node.sortValue[node.sortIconIndex][1] = colorSortValue
            node.iconColor = iconColor
        r, g, b = iconColor
        if slimItem.groupID in (const.groupWreck, const.groupSpawnContainer) and sm.GetService('wreck').IsViewedWreck(slimItem.itemID):
            attenuation = 0.55
            r, g, b = r * attenuation, g * attenuation, b * attenuation
        self.mainIcon.color = (r,
         g,
         b,
         1)

    def OnDblClick(self, *args):
        if uicore.cmd.IsCombatCommandLoaded():
            return
        slimItem = self.sr.node.slimItem()
        if slimItem:
            sm.GetService('menu').Activate(slimItem)

    def OnMouseEnter(self, *args):
        eve.Message('ListEntryEnter')
        if not self.hint:
            self.hint = sm.GetService('bracket').GetBracketName(self.sr.node.itemID)
        self.CreateHiliteSprite().state = uiconst.UI_DISABLED
        sm.GetService('state').SetState(self.sr.node.itemID, state.mouseOver, 1)

    def OnMouseExit(self, *args):
        if self.sr.hilite:
            self.sr.hilite.state = uiconst.UI_HIDDEN
        sm.GetService('state').SetState(self.sr.node.itemID, state.mouseOver, 0)

    def OnClick(self, *args):
        eve.Message('ListEntryClick')
        self.sr.node.scroll.SelectNode(self.sr.node)
        uicore.cmd.ExecuteCombatCommand(self.sr.node.itemID, uiconst.UI_CLICK)

    def GetMenu(self, *args):
        return sm.GetService('menu').CelestialMenu(self.sr.node.itemID)

    def SetLabelAlpha(self, alpha):
        self.sr.label.color.a = alpha

    def UpdateTutorialHighlight(self, isActive):
        frame = getattr(self, 'tutorialHighlight', None)
        if isActive:
            from tutorial import TutorialColor
            if frame is None:
                self.tutorialHighlight = uicls.Fill(parent=self, color=TutorialColor.HINT_FRAME, opacity=0.25)
        elif frame is not None:
            self.tutorialHighlight.Close()
            self.tutorialHighlight = None


class BaseTacticalEntry(listentry.Generic):
    __guid__ = 'listentry.BaseTacticalEntry'
    __notifyevents__ = ['OnStateChange']
    __update_on_reload__ = 1

    def init(self):
        self.gaugesInited = 0
        self.gaugesVisible = 0
        self.sr.gaugeParent = None
        self.sr.gauge_shield = None
        self.sr.gauge_armor = None
        self.sr.gauge_struct = None
        self.sr.dmgTimer = None

    def Startup(self, *args):
        listentry.Generic.Startup(self, *args)
        sm.RegisterNotify(self)

    @telemetry.ZONE_METHOD
    def Load(self, node):
        data = node
        selected, = sm.GetService('state').GetStates(data.itemID, [state.selected])
        node.selected = selected
        listentry.Generic.Load(self, node)
        self.sr.label.left = 20 + 16 * data.sublevel
        self.UpdateDamage()
        self.sr.label.Update()

    def UpdateDamage(self):
        if not util.InBubble(self.GetShipID()):
            self.HideDamageDisplay()
            return False
        d = self.sr.node
        if not getattr(d, 'slimItem', None):
            typeOb = cfg.invtypes.Get(d.typeID)
            groupID = typeOb.groupID
            categoryID = typeOb.categoryID
        else:
            slimItem = d.slimItem()
            if not slimItem:
                self.HideDamageDisplay()
                return False
            groupID = slimItem.groupID
            categoryID = slimItem.categoryID
        shipID = self.GetShipID()
        ret = False
        if shipID and categoryID in (const.categoryShip, const.categoryDrone):
            dmg = self.GetDamage(shipID)
            if dmg is not None:
                ret = self.SetDamageState(dmg)
                if self.sr.dmgTimer is None:
                    self.sr.dmgTimer = base.AutoTimer(1000, self.UpdateDamage)
            else:
                self.HideDamageDisplay()
        return ret

    def ShowDamageDisplay(self):
        self.InitGauges()

    def HideDamageDisplay(self):
        if self.gaugesInited:
            self.sr.gaugeParent.state = uiconst.UI_HIDDEN

    def GetDamage(self, itemID):
        bp = sm.GetService('michelle').GetBallpark()
        if bp is None:
            self.sr.dmgTimer = None
            return
        ret = bp.GetDamageState(itemID)
        if ret is None:
            self.sr.dmgTimer = None
        return ret

    def GetHeight(self, *args):
        node, width = args
        node.height = node.Get('height', 0) or 32
        return node.height

    def GetMenu(self):
        return sm.GetService('menu').CelestialMenu(self.sr.node.itemID)

    def GetShipID(self):
        if self.sr.node:
            return self.sr.node.itemID

    def OnMouseEnter(self, *args):
        listentry.Generic.OnMouseEnter(self, *args)
        if self.sr.node:
            sm.GetService('state').SetState(self.sr.node.itemID, state.mouseOver, 1)

    def OnMouseExit(self, *args):
        listentry.Generic.OnMouseExit(self, *args)
        if self.sr.node:
            sm.GetService('state').SetState(self.sr.node.itemID, state.mouseOver, 0)

    def OnStateChange(self, itemID, flag, true, *args):
        if util.GetAttrs(self, 'sr', 'node') is None:
            return
        if self.sr.node.itemID != itemID:
            return
        if flag == state.mouseOver:
            self.Hilite(true)
        elif flag == state.selected:
            self.Select(true)

    def Hilite(self, state):
        if self.sr.node:
            self.sr.hilite.state = [uiconst.UI_HIDDEN, uiconst.UI_DISABLED][state]

    def Select(self, state):
        self.sr.selection.state = [uiconst.UI_HIDDEN, uiconst.UI_DISABLED][state]
        self.sr.node.selected = state

    def SetDamageState(self, state):
        self.InitGauges()
        visible = 0
        gotDmg = False
        for i, gauge in enumerate((self.sr.gauge_shield, self.sr.gauge_armor, self.sr.gauge_struct)):
            if state[i] is None:
                gauge.state = uiconst.UI_HIDDEN
            else:
                oldWidth = gauge.sr.bar.width
                gauge.sr.bar.width = int(gauge.width * round(state[i], 3))
                if gauge.sr.bar.width < oldWidth:
                    gotDmg = True
                gauge.state = uiconst.UI_DISABLED
                visible += 1

        self.gaugesVisible = visible
        return gotDmg

    def InitGauges(self):
        if self.gaugesInited:
            self.sr.gaugeParent.state = uiconst.UI_NORMAL
            return
        par = uicls.Container(name='gauges', parent=self, align=uiconst.TORIGHT, width=68, height=0, state=uiconst.UI_NORMAL, top=2, idx=0)
        uicls.Container(name='push', parent=par, align=uiconst.TORIGHT, width=4)
        for each in ('SHIELD', 'ARMOR', 'STRUCT'):
            g = uicls.Container(name=each, align=uiconst.TOTOP, width=64, height=9, left=-2)
            uicls.Container(name='push', parent=g, align=uiconst.TOBOTTOM, height=2)
            uicls.EveLabelSmall(text=each[:2], parent=g, left=68, top=-1, width=64, height=12, state=uiconst.UI_DISABLED)
            g.name = 'gauge_%s' % each.lower()
            uicls.Line(parent=g, align=uiconst.TOTOP)
            uicls.Line(parent=g, align=uiconst.TOBOTTOM)
            uicls.Line(parent=g, align=uiconst.TOLEFT)
            uicls.Line(parent=g, align=uiconst.TORIGHT)
            g.sr.bar = uicls.Fill(parent=g, align=uiconst.TOLEFT)
            uicls.Fill(parent=g, color=(158 / 256.0,
             11 / 256.0,
             14 / 256.0,
             1.0))
            par.children.append(g)
            setattr(self.sr, 'gauge_%s' % each.lower(), g)

        self.sr.gaugeParent = par
        self.gaugesInited = 1


class OverviewSettings(uicls.Window):
    __guid__ = 'form.OverviewSettings'
    __notifyevents__ = ['OnTacticalPresetChange', 'OnOverviewPresetSaved']
    default_windowID = 'overviewsettings'

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        self.currentKey = None
        self.specialGroups = util.GetNPCGroups()
        self.scope = 'inflight'
        self.SetCaption(localization.GetByLabel('UI/Overview/OverviewSettings'))
        self.minWidth = 322
        self.minHeight = 250
        self.SetWndIcon()
        self.SetHeaderIcon()
        settingsIcon = self.sr.headerIcon
        settingsIcon.state = uiconst.UI_NORMAL
        settingsIcon.GetMenu = self.GetPresetsMenu
        settingsIcon.expandOnLeft = 1
        settingsIcon.hint = ''
        self.SetTopparentHeight(0)
        self.sr.main = uiutil.GetChild(self, 'main')
        self.statetop = statetop = uicls.Container(name='statetop', parent=self.sr.main, align=uiconst.TOTOP)
        topText = uicls.EveLabelMedium(text=localization.GetByLabel('UI/Overview/HintToggleDisplayState'), parent=statetop, align=uiconst.TOTOP, padding=(10, 3, 10, 0), state=uiconst.UI_NORMAL)
        cb = uicls.Checkbox(text=localization.GetByLabel('UI/Overview/ApplyToShipsAndDronesOnly'), parent=statetop, configName='applyOnlyToShips', retval=None, checked=settings.user.overview.Get('applyOnlyToShips', 1), groupname=None, callback=self.CheckBoxChange, prefstype=('user', 'overview'), align=uiconst.TOTOP, padding=(9, 0, 0, 0))
        self.sr.applyOnlyToShips = cb
        cb = uicls.Checkbox(text=localization.GetByLabel('UI/Overview/UseSmallColortags'), parent=statetop, configName='useSmallColorTags', retval=None, checked=settings.user.overview.Get('useSmallColorTags', 0), groupname=None, callback=self.CheckBoxChange, prefstype=('user', 'overview'), align=uiconst.TOTOP, padding=(9, 0, 0, 0))
        self.sr.useSmallColorTags = cb
        self.sr.useSmallText = uicls.Checkbox(text=localization.GetByLabel('UI/Overview/UseSmallFont'), parent=statetop, configName='useSmallText', retval=None, checked=settings.user.overview.Get('useSmallText', 0), callback=self.CheckBoxChange, prefstype=('user', 'overview'), align=uiconst.TOTOP, padding=(9, 0, 0, 0))
        statebtns = uicls.ButtonGroup(btns=[[localization.GetByLabel('UI/Commands/ResetAll'),
          self.ResetStateSettings,
          (),
          None]], parent=self.sr.main, idx=0)
        coltop = uicls.Container(name='coltop', parent=self.sr.main, align=uiconst.TOTOP, height=52)
        uicls.EveLabelMedium(text=localization.GetByLabel('UI/Overview/HintToggleDisplayStateAndOrder'), parent=coltop, align=uiconst.TOTOP, padding=(10, 2, 10, 12), state=uiconst.UI_NORMAL)
        colbtns = uicls.ButtonGroup(btns=[[localization.GetByLabel('UI/Overview/ResetColumns'),
          self.ResetColumns,
          (),
          None]], parent=self.sr.main, idx=0)
        filtertop = uicls.Container(name='filtertop', parent=self.sr.main, align=uiconst.TOTOP)
        uicls.Container(name='push', parent=filtertop, align=uiconst.TOTOP, height=36, state=uiconst.UI_DISABLED)
        shiptop = uicls.Container(name='filtertop', parent=self.sr.main, align=uiconst.TOTOP, height=57)
        presetMenu = uicls.MenuIcon()
        presetMenu.GetMenu = self.GetShipLabelMenu
        presetMenu.left = 6
        presetMenu.top = 10
        presetMenu.hint = ''
        shiptop.children.append(presetMenu)
        cb = uicls.Checkbox(text=localization.GetByLabel('UI/Overview/HideTickerIfInAlliance'), parent=shiptop, configName='hideCorpTicker', retval=None, checked=settings.user.overview.Get('hideCorpTicker', 0), groupname=None, callback=self.CheckBoxChange, prefstype=('user', 'overview'), align=uiconst.TOTOP, pos=(0, 30, 0, 16))
        cb.padLeft = 8
        self.sr.applyOnlyToShips = cb
        overviewtabbtns = uicls.ButtonGroup(btns=[[localization.GetByLabel('UI/Commands/Apply'),
          self.UpdateOverviewTab,
          (),
          None]], parent=self.sr.main, idx=0)
        misctop = uicls.Container(name='misctop', parent=self.sr.main, align=uiconst.TOALL, left=const.defaultPadding, width=const.defaultPadding, top=const.defaultPadding)
        miscPadding = 4
        overviewBroadcastsToTop = uicls.Checkbox(text=localization.GetByLabel('UI/Overview/MoveBroadcastersToTop'), parent=misctop, configName='overviewBroadcastsToTop', retval=None, checked=settings.user.overview.Get('overviewBroadcastsToTop', 0), groupname=None, prefstype=('user', 'overview'), align=uiconst.TOTOP, padLeft=miscPadding)
        self.targetRangeSubCheckboxes = []
        btnCont = uicls.Container(parent=misctop, height=20, align=uiconst.TOTOP)
        uicls.Button(parent=btnCont, label=localization.GetByLabel('UI/Overview/ResetOverview'), func=self.ResetAllOverviewSettings, left=miscPadding)
        uicls.EveHeaderSmall(text=localization.GetByLabel('UI/Overview/BracketAndTargetsHeader'), parent=misctop, align=uiconst.TOTOP, state=uiconst.UI_DISABLED, top=14, padLeft=miscPadding + 2)
        dmgIndicatorCb = uicls.Checkbox(text=localization.GetByLabel('UI/Overview/DisplayDamageIndications'), parent=misctop, configName='showBiggestDamageDealers', retval=None, checked=settings.user.ui.Get('showBiggestDamageDealers', True), groupname=None, prefstype=('user', 'ui'), align=uiconst.TOTOP, callback=self.MiscCheckboxChange, padLeft=miscPadding)
        moduleHairlineCb = uicls.Checkbox(text=localization.GetByLabel('UI/Overview/DisplayModuleLinks'), parent=misctop, configName='showModuleHairlines', retval=None, checked=settings.user.ui.Get('showModuleHairlines', True), groupname=None, prefstype=('user', 'ui'), align=uiconst.TOTOP, padLeft=miscPadding)
        targetCrosshairCb = uicls.Checkbox(text=localization.GetByLabel('UI/SystemMenu/GeneralSettings/Inflight/ShowTargettingCrosshair'), parent=misctop, configName='targetCrosshair', retval=None, checked=settings.user.ui.Get('targetCrosshair', True), groupname=None, prefstype=('user', 'ui'), align=uiconst.TOTOP, callback=self.MiscCheckboxChange, padLeft=miscPadding)
        targetRangeCb = uicls.Checkbox(text=localization.GetByLabel('UI/Overview/DisplayRangeBrackets'), parent=misctop, configName='showInTargetRange', retval=None, checked=settings.user.ui.Get('showInTargetRange', True), groupname=None, prefstype=('user', 'ui'), align=uiconst.TOTOP, callback=self.MiscCheckboxChange, padLeft=miscPadding)
        configName = 'showCategoryInTargetRange_%s' % const.categoryShip
        targetRangeShipsCb = uicls.Checkbox(text=localization.GetByLabel('UI/Overview/Ships'), parent=misctop, configName=configName, retval=None, checked=settings.user.ui.Get(configName, True), groupname=None, prefstype=('user', 'ui'), align=uiconst.TOTOP, callback=self.MiscCheckboxChange, padLeft=3 * miscPadding)
        self.targetRangeSubCheckboxes.append(targetRangeShipsCb)
        configName = 'showCategoryInTargetRange_%s' % const.categoryEntity
        targetRangeNPCsCb = uicls.Checkbox(text=localization.GetByLabel('UI/Overview/NPCs'), parent=misctop, configName=configName, retval=None, checked=settings.user.ui.Get(configName, True), groupname=None, prefstype=('user', 'ui'), align=uiconst.TOTOP, callback=self.MiscCheckboxChange, padLeft=3 * miscPadding)
        self.targetRangeSubCheckboxes.append(targetRangeNPCsCb)
        configName = 'showCategoryInTargetRange_%s' % const.categoryDrone
        targetRangeDronesCb = uicls.Checkbox(text=localization.GetByLabel('UI/Overview/Drones'), parent=misctop, configName=configName, retval=None, checked=settings.user.ui.Get(configName, True), groupname=None, prefstype=('user', 'ui'), align=uiconst.TOTOP, callback=self.MiscCheckboxChange, padLeft=3 * miscPadding)
        self.targetRangeSubCheckboxes.append(targetRangeDronesCb)
        left = 10
        overviewtabtop = uicls.Container(name='overviewtabtop', parent=self.sr.main, align=uiconst.TOALL, pos=(0, 0, 0, 0))
        comboOptions = []
        comboOptions.append([' ', None])
        overviewOptions = [(' ', [' ', None])]
        bracketOptions = [('  ', [localization.GetByLabel('UI/Overview/ShowAllBrackets'), None])]
        presets = settings.user.overview.Get('overviewPresets', {})
        for label in presets.keys():
            if label == 'ccp_notsaved':
                overviewOptions.append(('  ', [localization.GetByLabel('UI/Overview/NotSaved'), label]))
                bracketOptions.append(('   ', [localization.GetByLabel('UI/Overview/NotSaved'), label]))
            else:
                overviewName = sm.GetService('overviewPresetSvc').GetDefaultOverviewName(label)
                lowerLabel = label.lower()
                if overviewName is not None:
                    overviewOptions.append((lowerLabel, [overviewName, label]))
                    bracketOptions.append((lowerLabel, [overviewName, label]))
                else:
                    overviewOptions.append((lowerLabel, [label, label]))
                    bracketOptions.append((lowerLabel, [label, label]))

        overviewOptions = [ x[1] for x in localizationUtil.Sort(overviewOptions, key=lambda x: x[0]) ]
        bracketOptions = [ x[1] for x in localizationUtil.Sort(bracketOptions, key=lambda x: x[0]) ]
        top = uix.GetTextHeight('Xg') + const.defaultPadding
        offset = 6
        topOffset = 6
        widthOverview = uix.GetTextWidth(localization.GetByLabel('UI/Overview/OverviewProfile'), 11, uppercase=1, hspace=1)
        widthBracket = uix.GetTextWidth(localization.GetByLabel('UI/Overview/BracketProfile'), 11, uppercase=1, hspace=1)
        widthText = 150
        self.tabedit = {}
        self.comboTabOverview = {}
        self.comboTabBracket = {}
        tabsettings = settings.user.overview.Get('tabsettings', {})
        for i in range(5):
            tabeditVal = ''
            comboTabOverviewVal = None
            comboTabBracketVal = None
            if tabsettings.has_key(i):
                tabeditVal = tabsettings[i].get('name', None)
                comboTabBracketVal = tabsettings[i].get('bracket', None)
                comboTabOverviewVal = tabsettings[i].get('overview', None)
            left = 6
            tabedit = uicls.SinglelineEdit(name='edit' + str(i), parent=overviewtabtop, align=uiconst.TOPLEFT, pos=(left,
             top,
             80,
             0), setvalue=tabeditVal)
            self.tabedit[i] = tabedit
            left += tabedit.width + offset
            comboTabOverview = uicls.Combo(label='', parent=overviewtabtop, options=overviewOptions, name='comboTabOverview', select=comboTabOverviewVal, pos=(left,
             top,
             0,
             0), align=uiconst.TOPLEFT, width=widthOverview)
            self.comboTabOverview[i] = comboTabOverview
            left += comboTabOverview.width + offset
            comboTabBracket = uicls.Combo(label='', parent=overviewtabtop, options=bracketOptions, name='comboTabBracket', select=comboTabBracketVal, pos=(left,
             top,
             0,
             0), width=widthBracket, align=uiconst.TOPLEFT)
            self.comboTabBracket[i] = comboTabBracket
            top += topOffset + tabedit.height

        left = 6
        top = 4
        uicls.EveLabelSmall(text=localization.GetByLabel('UI/Overview/TabName'), parent=overviewtabtop, left=left, top=top, state=uiconst.UI_DISABLED, color=None, maxLines=1)
        left += tabedit.width + offset
        uicls.EveLabelSmall(text=localization.GetByLabel('UI/Overview/OverviewProfile'), parent=overviewtabtop, left=left, top=top, state=uiconst.UI_DISABLED, color=None, maxLines=1)
        left += comboTabOverview.width + offset
        uicls.EveLabelSmall(text=localization.GetByLabel('UI/Overview/BracketProfile'), parent=overviewtabtop, left=left, top=top, state=uiconst.UI_DISABLED, color=None, maxLines=1)
        left = 6
        top = 30
        btns = uicls.ButtonGroup(btns=[[localization.GetByLabel('UI/Common/SelectAll'),
          self.SelectAll,
          (),
          None], [localization.GetByLabel('UI/Common/DeselectAll'),
          self.DeselectAll,
          (),
          None]], parent=self.sr.main, idx=0)
        top = 6
        l = uicls.EveLabelSmall(text=localization.GetByLabel('UI/Overview/Presets'), parent=filtertop, width=200, left=14, top=top)
        top += l.textheight
        acs = settings.user.overview.Get('activeOverviewPreset', 'default')
        overviewName = sm.GetService('overviewPresetSvc').GetDefaultOverviewName(acs)
        if overviewName is not None:
            acs = overviewName
        if acs == 'ccp_notsaved':
            acs = localization.GetByLabel('UI/Overview/NotSaved')
        self.sr.presetText = uicls.EveLabelSmall(text=acs, parent=filtertop, width=200, left=14, top=top)
        top += self.sr.presetText.textheight
        self.sr.scroll = uicls.Scroll(name='scroll', parent=self.sr.main, padding=const.defaultPadding)
        self.sr.scroll.multiSelect = 0
        self.sr.scroll.SelectAll = self.SelectAll
        self.sr.scroll.sr.content.OnDropData = self.MoveStuff
        self.Maximize()
        self.state = uiconst.UI_NORMAL
        stateTabs = [[localization.GetByLabel('UI/Overview/Colortag'),
          statebtns,
          self,
          'flag'], [localization.GetByLabel('UI/Overview/Background'),
          statebtns,
          self,
          'background'], [localization.GetByLabel('UI/Overview/EWAR'),
          None,
          self,
          'smartFilters']]
        self.sr.statetabs = uicls.TabGroup(name='overviewstatesTab', height=18, align=uiconst.TOBOTTOM, parent=statetop, idx=0, tabs=stateTabs, groupID='overviewstatesTab', autoselecttab=0)
        filterTabs = [[localization.GetByLabel('UI/Generic/Types'),
          btns,
          self,
          'filtertypes'], [localization.GetByLabel('UI/Generic/States'),
          None,
          self,
          'filterstates']]
        self.sr.filtertabs = uicls.TabGroup(name='overviewstatesTab', height=18, align=uiconst.TOBOTTOM, parent=filtertop, tabs=filterTabs, groupID='overviewfilterTab', autoselecttab=0)
        filtertop.height = top + self.sr.filtertabs.height
        settingsTabs = [[uiutil.FixedTabName('UI/Generic/Filters'),
          btns,
          self,
          'filters',
          filtertop],
         [uiutil.FixedTabName('UI/Generic/Appearance'),
          statebtns,
          self,
          'appearance',
          statetop],
         [uiutil.FixedTabName('UI/Generic/Columns'),
          colbtns,
          self,
          'columns',
          coltop],
         [uiutil.FixedTabName('UI/Common/ItemTypes/Ships'),
          [],
          self,
          'ships',
          shiptop],
         [localization.GetByLabel('UI/Overview/OverviewTabs'),
          overviewtabbtns,
          self,
          'overviewTabs',
          overviewtabtop],
         [uiutil.FixedTabName('UI/Generic/Misc'),
          [],
          self,
          'misc',
          misctop]]
        self.sr.tabs = uicls.TabGroup(name='overviewsettingsTab', height=18, align=uiconst.TOTOP, parent=self.sr.main, idx=0, tabs=settingsTabs, groupID='overviewsettingsTab', UIIDPrefix='overviewSettingsTab')
        self.sr.statetabs.align = uiconst.TOBOTTOM
        self.ResetMinSize()
        self.UpdateStateTopHeight()

    def UpdateStateTopHeight(self):
        self.statetop.height = sum((c.height for c in self.statetop.children))

    def MoveStuff(self, dragObj, entries, idx = -1, *args):
        if self.currentKey is None:
            return
        if self.currentKey == 'columns':
            self.MoveColumn(idx)
        elif self.currentKey in ('flag', 'background'):
            self.Move(idx)
        elif self.currentKey == 'ships':
            self.MoveShipLabel(idx)

    def OnTacticalPresetChange(self, label, preset):
        overviewName = sm.GetService('overviewPresetSvc').GetDefaultOverviewName(label)
        if overviewName is not None:
            label = overviewName
        if label == 'ccp_notsaved':
            label = localization.GetByLabel('UI/Overview/NotSaved')
        self.sr.presetText.text = label
        if uiutil.IsVisible(self.sr.filtertabs) and self.sr.filtertabs.GetSelectedArgs() in ('filtertypes', 'filterstates'):
            self.sr.filtertabs.ReloadVisible()

    def OnOverviewPresetSaved(self):
        overviewOptions = [(' ', [' ', None])]
        bracketOptions = [(' ', [' ', ' '], [localization.GetByLabel('UI/Overview/ShowAllBrackets'), None])]
        tabsettings = settings.user.overview.Get('tabsettings', {})
        presets = settings.user.overview.Get('overviewPresets', {})
        for label in presets.keys():
            if label == 'ccp_notsaved':
                overviewOptions.append(('  ', [localization.GetByLabel('UI/Overview/NotSaved'), label]))
                bracketOptions.append(('  ', [localization.GetByLabel('UI/Overview/NotSaved'), label]))
            else:
                overviewName = sm.GetService('overviewPresetSvc').GetDefaultOverviewName(label)
                lowerLabel = label.lower()
                if overviewName is not None:
                    overviewOptions.append((lowerLabel, [overviewName, label]))
                    bracketOptions.append((lowerLabel, [overviewName, label]))
                else:
                    overviewOptions.append((lowerLabel, [label, label]))
                    bracketOptions.append((lowerLabel, [label, label]))

        overviewOptions = [ x[1] for x in localizationUtil.Sort(overviewOptions, key=lambda x: x[0]) ]
        bracketOptions = [ x[1] for x in localizationUtil.Sort(bracketOptions, key=lambda x: x[0]) ]
        for i in range(5):
            comboTabOverviewVal = None
            comboTabBracketVal = None
            if tabsettings.has_key(i):
                comboTabOverviewVal = tabsettings[i].get('overview', None)
                comboTabBracketVal = tabsettings[i].get('bracket', None)
            self.comboTabOverview[i].LoadOptions(overviewOptions, comboTabOverviewVal)
            self.comboTabBracket[i].LoadOptions(overviewOptions, comboTabBracketVal)

    def ExportSettings(self, *args):
        pass

    def ResetAllOverviewSettings(self, *args):
        if eve.Message('ResetAllOverviewSettings', {}, uiconst.YESNO) == uiconst.ID_YES:
            oldTabs = settings.user.overview.Get('tabsettings', {})
            values = settings.user.overview.GetValues()
            keys = values.keys()
            for key in keys:
                settings.user.overview.Delete(key)

            sm.StartService('tactical').PrimePreset()
            overviewWindow = form.OverView.GetIfOpen()
            if overviewWindow:
                newTabs = settings.user.overview.Get('tabsettings', {})
                overviewWindow.OnOverviewTabChanged(newTabs, oldTabs)
            stateSvc = sm.StartService('state')
            stateSvc.SetDefaultShipLabel('default')
            stateSvc.ResetColors()
            default = sm.GetService('overviewPresetSvc').GetDefaultOverviewGroups('default')
            settings.user.overview.Set('overviewPresets', {'default': default})
            self.CloseByUser()

    def DoFontChange(self):
        self.ResetMinSize()

    def ResetMinSize(self):
        maxBtnWidth = max([ uiutil.GetChild(wnd, 'btns').width for wnd in self.sr.main.children if wnd.name == 'btnsmainparent' ])
        margin = 12
        minWidth = max(self.minWidth, maxBtnWidth + margin * 2)
        self.SetMinSize((minWidth, self.minHeight))

    ResetMinSize = uiutil.ParanoidDecoMethod(ResetMinSize, ('sr', 'main'))

    def SelectAll(self, *args):
        self.cachedScrollPos = self.sr.scroll.GetScrollProportion()
        groups = []
        for entry in self.sr.scroll.GetNodes():
            if entry.__guid__ == 'listentry.Checkbox':
                entry.checked = 1
                if entry.panel:
                    entry.panel.Load(entry)
            if entry.__guid__ == 'listentry.Group':
                for item in entry.groupItems:
                    if type(item[0]) == list:
                        groups += item[0]
                    else:
                        groups.append(item[0])

        if groups:
            sm.GetService('tactical').SetSettings('groups', groups)

    def DeselectAll(self, *args):
        self.cachedScrollPos = self.sr.scroll.GetScrollProportion()
        for entry in self.sr.scroll.GetNodes():
            if entry.__guid__ == 'listentry.Checkbox':
                entry.checked = 0
                if entry.panel:
                    entry.panel.Load(entry)

        sm.GetService('tactical').SetSettings('groups', [])

    def GetPresetsMenu(self):
        return sm.GetService('tactical').GetPresetsMenu()

    def GetShipLabelMenu(self):
        return [(localization.GetByLabel('UI/Overview/ShipLabelFormatPilotCC'), self.SetDefaultShipLabel, ('default',)), (localization.GetByLabel('UI/Overview/ShipLabelFormatPilotCCAA'), self.SetDefaultShipLabel, ('ally',)), (localization.GetByLabel('UI/Overview/ShipLabelFormatCCPilotAA'), self.SetDefaultShipLabel, ('corpally',))]

    def SetDefaultShipLabel(self, setting):
        sm.GetService('state').SetDefaultShipLabel(setting)
        self.LoadShips()

    def Load(self, key):
        if self.currentKey is None or self.currentKey != key:
            self.cachedScrollPos = 0
        self.currentKey = key
        self.sr.scroll.state = uiconst.UI_NORMAL
        if key == 'filtertypes':
            self.LoadTypes()
        elif key == 'filterstates':
            self.LoadStateFilters()
        elif key == 'columns':
            self.LoadColumns()
        elif key == 'appearance':
            self.sr.statetabs.AutoSelect()
        elif key == 'filters':
            self.sr.filtertabs.AutoSelect()
        elif key == 'ships':
            self.LoadShips()
        elif key == 'misc':
            self.sr.scroll.state = uiconst.UI_HIDDEN
        elif key == 'overviewTabs':
            self.sr.scroll.state = uiconst.UI_HIDDEN
        elif key == 'smartFilters':
            self.LoadSmartFilters()
        else:
            self.LoadFlags()

    def LoadStateFilters(self):
        scrolllist = []
        all = sm.GetService('state').GetStateProps()
        filtered = sm.GetService('tactical').GetFilteredStates() or []
        for flag, props in all.iteritems():
            data = util.KeyVal()
            data.label = props.text
            data.props = props
            data.checked = flag not in filtered
            data.cfgname = 'filteredStates'
            data.retval = flag
            data.flag = flag
            data.hint = props.hint
            data.OnChange = self.CheckBoxChange
            scrolllist.append(listentry.Get('FlagEntry', data=data))

        scrolllist = localizationUtil.Sort(scrolllist, key=lambda x: x.label)
        self.sr.scroll.Load(contentList=scrolllist, scrollTo=getattr(self, 'cachedScrollPos', 0.0))

    def LoadSmartFilters(self, selected = None):
        scrolllist = []
        stateMgr = sm.GetService('state')
        all = stateMgr.GetSmartFilterProps()
        filtered = sm.GetService('tactical').GetEwarFiltered() or []
        ewarTypeByState = stateMgr.GetEwarTypeByEwarState()
        for flag, props in all.iteritems():
            data = util.KeyVal()
            data.label = props.text
            data.props = props
            data.checked = ewarTypeByState[flag] not in filtered
            data.cfgname = 'smartFilters'
            data.retval = flag
            data.flag = flag
            data.hint = props.hint
            data.OnChange = self.CheckBoxChange
            data.GetMenu = lambda : None
            scrolllist.append(listentry.Get('FlagEntry', data=data))

        self.sr.scroll.Load(contentList=scrolllist, scrollTo=getattr(self, 'cachedScrollPos', 0.0))

    def LoadFlags(self, selected = None):
        where = self.sr.statetabs.GetSelectedArgs()
        flagOrder = sm.GetService('state').GetStateOrder(where)
        scrolllist = []
        i = 0
        for flag in flagOrder:
            props = sm.GetService('state').GetStateProps(flag)
            data = util.KeyVal()
            data.label = props.text
            data.props = props
            data.checked = sm.GetService('state').GetStateState(where, flag)
            data.cfgname = where
            data.retval = flag
            data.flag = flag
            data.canDrag = True
            data.hint = props.hint
            data.OnChange = self.CheckBoxChange
            data.isSelected = selected == i
            scrolllist.append(listentry.Get('FlagEntry', data=data))
            i += 1

        self.sr.scroll.Load(contentList=scrolllist, scrollTo=getattr(self, 'cachedScrollPos', 0.0))

    def LoadShips(self, selected = None):
        shipLabels = sm.GetService('state').GetShipLabels()
        allLabels = sm.GetService('state').GetAllShipLabels()
        self.sr.applyOnlyToShips.SetChecked(sm.GetService('state').GetHideCorpTicker())
        hints = {None: '',
         'corporation': localization.GetByLabel('UI/Common/CorpTicker'),
         'alliance': localization.GetByLabel('UI/Shared/AllianceTicker'),
         'pilot name': localization.GetByLabel('UI/Common/PilotName'),
         'ship name': localization.GetByLabel('UI/Common/ShipName'),
         'ship type': localization.GetByLabel('UI/Common/ShipType')}
        comments = {None: localization.GetByLabel('UI/Overview/AdditionalTextForCorpTicker'),
         'corporation': localization.GetByLabel('UI/Overview/OnlyShownForPlayerCorps'),
         'alliance': localization.GetByLabel('UI/Overview/OnlyShownWhenAvailable')}
        newlabels = [ label for label in allLabels if label['type'] not in [ alabel['type'] for alabel in shipLabels ] ]
        shipLabels += newlabels
        scrolllist = []
        for i, flag in enumerate(shipLabels):
            data = util.KeyVal()
            data.label = hints[flag['type']]
            data.checked = flag['state']
            data.cfgname = 'shiplabels'
            data.retval = flag
            data.flag = flag
            data.canDrag = True
            data.hint = hints[flag['type']]
            data.comment = comments.get(flag['type'], '')
            data.OnChange = self.CheckBoxChange
            data.isSelected = selected == i
            scrolllist.append(listentry.Get('ShipEntry', data=data))

        self.sr.scroll.Load(contentList=scrolllist, scrollTo=getattr(self, 'cachedScrollPos', 0.0))
        maxLeft = 140
        for shipEntry in self.sr.scroll.GetNodes():
            if shipEntry.panel:
                postLeft = shipEntry.panel.sr.label.left + shipEntry.panel.sr.label.textwidth + 4
                maxLeft = max(maxLeft, postLeft)

        for shipEntry in self.sr.scroll.GetNodes():
            if shipEntry.panel:
                shipEntry.panel.postCont.left = maxLeft

    def Move(self, idx = None, *args):
        self.cachedScrollPos = self.sr.scroll.GetScrollProportion()
        selected = self.sr.scroll.GetSelected()
        if selected:
            selected = selected[0]
            if idx is not None:
                if idx != selected.idx:
                    if selected.idx < idx:
                        newIdx = idx - 1
                    else:
                        newIdx = idx
                else:
                    return
            else:
                newIdx = max(0, selected.idx - 1)
            sm.GetService('state').ChangeStateOrder(self.GetWhere(), selected.flag, newIdx)
            self.LoadFlags(newIdx)

    def GetWhere(self):
        where = self.sr.statetabs.GetSelectedArgs()
        return where

    def ResetStateSettings(self, *args):
        where = self.sr.statetabs.GetSelectedArgs()
        settings.user.overview.Set('flagOrder', None)
        settings.user.overview.Set('iconOrder', None)
        settings.user.overview.Set('backgroundOrder', None)
        settings.user.overview.Set('flagStates', None)
        settings.user.overview.Set('iconStates', None)
        settings.user.overview.Set('backgroundStates', None)
        settings.user.overview.Set('stateColors', {})
        sm.GetService('state').InitColors(1)
        settings.user.overview.Set('stateBlinks', {})
        settings.user.overview.Set('applyOnlyToShips', 1)
        self.sr.applyOnlyToShips.SetChecked(1, 0)
        settings.user.overview.Set('useSmallColorTags', 0)
        self.sr.useSmallColorTags.SetChecked(0, 0)
        self.LoadFlags()
        sm.GetService('state').NotifyOnStateSetupChance('reset')

    def LoadColumns(self, selected = None):
        userSet = sm.GetService('tactical').GetColumns()
        userSetOrder = sm.GetService('tactical').GetColumnOrder()
        missingColumns = [ col for col in sm.GetService('tactical').GetAllColumns() if col not in userSetOrder ]
        userSetOrder += missingColumns
        i = 0
        scrolllist = []
        for columnID in userSetOrder:
            data = util.KeyVal()
            data.label = sm.GetService('tactical').GetColumnLabel(columnID)
            data.checked = columnID in userSet
            data.cfgname = 'columns'
            data.retval = columnID
            data.canDrag = True
            data.isSelected = selected == i
            data.OnChange = self.CheckBoxChange
            scrolllist.append(listentry.Get('ColumnEntry', data=data))
            i += 1

        self.sr.scroll.Load(contentList=scrolllist, scrollTo=getattr(self, 'cachedScrollPos', 0.0))

    def LoadTypes(self):
        categoryList = {}
        for groupID, name in sm.GetService('tactical').GetAvailableGroups():
            for cat, groupdict in self.specialGroups.iteritems():
                for group, groupIDs in groupdict.iteritems():
                    if groupID in groupIDs:
                        catName = cat
                        groupID = groupIDs
                        name = group
                        break
                else:
                    continue

                break
            else:
                catName = cfg.invcategories.Get(cfg.invgroups.Get(groupID).categoryID).name

            if catName not in categoryList:
                categoryList[catName] = [(groupID, name)]
            elif (groupID, name) not in categoryList[catName]:
                categoryList[catName].append((groupID, name))

        sortCat = categoryList.keys()
        sortCat.sort()
        scrolllist = []
        for catName in sortCat:
            data = {'GetSubContent': self.GetCatSubContent,
             'label': catName,
             'MenuFunction': self.GetSubFolderMenu,
             'id': ('GroupSel', catName),
             'groupItems': categoryList[catName],
             'showlen': 1,
             'sublevel': 0,
             'state': 'locked'}
            scrolllist.append(listentry.Get('Group', data))

        self.sr.scroll.Load(contentList=scrolllist, scrolltotop=0, scrollTo=getattr(self, 'cachedScrollPos', 0.0))

    def GetSubFolderMenu(self, node):
        m = [None, (localization.GetByLabel('UI/Common/SelectAll'), self.SelectGroup, (node, True)), (localization.GetByLabel('UI/Common/DeselectAll'), self.SelectGroup, (node, False))]
        return m

    def SelectGroup(self, node, isSelect):
        groups = []
        for entry in node.groupItems:
            if type(entry[0]) == list:
                for entry1 in entry[0]:
                    groups.append(entry1)

            else:
                groups.append(entry[0])

        sm.StartService('tactical').ChangeSettings('groups', groups, isSelect)

    def GetCatSubContent(self, nodedata, newitems = 0):
        userSettings = sm.GetService('tactical').GetGroups()
        scrolllist = []
        for groupID, name in nodedata.groupItems:
            if type(groupID) == list:
                for each in groupID:
                    if each in userSettings:
                        checked = 1
                        break
                else:
                    checked = 0

            else:
                name = cfg.invgroups.Get(groupID).groupName
                checked = groupID in userSettings
            data = util.KeyVal()
            data.label = name
            data.checked = checked
            data.cfgname = 'groups'
            data.retval = groupID
            data.OnChange = self.CheckBoxChange
            scrolllist.append(listentry.Get('Checkbox', data=data))

        return scrolllist

    def MoveColumn(self, idx = None, *args):
        self.cachedScrollPos = self.sr.scroll.GetScrollProportion()
        selected = self.sr.scroll.GetSelected()
        if selected:
            selected = selected[0]
            if idx is not None:
                if idx != selected.idx:
                    if selected.idx < idx:
                        newIdx = idx - 1
                    else:
                        newIdx = idx
                else:
                    return
            else:
                newIdx = max(0, selected.idx - 1)
            column = selected.retval
            current = sm.GetService('tactical').GetColumnOrder()[:]
            while column in current:
                current.remove(column)

            if idx == -1:
                idx = len(current)
            current.insert(idx, column)
            settings.user.overview.Set('overviewColumnOrder', current)
            self.LoadColumns(newIdx)
            overview = form.OverView.GetIfOpen()
            if overview:
                overview.FullReload()

    def ResetColumns(self, *args):
        settings.user.overview.Set('overviewColumnOrder', None)
        settings.user.overview.Set('overviewColumns', None)
        self.LoadColumns()
        sm.GetService('state').NotifyOnStateSetupChance('column reset')

    def CheckBoxChange(self, checkbox):
        if self and not self.destroyed:
            self.cachedScrollPos = self.sr.scroll.GetScrollProportion()
        if checkbox.data.has_key('config'):
            config = checkbox.data['config']
            if config == 'applyOnlyToShips':
                sm.GetService('tactical').SetNPCGroups()
                sm.GetService('state').InitFilter()
                sm.GetService('state').NotifyOnStateSetupChance('filter')
            elif config == 'hideCorpTicker':
                sm.GetService('bracket').UpdateLabels()
            elif config == 'useSmallColorTags':
                sm.GetService('state').NotifyOnStateSetupChance('filter')
            elif config == 'useSmallText':
                if checkbox.checked:
                    settings.user.overview.Set('useSmallText', 1)
                else:
                    settings.user.overview.Set('useSmallText', 0)
                overview = form.OverView.GetIfOpen()
                if overview:
                    overview.FullReload()
        if checkbox.data.has_key('key'):
            key = checkbox.data['key']
            if key == 'groups':
                sm.GetService('tactical').ChangeSettings(checkbox.data['key'], checkbox.data['retval'], checkbox.checked)
            elif key == 'columns':
                checked = checkbox.checked
                column = checkbox.data['retval']
                current = sm.GetService('tactical').GetColumns()[:]
                while column in current:
                    current.remove(column)

                if checked:
                    current.append(column)
                settings.user.overview.Set('overviewColumns', current)
                overview = form.OverView.GetIfOpen()
                if overview:
                    overview.FullReload()
            elif key == 'filteredStates':
                sm.GetService('tactical').ChangeSettings('filteredStates', checkbox.data['retval'], not checkbox.checked)
            elif key == 'smartFilters':
                sm.GetService('tactical').ChangeSettings('smartFilters', sm.GetService('state').GetEwarTypeByEwarState()[checkbox.data['retval']], not checkbox.checked)
            elif key == self.GetWhere():
                sm.GetService('state').ChangeStateState(self.GetWhere(), checkbox.data['retval'], checkbox.checked)
            elif key == 'shiplabels':
                sm.GetService('state').ChangeShipLabels(checkbox.data['retval'], checkbox.checked)
        blue.pyos.synchro.Yield()
        uicore.registry.SetFocus(self.sr.scroll)

    def EwarCheckBoxChanged(self, checkbox):
        sm.GetService('tactical').ChangeSettings('smartFilters', checkbox.name, checkbox.checked)

    def MoveShipLabel(self, idx = None, *args):
        self.cachedScrollPos = self.sr.scroll.GetScrollProportion()
        selected = self.sr.scroll.GetSelected()
        if selected:
            selected = selected[0]
            if idx is not None:
                if idx != selected.idx:
                    if selected.idx < idx:
                        newIdx = idx - 1
                    else:
                        newIdx = idx
                else:
                    return
            else:
                newIdx = max(0, selected.idx - 1)
            sm.GetService('state').ChangeLabelOrder(selected.idx, newIdx)
            self.LoadShips(newIdx)

    def UpdateOverviewTab(self, *args):
        tabSettings = {}
        for key in self.tabedit.keys():
            editContainer = self.tabedit.get(key, None)
            comboTabBracketContainer = self.comboTabBracket.get(key, None)
            comboTabOverviewContainer = self.comboTabOverview.get(key, None)
            if not (editContainer and comboTabOverviewContainer and comboTabBracketContainer):
                continue
            if not editContainer.text:
                continue
            tabSettings[key] = {'name': editContainer.text,
             'bracket': comboTabBracketContainer.selectedValue,
             'overview': comboTabOverviewContainer.selectedValue}

        oldtabsettings = settings.user.overview.Get('tabsettings', {})
        sm.ScatterEvent('OnOverviewTabChanged', tabSettings, oldtabsettings)

    def _OnResize(self, *args):
        self.UpdateStateTopHeight()

    def MiscCheckboxChange(self, cb, *args):
        configName = cb.data.get('config', '')
        if configName == 'showInTargetRange':
            if cb.checked:
                sm.GetService('bracket').EnableInTargetRange()
                for subCb in self.targetRangeSubCheckboxes:
                    subCb.Enable()
                    subCb.opacity = 1.0

            else:
                sm.GetService('bracket').DisableInTargetRange()
                for subCb in self.targetRangeSubCheckboxes:
                    subCb.Disable()
                    subCb.opacity = 0.3

        elif configName == 'showBiggestDamageDealers':
            if cb.checked:
                sm.GetService('bracket').EnableShowingDamageDealers()
            else:
                sm.GetService('bracket').DisableShowingDamageDealers()
        elif configName == 'targetCrosshair':
            sm.GetService('bracket').Reload()
        elif cb in self.targetRangeSubCheckboxes:
            sm.GetService('bracket').ShowInTargetRange()


class DraggableOverviewEntry(listentry.Checkbox):
    __guid__ = 'listentry.DraggableOverviewEntry'
    isDragObject = True

    def Startup(self, *args):
        listentry.Checkbox.Startup(self, args)
        self.sr.posIndicatorCont = uicls.Container(name='posIndicator', parent=self, align=uiconst.TOTOP, state=uiconst.UI_DISABLED, height=2)
        self.sr.posIndicator = uicls.Fill(parent=self.sr.posIndicatorCont, color=(1.0, 1.0, 1.0, 0.5))
        self.sr.posIndicator.state = uiconst.UI_HIDDEN
        self.canDrag = False

    def GetDragData(self, *args):
        if not self.sr.node.canDrag:
            return
        self.sr.node.scroll.SelectNode(self.sr.node)
        return [self.sr.node]

    def OnDropData(self, dragObj, nodes, *args):
        if util.GetAttrs(self, 'parent', 'OnDropData'):
            node = nodes[0]
            if util.GetAttrs(node, 'panel'):
                self.parent.OnDropData(dragObj, nodes, idx=self.sr.node.idx)

    def OnDragEnter(self, dragObj, nodes, *args):
        self.sr.posIndicator.state = uiconst.UI_DISABLED

    def OnDragExit(self, *args):
        self.sr.posIndicator.state = uiconst.UI_HIDDEN


class ColumnEntry(DraggableOverviewEntry):
    __guid__ = 'listentry.ColumnEntry'

    def Startup(self, *args):
        listentry.DraggableOverviewEntry.Startup(self, args)
        self.sr.checkbox.state = uiconst.UI_PICKCHILDREN
        diode = uiutil.GetChild(self, 'diode')
        diode.state = uiconst.UI_NORMAL
        diode.OnClick = self.ClickDiode

    def ClickDiode(self, *args):
        self.sr.checkbox.ToggleState()

    def OnClick(self, *args):
        listentry.Generic.OnClick(self, *args)


class FlagEntry(DraggableOverviewEntry):
    __guid__ = 'listentry.FlagEntry'

    def Startup(self, *args):
        listentry.DraggableOverviewEntry.Startup(self, args)
        self.sr.flag = None
        self.sr.checkbox.state = uiconst.UI_PICKCHILDREN
        diode = uiutil.GetChild(self, 'diode')
        diode.state = uiconst.UI_NORMAL
        diode.OnClick = self.ClickDiode

    def Load(self, node):
        listentry.Checkbox.Load(self, node)
        if self.sr.flag:
            f = self.sr.flag
            self.sr.flag = None
            f.Close()
        if node.cfgname not in ('filteredStates', 'smartFilters'):
            col = sm.GetService('state').GetStateColor(node.flag, where=node.cfgname)
            blink = sm.GetService('state').GetStateBlink(node.cfgname, node.flag)
            if node.cfgname == 'flag':
                icon = (node.props.iconIndex + 1) * 10
            else:
                icon = 0
            new = uicls.Container(parent=self, pos=(3, 4, 9, 9), name='flag', state=uiconst.UI_DISABLED, align=uiconst.TOPRIGHT, idx=0)
            flagIcon = uicls.Sprite(parent=new, pos=(0, 0, 10, 10), name='icon', state=uiconst.UI_DISABLED, rectWidth=10, rectHeight=10, texturePath='res:/UI/Texture/classes/Bracket/flagIcons.png', align=uiconst.RELATIVE, color=node.props.iconColor)
            flagBackground = uicls.Fill(parent=new, color=col)
            flagBackground.color.a *= 0.75
            if blink:
                sm.GetService('ui').BlinkSpriteA(flagIcon, 1.0, 500, None, passColor=0)
                sm.GetService('ui').BlinkSpriteA(flagBackground, 1.0, 500, None, passColor=0)
            flagIcon.rectLeft = icon
            self.sr.flag = new

    def ClickDiode(self, *args):
        self.sr.checkbox.ToggleState()

    def OnClick(self, *args):
        listentry.Generic.OnClick(self, *args)

    def GetMenu(self):
        if self.sr.node.GetMenu:
            return self.sr.node.GetMenu()
        colors = sm.GetService('state').GetStateColors()
        m = []
        for color, localizedName in colors.itervalues():
            m.append((uiutil.MenuLabel(localizedName), self.ChangeColor, (color,)))

        if self.sr.node.cfgname in ('flag', 'background'):
            m.append(None)
            m.append((uiutil.MenuLabel('UI/Overview/ToggleBlink'), self.ToggleBlink))
        return m

    def ToggleBlink(self):
        current = sm.GetService('state').GetStateBlink(self.sr.node.cfgname, self.sr.node.flag)
        sm.GetService('state').SetStateBlink(self.sr.node.cfgname, self.sr.node.flag, not current)
        self.Load(self.sr.node)

    def ChangeColor(self, color):
        sm.GetService('state').SetStateColor(self.sr.node.cfgname, self.sr.node.flag, color)
        self.Load(self.sr.node)


class ShipEntry(DraggableOverviewEntry):
    __guid__ = 'listentry.ShipEntry'

    def Startup(self, *args):
        listentry.DraggableOverviewEntry.Startup(self, args)
        self.sr.checkbox.state = uiconst.UI_PICKCHILDREN
        diode = uiutil.GetChild(self, 'diode')
        diode.state = uiconst.UI_NORMAL
        diode.OnClick = self.ClickDiode
        self.sr.preEdit = uicls.SinglelineEdit(name='edit', parent=self, align=uiconst.TOPLEFT, pos=(32, 0, 20, 0))
        self.sr.preEdit.OnChange = self.OnPreChange
        self.postCont = uicls.Container(parent=self, align=uiconst.TOALL, pos=(140, 0, 20, 0))
        self.sr.postEdit = uicls.SinglelineEdit(name='edit', parent=self.postCont, align=uiconst.TOPLEFT, pos=(0, 0, 20, 0))
        self.sr.postEdit.OnChange = self.OnPostChange
        self.sr.comment = uicls.EveLabelMedium(text='', parent=self.postCont, left=28, top=2, state=uiconst.UI_DISABLED)

    def Load(self, node):
        listentry.Checkbox.Load(self, node)
        self.sr.label.left = 60
        self.sr.preEdit.SetValue(self.sr.node.flag['pre'])
        self.sr.postEdit.SetValue(self.sr.node.flag['post'])
        if self.sr.node.flag['type'] is None:
            self.sr.postEdit.state = uiconst.UI_HIDDEN
        else:
            self.sr.postEdit.state = uiconst.UI_NORMAL
        self.sr.comment.text = self.sr.node.comment

    def ClickDiode(self, *args):
        self.sr.checkbox.ToggleState()

    def OnClick(self, *args):
        listentry.Generic.OnClick(self, *args)

    def OnPreChange(self, text, *args):
        if self.sr.node.flag['pre'] != text:
            self.sr.node.flag['pre'] = text.replace('<', '&lt;').replace('>', '&gt;')
            self.sr.node.OnChange(self.sr.checkbox)

    def OnPostChange(self, text, *args):
        if self.sr.node.flag['post'] != text:
            self.sr.node.flag['post'] = text.replace('<', '&lt;').replace('>', '&gt;')
            self.sr.node.OnChange(self.sr.checkbox)