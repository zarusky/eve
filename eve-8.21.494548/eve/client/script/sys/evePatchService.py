#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/sys/evePatchService.py
import util
appName = 'EVE'
patchInfoURLs = {'optic': 'http://www.eve-online.com.cn/patches/',
 'ccp': 'http://client.eveonline.com/patches/'}
optionalPatchInfoURLs = {'optic': 'http://www.eve-online.com.cn/patches/optional/',
 'ccp': 'http://client.eveonline.com/patches/optional/'}
exports = util.AutoExports('appPatch', locals())