#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/common/script/entities/collisionMeshService.py
import service
import collections
import GameWorld
import miscUtil
import blue
import sys

class StaticShapeComponent:
    __guid__ = 'entities.StaticShapeComponent'

    def __init__(self, state):
        self.graphicID = state.get('graphicID')
        self.avatar = None


class CollisionMeshServer(service.Service):
    __guid__ = 'entities.collisionMeshService'

    def CreateComponent(self, name, state):
        component = StaticShapeComponent(state)
        self.graphicID = state.get('graphicID')
        return component

    def PackUpForClientTransfer(self, component):
        return {'graphicID': component.graphicID}

    def PackUpForSceneTransfer(self, component, destinationSceneID):
        return self.PackUpForClientTransfer(component)

    def UnPackFromSceneTransfer(self, component, entity, state):
        component.graphicID = state['graphicID']
        return component

    def ReportState(self, component, entity):
        report = collections.OrderedDict()
        report['Graphic ID'] = component.graphicID
        report['Collision File'] = miscUtil.GetCommonResourcePath(cfg.graphics.Get(component.graphicID).collisionFile)
        report['Failed'] = component.avatar.failed
        report['Is Initialized'] = component.avatar.isInitialized
        report['collisionGroup'] = component.avatar.collisionGroup
        report['entID'] = component.avatar.entID
        report['flags'] = component.avatar.flags
        report['Has Position Component'] = component.avatar.positionComponent is not None
        report['Has Bounding Component'] = component.avatar.boundingVolumeComponent is not None
        report['World AABB Min'] = ', '.join([ '%.2f' % f for f in component.avatar.GetWorldAABB()[0] ])
        report['World AABB Max'] = ', '.join([ '%.2f' % f for f in component.avatar.GetWorldAABB()[1] ])
        return report

    def PrepareComponent(self, sceneID, entityID, component):
        graphic = cfg.graphics.GetIfExists(component.graphicID)
        error = False
        collisionFile = None
        if graphic:
            collisionFilePath = getattr(graphic, 'collisionFile', None)
            if collisionFilePath:
                collisionFile = miscUtil.GetCommonResourcePath(collisionFilePath)
            else:
                error = True
        else:
            error = True
        if collisionFile is None or collisionFile == 'None':
            error = True
        if error:
            self.LogError('Collision for graphicID:', component.graphicID, 'could not be found.')
            return
        if collisionFile:
            sID = long(sceneID)
            gw = GameWorld.Manager.GetGameWorld(sID)
            component.avatar = gw.CreateStaticMesh(collisionFile)
            component.avatar.entID = entityID
            while not component.avatar.loaded and not component.avatar.Failed():
                blue.synchro.Yield()

            if component.avatar.Failed():
                gw.RemoveStaticShape(component.avatar)
                component.avatar = None

    def SetupComponent(self, entity, component):
        if component.graphicID is None:
            return
        if component.avatar:
            component.avatar.positionComponent = entity.GetComponent('position')
            component.avatar.boundingVolumeComponent = entity.GetComponent('boundingVolume')
            component.avatar.AddToScene()

    def TearDownComponent(self, entity, component):
        if component.graphicID is None:
            return
        if component.avatar is None:
            return
        gw = GameWorld.Manager.GetGameWorld(long(entity.scene.sceneID))
        gw.RemoveStaticShape(component.avatar)
        if component.avatar:
            component.avatar.positionComponent = None
            component.avatar.boundingVolumeComponent = None