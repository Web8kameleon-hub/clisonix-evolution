import { NextRequest, NextResponse } from 'next/server';

// Life Sciences & Research Hub - Burime nga fusha të jetës
export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const field = searchParams.get('field');
  
  try {
    const lifeSciencesResources = {
      // Bioinformatics & Computational Biology
      bioinformatics: {
        biopython: {
          url: 'https://github.com/biopython/biopython',
          description: 'Python tools for computational molecular biology',
          type: 'library',
          language: 'Python',
          stars: '4k+',
          license: 'BSD-3-Clause',
          applications: ['DNA/RNA analysis', 'Protein structure', 'Phylogenetics']
        },
        bioconductor: {
          url: 'https://github.com/Bioconductor/BiocManager',
          description: 'R packages for bioinformatics and computational biology',
          type: 'platform',
          language: 'R',
          stars: '300+',
          license: 'Artistic-2.0',
          applications: ['Genomics', 'Microarray analysis', 'RNA-seq']
        },
        galaxy: {
          url: 'https://github.com/galaxyproject/galaxy',
          description: 'Web-based platform for accessible, reproducible, and collaborative biomedical analyses',
          type: 'platform',
          language: 'Python/JavaScript',
          stars: '1k+',
          license: 'MIT',
          applications: ['Workflow management', 'Data analysis', 'Collaboration']
        }
      },

      // Medical Imaging & Healthcare
      medical_imaging: {
        itk: {
          url: 'https://github.com/InsightSoftwareConsortium/ITK',
          description: 'Insight Segmentation and Registration Toolkit',
          type: 'library',
          language: 'C++/Python',
          stars: '1k+',
          license: 'Apache-2.0',
          applications: ['Medical image analysis', '3D visualization', 'Image registration']
        },
        dicom: {
          url: 'https://github.com/pydicom/pydicom',
          description: 'Read, modify and write DICOM files with python',
          type: 'library',
          language: 'Python',
          stars: '2k+',
          license: 'MIT',
          applications: ['Medical imaging', 'DICOM processing', 'Healthcare IT']
        },
        opencv_medical: {
          url: 'https://github.com/opencv/opencv_contrib',
          description: 'OpenCV contrib modules including medical imaging',
          type: 'library',
          language: 'C++/Python',
          stars: '9k+',
          license: 'Apache-2.0',
          applications: ['X-ray analysis', 'MRI processing', 'CT scan analysis']
        }
      },

      // Environmental Science & Climate
      environmental: {
        climate_data: {
          url: 'https://github.com/pangeo-data/pangeo',
          description: 'Big Data geoscience platform',
          type: 'platform',
          language: 'Python',
          stars: '700+',
          license: 'MIT',
          applications: ['Climate modeling', 'Weather prediction', 'Environmental monitoring']
        },
        earth_engine: {
          url: 'https://github.com/google/earthengine-api',
          description: 'Google Earth Engine API for planetary-scale geospatial analysis',
          type: 'api',
          language: 'JavaScript/Python',
          stars: '2k+',
          license: 'Apache-2.0',
          applications: ['Satellite imagery', 'Deforestation tracking', 'Land use analysis']
        },
        atmospheric: {
          url: 'https://github.com/NCAR/atmospheric-chemistry',
          description: 'Tools for atmospheric chemistry and air quality modeling',
          type: 'toolkit',
          language: 'Fortran/Python',
          stars: '200+',
          license: 'BSD-3-Clause',
          applications: ['Air quality', 'Pollution modeling', 'Climate research']
        }
      },

      // Agriculture & Food Science
      agriculture: {
        farmbot: {
          url: 'https://github.com/FarmBot/Farmbot-Web-App',
          description: 'Web application for FarmBot automated farming',
          type: 'platform',
          language: 'TypeScript/Ruby',
          stars: '800+',
          license: 'MIT',
          applications: ['Precision agriculture', 'Automated farming', 'Crop monitoring']
        },
        plant_cv: {
          url: 'https://github.com/danforthcenter/plantcv',
          description: 'Plant phenotyping using computer vision',
          type: 'library',
          language: 'Python',
          stars: '600+',
          license: 'MIT',
          applications: ['Plant analysis', 'Growth monitoring', 'Agricultural research']
        },
        agroml: {
          url: 'https://github.com/agroimpacts/farmlandmapper',
          description: 'Machine learning for agricultural land mapping',
          type: 'toolkit',
          language: 'Python/R',
          stars: '100+',
          license: 'MIT',
          applications: ['Crop classification', 'Yield prediction', 'Land use mapping']
        }
      },

      // Neuroscience & Brain Research
      neuroscience: {
        nilearn: {
          url: 'https://github.com/nilearn/nilearn',
          description: 'Machine learning for neuroimaging in Python',
          type: 'library',
          language: 'Python',
          stars: '1k+',
          license: 'BSD-3-Clause',
          applications: ['fMRI analysis', 'Brain connectivity', 'Neuroimaging']
        },
        mne: {
          url: 'https://github.com/mne-tools/mne-python',
          description: 'MEG and EEG data analysis',
          type: 'library',
          language: 'Python',
          stars: '2k+',
          license: 'BSD-3-Clause',
          applications: ['EEG/MEG analysis', 'Brain signal processing', 'Neurofeedback']
        },
        brian: {
          url: 'https://github.com/brian-team/brian2',
          description: 'Spiking neural network simulator',
          type: 'simulator',
          language: 'Python',
          stars: '900+',
          license: 'MIT',
          applications: ['Neural modeling', 'Brain simulation', 'Computational neuroscience']
        }
      },

      // Chemistry & Materials Science
      chemistry: {
        rdkit: {
          url: 'https://github.com/rdkit/rdkit',
          description: 'Cheminformatics and machine learning software',
          type: 'library',
          language: 'C++/Python',
          stars: '3k+',
          license: 'BSD-3-Clause',
          applications: ['Drug discovery', 'Molecular analysis', 'Chemical informatics']
        },
        openmm: {
          url: 'https://github.com/openmm/openmm',
          description: 'High performance toolkit for molecular simulation',
          type: 'library',
          language: 'C++/Python',
          stars: '800+',
          license: 'MIT',
          applications: ['Protein folding', 'Drug design', 'Molecular dynamics']
        },
        materials: {
          url: 'https://github.com/materialsproject/pymatgen',
          description: 'Python Materials Genomics',
          type: 'library',
          language: 'Python',
          stars: '1k+',
          license: 'MIT',
          applications: ['Materials discovery', 'Crystal structure', 'Battery research']
        }
      },

      // Education & Research Tools
      education: {
        jupyter_lab: {
          url: 'https://github.com/jupyterlab/jupyterlab',
          description: 'Next-generation user interface for Jupyter notebooks',
          type: 'platform',
          language: 'TypeScript/Python',
          stars: '14k+',
          license: 'BSD-3-Clause',
          applications: ['Research notebooks', 'Data visualization', 'Interactive computing']
        },
        r_studio: {
          url: 'https://github.com/rstudio/rstudio',
          description: 'Integrated development environment for R',
          type: 'ide',
          language: 'C++/JavaScript',
          stars: '5k+',
          license: 'AGPL-3.0',
          applications: ['Statistical analysis', 'Data science', 'Research publishing']
        },
        zotero: {
          url: 'https://github.com/zotero/zotero',
          description: 'Personal research assistant',
          type: 'tool',
          language: 'JavaScript',
          stars: '10k+',
          license: 'AGPL-3.0',
          applications: ['Reference management', 'Research organization', 'Citation formatting']
        }
      }
    };

    // Global research initiatives
    const researchInitiatives = {
      openScience: [
        'Open Access Publishing',
        'Reproducible Research',
        'Data Sharing Platforms',
        'Collaborative Research Networks'
      ],
      globalChallenges: [
        'Climate Change Research',
        'Pandemic Preparedness',
        'Food Security',
        'Renewable Energy',
        'Biodiversity Conservation'
      ],
      emergingFields: [
        'Synthetic Biology',
        'Quantum Biology',
        'Digital Health',
        'Precision Medicine',
        'Brain-Computer Interfaces'
      ]
    };

    // Filter by field if specified
    let responseData;
    if (field && lifeSciencesResources[field as keyof typeof lifeSciencesResources]) {
      responseData = {
        field,
        resources: lifeSciencesResources[field as keyof typeof lifeSciencesResources],
        totalInField: Object.keys(lifeSciencesResources[field as keyof typeof lifeSciencesResources]).length
      };
    } else {
      responseData = {
        allFields: lifeSciencesResources,
        researchInitiatives,
        totalFields: Object.keys(lifeSciencesResources).length,
        totalResources: Object.values(lifeSciencesResources).reduce((acc, field) => acc + Object.keys(field).length, 0)
      };
    }

    return NextResponse.json({
      status: 'success',
      data: responseData,
      metadata: {
        endpoint: '/api/life-sciences-hub',
        version: '1.0.0',
        timestamp: new Date().toISOString(),
        message: 'Burime nga të gjitha fushat e jetës - shkencë, mjekësi, mjedis, bujqësi dhe më shumë!'
      }
    });

  } catch (error) {
    return NextResponse.json({
      status: 'error',
      message: 'Failed to fetch life sciences resources',
      error: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 });
  }
}
