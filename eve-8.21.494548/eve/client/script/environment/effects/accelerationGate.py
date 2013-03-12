#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/environment/effects/accelerationGate.py
import effects

class AccelerationGate(effects.GenericEffect):
    __guid__ = 'effects.WarpGateEffect'

    def Start(self, duration):
        gateID = self.GetEffectShipID()
        targetID = self.GetEffectTargetID()
        gateBall = self.GetEffectShipBall()
        slimItem = self.fxSequencer.GetItem(gateID)
        if slimItem.dunMusicUrl is not None and targetID == eve.session.shipid:
            sm.GetService('audio').SendUIEvent(slimItem.dunMusicUrl.lower())
        self.PlayNamedAnimations(gateBall.model, 'Activation')