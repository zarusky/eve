#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\eve\common\lib\appConst.py
import sys
if getattr(sys, 'ue3', False):
    SEC = 10000000L
    MIN = SEC * 60L
    HOUR = MIN * 60L
    DAY = HOUR * 24L
else:
    from const import *
raceCaldari = 1
raceMinmatar = 2
raceAmarr = 4
raceGallente = 8
raceJove = 16
raceAngel = 32
raceSleepers = 64
raceORE = 128
bloodlineAchura = 11
bloodlineAmarr = 5
bloodlineBrutor = 4
bloodlineCivire = 2
bloodlineDeteis = 1
bloodlineGallente = 7
bloodlineIntaki = 8
bloodlineJinMei = 12
bloodlineKhanid = 13
bloodlineModifier = 10
bloodlineNiKunni = 6
bloodlineSebiestor = 3
bloodlineStatic = 9
bloodlineVherokior = 14
FEMALE = 0
MALE = 1
TYPEID_NONE = -1
USL_SERVER_PORT = 26004
NUM_BATTLES_PER_NODE = 256
intervalDustUser = 20
minDustUserType = 100
minDustUser = 1000000000
minDustCharacter = 2100000000
maxDustCharacter = 2130000000
userTypeDustPlayer = 101
userTypeDustCCP = 102
userTypeDustBattleServer = 103
userConnectTypeDustClient = 101
objectiveStateCeasefire = 0
objectiveStateMobilizing = 1
objectiveStateWar = 2
objectiveStateRebuilding = 3
OFFLINE_CHARID = -1
OFFLINE_USERID = -1
DUST_AUR_CURRENCY = 'AUR'
DUST_ISK_CURRENCY = 'ISK'
ACCOUNTING_DUST_ISK = 10000
ACCOUNTING_DUST_AUR = 11000
corporationStartupCost = 1599800
colorValues = [{'color': '0x202020',
  'blending': 'solid',
  'id': 671},
 {'color': '0xa5d4ff',
  'blending': 'multiply',
  'id': 673},
 {'color': '0xffffff',
  'blending': 'multiply',
  'id': 674},
 {'color': '0x789fff',
  'blending': 'multiply',
  'id': 676},
 {'color': '0xffd659',
  'blending': 'multiply',
  'id': 677},
 {'color': '0x939b9b',
  'blending': 'multiply',
  'id': 678},
 {'color': '0xff7800',
  'blending': 'multiply',
  'id': 679},
 {'color': '0x960000',
  'blending': 'multiply',
  'id': 680},
 {'color': '0x000000',
  'blending': 'solid',
  'alpha': 50,
  'id': 682},
 {'color': '0x3e4040',
  'blending': 'solid',
  'alpha': 40,
  'id': 683},
 {'color': '0xe8e8e8',
  'blending': 'solid',
  'id': 684},
 {'color': '0xffb23e',
  'blending': 'solid',
  'id': 685}]
ACCOUNT_TYPES_TO_CURRENCY_TYPE = {ACCOUNTING_DUST_ISK: DUST_ISK_CURRENCY}
VALID_VGS_CURRENCIES = set([DUST_AUR_CURRENCY])
DUST_VGS_STORE_NAME = 'DUST 514 Virtual Goods Store'
ACCOUNTING_DUST_MODIFYISK = 10001
ACCOUNTING_DUST_PRIMARYMARKETPURCHASE = 10002
ACCOUNTING_DUST_NEW_CHARACTER_MONEY = 10004
ACCOUNTING_DUST_CORP_WITHDRAWAL = 10005
ACCOUNTING_DUST_CORP_DEPOSIT = 10006
ACCOUNTING_DUST_BATTLEREWARD_WIN = 10009
ACCOUNTING_DUST_BATTLEREWARD_LOSS = 10010
ACCOUNTING_DUST_ISK_RESET_FOR_CHARACTER_WIPE = 10011
ACCOUNTING_DUST_CONTRACT_DEPOSIT = 10012
ACCOUNTING_DUST_CONTRACT_DEPOSIT_REFUND = 10013
ACCOUNTING_DUST_CONTRACT_COLLATERAL = 10014
ACCOUNTING_DUST_CONTRACT_COLLATERAL_REFUND = 10015
ACCOUNTING_DUST_CONTRACT_REWARD = 10016
ACCOUNTING_DUST_MODIFYRMC = 11001
BATTLEKICKSTATUS_SERVERSHUTDOWN = 0
BATTLEKICKSTATUS_NORMALKICK = 1
TEAM_OBSERVING = 255
TEAM_ATTACKING = 0
TEAM_DEFENDING = 1
ATTACKER_WIN = 1
DEFENDER_WIN = 2
DATA_SORT_ORDER_ASC = 0
DATA_SORT_ORDER_DESC = 1
MARKET_GROUPID_UNCATEGORIZED = -1
MARKET_GROUPNAME_UNCATEGORIZED = 'Uncategorized Items'
FAKE_ITEM_ID = None
CHARACTER_POSITION_RESPAWN = -1
CHARACTER_POSITION_RUN = 0
CHARACTER_POSITION_DRIVEN = 1
CHARACTER_POSITION_FLOWN = 2
INVOKE_ASYNCHRONOUS = 0
INVOKE_SYNCHRONOUS = 1
GTYPE_TEAM = 0
GTYPE_COMMANDER = 1
GTYPE_DOODLE = 2
GTYPE_SKIRMISH = 3
GTYPE_UNKNOWN = 4
INVENTORY_DUST_CORP_WITHDRAWAL = 20001
INVENTORY_DUST_CORP_DEPOSIT = 20002
DEFAULT_SPAWN_POINT = -1
battleLightingMoodDay = 0
battleLightingMoodDull = 1
battleLightingMoodDark = 2
BATTLE_LIGHTING_MOOD = {battleLightingMoodDay: 'MOOD_DAY',
 battleLightingMoodDull: 'MOOD_DULL',
 battleLightingMoodDark: 'MOOD_DARK'}
battleTypeBattleSeries = 0
battleTypeCorporationBattle = 1
SKILL_MULTIPLIER_PASSIVE_BOOSTER = 0
SKILL_MULTIPLIER_ACTIVE_BOOSTER = 1
VOICE_ACTIVATION_BOOSTER = 2
EDITOR_MULTIPLIER_KIND_NAME = {SKILL_MULTIPLIER_PASSIVE_BOOSTER: 'Passive',
 SKILL_MULTIPLIER_ACTIVE_BOOSTER: 'Active',
 VOICE_ACTIVATION_BOOSTER: 'Voice'}
MULTIPLIER_CATMA_CLASS_NAME = {SKILL_MULTIPLIER_PASSIVE_BOOSTER: 'PassiveSkillGainBooster',
 SKILL_MULTIPLIER_ACTIVE_BOOSTER: 'ActiveSkillGainBooster'}
MULTIPLIER_REASON_CHARACTER_SKILL_GAIN = 0
MULTIPLIER_REASON_BOOSTER = 1
EDITOR_MULTIPLIER_REASON_NAME = {MULTIPLIER_REASON_CHARACTER_SKILL_GAIN: 'Passive Skill Gain Activated',
 MULTIPLIER_REASON_BOOSTER: 'Booster'}
MAX_DUST_SKILL_LEVEL = 5
DUST_SKILL_COST_TABLE = [6220,
 18650,
 43530,
 87060,
 155460]
MAX_PLAYERLIST_IN_CORP_CHAT = 20
BATTLE_REGION_US = 10007
BATTLE_REGION_EU = 10008
BATTLE_REGION_ASIA = 10009
BATTLE_REGION_ALL = 10010
SEARCH_CHARS_NPCS_CORPS = 0
SEARCH_CHARS_NPCS = 1
SEARCH_CORPS = 2
SEARCH_PLAYER_CHARS = 3
SEARCH_DUST_PLAYER_CHARS = 4
SEARCH_EVE_PLAYER_CHARS = 5
SEARCH_PLAYER_CHARS_CORPS = 6
SKILL_CORPORATION_MANAGEMENT = 352887
SKILL_EMIPRE_CONTROL = 352890
SKILL_MEGACORP_MANAGEMENT = 352888
RDV_DENIED_REQUESTNOTFINISH = 'requestNotFinish'
userTypeBattleServer = 103
intervalEveUser = 10
uniqueCharacterIdentifier = 'charid'
ACT_IDX_START = 0
ACT_IDX_DURATION = 1
ACT_IDX_ENV = 2
ACT_IDX_REPEAT = 3
AU = 149597870700.0
LIGHTYEAR = 9460000000000000.0
dgmAssPreAssignment = -1
dgmAssPreMul = 0
dgmAssPreDiv = 1
dgmAssModAdd = 2
dgmAssModSub = 3
dgmAssPostMul = 4
dgmAssPostDiv = 5
dgmAssPostPercent = 6
dgmAssPostAssignment = 7
dgmEnvSelf = 0
dgmEnvChar = 1
dgmEnvShip = 2
dgmEnvTarget = 3
dgmEnvOther = 4
dgmEnvArea = 5
dgmEffActivation = 1
dgmEffArea = 3
dgmEffOnline = 4
dgmEffPassive = 0
dgmEffTarget = 2
dgmEffOverload = 5
dgmEffDungeon = 6
dgmEffSystem = 7
dgmPassiveEffectCategories = (dgmEffPassive, dgmEffDungeon, dgmEffSystem)
dgmTauConstant = 10000
dgmExprSkip = 0
dgmExprOwner = 1
dgmExprShip = 2
dgmExprOwnerAndShip = 3
dgmAttrCatGroup = 12
dgmAttrCatType = 11
flagAutoFit = 0
flagBonus = 86
flagBooster = 88
flagBriefcase = 6
flagCapsule = 56
flagCargo = 5
flagCorpMarket = 62
flagCorpSAG2 = 116
flagCorpSAG3 = 117
flagCorpSAG4 = 118
flagCorpSAG5 = 119
flagCorpSAG6 = 120
flagCorpSAG7 = 121
flagDroneBay = 87
flagDustDatabank = 152
flagDustBattle = 153
flagCorpSAGs = (flagCorpSAG2,
 flagCorpSAG3,
 flagCorpSAG4,
 flagCorpSAG5,
 flagCorpSAG6,
 flagCorpSAG7)
flagFactoryOperation = 100
flagFixedSlot = 35
flagFleetHangar = 155
flagHangar = 4
flagHangarAll = 1000
flagHiSlot0 = 27
flagHiSlot1 = 28
flagHiSlot2 = 29
flagHiSlot3 = 30
flagHiSlot4 = 31
flagHiSlot5 = 32
flagHiSlot6 = 33
flagHiSlot7 = 34
flagImplant = 89
flagLoSlot0 = 11
flagLoSlot7 = 18
flagLocked = 63
flagMedSlot0 = 19
flagMedSlot7 = 26
flagNone = 0
flagPilot = 57
flagPlanetSurface = 150
flagQuafeBay = 154
flagReward = 8
flagRigSlot0 = 92
flagRigSlot1 = 93
flagRigSlot2 = 94
flagRigSlot3 = 95
flagRigSlot4 = 96
flagRigSlot5 = 97
flagRigSlot6 = 98
flagRigSlot7 = 99
flagSecondaryStorage = 122
flagShipHangar = 90
flagShipOffline = 91
flagSkill = 7
flagSkillInTraining = 61
flagSpecializedFuelBay = 133
flagSpecializedOreHold = 134
flagSpecializedGasHold = 135
flagSpecializedMineralHold = 136
flagSpecializedSalvageHold = 137
flagSpecializedShipHold = 138
flagSpecializedSmallShipHold = 139
flagSpecializedMediumShipHold = 140
flagSpecializedLargeShipHold = 141
flagSpecializedIndustrialShipHold = 142
flagSpecializedAmmoHold = 143
flagSpecializedCommandCenterHold = 148
flagSpecializedPlanetaryCommoditiesHold = 149
flagSpecializedMaterialBay = 151
flagSlotFirst = 11
flagSlotLast = 35
flagStructureActive = 144
flagStructureInactive = 145
flagWorldSpace = 124
flagSubSystemSlot0 = 125
flagSubSystemSlot1 = 126
flagSubSystemSlot2 = 127
flagSubSystemSlot3 = 128
flagSubSystemSlot4 = 129
flagSubSystemSlot5 = 130
flagSubSystemSlot6 = 131
flagSubSystemSlot7 = 132
flagUnlocked = 64
flagWallet = 1
flagJunkyardReprocessed = 146
flagJunkyardTrashed = 147
flagWardrobe = 3
categoryAbstract = 29
categoryAccessories = 5
categoryAncientRelic = 34
categoryApparel = 30
categoryAsteroid = 25
categoryWorldSpace = 26
categoryBlueprint = 9
categoryBonus = 14
categoryCelestial = 2
categoryCharge = 8
categoryCommodity = 17
categoryDecryptors = 35
categoryDeployable = 22
categoryDrone = 18
categoryEntity = 11
categoryImplant = 20
categoryInfantry = 350001
categoryMaterial = 4
categoryModule = 7
categoryOrbital = 46
categoryOwner = 1
categoryPlaceables = 49
categoryPlanetaryCommodities = 43
categoryPlanetaryInteraction = 41
categoryPlanetaryResources = 42
categoryReaction = 24
categoryShip = 6
categorySkill = 16
categorySovereigntyStructure = 40
categoryStation = 3
categoryStructure = 23
categoryStructureUpgrade = 39
categorySubSystem = 32
categorySystem = 0
categoryTrading = 10
groupAccelerationGateKeys = 474
groupAfterBurner = 46
groupAgentsinSpace = 517
groupAlliance = 32
groupAncientCompressedIce = 903
groupAncientSalvage = 966
groupArkonor = 450
groupArmorPlatingEnergized = 326
groupArmorHardener = 328
groupArmorReinforcer = 329
groupArmorRepairUnit = 62
groupArmorRepairProjector = 325
groupArmorResistanceShiftHardener = 1150
groupAssemblyArray = 397
groupAsteroidAngelCartelBattleCruiser = 576
groupAsteroidAngelCartelBattleship = 552
groupAsteroidAngelCartelCommanderBattleCruiser = 793
groupAsteroidAngelCartelCommanderCruiser = 790
groupAsteroidAngelCartelCommanderDestroyer = 794
groupAsteroidAngelCartelCommanderFrigate = 789
groupAsteroidAngelCartelCruiser = 551
groupAsteroidAngelCartelDestroyer = 575
groupAsteroidAngelCartelFrigate = 550
groupAsteroidAngelCartelHauler = 554
groupAsteroidAngelCartelOfficer = 553
groupAsteroidBelt = 9
groupAsteroid = 25
groupAsteroidBloodRaidersBattleCruiser = 578
groupAsteroidBloodRaidersBattleship = 556
groupAsteroidBloodRaidersCommanderBattleCruiser = 795
groupAsteroidBloodRaidersCommanderCruiser = 791
groupAsteroidBloodRaidersCommanderDestroyer = 796
groupAsteroidBloodRaidersCommanderFrigate = 792
groupAsteroidBloodRaidersCruiser = 555
groupAsteroidBloodRaidersDestroyer = 577
groupAsteroidBloodRaidersFrigate = 557
groupAsteroidBloodRaidersHauler = 558
groupAsteroidBloodRaidersOfficer = 559
groupAsteroidGuristasBattleCruiser = 580
groupAsteroidGuristasBattleship = 560
groupAsteroidGuristasCommanderBattleCruiser = 797
groupAsteroidGuristasCommanderCruiser = 798
groupAsteroidGuristasCommanderDestroyer = 799
groupAsteroidGuristasCommanderFrigate = 800
groupAsteroidGuristasCruiser = 561
groupAsteroidGuristasDestroyer = 579
groupAsteroidGuristasFrigate = 562
groupAsteroidGuristasHauler = 563
groupAsteroidGuristasOfficer = 564
groupAsteroidRogueDroneBattleCruiser = 755
groupAsteroidRogueDroneBattleship = 756
groupAsteroidRogueDroneCruiser = 757
groupAsteroidRogueDroneDestroyer = 758
groupAsteroidRogueDroneFrigate = 759
groupAsteroidRogueDroneHauler = 760
groupAsteroidRogueDroneSwarm = 761
groupAsteroidRogueDroneOfficer = 1174
groupAsteroidSanshasNationBattleCruiser = 582
groupAsteroidSanshasNationBattleship = 565
groupAsteroidSanshasNationCommanderBattleCruiser = 807
groupAsteroidSanshasNationCommanderCruiser = 808
groupAsteroidSanshasNationCommanderDestroyer = 809
groupAsteroidSanshasNationCommanderFrigate = 810
groupAsteroidSanshasNationCruiser = 566
groupAsteroidSanshasNationDestroyer = 581
groupAsteroidSanshasNationFrigate = 567
groupAsteroidSanshasNationHauler = 568
groupAsteroidSanshasNationOfficer = 569
groupAsteroidSerpentisBattleCruiser = 584
groupAsteroidSerpentisBattleship = 570
groupAsteroidSerpentisCommanderBattleCruiser = 811
groupAsteroidSerpentisCommanderCruiser = 812
groupAsteroidSerpentisCommanderDestroyer = 813
groupAsteroidSerpentisCommanderFrigate = 814
groupAsteroidSerpentisCruiser = 571
groupAsteroidSerpentisDestroyer = 583
groupAsteroidSerpentisFrigate = 572
groupAsteroidSerpentisHauler = 573
groupAsteroidSerpentisOfficer = 574
groupAsteroidRogueDroneCommanderFrigate = 847
groupAsteroidRogueDroneCommanderDestroyer = 846
groupAsteroidRogueDroneCommanderCruiser = 845
groupAsteroidRogueDroneCommanderBattleCruiser = 843
groupAsteroidRogueDroneCommanderBattleship = 844
groupAsteroidAngelCartelCommanderBattleship = 848
groupAsteroidBloodRaidersCommanderBattleship = 849
groupAsteroidGuristasCommanderBattleship = 850
groupAsteroidSanshasNationCommanderBattleship = 851
groupAsteroidSerpentisCommanderBattleship = 852
groupMissionAmarrEmpireCarrier = 865
groupMissionCaldariStateCarrier = 866
groupMissionContainer = 952
groupMissionGallenteFederationCarrier = 867
groupMissionMinmatarRepublicCarrier = 868
groupMissionFighterDrone = 861
groupMissionGenericFreighters = 875
groupAssaultShip = 324
groupAttackBattlecruiser = 1201
groupAuditLogSecureContainer = 448
groupBattlecruiser = 419
groupBattleship = 27
groupBeacon = 310
groupBillboard = 323
groupBiohazard = 284
groupBiomass = 14
groupBistot = 451
groupBlackOps = 898
groupBlockadeRunner = 1202
groupBooster = 303
groupBubbleProbeLauncher = 589
groupCapDrainDrone = 544
groupCapacitorBooster = 76
groupCapacitorBoosterCharge = 87
groupCapitalIndustrialShip = 883
groupCapsule = 29
groupCapsuleerBases = 1082
groupCapturePointTower = 922
groupCargoContainer = 12
groupCarrier = 547
groupCharacter = 1
groupCheatModuleGroup = 225
groupCloakingDevice = 330
groupClone = 23
groupCloud = 227
groupCombatDrone = 100
groupComet = 305
groupCommandPins = 1027
groupCommandShip = 540
groupCommodities = 526
groupComposite = 429
groupComputerInterfaceNode = 317
groupConcordDrone = 301
groupConstellation = 4
groupConstructionPlatform = 307
groupControlBunker = 925
groupControlTower = 365
groupConvoy = 297
groupConvoyDrone = 298
groupCorporateHangarArray = 471
groupCorporation = 2
groupCosmicAnomaly = 885
groupCosmicSignature = 502
groupCovertBeacon = 897
groupCovertOps = 830
groupCrokite = 452
groupCruiser = 26
groupStrategicCruiser = 963
groupCustomsOfficial = 446
groupCynosuralGeneratorArray = 838
groupCynosuralSystemJammer = 839
groupDamageControl = 60
groupDarkOchre = 453
groupDataInterfaces = 716
groupDatacores = 333
groupDeadspaceAngelCartelBattleCruiser = 593
groupDeadspaceAngelCartelBattleship = 594
groupDeadspaceAngelCartelCruiser = 595
groupDeadspaceAngelCartelDestroyer = 596
groupDeadspaceAngelCartelFrigate = 597
groupDeadspaceBloodRaidersBattleCruiser = 602
groupDeadspaceBloodRaidersBattleship = 603
groupDeadspaceBloodRaidersCruiser = 604
groupDeadspaceBloodRaidersDestroyer = 605
groupDeadspaceBloodRaidersFrigate = 606
groupDeadspaceGuristasBattleCruiser = 611
groupDeadspaceGuristasBattleship = 612
groupDeadspaceGuristasCruiser = 613
groupDeadspaceGuristasDestroyer = 614
groupDeadspaceGuristasFrigate = 615
groupDeadspaceOverseer = 435
groupDeadspaceOverseersBelongings = 496
groupDeadspaceOverseersSentry = 495
groupDeadspaceOverseersStructure = 494
groupDeadspaceRogueDroneBattleCruiser = 801
groupDeadspaceRogueDroneBattleship = 802
groupDeadspaceRogueDroneCruiser = 803
groupDeadspaceRogueDroneDestroyer = 804
groupDeadspaceRogueDroneFrigate = 805
groupDeadspaceRogueDroneSwarm = 806
groupDeadspaceSanshasNationBattleCruiser = 620
groupDeadspaceSanshasNationBattleship = 621
groupDeadspaceSanshasNationCruiser = 622
groupDeadspaceSanshasNationDestroyer = 623
groupDeadspaceSanshasNationFrigate = 624
groupDeadspaceSerpentisBattleCruiser = 629
groupDeadspaceSerpentisBattleship = 630
groupDeadspaceSerpentisCruiser = 631
groupDeadspaceSerpentisDestroyer = 632
groupDeadspaceSerpentisFrigate = 633
groupDeadspaceSleeperSleeplessPatroller = 983
groupDeadspaceSleeperSleeplessSentinel = 959
groupDeadspaceSleeperSleeplessDefender = 982
groupDeadspaceSleeperAwakenedPatroller = 985
groupDeadspaceSleeperAwakenedSentinel = 960
groupDeadspaceSleeperAwakenedDefender = 984
groupDeadspaceSleeperEmergentPatroller = 987
groupDeadspaceSleeperEmergentSentinel = 961
groupDeadspaceSleeperEmergentDefender = 986
groupDefenseBunkers = 1004
groupDestroyer = 420
groupDestructibleAgentsInSpace = 715
groupDestructibleSentryGun = 383
groupDestructibleStationServices = 874
groupDreadnought = 485
groupElectronicCounterCounterMeasures = 202
groupElectronicCounterMeasureBurst = 80
groupElectronicCounterMeasures = 201
groupEffectBeacon = 920
groupElectronicWarfareBattery = 439
groupElectronicWarfareDrone = 639
groupEliteBattleship = 381
groupEnergyDestabilizer = 71
groupEnergyNeutralizingBattery = 837
groupEnergyTransferArray = 67
groupEnergyWeapon = 53
groupEnergyVampire = 68
groupExhumer = 543
groupExtractionControlUnitPins = 1063
groupExtractorPins = 1026
groupFaction = 19
groupFactionDrone = 288
groupFakeSkills = 505
groupFighterBomber = 1023
groupFighterDrone = 549
groupFlashpoint = 1071
groupForceField = 411
groupForceFieldArray = 445
groupFreightContainer = 649
groupFreighter = 513
groupFrequencyCrystal = 86
groupFrequencyMiningLaser = 483
groupFrigate = 25
groupFrozen = 281
groupFueledArmorRepairer = 1199
groupFueledShieldBooster = 1156
groupGangCoordinator = 316
groupGasCloudHarvester = 737
groupGasIsotopes = 422
groupGeneral = 280
groupGlobalWarpDisruptor = 368
groupGneiss = 467
groupHarvestableCloud = 711
groupHeavyAssaultShip = 358
groupHedbergite = 454
groupHemorphite = 455
groupHullRepairUnit = 63
groupHybridAmmo = 85
groupHybridWeapon = 74
groupIce = 465
groupIceProduct = 423
groupIndustrial = 28
groupIndustrialCommandShip = 941
groupInfantryDropsuit = 351064
groupInfrastructureHub = 1012
groupInterceptor = 831
groupInterdictor = 541
groupIntermediateMaterials = 428
groupInvasionSanshaNationBattleship = 1056
groupInvasionSanshaNationCapital = 1052
groupInvasionSanshaNationCruiser = 1054
groupInvasionSanshaNationFrigate = 1053
groupInvasionSanshaNationIndustrial = 1051
groupJaspet = 456
groupJumpPortalArray = 707
groupJumpPortalGenerator = 590
groupKernite = 457
groupLCODrone = 279
groupLandmark = 318
groupLargeCollidableObject = 226
groupLargeCollidableShip = 784
groupLargeCollidableStructure = 319
groupLearning = 267
groupLease = 652
groupLivestock = 283
groupLogisticDrone = 640
groupLogistics = 832
groupLogisticsArray = 710
groupMercenaryBases = 1081
groupMercoxit = 468
groupMine = 92
groupMineral = 18
groupMiningBarge = 463
groupMiningDrone = 101
groupMiningLaser = 54
groupMissile = 84
groupMiscellaneous = 314
groupCitadelTorpedo = 476
groupCitadelCruise = 1019
groupBomb = 90
groupBombECM = 863
groupBombEnergy = 864
groupTorpedo = 89
groupAdvancedTorpedo = 657
groupCruiseMissile = 386
groupFOFCruiseMissile = 396
groupAdvancedCruiseMissile = 656
groupHeavyMissile = 385
groupFOFHeavyMissile = 395
groupAdvancedHeavyMissile = 655
groupAssaultMissile = 772
groupAdvancedAssaultMissile = 654
groupLightMissile = 384
groupFOFLightMissile = 394
groupAdvancedLightMissile = 653
groupRocket = 387
groupAdvancedRocket = 648
groupDefenderMissile = 88
groupHeavyDefenderMissile = 1158
groupFestivalMissile = 500
groupMissileLauncher = 56
groupMissileLauncherAssault = 511
groupMissileLauncherBomb = 862
groupMissileLauncherCitadel = 524
groupMissileLauncherCruise = 506
groupMissileLauncherDefender = 512
groupMissileLauncherHeavy = 510
groupMissileLauncherHeavyAssault = 771
groupMissileLauncherRocket = 507
groupMissileLauncherSiege = 508
groupMissileLauncherFestival = 501
groupMissileLauncherStandard = 509
groupMissionAmarrEmpireBattlecruiser = 666
groupMissionAmarrEmpireBattleship = 667
groupMissionAmarrEmpireCruiser = 668
groupMissionAmarrEmpireDestroyer = 669
groupMissionAmarrEmpireFrigate = 665
groupMissionAmarrEmpireOther = 670
groupMissionCONCORDBattlecruiser = 696
groupMissionCONCORDBattleship = 697
groupMissionCONCORDCruiser = 695
groupMissionCONCORDDestroyer = 694
groupMissionCONCORDFrigate = 693
groupMissionCONCORDOther = 698
groupMissionCaldariStateBattlecruiser = 672
groupMissionCaldariStateBattleship = 674
groupMissionCaldariStateCruiser = 673
groupMissionCaldariStateDestroyer = 676
groupMissionCaldariStateFrigate = 671
groupMissionCaldariStateOther = 675
groupMissionDrone = 337
groupMissionFactionBattleships = 924
groupMissionFactionCruisers = 1006
groupMissionFactionFrigates = 1007
groupMissionFactionIndustrials = 927
groupMissionGallenteFederationBattlecruiser = 681
groupMissionGallenteFederationBattleship = 680
groupMissionGallenteFederationCruiser = 678
groupMissionGallenteFederationDestroyer = 679
groupMissionGallenteFederationFrigate = 677
groupMissionGallenteFederationOther = 682
groupMissionKhanidBattlecruiser = 690
groupMissionKhanidBattleship = 691
groupMissionKhanidCruiser = 689
groupMissionKhanidDestroyer = 688
groupMissionKhanidFrigate = 687
groupMissionKhanidOther = 692
groupMissionMinmatarRepublicBattlecruiser = 685
groupMissionMinmatarRepublicBattleship = 706
groupMissionMinmatarRepublicCruiser = 705
groupMissionMinmatarRepublicDestroyer = 684
groupMissionMinmatarRepublicFrigate = 683
groupMissionMinmatarRepublicOther = 686
groupMissionMorduBattlecruiser = 702
groupMissionMorduBattleship = 703
groupMissionMorduCruiser = 701
groupMissionMorduDestroyer = 700
groupMissionMorduFrigate = 699
groupMissionMorduOther = 704
groupMobileHybridSentry = 449
groupMobileLaboratory = 413
groupMobileLaserSentry = 430
groupMobileMissileSentry = 417
groupTransportShip = 380
groupJumpFreighter = 902
groupFWMinmatarRepublicFrigate = 1166
groupFWMinmatarRepublicDestroyer = 1178
groupFWMinmatarRepublicCruiser = 1182
groupFWMinmatarRepublicBattlecruiser = 1186
groupFWGallenteFederationFrigate = 1168
groupFWGallenteFederationDestroyer = 1177
groupFWGallenteFederationCruiser = 1181
groupFWGallenteFederationBattlecruiser = 1185
groupFWCaldariStateFrigate = 1167
groupFWCaldariStateDestroyer = 1176
groupFWCaldariStateCruiser = 1180
groupFWCaldariStateBattlecruiser = 1184
groupFWAmarrEmpireFrigate = 1169
groupFWAmarrEmpireDestroyer = 1175
groupFWAmarrEmpireCruiser = 1179
groupFWAmarrEmpireBattlecruiser = 1183
groupMobilePowerCore = 414
groupMobileProjectileSentry = 426
groupMobileReactor = 438
groupMobileSentryGun = 336
groupMobileShieldGenerator = 418
groupMobileStorage = 364
groupMobileMicroJumpDisruptor = 1149
groupMobileWarpDisruptor = 361
groupMoney = 17
groupMoon = 8
groupMoonMaterials = 427
groupMoonMining = 416
groupSupercarrier = 659
groupOmber = 469
groupOrbitalConstructionPlatforms = 1106
groupOverseerPersonalEffects = 493
groupOutpostImprovements = 872
groupOutpostUpgrades = 876
groupPirateDrone = 185
groupPlagioclase = 458
groupPlanet = 7
groupPlanetaryCustomsOffices = 1025
groupPlanetaryCloud = 312
groupPlanetaryLinks = 1036
groupPledges = 1075
groupPoliceDrone = 182
groupProcessPins = 1028
groupProjectedElectronicCounterCounterMeasures = 289
groupProjectileAmmo = 83
groupProjectileWeapon = 55
groupProtectiveSentryGun = 180
groupPrototypeExplorationShip = 1022
groupProximityDrone = 97
groupPyroxeres = 459
groupRadioactive = 282
groupForceReconShip = 833
groupCombatReconShip = 906
groupRefinables = 355
groupRefiningArray = 311
groupRegion = 3
groupRemoteHullRepairer = 585
groupRemoteSensorBooster = 290
groupRemoteSensorDamper = 208
groupRepairDrone = 299
groupRing = 13
groupRogueDrone = 287
groupRookieship = 237
groupSalvagedMaterials = 754
groupSalvageDrone = 1159
groupSatellite = 1165
groupScanProbeLauncher = 481
groupScannerArray = 709
groupScannerProbe = 479
groupScordite = 460
groupSecureCargoContainer = 340
groupSensorBooster = 212
groupSensorDampeningBattery = 440
groupSentryGun = 99
groupShieldBooster = 40
groupShieldHardener = 77
groupShieldHardeningArray = 444
groupShieldTransporter = 41
groupShipMaintenanceArray = 363
groupShippingCrates = 382
groupShuttle = 31
groupSiegeModule = 515
groupSilo = 404
groupSmartBomb = 72
groupSolarSystem = 5
groupSovereigntyClaimMarkers = 1003
groupSovereigntyDisruptionStructures = 1005
groupSovereigntyStructures = 1004
groupSpaceportPins = 1030
groupSpawnContainer = 306
groupSpodumain = 461
groupStargate = 10
groupStatisWeb = 65
groupStasisWebificationBattery = 441
groupStasisWebifyingDrone = 641
groupStation = 15
groupStationServices = 16
groupStationUpgradePlatform = 835
groupStationImprovementPlatform = 836
groupStealthBomber = 834
groupStealthEmitterArray = 480
groupStoragePins = 1029
groupStorylineBattleship = 523
groupStorylineCruiser = 522
groupStorylineFrigate = 520
groupStorylineMissionBattleship = 534
groupStorylineMissionCruiser = 533
groupStorylineMissionFrigate = 527
groupStripMiner = 464
groupStructureRepairArray = 840
groupSovUpgradeIndustrial = 1020
groupSovUpgradeMilitary = 1021
groupSun = 6
groupSuperWeapon = 588
groupSurveyProbe = 492
groupSystem = 0
groupTargetBreaker = 1154
groupTargetPainter = 379
groupTargetPaintingBattery = 877
groupTemporaryCloud = 335
groupTestOrbitals = 1073
groupTerranArtifacts = 519
groupTitan = 30
groupTool = 332
groupTrackingArray = 473
groupTrackingComputer = 213
groupTrackingDisruptor = 291
groupTrackingLink = 209
groupTractorBeam = 650
groupTradeSession = 95
groupTrading = 94
groupTutorialDrone = 286
groupUnanchoringDrone = 470
groupVeldspar = 462
groupVoucher = 24
groupWarpDisruptFieldGenerator = 899
groupWarpDisruptionProbe = 548
groupWarpGate = 366
groupWarpScrambler = 52
groupWarpScramblingBattery = 443
groupWarpScramblingDrone = 545
groupWreck = 186
groupZombieEntities = 934
groupMissionGenericBattleships = 816
groupMissionGenericCruisers = 817
groupMissionGenericFrigates = 818
groupMissionThukkerBattlecruiser = 822
groupMissionThukkerBattleship = 823
groupMissionThukkerCruiser = 824
groupMissionThukkerDestroyer = 825
groupMissionThukkerFrigate = 826
groupMissionThukkerOther = 827
groupMissionGenericBattleCruisers = 828
groupMissionGenericDestroyers = 829
groupDeadspaceOverseerFrigate = 819
groupDeadspaceOverseerCruiser = 820
groupDeadspaceOverseerBattleship = 821
groupElectronicAttackShips = 893
groupEnergyNeutralizingBattery = 837
groupHeavyInterdictors = 894
groupMarauders = 900
groupDecorations = 937
groupDefensiveSubSystems = 954
groupElectronicSubSystems = 955
groupEngineeringSubSystems = 958
groupOffensiveSubSystems = 956
groupPropulsionSubSystems = 957
groupWormhole = 988
groupSecondarySun = 995
groupGameTime = 943
groupWorldSpace = 935
groupSalvager = 1122
groupOrbitalTarget = 1198
locationGroupServiceMasks = {groupSolarSystem: 'beyonce',
 groupStation: 'station',
 groupWorldSpace: 'worldspace',
 groupPlanet: 'planetMgr'}
minDustTypeID = 350000
typeTicketFrigate = 30717
typeTicketDestroyer = 30718
typeTicketBattleship = 30721
typeTicketCruiser = 30722
typeTicketBattlecruiser = 30723
typeAccelerationGate = 17831
typeAccounting = 16622
typeAcolyteI = 2203
typeAdvancedLaboratoryOperation = 24624
typeAdvancedMassProduction = 24625
typeAdvancedPlanetology = 2403
typeAlliance = 16159
typeAmarrFreighterWreck = 26483
typeAmarrCaptainsQuarters = 32578
typeAmarrEliteFreighterWreck = 29033
typeApocalypse = 642
typeArchaeology = 13278
typeAstrometrics = 3412
typeAutomatedCentiiKeyholder = 22053
typeAutomatedCentiiTrainingVessel = 21849
typeAutomatedCoreliTrainingVessel = 21845
typeAutomatedCorpiiTrainingVessel = 21847
typeAutomatedGistiTrainingVessel = 21846
typeAutomatedPithiTrainingVessel = 21848
typeBHMegaCargoShip = 11019
typeBasicDamageControl = 521
typeBeacon = 10124
typeBiomass = 3779
typeBookmark = 51
typeBrokerRelations = 3446
typeBubbleProbeLauncher = 22782
typeCaldariFreighterWreck = 26505
typeCaldariCaptainsQuarters = 32581
typeCaldariEliteFreighterWreck = 29034
typeCapitalShips = 20533
typeCargoContainer = 23
typeCelestialAgentSiteBeacon = 25354
typeCelestialBeacon = 10645
typeCelestialBeaconII = 19706
typeCertificate = 29530
typeCharacterAchura = 1383
typeCharacterAmarr = 1373
typeCharacterBrutor = 1380
typeCharacterCivire = 1375
typeCharacterDeteis = 1376
typeCharacterGallente = 1377
typeCharacterIntaki = 1378
typeCharacterJinMei = 1384
typeCharacterKhanid = 1385
typeCharacterModifier = 1382
typeCharacterNiKunni = 1374
typeCharacterSebiestor = 1379
typeCharacterStatic = 1381
typeCharacterVherokior = 1386
typeCloneGradeAlpha = 164
typeCloneVatBayI = 23735
typeCloningService = 28158
typeCommandCenterUpgrade = 2505
typeCompanyShares = 50
typeConnections = 3359
typeConstellation = 4
typeContracting = 25235
typeCorporation = 2
typeCorporationContracting = 25233
typeCorporationManagement = 3363
typeCorpse = 25
typeCorpseFemale = 29148
typeCovertCynosuralFieldI = 28650
typeCredits = 29
typeCriminalConnections = 3361
typeCrowBlueprint = 11177
typeCynosuralFieldI = 21094
typeCynosuralJammerBeacon = 32798
typeDamageControlI = 2046
typeDaytrading = 16595
typeDeadspaceSignature = 19728
typeDefenderI = 265
typeDiplomacy = 3357
typeDistributionConnections = 3894
typeDistrictSatellite = 32884
typeDoomTorpedoIBlueprint = 17864
typeDuplicating = 10298
typeDustStreak = 10756
typeElectronics = 3426
typeEmpireControl = 3732
typeEngineering = 3413
typeEthnicRelations = 3368
typeFaction = 30
typeFactoryService = 28157
typeFittingService = 28155
typeFixedLinkAnnexationGenerator = 32226
typeFlashpoint = 3692
typeFleetCommand = 24764
typeForceField = 16103
typeGallenteFreighterWreck = 26527
typeGallenteCaptainsQuarters = 32579
typeGallenteEliteFreighterWreck = 29035
typeEnormousFreightContainer = 33003
typeGiantFreightContainer = 24445
typeHugeFreightContainer = 33005
typeLargeFreightContainer = 33007
typeMediumFreightContainer = 33009
typeSmallFreightContainer = 33011
typeGiantSecureContainer = 11489
typeGistiiHijacker = 16877
typeHacking = 21718
typeHangarContainer = 3298
typeHugeSecureContainer = 11488
typeIndustry = 3380
typeInfrastructureHub = 32458
typeInterplanetaryConsolidation = 2495
typeLaboratoryOperation = 3406
typeLaboratoryService = 28166
typeLargeAuditLogSecureContainer = 17365
typeLargeCratesOfQuafe = 4090
typeLargeCryoContainer = 3464
typeLargeLifeSupportContainer = 3459
typeLargeRadiationShieldedContainer = 3461
typeLargeSecureContainer = 3465
typeLargeStandardContainer = 3296
typeLeadership = 3348
typeLoyaltyPoints = 29247
typeMapLandmark = 11367
typeMarginTrading = 16597
typeMarketing = 16598
typeMassProduction = 3387
typeMedal = 29496
typeMediumAuditLogSecureContainer = 17364
typeMediumCryoContainer = 3463
typeMediumLifeSupportContainer = 3458
typeMediumRadiationShieldedContainer = 3460
typeMediumSecureContainer = 3466
typeMediumStandardContainer = 3293
typeMetallurgy = 3409
typeMicroJumpDrive = 4383
typeMinmatarFreighterWreck = 26549
typeMinmatarEliteFreighterWreck = 29036
typeMiningConnections = 3893
typeMinmatarCaptainsQuarters = 32580
typeMissileLauncherOperation = 3319
typeMoon = 14
typeNaniteRepairPaste = 28668
typeNegotiation = 3356
typeOffice = 27
typeOfficeFolder = 26
typeOmnipotent = 19430
typeOrbitalCommandCenter = 3964
typeOrbitalTarget = 33069
typePlanetaryCustomsOffice = 2233
typePlanetaryLaunchContainer = 2263
typePlanetEarthlike = 11
typePlanetGas = 13
typePlanetIce = 12
typePlanetLava = 2015
typePlanetOcean = 2014
typePlanetSandstorm = 2016
typePlanetShattered = 30889
typePlanetThunderstorm = 2017
typePlanetPlasma = 2063
typePlanetology = 2406
typePlasticWrap = 3468
typePlayerKill = 49
typePolarisCenturion = 9858
typePolarisCenturionFrigate = 9862
typePolarisInspectorFrigate = 9854
typePolarisLegatusFrigate = 9860
typeProcurement = 16594
typeQuafe = 3699
typeQuafeUltra = 12865
typeQuafeUltraSpecialEdition = 12994
typeQuafeZero = 3898
typeRank = 29495
typeRegion = 3
typeRemoteSensing = 13279
typeRepairService = 28159
typeRepairSystems = 3393
typeReprocessingService = 28156
typeResearch = 3403
typeResearchProjectManagement = 12179
typeRetail = 3444
typeRibbon = 29497
typeSchematic = 2733
typeScience = 3402
typeScientificNetworking = 24270
typeScrapmetalProcessing = 12196
typeSecurityConnections = 3895
typeShieldOperations = 3416
typeShieldGenerator = 3860
typeSilo = 14343
typeSlaver = 12049
typeSmallAuditLogSecureContainer = 17363
typeSmallCryoContainer = 3462
typeSmallLifeSupportContainer = 3295
typeSmallRadiationShieldedContainer = 3294
typeSmallSecureContainer = 3467
typeSmallStandardContainer = 3297
typeSocial = 3355
typeSoftCloud = 10753
typeSolarSystem = 5
typeSpaceAnchor = 2528
typeSpikedQuafe = 21661
typeStationConquerable1 = 12242
typeStationConquerable2 = 12294
typeStationConquerable3 = 12295
typeStationContainer = 17366
typeStationVault = 17367
typeStationWarehouse = 17368
typeStrontiumClathrates = 16275
typeSupplyChainManagement = 24268
typeSystem = 0
typeTacticalEMPAmmoS = 32801
typeTacticalHybridAmmoS = 32803
typeTacticalLaserAmmoS = 32799
typeTargetedAccelerationGate = 4077
typeTestPlanetaryLink = 2280
typeTestSurfaceCommandCenter = 3936
typeThePrizeContainer = 19373
typeThermodynamics = 28164
typeTrade = 3443
typeTradeSession = 53
typeTrading = 52
typeTritanium = 34
typeTycoon = 18580
typeUniverse = 9
typeVeldspar = 1230
typeVisibility = 3447
typeWarpDisruptionFocusingScript = 29003
typeWholesale = 16596
typeWingCommand = 11574
typeWispyChlorineCloud = 10758
typeWispyOrangeCloud = 10754
typeWreck = 26468
typePilotLicence = 29668
typeAsteroidBelt = 15
typeLetterOfRecommendation = 30906
typeWater = 3645
typeOxygen = 3683
accountingKeyCash = 1000
accountingKeyCash2 = 1001
accountingKeyCash3 = 1002
accountingKeyCash4 = 1003
accountingKeyCash5 = 1004
accountingKeyCash6 = 1005
accountingKeyCash7 = 1006
accountingKeyProperty = 1100
accountingKeyAUR = 1200
accountingKeyAUR2 = 1201
accountingKeyAUR3 = 1202
accountingKeyAUR4 = 1203
accountingKeyAUR5 = 1204
accountingKeyAUR6 = 1205
accountingKeyAUR7 = 1206
accountingKeyEscrow = 1500
accountingKeyReceivables = 1800
accountingKeyPayables = 2000
accountingKeyGold = 2010
accountingKeyEquity = 2900
accountingKeySales = 3000
accountingKeyPurchases = 4000
flagLoSlot0 = 11
flagLoSlot1 = 12
flagLoSlot2 = 13
flagLoSlot3 = 14
flagLoSlot4 = 15
flagLoSlot5 = 16
flagLoSlot6 = 17
flagLoSlot7 = 18
flagMedSlot0 = 19
flagMedSlot1 = 20
flagMedSlot2 = 21
flagMedSlot3 = 22
flagMedSlot4 = 23
flagMedSlot5 = 24
flagMedSlot6 = 25
flagMedSlot7 = 26
flagHiSlot0 = 27
flagHiSlot1 = 28
flagHiSlot2 = 29
flagHiSlot3 = 30
flagHiSlot4 = 31
flagHiSlot5 = 32
flagHiSlot6 = 33
flagHiSlot7 = 34
loSlotFlags = [flagLoSlot0,
 flagLoSlot1,
 flagLoSlot2,
 flagLoSlot3,
 flagLoSlot4,
 flagLoSlot5,
 flagLoSlot6,
 flagLoSlot7]
medSlotFlags = [flagMedSlot0,
 flagMedSlot1,
 flagMedSlot2,
 flagMedSlot3,
 flagMedSlot4,
 flagMedSlot5,
 flagMedSlot6,
 flagMedSlot7]
hiSlotFlags = [flagHiSlot0,
 flagHiSlot1,
 flagHiSlot2,
 flagHiSlot3,
 flagHiSlot4,
 flagHiSlot5,
 flagHiSlot6,
 flagHiSlot7]
subSystemSlotFlags = [flagSubSystemSlot0,
 flagSubSystemSlot1,
 flagSubSystemSlot2,
 flagSubSystemSlot3,
 flagSubSystemSlot4]
rigSlotFlags = [flagRigSlot0, flagRigSlot1, flagRigSlot2]
ALSCActionNone = 0
ALSCActionAdd = 6
ALSCActionAssemble = 1
ALSCActionConfigure = 10
ALSCActionEnterPassword = 9
ALSCActionLock = 7
ALSCActionRepackage = 2
ALSCActionSetName = 3
ALSCActionSetPassword = 5
ALSCActionUnlock = 8
ALSCPasswordNeededToOpen = 1
ALSCPasswordNeededToLock = 2
ALSCPasswordNeededToUnlock = 4
ALSCPasswordNeededToViewAuditLog = 8
ALSCLockAddedItems = 16
CTPC_CHAT = 8
CTPC_MAIL = 9
CTPG_CASH = 6
CTPG_SHARES = 7
CTV_ADD = 1
CTV_COMMS = 5
CTV_GIVE = 4
CTV_REMOVE = 2
CTV_SET = 3
SCCPasswordTypeConfig = 2
SCCPasswordTypeGeneral = 1
agentTypeBasicAgent = 2
agentTypeEventMissionAgent = 8
agentTypeGenericStorylineMissionAgent = 6
agentTypeNonAgent = 1
agentTypeResearchAgent = 4
agentTypeStorylineMissionAgent = 7
agentTypeTutorialAgent = 3
agentTypeFactionalWarfareAgent = 9
agentTypeEpicArcAgent = 10
agentTypeAura = 11
agentTypeCareerAgent = 12
auraAgentIDs = [3019499,
 3019493,
 3019495,
 3019490,
 3019497,
 3019496,
 3019486,
 3019498,
 3019492,
 3019500,
 3019489,
 3019494]
agentRangeSameSystem = 1
agentRangeSameOrNeighboringSystemSameConstellation = 2
agentRangeSameOrNeighboringSystem = 3
agentRangeNeighboringSystemSameConstellation = 4
agentRangeNeighboringSystem = 5
agentRangeSameConstellation = 6
agentRangeSameOrNeighboringConstellationSameRegion = 7
agentRangeSameOrNeighboringConstellation = 8
agentRangeNeighboringConstellationSameRegion = 9
agentRangeNeighboringConstellation = 10
agentRangeNearestEnemyCombatZone = 11
agentRangeNearestCareerHub = 12
agentIskMultiplierLevel1 = 1
agentIskMultiplierLevel2 = 2
agentIskMultiplierLevel3 = 4
agentIskMultiplierLevel4 = 8
agentIskMultiplierLevel5 = 16
agentIskMultipliers = (agentIskMultiplierLevel1,
 agentIskMultiplierLevel2,
 agentIskMultiplierLevel3,
 agentIskMultiplierLevel4,
 agentIskMultiplierLevel5)
agentLpMultiplierLevel1 = 20
agentLpMultiplierLevel2 = 60
agentLpMultiplierLevel3 = 180
agentLpMultiplierLevel4 = 540
agentLpMultiplierLevel5 = 4860
agentLpMultipliers = (agentLpMultiplierLevel1,
 agentLpMultiplierLevel2,
 agentLpMultiplierLevel3,
 agentLpMultiplierLevel4,
 agentLpMultiplierLevel5)
agentIskRandomLowValue = 11000
agentIskRandomHighValue = 16500
agentDivisionBusiness = 25
agentDivisionExploration = 26
agentDivisionIndustry = 27
agentDivisionMilitary = 28
agentDivisionAdvMilitary = 29
agentDivisionsCareer = [agentDivisionBusiness,
 agentDivisionExploration,
 agentDivisionIndustry,
 agentDivisionMilitary,
 agentDivisionAdvMilitary]
agentDialogueButtonViewMission = 1
agentDialogueButtonRequestMission = 2
agentDialogueButtonAccept = 3
agentDialogueButtonAcceptChoice = 4
agentDialogueButtonAcceptRemotely = 5
agentDialogueButtonComplete = 6
agentDialogueButtonCompleteRemotely = 7
agentDialogueButtonContinue = 8
agentDialogueButtonDecline = 9
agentDialogueButtonDefer = 10
agentDialogueButtonQuit = 11
agentDialogueButtonStartResearch = 12
agentDialogueButtonCancelResearch = 13
agentDialogueButtonBuyDatacores = 14
agentDialogueButtonLocateCharacter = 15
agentDialogueButtonLocateAccept = 16
agentDialogueButtonLocateReject = 17
agentDialogueButtonYes = 18
agentDialogueButtonNo = 19
allianceApplicationAccepted = 2
allianceApplicationEffective = 3
allianceApplicationNew = 1
allianceApplicationRejected = 4
allianceCreationCost = 1000000000
allianceMembershipCost = 2000000
allianceRelationshipCompetitor = 3
allianceRelationshipEnemy = 4
allianceRelationshipFriend = 2
allianceRelationshipNAP = 1
operandADD = 1
operandAGGM = 2
operandAGIM = 3
operandAGORSM = 4
operandAGRSM = 5
operandAIM = 6
operandALGM = 7
operandALM = 8
operandALRSM = 9
operandAND = 10
operandAORSM = 11
operandATT = 12
operandATTACK = 13
operandCARGOSCAN = 14
operandCHEATTELEDOCK = 15
operandCHEATTELEGATE = 16
operandCOMBINE = 17
operandDEC = 18
operandDECLOAKWAVE = 19
operandDECN = 20
operandDEFASSOCIATION = 21
operandDEFATTRIBUTE = 22
operandDEFBOOL = 23
operandDEFENVIDX = 24
operandDEFFLOAT = 25
operandDEFGROUP = 26
operandDEFINT = 27
operandDEFSTRING = 28
operandDEFTYPEID = 29
operandECMBURST = 30
operandEFF = 31
operandEMPWAVE = 32
operandEQ = 33
operandGA = 34
operandGET = 35
operandGETTYPE = 36
operandGM = 37
operandGT = 38
operandGTE = 39
operandIA = 40
operandIF = 41
operandINC = 42
operandINCN = 43
operandLAUNCH = 44
operandLAUNCHDEFENDERMISSILE = 45
operandLAUNCHDRONE = 46
operandLAUNCHFOFMISSILE = 47
operandLG = 48
operandLS = 49
operandMINE = 50
operandMUL = 51
operandOR = 52
operandPOWERBOOST = 53
operandRGGM = 54
operandRGIM = 55
operandRGORSM = 56
operandRGRSM = 57
operandRIM = 58
operandRLGM = 59
operandRLM = 60
operandRLRSM = 61
operandRORSM = 62
operandRS = 63
operandRSA = 64
operandSET = 65
operandSHIPSCAN = 66
operandSKILLCHECK = 67
operandSUB = 68
operandSURVEYSCAN = 69
operandTARGETHOSTILES = 70
operandTARGETSILENTLY = 71
operandTOOLTARGETSKILLS = 72
operandUE = 73
operandVERIFYTARGETGROUP = 74
attributeAccessDifficulty = 901
attributeAccessDifficultyBonus = 902
attributeAccuracyMultiplier = 205
attributeActivationBlocked = 1349
attributeActivationTargetLoss = 855
attributeAgentAutoPopupRange = 844
attributeAgentCommRange = 841
attributeAgentID = 840
attributeAgility = 70
attributeIgnoreDronesBelowSignatureRadius = 1855
attributeAimedLaunch = 644
attributeAllowsCloneJumpsWhenActive = 981
attributeAllowedInCapIndustrialMaintenanceBay = 1891
attributeAmmoLoaded = 127
attributeAnchoringDelay = 556
attributeAnchorDistanceMax = 1591
attributeAnchorDistanceMin = 1590
attributeAnchoringRequiresSovereignty = 1033
attributeAnchoringRequiresSovUpgrade1 = 1595
attributeAnchoringSecurityLevelMax = 1032
attributeAoeCloudSize = 654
attributeAoeDamageReductionFactor = 1353
attributeAoeDamageReductionSensitivity = 1354
attributeAoeFalloff = 655
attributeAoeVelocity = 653
attributeArmorBonus = 65
attributeArmorDamage = 266
attributeArmorDamageAmount = 84
attributeArmorEmDamageResonance = 267
attributeArmorEmDamageResistanceBonus = 1465
attributeArmorExplosiveDamageResonance = 268
attributeArmorExplosiveDamageResistanceBonus = 1468
attributeArmorHP = 265
attributeArmorHPBonusAdd = 1159
attributeArmorHPMultiplier = 148
attributeArmorHpBonus = 335
attributeArmorKineticDamageResonance = 269
attributeArmorKineticDamageResistanceBonus = 1466
attributeArmorThermalDamageResonance = 270
attributeArmorThermalDamageResistanceBonus = 1467
attributeArmorUniformity = 524
attributeAttributePoints = 185
attributeAurumConversionRate = 1818
attributeBarrageDmgMultiplier = 326
attributeBaseDefenderAllyCost = 1820
attributeBaseMaxScanDeviation = 1372
attributeBaseSensorStrength = 1371
attributeBaseScanRange = 1370
attributeBoosterDuration = 330
attributeBoosterness = 1087
attributeBoosterMaxCharAgeHours = 1647
attributeBrokenRepairCostMultiplier = 1264
attributeCanBeJettisoned = 1852
attributeCanCloak = 1163
attributeCanJump = 861
attributeCanNotBeTrainedOnTrial = 1047
attributeCanNotUseStargates = 1254
attributeCanReceiveCloneJumps = 982
attributeCapacitorBonus = 67
attributeCapacitorCapacity = 482
attributeCapacitorCapacityBonus = 1079
attributeCapacitorCapacityMultiplier = 147
attributeCapacitorCharge = 18
attributeCapacitorRechargeRateMultiplier = 144
attributeCapacity = 38
attributeCapacitySecondary = 1233
attributeCapacityBonus = 72
attributeCapRechargeBonus = 314
attributeCaptureProximityRange = 1337
attributeCargoCapacityMultiplier = 149
attributeCargoGroup = 629
attributeCargoGroup2 = 1846
attributeCargoScanResistance = 188
attributeChanceToNotTargetSwitch = 1651
attributeCharge = 18
attributeChargedArmorDamageMultiplier = 1886
attributeChargeGroup1 = 604
attributeChargeRate = 56
attributeChargeSize = 128
attributeCharisma = 164
attributeCloakingTargetingDelay = 560
attributeClothingAlsoCoversCategory = 1797
attributeCloudDuration = 545
attributeCloudEffectDelay = 544
attributeColor = 1417
attributeCommandbonus = 833
attributeConstructionType = 1771
attributeConsumptionQuantity = 714
attributeConsumptionType = 713
attributeContrabandDetectionChance = 723
attributeControlTowerMinimumDistance = 1165
attributeCopySpeedPercent = 387
attributeFleetHangarCapacity = 912
attributeCorporateHangarCapacity = 912
attributeCorporationMemberLimit = 190
attributeCpu = 50
attributeCpuLoad = 49
attributeCpuLoadLevelModifier = 1635
attributeCpuLoadPerKm = 1634
attributeCpuMultiplier = 202
attributeCpuOutput = 48
attributeCrystalVolatilityChance = 783
attributeCrystalVolatilityDamage = 784
attributeCrystalsGetDamaged = 786
attributeDamage = 3
attributeDamageCloudChance = 522
attributeDamageCloudType = 546
attributeDamageMultiplier = 64
attributeDeadspaceUnsafe = 801
attributeDecloakFieldRange = 651
attributeDecryptorID = 1115
attributeDefaultCustomsOfficeTaxRate = 1781
attributeDevIndexMilitary = 1583
attributeDevIndexIndustrial = 1584
attributeDevIndexSovereignty = 1615
attributeDevIndexUpgrade = 1616
attributeDisallowAssistance = 854
attributeDisallowEarlyDeactivation = 906
attributeDisallowInEmpireSpace = 1074
attributeDisallowOffensiveModifiers = 872
attributeDisallowRepeatingActivation = 1014
attributeDistributionID01 = 1755
attributeDistributionID02 = 1756
attributeDistributionID03 = 1757
attributeDistributionID04 = 1758
attributeDistributionID05 = 1759
attributeDistributionID06 = 1760
attributeDistributionID07 = 1761
attributeDistributionID08 = 1762
attributeDistributionID09 = 1763
attributeDistributionID10 = 1764
attributeDistributionIDAngel01 = 1695
attributeDistributionIDAngel02 = 1696
attributeDistributionIDAngel03 = 1697
attributeDistributionIDAngel04 = 1698
attributeDistributionIDAngel05 = 1699
attributeDistributionIDAngel06 = 1700
attributeDistributionIDAngel07 = 1701
attributeDistributionIDAngel08 = 1702
attributeDistributionIDAngel09 = 1703
attributeDistributionIDAngel10 = 1704
attributeDistributionIDBlood01 = 1705
attributeDistributionIDBlood02 = 1706
attributeDistributionIDBlood03 = 1707
attributeDistributionIDBlood04 = 1708
attributeDistributionIDBlood05 = 1709
attributeDistributionIDBlood06 = 1710
attributeDistributionIDBlood07 = 1711
attributeDistributionIDBlood08 = 1712
attributeDistributionIDBlood09 = 1713
attributeDistributionIDBlood10 = 1714
attributeDistributionIDGurista01 = 1715
attributeDistributionIDGurista02 = 1716
attributeDistributionIDGurista03 = 1717
attributeDistributionIDGurista04 = 1718
attributeDistributionIDGurista05 = 1719
attributeDistributionIDGurista06 = 1720
attributeDistributionIDGurista07 = 1721
attributeDistributionIDGurista08 = 1722
attributeDistributionIDGurista09 = 1723
attributeDistributionIDGurista10 = 1724
attributeDistributionIDRogueDrone01 = 1725
attributeDistributionIDRogueDrone02 = 1726
attributeDistributionIDRogueDrone03 = 1727
attributeDistributionIDRogueDrone04 = 1728
attributeDistributionIDRogueDrone05 = 1729
attributeDistributionIDRogueDrone06 = 1730
attributeDistributionIDRogueDrone07 = 1731
attributeDistributionIDRogueDrone08 = 1732
attributeDistributionIDRogueDrone09 = 1733
attributeDistributionIDRogueDrone10 = 1734
attributeDistributionIDSansha01 = 1735
attributeDistributionIDSansha02 = 1736
attributeDistributionIDSansha03 = 1737
attributeDistributionIDSansha04 = 1738
attributeDistributionIDSansha05 = 1739
attributeDistributionIDSansha06 = 1740
attributeDistributionIDSansha07 = 1741
attributeDistributionIDSansha08 = 1742
attributeDistributionIDSansha09 = 1743
attributeDistributionIDSansha10 = 1744
attributeDistributionIDSerpentis01 = 1745
attributeDistributionIDSerpentis02 = 1746
attributeDistributionIDSerpentis03 = 1747
attributeDistributionIDSerpentis04 = 1748
attributeDistributionIDSerpentis05 = 1749
attributeDistributionIDSerpentis06 = 1750
attributeDistributionIDSerpentis07 = 1751
attributeDistributionIDSerpentis08 = 1752
attributeDistributionIDSerpentis09 = 1753
attributeDistributionIDSerpentis10 = 1754
attributeDoesNotEmergencyWarp = 1854
attributeDrawback = 1138
attributeDroneBandwidth = 1271
attributeDroneBandwidthLoad = 1273
attributeDroneBandwidthUsed = 1272
attributeDroneCapacity = 283
attributeDroneControlDistance = 458
attributeDroneFocusFire = 1297
attributeDroneIsAggressive = 1275
attributeDroneIsChaotic = 1278
attributeDuplicatingChance = 399
attributeDuration = 73
attributeEcmBurstRange = 142
attributeEcuAreaOfInfluence = 1689
attributeEcuDecayFactor = 1683
attributeExtractorHeadCPU = 1690
attributeExtractorHeadPower = 1691
attributeEcuMaxVolume = 1684
attributeEcuOverlapFactor = 1685
attributeEcuNoiseFactor = 1687
attributeEffectDeactivationDelay = 1579
attributeEmDamage = 114
attributeEmDamageResistanceBonus = 984
attributeEmDamageResonance = 113
attributeEmDamageResonanceMultiplier = 133
attributeEmpFieldRange = 99
attributeEnergyDestabilizationAmount = 97
attributeEntityArmorRepairAmount = 631
attributeEntityAttackDelayMax = 476
attributeEntityAttackDelayMin = 475
attributeEntityAttackRange = 247
attributeEntityBracketColour = 798
attributeEntityChaseMaxDelay = 580
attributeEntityChaseMaxDelayChance = 581
attributeEntityChaseMaxDistance = 665
attributeEntityChaseMaxDuration = 582
attributeEntityChaseMaxDurationChance = 583
attributeEntityCruiseSpeed = 508
attributeEntityDefenderChance = 497
attributeEntityEquipmentGroupMax = 465
attributeEntityEquipmentMax = 457
attributeEntityEquipmentMin = 456
attributeEntityFactionLoss = 562
attributeEntityFlyRange = 416
attributeEntityFlyRangeFactor = 772
attributeEntityGroupRespawnChance = 640
attributeEntityGroupArmorResistanceBonus = 1676
attributeEntityGroupArmorResistanceActivationChance = 1682
attributeEntityGroupArmorResistanceDuration = 1681
attributeEntityGroupPropJamBonus = 1675
attributeEntityGroupPropJamActivationChance = 1680
attributeEntityGroupPropJamDuration = 1679
attributeEntityGroupShieldResistanceBonus = 1671
attributeEntityGroupShieldResistanceActivationChance = 1673
attributeEntityGroupShieldResistanceDuration = 1672
attributeEntityGroupSpeedBonus = 1674
attributeEntityGroupSpeedActivationChance = 1678
attributeEntityGroupSpeedDuration = 1677
attributeEntityKillBounty = 481
attributeEntityLootCountMax = 251
attributeEntityLootCountMin = 250
attributeEntityLootValueMax = 249
attributeEntityLootValueMin = 248
attributeEntityMaxVelocitySignatureRadiusMultiplier = 1133
attributeEntityMaxWanderRange = 584
attributeEntityMissileTypeID = 507
attributeEntityRemoteECMBaseDuration = 1661
attributeEntityRemoteECMChanceOfActivation = 1664
attributeEntityRemoteECMDuration = 1658
attributeEntityRemoteECMDurationScale = 1660
attributeEntityRemoteECMExtraPlayerScale = 1662
attributeEntityRemoteECMIntendedNumPlayers = 1663
attributeEntityRemoteECMMinDuration = 1659
attributeEntitySecurityMaxGain = 563
attributeEntitySecurityStatusKillBonus = 252
attributeEntityWarpScrambleChance = 504
attributeExpiryTime = 1088
attributeExplosionDelay = 281
attributeExplosionDelayWreck = 1162
attributeExplosionRange = 107
attributeExplosiveDamage = 116
attributeExplosiveDamageResistanceBonus = 985
attributeExplosiveDamageResonance = 111
attributeExplosiveDamageResonanceMultiplier = 132
attributeExportTax = 1639
attributeExportTaxMultiplier = 1641
attributeExtractorDepletionRange = 1644
attributeExtractorDepletionRate = 1645
attributeFactionID = 1341
attributeFalloff = 158
attributeFalloffBonus = 349
attributeFastTalkPercentage = 359
attributeFighterAttackAndFollow = 1283
attributeFitsToShipType = 1380
attributeFwLpKill = 1555
attributeGfxBoosterID = 246
attributeGfxTurretID = 245
attributeHarvesterQuality = 710
attributeHarvesterType = 709
attributeHasFleetHangars = 911
attributeHasCorporateHangars = 911
attributeHasShipMaintenanceBay = 907
attributeHeatAbsorbtionRateHi = 1182
attributeHeatAbsorbtionRateLow = 1184
attributeHeatAbsorbtionRateMed = 1183
attributeHeatAttenuationHi = 1259
attributeHeatAttenuationLow = 1262
attributeHeatAttenuationMed = 1261
attributeHeatCapacityHi = 1178
attributeHeatCapacityLow = 1200
attributeHeatCapacityMed = 1199
attributeHeatDamage = 1211
attributeHeatDissipationRateHi = 1179
attributeHeatDissipationRateLow = 1198
attributeHeatDissipationRateMed = 1196
attributeHeatGenerationMultiplier = 1224
attributeHeatAbsorbtionRateModifier = 1180
attributeHeatHi = 1175
attributeHeatLow = 1177
attributeHeatMed = 1176
attributeHiSlotModifier = 1374
attributeHiSlots = 14
attributeHitsMissilesOnly = 823
attributeHp = 9
attributeHullEmDamageResonance = 974
attributeHullExplosiveDamageResonance = 975
attributeHullKineticDamageResonance = 976
attributeHullThermalDamageResonance = 977
attributeImmuneToSuperWeapon = 1654
attributeDamageDelayDuration = 1839
attributeImpactDamage = 660
attributeImplantness = 331
attributeImportTax = 1638
attributeImportTaxMultiplier = 1640
attributeIncapacitationRatio = 156
attributeIntelligence = 165
attributeInventionMEModifier = 1113
attributeInventionMaxRunModifier = 1124
attributeInventionPEModifier = 1114
attributeInventionPropabilityMultiplier = 1112
attributeIsIncapacitated = 1168
attributeIsArcheology = 1331
attributeIsCapitalSize = 1785
attributeIsCovert = 1252
attributeIsGlobal = 1207
attributeIsHacking = 1330
attributeIsOnline = 2
attributeIsPlayerOwnable = 589
attributeIsRAMcompatible = 998
attributeJumpClonesLeft = 1336
attributeJumpDriveCapacitorNeed = 898
attributeJumpDriveConsumptionAmount = 868
attributeJumpDriveConsumptionType = 866
attributeJumpDriveDuration = 869
attributeJumpDriveRange = 867
attributeJumpHarmonics = 1253
attributeJumpPortalCapacitorNeed = 1005
attributeJumpPortalConsumptionMassFactor = 1001
attributeJumpPortalDuration = 1002
attributejumpDelayDuration = 1221
attributeKineticDamage = 117
attributeKineticDamageResistanceBonus = 986
attributeKineticDamageResonance = 109
attributeKineticDamageResonanceMultiplier = 131
attributeLauncherGroup = 137
attributeLauncherHardPointModifier = 1369
attributeLauncherSlotsLeft = 101
attributeLeechBalanceFactor = 1232
attributeLogisticalCapacity = 1631
attributeLootRespawnTime = 470
attributeLowSlotModifier = 1376
attributeLowSlots = 12
attributeManufactureCostMultiplier = 369
attributeManufactureSlotLimit = 196
attributeManufactureTimeMultiplier = 219
attributeManufacturingTimeResearchSpeed = 385
attributeMass = 4
attributeMassAddition = 796
attributeMaxActiveDrones = 352
attributeMaxDefenseBunkers = 1580
attributeMaxDirectionalVelocity = 661
attributeMaxGangModules = 435
attributeMaxGroupActive = 763
attributeMaxGroupFitted = 1544
attributeMaxJumpClones = 979
attributeMaxLaborotorySlots = 467
attributeMaxLockedTargets = 192
attributeMaxLockedTargetsBonus = 235
attributeMaxMissileVelocity = 664
attributeMaxOperationalDistance = 715
attributeMaxOperationalUsers = 716
attributeMaxRange = 54
attributeMaxRangeBonus = 351
attributeMaxScanDeviation = 788
attributeMaxScanGroups = 1122
attributeMaxShipGroupActive = 910
attributeMaxShipGroupActiveID = 909
attributeMaxStructureDistance = 650
attributeMaxSubSystems = 1367
attributeMaxTargetRange = 76
attributeMaxTargetRangeMultiplier = 237
attributeMaxTractorVelocity = 1045
attributeMaxVelocity = 37
attributeMaxVelocityActivationLimit = 1334
attributeMaxVelocityLimited = 1333
attributeMaxVelocityBonus = 306
attributeMedSlotModifier = 1375
attributeMedSlots = 13
attributeMemory = 166
attributeMetaGroupID = 1692
attributeMetaLevel = 633
attributeMinMissileVelDmgMultiplier = 663
attributeMinScanDeviation = 787
attributeMinTargetVelDmgMultiplier = 662
attributeMineralNeedResearchSpeed = 398
attributeMiningAmount = 77
attributeMiningDroneAmountPercent = 428
attributeMissileDamageMultiplier = 212
attributeMissileEntityAoeCloudSizeMultiplier = 858
attributeMissileEntityAoeFalloffMultiplier = 860
attributeMissileEntityAoeVelocityMultiplier = 859
attributeMissileEntityFlightTimeMultiplier = 646
attributeMissileEntityVelocityMultiplier = 645
attributeMissileNeverDoesDamage = 1075
attributeModifyTargetSpeedChance = 512
attributeModifyTargetSpeedRange = 514
attributeModuleReactivationDelay = 669
attributeModuleRepairRate = 1267
attributeMoonAnchorDistance = 711
attributeMoonMiningAmount = 726
attributeNeutReflectAmount = 1815
attributeNeutReflector = 1809
attributeNonBrokenModuleRepairCostMultiplier = 1276
attributeNosReflectAmount = 1814
attributeNosReflector = 1808
attributeNPCAssistancePriority = 1451
attributeNPCAssistanceRange = 1464
attributeNpcCustomsOfficeTaxRate = 1780
attributeNPCRemoteArmorRepairAmount = 1455
attributeNPCRemoteArmorRepairDuration = 1454
attributeNPCRemoteArmorRepairMaxTargets = 1501
attributeNPCRemoteArmorRepairThreshold = 1456
attributeNPCRemoteShieldBoostAmount = 1460
attributeNPCRemoteShieldBoostDuration = 1458
attributeNPCRemoteShieldBoostMaxTargets = 1502
attributeNPCRemoteShieldBoostThreshold = 1462
attributeOnliningDelay = 677
attributeOnliningRequiresSovUpgrade1 = 1601
attributeOrbitalStrikeAccuracy = 1844
attributeOrbitalStrikeDamage = 1845
attributeEntityOverviewShipGroupID = 1766
attributePinCycleTime = 1643
attributePinExtractionQuantity = 1642
attributePosAnchoredPerSolarSystemAmount = 1195
attributePowerTransferAmount = 90
attributeProbeCanScanShips = 1413
attributeOperationalDuration = 719
attributeOptimalSigRadius = 620
attributePackageRadius = 690
attributePerception = 167
attributePassiveEmDamageResistanceBonus = 994
attributePassiveExplosiveDamageResistanceBonus = 995
attributePassiveKineticDamageResistanceBonus = 996
attributePassiveThermicDamageResistanceBonus = 997
attributePlanetAnchorDistance = 865
attributePlanetRestriction = 1632
attributePosCargobayAcceptGroup = 1352
attributePosCargobayAcceptType = 1351
attributePosControlTowerPeriod = 722
attributePosPlayerControlStructure = 1167
attributePosStructureControlAmount = 1174
attributePosStructureControlDistanceMax = 1214
attributePower = 30
attributePowerEngineeringOutputBonus = 313
attributePowerIncrease = 549
attributePowerLoad = 15
attributePowerLoadLevelModifier = 1636
attributePowerLoadPerKm = 1633
attributePowerOutput = 11
attributePowerOutputMultiplier = 145
attributePowerTransferRange = 91
attributeMaxNeutralizationRange = 98
attributePreferredSignatureRadius = 1655
attributePrereqimplant = 641
attributePrimaryAttribute = 180
attributePropulsionFusionStrength = 819
attributePropulsionFusionStrengthBonus = 815
attributePropulsionIonStrength = 820
attributePropulsionIonStrengthBonus = 816
attributePropulsionMagpulseStrength = 821
attributePropulsionMagpulseStrengthBonus = 817
attributePropulsionPlasmaStrength = 822
attributePropulsionPlasmaStrengthBonus = 818
attributeProximityRange = 154
attributeQuantity = 805
attributeRaceID = 195
attributeRadius = 162
attributeRangeFactor = 1373
attributeReactionGroup1 = 842
attributeReactionGroup2 = 843
attributeRechargeRate = 55
attributeRefineryCapacity = 720
attributeRefiningDelayMultiplier = 721
attributeRefiningYieldMultiplier = 717
attributeRefiningYieldPercentage = 378
attributeReloadTime = 1795
attributeReinforcementDuration = 1612
attributeReinforcementVariance = 1613
attributeRepairCostMultiplier = 187
attributeReprocessingSkillType = 790
attributeRequiredSkill1 = 182
attributeRequiredSkill1Level = 277
attributeRequiredSkill2 = 183
attributeRequiredSkill2Level = 278
attributeRequiredSkill3 = 184
attributeRequiredSkill3Level = 279
attributeRequiredSkill4 = 1285
attributeRequiredSkill4Level = 1286
attributeRequiredSkill5 = 1289
attributeRequiredSkill5Level = 1287
attributeRequiredSkill6 = 1290
attributeRequiredSkill6Level = 1288
attributeRequiredThermoDynamicsSkill = 1212
attributeResistanceShiftAmount = 1849
attributeRigSize = 1547
attributeRigSlots = 1137
attributeScanAllStrength = 1136
attributeScanFrequencyResult = 1161
attributeScanGravimetricStrength = 211
attributeScanGravimetricStrengthBonus = 238
attributeScanGravimetricStrengthPercent = 1027
attributeScanLadarStrength = 209
attributeScanLadarStrengthBonus = 239
attributeScanLadarStrengthPercent = 1028
attributeScanMagnetometricStrength = 210
attributeScanMagnetometricStrengthBonus = 240
attributeScanMagnetometricStrengthPercent = 1029
attributeScanRadarStrength = 208
attributeScanRadarStrengthBonus = 241
attributeScanRadarStrengthPercent = 1030
attributeScanRange = 765
attributeScanResolution = 564
attributeScanResolutionBonus = 566
attributeScanResolutionMultiplier = 565
attributeScanSpeed = 79
attributeSecondaryAttribute = 181
attributeShieldBonus = 68
attributeShieldCapacity = 263
attributeShieldCapacityMultiplier = 146
attributeShieldCharge = 264
attributeShieldEmDamageResonance = 271
attributeShieldEmDamageResistanceBonus = 1489
attributeShieldExplosiveDamageResonance = 272
attributeShieldExplosiveDamageResistanceBonus = 1490
attributeShieldKineticDamageResonance = 273
attributeShieldKineticDamageResistanceBonus = 1491
attributeShieldRadius = 680
attributeShieldRechargeRate = 479
attributeShieldRechargeRateMultiplier = 134
attributeShieldThermalDamageResonance = 274
attributeShieldThermalDamageResistanceBonus = 1492
attributeShieldUniformity = 484
attributeShipBrokenModuleRepairCostMultiplier = 1277
attributeShipMaintenanceBayCapacity = 908
attributeShipScanResistance = 511
attributeShouldUseEffectMultiplier = 1652
attributeShouldUseEvasiveManeuver = 1414
attributeShouldUseTargetSwitching = 1648
attributeShouldUseSecondaryTarget = 1649
attributeShouldUseSignatureRadius = 1650
attributeSiegeModeWarpStatus = 852
attributeSignatureRadius = 552
attributeSignatureRadiusAdd = 983
attributeSignatureRadiusBonus = 554
attributeSignatureRadiusBonusPercent = 973
attributeSkillLevel = 280
attributeSkillPoints = 276
attributeSkillPointsSaved = 419
attributeSkillTimeConstant = 275
attributeSlots = 47
attributeSmugglingChance = 445
attributeSovBillSystemCost = 1603
attributeSovUpgradeBlockingUpgradeID = 1598
attributeSovUpgradeSovereigntyHeldFor = 1597
attributeSovUpgradeRequiredOutpostUpgradeLevel = 1600
attributeSovUpgradeRequiredUpgradeID = 1599
attributeSpawnWithoutGuardsToo = 903
attributeSpecialCommandCenterHoldCapacity = 1646
attributeSpecialPlanetaryCommoditiesHoldCapacity = 1653
attributeSpecialAmmoHoldCapacity = 1573
attributeSpecialFuelBayCapacity = 1549
attributeSpecialGasHoldCapacity = 1557
attributeSpecialIndustrialShipHoldCapacity = 1564
attributeSpecialLargeShipHoldCapacity = 1563
attributeSpecialMediumShipHoldCapacity = 1562
attributeSpecialMineralHoldCapacity = 1558
attributeSpecialOreHoldCapacity = 1556
attributeSpecialSalvageHoldCapacity = 1559
attributeSpecialShipHoldCapacity = 1560
attributeSpecialSmallShipHoldCapacity = 1561
attributeSpecialTutorialLootRespawnTime = 1582
attributeSpecialMaterialBayCapacity = 1770
attributeSpecialQuafeHoldCapacity = 1804
attributeSpecialisationAsteroidGroup = 781
attributeSpecialisationAsteroidYieldMultiplier = 782
attributeSpeedBonus = 80
attributeSpeedBoostFactor = 567
attributeSpeedFactor = 20
attributeStationTypeID = 472
attributeStructureBonus = 82
attributeStructureDamageAmount = 83
attributeStructureHPMultiplier = 150
attributeStructureUniformity = 525
attributeSubSystemSlot = 1366
attributeSurveyScanRange = 197
attributeSystemEffectDamageReduction = 1686
attributeTypeColorScheme = 1768
attributeTankingModifier = 1657
attributeTankingModifierDrone = 1656
attributeTargetGroup = 189
attributeTargetHostileRange = 143
attributeTargetSwitchDelay = 691
attributeTargetSwitchTimer = 1416
attributeTechLevel = 422
attributeThermalDamage = 118
attributeThermalDamageResistanceBonus = 987
attributeThermalDamageResonance = 110
attributeThermalDamageResonanceMultiplier = 130
attributeTrackingSpeedBonus = 767
attributeDisallowAgainstEwImmuneTarget = 1798
attributeTurretDamageScalingRadius = 1812
attributeTurretHardpointModifier = 1368
attributeTurretSlotsLeft = 102
attributeUnanchoringDelay = 676
attributeUnfitCapCost = 785
attributeUntargetable = 1158
attributeUpgradeCapacity = 1132
attributeUpgradeCost = 1153
attributeUpgradeLoad = 1152
attributeUpgradeSlotsLeft = 1154
attributeUsageWeighting = 862
attributeVolume = 161
attributeVelocityModifier = 1076
attributeWarpBubbleImmune = 1538
attributeWarpCapacitorNeed = 153
attributeWarpScrambleRange = 103
attributeWarpScrambleStatus = 104
attributeWarpScrambleStrength = 105
attributeWarpSpeedMultiplier = 600
attributeWillpower = 168
attributeDisallowActivateOnWarp = 1245
attributeBaseWarpSpeed = 1281
attributeMaxTargetRangeBonus = 309
attributeRateOfFire = 51
attributeWormholeMassRegeneration = 1384
attributeWormholeMaxJumpMass = 1385
attributeWormholeMaxStableMass = 1383
attributeWormholeMaxStableTime = 1382
attributeWormholeTargetSystemClass = 1381
attributeWormholeTargetDistribution = 1457
attributeNumDays = 1551
attributeCharismaBonus = 175
attributeIntelligenceBonus = 176
attributeMemoryBonus = 177
attributePerceptionBonus = 178
attributeWillpowerBonus = 179
effectAdaptiveArmorHardener = 4928
effectAnchorDrop = 649
effectAnchorDropForStructures = 1022
effectAnchorLift = 650
effectAnchorLiftForStructures = 1023
effectArmorRepair = 27
effectBarrage = 263
effectBombLaunching = 2971
effectCloaking = 607
effectCloakingWarpSafe = 980
effectCloneVatBay = 2858
effectCynosuralGeneration = 2857
effectConcordWarpScramble = 3713
effectConcordModifyTargetSpeed = 3714
effectConcordTargetJam = 3710
effectDecreaseTargetSpeed = 586
effectDefenderMissileLaunching = 103
effectDeployPledge = 4774
effectECMBurst = 53
effectEmpWave = 38
effectEmpWaveGrid = 2071
effectEnergyDestabilizationNew = 2303
effectEnergyTransfer = 31
effectEntityCapacitorDrain = 1872
effectEntitySensorDampen = 1878
effectEntityTargetJam = 1871
effectEntityTargetPaint = 1879
effectEntityTrackingDisrupt = 4982
effectEwTargetPaint = 1549
effectEwTestEffectWs = 1355
effectEwTestEffectJam = 1358
effectFighterMissile = 4729
effectFlagshipmultiRelayEffect = 1495
effectFofMissileLaunching = 104
effectFueledArmorRepair = 5275
effectFueledShieldBoosting = 4936
effectGangBonusSignature = 1411
effectGangShieldBoosterAndTransporterSpeed = 2415
effectGangShieldBoosteAndTransporterCapacitorNeed = 2418
effectGangIceHarvestingDurationBonus = 2441
effectGangInformationWarfareRangeBonus = 2642
effectGangArmorHardening = 1510
effectGangPropulsionJammingBoost = 1546
effectGangShieldHardening = 1548
effectGangECCMfixed = 1648
effectGangArmorRepairCapReducerSelfAndProjected = 3165
effectGangArmorRepairSpeedAmplifierSelfAndProjected = 3167
effectGangMiningLaserAndIceHarvesterAndGasCloudHarvesterMaxRangeBonus = 3296
effectGangGasHarvesterAndIceHarvesterAndMiningLaserDurationBonus = 3302
effectGangGasHarvesterAndIceHarvesterAndMiningLaserCapNeedBonus = 3307
effectGangInformationWarfareSuperiority = 3647
effectGangAbMwdFactorBoost = 1755
effectHackOrbital = 4773
effectHardPointModifier = 3773
effectHiPower = 12
effectIndustrialCoreEffect = 4575
effectJumpPortalGeneration = 2152
effectJumpPortalGenerationBO = 3674
effectLauncherFitted = 40
effectLeech = 3250
effectLoPower = 11
effectMedPower = 13
effectMicroJumpDrive = 4921
effectMineLaying = 102
effectMining = 17
effectMiningClouds = 2726
effectMiningLaser = 67
effectMissileLaunching = 9
effectMissileLaunchingForEntity = 569
effectModifyTargetSpeed2 = 575
effectNPCGroupArmorAssist = 4689
effectNPCGroupPropJamAssist = 4688
effectNPCGroupShieldAssist = 4686
effectNPCGroupSpeedAssist = 4687
effectNPCRemoteArmorRepair = 3852
effectNPCRemoteShieldBoost = 3855
effectNPCRemoteECM = 4656
effectOffensiveDefensiveReduction = 4728
effectOnline = 16
effectOnlineForStructures = 901
effectOpenSpawnContainer = 1738
effectOrbitalStrike = 5141
effectProbeLaunching = 3793
effectProjectileFired = 34
effectProjectileFiredForEntities = 1086
effectRemoteHullRepair = 3041
effectRemoteEcmBurst = 2913
effectRigSlot = 2663
effectSalvageDroneEffect = 5163
effectSalvaging = 2757
effectScanStrengthBonusTarget = 124
effectscanStrengthTargetPercentBonus = 2246
effectShieldBoosting = 4
effectShieldTransfer = 18
effectShieldResonanceMultiplyOnline = 105
effectSiegeModeEffect = 4877
effectSkillEffect = 132
effectSlotModifier = 3774
effectSnowBallLaunching = 2413
effectStructureUnanchorForced = 1129
effectStructureRepair = 26
effectSubSystem = 3772
effectSuicideBomb = 885
effectSuperWeaponAmarr = 4489
effectSuperWeaponCaldari = 4490
effectSuperWeaponGallente = 4491
effectSuperWeaponMinmatar = 4492
effectTargetArmorRepair = 592
effectTargetAttack = 10
effectTargetAttackForStructures = 1199
effectTargetBreaker = 4942
effectTargetTrackingDisruptorCombinedGunneryAndMissileEffect = 4932
effectTargetGunneryMaxRangeAndTrackingSpeedBonusHostile = 3555
effectTargetGunneryMaxRangeAndTrackingSpeedAndFalloffBonusHostile = 3690
effectTargetMaxTargetRangeAndScanResolutionBonusHostile = 3584
effectTargetGunneryMaxRangeAndTrackingSpeedBonusAssistance = 3556
effectTargetMaxTargetRangeAndScanResolutionBonusAssistance = 3583
effectTargetPassively = 54
effectTorpedoLaunching = 127
effectTorpedoLaunchingIsOffensive = 2576
effectTractorBeamCan = 2255
effectTriageMode = 4839
effectTriageMode7 = 4893
effectTurretFitted = 42
effectTurretWeaponRangeFalloffTrackingSpeedMultiplyTargetHostile = 3697
effectUseMissiles = 101
effectWarpDisruptSphere = 3380
effectWarpScramble = 39
effectWarpScrambleForEntity = 563
effectWarpScrambleTargetMWDBlockActivation = 3725
effectModifyShieldResonancePostPercent = 2052
effectModifyArmorResonancePostPercent = 2041
effectModifyHullResonancePostPercent = 3791
effectShipMaxTargetRangeBonusOnline = 3659
effectSensorBoostTargetedHostile = 837
effectmaxTargetRangeBonus = 2646
bloodline11Type = 1383
bloodline5Type = 1373
bloodline4Type = 1380
bloodline2Type = 1375
bloodline1Type = 1376
bloodline7Type = 1377
bloodline8Type = 1378
bloodline12Type = 1384
bloodline13Type = 1385
bloodline10Type = 1382
bloodline6Type = 1374
bloodline3Type = 1379
bloodline9Type = 1381
bloodline14Type = 1386
bloodlineAchura = 11
bloodlineAmarr = 5
bloodlineBrutor = 4
bloodlineCivire = 2
bloodlineDeteis = 1
bloodlineGallente = 7
bloodlineIntaki = 8
bloodlineJinMei = 12
bloodlineKhanid = 13
bloodlineModifier = 10
bloodlineNiKunni = 6
bloodlineSebiestor = 3
bloodlineStatic = 9
bloodlineVherokior = 14
raceCaldari = 1
raceMinmatar = 2
raceAmarr = 4
raceGallente = 8
raceJove = 16
raceAngel = 32
raceSleepers = 64
raceORE = 128
cacheEosNpcToNpcStandings = 109998
cacheAutAffiliates = 109997
cacheAutCdkeyTypes = 109996
cacheEveWarnings = 109995
cacheTutCategories = 200006
cacheTutCriterias = 200003
cacheTutTutorials = 200001
cacheTutActions = 200009
cacheDungeonArchetypes = 300001
cacheDungeonDungeons = 300005
cacheDungeonEntityGroupTypes = 300004
cacheDungeonEventMessageTypes = 300017
cacheDungeonEventTypes = 300015
cacheDungeonSpawnpoints = 300012
cacheDungeonTriggerTypes = 300013
cacheInvCategories = 600001
cacheInvContrabandTypes = 600008
cacheInvGroups = 600002
cacheInvTypes = 600004
cacheInvTypeMaterials = 600005
cacheInvTypeReactions = 600010
cacheInvWreckUsage = 600009
cacheInvMetaGroups = 600006
cacheInvMetaTypes = 600007
cacheDogmaAttributes = 800004
cacheDogmaEffects = 800005
cacheDogmaExpressionCategories = 800001
cacheDogmaExpressions = 800003
cacheDogmaOperands = 800002
cacheDogmaTypeAttributes = 800006
cacheDogmaTypeEffects = 800007
cacheDogmaUnits = 800009
cacheEveMessages = 1000001
cacheInvBlueprintTypes = 1200001
cacheMapRegions = 1409999
cacheMapConstellations = 1409998
cacheMapSolarSystems = 1409997
cacheMapSolarSystemLoadRatios = 1409996
cacheLocationWormholeClasses = 1409994
cacheMapPlanets = 1409993
cacheMapSolarSystemJumpIDs = 1409992
cacheMapTypeBalls = 1400001
cacheMapWormholeClasses = 1400003
cacheMapLocationTypes = 1400004
cacheMapCelestialDescriptions = 1400008
cacheMapNebulas = 1400016
cacheMapLocationWormholeClasses = 1400002
cacheMapRegionsTable = 1400009
cacheMapConstellationsTable = 1400010
cacheMapSolarSystemsTable = 1400011
cacheMapPlanetsTable = 1400020
cacheMapMoonsTable = 1400021
cacheMapStargateTable = 1400022
cacheMapStarsTable = 1400023
cacheMapBeltsTable = 1400024
cacheMapCelestialStatistics = 1400025
cacheNpcCommandLocations = 1600009
cacheNpcCommands = 1600005
cacheNpcDirectorCommandParameters = 1600007
cacheNpcDirectorCommands = 1600006
cacheNpcLootTableFrequencies = 1600004
cacheNpcCommandParameters = 1600008
cacheNpcTypeGroupingClassSettings = 1600016
cacheNpcTypeGroupingClasses = 1600015
cacheNpcTypeGroupingTypes = 1600017
cacheNpcTypeGroupings = 1600014
cacheNpcTypeLoots = 1600001
cacheRamSkillInfo = 1809999
cacheRamActivities = 1800003
cacheRamAssemblyLineTypes = 1800006
cacheRamAssemblyLineTypesCategory = 1800004
cacheRamAssemblyLineTypesGroup = 1800005
cacheRamCompletedStatuses = 1800007
cacheRamInstallationTypes = 1800002
cacheRamTypeRequirements = 1800001
cacheReverseEngineeringTableTypes = 1800009
cacheReverseEngineeringTables = 1800008
cacheShipInsurancePrices = 2000007
cacheShipTypes = 2000001
cacheStaOperations = 2209999
cacheStaServices = 2209998
cacheStaOperationServices = 2209997
cacheStaSIDAssemblyLineQuantity = 2209996
cacheStaSIDAssemblyLineType = 2209995
cacheStaSIDAssemblyLineTypeQuantity = 2209994
cacheStaSIDOfficeSlots = 2209993
cacheStaSIDReprocessingEfficiency = 2209992
cacheStaSIDServiceMask = 2209991
cacheStaStationImprovementTypes = 2209990
cacheStaStationUpgradeTypes = 2209989
cacheStaStations = 2209988
cacheStaStationsStatic = 2209987
cacheMktAveragePriceHistorySelect = 2409996
cacheMktAveragePricesSelectAveragePrice = 2409997
cacheMktOrderStates = 2409999
cacheMktAveragePricesSelect = 2409998
cacheMktNpcMarketData = 2400001
cacheCrpRoles = 2809999
cacheCrpActivities = 2809998
cacheCrpNpcDivisions = 2809997
cacheCrpCorporations = 2809996
cacheCrpNpcMembers = 2809994
cacheCrpPlayerCorporationIDs = 2809993
cacheCrpTickerNamesStatic = 2809992
cacheNpcSupplyDemand = 2800001
cacheCrpRegistryGroups = 2800002
cacheCrpRegistryTypes = 2800003
cacheCrpNpcCorporations = 2800006
cacheAgentAgents = 3009999
cacheAgentCorporationActivities = 3009998
cacheAgentCorporations = 3009997
cacheAgentEpicMissionMessages = 3009996
cacheAgentEpicMissionsBranching = 3009995
cacheAgentEpicMissionsNonEnd = 3009994
cacheAgtContentAgentInteractionMissions = 3009992
cacheAgtContentFlowControl = 3009991
cacheAgtContentTalkToAgentMissions = 3009990
cacheAgtPrices = 3009989
cacheAgtResearchStartupData = 3009988
cacheAgtContentTemplates = 3000001
cacheAgentMissionsKill = 3000006
cacheAgtStorylineMissions = 3000008
cacheAgtContentCourierMissions = 3000003
cacheAgtContentExchangeOffers = 3000005
cacheAgentEpicArcConnections = 3000013
cacheAgentEpicArcMissions = 3000015
cacheAgentEpicArcs = 3000012
cacheAgtContentMissionExtraStandings = 3000020
cacheAgtContentMissionTutorials = 3000018
cacheAgtContentMissionLocationFilters = 3000021
cacheAgtOfferDetails = 3000004
cacheAgtOfferTableContents = 3000010
cacheChrSchools = 3209997
cacheChrRaces = 3200001
cacheChrBloodlines = 3200002
cacheChrAncestries = 3200003
cacheChrCareers = 3200004
cacheChrSpecialities = 3200005
cacheChrBloodlineNames = 3200010
cacheChrAttributes = 3200014
cacheChrFactions = 3200015
cacheChrDefaultOverviews = 3200011
cacheChrDefaultOverviewGroups = 3200012
cacheChrNpcCharacters = 3200016
cacheFacWarCombatZoneSystems = 4500006
cacheFacWarCombatZones = 4500005
cacheRedeemWhitelist = 6300001
cacheActBillTypes = 6400004
cachePetCategories = 8109999
cachePetQueues = 8109998
cachePetCategoriesVisible = 8109997
cachePetGMQueueOrder = 8109996
cachePetOsTypes = 8109995
cacheCertificates = 5100001
cacheCertificateRelationships = 5100004
cachePlanetBlacklist = 7309999
cachePlanetSchematics = 7300004
cachePlanetSchematicsTypeMap = 7300005
cachePlanetSchematicsPinMap = 7300003
cacheMapDistrictCelestials = 100309999
cacheMapDistricts = 100300014
cacheMapBattlefields = 100300015
cacheMapLevels = 100300020
cacheMapOutposts = 100300022
cacheMapLandmarks = 100300023
cacheEspCorporations = 1
cacheEspAlliances = 2
cacheEspSolarSystems = 3
cacheSolarSystemObjects = 4
cacheCargoContainers = 5
cachePriceHistory = 6
cacheTutorialVersions = 7
cacheSolarSystemOffices = 8
tableTutorialTutorials = 200001
tableDungeonDungeons = 300005
tableAgentMissions = 3000002
corpLogoChangeCost = 100
corpRoleDiplomat = 17179869184L
corpRoleAccountCanTake1 = 134217728
corpRoleAccountCanTake2 = 268435456
corpRoleAccountCanTake3 = 536870912
corpRoleAccountCanTake4 = 1073741824
corpRoleAccountCanTake5 = 2147483648L
corpRoleAccountCanTake6 = 4294967296L
corpRoleAccountCanTake7 = 8589934592L
corpRoleAccountant = 256
corpRoleAuditor = 4096
corpRoleCanRentFactorySlot = 1125899906842624L
corpRoleCanRentOffice = 562949953421312L
corpRoleCanRentResearchSlot = 2251799813685248L
corpRoleChatManager = 36028797018963968L
corpRoleContainerCanTake1 = 4398046511104L
corpRoleContainerCanTake2 = 8796093022208L
corpRoleContainerCanTake3 = 17592186044416L
corpRoleContainerCanTake4 = 35184372088832L
corpRoleContainerCanTake5 = 70368744177664L
corpRoleContainerCanTake6 = 140737488355328L
corpRoleContainerCanTake7 = 281474976710656L
corpRoleContractManager = 72057594037927936L
corpRoleStarbaseCaretaker = 288230376151711744L
corpRoleDirector = 1
corpRoleEquipmentConfig = 2199023255552L
corpRoleFactoryManager = 1024
corpRoleFittingManager = 576460752303423488L
corpRoleHangarCanQuery1 = 1048576
corpRoleHangarCanQuery2 = 2097152
corpRoleHangarCanQuery3 = 4194304
corpRoleHangarCanQuery4 = 8388608
corpRoleHangarCanQuery5 = 16777216
corpRoleHangarCanQuery6 = 33554432
corpRoleHangarCanQuery7 = 67108864
corpRoleHangarCanTake1 = 8192
corpRoleHangarCanTake2 = 16384
corpRoleHangarCanTake3 = 32768
corpRoleHangarCanTake4 = 65536
corpRoleHangarCanTake5 = 131072
corpRoleHangarCanTake6 = 262144
corpRoleHangarCanTake7 = 524288
corpRoleJuniorAccountant = 4503599627370496L
corpRoleLocationTypeBase = 2
corpRoleLocationTypeHQ = 1
corpRoleLocationTypeOther = 3
corpRolePersonnelManager = 128
corpRoleSecurityOfficer = 512
corpRoleStarbaseConfig = 9007199254740992L
corpRoleStationManager = 2048
corpRoleTrader = 18014398509481984L
corpRoleInfrastructureTacticalOfficer = 144115188075855872L
corpHangarTakeRolesByFlag = {flagHangar: corpRoleHangarCanTake1,
 flagCorpSAG2: corpRoleHangarCanTake2,
 flagCorpSAG3: corpRoleHangarCanTake3,
 flagCorpSAG4: corpRoleHangarCanTake4,
 flagCorpSAG5: corpRoleHangarCanTake5,
 flagCorpSAG6: corpRoleHangarCanTake6,
 flagCorpSAG7: corpRoleHangarCanTake7}
corpHangarQueryRolesByFlag = {flagHangar: corpRoleHangarCanQuery1,
 flagCorpSAG2: corpRoleHangarCanQuery2,
 flagCorpSAG3: corpRoleHangarCanQuery3,
 flagCorpSAG4: corpRoleHangarCanQuery4,
 flagCorpSAG5: corpRoleHangarCanQuery5,
 flagCorpSAG6: corpRoleHangarCanQuery6,
 flagCorpSAG7: corpRoleHangarCanQuery7}
corpContainerTakeRolesByFlag = {flagHangar: corpRoleContainerCanTake1,
 flagCorpSAG2: corpRoleContainerCanTake2,
 flagCorpSAG3: corpRoleContainerCanTake3,
 flagCorpSAG4: corpRoleContainerCanTake4,
 flagCorpSAG5: corpRoleContainerCanTake5,
 flagCorpSAG6: corpRoleContainerCanTake6,
 flagCorpSAG7: corpRoleContainerCanTake7}
corpStationMgrGraceMinutes = 60
corpactivityEducation = 18
corpactivityEntertainment = 8
corpactivityMilitary = 5
corpactivitySecurity = 16
corpactivityTrading = 12
corpactivityWarehouse = 10
corpDivisionDistribution = 22
corpDivisionMining = 23
corpDivisionSecurity = 24
corporationStartupCost = 1599800
corporationAdvertisementFlatFee = 500000
corporationAdvertisementDailyRate = 250000
corporationMaxCorpRecruiters = 6
corporationMaxRecruitmentAds = 3
corporationMaxRecruitmentAdDuration = 28
corporationMinRecruitmentAdDuration = 3
corporationRecMaxTitleLength = 40
corporationRecMaxMessageLength = 1000
dunArchetypeAgentMissionDungeon = 20
dunArchetypeFacwarDefensive = 32
dunArchetypeFacwarOffensive = 35
dunArchetypeFacwarDungeons = (dunArchetypeFacwarDefensive, dunArchetypeFacwarOffensive)
dunArchetypeWormhole = 38
dunArchetypeZTest = 19
dunEventMessageEnvironment = 3
dunEventMessageImminentDanger = 1
dunEventMessageMissionInstruction = 7
dunEventMessageMissionObjective = 6
dunEventMessageMood = 4
dunEventMessageNPC = 2
dunEventMessageStory = 5
dunEventMessageWarning = 8
dunExpirationDelay = 48
dungeonGateUnlockPeriod = 66
dungeonKeylockUnlocked = 0
dungeonKeylockPrivate = 1
dungeonKeylockPublic = 2
dungeonKeylockTrigger = 3
dunTriggerArchaeologyFailure = 16
dunTriggerArchaeologySuccess = 15
dunTriggerArmorConditionLevel = 5
dunTriggerAttacked = 1
dunTriggerCounterEQ = 34
dunTriggerCounterGE = 36
dunTriggerCounterGT = 35
dunTriggerCounterLE = 38
dunTriggerCounterLT = 37
dunTriggerEffectActivated = 27
dunTriggerExploding = 3
dunTriggerFWShipEnteredProximity = 21
dunTriggerFWShipLeftProximity = 30
dunTriggerHackingFailure = 12
dunTriggerHackingSuccess = 11
dunTriggerItemInCargo = 33
dunTriggerItemPlacedInMissionContainer = 23
dunTriggerItemRemovedFromSpawnContainer = 32
dunTriggerMined = 7
dunTriggerPlayerKilled = 26
dunTriggerRoomCapturedAlliance = 19
dunTriggerRoomCapturedFacWar = 20
dunTriggerRoomCapturedCorp = 18
dunTriggerRoomEntered = 8
dunTriggerRoomMined = 10
dunTriggerRoomMinedOut = 9
dunTriggerRoomWipedOut = 31
dunTriggerSalvagingFailure = 14
dunTriggerSalvagingSuccess = 13
dunTriggerShieldConditionLevel = 4
dunTriggerShipEnteredProximity = 2
dunTriggerShipLeftProximity = 29
dunTriggerShipsEnteredRoom = 17
dunTriggerShipsLeftRoom = 28
dunTriggerStructureConditionLevel = 6
dunTriggerEventActivateGate = 1
dunTriggerEventAdjustSystemInfluence = 39
dunTriggerEventAgentMessage = 23
dunTriggerEventAgentTalkTo = 22
dunTriggerEventCounterAdd = 32
dunTriggerEventCounterDivide = 35
dunTriggerEventCounterMultiply = 34
dunTriggerEventCounterSet = 36
dunTriggerEventCounterSubtract = 33
dunTriggerEventDropLoot = 24
dunTriggerEventDungeonCompletion = 11
dunTriggerEventEffectBeaconActivate = 13
dunTriggerEventEffectBeaconDeactivate = 14
dunTriggerEventEntityDespawn = 18
dunTriggerEventEntityExplode = 19
dunTriggerEventGrantGroupReward = 37
dunTriggerEventGrantGroupRewardLimitedRestrictions = 45
dunTriggerEventGrantDelayedGroupReward = 38
dunTriggerFacWarLoyaltyPointsGranted = 48
dunTriggerFacWarVictoryPointsGranted = 20
dunTriggerEventMessage = 10
dunTriggerEventMissionCompletion = 9
dunTriggerEventMissionFailure = 31
dunTriggerEventObjectDespawn = 15
dunTriggerEventObjectExplode = 16
dunTriggerEventOpenTutorial = 46
dunTriggerEventRangedNPCDamageEM = 26
dunTriggerEventRangedNPCDamageExplosive = 27
dunTriggerEventRangedNPCDamageKinetic = 28
dunTriggerEventRangedNPCDamageThermal = 29
dunTriggerEventRangedNPCHealing = 4
dunTriggerEventRangedPlayerDamageEM = 5
dunTriggerEventRangedPlayerDamageExplosive = 6
dunTriggerEventRangedPlayerDamageKinetic = 7
dunTriggerEventRangedPlayerDamageThermal = 8
dunTriggerEventRangedPlayerHealing = 25
dunTriggerEventSpawnGuardObject = 3
dunTriggerEventSpawnGuards = 2
dunTriggerEventSpawnItemInCargo = 30
dunTriggerEventSpawnShip = 47
dunTriggerEventSupressAllRespawn = 42
dunTriggerEventWarpShipAwayAndComeBack = 41
dunTriggerEventWarpShipAwayDespawn = 40
DUNGEON_EVENT_TYPE_AFFECTS_ENTITY = [dunTriggerEventEntityExplode,
 dunTriggerEventEntityDespawn,
 dunTriggerEventSpawnGuards,
 dunTriggerEventWarpShipAwayDespawn,
 dunTriggerEventWarpShipAwayAndComeBack]
DUNGEON_EVENT_TYPE_AFFECTS_OBJECT = [dunTriggerEventSpawnGuardObject,
 dunTriggerEventEffectBeaconActivate,
 dunTriggerEventEffectBeaconDeactivate,
 dunTriggerEventObjectExplode,
 dunTriggerEventObjectDespawn,
 dunTriggerEventActivateGate]
DUNGEON_ORIGIN_UNDEFINED = None
DUNGEON_ORIGIN_STATIC = 1
DUNGEON_ORIGIN_AGENT = 2
DUNGEON_ORIGIN_PLAYTEST = 3
DUNGEON_ORIGIN_EDIT = 4
DUNGEON_ORIGIN_DISTRIBUTION = 5
DUNGEON_ORIGIN_PATH = 6
DUNGEON_ORIGIN_TUTORIAL = 7
dungeonSpawnBelts = 0
dungeonSpawnGate = 1
dungeonSpawnNear = 2
dungeonSpawnDeep = 3
dungeonSpawnReinforcments = 4
dungeonSpawnStations = 5
dungeonSpawnFaction = 6
dungeonSpawnConcord = 7
ixGroupID = 6
ixCategoryID = 7
ixCustomInfo = 8
ixStackSize = 9
ixSingleton = 10
ownerBank = 2
ownerCONCORD = 1000125
ownerNone = 0
ownerSCC = 1000132
ownerStation = 4
ownerSystem = 1
ownerUnknown = 3006
ownerCombatSimulator = 5
ownerDED = 1000137
locationAbstract = 0
locationSystem = 1
locationBank = 2
locationTemp = 5
locationTrading = 7
locationGraveyard = 8
locationUniverse = 9
locationHiddenSpace = 9000001
locationJunkyard = 10
locationCorporation = 13
locationSingletonJunkyard = 25
locationTradeSessionJunkyard = 1008
locationCharacterGraveyard = 1501
locationCorporationGraveyard = 1502
locationRAMInstalledItems = 2003
locationAlliance = 3007
locationMinJunkyardID = 1000
locationMaxJunkyardID = 1999
minFaction = 500000
maxFaction = 599999
minNPCCorporation = 1000000
maxNPCCorporation = 1999999
minAgent = 3000000
maxAgent = 3999999
minRegion = 10000000
maxRegion = 19999999
minConstellation = 20000000
maxConstellation = 29999999
minSolarSystem = 30000000
maxSolarSystem = 39999999
minValidLocation = 30000000
minValidShipLocation = 30000000
minUniverseCelestial = 40000000
maxUniverseCelestial = 49999999
minStargate = 50000000
maxStargate = 59999999
minStation = 60000000
maxNPCStation = 60999999
maxStation = 69999999
minValidCharLocation = 60000000
minUniverseAsteroid = 70000000
maxUniverseAsteroid = 79999999
minPlayerItem = 100000000
maxNonCapitalModuleSize = 500
minEveMarketGroup = 0
maxEveMarketGroup = 350000
minDustMarketGroup = 350001
maxDustMarketGroup = 999999
factionNoFaction = 0
factionAmarrEmpire = 500003
factionAmmatar = 500007
factionAngelCartel = 500011
factionCONCORDAssembly = 500006
factionCaldariState = 500001
factionGallenteFederation = 500004
factionGuristasPirates = 500010
factionInterBus = 500013
factionJoveEmpire = 500005
factionKhanidKingdom = 500008
factionMinmatarRepublic = 500002
factionMordusLegion = 500018
factionORE = 500014
factionOuterRingExcavations = 500014
factionSanshasNation = 500019
factionSerpentis = 500020
factionSistersOfEVE = 500016
factionSocietyOfConsciousThought = 500017
factionTheBloodRaiderCovenant = 500012
factionTheServantSistersofEVE = 500016
factionTheSyndicate = 500009
factionThukkerTribe = 500015
factionUnknown = 500021
factionMordusLegionCommand = 500018
factionTheInterBus = 500013
factionAmmatarMandate = 500007
factionTheSociety = 500017
refSkipLog = -1
refUndefined = 0
refPlayerTrading = 1
refMarketTransaction = 2
refGMCashTransfer = 3
refATMWithdraw = 4
refATMDeposit = 5
refBackwardCompatible = 6
refMissionReward = 7
refCloneActivation = 8
refInheritance = 9
refPlayerDonation = 10
refCorporationPayment = 11
refDockingFee = 12
refOfficeRentalFee = 13
refFactorySlotRentalFee = 14
refRepairBill = 15
refBounty = 16
refBountyPrize = 17
refInsurance = 19
refMissionExpiration = 20
refMissionCompletion = 21
refShares = 22
refCourierMissionEscrow = 23
refMissionCost = 24
refAgentMiscellaneous = 25
refPaymentToLPStore = 26
refAgentLocationServices = 27
refAgentDonation = 28
refAgentSecurityServices = 29
refAgentMissionCollateralPaid = 30
refAgentMissionCollateralRefunded = 31
refAgentMissionReward = 33
refAgentMissionTimeBonusReward = 34
refCSPA = 35
refCSPAOfflineRefund = 36
refCorporationAccountWithdrawal = 37
refCorporationDividendPayment = 38
refCorporationRegistrationFee = 39
refCorporationLogoChangeCost = 40
refReleaseOfImpoundedProperty = 41
refMarketEscrow = 42
refMarketFinePaid = 44
refBrokerfee = 46
refAllianceRegistrationFee = 48
refWarFee = 49
refAllianceMaintainanceFee = 50
refContrabandFine = 51
refCloneTransfer = 52
refAccelerationGateFee = 53
refTransactionTax = 54
refJumpCloneInstallationFee = 55
refManufacturing = 56
refResearchingTechnology = 57
refResearchingTimeProductivity = 58
refResearchingMaterialProductivity = 59
refCopying = 60
refDuplicating = 61
refReverseEngineering = 62
refContractAuctionBid = 63
refContractAuctionBidRefund = 64
refContractCollateral = 65
refContractRewardRefund = 66
refContractAuctionSold = 67
refContractReward = 68
refContractCollateralRefund = 69
refContractCollateralPayout = 70
refContractPrice = 71
refContractBrokersFee = 72
refContractSalesTax = 73
refContractDeposit = 74
refContractDepositSalesTax = 75
refSecureEVETimeCodeExchange = 76
refContractAuctionBidCorp = 77
refContractCollateralCorp = 78
refContractPriceCorp = 79
refContractBrokersFeeCorp = 80
refContractDepositCorp = 81
refContractDepositRefund = 82
refContractRewardAdded = 83
refContractRewardAddedCorp = 84
refBountyPrizes = 85
refCorporationAdvertisementFee = 86
refMedalCreation = 87
refMedalIssuing = 88
refAttributeRespecification = 90
refSovereignityRegistrarFee = 91
refSovereignityUpkeepAdjustment = 95
refPlanetaryImportTax = 96
refPlanetaryExportTax = 97
refPlanetaryConstruction = 98
refRewardManager = 99
refBountySurcharge = 101
refContractReversal = 102
refStorePurchase = 106
refStoreRefund = 107
refPlexConversion = 108
refAurumGiveAway = 109
refAurumTokenConversion = 111
refDatacoreFee = 112
refWarSurrenderFee = 113
refWarAllyContract = 114
refBountyReimbursement = 115
refKillRightBuy = 116
refMaxEve = 10000
refCorporationTaxNpcBounties = 92
refCorporationTaxAgentRewards = 93
refCorporationTaxAgentBonusRewards = 94
refCorporationTaxRewards = 103
derivedTransactionParentMapping = {refCorporationTaxNpcBounties: refBountyPrize,
 refCorporationTaxAgentRewards: refAgentMissionReward,
 refCorporationTaxAgentBonusRewards: refAgentMissionTimeBonusReward,
 refCorporationTaxRewards: refRewardManager}
recDescription = 'DESC'
recDescNpcBountyList = 'NBL'
recDescNpcBountyListTruncated = 'NBLT'
recStoreItems = 'STOREITEMS'
recDescOwners = 'OWNERIDS'
recDescOwnersTrunc = 'OWNERST'
minCorporationTaxAmount = 100000.0
stationServiceBountyMissions = 1
stationServiceAssassinationMissions = 2
stationServiceCourierMission = 4
stationServiceInterbus = 8
stationServiceReprocessingPlant = 16
stationServiceRefinery = 32
stationServiceMarket = 64
stationServiceBlackMarket = 128
stationServiceStockExchange = 256
stationServiceCloning = 512
stationServiceSurgery = 1024
stationServiceDNATherapy = 2048
stationServiceRepairFacilities = 4096
stationServiceFactory = 8192
stationServiceLaboratory = 16384
stationServiceGambling = 32768
stationServiceFitting = 65536
stationServiceNews = 262144
stationServiceStorage = 524288
stationServiceInsurance = 1048576
stationServiceDocking = 2097152
stationServiceOfficeRental = 4194304
stationServiceJumpCloneFacility = 8388608
stationServiceLoyaltyPointStore = 16777216
stationServiceNavyOffices = 33554432
stationServiceCombatSimulator = 134217728
unitAbsolutePercent = 127
unitAttributeID = 119
unitAttributePoints = 120
unitGroupID = 115
unitHour = 129
unitInverseAbsolutePercent = 108
unitInversedModifierPercent = 111
unitLength = 1
unitMass = 2
unitMilliseconds = 101
unitModifierPercent = 109
unitMoney = 133
unitSizeclass = 117
unitTime = 3
unitTypeID = 116
unitVolume = 9
unitCapacitorUnits = 114
unitSlot = 136
unitBoolean = 137
unitUnits = 138
unitBonus = 139
unitLevel = 140
unitHardpoints = 141
unitGender = 142
unitHitpoints = 113
unitMaxVelocity = 11
billTypeMarketFine = 1
billTypeRentalBill = 2
billTypeBrokerBill = 3
billTypeWarBill = 4
billTypeAllianceMaintainanceBill = 5
billTypeSovereignityMarker = 6
billUnpaid = 0
billPaid = 1
billCancelled = 2
billHidden = 3
chrattrIntelligence = 1
chrattrCharisma = 2
chrattrPerception = 3
chrattrMemory = 4
chrattrWillpower = 5
completedStatusAborted = 2
completedStatusUnanchored = 4
completedStatusDestroyed = 5
ramActivityCopying = 5
ramActivityDuplicating = 6
ramActivityInvention = 8
ramActivityManufacturing = 1
ramActivityNone = 0
ramActivityResearchingMaterialProductivity = 4
ramActivityResearchingTimeProductivity = 3
ramActivityReverseEngineering = 7
ramJobStatusPending = 1
ramJobStatusInProgress = 2
ramJobStatusReady = 3
ramJobStatusDelivered = 4
ramMaxCopyRuns = 20
ramMaxProductionTimeInDays = 30
ramRestrictNone = 0
ramRestrictBySecurity = 1
ramRestrictByStanding = 2
ramRestrictByCorp = 4
ramRestrictByAlliance = 8
activityCopying = 5
activityDuplicating = 6
activityInvention = 8
activityManufacturing = 1
activityNone = 0
activityResearchingMaterialProductivity = 4
activityResearchingTechnology = 2
activityResearchingTimeProductivity = 3
activityReverseEngineering = 7
conAvailMyAlliance = 3
conAvailMyCorp = 2
conAvailMyself = 1
conAvailPublic = 0
conStatusOutstanding = 0
conStatusInProgress = 1
conStatusFinishedIssuer = 2
conStatusFinishedContractor = 3
conStatusFinished = 4
conStatusCancelled = 5
conStatusRejected = 6
conStatusFailed = 7
conStatusDeleted = 8
conStatusReversed = 9
conTypeNothing = 0
conTypeItemExchange = 1
conTypeAuction = 2
conTypeCourier = 3
conTypeLoan = 4
facwarLPPayoutAdjustment = 10000
facwarCorporationJoining = 0
facwarCorporationActive = 1
facwarCorporationLeaving = 2
facwarStandingPerVictoryPoint = 0.0015
facwarWarningStandingCharacter = 0
facwarWarningStandingCorporation = 1
facwarMinStandingsToJoin = -0.0001
facwarSolarSystemUpgradeThresholds = [40000,
 60000,
 90000,
 140000,
 200000]
facwarSolarSystemMaxLPPool = 300000
facwarLPGainBonus = [0.5,
 1.0,
 1.75,
 2.5,
 3.25]
facwarIHubInteractDist = 2500.0
facwarBaseVictoryPointsThreshold = 3000
facwarCaptureBleedLPs = 0.1
facwarDefensivePlexingLPMultiplier = 0.75
facwarMinLPDonation = 10
facwarMaxVictoryPointsOverThreshold = 100
facwarMaxLPUnknownGroup = 25000
facwarMaxLPPayout = {groupAssaultShip: 10000,
 groupAttackBattlecruiser: 15000,
 groupBattlecruiser: 15000,
 groupBattleship: 50000,
 groupBlackOps: 150000,
 groupBlockadeRunner: 150000,
 groupCapitalIndustrialShip: 150000,
 groupCapsule: 50000,
 groupCarrier: 150000,
 groupCombatReconShip: 50000,
 groupCommandShip: 50000,
 groupCovertOps: 10000,
 groupCruiser: 10000,
 groupDestroyer: 3000,
 groupDreadnought: 150000,
 groupElectronicAttackShips: 10000,
 groupExhumer: 50000,
 groupForceReconShip: 50000,
 groupFreighter: 150000,
 groupFrigate: 2000,
 groupHeavyAssaultShip: 50000,
 groupHeavyInterdictors: 50000,
 groupIndustrial: 50000,
 groupIndustrialCommandShip: 150000,
 groupInterceptor: 10000,
 groupInterdictor: 10000,
 groupJumpFreighter: 150000,
 groupLogistics: 50000,
 groupMarauders: 150000,
 groupMiningBarge: 10000,
 groupPrototypeExplorationShip: 10000,
 groupRookieship: 2000,
 groupShuttle: 2000,
 groupStealthBomber: 10000,
 groupStrategicCruiser: 100000,
 groupSupercarrier: 150000,
 groupTitan: 150000,
 groupTransportShip: 150000}
facwarMaxLPPayoutFactionOverwrites = {groupBattleship: 150000,
 groupCruiser: 50000,
 groupFrigate: 10000,
 groupIndustrial: 150000}
facwarStatTypeKill = 0
facwarStatTypeLoss = 1
battleSquadPlayers = 4
battleSquadSlots = 4
battleServerStatusCreated = 1
battleServerStatusRequested = 2
battleServerStatusStarting = 3
battleServerStatusRunning = 4
battleServerStatusStopping = 5
battleServerStatusStopped = 6
battleServerStatusFailed = 7
battleServerStatuses = {battleServerStatusCreated: 'created',
 battleServerStatusRequested: 'requested',
 battleServerStatusStarting: 'starting',
 battleServerStatusRunning: 'running',
 battleServerStatusStopping: 'stopping',
 battleServerStatusStopped: 'stopped',
 battleServerStatusFailed: 'failed'}
battleServerStatusNames = {v:k for k, v in battleServerStatuses.iteritems()}
battleStatusCreated = 1
battleStatusStarting = 2
battleStatusRunning = 3
battleStatusCompleted = 0
battleStatuses = {battleStatusCreated: 'created',
 battleStatusStarting: 'starting',
 battleStatusRunning: 'running',
 battleStatusCompleted: 'completed'}
battleStatusNames = {v:k for k, v in battleStatuses.iteritems()}
battleTeamAttacker = 'A'
battleTeamDefender = 'D'
battleTeams = {battleTeamAttacker: 'attacker',
 battleTeamDefender: 'defender'}
battleOrbitalStatusConnected = 1
battleOrbitalStatusDisonnected = 2
battleOrbitalStatuses = {battleOrbitalStatusConnected: 'connected',
 battleOrbitalStatusDisonnected: 'disconnected'}
battleOrbitalSupportStatusRequested = 1
battleOrbitalSupportStatusPending = 2
battleOrbitalSupportStatusApproved = 3
battleOrbitalSupportStatusCompleted = 4
battleOrbitalSupportStatuses = {battleOrbitalSupportStatusRequested: 'requested',
 battleOrbitalSupportStatusPending: 'pending',
 battleOrbitalSupportStatusApproved: 'approved',
 battleOrbitalSupportStatusCompleted: 'completed'}
districtWarpinRange = 1.4
districtConflictActionTake = 1
districtConflictActionDestroy = 2
districtConflictActions = (districtConflictActionTake, districtConflictActionDestroy)
districtConflictStatusCreated = 1
districtConflictStatusStarted = 2
districtConflictStatusResolved = 100
districtConflictStatusTaken = 101
districtConflictStatusDestroyed = 102
districtConflictStatusDefended = 103
districtConflictStatusReverted = 104
districtConflictStatuses = (districtConflictStatusCreated,
 districtConflictStatusStarted,
 districtConflictStatusTaken,
 districtConflictStatusDestroyed,
 districtConflictStatusDefended,
 districtConflictStatusReverted)
districtContractTypeAttack = 1
districtContractTypeDefense = 2
districtContractTypes = {districtContractTypeAttack: 'attack',
 districtContractTypeDefense: 'defense'}
districtContractStatusOffered = 1
districtContractStatusCreated = 2
districtContractStatusAssigned = 3
districtContractStatusCompleted = 100
districtContractStatusSuccess = 101
districtContractStatusFailed = 102
districtContractStatusCancelled = 103
districtContractStatusReverted = 104
districtContractStatuses = (districtContractStatusOffered,
 districtContractStatusCreated,
 districtContractStatusAssigned,
 districtContractStatusSuccess,
 districtContractStatusFailed,
 districtContractStatusCancelled,
 districtContractStatusReverted)
averageManufacturingCostPerUnitTime = 0
blockAmarrCaldari = 1
blockGallenteMinmatar = 2
blockSmugglingCartel = 3
blockTerrorist = 4
cargoContainerLifetime = 120
containerCharacter = 10011
containerCorpMarket = 10012
containerGlobal = 10002
containerHangar = 10004
containerOffices = 10009
containerRecycler = 10008
containerSolarSystem = 10003
containerStationCharacters = 10010
containerWallet = 10001
costCloneContract = 5600
costJumpClone = 100000
crpApplicationAcceptedByCharacter = 2
crpApplicationAcceptedByCorporation = 6
crpApplicationAppliedByCharacter = 0
crpApplicationRejectedByCharacter = 3
crpApplicationRejectedByCorporation = 4
crpApplicationRenegotiatedByCharacter = 1
crpApplicationRenegotiatedByCorporation = 5
crpApplicationWithdrawnByCharacter = 7
crpApplicationMaxSize = 1000
crpApplicationEndStatuses = [crpApplicationRejectedByCorporation,
 crpApplicationWithdrawnByCharacter,
 crpApplicationAcceptedByCharacter,
 crpApplicationRejectedByCharacter]
deftypeCapsule = 670
deftypeHouseWarmingGift = 34
directorConcordSecurityLevelMax = 1000
directorConcordSecurityLevelMin = 450
directorConvoySecurityLevelMin = 450
directorPirateGateSecurityLevelMax = 349
directorPirateGateSecurityLevelMin = -1000
directorPirateSecurityLevelMax = 849
directorPirateSecurityLevelMin = -1000
entityApproaching = 3
entityCombat = 1
entityDeparting = 4
entityDeparting2 = 5
entityEngage = 10
entityFleeing = 7
entityIdle = 0
entityMining = 2
entityOperating = 9
entityPursuit = 6
entitySalvaging = 18
fleetGroupingRange = 300
fleetJobCreator = 2
fleetJobNone = 0
fleetJobScout = 1
fleetLeaderRole = 1
fleetRoleLeader = 1
fleetRoleMember = 4
fleetRoleSquadCmdr = 3
fleetRoleWingCmdr = 2
fleetBoosterNone = 0
fleetBoosterFleet = 1
fleetBoosterWing = 2
fleetBoosterSquad = 3
rejectFleetInviteTimeout = 1
rejectFleetInviteAlreadyInFleet = 2
fleetRejectionReasons = {rejectFleetInviteTimeout: 'UI/Fleet/FleetServer/NoResponse',
 rejectFleetInviteAlreadyInFleet: 'UI/Fleet/FleetServer/AlreadyInFleet'}
graphicCorpLogoLibNoShape = 415
graphicCorpLogoLibShapes = {415: 'res:/UI/Texture/corpLogoLibs/415.png',
 416: 'res:/UI/Texture/corpLogoLibs/416.png',
 417: 'res:/UI/Texture/corpLogoLibs/417.png',
 418: 'res:/UI/Texture/corpLogoLibs/418.png',
 419: 'res:/UI/Texture/corpLogoLibs/419.png',
 420: 'res:/UI/Texture/corpLogoLibs/420.png',
 421: 'res:/UI/Texture/corpLogoLibs/421.png',
 422: 'res:/UI/Texture/corpLogoLibs/422.png',
 423: 'res:/UI/Texture/corpLogoLibs/423.png',
 424: 'res:/UI/Texture/corpLogoLibs/424.png',
 425: 'res:/UI/Texture/corpLogoLibs/425.png',
 426: 'res:/UI/Texture/corpLogoLibs/426.png',
 427: 'res:/UI/Texture/corpLogoLibs/427.png',
 428: 'res:/UI/Texture/corpLogoLibs/428.png',
 429: 'res:/UI/Texture/corpLogoLibs/429.png',
 430: 'res:/UI/Texture/corpLogoLibs/430.png',
 431: 'res:/UI/Texture/corpLogoLibs/431.png',
 432: 'res:/UI/Texture/corpLogoLibs/432.png',
 433: 'res:/UI/Texture/corpLogoLibs/433.png',
 434: 'res:/UI/Texture/corpLogoLibs/434.png',
 435: 'res:/UI/Texture/corpLogoLibs/435.png',
 436: 'res:/UI/Texture/corpLogoLibs/436.png',
 437: 'res:/UI/Texture/corpLogoLibs/437.png',
 438: 'res:/UI/Texture/corpLogoLibs/438.png',
 439: 'res:/UI/Texture/corpLogoLibs/439.png',
 440: 'res:/UI/Texture/corpLogoLibs/440.png',
 441: 'res:/UI/Texture/corpLogoLibs/441.png',
 442: 'res:/UI/Texture/corpLogoLibs/442.png',
 443: 'res:/UI/Texture/corpLogoLibs/443.png',
 444: 'res:/UI/Texture/corpLogoLibs/444.png',
 445: 'res:/UI/Texture/corpLogoLibs/445.png',
 446: 'res:/UI/Texture/corpLogoLibs/446.png',
 447: 'res:/UI/Texture/corpLogoLibs/447.png',
 448: 'res:/UI/Texture/corpLogoLibs/448.png',
 449: 'res:/UI/Texture/corpLogoLibs/449.png',
 450: 'res:/UI/Texture/corpLogoLibs/450.png',
 451: 'res:/UI/Texture/corpLogoLibs/451.png',
 452: 'res:/UI/Texture/corpLogoLibs/452.png',
 453: 'res:/UI/Texture/corpLogoLibs/453.png',
 454: 'res:/UI/Texture/corpLogoLibs/454.png',
 455: 'res:/UI/Texture/corpLogoLibs/455.png',
 456: 'res:/UI/Texture/corpLogoLibs/456.png',
 457: 'res:/UI/Texture/corpLogoLibs/457.png',
 458: 'res:/UI/Texture/corpLogoLibs/458.png',
 459: 'res:/UI/Texture/corpLogoLibs/459.png',
 460: 'res:/UI/Texture/corpLogoLibs/460.png',
 461: 'res:/UI/Texture/corpLogoLibs/461.png',
 462: 'res:/UI/Texture/corpLogoLibs/462.png',
 463: 'res:/UI/Texture/corpLogoLibs/463.png',
 464: 'res:/UI/Texture/corpLogoLibs/464.png',
 465: 'res:/UI/Texture/corpLogoLibs/465.png',
 466: 'res:/UI/Texture/corpLogoLibs/466.png',
 467: 'res:/UI/Texture/corpLogoLibs/467.png',
 468: 'res:/UI/Texture/corpLogoLibs/468.png',
 469: 'res:/UI/Texture/corpLogoLibs/469.png',
 470: 'res:/UI/Texture/corpLogoLibs/470.png',
 471: 'res:/UI/Texture/corpLogoLibs/471.png',
 472: 'res:/UI/Texture/corpLogoLibs/472.png',
 473: 'res:/UI/Texture/corpLogoLibs/473.png',
 474: 'res:/UI/Texture/corpLogoLibs/474.png',
 475: 'res:/UI/Texture/corpLogoLibs/475.png',
 476: 'res:/UI/Texture/corpLogoLibs/476.png',
 477: 'res:/UI/Texture/corpLogoLibs/477.png',
 478: 'res:/UI/Texture/corpLogoLibs/478.png',
 479: 'res:/UI/Texture/corpLogoLibs/479.png',
 480: 'res:/UI/Texture/corpLogoLibs/480.png',
 481: 'res:/UI/Texture/corpLogoLibs/481.png',
 482: 'res:/UI/Texture/corpLogoLibs/482.png',
 483: 'res:/UI/Texture/corpLogoLibs/483.png',
 484: 'res:/UI/Texture/corpLogoLibs/484.png',
 485: 'res:/UI/Texture/corpLogoLibs/485.png',
 486: 'res:/UI/Texture/corpLogoLibs/486.png',
 487: 'res:/UI/Texture/corpLogoLibs/487.png',
 488: 'res:/UI/Texture/corpLogoLibs/488.png',
 489: 'res:/UI/Texture/corpLogoLibs/489.png',
 490: 'res:/UI/Texture/corpLogoLibs/490.png',
 491: 'res:/UI/Texture/corpLogoLibs/491.png',
 492: 'res:/UI/Texture/corpLogoLibs/492.png',
 493: 'res:/UI/Texture/corpLogoLibs/493.png',
 494: 'res:/UI/Texture/corpLogoLibs/494.png',
 495: 'res:/UI/Texture/corpLogoLibs/495.png',
 496: 'res:/UI/Texture/corpLogoLibs/496.png',
 497: 'res:/UI/Texture/corpLogoLibs/497.png',
 498: 'res:/UI/Texture/corpLogoLibs/498.png',
 499: 'res:/UI/Texture/corpLogoLibs/499.png',
 500: 'res:/UI/Texture/corpLogoLibs/500.png',
 501: 'res:/UI/Texture/corpLogoLibs/501.png',
 502: 'res:/UI/Texture/corpLogoLibs/502.png',
 503: 'res:/UI/Texture/corpLogoLibs/503.png',
 504: 'res:/UI/Texture/corpLogoLibs/504.png',
 505: 'res:/UI/Texture/corpLogoLibs/505.png',
 506: 'res:/UI/Texture/corpLogoLibs/506.png',
 507: 'res:/UI/Texture/corpLogoLibs/507.png',
 508: 'res:/UI/Texture/corpLogoLibs/508.png',
 509: 'res:/UI/Texture/corpLogoLibs/509.png',
 510: 'res:/UI/Texture/corpLogoLibs/510.png',
 511: 'res:/UI/Texture/corpLogoLibs/511.png',
 512: 'res:/UI/Texture/corpLogoLibs/512.png',
 513: 'res:/UI/Texture/corpLogoLibs/513.png',
 514: 'res:/UI/Texture/corpLogoLibs/514.png',
 515: 'res:/UI/Texture/corpLogoLibs/515.png',
 516: 'res:/UI/Texture/corpLogoLibs/516.png',
 517: 'res:/UI/Texture/corpLogoLibs/517.png',
 518: 'res:/UI/Texture/corpLogoLibs/518.png',
 519: 'res:/UI/Texture/corpLogoLibs/519.png',
 520: 'res:/UI/Texture/corpLogoLibs/520.png',
 521: 'res:/UI/Texture/corpLogoLibs/521.png',
 522: 'res:/UI/Texture/corpLogoLibs/522.png',
 523: 'res:/UI/Texture/corpLogoLibs/523.png',
 524: 'res:/UI/Texture/corpLogoLibs/524.png',
 525: 'res:/UI/Texture/corpLogoLibs/525.png',
 526: 'res:/UI/Texture/corpLogoLibs/526.png',
 527: 'res:/UI/Texture/corpLogoLibs/527.png',
 528: 'res:/UI/Texture/corpLogoLibs/528.png',
 529: 'res:/UI/Texture/corpLogoLibs/529.png',
 530: 'res:/UI/Texture/corpLogoLibs/530.png',
 531: 'res:/UI/Texture/corpLogoLibs/531.png',
 532: 'res:/UI/Texture/corpLogoLibs/532.png',
 533: 'res:/UI/Texture/corpLogoLibs/533.png',
 534: 'res:/UI/Texture/corpLogoLibs/534.png',
 535: 'res:/UI/Texture/corpLogoLibs/535.png',
 536: 'res:/UI/Texture/corpLogoLibs/536.png',
 537: 'res:/UI/Texture/corpLogoLibs/537.png',
 538: 'res:/UI/Texture/corpLogoLibs/538.png',
 539: 'res:/UI/Texture/corpLogoLibs/539.png',
 540: 'res:/UI/Texture/corpLogoLibs/540.png',
 541: 'res:/UI/Texture/corpLogoLibs/541.png',
 542: 'res:/UI/Texture/corpLogoLibs/542.png',
 543: 'res:/UI/Texture/corpLogoLibs/543.png',
 544: 'res:/UI/Texture/corpLogoLibs/544.png',
 545: 'res:/UI/Texture/corpLogoLibs/545.png',
 546: 'res:/UI/Texture/corpLogoLibs/546.png',
 547: 'res:/UI/Texture/corpLogoLibs/547.png',
 548: 'res:/UI/Texture/corpLogoLibs/548.png',
 549: 'res:/UI/Texture/corpLogoLibs/549.png',
 550: 'res:/UI/Texture/corpLogoLibs/550.png',
 551: 'res:/UI/Texture/corpLogoLibs/551.png',
 552: 'res:/UI/Texture/corpLogoLibs/552.png',
 553: 'res:/UI/Texture/corpLogoLibs/553.png',
 554: 'res:/UI/Texture/corpLogoLibs/554.png',
 555: 'res:/UI/Texture/corpLogoLibs/555.png',
 556: 'res:/UI/Texture/corpLogoLibs/556.png',
 557: 'res:/UI/Texture/corpLogoLibs/557.png',
 558: 'res:/UI/Texture/corpLogoLibs/558.png',
 559: 'res:/UI/Texture/corpLogoLibs/559.png',
 560: 'res:/UI/Texture/corpLogoLibs/560.png',
 561: 'res:/UI/Texture/corpLogoLibs/561.png',
 562: 'res:/UI/Texture/corpLogoLibs/562.png',
 563: 'res:/UI/Texture/corpLogoLibs/563.png',
 564: 'res:/UI/Texture/corpLogoLibs/564.png',
 565: 'res:/UI/Texture/corpLogoLibs/565.png',
 566: 'res:/UI/Texture/corpLogoLibs/566.png',
 567: 'res:/UI/Texture/corpLogoLibs/567.png',
 568: 'res:/UI/Texture/corpLogoLibs/568.png',
 569: 'res:/UI/Texture/corpLogoLibs/569.png',
 570: 'res:/UI/Texture/corpLogoLibs/570.png',
 571: 'res:/UI/Texture/corpLogoLibs/571.png',
 572: 'res:/UI/Texture/corpLogoLibs/572.png',
 573: 'res:/UI/Texture/corpLogoLibs/573.png',
 574: 'res:/UI/Texture/corpLogoLibs/574.png',
 575: 'res:/UI/Texture/corpLogoLibs/575.png',
 576: 'res:/UI/Texture/corpLogoLibs/576.png',
 577: 'res:/UI/Texture/corpLogoLibs/577.png'}
dustCharPortraits = {0: {0: {'128': 'res:/UI/Texture/dustCharacterPortraits/female/DustAvatar1_128.png',
         '64': 'res:/UI/Texture/dustCharacterPortraits/female/DustAvatar1_64.png'},
     1: {'128': 'res:/UI/Texture/dustCharacterPortraits/female/DustAvatar2_128.png',
         '64': 'res:/UI/Texture/dustCharacterPortraits/female/DustAvatar2_64.png'},
     2: {'128': 'res:/UI/Texture/dustCharacterPortraits/female/DustAvatar3_128.png',
         '64': 'res:/UI/Texture/dustCharacterPortraits/female/DustAvatar3_64.png'},
     3: {'128': 'res:/UI/Texture/dustCharacterPortraits/female/DustAvatar4_128.png',
         '64': 'res:/UI/Texture/dustCharacterPortraits/female/DustAvatar4_64.png'}},
 1: {0: {'128': 'res:/UI/Texture/dustCharacterPortraits/male/DustAvatar1_128.png',
         '64': 'res:/UI/Texture/dustCharacterPortraits/male/DustAvatar1_64.png'},
     1: {'128': 'res:/UI/Texture/dustCharacterPortraits/male/DustAvatar2_128.png',
         '64': 'res:/UI/Texture/dustCharacterPortraits/male/DustAvatar2_64.png'},
     2: {'128': 'res:/UI/Texture/dustCharacterPortraits/male/DustAvatar3_128.png',
         '64': 'res:/UI/Texture/dustCharacterPortraits/male/DustAvatar3_64.png'},
     3: {'128': 'res:/UI/Texture/dustCharacterPortraits/male/DustAvatar4_128.png',
         '64': 'res:/UI/Texture/dustCharacterPortraits/male/DustAvatar4_64.png'}}}
CORPLOGO_BLEND = 1
CORPLOGO_SOLID = 2
CORPLOGO_GRADIENT = 3
graphicCorpLogoLibColors = {671: ((0.125, 0.125, 0.125, 1.0), CORPLOGO_SOLID),
 672: ((0.59, 0.5, 0.35, 1.0), CORPLOGO_GRADIENT),
 673: ((0.66, 0.83, 1.0, 1.0), CORPLOGO_BLEND),
 674: ((1.0, 1.0, 1.0, 1.0), CORPLOGO_BLEND),
 675: ((0.29, 0.29, 0.29, 1.0), CORPLOGO_GRADIENT),
 676: ((0.66, 1.04, 2.0, 1.0), CORPLOGO_BLEND),
 677: ((2.0, 1.4, 0.5, 1.0), CORPLOGO_BLEND),
 678: ((0.57, 0.6, 0.6, 1.0), CORPLOGO_BLEND),
 679: ((1.0, 0.47, 0.0, 1.0), CORPLOGO_BLEND),
 680: ((0.59, 0.0, 0.0, 1.0), CORPLOGO_BLEND),
 681: ((0.49, 0.5, 0.5, 1.0), CORPLOGO_GRADIENT),
 682: ((0.0, 0.0, 0.0, 0.5), CORPLOGO_SOLID),
 683: ((0.49, 0.5, 0.5, 0.41), CORPLOGO_SOLID),
 684: ((0.91, 0.91, 0.91, 1.0), CORPLOGO_SOLID),
 685: ((1.0, 0.7, 0.24, 1.0), CORPLOGO_SOLID)}
iconUnknown = 0
iconSkill = 33
iconModuleSensorDamper = 105
iconModuleECM = 109
iconModuleWarpScrambler = 111
iconModuleStasisWeb = 1284
iconDuration = 1392
iconModuleTrackingDisruptor = 1639
iconModuleTargetPainter = 2983
iconModuleDroneCommand = 2987
iconModuleNosferatu = 1029
iconModuleEnergyNeutralizer = 1283
iconWillpower = 3127
iconFemale = 3267
iconMale = 3268
invulnerabilityDocking = 3000
invulnerabilityJumping = 5000
invulnerabilityRestoring = 60000
invulnerabilityUndocking = 30000
invulnerabilityWarpingIn = 10000
invulnerabilityWarpingOut = 5000
jumpRadiusFactor = 130
jumpRadiusRandom = 15000
lifetimeOfDefaultContainer = 120
lifetimeOfDurableContainers = 43200
limitCloneJumpHours = 24
lockedContainerAccessTime = 180000
marketCommissionPercentage = 1
maxBoardingDistance = 6550
maxBuildDistance = 10000
maxCargoContainerTransferDistance = 2500
maxConfigureDistance = 5000
maxDockingDistance = 50000
maxDungeonPlacementDistance = 300
maxItemCountPerLocation = 1000
maxJumpInDistance = 13000
maxPetitionsPerDay = 2
maxSelfDestruct = 15000
maxStargateJumpingDistance = 2500
maxWormholeEnterDistance = 5000
maxWarpEndDistance = 100000
maxWarpSpeed = 30
minAutoPilotWarpInDistance = 15000
minCloakingDistance = 2000
minDungeonPlacementDistance = 25
minJumpInDistance = 12000
minJumpDriveDistance = 100000
minSpawnContainerDelay = 300000
minSpecialTutorialSpawnContainerDelay = 10000
minWarpDistance = 150000
minWarpEndDistance = 0
mktMinimumFee = 100
mktModificationDelay = 300
mktOrderCancelled = 3
mktOrderExpired = 2
mktTransactionTax = 1.5
npcCorpMax = 1999999
npcCorpMin = 1000000
npcDivisionAccounting = 1
npcDivisionAdministration = 2
npcDivisionAdvisory = 3
npcDivisionArchives = 4
npcDivisionAstrosurveying = 5
npcDivisionCommand = 6
npcDivisionDistribution = 7
npcDivisionFinancial = 8
npcDivisionIntelligence = 9
npcDivisionInternalSecurity = 10
npcDivisionLegal = 11
npcDivisionManufacturing = 12
npcDivisionMarketing = 13
npcDivisionMining = 14
npcDivisionPersonnel = 15
npcDivisionProduction = 16
npcDivisionPublicRelations = 17
npcDivisionRD = 18
npcDivisionSecurity = 19
npcDivisionStorage = 20
npcDivisionSurveillance = 21
onlineCapacitorChargeRatio = 95
onlineCapacitorRemainderRatio = 33
outlawSecurityStatus = -5
petitionMaxChatLogSize = 200000
petitionMaxCombatLogSize = 200000
posShieldStartLevel = 0.505
posMaxShieldPercentageForWatch = 0.95
posMinDamageDiffToPersist = 0.05
rangeConstellation = 4
rangeRegion = 32767
rangeSolarSystem = 0
rangeStation = -1
rentalPeriodOffice = 30
repairCostPercentage = 100
secLevelForBounty = -1
sentryTargetSwitchDelay = 40000
shipHidingCombatDelay = 120000
shipHidingDelay = 60000
shipHidingPvpCombatDelay = 900000
simulationTimeStep = 1000
skillEventCharCreation = 33
skillEventClonePenalty = 34
skillEventGMGive = 39
skillEventHaltedAccountLapsed = 260
skillEventTaskMaster = 35
skillEventTrainingCancelled = 38
skillEventTrainingComplete = 37
skillEventTrainingStarted = 36
skillEventQueueTrainingCompleted = 53
skillEventSkillInjected = 56
skillEventFreeSkillPointsUsed = 307
skillEventGMReverseFreeSkillPointsUsed = 309
skillPointMultiplier = 250
solarsystemTimeout = 86400
sovereignityBillingPeriod = 14
sovereigntyDisruptorAnchorRange = 20000
sovereigntyDisruptorAnchorRangeMinBetween = 45000
starbaseSecurityLimit = 800
terminalExplosionDelay = 30
visibleSubSystems = 5
voteCEO = 0
voteGeneral = 4
voteItemLockdown = 5
voteItemUnlock = 6
voteKickMember = 3
voteShares = 2
voteWar = 1
warRelationshipAlliesAtWar = 5
warRelationshipAtWar = 3
warRelationshipAtWarCanFight = 4
warRelationshipUnknown = 0
warRelationshipYourAlliance = 2
warRelationshipYourCorp = 1
warpJitterRadius = 2500
scanProbeNumberOfRangeSteps = 8
scanProbeBaseNumberOfProbes = 4
solarSystemPolaris = 30000380
maxLoyaltyStoreBulkOffers = 100
leaderboardShipTypeAll = 0
leaderboardShipTypeTopFrigate = 1
leaderboardShipTypeTopDestroyer = 2
leaderboardShipTypeTopCruiser = 3
leaderboardShipTypeTopBattlecruiser = 4
leaderboardShipTypeTopBattleship = 5
leaderboardPeopleBuddies = 1
leaderboardPeopleCorpMembers = 2
leaderboardPeopleAllianceMembers = 3
leaderboardPeoplePlayersInSim = 4
securityClassZeroSec = 0
securityClassLowSec = 1
securityClassHighSec = 2
contestionStateNone = 0
contestionStateContested = 1
contestionStateVulnerable = 2
contestionStateCaptured = 3
aggressionTime = 15
certificateGradeBasic = 1
certificateGradeStandard = 2
certificateGradeImproved = 3
certificateGradeAdvanced = 4
certificateGradeElite = 5
medalMinNameLength = 3
medalMaxNameLength = 100
medalMaxDescriptionLength = 1000
medalMinDescriptionLength = 10
respecTimeInterval = 365 * DAY
respecMinimumAttributeValue = 17
respecMaximumAttributeValue = 27
respecTotalRespecPoints = 99
probeStateInactive = 0
probeStateIdle = 1
probeStateMoving = 2
probeStateWarping = 3
probeStateScanning = 4
probeStateReturning = 5
probeResultPerfect = 1.0
probeResultInformative = 0.75
probeResultGood = 0.25
probeResultUnusable = 0.001
shipNotWarping = 0
shipWarping = 1
shipAligning = 2
warpTypeNone = 0
warpTypeRegular = 1
warpTypeForced = 2
probeScanGroupScrap = 1
probeScanGroupSignatures = 4
probeScanGroupShips = 8
probeScanGroupStructures = 16
probeScanGroupDronesAndProbes = 32
probeScanGroupCelestials = 64
probeScanGroupAnomalies = 128
probeScanGroups = {}
probeScanGroups[probeScanGroupScrap] = set([groupBiomass,
 groupCargoContainer,
 groupWreck,
 groupSecureCargoContainer,
 groupAuditLogSecureContainer])
probeScanGroups[probeScanGroupSignatures] = set([groupCosmicSignature])
probeScanGroups[probeScanGroupAnomalies] = set([groupCosmicAnomaly])
probeScanGroups[probeScanGroupShips] = set([groupAssaultShip,
 groupAttackBattlecruiser,
 groupBattlecruiser,
 groupBattleship,
 groupBlackOps,
 groupBlockadeRunner,
 groupCapitalIndustrialShip,
 groupCapsule,
 groupCarrier,
 groupCombatReconShip,
 groupCommandShip,
 groupCovertOps,
 groupCruiser,
 groupDestroyer,
 groupDreadnought,
 groupElectronicAttackShips,
 groupEliteBattleship,
 groupExhumer,
 groupForceReconShip,
 groupFreighter,
 groupFrigate,
 groupHeavyAssaultShip,
 groupHeavyInterdictors,
 groupIndustrial,
 groupIndustrialCommandShip,
 groupInterceptor,
 groupInterdictor,
 groupJumpFreighter,
 groupLogistics,
 groupMarauders,
 groupMiningBarge,
 groupSupercarrier,
 groupPrototypeExplorationShip,
 groupRookieship,
 groupShuttle,
 groupStealthBomber,
 groupTitan,
 groupTransportShip,
 groupStrategicCruiser])
probeScanGroups[probeScanGroupStructures] = set([groupConstructionPlatform,
 groupStationUpgradePlatform,
 groupStationImprovementPlatform,
 groupMobileWarpDisruptor,
 groupAssemblyArray,
 groupControlTower,
 groupCorporateHangarArray,
 groupElectronicWarfareBattery,
 groupEnergyNeutralizingBattery,
 groupForceFieldArray,
 groupJumpPortalArray,
 groupLogisticsArray,
 groupMobileHybridSentry,
 groupMobileLaboratory,
 groupMobileLaserSentry,
 groupMobileMissileSentry,
 groupMobilePowerCore,
 groupMobileProjectileSentry,
 groupMobileReactor,
 groupMobileShieldGenerator,
 groupMobileStorage,
 groupMoonMining,
 groupRefiningArray,
 groupScannerArray,
 groupSensorDampeningBattery,
 groupShieldHardeningArray,
 groupShipMaintenanceArray,
 groupSilo,
 groupStasisWebificationBattery,
 groupStealthEmitterArray,
 groupTrackingArray,
 groupWarpScramblingBattery,
 groupCynosuralSystemJammer,
 groupCynosuralGeneratorArray,
 groupInfrastructureHub,
 groupSovereigntyClaimMarkers,
 groupSovereigntyDisruptionStructures,
 groupOrbitalConstructionPlatforms,
 groupPlanetaryCustomsOffices,
 groupSatellite])
probeScanGroups[probeScanGroupDronesAndProbes] = set([groupCapDrainDrone,
 groupCombatDrone,
 groupElectronicWarfareDrone,
 groupFighterDrone,
 groupFighterBomber,
 groupLogisticDrone,
 groupMiningDrone,
 groupProximityDrone,
 groupRepairDrone,
 groupStasisWebifyingDrone,
 groupUnanchoringDrone,
 groupWarpScramblingDrone,
 groupScannerProbe,
 groupSurveyProbe,
 groupSalvageDrone,
 groupWarpDisruptionProbe])
probeScanGroups[probeScanGroupCelestials] = set([groupAsteroidBelt,
 groupForceField,
 groupMoon,
 groupPlanet,
 groupStargate,
 groupSun,
 groupStation])
planetResourceScanDistance = 1000000000
planetResourceProximityDistant = 0
planetResourceProximityRegion = 1
planetResourceProximityConstellation = 2
planetResourceProximitySystem = 3
planetResourceProximityPlanet = 4
planetResourceProximityLimits = [(2, 6),
 (4, 10),
 (6, 15),
 (10, 20),
 (15, 30)]
planetResourceScanningRanges = [9.0,
 7.0,
 5.0,
 3.0,
 1.0]
planetResourceUpdateTime = 1 * HOUR
planetResourceMaxValue = 1.21
mapWormholeRegionMin = 11000000
mapWormholeRegionMax = 11999999
mapWormholeConstellationMin = 21000000
mapWormholeConstellationMax = 21999999
mapWormholeSystemMin = 31000000
mapWormholeSystemMax = 31999999
mapWorldSpaceMin = 81000000
mapWorldSpaceMax = 81999999
skillQueueTime = 864000000000L
skillQueueMaxSkills = 50
skillsWithHintPerMinute = 50
shipColor = {'MAIN': {raceAmarr: {0: (0.5, 0.5, 0.5, 1.0)},
          raceCaldari: {0: (0.36, 0.37, 0.37, 1.0),
                        1: (0.23, 0.24, 0.22, 1.0),
                        2: (0.33, 0.32, 0.3, 1.0),
                        3: (0.21, 0.25, 0.26, 1.0),
                        4: (0.21, 0.21, 0.21, 1.0)},
          raceGallente: {0: (0.5, 0.5, 0.5, 1.0)},
          raceMinmatar: {0: (0.5, 0.5, 0.5, 1.0)}},
 'MARKINGS': {raceAmarr: {0: (0.5, 0.5, 0.5, 1.0)},
              raceCaldari: {0: (0.63, 0.63, 0.63, 1.0),
                            1: (0.2, 0.09, 0.05, 1.0),
                            2: (0.1, 0.18, 0.23, 1.0),
                            3: (0.08, 0.08, 0.08, 1.0),
                            4: (0.2, 0.18, 0.12, 1.0)},
              raceGallente: {0: (0.5, 0.5, 0.5, 1.0)},
              raceMinmatar: {0: (0.5, 0.5, 0.5, 1.0)}},
 'LIGHTS': {raceAmarr: {0: (0.5, 0.5, 0.5, 1.0)},
            raceCaldari: {0: (0.56, 0.76, 0.92, 1.0),
                          1: (0.57, 0.57, 0.5, 1.0),
                          2: (0.76, 0.74, 0.51, 1.0),
                          3: (0.7, 0.85, 0.52, 1.0),
                          4: (0.99, 0.65, 0.43, 1.0)},
            raceGallente: {0: (0.5, 0.5, 0.5, 1.0)},
            raceMinmatar: {0: (0.5, 0.5, 0.5, 1.0)}}}
agentMissionOffered = 'offered'
agentMissionOfferAccepted = 'offer_accepted'
agentMissionOfferDeclined = 'offer_declined'
agentMissionOfferExpired = 'offer_expired'
agentMissionOfferRemoved = 'offer_removed'
agentMissionAccepted = 'accepted'
agentMissionDeclined = 'declined'
agentMissionCompleted = 'completed'
agentTalkToMissionCompleted = 'talk_to_completed'
agentMissionQuit = 'quit'
agentMissionFailed = 'failed'
agentMissionResearchUpdatePPD = 'research_update_ppd'
agentMissionResearchStarted = 'research_started'
agentMissionProlonged = 'prolong'
agentMissionReset = 'reset'
agentMissionModified = 'modified'
agentMissionFailed = 'failed'
agentMissionStateAllocated = 0
agentMissionStateOffered = 1
agentMissionStateAccepted = 2
agentMissionStateFailed = 3
agentMissionDungeonStarted = 0
agentMissionDungeonCompleted = 1
agentMissionDungeonFailed = 2
rookieAgentList = [3018681,
 3018821,
 3018822,
 3018823,
 3018824,
 3018680,
 3018817,
 3018818,
 3018819,
 3018820,
 3018682,
 3018809,
 3018810,
 3018811,
 3018812,
 3018678,
 3018837,
 3018838,
 3018839,
 3018840,
 3018679,
 3018841,
 3018842,
 3018843,
 3018844,
 3018677,
 3018845,
 3018846,
 3018847,
 3018848,
 3018676,
 3018825,
 3018826,
 3018827,
 3018828,
 3018675,
 3018805,
 3018806,
 3018807,
 3018808,
 3018672,
 3018801,
 3018802,
 3018803,
 3018804,
 3018684,
 3018829,
 3018830,
 3018831,
 3018832,
 3018685,
 3018813,
 3018814,
 3018815,
 3018816,
 3018683,
 3018833,
 3018834,
 3018835,
 3018836]
epicArcNPEArcs = [64,
 67,
 68,
 69,
 70,
 71,
 72,
 73,
 74,
 75,
 76,
 77]
petitionPropertyAgentMissionReq = 2
petitionPropertyAgentMissionNoReq = 3
petitionPropertyAgents = 4
petitionPropertyShipID = 5
petitionPropertyStarbaseLocation = 6
petitionPropertyCharacter = 7
petitionPropertyUserCharacters = 8
petitionPropertyWebAddress = 9
petitionPropertyCorporations = 10
petitionPropertyChrAgent = 11
petitionPropertyOS = 12
petitionPropertyChrEpicArc = 13
tutorialPagesActionOpenCareerFunnel = 1
actionTypes = {1: 'Play_MLS_Audio',
 2: 'Neocom_Button_Blink',
 3: 'Open_MLS_Message',
 4: 'Poll_Criteria_Open_Tutorial',
 5: 'SpaceObject_UI_Pointer'}
neocomButtonScopeEverywhere = 1
neocomButtonScopeInflight = 2
neocomButtonScopeStation = 3
neocomButtonScopeStationOrWorldspace = 4
marketCategoryBluePrints = 2
marketCategoryShips = 4
marketCategoryShipEquipment = 9
marketCategoryAmmunitionAndCharges = 11
marketCategoryTradeGoods = 19
marketCategoryImplantesAndBoosters = 24
marketCategorySkills = 150
marketCategoryDrones = 157
marketCategoryManufactureAndResearch = 475
marketCategoryStarBaseStructures = 477
marketCategoryShipModifications = 955
maxCharFittings = 100
maxCorpFittings = 200
maxLengthFittingName = 50
maxLengthFittingDescription = 500
dungeonCompletionDestroyLCS = 0
dungeonCompletionDestroyGuards = 1
dungeonCompletionDestroyLCSandGuards = 2
turretModuleGroups = [groupEnergyWeapon,
 groupGasCloudHarvester,
 groupHybridWeapon,
 groupMiningLaser,
 groupProjectileWeapon,
 groupStripMiner,
 groupFrequencyMiningLaser,
 groupTractorBeam,
 groupSalvager,
 groupMissileLauncherAssault,
 groupMissileLauncherBomb,
 groupMissileLauncherCitadel,
 groupMissileLauncherCruise,
 groupMissileLauncherDefender,
 groupMissileLauncherHeavy,
 groupMissileLauncherHeavyAssault,
 groupMissileLauncherRocket,
 groupMissileLauncherSiege,
 groupMissileLauncherFestival,
 groupMissileLauncherStandard]
turretAmmoGroups = [groupCitadelTorpedo,
 groupCitadelCruise,
 groupBomb,
 groupBombECM,
 groupBombEnergy,
 groupTorpedo,
 groupAdvancedTorpedo,
 groupCruiseMissile,
 groupFOFCruiseMissile,
 groupAdvancedCruiseMissile,
 groupHeavyMissile,
 groupFOFHeavyMissile,
 groupAdvancedHeavyMissile,
 groupAssaultMissile,
 groupAdvancedAssaultMissile,
 groupLightMissile,
 groupFOFLightMissile,
 groupAdvancedLightMissile,
 groupRocket,
 groupAdvancedRocket,
 groupDefenderMissile,
 groupHeavyDefenderMissile,
 groupFestivalMissile]
previewCategories = [categoryDrone,
 categoryShip,
 categoryStructure,
 categoryStation,
 categorySovereigntyStructure,
 categoryApparel]
previewGroups = [groupStargate,
 groupFreightContainer,
 groupSecureCargoContainer,
 groupCargoContainer,
 groupAuditLogSecureContainer]
previewGroups += turretModuleGroups
previewGroups += turretAmmoGroups
reverseRedeemingLegalGroups = [groupGameTime]
defaultPadding = 4
infoEventTutorialPageCompletion = 1
infoEventOreMined = 2
infoEventSalvagingAttempts = 3
infoEventHackingAttempts = 4
infoEventArcheologyAttempts = 5
infoEventScanningAttempts = 6
infoEventFleet = 7
infoEventFleetCreated = 8
infoEventFleetBroadcast = 9
infoEventNPCKilled = 12
infoEventRefinedTypesAmount = 13
infoEventRefiningYieldTypesAmount = 14
infoEventPlanetResourceDepletion = 15
infoEventPlanetResourceScanning = 16
infoEventPlanetUserAccess = 17
infoEventPlanetInstallProgramQuery = 18
infoEventPlanetUpdateNetwork = 19
infoEventPlanetAbandonPlanet = 20
infoEventPlanetEstablishColony = 21
infoEventEntityKillWithoutBounty = 22
infoEventRecruitmentAdSearch = 23
infoEventNexCloseNex = 24
infoEventViewStateUsage = 25
infoEventDoubleclickToMove = 26
infoEventCCDuration = 27
infoEvenTrackingCameraEnabled = 28
sovereigntyClaimStructuresGroups = (groupSovereigntyClaimMarkers, groupSovereigntyDisruptionStructures)
sovereigntyStructuresGroups = (groupSovereigntyClaimMarkers,
 groupSovereigntyDisruptionStructures,
 groupSovereigntyStructures,
 groupInfrastructureHub)
mailingListBlocked = 0
mailingListAllowed = 1
mailingListMemberMuted = 0
mailingListMemberDefault = 1
mailingListMemberOperator = 2
mailingListMemberOwner = 3
ALLIANCE_SERVICE_MOD = 200
CHARNODE_MOD = 64
PLANETARYMGR_MOD = 128
BATTLEINSTANCEMANANGER_MOD = 128
BATTLEQUICKMATCHER_MOD = 64
mailTypeMail = 1
mailTypeNotifications = 2
mailStatusMaskRead = 1
mailStatusMaskReplied = 2
mailStatusMaskForwarded = 4
mailStatusMaskTrashed = 8
mailStatusMaskDraft = 16
mailStatusMaskAutomated = 32
mailLabelInbox = 1
mailLabelSent = 2
mailLabelCorporation = 4
mailLabelAlliance = 8
mailLabelsSystem = mailLabelInbox + mailLabelSent + mailLabelCorporation + mailLabelAlliance
mailMaxRecipients = 50
mailMaxGroups = 1
mailMaxSubjectSize = 150
mailMaxBodySize = 8000
mailMaxTaggedBodySize = 10000
mailMaxLabelSize = 40
mailMaxNumLabels = 25
mailMaxPerPage = 100
mailTrialAccountTimer = 1
mailMaxMessagePerMinute = 5
mailinglistMaxMembers = 3000
mailinglistMaxMembersUpdated = 1000
mailingListMaxNameSize = 60
notificationsMaxUpdated = 100
calendarMonday = 0
calendarTuesday = 1
calendarWednesday = 2
calendarThursday = 3
calendarFriday = 4
calendarSaturday = 5
calendarSunday = 6
calendarJanuary = 1
calendarFebruary = 2
calendarMarch = 3
calendarApril = 4
calendarMay = 5
calendarJune = 6
calendarJuly = 7
calendarAugust = 8
calendarSeptember = 9
calendarOctober = 10
calendarNovember = 11
calendarDecember = 12
calendarNumDaysInWeek = 7
calendarTagPersonal = 1
calendarTagCorp = 2
calendarTagAlliance = 4
calendarTagCCP = 8
calendarTagAutomated = 16
calendarViewRangeInMonths = 12
calendarMaxTitleSize = 40
calendarMaxDescrSize = 500
calendarMaxInvitees = 50
calendarMaxInviteeDisplayed = 100
calendarAutoEventPosFuel = 1
eventResponseUninvited = 0
eventResponseDeleted = 1
eventResponseDeclined = 2
eventResponseUndecided = 3
eventResponseAccepted = 4
eventResponseMaybe = 5
calendarStartYear = 2003
defaultShieldThreshold = 0.25
defaultArmourThreshold = 0.4
defaultHullThreshold = 0.95
defaultCapacitorThreshold = 0.3
damageSoundNotifications = ['ui_notify_negative_05_play',
 'ui_notify_negative_03_play',
 'ui_notify_negative_01_play',
 'ui_notify_negative_04_play']
soundNotificationVars = [['shieldNotificationEnabled', 'shieldThreshold', defaultShieldThreshold],
 ['armourNotificationEnabled', 'armourThreshold', defaultArmourThreshold],
 ['hullNotificationEnabled', 'hullThreshold', defaultHullThreshold],
 ['capacitorNotificationEnabled', 'capacitorThreshold', defaultCapacitorThreshold]]
costReceiverTypeOwner = 0
costReceiverTypeMailingList = 1
costContactMax = 1000000
contactHighStanding = 10
contactGoodStanding = 5
contactNeutralStanding = 0
contactBadStanding = -5
contactHorribleStanding = -10
contactAll = 100
contactBlocked = 200
contactWatchlist = 300
contactNotifications = 400
developmentIndices = [attributeDevIndexMilitary,
 attributeDevIndexIndustrial,
 attributeDevIndexSovereignty,
 attributeDevIndexUpgrade]
sovAudioEventStopOnline = 0
sovAudioEventStopDestroyed = 1
sovAudioEventFlagVulnerable = 2
sovAudioEventFlagDestroyed = 3
sovAudioEventFlagClaimed = 4
sovAudioEventOutpostReinforced = 5
sovAudioEventOutpostCaptured = 6
sovAudioEventHubReinforced = 7
sovAudioEventHubDestroyed = 8
sovAudioEventOutpostAttacked = 9
sovAudioEventFiles = {sovAudioEventStopOnline: ('msg_stop_online_play', 'SovAudioMsg_StopOnline'),
 sovAudioEventStopDestroyed: ('msg_stop_destroyed_play', 'SovAudioMsg_StopDestroyed'),
 sovAudioEventFlagVulnerable: ('msg_flag_vulnerable_play', 'SovAudioMsg_FlagVulnerable'),
 sovAudioEventFlagDestroyed: ('msg_flag_destroyed_play', 'SovAudioMsg_FlagDestroyed'),
 sovAudioEventFlagClaimed: ('msg_flag_claimed_play', 'SovAudioMsg_FlagClaimed'),
 sovAudioEventOutpostReinforced: ('msg_outpost_reinforced_play', 'SovAudioMsg_OutpostReinforced'),
 sovAudioEventOutpostCaptured: ('msg_outpost_captureed_play', 'SovAudioMsg_OutpostCaptured'),
 sovAudioEventOutpostAttacked: ('msg_outpost_attacked_play', 'SovAudioMsg_OutpostUnderAttack'),
 sovAudioEventHubReinforced: ('msg_hub_reinforced_play', 'SovAudioMsg_HubReinforced'),
 sovAudioEventHubDestroyed: ('msg_hub_destroyed_play', 'SovAudioMsg_HubDestroyed')}
maxLong = 9223372036854775807L
maxContacts = 1024
maxAllianceContacts = 2600
maxContactsPerPage = 50
contactMaxLabelSize = 40
pwnStructureStateAnchored = 'anchored'
pwnStructureStateAnchoring = 'anchoring'
pwnStructureStateOnline = 'online'
pwnStructureStateOnlining = 'onlining'
pwnStructureStateUnanchored = 'unanchored'
pwnStructureStateUnanchoring = 'unanchoring'
pwnStructureStateVulnerable = 'vulnerable'
pwnStructureStateInvulnerable = 'invulnerable'
pwnStructureStateReinforced = 'reinforced'
pwnStructureStateOperating = 'operating'
pwnStructureStateIncapacitated = 'incapacitated'
pwnStructureStateAnchor = 'anchor'
pwnStructureStateUnanchor = 'unanchor'
pwnStructureStateOffline = 'offline'
pwnStructureStateOnlineActive = 'online - active'
pwnStructureStateOnlineStartingUp = 'online - starting up'
piLaunchOrbitDecayTime = DAY * 5
piCargoInOrbit = 0
piCargoDeployed = 1
piCargoClaimed = 2
piCargoDeleted = 3
piSECURITY_BANDS_LABELS = [(0, '[-1;-0.75]'),
 (1, ']-0.75;-0.45]'),
 (2, ']-0.45;-0.25]'),
 (3, ']-0.25;0.0['),
 (4, '[0.0;0.15['),
 (5, '[0.15;0.25['),
 (6, '[0.25;0.35['),
 (7, '[0.35;0.45['),
 (8, '[0.45;0.55['),
 (9, '[0.55;0.65['),
 (10, '[0.65;0.75['),
 (11, '[0.75;1.0]')]
singleCharsAllowedForShortcut = ['OEM_1',
 'OEM_102',
 'OEM_2',
 'OEM_3',
 'OEM_4',
 'OEM_5',
 'OEM_6',
 'OEM_7',
 'OEM_8',
 'OEM_CLEAR',
 'OEM_COMMA',
 'OEM_MINUS',
 'OEM_PERIOD',
 'OEM_PLUS',
 'F1',
 'F10',
 'F11',
 'F12',
 'F13',
 'F14',
 'F15',
 'F16',
 'F17',
 'F18',
 'F19',
 'F2',
 'F20',
 'F21',
 'F22',
 'F23',
 'F24',
 'F3',
 'F4',
 'F5',
 'F6',
 'F7',
 'F8',
 'F9']
repackableCategorys = (categoryStructure,
 categoryShip,
 categoryDrone,
 categoryModule,
 categorySubSystem,
 categorySovereigntyStructure)
repackableGroups = (groupCargoContainer,
 groupSecureCargoContainer,
 groupAuditLogSecureContainer,
 groupFreightContainer,
 groupTool,
 groupMobileWarpDisruptor)
vcPrefixAlliance = 'allianceid'
vcPrefixFleet = 'fleetid'
vcPrefixCorp = 'corpid'
vcPrefixSquad = 'squadid'
vcPrefixWing = 'wingid'
vcPrefixInst = 'inst'
systemInfluenceAny = 0
systemInfluenceDecline = 1
systemInfluenceRising = 2
incursionStateWithdrawing = 0
incursionStateMobilizing = 1
incursionStateEstablished = 2
rewardIneligibleReasonTrialAccount = 1
rewardIneligibleReasonInvalidGroup = 2
rewardIneligibleReasonShipCloaked = 3
rewardIneligibleReasonNotInFleet = 4
rewardIneligibleReasonNotBestFleet = 5
rewardIneligibleReasonNotTop5 = 6
rewardIneligibleReasonNotRightAmoutOfPlayers = 7
rewardIneligibleReasonTaleAlreadyEnded = 8
rewardIneligibleReasonNotInRange = 9
rewardIneligibleReasonNoISKLost = 10
rewardTypeLP = 1
rewardTypeISK = 2
rewardCriteriaAllSecurityBands = 0
rewardCriteriaHighSecurity = 1
rewardCriteriaLowSecurity = 2
rewardCriteriaNullSecurity = 3
rewardInvalidGroups = {groupCapsule,
 groupShuttle,
 groupRookieship,
 groupPrototypeExplorationShip}
rewardInvalidGroupsLimitedRestrictions = {groupCapsule, groupShuttle, groupPrototypeExplorationShip}
creditsISK = 0
creditsAURUM = 1
creditsDustMPLEX = 2
Plex2AurExchangeRatio = 3500
chinaPlex2AurExchangeRatio = 600
AurumToken2AurExchangeRatio = 1000
blacklistedTaleLocations = 1
defaultCustomsOfficeTaxRate = 0.05
configValues = {'MaxPush': 2.5,
 'VisibilityRangeAdd': 60.0,
 'VisibilityRangeRemove': 65.0}
dbMaxCountForIntList = 750
dbMaxCountForBigintList = 350
dbMaxQuantity = 2147483647
singletonBlueprintOriginal = 1
singletonBlueprintCopy = 2
metaGroupUnused = 0
metaGroupStoryline = 3
metaGroupFaction = 4
metaGroupOfficer = 5
metaGroupDeadspace = 6
metaGroupsUsed = [metaGroupStoryline,
 metaGroupFaction,
 metaGroupOfficer,
 metaGroupDeadspace]
NCC_MAX_NORMAL_BACKGROUND_ID = 1000
GENDER_AS_ROOT_FOLDER = True
if GENDER_AS_ROOT_FOLDER:
    DEFAULT_FEMALE_PAPERDOLL_MODEL = 'res:/Graphics/Character/Female/Skeleton/masterSkeletonFemale.gr2'
    DEFAULT_MALE_PAPERDOLL_MODEL = 'res:/Graphics/Character/Male/Skeleton/masterSkeletonMale.gr2'
else:
    DEFAULT_FEMALE_PAPERDOLL_MODEL = 'res:/Graphics/Character/Skeletons/masterSkeletonFemale.gr2'
    DEFAULT_MALE_PAPERDOLL_MODEL = 'res:/Graphics/Character/Skeletons/masterSkeletonMale.gr2'
PAPERDOLL_LODS_IN_SEPARATE_FOLDER = True
PAPERDOLL_LOD_RED_FILES = True
FEMALE_MORPHEME_PATH = 'res:/morpheme/IncarnaPlayerNetwork/Female/IncarnaPlayerNetwork.mor'
MALE_MORPHEME_PATH = 'res:/morpheme/IncarnaPlayerNetwork/Male/IncarnaPlayerNetwork.mor'
MORPHEMEPATH = FEMALE_MORPHEME_PATH
AVATAR_MOVEMENT_SPEED_MAX = 1.9
AVATAR_STEP_HEIGHT = 0.2
BASE_INVENTORY_TYPES_TABLE = 'inventory.types'
CYNOJAM_JAMSHIPS = 1
CYNOJAM_JAMSHIPS_AND_JUMPBRIDGE = 2
INPUT_TYPE_LEFTCLICK = 1
INPUT_TYPE_RIGHTCLICK = 2
INPUT_TYPE_MIDDLECLICK = 3
INPUT_TYPE_EX1CLICK = 4
INPUT_TYPE_EX2CLICK = 5
INPUT_TYPE_DOUBLECLICK = 6
INPUT_TYPE_MOUSEMOVE = 7
INPUT_TYPE_MOUSEWHEEL = 8
INPUT_TYPE_MOUSEDOWN = 9
INPUT_TYPE_MOUSEUP = 10
MOVDIR_FORWARD = 0
MOVDIR_BACKWARD = 1
MOVDIR_LEFT = 2
MOVDIR_RIGHT = 3
INCARNA_CAMERA_FULL_CHASE = 10
INCARNA_CAMERA_CHASE_WHEN_MOVING = 11
INCARNA_CAMERA_NO_CHASE = 12
INCARNA_FLAT = 0
INCARNA_SLOPE_DOWN = 1
INCARNA_SLOPE_UP = 2
INCARNA_STEPS_DOWN = 3
INCARNA_STEPS_UP = 4
BAD_ASSET_PATH = 'res:/Graphics/Placeable/EditorOnly/BadAsset/'
BAD_ASSET_FILE = 'BadAsset.red'
BAD_ASSET_PATH_AND_FILE = BAD_ASSET_PATH + BAD_ASSET_FILE
BAD_ASSET_STATIC = 'res:/Tools/BadAsset/BadInteriorAsset.red'
BAD_ASSET_COLLISION = 'res:/Graphics/Placeable/EditorOnly/BadAsset/BadAsset.nxb'
from constants import cef
dgmUnnerfedCategories = [categorySkill,
 categoryImplant,
 categoryShip,
 categoryCharge,
 categorySubSystem]
dgmPreStackingNerfOperators = {dgmAssPreAssignment: lambda ret, value: value,
 dgmAssPreMul: lambda ret, value: ret * value,
 dgmAssPreDiv: lambda ret, value: ret / value,
 dgmAssModAdd: lambda ret, value: ret + value,
 dgmAssModSub: lambda ret, value: ret - value}
dgmOperators = {dgmAssPreAssignment: lambda ret, value: value,
 dgmAssPostAssignment: lambda ret, value: value,
 dgmAssPreMul: lambda ret, value: ret * value,
 dgmAssPostMul: lambda ret, value: ret * value,
 dgmAssPreDiv: lambda ret, value: ret / value,
 dgmAssPostDiv: lambda ret, value: ret / value,
 dgmAssModAdd: lambda ret, value: ret + value,
 dgmAssModSub: lambda ret, value: ret - value,
 dgmAssPostPercent: lambda ret, value: ret * (100 + value) / 100}
completionTypeRookieArcCompletion = 1
ZACTION_DEFAULT_ACTION = 12
dgmAttributesByIdx = {1: attributeIsOnline,
 2: attributeDamage,
 3: attributeCharge,
 4: attributeSkillPoints,
 5: attributeArmorDamage,
 6: attributeShieldCharge,
 7: attributeIsIncapacitated}
dgmGroupableGroupIDs = set([groupEnergyWeapon,
 groupProjectileWeapon,
 groupHybridWeapon,
 groupMissileLauncher,
 groupMissileLauncherAssault,
 groupMissileLauncherCitadel,
 groupMissileLauncherCruise,
 groupMissileLauncherDefender,
 groupMissileLauncherHeavy,
 groupMissileLauncherHeavyAssault,
 groupMissileLauncherRocket,
 groupMissileLauncherSiege,
 groupMissileLauncherStandard])
ZACTION_DEFAULT_ACTION = 12
UE_OWNERID = 2
UE_LOCID = 3
UE_TYPEID = 4
UE_TYPEID2 = 5
UE_TYPEIDL = 29
UE_BPTYPEID = 6
UE_GROUPID = 7
UE_GROUPID2 = 8
UE_CATID = 9
UE_CATID2 = 10
UE_DGMATTR = 11
UE_DGMFX = 12
UE_DGMTYPEFX = 13
UE_AMT = 18
UE_AMT2 = 19
UE_AMT3 = 20
UE_DIST = 21
UE_TYPEIDANDQUANTITY = 24
UE_OWNERIDNICK = 25
UE_ISK = 28
UE_AUR = 30
CHAT_SYSTEM_CHANNEL = -1
WAR_NEGOTIATION_TYPE_ALLY_OFFER = 0
WAR_NEGOTIATION_TYPE_SURRENDER_OFFER = 2
warNegotiationNew = 0
warNegotiationAccepted = 1
warNegotiationDeclined = 2
GROUP_CAPSULES = 0
GROUP_FRIGATES = 1
GROUP_DESTROYERS = 2
GROUP_CRUISERS = 3
GROUP_BATTLESHIPS = 4
GROUP_BATTLECRUISERS = 5
GROUP_CAPITALSHIPS = 6
GROUP_INDUSTRIALS = 7
GROUP_POS = 8
OVERVIEW_NORMAL_COLOR = (1.0, 1.0, 1.0)
OVERVIEW_HOSTILE_COLOR = (1.0, 0.1, 0.1)
OVERVIEW_AUTO_PILOT_DESTINATION_COLOR = (1.0, 1.0, 0.0)
OVERVIEW_FORBIDDEN_CONTAINER_COLOR = (1.0, 1.0, 0.0)
OVERVIEW_ABANDONED_CONTAINER_COLOR = (0.2, 0.5, 1.0)
MAX_FOLDERNAME_LENGTH = 40
maxCorpBookmarkCount = 250
maxCharBookmarkCount = 13000
BOOKMARKACTIONTHROTTLEKEY = 'BookmarkActionThrottleKey'
bookmarkThrottleMaxTimes = 20
bookmarkThrottleDuration = MIN
EXPLORATION_SITE_TYPES = {attributeScanGravimetricStrength: 'UI/Inflight/Scanner/Gravimetric',
 attributeScanLadarStrength: 'UI/Inflight/Scanner/Ladar',
 attributeScanMagnetometricStrength: 'UI/Inflight/Scanner/Magnetometric',
 attributeScanRadarStrength: 'UI/Inflight/Scanner/Radar',
 attributeScanAllStrength: 'UI/Common/Unknown'}
MAX_DRONE_RECONNECTS = 25
PLAYER_STATUS_ACTIVE = 0
PLAYER_STATUS_AFK = 1
searchByPartialTerms = 0
searchByExactTerms = 1
searchByExactPhrase = 2
searchByOnlyExactPhrase = 3
searchResultAgent = 1
searchResultCharacter = 2
searchResultCorporation = 3
searchResultAlliance = 4
searchResultFaction = 5
searchResultConstellation = 6
searchResultSolarSystem = 7
searchResultRegion = 8
searchResultStation = 9
searchResultInventoryType = 10
searchResultAllOwners = [1,
 2,
 3,
 4,
 5]
searchResultAllLocations = [6,
 7,
 8,
 9]
searchMaxResults = 500
searchMinWildcardLength = 3
tianCityBannerUrl = 'http://eve.tiancity.com/homepage/endbanner/endbanner.html'
DEFAULT_SIGNATURE_RADIUS = 1000.0
warningISKBuying = 244
CHT_MAX_STRIPPED_INPUT = 253
CHT_MAX_INPUT = CHT_MAX_STRIPPED_INPUT * 2
mapHistoryStatJumps = 1
mapHistoryStatKills = 3
mapHistoryStatFacWarKills = 5
corpInvFlagByDivision = {0: flagHangar,
 1: flagCorpSAG2,
 2: flagCorpSAG3,
 3: flagCorpSAG4,
 4: flagCorpSAG5,
 5: flagCorpSAG6,
 6: flagCorpSAG7}
corpDivisionByInvFlag = {flagHangar: 0,
 flagCorpSAG2: 1,
 flagCorpSAG3: 2,
 flagCorpSAG4: 3,
 flagCorpSAG5: 4,
 flagCorpSAG6: 5,
 flagCorpSAG7: 6}
zmetricCounter_EVEOnline = 10
zmetricCounter_EVETrial = 11
zmetricCounter_EVECREST = 12
counterBattleMembers = 10010
counterBattleMembersRegionUS = 10007
counterBattleMembersRegionEU = 10008
counterBattleMembersRegionAS = 10009
counterBattleMembersRegionOC = 10011
counterBattles = 10020
counterBattlesRegionUS = 10021
counterBattlesRegionEU = 10022
counterBattlesRegionAS = 10023
counterBattlesRegionOC = 10024
counterMatchmaking = 10025
counterMatchmakingRegionUS = 10026
counterMatchmakingRegionEU = 10027
counterMatchmakingRegionAS = 10028
counterMatchmakingRegionOC = 10029
zmetricCounter_DUSTOnline = 10040
zmetricCounter_DUSTUser = 10041
zmetricCounter_DUSTBattle = 10042
battleRegionUS = 'us'
battleRegionEU = 'eu'
battleRegionAS = 'as'
battleRegionOC = 'oc'
battleRegionCounters = {battleRegionUS: (counterBattlesRegionUS, counterBattleMembersRegionUS),
 battleRegionEU: (counterBattlesRegionEU, counterBattleMembersRegionEU),
 battleRegionAS: (counterBattlesRegionAS, counterBattleMembersRegionAS),
 battleRegionOC: (counterBattlesRegionOC, counterBattleMembersRegionOC)}
militiaCorporationMinmatar = 1000182
militiaCorporationAmarr = 1000179
militiaCorporationCaldari = 1000180
militiaCorporationGallente = 1000181
militiaFactionsByCorporation = {militiaCorporationMinmatar: factionMinmatarRepublic,
 militiaCorporationAmarr: factionAmarrEmpire,
 militiaCorporationCaldari: factionCaldariState,
 militiaCorporationGallente: factionGallenteFederation}
militiaCorporationsByFaction = {v:k for k, v in militiaFactionsByCorporation.items()}
militiaCorporations = militiaCorporationsByFaction.values()
militiaFactions = militiaFactionsByCorporation.values()
militiaOpponents = {militiaCorporationMinmatar: militiaCorporationAmarr,
 militiaCorporationAmarr: militiaCorporationMinmatar,
 militiaCorporationCaldari: militiaCorporationGallente,
 militiaCorporationGallente: militiaCorporationCaldari}
miltiaAllies = {militiaCorporationMinmatar: militiaCorporationGallente,
 militiaCorporationAmarr: militiaCorporationCaldari,
 militiaCorporationCaldari: militiaCorporationAmarr,
 militiaCorporationGallente: militiaCorporationMinmatar}
orbitalStrikeAmmo = {typeTacticalEMPAmmoS: 356506,
 typeTacticalHybridAmmoS: 356508,
 typeTacticalLaserAmmoS: 356507}
weaponsTimerStateIdle = 100
weaponsTimerStateActive = 101
weaponsTimerStateTimer = 102
weaponsTimerStateInherited = 103
pvpTimerStateIdle = 200
pvpTimerStateActive = 201
pvpTimerStateTimer = 202
pvpTimerStateInherited = 203
criminalTimerStateIdle = 300
criminalTimerStateActiveCriminal = 301
criminalTimerStateActiveSuspect = 302
criminalTimerStateTimerCriminal = 303
criminalTimerStateTimerSuspect = 304
criminalTimerStateInheritedCriminal = 305
criminalTimerStateInheritedSuspect = 306
npcTimerStateIdle = 400
npcTimerStateActive = 401
npcTimerStateTimer = 402
npcTimerStateInherited = 403
weaponsTimerTimeout = 60 * SEC
pvpTimerTimeout = 15 * MIN
criminalTimerTimeout = 15 * MIN
npcTimerTimeout = 5 * MIN
crimewatchEngagementTimeoutOngoing = -1
crimewatchEngagementDuration = 5 * MIN
shipSafetyLevelNone = 0
shipSafetyLevelPartial = 1
shipSafetyLevelFull = 2
illegalTargetNpcOwnedGroups = {groupStation, groupStargate}
crimewatchOutcomeNone = 0
crimewatchOutcomeSuspect = 1
crimewatchOutcomeCriminal = 2
crimewatchOutcomeEngagement = 3
duelOfferExpiryTimeout = 30 * SEC
autoRejectDuelSettingsKey = 'autoRejectDuelInvitations'
MIN_BOUNTY_AMOUNT_CHAR = 100000
MIN_BOUNTY_AMOUNT_CORP = 20000000
MIN_BOUNTY_AMOUNT_ALLIANCE = 100000000
MAX_BOUNTY_AMOUNT = 100000000000L
containerGroupIDs = {groupWreck,
 groupCargoContainer,
 groupSpawnContainer,
 groupSecureCargoContainer,
 groupAuditLogSecureContainer,
 groupFreightContainer,
 groupDeadspaceOverseersBelongings,
 groupMissionContainer}
WARS_PER_PAGE = 50
canFitShipGroups = [1298,
 1299,
 1300,
 1301,
 1872,
 1879,
 1880,
 1881]
canFitShipTypes = [1302,
 1303,
 1304,
 1305]