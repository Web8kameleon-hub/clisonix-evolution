'use client'

import React, { useState } from 'react'

interface FormField {
  id: string
  type: 'text' | 'number' | 'date' | 'select' | 'checkbox' | 'textarea' | 'signature'
  label: string
  required: boolean
  options?: string[]
  value?: string
  placeholder?: string
  validation?: {
    min?: number
    max?: number
    pattern?: string
  }
}

interface FormTemplate {
  name: string
  description: string
  fields: FormField[]
  category: 'administrative' | 'business' | 'personal' | 'legal'
}

const albanianFormTemplates: FormTemplate[] = [
  {
    name: 'Aplikim për Leje Qëndrimi',
    description: 'Formular zyrtar për aplikim leje qëndrimi në Shqipëri',
    category: 'administrative',
    fields: [
      { id: 'emri', type: 'text', label: 'Emri', required: true },
      { id: 'mbiemri', type: 'text', label: 'Mbiemri', required: true },
      { id: 'emriAtit', type: 'text', label: 'Emri i Atit', required: true },
      { id: 'emriNenes', type: 'text', label: 'Emri i Nënës', required: true },
      { id: 'datalindjes', type: 'date', label: 'Data e Lindjes', required: true },
      { id: 'vendlindja', type: 'text', label: 'Vendi i Lindjes', required: true },
      { id: 'kombesia', type: 'select', label: 'Kombësia', required: true, 
        options: ['Shqiptare', 'Italiane', 'Greke', 'Maqedonase', 'Të tjera'] },
      { id: 'adresa', type: 'textarea', label: 'Adresa e Banimit', required: true },
      { id: 'telefoni', type: 'text', label: 'Numri i Telefonit', required: true },
      { id: 'email', type: 'text', label: 'Email', required: false },
      { id: 'qellimi', type: 'select', label: 'Qëllimi i Qëndrimit', required: true,
        options: ['Punë', 'Studime', 'Familje', 'Investime', 'Tjetër'] },
      { id: 'data', type: 'date', label: 'Data e Aplikimit', required: true },
      { id: 'nenshkrimi', type: 'signature', label: 'Nënshkrimi i Aplikuesit', required: true }
    ]
  },
  {
    name: 'Kontratë Qiraje',
    description: 'Kontratë standarde për qira prone në Shqipëri',
    category: 'legal',
    fields: [
      { id: 'pronariEmri', type: 'text', label: 'Emri i Pronarit', required: true },
      { id: 'pronariAdresa', type: 'textarea', label: 'Adresa e Pronarit', required: true },
      { id: 'qiramaresiEmri', type: 'text', label: 'Emri i Qiramarrësit', required: true },
      { id: 'qiramaresiAdresa', type: 'textarea', label: 'Adresa e Qiramarrësit', required: true },
      { id: 'prona', type: 'textarea', label: 'Përshkrimi i Pronës', required: true },
      { id: 'çmimi', type: 'number', label: 'Çmimi Mujor (ALL)', required: true },
      { id: 'afati', type: 'select', label: 'Afati i Kontratës', required: true,
        options: ['6 muaj', '1 vit', '2 vjet', '3 vjet', 'Afatgjatë'] },
      { id: 'dataFillimi', type: 'date', label: 'Data e Fillimit', required: true },
      { id: 'dataMbarimi', type: 'date', label: 'Data e Mbarimit', required: true },
      { id: 'kushtet', type: 'textarea', label: 'Kushte të Veçanta', required: false },
      { id: 'garantia', type: 'number', label: 'Shuma e Garancisë (ALL)', required: true },
      { id: 'nenshkrimiPronari', type: 'signature', label: 'Nënshkrimi i Pronarit', required: true },
      { id: 'nenshkrimiQiramarresi', type: 'signature', label: 'Nënshkrimi i Qiramarrësit', required: true }
    ]
  },
  {
    name: 'Aplikim për Punë',
    description: 'Formular aplikimi për pozicione pune',
    category: 'business',
    fields: [
      { id: 'emriMbiemri', type: 'text', label: 'Emri dhe Mbiemri', required: true },
      { id: 'datalindjes', type: 'date', label: 'Data e Lindjes', required: true },
      { id: 'adresa', type: 'textarea', label: 'Adresa', required: true },
      { id: 'telefoni', type: 'text', label: 'Telefoni', required: true },
      { id: 'email', type: 'text', label: 'Email', required: true },
      { id: 'pozicioni', type: 'text', label: 'Pozicioni i Kërkuar', required: true },
      { id: 'arsimimi', type: 'select', label: 'Niveli i Arsimimit', required: true,
        options: ['8/9-vjeçare', 'Gjimnaz', 'Universitet', 'Master', 'Doktoratë'] },
      { id: 'pervoja', type: 'number', label: 'Vitet e Përvojës', required: true },
      { id: 'aftesit', type: 'textarea', label: 'Aftësitë dhe Njohuritë', required: true },
      { id: 'gjuhet', type: 'textarea', label: 'Gjuhët e Huaja', required: false },
      { id: 'referenca', type: 'textarea', label: 'Referenca', required: false },
      { id: 'disponueshmeria', type: 'select', label: 'Disponueshmëria', required: true,
        options: ['Menjëherë', 'Brenda 1 muaji', 'Brenda 2 muajsh', 'Për t\'u diskutuar'] },
      { id: 'nenshkrimi', type: 'signature', label: 'Nënshkrimi', required: true }
    ]
  },
  {
    name: 'Ankesë Zyrtare',
    description: 'Formular për paraqitjen e ankesave zyrtare',
    category: 'administrative',
    fields: [
      { id: 'emriAnkuesi', type: 'text', label: 'Emri i Ankuesit', required: true },
      { id: 'adresa', type: 'textarea', label: 'Adresa', required: true },
      { id: 'telefoni', type: 'text', label: 'Telefoni', required: true },
      { id: 'institucioni', type: 'text', label: 'Institucioni ndaj të cilit drejtohet ankesa', required: true },
      { id: 'objekti', type: 'text', label: 'Objekti i Ankesës', required: true },
      { id: 'pershkrimi', type: 'textarea', label: 'Përshkrimi i Detajuar i Ankesës', required: true },
      { id: 'dokumentet', type: 'text', label: 'Dokumentet Bashkëlidhur', required: false },
      { id: 'zgjidhja', type: 'textarea', label: 'Zgjidhja e Kërkuar', required: true },
      { id: 'dataParaqitjes', type: 'date', label: 'Data e Paraqitjes', required: true },
      { id: 'nenshkrimi', type: 'signature', label: 'Nënshkrimi i Ankuesit', required: true }
    ]
  }
]

export const AlbanianFormCreator: React.FC = () => {
  const [selectedTemplate, setSelectedTemplate] = useState<FormTemplate | null>(null)
  const [formData, setFormData] = useState<{ [key: string]: string }>({})
  const [isPreview, setIsPreview] = useState(false)
  const [customForm, setCustomForm] = useState<FormField[]>([])
  const [showTemplates, setShowTemplates] = useState(true)

  const handleFieldChange = (fieldId: string, value: string) => {
    setFormData(prev => ({
      ...prev,
      [fieldId]: value
    }))
  }

  const addCustomField = () => {
    const newField: FormField = {
      id: `field_${Date.now()}`,
      type: 'text',
      label: 'Fusha e Re',
      required: false
    }
    setCustomForm(prev => [...prev, newField])
  }

  const updateCustomField = (index: number, field: Partial<FormField>) => {
    setCustomForm(prev => prev.map((f, i) => i === index ? { ...f, ...field } : f))
  }

  const removeCustomField = (index: number) => {
    setCustomForm(prev => prev.filter((_, i) => i !== index))
  }

  const exportToPDF = () => {
    window.print()
  }

  const saveForm = () => {
    const formContent = {
      template: selectedTemplate?.name || 'Formular i Personalizuar',
      data: formData,
      timestamp: new Date().toISOString()
    }
    
    const blob = new Blob([JSON.stringify(formContent, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${formContent.template.replace(/\s+/g, '_')}.json`
    a.click()
  }

  const renderField = (field: FormField) => {
    const value = formData[field.id] || ''
    const fieldClass = "w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent"

    switch (field.type) {
      case 'text':
        return (
          <input
            type="text"
            value={value}
            onChange={(e) => handleFieldChange(field.id, e.target.value)}
            placeholder={field.placeholder}
            className={fieldClass}
            required={field.required}
          />
        )
      
      case 'number':
        return (
          <input
            type="number"
            value={value}
            onChange={(e) => handleFieldChange(field.id, e.target.value)}
            className={fieldClass}
            required={field.required}
          />
        )
      
      case 'date':
        return (
          <input
            type="date"
            value={value}
            onChange={(e) => handleFieldChange(field.id, e.target.value)}
            className={fieldClass}
            required={field.required}
          />
        )
      
      case 'select':
        return (
          <select
            value={value}
            onChange={(e) => handleFieldChange(field.id, e.target.value)}
            className={fieldClass}
            required={field.required}
          >
            <option value="">Zgjidhni...</option>
            {field.options?.map((option, index) => (
              <option key={index} value={option}>{option}</option>
            ))}
          </select>
        )
      
      case 'textarea':
        return (
          <textarea
            value={value}
            onChange={(e) => handleFieldChange(field.id, e.target.value)}
            placeholder={field.placeholder}
            className={`${fieldClass} h-24 resize-vertical`}
            required={field.required}
          />
        )
      
      case 'checkbox':
        return (
          <label className="flex items-center space-x-2 cursor-pointer">
            <input
              type="checkbox"
              checked={value === 'true'}
              onChange={(e) => handleFieldChange(field.id, e.target.checked.toString())}
              className="w-4 h-4 text-red-600 border-gray-300 rounded focus:ring-red-500"
            />
            <span>Po, pranoj</span>
          </label>
        )
      
      case 'signature':
        return (
          <div className="border-2 border-dashed border-gray-300 p-8 text-center">
            <div className="text-gray-500 mb-2">Zona e Nënshkrimit</div>
            <div className="text-sm text-gray-400">
              {value ? 'Nënshkruar' : 'Klikoni për të nënshkruar'}
            </div>
            {!value && (
              <button
                type="button"
                onClick={() => handleFieldChange(field.id, `Nënshkruar më ${new Date().toLocaleDateString('sq-AL')}`)}
                className="mt-2 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
              >
                Nënshkruaj
              </button>
            )}
          </div>
        )
      
      default:
        return null
    }
  }

  if (showTemplates) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-red-50 to-gray-50 p-6">
        <div className="max-w-6xl mx-auto">
          {/* Header */}
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-gray-800 mb-4">
              🇦🇱 Krijuesi i Formularëve Shqiptarë
            </h1>
            <p className="text-xl text-gray-600">
              Krijoni dhe plotësoni formularë zyrtarë me standardet shqiptare
            </p>
          </div>

          {/* Template Categories */}
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            {Object.entries(
              albanianFormTemplates.reduce((acc, template) => {
                if (!acc[template.category]) acc[template.category] = []
                acc[template.category].push(template)
                return acc
              }, {} as { [key: string]: FormTemplate[] })
            ).map(([category, templates]) => (
              <div key={category} className="bg-white rounded-xl shadow-lg p-6">
                <h3 className="font-bold text-lg mb-4 capitalize">
                  {category === 'administrative' && '🏛️ Administrative'}
                  {category === 'business' && '💼 Biznes'}
                  {category === 'personal' && '👤 Personale'}
                  {category === 'legal' && '⚖️ Ligjore'}
                </h3>
                <div className="space-y-2">
                  {templates.map((template, index) => (
                    <button
                      key={index}
                      onClick={() => {
                        setSelectedTemplate(template)
                        setShowTemplates(false)
                        setFormData({})
                      }}
                      className="w-full text-left p-3 rounded-lg hover:bg-red-50 border border-gray-200 hover:border-red-200 transition-colors"
                    >
                      <div className="font-medium text-sm">{template.name}</div>
                      <div className="text-xs text-gray-500 mt-1">{template.description}</div>
                    </button>
                  ))}
                </div>
              </div>
            ))}
          </div>

          {/* Custom Form Option */}
          <div className="bg-white rounded-xl shadow-lg p-8 text-center">
            <div className="text-4xl mb-4">✏️</div>
            <h3 className="text-2xl font-bold mb-4">Krijoni Formular të Personalizuar</h3>
            <p className="text-gray-600 mb-6">
              Ndërtoni formularin tuaj të personalizuar me fushat që ju nevojiten
            </p>
            <button
              onClick={() => {
                setSelectedTemplate(null)
                setShowTemplates(false)
                setCustomForm([])
              }}
              className="px-6 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
            >
              Filloni nga e Para
            </button>
          </div>
        </div>
      </div>
    )
  }

  const currentFields = selectedTemplate?.fields || customForm

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b shadow-sm p-4">
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <button
              onClick={() => setShowTemplates(true)}
              className="text-gray-600 hover:text-red-600"
            >
              ← Kthehu te shabllonet
            </button>
            <h2 className="text-xl font-bold">
              {selectedTemplate?.name || 'Formular i Personalizuar'}
            </h2>
          </div>
          
          <div className="flex space-x-2">
            {!selectedTemplate && (
              <button
                onClick={addCustomField}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                + Shto Fushë
              </button>
            )}
            <button
              onClick={() => setIsPreview(!isPreview)}
              className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
            >
              {isPreview ? 'Ndrysho' : 'Shiko'}
            </button>
            <button
              onClick={saveForm}
              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
            >
              💾 Ruaj
            </button>
            <button
              onClick={exportToPDF}
              className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
            >
              📄 PDF
            </button>
          </div>
        </div>
      </div>

      {/* Form Content */}
      <div className="max-w-4xl mx-auto p-6">
        {isPreview ? (
          // Preview Mode
          <div className="bg-white shadow-lg rounded-lg p-8 print:shadow-none">
            <div className="text-center mb-8">
              <h1 className="text-2xl font-bold uppercase">
                {selectedTemplate?.name || 'FORMULAR I PERSONALIZUAR'}
              </h1>
              <div className="mt-2 text-sm text-gray-600">
                Republika e Shqipërisë
              </div>
            </div>

            <div className="space-y-4">
              {currentFields.map((field) => (
                <div key={field.id} className="flex border-b border-gray-200 pb-2">
                  <div className="w-1/3 font-medium">
                    {field.label}{field.required && ' *'}:
                  </div>
                  <div className="w-2/3 border-b border-dotted border-gray-400 min-h-6">
                    {formData[field.id] || '________________________'}
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-8 text-center text-sm text-gray-600">
              Plotësuar më: {new Date().toLocaleDateString('sq-AL')}
            </div>
          </div>
        ) : (
          // Edit Mode
          <div className="bg-white shadow-lg rounded-lg p-8">
            <form className="space-y-6">
              {currentFields.map((field, index) => (
                <div key={field.id} className="space-y-2">
                  {!selectedTemplate && (
                    // Custom field editor
                    <div className="bg-gray-50 p-4 rounded-lg mb-4">
                      <div className="flex items-center justify-between mb-2">
                        <input
                          type="text"
                          value={field.label}
                          onChange={(e) => updateCustomField(index, { label: e.target.value })}
                          className="font-medium text-lg border-none bg-transparent"
                          placeholder="Etiketa e fushës"
                        />
                        <button
                          type="button"
                          onClick={() => removeCustomField(index)}
                          className="text-red-600 hover:text-red-800"
                        >
                          🗑️
                        </button>
                      </div>
                      <div className="flex space-x-4">
                        <select
                          value={field.type}
                          onChange={(e) => updateCustomField(index, { type: e.target.value as any })}
                          className="px-3 py-1 border rounded"
                        >
                          <option value="text">Tekst</option>
                          <option value="number">Numër</option>
                          <option value="date">Datë</option>
                          <option value="select">Lista</option>
                          <option value="textarea">Tekst i gjatë</option>
                          <option value="checkbox">Kutiza</option>
                          <option value="signature">Nënshkrim</option>
                        </select>
                        <label className="flex items-center">
                          <input
                            type="checkbox"
                            checked={field.required}
                            onChange={(e) => updateCustomField(index, { required: e.target.checked })}
                            className="mr-2"
                          />
                          I detyrueshëm
                        </label>
                      </div>
                    </div>
                  )}
                  
                  <label className="block text-sm font-medium text-gray-700">
                    {field.label} {field.required && <span className="text-red-500">*</span>}
                  </label>
                  {renderField(field)}
                </div>
              ))}
            </form>
          </div>
        )}
      </div>
    </div>
  )
}

export default AlbanianFormCreator
