#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/client/script/ui/primitives/container.py
import uiconst
import uicls
import uiutil
import uthread
import blue
import telemetry
import base
import trinity
import weakref

class Container(uicls.Base):
    __guid__ = 'uicls.Container'
    __renderObject__ = trinity.Tr2Sprite2dContainer
    __members__ = uicls.Base.__members__ + ['opacity',
     'children',
     'background',
     'clipChildren']
    isDropLocation = True
    default_clipChildren = False
    default_pickRadius = 0
    default_opacity = 1.0
    default_align = uiconst.TOALL
    default_state = uiconst.UI_PICKCHILDREN
    default_depthMin = 0.0
    default_depthMax = 0.0
    default_bgColor = None
    default_bgTexturePath = None
    _childrenDirty = False
    _cacheContents = False
    _containerClosing = False
    _nextChildrenHaveBeenFlagged = False
    _isTraversing = False

    def ApplyAttributes(self, attributes):
        self.children = self.GetChildrenList()
        self.background = uicls.BackgroundList(self)
        uicls.Base.ApplyAttributes(self, attributes)
        self.depthMin = attributes.get('depthMin', self.default_depthMin)
        self.depthMax = attributes.get('depthMax', self.default_depthMax)
        self.pickRadius = attributes.get('pickRadius', self.default_pickRadius)
        self.opacity = attributes.get('opacity', self.default_opacity)
        self.clipChildren = attributes.get('clipChildren', self.default_clipChildren)
        bgColor = attributes.get('bgColor', self.default_bgColor)
        bgTexturePath = attributes.get('bgTexturePath', self.default_bgTexturePath)
        if bgTexturePath:
            uicls.Sprite(bgParent=self, texturePath=bgTexturePath, color=bgColor or (1.0, 1.0, 1.0, 1.0))
        elif bgColor:
            uicls.Fill(bgParent=self, color=bgColor)

    def Close(self):
        if getattr(self, 'destroyed', False):
            return
        self._containerClosing = True
        for child in self.children[:]:
            child.Close()

        for child in self.background[:]:
            child.Close()

        uicls.Base.Close(self)

    def FlagHasDirtyChildren(self):
        if self._childrenDirty and not self._displayDirty:
            return
        self._childrenDirty = True
        if self.align == uiconst.NOALIGN:
            uicore.uilib.alignIslands.append(self)
            return
        parent = self.parent
        if parent:
            parent.FlagHasDirtyChildren()

    def FlagNextChildrenDirty(self, child):
        if self._isTraversing and self._nextChildrenHaveBeenFlagged:
            return
        align = child.align
        if align in uiconst.PUSHALIGNMENTS:
            foundChild = False
            for each in self.children:
                if each is child:
                    foundChild = True
                    self._nextChildrenHaveBeenFlagged = True
                    continue
                if foundChild and each.display and each.align in uiconst.AFFECTEDBYPUSHALIGNMENTS:
                    each.FlagAlignmentDirty()

    def Traverse(self, mbudget):
        if self.destroyed:
            return mbudget
        if self._alignmentDirty:
            mbudget = self.UpdateAlignment(mbudget)
            self._childrenDirty = True
        elif self.display:
            mbudget = self.ConsumeBudget(mbudget)
        if self._childrenDirty:
            self._childrenDirty = False
            self._nextChildrenHaveBeenFlagged = False
            self._isTraversing = True
            budget = (0,
             0,
             self.displayWidth,
             self.displayHeight)
            for each in self.children:
                if each.display:
                    budget = each.Traverse(budget)

            self._isTraversing = False
        return mbudget

    def GetChildrenList(self):
        return uicls.UIChildrenList(self)

    def GetOpacity(self):
        return self.opacity

    def SetOpacity(self, opacity):
        self.opacity = opacity

    opacity = property(GetOpacity, SetOpacity)

    def AutoFitToContent(self):
        if self.align in uiconst.AFFECTEDBYPUSHALIGNMENTS:
            raise RuntimeError('AutoFitToContent: invalid alignment')
        minWidth = 0
        minHeight = 0
        totalAutoVertical = 0
        totalAutoHorizontal = 0
        for each in self.children:
            if each.align not in uiconst.AFFECTEDBYPUSHALIGNMENTS:
                minWidth = max(minWidth, each.left + each.width)
                minHeight = max(minHeight, each.top + each.height)
            elif each.align in (uiconst.TOTOP, uiconst.TOBOTTOM):
                totalAutoVertical += each.padTop + each.height + each.padBottom
            elif each.align in (uiconst.TOLEFT, uiconst.TORIGHT):
                totalAutoHorizontal += each.padLeft + each.width + each.padRight

        self.width = max(minWidth, totalAutoHorizontal)
        self.height = max(minHeight, totalAutoVertical)

    def Flush(self):
        for child in self.children[:]:
            child.Close()

    def FindChild(self, *names, **kwds):
        if self.destroyed:
            return
        ret = None
        searchFrom = self
        for name in names:
            ret = searchFrom._FindChildByName(name)
            if hasattr(ret, 'children'):
                searchFrom = ret

        if not ret or ret.name != names[-1]:
            if kwds.get('raiseError', False):
                raise RuntimeError('ChildNotFound', (self.name, names))
            return
        return ret

    def _FindChildByName(self, name, lvl = 0):
        for child in self.children:
            if child.name == name:
                return child

        for child in self.children:
            if hasattr(child, 'children'):
                ret = child._FindChildByName(name, lvl + 1)
                if ret is not None:
                    return ret

    def Find(self, triTypeName):

        def FindType(under, typeName, addto):
            if under.__bluetype__ == typeName:
                addto.append(under)
            if hasattr(under, 'children'):
                for each in under.children:
                    FindType(each, typeName, addto)

        ret = []
        for child in self.children:
            FindType(child, triTypeName, ret)

        return ret

    def GetChild(self, *names):
        return self.FindChild(*names, **{'raiseError': True})

    def IsChildClipped(self, child):
        if not self.clipChildren:
            return False
        cdx = child.displayX
        cdw = child.displayWidth
        sdx = self.displayX
        sdw = self.displayWidth
        if cdx >= sdx and cdx <= sdx + sdw or cdx + cdw >= sdx and cdx + cdw <= sdx + sdw:
            cdy = child.displayY
            cdh = child.displayHeight
            sdy = self.displayY
            sdh = self.displayHeight
            if cdy >= sdy and cdy <= sdy + sdh or cdy + cdh >= sdy and cdy + cdh <= sdy + sdh:
                return False
        return True

    @apply
    def depthMin():
        doc = 'Minimum depth value'

        def fget(self):
            return self._depthMin

        def fset(self, value):
            self._depthMin = value
            ro = self.renderObject
            if ro and hasattr(ro, 'depthMin'):
                ro.depthMin = value or 0.0

        return property(**locals())

    @apply
    def depthMax():
        doc = 'Maximum depth value'

        def fget(self):
            return self._depthMax

        def fset(self, value):
            self._depthMax = value
            ro = self.renderObject
            if ro and hasattr(ro, 'depthMax'):
                ro.depthMax = value or 0.0

        return property(**locals())

    @apply
    def clipChildren():
        doc = 'Clip children?'

        def fget(self):
            return self._clipChildren

        def fset(self, value):
            self._clipChildren = value
            ro = self.renderObject
            if ro and hasattr(ro, 'clip'):
                ro.clip = value

        return property(**locals())

    @apply
    def opacity():
        doc = 'Opacity'

        def fget(self):
            return self._opacity

        def fset(self, value):
            self._opacity = value
            ro = self.renderObject
            if ro and hasattr(ro, 'opacity'):
                ro.opacity = value or 0.0

        return property(**locals())

    @apply
    def pickRadius():
        doc = 'Pick radius'

        def fget(self):
            return self._pickRadius

        def fset(self, value):
            self._pickRadius = value
            ro = self.renderObject
            if ro and hasattr(ro, 'pickRadius'):
                ro.pickRadius = uicore.ScaleDpi(value) or 0.0

        return property(**locals())

    @apply
    def displayWidth():
        doc = 'Width of container. Background objects are always assigned this width as well'
        fget = uicls.Base.displayWidth.fget

        def fset(self, value):
            uicls.Base.displayWidth.fset(self, value)
            if hasattr(self, 'background'):
                for each in self.background:
                    pl, pt, pr, pb = each.padding
                    each.displayWidth = self._displayWidth - uicore.ScaleDpi(pl + pr)

        return property(**locals())

    @apply
    def displayHeight():
        doc = 'Height of container. Background objects are always assigned this height as well'
        fget = uicls.Base.displayHeight.fget

        def fset(self, value):
            uicls.Base.displayHeight.fset(self, value)
            if hasattr(self, 'background'):
                for each in self.background:
                    pl, pt, pr, pb = each.padding
                    each.displayHeight = self._displayHeight - uicore.ScaleDpi(pt + pb)

        return property(**locals())

    @apply
    def displayRect():
        doc = ''
        fget = uicls.Base.displayRect.fget

        def fset(self, value):
            uicls.Base.displayRect.fset(self, value)
            if len(self.background) > 0:
                for each in self.background:
                    pl, pt, pr, pb = each.padding
                    each.displayRect = (uicore.ScaleDpi(pl),
                     uicore.ScaleDpi(pt),
                     self._displayWidth - uicore.ScaleDpi(pl + pr),
                     self._displayHeight - uicore.ScaleDpi(pt + pb))

        return property(**locals())

    @apply
    def cacheContents():
        doc = '\n            Should contents of this container be cached? This can drastically improve\n            render performance of containers with static contents.\n            '

        def fget(self):
            return self._cacheContents

        def fset(self, value):
            self._cacheContents = value
            if self.renderObject:
                self.renderObject.cacheContents = value

        return property(**locals())

    def _AppendChildRO(self, child):
        RO = self.GetRenderObject()
        if not RO:
            return
        childRO = child.GetRenderObject()
        if childRO:
            RO.children.append(childRO)
        if child.align != uiconst.NOALIGN:
            self.FlagAlignmentDirty()

    def _InsertChildRO(self, idx, child):
        RO = self.GetRenderObject()
        if not RO:
            return
        childRO = child.GetRenderObject()
        if childRO:
            RO.children.insert(idx, childRO)
        if child.align != uiconst.NOALIGN:
            self.FlagAlignmentDirty()

    def _RemoveChildRO(self, child):
        RO = self.GetRenderObject()
        if not RO:
            return
        childRO = child.GetRenderObject()
        if childRO and childRO in RO.children:
            RO.children.remove(childRO)
        self.FlagAlignmentDirty()

    def AppendBackgroundObject(self, child):
        RO = self.GetRenderObject()
        if not RO:
            return
        childRO = child.GetRenderObject()
        if childRO:
            RO.background.append(childRO)
        self.FlagAlignmentDirty()

    def InsertBackgroundObject(self, idx, child):
        RO = self.GetRenderObject()
        if not RO:
            return
        childRO = child.GetRenderObject()
        if childRO:
            RO.background.insert(idx, childRO)
        self.FlagAlignmentDirty()

    def RemoveBackgroundObject(self, child):
        RO = self.GetRenderObject()
        if not RO:
            return
        childRO = child.GetRenderObject()
        if childRO and childRO in RO.background:
            RO.background.remove(childRO)
        self.FlagAlignmentDirty()