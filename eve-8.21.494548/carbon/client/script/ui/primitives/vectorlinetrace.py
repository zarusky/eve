#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/client/script/ui/primitives/vectorlinetrace.py
import uicls
import uiconst
import trinity

class VectorLineTrace(uicls.TexturedBase):
    __guid__ = 'uicls.VectorLineTrace'
    __renderObject__ = trinity.Tr2Sprite2dLineTrace
    default_name = 'vectorlinetrace'
    default_align = uiconst.TOPLEFT
    default_width = 1
    default_spriteEffect = trinity.TR2_SFX_FILL_AA

    def ApplyAttributes(self, attributes):
        uicls.TexturedBase.ApplyAttributes(self, attributes)
        self.width = attributes.get('width', self.default_width)

    @apply
    def width():
        doc = '\n        The width of the line segments.\n        '

        def fget(self):
            return self.renderObject.width

        def fset(self, value):
            self.renderObject.width = value

        return property(**locals())

    @apply
    def isLoop():
        doc = '\n        If set, the path is closed, implicitly adding a line segment from\n        the last point to the starting point.\n        '

        def fget(self):
            return self.renderObject.isLoop

        def fset(self, value):
            self.renderObject.isLoop = value

        return property(**locals())

    @apply
    def start():
        doc = '\n        Where to start drawing the line, as a proportion of the length of\n        the line path. Defaults to 0 to start at the start of the path.\n        '

        def fget(self):
            return self.renderObject.start

        def fset(self, value):
            self.renderObject.start = value

        return property(**locals())

    @apply
    def end():
        doc = '\n        Where to stop drawing the line, as a proportion of the length of\n        the line path. Defaults to 1 to stop at the end of the path.\n        '

        def fget(self):
            return self.renderObject.end

        def fset(self, value):
            self.renderObject.end = value

        return property(**locals())

    def AddPoint(self, pos, color = (1, 1, 1, 1), name = '', idx = -1):
        v = trinity.Tr2Sprite2dLineTraceVertex()
        v.position = pos
        v.color = color
        v.name = name
        self.renderObject.vertices.insert(idx, v)