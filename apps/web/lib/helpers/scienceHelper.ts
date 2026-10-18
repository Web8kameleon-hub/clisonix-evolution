/**
 * ScienceHelper - Fact-based knowledge without speculation
 * Provides deterministic scientific definitions & facts
 */

import { Helper, HelperResult } from './types';

// Curated Albanian science knowledge base
const SCIENCE_KB: Record<string, { definition: string; details?: string }> = {
  atom: {
    definition: 'Atomi është njësia më e vogël e një elementi kimik që ruan vetitë e tij; përbëhet nga protonë, neutronë dhe elektrone.',
    details: 'Protoni dhe neutroni rrezidojnë në bërthamë; elektronet orbitojnë rreth saj.',
  },
  ujë: {
    definition: 'Uji (H₂O) është një komponim kimik i përbërë nga dy atome hidrogjeni dhe një atom oksigjeni.',
    details: 'Uji është zgjidhës universal, përgjegjës për të gjithë jetën në Tokë.',
  },
  gravitet: {
    definition: 'Graviteti është forca tërheqëse mes objekteve me masë; mban trupat në tokë dhe planetët në orbitë rreth Diellit.',
    details: 'Formula Njutoniane: F = G × (m₁ × m₂) / r².',
  },
  fotosinteza: {
    definition: 'Fotosinteza është procesi me të cilin bimët, algjet dhe disa baktere përdorin dritën Dielli, ujin dhe CO₂ për të prodhuar glukozë dhe oksigjen.',
    details: '6 CO₂ + 6 H₂O + drita → C₆H₁₂O₆ + 6 O₂.',
  },
  'adn': {
    definition: 'ADN (acid deoksiribonukleik) është molekula që mban informacionin gjenetik të të gjithë organizmave të ndryshëm.',
    details: 'ADN përbëhet nga dy zinxhirë të lidhur, me baza: adeninë, timinën, guaninën dhe citosinën.',
  },
  'elektrit': {
    definition: 'Elektriciteti është fenomeni fizik i lidhur me pranisë dhe rrjedhimin e elektroneve.',
    details: 'Tension = Rrymë × Rezistencë (V = I × R).',
  },
  'magnetizem': {
    definition: 'Magnetizmi është vetia e disa materialeve që të tërheqin objekte të tjera ferrousha ose të ndërveprojnë me fusha magnetike.',
    details: 'Magnetët kanë pola pozitiv (+) dhe negativ (-); polat e kundërt tërhiqen, polat e njëjtë refuzohen.',
  },
  'nxehtësi': {
    definition: 'Nxehtësia është forma e energjisë që transferohet ndërmjet sistemeve (ose brenda një sistemi) për shkak të dallimit të temperaturave.',
    details: 'Transferohet përmes përçueshmërisë, konvekcës ose rrezatimit.',
  },
  'entropi': {
    definition: 'Entropia është masë e çrregullimit ose rastësinë në një sistem; rritet gjithmonë sipas ligjit të dytë të termodinamikës.',
    details: 'Në sisteme të izoluara, entropia nuk mund të zvogëlohet asnjëherë.',
  },
};

// Pattern matching for science questions
const SCIENCE_PATTERNS = [
  /atom|molekul|ion|elektron|proton|neutron/i,
  /ujë|uji|h2o|hidrogjen|oksigjeni/i,
  /gravitet|peshë|orkbitë|planet|yll|diell/i,
  /fotosintez|kloroplast|glukozë/i,
  /adn|arn|gene|kromo|mutacion/i,
  /elektrit|rrymë|tension|vat|amper/i,
  /magnetizem|pól magneti|ferromagnetizem/i,
  /nxehtësi|temperaturë|energji|kalori/i,
  /entropi|termodinamik|prill/i,
  /kimik|reaktiv|element|përbërje|formula/i,
  /fizik|mekanik|dinamik|kinematik/i,
];

export const ScienceHelper: Helper = {
  name: 'ScienceHelper',

  canHandle(question: string): boolean {
    return SCIENCE_PATTERNS.some((re) => re.test(question));
  },

  async handle(question: string): Promise<HelperResult> {
    const q = question.toLowerCase();

    // Try exact or fuzzy match in KB
    for (const [key, content] of Object.entries(SCIENCE_KB)) {
      // Check if question contains the key term
      const keyNormalized = key.replace(/it$/, '').replace(/it$/, '');
      if (q.includes(key) || q.includes(keyNormalized)) {
        return {
          domain: 'science',
          ok: true,
          confidence: 'high',
          answer: content.definition,
          notes: content.details || undefined,
        };
      }
    }

    // Partial match: check if any part of question relates to KB
    const keyWords = Object.keys(SCIENCE_KB);
    const foundKeyword = keyWords.find(
      (k) => q.includes(k) || q.includes(k.replace(/it$/, ''))
    );

    if (foundKeyword) {
      const content = SCIENCE_KB[foundKeyword];
      return {
        domain: 'science',
        ok: true,
        confidence: 'high',
        answer: content.definition,
        notes: content.details || undefined,
      };
    }

    // Question matches pattern but KB gap
    return {
      domain: 'science',
      ok: true,
      confidence: 'low',
      answer: 'ScienceHelper: Njoh këtë lloj pyetjeje shkencore, por nuk kam përkufizim të saktë në bazën e njohurive.',
      notes: 'Kërkesa: zgjerimi i bazazës për më shumë terma shkencorë. Kontakto admin për përditësime.',
    };
  },
};
