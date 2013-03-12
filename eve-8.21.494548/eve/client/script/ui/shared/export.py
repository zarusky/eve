#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/ui/shared/export.py
import uix
import form
import util
import listentry
import os
import blue
import codecs
import sys
import uicls
import uiconst
import localization
from xml.dom.minidom import getDOMImplementation, parse

class ImportBaseWindow(uicls.Window):
    __guid__ = 'form.ImportBaseWindow'

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        self.SetMinSize([450, 250])
        self.minWidth = 225
        self.SetTopparentHeight(0)
        self.SetWndIcon(None)
        self.scrollWidth = 0
        dirpath = attributes.get('dirpath', None)
        if dirpath:
            self.dirpath = dirpath
        else:
            self.dirpath = os.path.join(blue.win32.SHGetFolderPath(blue.win32.CSIDL_PERSONAL), 'EVE', 'Overview')
        self.ConstructLayout()

    def ConstructLayout(self, *args):
        self.sr.fileContainer = uicls.Container(name='fileContainer', align=uiconst.TOLEFT, parent=self.sr.main, top=const.defaultPadding, width=256)
        self.sr.profilesContainer = uicls.Container(name='profilesContainer', align=uiconst.TOALL, parent=self.sr.main, pos=(0, 0, 0, 0))
        fileTopCont = uicls.Container(name='fileTopCont', parent=self.sr.fileContainer, align=uiconst.TOTOP, height=40)
        fileScrollCont = uicls.Container(name='fileScrollCont', parent=self.sr.fileContainer, align=uiconst.TOALL)
        self.sr.fileHeader = uicls.CaptionLabel(text=localization.GetByLabel('UI/Common/Files/FileName'), parent=fileTopCont, left=const.defaultPadding, top=const.defaultPadding)
        self.sr.fileHeader.fontsize = 14
        self.sr.fileScroll = uicls.Scroll(name='fileScroll', parent=fileScrollCont, padding=(const.defaultPadding,
         0,
         const.defaultPadding,
         const.defaultPadding))
        self.sr.refreshFileListBtn = uicls.ButtonGroup(btns=[[localization.GetByLabel('UI/Commands/Refresh'),
          self.RefreshFileList,
          (),
          None]], parent=self.sr.fileContainer, idx=0)
        profilesTopCont = uicls.Container(name='fileTopCont', parent=self.sr.profilesContainer, align=uiconst.TOTOP, height=40)
        profilesScrollCont = uicls.Container(name='fileScrollCont', parent=self.sr.profilesContainer, align=uiconst.TOALL)
        self.sr.profilesHeader = uicls.CaptionLabel(text=localization.GetByLabel('UI/Common/PleaseSelect'), parent=profilesTopCont, left=const.defaultPadding, top=const.defaultPadding)
        self.sr.profilesHeader.fontsize = 14
        self.checkAllCB = uicls.Checkbox(text=localization.GetByLabel('UI/Shared/CheckAllOn'), parent=profilesTopCont, align=uiconst.TOBOTTOM, height=16, padLeft=const.defaultPadding, callback=self.CheckAll, checked=True)
        self.sr.profilesScroll = uicls.Scroll(name='profilesScroll', parent=profilesScrollCont, padding=(const.defaultPadding,
         0,
         const.defaultPadding,
         const.defaultPadding))
        self.sr.importProfilesBtn = uicls.ButtonGroup(btns=[[localization.GetByLabel('UI/Commands/Import'),
          self.Import,
          (),
          None]], parent=self.sr.profilesContainer, idx=0)
        self.sr.importProfilesBtn.state = uiconst.UI_HIDDEN
        self.RefreshFileList()

    def RefreshFileList(self, *args):
        filelist = []
        if os.path.exists(self.dirpath):
            for file in os.listdir(self.dirpath):
                if file.endswith('.xml'):
                    filelist.append(listentry.Get('Generic', {'label': file[:-4],
                     'OnClick': self.OnFileSelected}))

        self.sr.fileScroll.Load(contentList=filelist)

    def OnChange(self, *args):
        self.sr.importProfilesBtn.state = uiconst.UI_HIDDEN
        for checkbox in self.sr.profilesScroll.GetNodes():
            if getattr(checkbox, 'checked', None):
                self.sr.importProfilesBtn.state = uiconst.UI_NORMAL
                break

    def Import(self, *args):
        raise NotImplementedError('')

    def OnFileSelected(self, entry):
        raise NotImplementedError('')

    def CheckAll(self, *args):
        for entry in self.sr.profilesScroll.GetNodes():
            if entry.__guid__ == 'listentry.Checkbox':
                entry.checked = self.checkAllCB.checked
                if entry.panel:
                    entry.panel.Load(entry)


class ExportBaseWindow(uicls.Window):
    __guid__ = 'form.ExportBaseWindow'

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        dirpath = attributes.get('dirpath', None)
        if dirpath:
            self.dirpath = dirpath
        else:
            self.dirpath = os.path.join(blue.win32.SHGetFolderPath(blue.win32.CSIDL_PERSONAL), 'EVE', 'Overview')
        self.SetTopparentHeight(0)
        self.SetWndIcon(None)
        self.SetMinSize([370, 270])
        self.ConstructLayout()

    def ConstructLayout(self, *args):
        topCont = uicls.Container(name='topCont', align=uiconst.TOTOP, height=14, parent=self.sr.main)
        left = const.defaultPadding
        self.sr.buttonContainer = uicls.Container(name='buttonContainer', align=uiconst.TOBOTTOM, parent=self.sr.main)
        self.checkAllCB = uicls.Checkbox(text=localization.GetByLabel('UI/Shared/CheckAllOn'), parent=topCont, align=uiconst.TOTOP, height=16, padLeft=left, callback=self.CheckAll, checked=True)
        left = const.defaultPadding
        self.sr.filenameLabel = uicls.EveLabelMedium(text=localization.GetByLabel('UI/Common/Files/FileName'), parent=self.sr.buttonContainer, top=const.defaultPadding, left=left, state=uiconst.UI_NORMAL)
        left += self.sr.filenameLabel.width + const.defaultPadding
        self.sr.filename = uicls.SinglelineEdit(name='filename', parent=self.sr.buttonContainer, pos=(left,
         const.defaultPadding,
         150,
         0), align=uiconst.TOPLEFT)
        self.sr.filename.SetMaxLength(32)
        left += self.sr.filename.width + const.defaultPadding
        self.sr.exportBtn = uicls.Button(parent=self.sr.buttonContainer, label=localization.GetByLabel('UI/Commands/Export'), func=self.Export, btn_default=1, idx=0, pos=(left,
         const.defaultPadding,
         0,
         0))
        self.sr.buttonContainer.height = self.sr.filename.height + 10
        self.sr.scrolllistcontainer = uicls.Container(name='scrolllistcontainer', align=uiconst.TOALL, parent=self.sr.main, pos=(0, 0, 0, 0))
        self.sr.scroll = uicls.Scroll(name='scroll', parent=self.sr.scrolllistcontainer, padding=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding))
        self.ConstructScrollList()

    def CheckAll(self, *args):
        for entry in self.sr.scroll.GetNodes():
            if entry.__guid__ == 'listentry.Checkbox':
                entry.checked = self.checkAllCB.checked
                if entry.panel:
                    entry.panel.Load(entry)

    def OnSelectionChanged(self, c):
        self.sr.exportBtn.state = uiconst.UI_HIDDEN
        for entry in self.sr.scroll.GetNodes():
            if entry.checked:
                self.sr.exportBtn.state = uiconst.UI_NORMAL
                break


class ExportFittingsWindow(ExportBaseWindow):
    __guid__ = 'form.ExportFittingsWindow'
    default_windowID = 'ExportFittingsWindow'

    def ApplyAttributes(self, attributes):
        self.isCorp = attributes.isCorp
        self.fittingSvc = sm.StartService('fittingSvc')
        dirpath = os.path.join(blue.win32.SHGetFolderPath(blue.win32.CSIDL_PERSONAL), 'EVE', 'Overview')
        attributes.dirpath = dirpath
        form.ExportBaseWindow.ApplyAttributes(self, attributes)
        self.SetWndIcon('ui_17_128_4')
        self.SetCaption(localization.GetByLabel('UI/Fitting/ExportFittings'))

    def ConstructScrollList(self):
        fittings = self.fittingSvc.GetAllFittings()
        scrolllist = []
        fittingList = []
        for fittingID, fitting in fittings.iteritems():
            if self.isCorp:
                if fitting.ownerID == session.corpid:
                    fittingList.append((fitting.name, fitting))
            elif fitting.ownerID == session.charid:
                fittingList.append((fitting.name, fitting))

        fittingList.sort()
        for fittingName, fitting in fittingList:
            data = util.KeyVal()
            data.label = fittingName
            data.checked = True
            data.cfgname = 'groups'
            data.retval = True
            data.report = False
            data.OnChange = self.OnSelectionChanged
            data.fitting = fitting
            scrolllist.append(listentry.Get('Checkbox', data=data))

        self.sr.scroll.Load(contentList=scrolllist)

    def Export(self, *args):
        if self.sr.filename.GetValue().strip() == '':
            raise UserError('NameInvalid')
        impl = getDOMImplementation()
        newdoc = impl.createDocument(None, 'fittings', None)
        try:
            docEl = newdoc.documentElement
            export = {}
            for entry in self.sr.scroll.GetNodes():
                if not entry.checked:
                    continue
                profile = newdoc.createElement('fitting')
                docEl.appendChild(profile)
                profile.attributes['name'] = entry.fitting.name
                element = newdoc.createElement('description')
                element.attributes['value'] = entry.fitting.Get('description')
                profile.appendChild(element)
                element = newdoc.createElement('shipType')
                shipType = cfg.invtypes.Get(entry.fitting.Get('shipTypeID')).typeName
                element.attributes['value'] = shipType
                profile.appendChild(element)
                for typeID, flag, qty in entry.fitting.fitData:
                    typeName = cfg.invtypes.Get(typeID).typeName
                    hardWareElement = newdoc.createElement('hardware')
                    hardWareElement.attributes['type'] = typeName
                    slot = self.GetSlotFromFlag(flag)
                    hardWareElement.attributes['slot'] = slot
                    if flag in (const.flagDroneBay, const.flagCargo):
                        hardWareElement.attributes['qty'] = str(qty)
                    profile.appendChild(hardWareElement)

            filename = self.sr.filename.GetValue()
            illegalFileNameChars = ['?',
             '*',
             ':',
             ';',
             '~',
             '\\',
             '/',
             '"',
             '|']
            for char in illegalFileNameChars:
                if char in filename:
                    eve.Message('IllegalFilename')
                    return

            self.dirpath = os.path.join(blue.win32.SHGetFolderPath(blue.win32.CSIDL_PERSONAL), 'EVE', 'fittings')
            filepath = os.path.join(self.dirpath, self.sr.filename.GetValue() + '.xml')
            if not os.path.exists(self.dirpath):
                os.makedirs(self.dirpath)
            if os.path.exists(filepath):
                if eve.Message('FileExists', {}, uiconst.YESNO) == uiconst.ID_NO:
                    return
            outfile = codecs.open(filepath, 'w', 'utf-8')
            newdoc.writexml(outfile, indent='\t', addindent='\t', newl='\n')
            self.CloseByUser()
            eve.Message('FittingExportDone', {'filename': filepath})
        finally:
            newdoc.unlink()

    def GetSlotFromFlag(self, flag):
        if flag >= const.flagHiSlot0 and flag <= const.flagHiSlot7:
            return 'hi slot ' + str(flag - const.flagHiSlot0)
        if flag >= const.flagMedSlot0 and flag <= const.flagMedSlot7:
            return 'med slot ' + str(flag - const.flagMedSlot0)
        if flag >= const.flagLoSlot0 and flag <= const.flagLoSlot7:
            return 'low slot ' + str(flag - const.flagLoSlot0)
        if flag >= const.flagRigSlot0 and flag <= const.flagRigSlot7:
            return 'rig slot ' + str(flag - const.flagRigSlot0)
        if flag >= const.flagSubSystemSlot0 and flag <= const.flagSubSystemSlot7:
            return 'subsystem slot ' + str(flag - const.flagSubSystemSlot0)
        if flag == const.flagCargo:
            return 'cargo'
        if flag == const.flagDroneBay:
            return 'drone bay'


class ExportOverviewWindow(ExportBaseWindow):
    __guid__ = 'form.ExportOverviewWindow'
    default_windowID = 'ExportOverviewWindow'

    def ApplyAttributes(self, attributes):
        dirpath = os.path.join(blue.win32.SHGetFolderPath(blue.win32.CSIDL_PERSONAL), 'EVE', 'Overview')
        attributes.dirpath = dirpath
        form.ExportBaseWindow.ApplyAttributes(self, attributes)
        self.fittingSvc = sm.StartService('fittingSvc')
        self.SetCaption(localization.GetByLabel('UI/Commands/ExportOverviewSettings'))

    def ConstructScrollList(self):
        scrolllist = []
        globalSettings = util.KeyVal()
        globalSettings.label = localization.GetByLabel('UI/Overview/GlobalOverviewSettings')
        globalSettings.checked = True
        globalSettings.cfgname = 'groups'
        globalSettings.retval = True
        globalSettings.OnChange = self.OnSelectionChanged
        scrolllist.append(listentry.Get('Checkbox', data=globalSettings))
        tabs = settings.user.overview.Get('overviewPresets', {})
        defaultOverviewNames = sm.GetService('overviewPresetSvc').GetDefaultOverviewNameList()
        for name in tabs.keys():
            if name in ('ccp_notsaved',) or name in defaultOverviewNames:
                continue
            data = util.KeyVal()
            data.label = name
            data.checked = True
            data.cfgname = 'groups'
            data.retval = True
            data.report = False
            data.OnChange = self.OnSelectionChanged
            scrolllist.append(listentry.Get('Checkbox', data=data))

        self.sr.scroll.Load(contentList=scrolllist)

    def Export(self, a):
        if self.sr.filename.GetValue().strip() == '':
            eve.Message('FilenameMissing')
            return
        impl = getDOMImplementation()
        newdoc = impl.createDocument(None, 'eveOverview', None)
        try:
            docEl = newdoc.documentElement
            tabs = settings.user.overview.Get('overviewPresets', {})
            export = {}
            selectedProfiles = []
            for entry in self.sr.scroll.GetNodes():
                if not entry.checked or entry.label in (localization.GetByLabel('UI/Overview/GlobalOverviewSettings'),):
                    continue
                selectedProfiles.append(entry.label)

            for tab in settings.user.overview.Get('tabsettings', {}).values():
                if tab['overview'] in selectedProfiles and tab['bracket'] in selectedProfiles:
                    tabElement = newdoc.createElement('tab')
                    docEl.appendChild(tabElement)
                    for k, v in tab.items():
                        tabElement.attributes[k] = str(v)

            for entry in self.sr.scroll.GetNodes():
                if not entry.checked:
                    continue
                if entry.label in ('default',):
                    continue
                elif entry.label == localization.GetByLabel('UI/Overview/GlobalOverviewSettings'):
                    profile = newdoc.createElement('globalSettings')
                    docEl.appendChild(profile)
                    for setting in ['useSmallColorTags',
                     'applyOnlyToShips',
                     'hideCorpTicker',
                     'overviewBroadcastsToTop']:
                        element = newdoc.createElement(setting)
                        element.attributes['value'] = str(settings.user.overview.Get(setting, None))
                        profile.appendChild(element)

                    columns = sm.StartService('tactical').GetColumns()
                    columnsElement = newdoc.createElement('columns')
                    profile.appendChild(columnsElement)
                    for columnName in columns:
                        columnElement = newdoc.createElement('column')
                        columnElement.attributes['id'] = str(columnName)
                        columnsElement.appendChild(columnElement)

                    labels = settings.user.overview.Get('shipLabels', None)
                    if labels:
                        labelsElement = newdoc.createElement('shipLabels')
                        profile.appendChild(labelsElement)
                        for label in labels:
                            columnElement = newdoc.createElement('label')
                            for partName, partValue in label.items():
                                partElement = newdoc.createElement('part')
                                partElement.attributes['name'] = partName
                                partElement.attributes['value'] = str(partValue)
                                columnElement.appendChild(partElement)

                            labelsElement.appendChild(columnElement)

                else:
                    profile = newdoc.createElement('profile')
                    profile.attributes['name'] = entry.label
                    docEl.appendChild(profile)
                    groupsTag = newdoc.createElement('groups')
                    profile.appendChild(groupsTag)
                    for group in tabs[entry.label]['groups']:
                        groupElement = newdoc.createElement('group')
                        groupElement.attributes['id'] = str(group)
                        groupsTag.appendChild(groupElement)

                    filteredStatesTag = newdoc.createElement('filteredStates')
                    profile.appendChild(filteredStatesTag)
                    if 'filteredStates' in tabs[entry.label]:
                        for state in tabs[entry.label]['filteredStates']:
                            stateElement = newdoc.createElement('state')
                            stateElement.attributes['state'] = str(state)
                            filteredStatesTag.appendChild(stateElement)

                    ewarFilters = newdoc.createElement('ewarFilters')
                    profile.appendChild(ewarFilters)
                    if 'ewarFilters' in tabs[entry.label]:
                        for filter in tabs[entry.label]['ewarFilters']:
                            filterElement = newdoc.createElement('filter')
                            filterElement.attributes['id'] = filter
                            ewarFilters.appendChild(filterElement)

            filename = self.sr.filename.GetValue()
            illegalFileNameChars = ['?',
             '*',
             ':',
             ';',
             '~',
             '\\',
             '/']
            for char in illegalFileNameChars:
                if char in filename:
                    eve.Message('IllegalFilename')
                    return

            filepath = os.path.join(self.dirpath, self.sr.filename.GetValue() + '.xml')
            if not os.path.exists(self.dirpath):
                os.makedirs(self.dirpath)
            if os.path.exists(filepath):
                if eve.Message('FileExists', {}, uiconst.YESNO) != uiconst.ID_YES:
                    return
            outfile = codecs.open(filepath, 'w', 'utf-8')
            newdoc.writexml(outfile, indent='\t', addindent='\t', newl='\n')
            self.CloseByUser()
            eve.Message('OverviewExportDone', {'filename': filepath})
        finally:
            newdoc.unlink()


class ImportFittingsWindow(ImportBaseWindow):
    __guid__ = 'form.ImportFittingsWindow'
    default_windowID = 'ImportFittingsWindow'

    def ApplyAttributes(self, attributes):
        dirpath = os.path.join(blue.win32.SHGetFolderPath(blue.win32.CSIDL_PERSONAL), 'EVE', 'Fittings')
        attributes.dirpath = dirpath
        form.ImportBaseWindow.ApplyAttributes(self, attributes)
        self.SetCaption(localization.GetByLabel('UI/Fitting/ImportFittings'))
        self.SetWndIcon('ui_17_128_4')
        self.fittingSvc = sm.StartService('fittingSvc')
        uicls.WndCaptionLabel(text=localization.GetByLabel('UI/Fitting/ImportFittings'), parent=self.sr.topParent)

    def OnFileSelected(self, entry):
        filepath = os.path.join(self.dirpath, entry.sr.node.label + '.xml')
        self.sr.selectedFileName = entry.sr.node.label
        profileCheckboxes = []
        try:
            doc = parse(filepath)
            try:
                profiles = doc.documentElement.getElementsByTagName('fitting')
                for x in profiles:
                    fitting = util.KeyVal()
                    fitting.label = x.attributes['name'].value
                    fitting.checked = True
                    fitting.cfgname = 'profiles'
                    fitting.retval = True
                    fitting.OnChange = self.OnChange
                    profileCheckboxes.append(listentry.Get('Checkbox', data=fitting))

                self.sr.importProfilesBtn.state = uiconst.UI_NORMAL
            finally:
                doc.unlink()

        except Exception as e:
            raise 
            profileCheckboxes = [listentry.Get('Generic', {'label': localization.GetByLabel('UI/Common/Files/FileNotValid')})]
            self.sr.importProfilesBtn.state = uiconst.UI_HIDDEN

        self.sr.profilesScroll.Load(contentList=profileCheckboxes)
        self.OnChange()

    def Import(self, *args):
        filepath = os.path.join(self.dirpath, self.sr.selectedFileName + '.xml')
        godma = sm.GetService('godma')
        doc = parse(filepath)
        try:
            fittings = doc.documentElement.getElementsByTagName('fitting')
            fittingsDict = {}
            borkedTypeNames = set()
            borkedFlags = set()
            for checkbox in self.sr.profilesScroll.GetNodes():
                if not checkbox.checked:
                    continue
                fittingName = checkbox.label
                kv = util.KeyVal()
                for fitting in fittings:
                    if fitting.attributes['name'].value != fittingName:
                        continue
                    descriptionElements = fitting.getElementsByTagName('description')
                    if descriptionElements > 0:
                        description = descriptionElements[0].attributes['value'].value
                    else:
                        description = ''
                    shipTypeName = fitting.getElementsByTagName('shipType')[0].attributes['value'].value
                    try:
                        shipTypeID = godma.GetTypeFromName(shipTypeName).typeID
                    except KeyError:
                        sys.exc_clear()
                        borkedTypeNames.add(shipTypeName)
                        continue

                    shipTypeID = int(shipTypeID)
                    fitData = {}
                    for hardwareElement in fitting.getElementsByTagName('hardware'):
                        typeName = hardwareElement.attributes['type'].value
                        try:
                            typeID = godma.GetTypeFromName(typeName).typeID
                        except KeyError:
                            borkedTypeNames.add(typeName)
                            sys.exc_clear()
                            continue

                        slot = hardwareElement.attributes['slot'].value
                        flag = self.GetFlagFromSlot(slot)
                        if flag is None:
                            borkedFlags.add(typeName)
                            continue
                        categoryID = cfg.invtypes.Get(typeID).categoryID
                        if categoryID in [const.categoryModule, const.categorySubSystem]:
                            qty = 1
                        else:
                            qty = hardwareElement.attributes['qty'].value
                            qty = int(qty)
                        fitData[typeID, flag] = (typeID, flag, qty)

                    kv.name = fittingName
                    kv.description = description
                    kv.shipTypeID = shipTypeID
                    kv.fitData = fitData.values()
                    kv.ownerID = None
                    kv.fittingID = fittingName
                    fittingsDict[fittingName] = kv

            text = ''
            if len(borkedTypeNames) > 0:
                text += localization.GetByLabel('UI/Fitting/MalformedXML')
                text += '<br><br>'
                for typeName in borkedTypeNames:
                    text += typeName + '<br>'

            if len(borkedFlags) > 0:
                if len(text) > 0:
                    text += '<br><br>'
                text += localization.GetByLabel('UI/Fitting/MalformedFlagInformation')
                text += '<br><br>'
                for typeName in borkedTypeNames:
                    text += typeName + '<br>'

            if len(text) > 0:
                eve.Message('CustomInfo', {'info': text})
            self.fittingSvc.PersistManyFittings(session.charid, fittingsDict.values())
            self.CloseByUser()
        finally:
            doc.unlink()

    def GetFlagFromSlot(self, slot):
        if slot == 'drone bay':
            return const.flagDroneBay
        if slot == 'cargo':
            return const.flagCargo
        if slot.startswith('hi slot'):
            offset = int(slot[-1])
            return const.flagHiSlot0 + offset
        if slot.startswith('med slot'):
            offset = int(slot[-1])
            return const.flagMedSlot0 + offset
        if slot.startswith('low slot'):
            offset = int(slot[-1])
            return const.flagLoSlot0 + offset
        if slot.startswith('rig slot'):
            offset = int(slot[-1])
            return const.flagRigSlot0 + offset
        if slot.startswith('subsystem slot'):
            offset = int(slot[-1])
            return const.flagSubSystemSlot0 + offset


class ImportOverviewWindow(ImportBaseWindow):
    __guid__ = 'form.ImportOverviewWindow'
    default_windowID = 'ImportOverviewWindow'

    def ApplyAttributes(self, attributes):
        dirpath = os.path.join(blue.win32.SHGetFolderPath(blue.win32.CSIDL_PERSONAL), 'EVE', 'Overview')
        attributesdirpath = dirpath
        form.ImportBaseWindow.ApplyAttributes(self, attributes)
        self.SetCaption(localization.GetByLabel('UI/Overview/ImportOverviewSettings'))
        uicls.WndCaptionLabel(text=localization.GetByLabel('UI/Overview/ImportOverviewSettings'), parent=self.sr.topParent)
        self.sr.fileScroll.multiSelect = False

    def OnFileSelected(self, entry):
        filepath = os.path.join(self.dirpath, entry.sr.node.label + '.xml')
        self.sr.selectedFileName = entry.sr.node.label
        profileCheckboxes = []
        try:
            doc = parse(filepath)
            try:
                profiles = doc.documentElement.getElementsByTagName('profile')
                for x in profiles:
                    globalSettings = util.KeyVal()
                    globalSettings.label = x.attributes['name'].value
                    globalSettings.checked = True
                    globalSettings.cfgname = 'profiles'
                    globalSettings.retval = True
                    globalSettings.OnChange = self.OnChange
                    profileCheckboxes.append(listentry.Get('Checkbox', data=globalSettings))

                if len(doc.documentElement.getElementsByTagName('globalSettings')):
                    globalSettings = util.KeyVal()
                    globalSettings.label = localization.GetByLabel('UI/Overview/GlobalOverviewSettings')
                    globalSettings.checked = True
                    globalSettings.cfgname = 'profiles'
                    globalSettings.retval = True
                    globalSettings.OnChange = self.OnChange
                    profileCheckboxes.append(listentry.Get('Checkbox', data=globalSettings))
                self.sr.importProfilesBtn.state = uiconst.UI_NORMAL
            finally:
                doc.unlink()

        except Exception as e:
            profileCheckboxes = [listentry.Get('Generic', {'label': localization.GetByLabel('UI/Common/Files/FileNotValid')})]
            self.sr.importProfilesBtn.state = uiconst.UI_HIDDEN

        self.sr.profilesScroll.Load(contentList=profileCheckboxes)
        self.OnChange()

    def Import(self, *args):
        dirpath = os.path.join(blue.win32.SHGetFolderPath(blue.win32.CSIDL_PERSONAL), 'EVE', 'Overview')
        filepath = os.path.join(dirpath, self.sr.selectedFileName + '.xml')
        doc = parse(filepath)
        try:
            profiles = doc.documentElement.getElementsByTagName('profile')
            ov = settings.user.overview.Get('overviewPresets', {})
            miscSettings = {}
            selectedProfiles = []
            shipLabels = None
            overviewColumns = None
            newTabSettings = None
            closeWindow = True
            for checkbox in self.sr.profilesScroll.GetNodes():
                if checkbox.checked:
                    profileName = checkbox.label
                    if profileName in ov and eve.Message('OverviewProfileExists', {'name': profileName}, uiconst.YESNO) != uiconst.ID_YES:
                        closeWindow = False
                        continue
                    if profileName == localization.GetByLabel('UI/Overview/GlobalOverviewSettings'):
                        settingsElement = doc.documentElement.getElementsByTagName('globalSettings')[0]
                        for setting in ['useSmallColorTags',
                         'applyOnlyToShips',
                         'hideCorpTicker',
                         'overviewBroadcastsToTop']:
                            element = settingsElement.getElementsByTagName(setting)[0]
                            value = bool(element.attributes['value'])
                            miscSettings[setting] = value

                        overviewColumns = []
                        columnsElement = settingsElement.getElementsByTagName('columns')[0]
                        for columnElement in columnsElement.getElementsByTagName('column'):
                            overviewColumns.append(columnElement.attributes['id'].value)

                        shipLabels = []
                        if len(settingsElement.getElementsByTagName('shipLabels')):
                            shipLabelsElement = settingsElement.getElementsByTagName('shipLabels')[0]
                            shipLabelElements = shipLabelsElement.getElementsByTagName('label')
                            for sle in shipLabelElements:
                                d = {}
                                for shipLabelPartElement in sle.getElementsByTagName('part'):
                                    n = shipLabelPartElement.attributes['name'].value
                                    v = shipLabelPartElement.attributes['value'].value
                                    if n == 'state':
                                        v = int(v)
                                    if v == 'None':
                                        v = None
                                    d[n] = v

                                shipLabels.append(d)

                        stateService = sm.StartService('state')
                        if hasattr(stateService, 'shipLabels'):
                            delattr(stateService, 'shipLabels')
                        continue
                    selectedProfiles.append(profileName)
                    for profile in profiles:
                        groups = []
                        filteredStates = []
                        ewarFilters = []
                        if profile.attributes['name'].value == profileName:
                            for groupElement in profile.getElementsByTagName('groups')[0].getElementsByTagName('group'):
                                groups.append(int(groupElement.attributes['id'].value))

                            for el in profile.getElementsByTagName('filteredStates')[0].getElementsByTagName('state'):
                                filteredStates.append(int(el.attributes['state'].value))

                            for el in profile.getElementsByTagName('ewarFilters')[0].getElementsByTagName('filter'):
                                ewarFilters.append(el.attributes['id'].value)

                            ov[profileName] = {'groups': groups,
                             'filteredStates': filteredStates,
                             'ewarFilters': ewarFilters}

            oldTabSettings = settings.user.overview.Get('tabsettings', {})
            tabsChanged = False
            tabsData = {}
            id = 0
            for tabElement in doc.documentElement.getElementsByTagName('tab'):
                if id >= 5:
                    eve.Message('TooManyTabsImported')
                    break
                overviewProfileName = tabElement.attributes['overview'].value
                bracketProfileName = tabElement.attributes['bracket'].value
                if overviewProfileName in selectedProfiles and bracketProfileName in selectedProfiles:
                    tabdata = {}
                    for attributeName in ('name', 'overview', 'showNone', 'showSpecials', 'showAll', 'bracket'):
                        attribute = tabElement.getAttribute(attributeName)
                        if attribute:
                            if attribute in ('showNone', 'showSpecials', 'showAll'):
                                attribute = bool(attribute)
                            tabdata[attributeName] = attribute

                    tabsData[id] = tabdata
                    tabsChanged = True
                    id += 1

            settings.user.overview.Set('overviewPresets', ov)
            if overviewColumns:
                settings.user.overview.Set('overviewColumns', overviewColumns)
            if shipLabels:
                settings.user.overview.Set('shipLabels', shipLabels)
            for k, v in miscSettings.items():
                settings.user.overview.Set(k, v)

            sm.StartService('tactical').PrimePreset()
            overviewWindow = form.OverView.GetIfOpen()
            if overviewWindow:
                if tabsChanged:
                    overviewWindow.OnOverviewTabChanged(tabsData, oldTabSettings)
                else:
                    overviewWindow.FullReload()
            if closeWindow:
                self.CloseByUser()
        finally:
            doc.unlink()


class ImportLegacyFittingsWindow(ExportBaseWindow):
    __guid__ = 'form.ImportLegacyFittingsWindow'
    default_windowID = 'ImportLegacyFittingsWindow'

    def OnSelectionChanged(self, c):
        checkedCount = 0
        for entry in self.sr.scroll.GetNodes():
            if entry.checked:
                checkedCount += 1

        text = localization.GetByLabel('UI/Fitting/MovingCount', count=checkedCount, total=self.totalLocalFittings)
        if self.fittingCount > 0:
            text += ' (' + localization.GetByLabel('UI/Common/Files/CurrentlySaved', count=self.fittingCount) + ')'
        self.sr.countSelectedTextLabel.text = text
        if not self.okBtn.disabled and self.fittingCount + checkedCount > const.maxCharFittings:
            self.okBtn.Disable()
        elif self.okBtn.disabled and self.fittingCount + checkedCount <= const.maxCharFittings:
            self.okBtn.Enable()

    def ApplyAttributes(self, attributes):
        self.fittingSvc = sm.StartService('fittingSvc')
        self.fittingCount = len(self.fittingSvc.GetFittingMgr(session.charid).GetFittings(session.charid))
        uicls.Window.ApplyAttributes(self, attributes)
        self.SetTopparentHeight(0)
        self.SetWndIcon(None)
        self.SetMinSize([370, 270])
        self.SetWndIcon('ui_17_128_04')
        self.SetCaption(localization.GetByLabel('UI/Fitting/MoveToServer'))
        self.ConstructLayout()

    def ConstructLayout(self, *args):
        self.countSelectedText = ''
        self.sr.textContainer = uicls.Container(name='textContainer', align=uiconst.TOTOP, parent=self.sr.main, height=65, padding=const.defaultPadding)
        self.sr.textLabel = uicls.EveLabelMedium(text=localization.GetByLabel('UI/Fitting/LegacyImport', maxFittings=const.maxCharFittings), align=uiconst.TOTOP, parent=self.sr.textContainer)
        self.sr.textContainer2 = uicls.Container(name='textContainer', align=uiconst.TOTOP, parent=self.sr.main, height=15, padding=const.defaultPadding)
        self.sr.countSelectedTextLabel = uicls.EveLabelMedium(text=self.countSelectedText, align=uiconst.TOALL, parent=self.sr.textContainer2)
        self.sr.buttonContainer = uicls.Container(name='buttonContainer', align=uiconst.TOBOTTOM, parent=self.sr.main)
        btns = [[localization.GetByLabel('UI/Generic/Cancel'),
          self.CloseByUser,
          None,
          81], [localization.GetByLabel('UI/Generic/OK'),
          self.Import,
          None,
          81]]
        self.buttonGroup = uicls.ButtonGroup(btns=btns, parent=self.sr.buttonContainer)
        self.okBtn = self.buttonGroup.children[0].children[1]
        self.sr.buttonContainer.height = 23
        self.sr.scrolllistcontainer = uicls.Container(name='scrolllistcontainer', align=uiconst.TOALL, parent=self.sr.main, pos=(0, 0, 0, 0))
        self.sr.scroll = uicls.Scroll(name='scroll', parent=self.sr.scrolllistcontainer, padding=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding))
        self.ConstructScrollList()

    def ConstructScrollList(self):
        fittings = self.fittingSvc.GetLegacyClientFittings()
        scrolllist = []
        fittingList = []
        for fittingID, fitting in fittings.iteritems():
            fittingList.append((fitting.name, fitting))

        fittingList.sort()
        self.emptyFittings = []
        for fittingName, fitting in fittingList:
            if len(fitting.fitData) == 0:
                self.emptyFittings.append(fitting)
                continue
            typeFlag = set()
            for typeID, flag, qty in fitting.fitData[:]:
                if (typeID, flag) in typeFlag:
                    fitting.fitData.remove((typeID, flag, qty))
                else:
                    typeFlag.add((typeID, flag))

            data = util.KeyVal()
            data.label = fittingName
            data.checked = False
            data.OnChange = self.OnSelectionChanged
            data.cfgname = 'groups'
            data.retval = True
            data.report = False
            data.fitting = fitting
            scrolllist.append(listentry.Get('Checkbox', data=data))

        self.sr.scroll.Load(contentList=scrolllist)
        self.totalLocalFittings = len(fittingList)
        self.OnSelectionChanged(None)

    def Import(self, *args):
        impl = getDOMImplementation()
        newdoc = impl.createDocument(None, 'fittings', None)
        try:
            docEl = newdoc.documentElement
            fittings = []
            saveSomeToFile = False
            for entry in self.sr.scroll.GetNodes():
                if entry.checked:
                    fittings.append(entry.fitting)
                else:
                    saveSomeToFile = True
                    profile = newdoc.createElement('fitting')
                    docEl.appendChild(profile)
                    profile.attributes['name'] = entry.fitting.name
                    element = newdoc.createElement('description')
                    element.attributes['value'] = entry.fitting.Get('description')
                    profile.appendChild(element)
                    element = newdoc.createElement('shipType')
                    try:
                        shipType = cfg.invtypes.Get(entry.fitting.Get('shipTypeID')).typeName
                    except KeyError:
                        shipType = 'unknown type'

                    element.attributes['value'] = shipType
                    profile.appendChild(element)
                    for typeID, flag, qty in entry.fitting.fitData:
                        try:
                            typeName = cfg.invtypes.Get(typeID).typeName
                        except KeyError:
                            typeName = 'unknown type'

                        hardWareElement = newdoc.createElement('hardware')
                        hardWareElement.attributes['type'] = typeName
                        slot = self.GetSlotFromFlag(flag)
                        if slot is None:
                            slot = 'unknown slot'
                        hardWareElement.attributes['slot'] = slot
                        if flag == const.flagDroneBay:
                            hardWareElement.attributes['qty'] = str(qty)
                        profile.appendChild(hardWareElement)

            for emptyFitting in self.emptyFittings:
                saveSomeToFile = True
                profile = newdoc.createElement('fitting')
                docEl.appendChild(profile)
                profile.attributes['name'] = entry.fitting.name
                element = newdoc.createElement('description')
                element.attributes['value'] = entry.fitting.Get('description')
                profile.appendChild(element)
                element = newdoc.createElement('shipType')
                try:
                    shipType = cfg.invtypes.Get(entry.fitting.Get('shipTypeID')).typeName
                except KeyError:
                    shipType = 'unknown type'

                element.attributes['value'] = shipType
                profile.appendChild(element)

            if len(fittings) > 0:
                self.fittingSvc.PersistManyFittings(session.charid, fittings)
            if saveSomeToFile:
                self.dirpath = os.path.join(blue.win32.SHGetFolderPath(blue.win32.CSIDL_PERSONAL), 'EVE', 'fittings')
                filename = cfg.eveowners.Get(session.charid).ownerName
                filename = filename.replace(' ', '')
                filename = filename.replace('?', '').replace('*', '').replace(':', '').replace(';', '').replace('~', '')
                filename = filename.replace('\\', '').replace('/', '').replace('"', '').replace('|', '').replace("'", '')
                dirpath = os.path.join(blue.win32.SHGetFolderPath(blue.win32.CSIDL_PERSONAL), 'EVE', 'fittings')
                filename = os.path.join(dirpath, filename)
                extraEnding = ''
                while os.path.exists(filename + str(extraEnding) + '.xml'):
                    if not isinstance(extraEnding, int):
                        extraEnding = 1
                    extraEnding += 1

                filename += str(extraEnding) + '.xml'
                if not os.path.exists(self.dirpath):
                    os.makedirs(self.dirpath)
                outfile = codecs.open(filename, 'w', 'utf-8')
                newdoc.writexml(outfile, indent='\t', addindent='\t', newl='\n')
                eve.Message('LegacyFittingExportDone', {'filename': filename})
            self.fittingSvc.DeleteLegacyClientFittings()
            self.CloseByUser()
        finally:
            newdoc.unlink()

    def GetSlotFromFlag(self, flag):
        if flag >= const.flagHiSlot0 and flag <= const.flagHiSlot7:
            return 'hi slot ' + str(flag - const.flagHiSlot0)
        if flag >= const.flagMedSlot0 and flag <= const.flagMedSlot7:
            return 'med slot ' + str(flag - const.flagMedSlot0)
        if flag >= const.flagLoSlot0 and flag <= const.flagLoSlot7:
            return 'low slot ' + str(flag - const.flagLoSlot0)
        if flag >= const.flagRigSlot0 and flag <= const.flagRigSlot7:
            return 'rig slot ' + str(flag - const.flagRigSlot0)
        if flag >= const.flagSubSystemSlot0 and flag <= const.flagSubSystemSlot7:
            return 'subsystem slot ' + str(flag - const.flagSubSystemSlot0)
        if flag == const.flagDroneBay:
            return 'drone bay'