import { NextRequest, NextResponse } from 'next/server';

// ALBA/ASI Hub - Central Intelligence and Resource Management
export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const category = searchParams.get('category');
  const domain = searchParams.get('domain');
  
  try {
    // ALBA (Advanced Logic and Business Analytics) Resources
    const albaResources = {
      // Open Source AI/ML Libraries
      ai_ml: {
        tensorflow: {
          url: 'https://github.com/tensorflow/tensorflow',
          description: 'Open source machine learning framework',
          type: 'library',
          language: 'Python/C++',
          stars: '185k+',
          license: 'Apache-2.0'
        },
        pytorch: {
          url: 'https://github.com/pytorch/pytorch',
          description: 'Tensors and Dynamic neural networks',
          type: 'library',
          language: 'Python/C++',
          stars: '82k+',
          license: 'BSD-3-Clause'
        },
        huggingface: {
          url: 'https://github.com/huggingface/transformers',
          description: 'State-of-the-art ML for PyTorch/TensorFlow',
          type: 'library',
          language: 'Python',
          stars: '133k+',
          license: 'Apache-2.0'
        },
        scikit_learn: {
          url: 'https://github.com/scikit-learn/scikit-learn',
          description: 'Machine Learning in Python',
          type: 'library',
          language: 'Python',
          stars: '59k+',
          license: 'BSD-3-Clause'
        }
      },
      
      // Web Development Frameworks
      web_dev: {
        nextjs: {
          url: 'https://github.com/vercel/next.js',
          description: 'The React Framework for the Web',
          type: 'framework',
          language: 'JavaScript/TypeScript',
          stars: '125k+',
          license: 'MIT'
        },
        react: {
          url: 'https://github.com/facebook/react',
          description: 'The library for web and native user interfaces',
          type: 'library',
          language: 'JavaScript',
          stars: '228k+',
          license: 'MIT'
        },
        vue: {
          url: 'https://github.com/vuejs/vue',
          description: 'Progressive JavaScript framework',
          type: 'framework',
          language: 'JavaScript',
          stars: '208k+',
          license: 'MIT'
        },
        svelte: {
          url: 'https://github.com/sveltejs/svelte',
          description: 'Cybernetically enhanced web apps',
          type: 'framework',
          language: 'JavaScript',
          stars: '78k+',
          license: 'MIT'
        }
      },

      // Backend & APIs
      backend: {
        fastapi: {
          url: 'https://github.com/tiangolo/fastapi',
          description: 'Modern, fast web framework for building APIs',
          type: 'framework',
          language: 'Python',
          stars: '76k+',
          license: 'MIT'
        },
        express: {
          url: 'https://github.com/expressjs/express',
          description: 'Fast, unopinionated, minimalist web framework',
          type: 'framework',
          language: 'JavaScript',
          stars: '65k+',
          license: 'MIT'
        },
        django: {
          url: 'https://github.com/django/django',
          description: 'High-level Python web framework',
          type: 'framework',
          language: 'Python',
          stars: '79k+',
          license: 'BSD-3-Clause'
        },
        spring_boot: {
          url: 'https://github.com/spring-projects/spring-boot',
          description: 'Spring Boot helps create stand-alone applications',
          type: 'framework',
          language: 'Java',
          stars: '74k+',
          license: 'Apache-2.0'
        }
      },

      // Data Science & Analytics
      data_science: {
        pandas: {
          url: 'https://github.com/pandas-dev/pandas',
          description: 'Powerful data analysis and manipulation library',
          type: 'library',
          language: 'Python',
          stars: '43k+',
          license: 'BSD-3-Clause'
        },
        numpy: {
          url: 'https://github.com/numpy/numpy',
          description: 'Fundamental package for scientific computing',
          type: 'library',
          language: 'Python',
          stars: '28k+',
          license: 'BSD-3-Clause'
        },
        jupyter: {
          url: 'https://github.com/jupyter/notebook',
          description: 'Web-based notebook environment for interactive computing',
          type: 'platform',
          language: 'Python/JavaScript',
          stars: '12k+',
          license: 'BSD-3-Clause'
        },
        apache_spark: {
          url: 'https://github.com/apache/spark',
          description: 'Unified engine for large-scale data analytics',
          type: 'platform',
          language: 'Scala/Python/Java',
          stars: '39k+',
          license: 'Apache-2.0'
        }
      },

      // DevOps & Infrastructure
      devops: {
        kubernetes: {
          url: 'https://github.com/kubernetes/kubernetes',
          description: 'Production-Grade Container Scheduling and Management',
          type: 'platform',
          language: 'Go',
          stars: '110k+',
          license: 'Apache-2.0'
        },
        docker: {
          url: 'https://github.com/moby/moby',
          description: 'The Moby Project - container platform',
          type: 'platform',
          language: 'Go',
          stars: '68k+',
          license: 'Apache-2.0'
        },
        terraform: {
          url: 'https://github.com/hashicorp/terraform',
          description: 'Infrastructure as Code to provision and manage cloud',
          type: 'tool',
          language: 'Go',
          stars: '42k+',
          license: 'BUSL-1.1'
        },
        ansible: {
          url: 'https://github.com/ansible/ansible',
          description: 'Radically simple IT automation platform',
          type: 'tool',
          language: 'Python',
          stars: '62k+',
          license: 'GPL-3.0'
        }
      },

      // Blockchain & Crypto
      blockchain: {
        ethereum: {
          url: 'https://github.com/ethereum/go-ethereum',
          description: 'Official Go implementation of Ethereum protocol',
          type: 'blockchain',
          language: 'Go',
          stars: '47k+',
          license: 'GPL-3.0'
        },
        solidity: {
          url: 'https://github.com/ethereum/solidity',
          description: 'Solidity programming language',
          type: 'language',
          language: 'C++',
          stars: '23k+',
          license: 'GPL-3.0'
        },
        web3js: {
          url: 'https://github.com/web3/web3.js',
          description: 'Collection of libraries for Ethereum blockchain',
          type: 'library',
          language: 'JavaScript',
          stars: '19k+',
          license: 'LGPL-3.0'
        },
        bitcoin: {
          url: 'https://github.com/bitcoin/bitcoin',
          description: 'Bitcoin Core integration/staging tree',
          type: 'blockchain',
          language: 'C++',
          stars: '78k+',
          license: 'MIT'
        }
      },

      // IoT & Hardware
      iot: {
        arduino: {
          url: 'https://github.com/arduino/Arduino',
          description: 'Arduino IDE and libraries',
          type: 'platform',
          language: 'C/C++',
          stars: '14k+',
          license: 'GPL-2.0'
        },
        raspberry_pi: {
          url: 'https://github.com/raspberrypi/linux',
          description: 'Kernel source tree for Raspberry Pi',
          type: 'os',
          language: 'C',
          stars: '11k+',
          license: 'GPL-2.0'
        },
        platformio: {
          url: 'https://github.com/platformio/platformio-core',
          description: 'Professional collaborative platform for embedded development',
          type: 'platform',
          language: 'Python',
          stars: '7k+',
          license: 'Apache-2.0'
        },
        mqtt: {
          url: 'https://github.com/eclipse/mosquitto',
          description: 'Eclipse Mosquitto MQTT broker',
          type: 'broker',
          language: 'C',
          stars: '9k+',
          license: 'EPL-2.0'
        }
      }
    };

    // ASI (Advanced System Intelligence) Resources
    const asiResources = {
      autonomous_systems: {
        ros: {
          url: 'https://github.com/ros/ros',
          description: 'Robot Operating System',
          type: 'framework',
          language: 'C++/Python',
          stars: '3k+',
          license: 'BSD-3-Clause'
        },
        autopilot: {
          url: 'https://github.com/PX4/PX4-Autopilot',
          description: 'Open Source Flight Control Software',
          type: 'firmware',
          language: 'C++',
          stars: '8k+',
          license: 'BSD-3-Clause'
        }
      },
      
      computer_vision: {
        opencv: {
          url: 'https://github.com/opencv/opencv',
          description: 'Open Source Computer Vision Library',
          type: 'library',
          language: 'C++/Python',
          stars: '78k+',
          license: 'Apache-2.0'
        },
        yolo: {
          url: 'https://github.com/ultralytics/yolov5',
          description: 'Real-time object detection',
          type: 'model',
          language: 'Python',
          stars: '50k+',
          license: 'AGPL-3.0'
        }
      },

      natural_language: {
        spacy: {
          url: 'https://github.com/explosion/spaCy',
          description: 'Industrial-strength Natural Language Processing',
          type: 'library',
          language: 'Python',
          stars: '30k+',
          license: 'MIT'
        },
        nltk: {
          url: 'https://github.com/nltk/nltk',
          description: 'Natural Language Toolkit',
          type: 'library',
          language: 'Python',
          stars: '13k+',
          license: 'Apache-2.0'
        }
      }
    };

    // Filter resources based on category/domain
    let responseData;
    if (category && albaResources[category as keyof typeof albaResources]) {
      responseData = {
        category,
        resources: albaResources[category as keyof typeof albaResources],
        type: 'ALBA'
      };
    } else if (domain && asiResources[domain as keyof typeof asiResources]) {
      responseData = {
        domain,
        resources: asiResources[domain as keyof typeof asiResources],
        type: 'ASI'
      };
    } else {
      responseData = {
        alba: albaResources,
        asi: asiResources,
        totalResources: Object.keys(albaResources).length + Object.keys(asiResources).length
      };
    }

    return NextResponse.json({
      status: 'success',
      data: responseData,
      metadata: {
        endpoint: '/api/alba-asi-hub',
        version: '1.0.0',
        timestamp: new Date().toISOString(),
        message: 'ALBA/ASI Open Source Resource Hub - Sa më shumë burime, aq më shumë mundësi!'
      }
    });

  } catch (error) {
    return NextResponse.json({
      status: 'error',
      message: 'Failed to fetch ALBA/ASI resources',
      error: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 });
  }
}
