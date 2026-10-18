/**
 * AGI×Med Professional Access Portal
 * Controlled Professional Entry for Licensed Medical Professionals
 * 
 * @author UltraWeb Medical Team
 * @version 8.0.0-MEDICAL-PROFESSIONAL
 * @compliance HIPAA, GDPR, HL7-FHIR
 */

'use client';

import { useState } from 'react';
import { Shield, Lock, FileCheck, Users, Phone, Mail, AlertTriangle, CheckCircle, Building2, Microscope, Stethoscope, Heart, Brain, Activity } from 'lucide-react';

interface MedicalSystem {
  id: string;
  name: string;
  description: string;
  status: 'active' | 'restricted' | 'maintenance';
  accuracy: number;
  icon: unknown;
  requirements: string[];
}

export default function AGIMedProfessionalPortal() {
  const [selectedSystem, setSelectedSystem] = useState<string | null>(null);
  
  const medicalSystems: MedicalSystem[] = [
    {
      id: 'clinical-diagnostics',
      name: 'Clinical Diagnostics AI',
      description: 'Advanced clinical imaging analysis for licensed radiologists',
      status: 'active',
      accuracy: 99.8,
      icon: Microscope,
      requirements: ['Radiology License', 'Hospital Affiliation', 'DICOM Certification']
    },
    {
      id: 'clinical-pharmacology',
      name: 'Clinical Pharmacology',
      description: 'Drug interaction analysis and personalized dosing protocols',
      status: 'active',
      accuracy: 98.7,
      icon: Heart,
      requirements: ['Pharmacy License', 'Clinical Experience', 'Drug Safety Training']
    },
    {
      id: 'clinical-research',
      name: 'Clinical Research Analytics',
      description: 'Statistical analysis for clinical trials and medical research',
      status: 'active',
      accuracy: 97.9,
      icon: Activity,
      requirements: ['Research License', 'IRB Approval', 'Statistical Training']
    },
    {
      id: 'surgical-planning',
      name: 'Surgical Planning AI',
      description: 'Advanced surgical planning and outcome prediction',
      status: 'restricted',
      accuracy: 99.1,
      icon: Brain,
      requirements: ['Surgical License', 'Board Certification', 'Hospital Privileges']
    }
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return '#00ff00';
      case 'restricted': return '#ff6b00';
      case 'maintenance': return '#ff0000';
      default: return '#666';
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'active': return 'Aktiv';
      case 'restricted': return 'I Kufizuar';
      case 'maintenance': return 'Mirëmbajtje';
      default: return 'Panjohur';
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      background: `
        radial-gradient(circle at 20% 30%, #0066cc11 0%, transparent 50%),
        radial-gradient(circle at 80% 70%, #00cc6611 0%, transparent 50%),
        linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #16213e 100%)
      `,
      color: 'white',
      fontFamily: '"Inter", -apple-system, BlinkMacSystemFont, sans-serif'
    }}>
      
      {/* Header */}
      <div style={{
        background: 'linear-gradient(90deg, #1e3a8a, #1e40af, #0066cc)',
        padding: '2rem 0',
        borderBottom: '2px solid #0066cc'
      }}>
        <div style={{
          maxWidth: '1200px',
          margin: '0 auto',
          padding: '0 2rem',
          textAlign: 'center'
        }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '1rem',
            marginBottom: '1rem'
          }}>
            <Shield size={48} style={{ color: '#00ff00' }} />
            <h1 style={{
              fontSize: '3rem',
              fontWeight: 900,
              background: 'linear-gradient(45deg, #00ff00, #0066cc)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              margin: 0
            }}>
              AGI×Med
            </h1>
          </div>
          <p style={{
            fontSize: '1.25rem',
            color: '#e5e7eb',
            margin: 0
          }}>
            Hyrje e Kontrolluar Profesionale
          </p>
          <p style={{
            fontSize: '1rem',
            color: '#9ca3af',
            marginTop: '0.5rem'
          }}>
            I kufizuar vetëm për profesionistë të licencuar mjekësorë, klinika të akredituara dhe laboratorë të certifikuar
          </p>
        </div>
      </div>

      <div style={{
        maxWidth: '1200px',
        margin: '0 auto',
        padding: '3rem 2rem'
      }}>
        
        {/* Access Requirements */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
          gap: '2rem',
          marginBottom: '3rem'
        }}>
          
          {/* Entry Requirements */}
          <div style={{
            background: 'rgba(30, 58, 138, 0.2)',
            border: '1px solid #0066cc',
            borderRadius: '12px',
            padding: '2rem'
          }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.75rem',
              marginBottom: '1.5rem'
            }}>
              <FileCheck size={24} style={{ color: '#00ff00' }} />
              <h3 style={{
                fontSize: '1.25rem',
                fontWeight: 700,
                color: '#00ff00',
                margin: 0
              }}>
                📋 Kërkesat për Hyrje
              </h3>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {[
                'Licencë mjekësore e vlefshme',
                'Certifikatë profesionale',
                'Verifikim institucional',
                'Dokumentacion i plotë'
              ].map((requirement, index) => (
                <div key={index} style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                  marginBottom: '0.75rem'
                }}>
                  <CheckCircle size={16} style={{ color: '#00ff00' }} />
                  <span style={{ color: '#e5e7eb' }}>✓ {requirement}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Accepted Institutions */}
          <div style={{
            background: 'rgba(0, 102, 204, 0.2)',
            border: '1px solid #0066cc',
            borderRadius: '12px',
            padding: '2rem'
          }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.75rem',
              marginBottom: '1.5rem'
            }}>
              <Building2 size={24} style={{ color: '#0066cc' }} />
              <h3 style={{
                fontSize: '1.25rem',
                fontWeight: 700,
                color: '#0066cc',
                margin: 0
              }}>
                🏥 Institucione të Pranuara
              </h3>
            </div>
            <div>
              {[
                'Spitale publike/private',
                'Klinika të specializuara',
                'Laboratorë diagnostikë',
                'Qendra kërkimore'
              ].map((institution, index) => (
                <div key={index} style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                  marginBottom: '0.75rem'
                }}>
                  <CheckCircle size={16} style={{ color: '#0066cc' }} />
                  <span style={{ color: '#e5e7eb' }}>✓ {institution}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Medical Systems */}
        <div style={{ marginBottom: '3rem' }}>
          <h2 style={{
            fontSize: '2rem',
            fontWeight: 700,
            color: '#ffffff',
            marginBottom: '2rem',
            textAlign: 'center'
          }}>
            🔬 Sistemet Mjekësore AGI
          </h2>
          
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
            gap: '1.5rem'
          }}>
            {medicalSystems.map((system) => (
              <div
                key={system.id}
                style={{
                  background: selectedSystem === system.id ? 
                    'rgba(0, 255, 0, 0.1)' : 
                    'rgba(255, 255, 255, 0.05)',
                  border: selectedSystem === system.id ? 
                    '2px solid #00ff00' : 
                    '1px solid rgba(255, 255, 255, 0.1)',
                  borderRadius: '12px',
                  padding: '1.5rem',
                  cursor: 'pointer',
                  transition: 'all 0.3s ease'
                }}
                onClick={() => setSelectedSystem(selectedSystem === system.id ? null : system.id)}
                onMouseEnter={(e) => {
                  if (selectedSystem !== system.id) {
                    e.currentTarget.style.background = 'rgba(255, 255, 255, 0.08)';
                    e.currentTarget.style.transform = 'translateY(-2px)';
                  }
                }}
                onMouseLeave={(e) => {
                  if (selectedSystem !== system.id) {
                    e.currentTarget.style.background = 'rgba(255, 255, 255, 0.05)';
                    e.currentTarget.style.transform = 'translateY(0)';
                  }
                }}
              >
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '1rem',
                  marginBottom: '1rem'
                }}>
                  <system.icon size={32} style={{ color: getStatusColor(system.status) }} />
                  <div style={{ flex: 1 }}>
                    <h3 style={{
                      fontSize: '1.125rem',
                      fontWeight: 600,
                      color: '#ffffff',
                      margin: 0,
                      marginBottom: '0.25rem'
                    }}>
                      {system.name}
                    </h3>
                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.5rem'
                    }}>
                      <span style={{
                        fontSize: '0.75rem',
                        padding: '0.25rem 0.5rem',
                        borderRadius: '4px',
                        background: getStatusColor(system.status) + '22',
                        color: getStatusColor(system.status),
                        fontWeight: 600
                      }}>
                        {getStatusLabel(system.status)}
                      </span>
                      <span style={{
                        fontSize: '0.75rem',
                        color: '#9ca3af'
                      }}>
                        {system.accuracy}%
                      </span>
                    </div>
                  </div>
                </div>
                
                <p style={{
                  fontSize: '0.875rem',
                  color: '#d1d5db',
                  marginBottom: '1rem',
                  lineHeight: 1.5
                }}>
                  {system.description}
                </p>
                
                {selectedSystem === system.id && (
                  <div style={{
                    background: 'rgba(0, 0, 0, 0.3)',
                    borderRadius: '8px',
                    padding: '1rem',
                    marginTop: '1rem'
                  }}>
                    <h4 style={{
                      fontSize: '0.875rem',
                      fontWeight: 600,
                      color: '#ffffff',
                      marginBottom: '0.5rem'
                    }}>
                      Kërkesat e Qasjes:
                    </h4>
                    {system.requirements.map((req, index) => (
                      <div key={index} style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.5rem',
                        marginBottom: '0.25rem'
                      }}>
                        <Lock size={12} style={{ color: '#fbbf24' }} />
                        <span style={{
                          fontSize: '0.75rem',
                          color: '#e5e7eb'
                        }}>
                          {req}
                        </span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Security & Privacy */}
        <div style={{
          background: 'rgba(0, 0, 0, 0.3)',
          border: '1px solid #374151',
          borderRadius: '12px',
          padding: '2rem',
          marginBottom: '3rem'
        }}>
          <h2 style={{
            fontSize: '1.5rem',
            fontWeight: 700,
            color: '#ffffff',
            marginBottom: '1.5rem',
            textAlign: 'center'
          }}>
            🛡️ Siguria dhe Privatësia
          </h2>
          <p style={{
            textAlign: 'center',
            color: '#9ca3af',
            marginBottom: '2rem'
          }}>
            AGI×Med respekton standardet më të larta të sigurisë dhe privatësisë mjekësore
          </p>
          
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: '1.5rem'
          }}>
            {[
              { icon: '🔐', title: 'HIPAA Compliant', desc: 'Përputhshmëri e plotë me standardet ndërkombëtare' },
              { icon: '🏥', title: 'HL7 FHIR', desc: 'Integrim me sistemet e spitaleve' },
              { icon: '🌍', title: 'GDPR Ready', desc: 'Mbrojtje e të dhënave personale' },
              { icon: '🔒', title: 'End-to-End', desc: 'Enkriptim i plotë i të dhënave' }
            ].map((item, index) => (
              <div key={index} style={{
                textAlign: 'center',
                padding: '1rem'
              }}>
                <div style={{
                  fontSize: '2rem',
                  marginBottom: '0.5rem'
                }}>
                  {item.icon}
                </div>
                <h3 style={{
                  fontSize: '1rem',
                  fontWeight: 600,
                  color: '#ffffff',
                  marginBottom: '0.5rem'
                }}>
                  {item.title}
                </h3>
                <p style={{
                  fontSize: '0.75rem',
                  color: '#9ca3af',
                  lineHeight: 1.4
                }}>
                  {item.desc}
                </p>
              </div>
            ))}
          </div>
        </div>

        {/* Professional Application */}
        <div style={{
          background: 'linear-gradient(135deg, rgba(0, 102, 204, 0.2), rgba(0, 255, 0, 0.1))',
          border: '2px solid #0066cc',
          borderRadius: '12px',
          padding: '2rem',
          textAlign: 'center',
          marginBottom: '3rem'
        }}>
          <AlertTriangle size={48} style={{ color: '#fbbf24', marginBottom: '1rem' }} />
          <h2 style={{
            fontSize: '1.5rem',
            fontWeight: 700,
            color: '#ffffff',
            marginBottom: '1rem'
          }}>
            🔐 Aplikoni për Qasje Profesionale
          </h2>
          <p style={{
            color: '#d1d5db',
            marginBottom: '2rem',
            fontSize: '1rem'
          }}>
            📞 Kontaktoni Administratën
          </p>
          
          <button style={{
            background: 'linear-gradient(135deg, #0066cc, #00ff00)',
            border: 'none',
            borderRadius: '8px',
            padding: '1rem 2rem',
            color: 'white',
            fontSize: '1rem',
            fontWeight: 600,
            cursor: 'pointer',
            transition: 'all 0.3s ease'
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.transform = 'translateY(-2px)';
            e.currentTarget.style.boxShadow = '0 10px 25px rgba(0, 102, 204, 0.3)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.transform = 'translateY(0)';
            e.currentTarget.style.boxShadow = 'none';
          }}>
            Aplikoni Tani
          </button>
        </div>

        {/* Contact Information */}
        <div style={{
          background: 'rgba(255, 255, 255, 0.05)',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          borderRadius: '12px',
          padding: '2rem'
        }}>
          <h2 style={{
            fontSize: '1.5rem',
            fontWeight: 700,
            color: '#ffffff',
            marginBottom: '1.5rem',
            textAlign: 'center'
          }}>
            Për Informacion Profesional
          </h2>
          <p style={{
            textAlign: 'center',
            color: '#9ca3af',
            marginBottom: '2rem'
          }}>
            Kontaktoni departamentin tonë të marrëdhënieve me profesionistët mjekësorë
          </p>
          
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
            gap: '1.5rem'
          }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '1rem',
              padding: '1rem',
              background: 'rgba(0, 0, 0, 0.2)',
              borderRadius: '8px'
            }}>
              <Mail size={24} style={{ color: '#0066cc' }} />
              <div>
                <div style={{ fontSize: '0.875rem', color: '#9ca3af' }}>📧 Email</div>
                <div style={{ fontWeight: 600, color: '#ffffff' }}>medical-professionals@euroweb.al</div>
              </div>
            </div>
            
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '1rem',
              padding: '1rem',
              background: 'rgba(0, 0, 0, 0.2)',
              borderRadius: '8px'
            }}>
              <Phone size={24} style={{ color: '#00ff00' }} />
              <div>
                <div style={{ fontSize: '0.875rem', color: '#9ca3af' }}>📞 Telefon</div>
                <div style={{ fontWeight: 600, color: '#ffffff' }}>+355 4X XXX XXX</div>
              </div>
            </div>
            
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '1rem',
              padding: '1rem',
              background: 'rgba(0, 0, 0, 0.2)',
              borderRadius: '8px'
            }}>
              <Stethoscope size={24} style={{ color: '#fbbf24' }} />
              <div>
                <div style={{ fontSize: '0.875rem', color: '#9ca3af' }}>🏥 Departamenti</div>
                <div style={{ fontWeight: 600, color: '#ffffff' }}>Departamenti Mjekësor</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
