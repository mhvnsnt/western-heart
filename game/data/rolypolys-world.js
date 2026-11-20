// Roly-Polys World Tour — world data for the Western Heart Banabana hub.
//
// SOURCE (pulled whole, verbatim): the Phase 1 disc read of Roly-Polys World Tour
// (Banabana MK.1: Rolypolys no Sekai Daiboken, 1997, disc ROLY_2, created
// 1997-08-26) — sato/rolypolys/WORLD-TOUR.md in mhvnsnt/game-reverse-engineering,
// release sato-rolypolys-20261120. Area / region / scene names below are the disc's
// own directory and .DXR movie names, transcribed exactly (8.3 upper-case).
// Nothing here is invented: where the disc does not say, the entry says so.
//
// WH ADAPTATION (ours, per owner order 2026-11-20: WH canon + WH characters,
// never clones): the Banabana MK.1 carries the Nine Souls; RIN is the lead
// (the disc's Pon); TOU hosts the shooting gallery (the disc's Cho);
// KAI hosts the cooking game (the disc's Mr. Okhotsk / Pon's Cooking School);
// the Trader hosts the slot (the disc's Las Vegas Akiko).
//
// ITEM SYSTEM: the disc holds one ITEM*.CXT cast set per region. The WH slice
// grants one collectible per scene visited, named for the scene (e.g. visiting
// PYRAMID collects the PYRAMID item). Item NAMES beyond the scene names are
// not on the disc catalog and are not invented here.
//
// ENDINGS: the disc holds per-continent END movies for Africa (AFEND), America
// (USAEND), Asia (ASIAEND) and South America (SAEND). Europa, Japan and Oceania
// have no per-continent END movie on disc — their arcs close on the finale
// movie MNMENU/END.DXR (18.8 MB). That is recorded, not papered over.
//
// GOD-WITHIN ANCHORS: the disc's own mythic sites (SHRINE, PRAYER, GODDESS,
// TENG, PYRAMID, NASKA, BIGHEAD, DEVIL, STPAUL, TAJI). Each maps to a proposed
// WH god-within stage — proposals, not shipped stages.

export const ROLYPOLYS_SHIP = {
  name: 'Banabana MK.1',
  disc: 'SHIPCST.CXT / SHIPCSTM.CXT + EUROPA/SHIP.DXR',
  home: 'JAPAN/PON',
  note: 'The Roly-Polys sail the world in the Banabana MK.1. In WH it carries the Nine Souls. Home leg: JAPAN/PON (RIN\'s house — the disc opens there, JAPAN/PON/OPEN.DXR, 25.3 MB).',
};

export const ROLYPOLYS_AREAS = [
  {
    id: 'AFRICA', name: 'Africa',
    regions: [
      { id: 'FIRE', scenes: ['FIRE', 'MARCKET', 'SEASHORE', 'WATABE'] },
      { id: 'GRAND', scenes: ['DRUM', 'GRAND', 'MINING', 'OSTRICH', 'PRAYER'] },
      { id: 'LIFE', scenes: ['ISLAND', 'JETTY', 'LIFE', 'SAVANA', 'SAVANAIN', 'VILLAGE'] },
      { id: 'RUINS', scenes: ['AFEND', 'GATE', 'GRAVE', 'PYRAMID', 'RUINS', 'SHRINE', 'STAIRS'] },
      { id: 'SUN', scenes: ['OASIS', 'OIL', 'SUN'] },
      { id: 'WATER', scenes: ['LAKE', 'PIGMY', 'RIVER', 'RIVERON', 'WATER'] },
    ],
  },
  {
    id: 'AMERICA', name: 'America',
    regions: [
      { id: 'CANADA', scenes: ['BOAT', 'BRONZE', 'CANADA', 'CAR', 'FALLS', 'FIREFLY', 'HILLSTA', 'HOODOO', 'LAKEFIRE', 'LAKEMAP', 'MOUNT', 'SKIHOUS', 'SKYRIDE', 'SKYTRAIN', 'VIEWH', 'VILLAGE'] },
      { id: 'COWBOY', scenes: ['BAITO', 'CASINO', 'CLAYHOUS', 'COWBOY', 'GAMECOW', 'GRAND', 'HOTEL', 'LASVE', 'OILFIELD', 'ROCKET', 'SHOW', 'WESTERN'] },
      { id: 'LAKE', scenes: ['BUTOWN', 'CARDUNG', 'CITYCHI', 'CITYDET', 'EASY', 'FALLDET', 'LAKE', 'LAKECABN', 'PORTCHI', 'PORTDET', 'VIEWCHI'] },
      { id: 'LOS', scenes: ['BVRLHIL', 'CARUP', 'CRUISE', 'DEVIL', 'HITECH', 'HOLYWOOD', 'KCAR', 'LOS', 'LOSMAP', 'SANFRAMP', 'SANTMONI', 'WATERMIL', 'WINDMIL'] },
      { id: 'MEXICO', scenes: ['BIGHEAD', 'BRONZEM', 'CITYMEX', 'CONTEST', 'DANCEROK', 'MAGEI', 'MARIACH', 'MARKET', 'MEXICO', 'PYRAMSTP', 'PYRAMSUN', 'SEASIDE'] },
      { id: 'MIAMI', scenes: ['BEACHMI', 'HOTELMI', 'ISLANDMI', 'MIAMI', 'OLDMAN', 'PORTMI', 'SWAMP', 'VOODOO'] },
      { id: 'NY', scenes: ['BOSTON', 'CAB', 'ELV', 'GODDESS', 'HALL', 'NY', 'NYCITY', 'PARK', 'SHIP', 'TOWER', 'WHITEHUS'] },
      { id: 'SOUTH', scenes: ['BOURBON', 'HOUSEM', 'OILDUNG', 'SHIPN', 'SOUTH', 'TRAINLST', 'TRAINN'] },
    ],
  },
  {
    id: 'ASIA', name: 'Asia',
    regions: [
      { id: 'CHINA', scenes: ['ANIMAL', 'CASTLE', 'CHINA', 'PARK', 'PEACE'] },
      { id: 'INDIA', scenes: ['BARA', 'BRIDGE', 'CINE', 'GATE', 'HOTEL', 'INDCITY', 'INDIA', 'PALACE', 'PARK', 'SHOP', 'SNAKE', 'STONE', 'TAJI'] },
      { id: 'MIDEAST', scenes: ['DEADSEA', 'KUWAIT', 'MIDEAST', 'SISIKABA', 'VILLAGE'] },
      { id: 'SOUTHEST', scenes: ['BANBI', 'ENCORE', 'FIGHT', 'FIGHTING', 'MARKET', 'RIVER', 'SOUTHEST'] },
    ],
  },
  {
    id: 'EUROPA', name: 'Europa',
    regions: [
      { id: 'ENGLAND', scenes: ['AVARON', 'BACKIN', 'BACKNBEN', 'BAKELIVE', 'BAKERY', 'BASEMENT', 'BIGBEN', 'CLUB', 'ENGLAND', 'KING', 'LAKE', 'LONDON', 'ROLYS', 'SQUAIR', 'STPAUL', 'TOWER', 'TOWERMAP', 'TRAGCLUB', 'UNIV', 'UNIVCITY'] },
      { id: 'FRANCE', scenes: ['BOAT', 'CASINO', 'COAT', 'EIFFEL', 'FRANCE', 'HUT', 'JIIN'] },
      { id: 'GERMANY', scenes: ['BAR', 'BERLIN', 'CASTLE', 'CHURCH', 'GATE', 'GERMANY', 'HAUS', 'MARCHEN', 'PARK', 'TOWN', 'WINDMILL'] },
      { id: 'ITALY', scenes: ['BLUE', 'BLUEGAME', 'ITALY', 'OUTSIDE', 'PANTH', 'PARK', 'PARKIN', 'PISA', 'TOWN', 'WATER'] },
      { id: 'RUSSIA', scenes: ['MARKET', 'PARK', 'RED', 'REDIN', 'RUSSIA', 'VILLAGE', 'VLGIN'] },
      { id: 'SPANISH', scenes: ['COLON', 'COLONMAP', 'GATE', 'GATEMAP', 'OX', 'OXGAME', 'SAGRA', 'SPANISH', 'TABURAO'] },
    ],
  },
  {
    id: 'JAPAN', name: 'Japan (home leg)',
    regions: [
      { id: 'AKIBA', scenes: ['AKIBA', 'BALLOON', 'RADAR', 'ROJI', 'ROOF', 'SOUKO'] },
      { id: 'HIMEJI', scenes: ['HIMEGAME', 'HIMEJI', 'HIMEJIN', 'HIMEJTOP'] },
      { id: 'KYOTO', scenes: ['KYOTO', 'KYOTOIN'] },
      { id: 'PON', scenes: ['DELMONT', 'GEORGE', 'OPEN', 'PON', 'PONHOUS', 'PONROOM'] },
      { id: 'PONGI', scenes: ['PONGI'] },
      { id: 'SAPPORO', scenes: ['KANISHOP', 'MEIRO', 'SAPPORO'] },
      { id: 'TENG', scenes: ['TENGENT', 'TENGIN1', 'TENGIN2', 'TENGIN3'] },
    ],
  },
  {
    id: 'OCEANIA', name: 'Oceania',
    regions: [
      { id: 'CITY', scenes: ['BRIDGE', 'CHARCH', 'CITY', 'FOREST', 'FRSTMAP', 'KANGHUSE', 'KOASHOW', 'OPERA', 'ROOM01', 'ROOM02', 'ROOM03'] },
      { id: 'DESERT', scenes: ['ALLIGAT', 'BUSH', 'DESERT', 'DESM', 'WAVEROCK'] },
      { id: 'NABEL', scenes: ['AIRSROCK', 'BREESE', 'CLIMB', 'FINAL', 'MAZE', 'NABEL', 'OPEARL', 'OPGET', 'RESCUE', 'WALL'] },
      { id: 'SANGO', scenes: ['SANGO', 'SEAHOUS1', 'SEAHOUS2', 'SEAIN', 'SEASIDE', 'SEATURTL'] },
      { id: 'SHEEP', scenes: ['FARMSHP', 'FRMSPEND', 'HUTFARM', 'HUTSHEEP', 'KIWIBOAT', 'KIWIFARM', 'SHEEP', 'SHPGAME', 'SOUTHLND'] },
    ],
  },
  {
    id: 'SOUTHAME', name: 'South America',
    regions: [
      { id: 'AMAZONE', scenes: ['AMAZONE', 'FOREST'] },
      { id: 'NASKA', scenes: ['NASKA', 'NASKAITM'] },
      { id: 'RIO', scenes: ['RIO', 'RIOEND'] },
      { id: 'SAEND', scenes: ['SAEND'] },
    ],
  },
];

// Link back to the first game (disc: NANK + NANKMAP dirs). Not one of the 7 areas.
export const ROLYPOLYS_LINKS = [
  { id: 'NANKMAP', scenes: ['BASE', 'NANKMAP', 'PENGUIN', 'WHALE', 'WHALGAME'], note: 'Map back to Nanakorobi Yaoki (the alphabet game).' },
];

// Per-continent endings. kind 'continent' = an END movie on the disc;
// kind 'finale' = no per-continent END on disc; the arc closes on MNMENU/END.DXR.
export const ROLYPOLYS_ENDINGS = {
  AFRICA: { movie: 'AFEND', kind: 'continent', note: 'AFRICA/RUINS/AFEND.DXR' },
  AMERICA: { movie: 'USAEND', kind: 'continent', note: 'Per-continent END movie on disc.' },
  ASIA: { movie: 'ASIAEND', kind: 'continent', note: 'Per-continent END movie on disc.' },
  EUROPA: { movie: 'END.DXR', kind: 'finale', note: 'No per-continent END movie on disc; closes on the finale.' },
  JAPAN: { movie: 'END.DXR', kind: 'finale', note: 'No per-continent END movie on disc; closes on the finale.' },
  OCEANIA: { movie: 'END.DXR', kind: 'finale', note: 'No per-continent END movie on disc; closes on the finale.' },
  SOUTHAME: { movie: 'SAEND', kind: 'continent', note: 'SOUTHAME/SAEND/SAEND.DXR' },
};

// Embedded named minigames on the disc (*GAME.DXR) + maze scenes.
// status 'playable' = a WH-native playable shell ships in this slice;
// status 'shell' = source file + location recorded, rules live inside the .DXR
// (not recoverable from the catalog) — build follows, nothing faked.
export const ROLYPOLYS_MINIGAMES = [
  { id: 'BLUEGAME', area: 'EUROPA', region: 'ITALY', whName: 'Blue Game', status: 'shell', note: 'EUROPA/ITALY/BLUEGAME.DXR. Original rules live inside the .DXR.' },
  { id: 'OXGAME', area: 'EUROPA', region: 'SPANISH', whName: "Bull Run — TOU's Ox Dodge", status: 'playable', note: 'EUROPA/SPANISH/OXGAME.DXR. WH shell: dodge the charging ox; a hit ends the run.' },
  { id: 'HIMEGAME', area: 'JAPAN', region: 'HIMEJI', whName: 'Himeji Castle Game', status: 'shell', note: 'JAPAN/HIMEJI/HIMEGAME.DXR. Original rules live inside the .DXR.' },
  { id: 'WHALGAME', area: 'NANKMAP', region: 'NANKMAP', whName: 'Whale Game', status: 'shell', note: 'NANK/WHALGAME.DXR. Original rules live inside the .DXR.' },
  { id: 'SHPGAME', area: 'OCEANIA', region: 'SHEEP', whName: 'Sheep Farm Game', status: 'shell', note: 'OCEANIA/SHEEP/SHPGAME.DXR. Original rules live inside the .DXR.' },
  { id: 'GAMECOW', area: 'AMERICA', region: 'COWBOY', whName: 'Cowboy Game', status: 'shell', note: 'AMERICA/COWBOY/GAMECOW.DXR. Original rules live inside the .DXR.' },
  { id: 'MEIRO', area: 'JAPAN', region: 'SAPPORO', whName: 'Sapporo Maze', status: 'shell', note: 'JAPAN/SAPPORO/MEIRO.DXR (4.3 MB maze).' },
  { id: 'MAZE', area: 'OCEANIA', region: 'NABEL', whName: 'Nabel Maze', status: 'shell', note: 'OCEANIA/NABEL/MAZE.DXR.' },
];

// God-within anchors — the disc's own mythic sites. whStage is a PROPOSED WH
// god-within stage for each anchor, not a shipped stage.
export const ROLYPOLYS_GOD_WITHIN = [
  { scene: 'SHRINE', area: 'AFRICA', region: 'RUINS', whStage: 'Shrine of the God Within' },
  { scene: 'PRAYER', area: 'AFRICA', region: 'GRAND', whStage: 'Prayer in the Grand' },
  { scene: 'GODDESS', area: 'AMERICA', region: 'NY', whStage: 'Goddess Over the Harbour' },
  { scene: 'TENGIN3', area: 'JAPAN', region: 'TENG', whStage: 'Tengu Mountain', note: 'Disc anchor is the TENG region (tengu mythic site); TENGIN3 (5.3 MB) is its biggest scene movie.' },
  { scene: 'PYRAMID', area: 'AFRICA', region: 'RUINS', whStage: 'Pyramid of the Ruins' },
  { scene: 'PYRAMSTP', area: 'AMERICA', region: 'MEXICO', whStage: 'Step Pyramid' },
  { scene: 'PYRAMSUN', area: 'AMERICA', region: 'MEXICO', whStage: 'Sun Pyramid' },
  { scene: 'NASKA', area: 'SOUTHAME', region: 'NASKA', whStage: 'Nazca Lines' },
  { scene: 'BIGHEAD', area: 'AMERICA', region: 'MEXICO', whStage: 'Olmec Head' },
  { scene: 'DEVIL', area: 'AMERICA', region: 'LOS', whStage: 'Devil of Los Angeles' },
  { scene: 'STPAUL', area: 'EUROPA', region: 'ENGLAND', whStage: "St Paul's" },
  { scene: 'TAJI', area: 'ASIA', region: 'INDIA', whStage: 'Taj Mahal' },
];

// The 26 letter vignettes (Nanakorobi Yaoki: A–Z.DXR + EXPA–EXPZ.DXR).
// Disc words were Sato's proverbs (A Against, B Blue, ...). WH vignettes keep the
// A–Z shape and replace each word with WH canon. Every word below is a verified
// WH-canon term (Nine Souls, Five Lands, Phantom Marketplace, the Trial, the
// Shrine, Soul Shards / Soul Urge) or a file-grounded anchor (P for PRAYER).
// Host: RIN. Text is one line of WH canon each — no Sato proverb content reused.
export const ROLYPOLYS_VIGNETTES = [
  { letter: 'A', word: 'Arena', text: 'Every soul fights somewhere. The arenas are where the Trial is decided, bout by bout.' },
  { letter: 'B', word: 'Byou', text: 'The Sick Soul. Its illness is its weapon — a body that will not obey cannot be read.' },
  { letter: 'C', word: 'Chō-han', text: "The Trader's dice. Even or odd — the house takes its cut, and the Trader always eats." },
  { letter: 'D', word: 'Destruction', text: "The Helix Palace's Destruction room, made flesh in RETSU. Every hit is meant to end the fight." },
  { letter: 'E', word: 'Eyeball Mountains', text: 'They watch the Phantom Marketplace from above. Nothing here is real, but the prices are.' },
  { letter: 'F', word: 'Five Lands', text: 'Wood, Fire, Earth, Metal, Water. Every soul belongs to one land — and owes it.' },
  { letter: 'G', word: 'Gyou', text: 'The Moving Soul. Speed as identity; it cannot stop moving, so it never stops advancing.' },
  { letter: 'H', word: 'Helix Palace', text: 'The palace of the Nine Souls. Its rooms remember every telling back wrong.' },
  { letter: 'I', word: 'Immortality', text: "The Helix Palace's Immortality room: one hundred candles, one tale each." },
  { letter: 'J', word: 'Jin', text: 'The Blade Soul. It cuts both ways — precise, ritual, terrifying.' },
  { letter: 'K', word: 'Kai', text: 'The Sea Soul. It fights like water and finds every opening.' },
  { letter: 'L', word: 'Land of Wood', text: 'The Tree of Life holds glowing souls like fruit, and the harvest returns them home.' },
  { letter: 'M', word: 'Marketplace', text: 'The Phantom Marketplace, under the Eyeball Mountains. The Trader runs the table himself.' },
  { letter: 'N', word: 'Nine Souls', text: 'Nine lost souls of Tong-Nou. Each one remembers nothing but the trial.' },
  { letter: 'O', word: 'Octagonal Shrine', text: 'The shrine on the Central Mountain keeps a terminal where arriving souls are read before they are weighed.' },
  { letter: 'P', word: 'Prayer', text: 'A prayer scene stands in the Grand — the most direct god-within anchor on the Roly-Polys disc.' },
  { letter: 'Q', word: 'Question', text: 'The Trial asks every arriving soul one question. No soul remembers being asked — only the answer.' },
  { letter: 'R', word: 'Rin', text: 'The Protagonist Soul. Dignified, cold, self-possessed. The soul the player begins as.' },
  { letter: 'S', word: 'Shards', text: 'Soul Shards. Winnings from the side games; the currency of the head-world.' },
  { letter: 'T', word: 'Trial', text: 'The Trial of Tong-Nou: die, and be reborn. Death is progression.' },
  { letter: 'U', word: 'Urge', text: 'Soul Urge. The pips on the player card — the drive that spends itself in the fight.' },
  { letter: 'V', word: 'Versus', text: 'Soul against soul. The Trial, decided one bout at a time.' },
  { letter: 'W', word: 'Weighing', text: 'Arriving souls are read, then weighed. The shrine decides what a soul is worth.' },
  { letter: 'X', word: 'Xingyiquan', text: "The internal art — Byou's deceptive stances, Zen's stillness that kills." },
  { letter: 'Y', word: 'You', text: 'The arriving soul. The Trial is yours; the ship sails where you point it.' },
  { letter: 'Z', word: 'Zen', text: 'The Still Soul. It barely moves — and does not need to.' },
];

// Nanakorobi minigames (disc sources) and their WH hosts.
export const ROLYPOLYS_NANAKOROBI_GAMES = [
  { id: 'SHOOTING', disc: 'KOTOWAZA/SHOOTING.DXR', whName: "TOU's Shooting Gallery", whHost: 'TOU', note: 'Cho shooting gallery on disc; WH host is TOU, the Fighting Soul.' },
  { id: 'MISO_KO', disc: 'KOTOWAZA/MISO_KO.DXR', whName: "KAI's Cooking School — Miso", whHost: 'KAI', note: "Pon's Cooking School on disc; WH host is KAI, the Sea Soul (miso is the sea's soup)." },
  { id: 'SLOT', disc: 'slot_20231009 slot.dcr (OSD website, 1997-06-05)', whName: "The Trader's Slot", whHost: 'Trader', note: 'Shockwave slot machine from the OSD website; WH host is the Trader (Las Vegas Akiko on disc).' },
];

export const ROLYPOLYS_WORLD = {
  ship: ROLYPOLYS_SHIP,
  areas: ROLYPOLYS_AREAS,
  links: ROLYPOLYS_LINKS,
  endings: ROLYPOLYS_ENDINGS,
  minigames: ROLYPOLYS_MINIGAMES,
  godWithin: ROLYPOLYS_GOD_WITHIN,
  vignettes: ROLYPOLYS_VIGNETTES,
  nanakorobiGames: ROLYPOLYS_NANAKOROBI_GAMES,
};
