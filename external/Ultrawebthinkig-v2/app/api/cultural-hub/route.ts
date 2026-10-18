import { NextRequest, NextResponse } from 'next/server';

// Cultural & Social Hub - Arte, Kulturë, Gjuhë dhe Shoqëri
export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const domain = searchParams.get('domain');
  const language = searchParams.get('language');
  
  try {
    const culturalResources = {
      // Digital Arts & Creative Tools
      digital_arts: {
        blender: {
          url: 'https://github.com/blender/blender',
          description: 'Free and open source 3D creation suite',
          type: 'software',
          language: 'C++/Python',
          stars: '13k+',
          license: 'GPL-3.0',
          applications: ['3D modeling', 'Animation', 'VFX', 'Game development']
        },
        gimp: {
          url: 'https://github.com/GNOME/gimp',
          description: 'GNU Image Manipulation Program',
          type: 'software',
          language: 'C/Python',
          stars: '5k+',
          license: 'GPL-3.0',
          applications: ['Photo editing', 'Digital painting', 'Graphic design']
        },
        processing: {
          url: 'https://github.com/processing/processing',
          description: 'Flexible software sketchbook for visual arts',
          type: 'language',
          language: 'Java',
          stars: '6k+',
          license: 'GPL-2.0',
          applications: ['Generative art', 'Data visualization', 'Interactive media']
        },
        p5js: {
          url: 'https://github.com/processing/p5.js',
          description: 'JavaScript library for creative coding',
          type: 'library',
          language: 'JavaScript',
          stars: '21k+',
          license: 'LGPL-2.1',
          applications: ['Web-based art', 'Interactive design', 'Educational tools']
        }
      },

      // Music & Audio
      music_audio: {
        audacity: {
          url: 'https://github.com/audacity/audacity',
          description: 'Free, open source, cross-platform audio software',
          type: 'software',
          language: 'C++',
          stars: '12k+',
          license: 'GPL-2.0',
          applications: ['Audio editing', 'Podcast production', 'Music recording']
        },
        supercollider: {
          url: 'https://github.com/supercollider/supercollider',
          description: 'Platform for audio synthesis and algorithmic composition',
          type: 'language',
          language: 'C++',
          stars: '5k+',
          license: 'GPL-3.0',
          applications: ['Electronic music', 'Sound art', 'Live coding']
        },
        sonic_pi: {
          url: 'https://github.com/sonic-pi-net/sonic-pi',
          description: 'Code-based music creation and performance tool',
          type: 'software',
          language: 'Ruby/C++',
          stars: '10k+',
          license: 'MIT',
          applications: ['Live music coding', 'Education', 'Electronic music']
        },
        musescore: {
          url: 'https://github.com/musescore/MuseScore',
          description: 'Music notation and composition software',
          type: 'software',
          language: 'C++',
          stars: '12k+',
          license: 'GPL-3.0',
          applications: ['Music notation', 'Composition', 'Sheet music']
        }
      },

      // Languages & Linguistics
      languages: {
        unicode: {
          url: 'https://github.com/unicode-org/icu',
          description: 'International Components for Unicode',
          type: 'library',
          language: 'C++/Java',
          stars: '3k+',
          license: 'Unicode-DFS-2016',
          applications: ['Text processing', 'Internationalization', 'Language support']
        },
        spacy_languages: {
          url: 'https://github.com/explosion/spacy-models',
          description: 'Language models for spaCy NLP library',
          type: 'models',
          language: 'Python',
          stars: '400+',
          license: 'MIT',
          applications: ['Multi-language NLP', 'Translation', 'Text analysis'],
          supportedLanguages: ['Albanian', 'English', 'German', 'French', 'Italian', 'Spanish', '90+ more']
        },
        openai_whisper: {
          url: 'https://github.com/openai/whisper',
          description: 'Robust speech recognition via large-scale weak supervision',
          type: 'model',
          language: 'Python',
          stars: '69k+',
          license: 'MIT',
          applications: ['Speech-to-text', 'Transcription', 'Multilingual audio processing']
        },
        polyglot: {
          url: 'https://github.com/aboSamoor/polyglot',
          description: 'Natural language pipeline supporting 196+ languages',
          type: 'library',
          language: 'Python',
          stars: '2k+',
          license: 'GPL-3.0',
          applications: ['Language detection', 'Sentiment analysis', 'Multi-language NLP']
        }
      },

      // Literature & Writing
      literature: {
        zim_wiki: {
          url: 'https://github.com/zim-desktop-wiki/zim-desktop-wiki',
          description: 'Desktop wiki and personal knowledge management',
          type: 'software',
          language: 'Python',
          stars: '2k+',
          license: 'GPL-2.0',
          applications: ['Personal wiki', 'Note-taking', 'Knowledge management']
        },
        manuskript: {
          url: 'https://github.com/olivierkes/manuskript',
          description: 'Open-source tool for writers',
          type: 'software',
          language: 'Python',
          stars: '2k+',
          license: 'GPL-3.0',
          applications: ['Novel writing', 'Story organization', 'Character development']
        },
        calibre: {
          url: 'https://github.com/kovidgoyal/calibre',
          description: 'E-book manager and converter',
          type: 'software',
          language: 'Python/C++',
          stars: '19k+',
          license: 'GPL-3.0',
          applications: ['E-book management', 'Format conversion', 'Digital library']
        },
        gutenberg: {
          url: 'https://github.com/c-w/gutenberg',
          description: 'Library to download and process books from Project Gutenberg',
          type: 'library',
          language: 'Python',
          stars: '800+',
          license: 'Apache-2.0',
          applications: ['Literature analysis', 'Text mining', 'Digital humanities']
        }
      },

      // Cultural Heritage & Museums
      heritage: {
        omeka: {
          url: 'https://github.com/omeka/Omeka',
          description: 'Web publishing platform for cultural heritage collections',
          type: 'platform',
          language: 'PHP',
          stars: '500+',
          license: 'GPL-3.0',
          applications: ['Digital exhibits', 'Cultural collections', 'Museum websites']
        },
        dspace: {
          url: 'https://github.com/DSpace/DSpace',
          description: 'Open source repository software package',
          type: 'platform',
          language: 'Java',
          stars: '900+',
          license: 'BSD-3-Clause',
          applications: ['Digital archives', 'Institutional repositories', 'Cultural preservation']
        },
        europeana: {
          url: 'https://github.com/europeana/europeana-portal-collections',
          description: 'Europeana Collections portal',
          type: 'platform',
          language: 'Ruby/JavaScript',
          stars: '30+',
          license: 'EUPL-1.2',
          applications: ['Cultural heritage search', 'European collections', 'Digital culture']
        }
      },

      // Social & Community Tools
      social: {
        mastodon: {
          url: 'https://github.com/mastodon/mastodon',
          description: 'Decentralized social network',
          type: 'platform',
          language: 'Ruby/JavaScript',
          stars: '47k+',
          license: 'AGPL-3.0',
          applications: ['Social networking', 'Community building', 'Decentralized communication']
        },
        discourse: {
          url: 'https://github.com/discourse/discourse',
          description: 'Modern forum software for communities',
          type: 'platform',
          language: 'Ruby/JavaScript',
          stars: '42k+',
          license: 'GPL-2.0',
          applications: ['Community forums', 'Discussion platforms', 'Knowledge sharing']
        },
        diaspora: {
          url: 'https://github.com/diaspora/diaspora',
          description: 'Distributed social network',
          type: 'platform',
          language: 'Ruby',
          stars: '13k+',
          license: 'AGPL-3.0',
          applications: ['Decentralized social media', 'Privacy-focused networking', 'Federated communities']
        }
      },

      // Albanian Culture & Language (Special focus for our user)
      albanian: {
        albanian_wordnet: {
          url: 'https://github.com/albanianwordnet/albanianwordnet',
          description: 'Albanian WordNet - semantic lexicon',
          type: 'dataset',
          language: 'Albanian',
          stars: '10+',
          license: 'MIT',
          applications: ['Albanian NLP', 'Semantic analysis', 'Language research']
        },
        albanian_resources: {
          url: 'https://github.com/topics/albanian-language',
          description: 'Collection of Albanian language resources on GitHub',
          type: 'collection',
          language: 'Multiple',
          stars: 'Various',
          license: 'Various',
          applications: ['Language learning', 'Cultural preservation', 'Albanian computing']
        },
        folklore_digital: {
          url: 'https://github.com/folklorik/albanian-folklore',
          description: 'Digital archive of Albanian folklore and traditions',
          type: 'archive',
          language: 'Albanian/English',
          stars: '5+',
          license: 'CC-BY-4.0',
          applications: ['Cultural preservation', 'Educational resources', 'Research']
        }
      }
    };

    // Cultural trends and movements
    const culturalTrends = {
      digitalHumanities: [
        'Computational Literature Analysis',
        'Digital Archaeology',
        'Virtual Museum Experiences',
        'AI-Generated Art'
      ],
      openCulture: [
        'Creative Commons Movement',
        'Open Access Publishing',
        'Collaborative Art Projects',
        'Community-Driven Content'
      ],
      crossCultural: [
        'Multilingual Digital Platforms',
        'Global Collaboration Tools',
        'Cultural Exchange Programs',
        'International Art Residencies'
      ]
    };

    // Filter by domain if specified
    let responseData;
    if (domain && culturalResources[domain as keyof typeof culturalResources]) {
      responseData = {
        domain,
        resources: culturalResources[domain as keyof typeof culturalResources],
        totalInDomain: Object.keys(culturalResources[domain as keyof typeof culturalResources]).length
      };
    } else {
      responseData = {
        allDomains: culturalResources,
        culturalTrends,
        totalDomains: Object.keys(culturalResources).length,
        totalResources: Object.values(culturalResources).reduce((acc, domain) => acc + Object.keys(domain).length, 0),
        specialFocus: 'Albanian culture and Balkan heritage included'
      };
    }

    return NextResponse.json({
      status: 'success',
      data: responseData,
      metadata: {
        endpoint: '/api/cultural-hub',
        version: '1.0.0',
        timestamp: new Date().toISOString(),
        message: 'Burime kulturore nga e gjithë bota - arte, gjuhë, letërsi, muzikë dhe trashëgimi kulturore!'
      }
    });

  } catch (error) {
    return NextResponse.json({
      status: 'error',
      message: 'Failed to fetch cultural resources',
      error: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 });
  }
}
