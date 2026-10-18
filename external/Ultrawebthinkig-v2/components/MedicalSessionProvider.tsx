'use client';

/**
 * 🏥 MEDICAL SESSION PROVIDER
 * Client-side context for medical sessions
 * HIPAA Compliant • Medical Grade Security
 */

import * as React from 'react';

// ==================== TYPES & INTERFACES ====================
interface MedicalProfessional {
  readonly id: string;
  readonly licenseNumber: string;
  readonly specialization: MedicalSpecialization;
  readonly institution: MedicalInstitution;
  readonly accessLevel: AccessLevel;
  readonly credentials: ProfessionalCredentials;
  readonly lastVerification: Date;
}

interface MedicalInstitution {
  readonly id: string;
  readonly name: string;
  readonly type: 'hospital' | 'clinic' | 'research' | 'laboratory';
  readonly accreditation: AccreditationStatus;
  readonly hipaaCompliant: boolean;
}

interface ProfessionalCredentials {
  readonly medicalLicense: string;
  readonly deaNumber?: string;
  readonly boardCertifications: string[];
  readonly education: MedicalEducation[];
  readonly malpracticeInsurance: InsuranceStatus;
}

interface MedicalSession {
  readonly sessionId: string;
  readonly professional: MedicalProfessional;
  readonly accessScope: AccessScope;
  readonly securityContext: MedicalSecurityContext;
  readonly auditTrail: AuditEntry[];
  readonly startTime: Date;
}

interface MedicalSecurityContext {
  readonly encryptionLevel: 'hipaa' | 'military' | 'quantum';
  readonly authentication: MultiFactorAuth;
  readonly sessionTimeout: number;
  readonly threatDetection: ThreatMonitoring;
  readonly compliance: ComplianceStatus;
}

// ==================== CONTEXT & HOOKS ====================
const MedicalSessionContext = React.createContext<MedicalSession | null>(null);

export const useMedicalSession = (): MedicalSession => {
  const session = React.useContext(MedicalSessionContext);
  if (!session) {
    throw new Error('useMedicalSession must be used within MedicalSessionProvider');
  }
  return session;
};

// ==================== PROVIDER COMPONENT ====================
interface MedicalSessionProviderProps {
  children: React.ReactNode;
  session: MedicalSession | null;
}

export const MedicalSessionProvider: React.FC<MedicalSessionProviderProps> = ({
  children,
  session
}: MedicalSessionProviderProps) => {
  return (
    <MedicalSessionContext.Provider value={session}>
      {children}
    </MedicalSessionContext.Provider>
  );
};

// ==================== TYPE EXPORTS ====================
export type {
  MedicalSession,
  MedicalProfessional,
  ProfessionalCredentials,
  MedicalInstitution,
  MedicalSecurityContext
};

// Type definitions
type MedicalSpecialization =
  | 'internal_medicine'
  | 'surgery'
  | 'radiology'
  | 'pathology'
  | 'pediatrics'
  | 'psychiatry';

type AccessLevel =
  | 'general_medical'
  | 'diagnostic_imaging'
  | 'laboratory_analysis'
  | 'surgical_planning';

type AccessScope = {
  patientData: boolean;
  medicalImaging: boolean;
  labResults: boolean;
  treatmentPlans: boolean;
  researchData: boolean;
  administrative: boolean;
};

type AccreditationStatus = 'joint_commission' | 'cms' | 'state' | 'none';
type InsuranceStatus = 'active' | 'expired' | 'none';
type MultiFactorAuth = { enabled: boolean; methods: string[] };
type ThreatMonitoring = { enabled: boolean; level: 'basic' | 'advanced' | 'maximum' };
type ComplianceStatus = { hipaa: boolean; hitrust: boolean; soc2: boolean };

interface MedicalEducation {
  institution: string;
  degree: string;
  year: number;
}

interface AuditEntry {
  id: string;
  timestamp: Date;
  action: string;
  details: any;
  ipAddress: string;
  userAgent: string;
}
