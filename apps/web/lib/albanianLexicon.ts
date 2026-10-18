export interface AlbanianLexiconStats {
  count: number;
  anchors: string[];
  categories: {
    common: number;
    verbs: number;
    roots: number;
    prefixes: number;
    suffixes: number;
  };
}

const COMMON_WORDS = [
  'dhe', 'ose', 'por', 'sepse', 'megjithatë', 'ndërsa', 'atëherë', 'kështu', 'prandaj', 'ndoshta',
  'gjithmonë', 'shpesh', 'rrallë', 'sot', 'nesër', 'dje', 'tani', 'atëherë', 'shpejt', 'ngadalë',
  'mirë', 'keq', 'qartë', 'saktë', 'thjesht', 'natyrshëm', 'butë', 'fort', 'thellë', 'gjerë',
  'po', 'jo', 'sigurisht', 'ndoshta', 'vetëm', 'edhe', 'madje', 'sërish', 'përsëri', 'fillimisht',
  'pastaj', 'më pas', 'fund', 'fillim', 'rrugë', 'fjalë', 'mendim', 'ide', 'ndjenjë', 'zemër',
  'shpirt', 'tru', 'kujtesë', 'vëmendje', 'qetësi', 'besim', 'shpresë', 'dashuri', 'miqësi', 'respekt',
  'njeri', 'grua', 'burrë', 'vajzë', 'djalë', 'fëmijë', 'familje', 'mik', 'shok', 'shoqe',
  'punë', 'jetë', 'botë', 'kohë', 'ditë', 'natë', 'muaj', 'vit', 'moment', 'hap',
  'pyetje', 'përgjigje', 'bisedë', 'kuptim', 'arsye', 'logjikë', 'shembull', 'zgjidhje', 'plan', 'veprim',
  'aftësi', 'mundësi', 'forcë', 'vlerë', 'cilësi', 'qartësi', 'saktësi', 'kujdes', 'durim', 'urtësi',
  'qytet', 'fshat', 'shtëpi', 'dhomë', 'derë', 'dritare', 'rrjet', 'sistem', 'platformë', 'modul',
  'kamera', 'mikrofon', 'zë', 'tingull', 'imazh', 'foto', 'video', 'dokument', 'tekst', 'gjuhë',
  'shqip', 'anglisht', 'gjermanisht', 'frëngjisht', 'italisht', 'njohuri', 'mësim', 'libër', 'faqe', 'shënim',
  'pyes', 'dëgjoj', 'shoh', 'lexoj', 'shkruaj', 'flas', 'kuptoj', 'mendoj', 'provoj', 'ndihmoj',
  'rregull', 'gabim', 'problem', 'zgjedhje', 'qasje', 'rrjedhë', 'lidhje', 'sinjal', 'gjendje', 'status'
] as const;

const VERBS_OJ = [
  'punoj', 'lexoj', 'shkruaj', 'mendoj', 'kuptoj', 'ndihmoj', 'dëgjoj', 'shikoj', 'shpjegoj', 'analizoj',
  'krijoj', 'përdoroj', 'ndërtoj', 'kujtoj', 'besoj', 'vëzhgoj', 'krahasoj', 'kontrolloj', 'lidh', 'vazhdoj',
  'provoj', 'përmirësoj', 'zhvilloj', 'organizoj', 'komunikoj', 'vlerësoj', 'planifikoj', 'bashkoj', 'dërgoj', 'formuloj',
  'përshkruaj', 'studioj', 'hulumtoj', 'verifikoj', 'arsyetoj', 'thjeshtoj', 'saktësoj', 'qartësoj', 'mbështes', 'pranoj',
  'reflektoj', 'orientoj', 'adaptoj', 'ndryshoj', 'fokusohem', 'kujdesem', 'stabilizoj', 'filtrroj', 'rishikoj', 'plotësoj',
  'harmonizoj', 'sinkronizoj', 'parashikoj', 'konfirmoj', 'modifikoj', 'ruaj', 'mësoj', 'kujdesoj', 'korrigjoj', 'shoqëroj',
  'theksoj', 'qetësoj', 'adresoj', 'zgjeroj', 'thelloj', 'ndriçoj', 'rregulloj', 'shkallëzoj', 'siguroj', 'monitoroj',
  'raportoj', 'komentoj', 'strukturoj', 'modeloj', 'pasuroj', 'pastroj', 'freskoj', 'emërtoj', 'njoftoj', 'përqendroj'
] as const;

const ROOT_WORDS = [
  'gjuh', 'fjal', 'mend', 'ide', 'zemër', 'shpirt', 'tru', 'kujtes', 'vëmend', 'ndjenj',
  'qart', 'sakt', 'natyr', 'thjesht', 'urt', 'mençur', 'kujdes', 'dur', 'bes', 'shpres',
  'dashur', 'miq', 'respekt', 'mir', 'but', 'qet', 'thell', 'gjer', 'pastër', 'fort',
  'koh', 'dit', 'nat', 'moment', 'hap', 'rrug', 'jet', 'bot', 'pun', 'vepr',
  'pyet', 'përgjigj', 'bised', 'kupt', 'arsy', 'logjik', 'shembull', 'zgjidh', 'plan', 'zgjedh',
  'aft', 'mund', 'forc', 'vler', 'cil', 'status', 'gjend', 'sinjal', 'lidh', 'rrjet',
  'sistem', 'platform', 'modul', 'kamer', 'mikrofon', 'zë', 'tingull', 'imazh', 'foto', 'video',
  'dokument', 'tekst', 'lib', 'faq', 'shën', 'mës', 'njoh', 'ditur', 'shkenc', 'teknologj',
  'analiz', 'struktur', 'model', 'rit', 'rrit', 'zhvill', 'krij', 'ndërt', 'bashk', 'lëviz',
  'kujdesor', 'qendër', 'fokus', 'stabil', 'harmon', 'balanc', 'ritëm', 'ndriç', 'energj', 'rrjedh',
  'shik', 'dëgj', 'lex', 'shkrim', 'komunik', 'shpjeg', 'vëzhg', 'krahas', 'kontroll', 'verifik',
  'hulumt', 'përmirës', 'pasur', 'pastërt', 'qartës', 'saktës', 'thjeshtës', 'natyrshm', 'ngroht', 'afërs',
  'emocion', 'mirësjell', 'kujdesshm', 'qëndrueshm', 'lartës', 'thellës', 'gjerës', 'ndjeshm', 'përkusht', 'respektues',
  'bashkëpun', 'udhëzim', 'orientim', 'mbështet', 'sqarim', 'përmbajt', 'lexues', 'shkrues', 'dëgjues', 'vëzhgues'
] as const;

const PRODUCTIVE_PREFIXES = [
  'bashkë', 'mbi', 'nën', 'ndër', 'pa', 'ri', 'vetë', 'gjithë', 'mirë', 'keq', 'shumë', 'super'
] as const;

const PRODUCTIVE_SUFFIXES = [
  'im', 'je', 'or', 'ore', 'tar', 'tare', 'ësi', 'shmëri', 'ues', 'uese', 'isht', 'izëm'
] as const;

const ANCHOR_WORDS = [
  'mund', 'mundet', 'mundësi', 'qartë', 'saktë', 'natyrshëm', 'shqip', 'bisedë', 'dokument', 'sistem',
  'kamera', 'mikrofon', 'lexoj', 'shkruaj', 'kuptoj', 'ndihmoj', 'shpjegoj', 'analizoj', 'qetësi', 'respekt'
] as const;

function addWord(target: Set<string>, value: string) {
  const normalized = value
    .trim()
    .toLowerCase()
    .replace(/\s+/g, ' ')
    .replace(/[^a-zA-ZçëÇË\- ]/g, '');

  if (normalized.length >= 2) {
    target.add(normalized);
  }
}

function buildVerbForms(lemma: string): string[] {
  if (!lemma.endsWith('oj')) {
    return [lemma];
  }

  const stem = lemma.slice(0, -2);
  return [
    lemma,
    `${stem}on`,
    `${stem}ojmë`,
    `${stem}oni`,
    `${stem}ojnë`,
    `${stem}ova`,
    `${stem}ove`,
    `${stem}oi`,
    `${stem}uam`,
    `${stem}uat`,
    `${stem}uan`,
    `${stem}uar`,
    `${stem}im`,
    `${stem}je`,
    `${stem}ues`,
    `${stem}uese`,
  ];
}

function buildRootForms(root: string): string[] {
  const forms = new Set<string>([
    root,
    `${root}i`,
    `${root}e`,
    `${root}a`,
    `${root}et`,
    `${root}at`,
    `${root}or`,
    `${root}ore`,
    `${root}im`,
    `${root}je`,
    `${root}tar`,
    `${root}tare`,
    `${root}ësi`,
    `${root}shmëri`,
    `${root}ues`,
    `${root}uese`,
    `${root}isht`,
  ]);

  for (const prefix of PRODUCTIVE_PREFIXES) {
    forms.add(`${prefix}${root}`);
    forms.add(`${prefix}${root}im`);
    forms.add(`${prefix}${root}je`);
    forms.add(`${prefix}${root}or`);
  }

  for (const suffix of PRODUCTIVE_SUFFIXES) {
    forms.add(`${root}${suffix}`);
  }

  for (const prefix of PRODUCTIVE_PREFIXES.slice(0, 8)) {
    for (const suffix of PRODUCTIVE_SUFFIXES.slice(0, 8)) {
      forms.add(`${prefix}${root}${suffix}`);
    }
  }

  return [...forms];
}

function buildLexicon(): string[] {
  const words = new Set<string>();

  for (const word of COMMON_WORDS) {
    addWord(words, word);
  }

  for (const lemma of VERBS_OJ) {
    for (const form of buildVerbForms(lemma)) {
      addWord(words, form);
    }
  }

  for (const root of ROOT_WORDS) {
    for (const form of buildRootForms(root)) {
      addWord(words, form);
    }
  }

  return [...words].sort((left, right) => left.localeCompare(right, 'sq'));
}

export const ALBANIAN_LEXICON_WORDS = buildLexicon();
export const ALBANIAN_LEXICON_COUNT = ALBANIAN_LEXICON_WORDS.length;

export function getAlbanianLexiconStats(): AlbanianLexiconStats {
  return {
    count: ALBANIAN_LEXICON_COUNT,
    anchors: [...ANCHOR_WORDS],
    categories: {
      common: COMMON_WORDS.length,
      verbs: VERBS_OJ.length,
      roots: ROOT_WORDS.length,
      prefixes: PRODUCTIVE_PREFIXES.length,
      suffixes: PRODUCTIVE_SUFFIXES.length,
    },
  };
}

export function getAlbanianLexiconGuidance(): string {
  const stats = getAlbanianLexiconStats();
  return [
    `Internal Albanian lexicon available: ${stats.count} lexical anchors and word forms.`,
    'Prefer standard Albanian, simple syntax, and common words over stiff literal translation.',
    `Core anchors: ${stats.anchors.join(', ')}.`,
  ].join(' ');
}
