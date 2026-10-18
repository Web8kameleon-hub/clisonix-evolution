'use client'

import React, { useState } from 'react'
import AlbanianWordProcessor from '@/components/AlbanianDocuments/AlbanianWordProcessor'
import AlbanianSpreadsheet from '@/components/AlbanianDocuments/AlbanianSpreadsheet'
import AlbanianFormCreator from '@/components/AlbanianDocuments/AlbanianFormCreator'
import AlbanianLetterTemplate from '@/components/AlbanianDocuments/AlbanianLetterTemplate'

interface DocumentType {
  id: string
  name: string
  nameEn: string
  description: string
  icon: string
  component: React.ComponentType
}

const documentTypes: DocumentType[] = [
  {
    id: 'word',
    name: 'Dokument Teksti',
    nameEn: 'Word Document',
    description: 'Krijim dokumentesh me format tradicional shqiptar',
    icon: '📄',
    component: AlbanianWordProcessor
  },
  {
    id: 'spreadsheet',
    name: 'Tabelë/Excel',
    nameEn: 'Spreadsheet',
    description: 'Tabelat e llogaritjes dhe analizës së të dhënave',
    icon: '📊',
    component: AlbanianSpreadsheet
  },
  {
    id: 'forms',
    name: 'Formularë Zyrtarë',
    nameEn: 'Official Forms',
    description: 'Krijim formularësh me standardet shqiptare',
    icon: '📋',
    component: AlbanianFormCreator
  },
  {
    id: 'letters',
    name: 'Letra & Komunikime',
    nameEn: 'Letters & Communications',
    description: 'Shabllone për letra zyrtare dhe private',
    icon: '✉️',
    component: AlbanianLetterTemplate
  }
]

export const AlbanianDocumentSuite: React.FC = () => {
  const [activeDocument, setActiveDocument] = useState<string | null>(null)
  const [recentDocuments, setRecentDocuments] = useState<string[]>([])

  const ActiveComponent = activeDocument 
    ? documentTypes.find(doc => doc.id === activeDocument)?.component
    : null

  return (
    <div className="min-h-screen bg-gradient-to-br from-red-50 via-white to-red-50">
      {/* Header me flamurin shqiptar */}
      <header className="bg-gradient-to-r from-red-600 to-red-700 text-white p-6 shadow-xl">
        <div className="container mx-auto">
          <div className="flex items-center space-x-4">
            <div className="text-4xl">🇦🇱</div>
            <div>
              <h1 className="text-3xl font-bold">Suite Dokumentesh Shqiptare</h1>
              <p className="text-red-100">Krijim dokumentesh me format tradicional dhe modern</p>
            </div>
          </div>
        </div>
      </header>

      {!activeDocument ? (
        <main className="container mx-auto px-6 py-12">
          {/* Welcome Section */}
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold text-gray-800 mb-4">
              Mirë se erdhët në Suite-in e Dokumenteve
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Një platformë e plotë për krijimin e dokumenteve me format tradicional shqiptar. 
              Ruajmë traditën, përqafojmë teknologjinë moderne.
            </p>
          </div>

          {/* Document Types Grid */}
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8 mb-12">
            {documentTypes.map((docType) => (
              <div
                key={docType.id}
                onClick={() => setActiveDocument(docType.id)}
                className="bg-white rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 cursor-pointer transform hover:scale-105 border-2 border-transparent hover:border-red-200"
              >
                <div className="p-8 text-center">
                  <div className="text-5xl mb-4">{docType.icon}</div>
                  <h3 className="text-xl font-bold text-gray-800 mb-2">
                    {docType.name}
                  </h3>
                  <p className="text-sm text-gray-500 mb-3">{docType.nameEn}</p>
                  <p className="text-gray-600">{docType.description}</p>
                </div>
              </div>
            ))}
          </div>

          {/* Features Section */}
          <div className="bg-white rounded-xl shadow-lg p-8">
            <h3 className="text-2xl font-bold text-gray-800 mb-6 text-center">
              Karakteristikat e Platformës
            </h3>
            <div className="grid md:grid-cols-3 gap-6">
              <div className="text-center">
                <div className="text-3xl mb-3">🎨</div>
                <h4 className="font-bold text-lg mb-2">Format Tradicional</h4>
                <p className="text-gray-600">
                  Ruajmë standardet e vjetra shqiptare të dokumenteve zyrtare
                </p>
              </div>
              <div className="text-center">
                <div className="text-3xl mb-3">🌐</div>
                <h4 className="font-bold text-lg mb-2">Teknologji Moderne</h4>
                <p className="text-gray-600">
                  Platformë web e avancuar me veçori bashkëkohore
                </p>
              </div>
              <div className="text-center">
                <div className="text-3xl mb-3">📱</div>
                <h4 className="font-bold text-lg mb-2">Multi-Platform</h4>
                <p className="text-gray-600">
                  Punon në të gjitha pajisjet - desktop, tablet, mobile
                </p>
              </div>
            </div>
          </div>

          {/* Recent Documents */}
          {recentDocuments.length > 0 && (
            <div className="mt-12">
              <h3 className="text-2xl font-bold text-gray-800 mb-6">
                Dokumentet e Fundit
              </h3>
              <div className="grid md:grid-cols-3 gap-4">
                {recentDocuments.map((doc, index) => (
                  <div key={index} className="bg-white rounded-lg shadow p-4 hover:shadow-md transition-shadow">
                    <div className="flex items-center space-x-3">
                      <div className="text-2xl">📄</div>
                      <div>
                        <p className="font-medium">{doc}</p>
                        <p className="text-sm text-gray-500">Sot në {new Date().toLocaleTimeString('sq-AL')}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </main>
      ) : (
        <div className="min-h-screen">
          {/* Document Editor Header */}
          <div className="bg-white border-b shadow-sm p-4">
            <div className="container mx-auto flex items-center justify-between">
              <button
                onClick={() => setActiveDocument(null)}
                className="flex items-center space-x-2 text-gray-600 hover:text-red-600 transition-colors"
              >
                <span>←</span>
                <span>Kthehu në fillim</span>
              </button>
              <h2 className="text-xl font-bold text-gray-800">
                {documentTypes.find(doc => doc.id === activeDocument)?.name}
              </h2>
              <div className="flex space-x-2">
                <button className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors">
                  Ruaj
                </button>
                <button className="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition-colors">
                  Eksporto
                </button>
              </div>
            </div>
          </div>

          {/* Active Document Component */}
          <div className="container mx-auto">
            {ActiveComponent && <ActiveComponent />}
          </div>
        </div>
      )}
    </div>
  )
}

export default AlbanianDocumentSuite
