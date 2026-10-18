'use client'

import React, { useState, useCallback } from 'react'

interface Cell {
  value: string
  formula?: string
  type: 'text' | 'number' | 'date' | 'currency'
  style?: {
    bold?: boolean
    italic?: boolean
    backgroundColor?: string
    textColor?: string
    textAlign?: 'left' | 'center' | 'right'
  }
}

interface Sheet {
  name: string
  cells: { [key: string]: Cell }
  columns: number
  rows: number
}

const albanianNumberFormat = new Intl.NumberFormat('sq-AL', {
  style: 'currency',
  currency: 'ALL'
})

const albanianDateFormat = new Intl.DateTimeFormat('sq-AL', {
  day: '2-digit',
  month: '2-digit', 
  year: 'numeric'
})

export const AlbanianSpreadsheet: React.FC = () => {
  const [sheets, setSheets] = useState<Sheet[]>([
    {
      name: 'Fleta 1',
      cells: {},
      columns: 26,
      rows: 100
    }
  ])
  const [activeSheet, setActiveSheet] = useState(0)
  const [selectedCell, setSelectedCell] = useState<string | null>(null)
  const [showFormulas, setShowFormulas] = useState(false)

  const sheet = sheets[activeSheet]

  const getCellAddress = (row: number, col: number): string => {
    return `${String.fromCharCode(65 + col)}${row + 1}`
  }

  const parseFormula = (formula: string): number => {
    // Basic formula parser for Albanian spreadsheet
    try {
      // Replace Albanian decimal separator
      const cleanFormula = formula.replace(/,/g, '.')
      
      // Simple arithmetic evaluation
      if (cleanFormula.startsWith('=')) {
        const expression = cleanFormula.slice(1)
        
        // Handle basic functions
        if (expression.includes('SHUMA(')) {
          const range = expression.match(/SHUMA\(([^)]+)\)/)
          if (range) {
            // Calculate sum of range
            return 0 // Simplified for demo
          }
        }
        
        // Evaluate arithmetic
        return eval(expression)
      }
      
      return parseFloat(cleanFormula) || 0
    } catch {
      return 0
    }
  }

  const updateCell = useCallback((address: string, value: string) => {
    setSheets(prevSheets => {
      const newSheets = [...prevSheets]
      const currentSheet = { ...newSheets[activeSheet] }
      
      if (!currentSheet.cells[address]) {
        currentSheet.cells[address] = {
          value: '',
          type: 'text'
        }
      }
      
      const cell = { ...currentSheet.cells[address] }
      
      // Determine cell type
      if (value.startsWith('=')) {
        cell.formula = value
        cell.value = parseFormula(value).toString()
        cell.type = 'number'
      } else if (!isNaN(Number(value)) && value !== '') {
        cell.value = value
        cell.type = 'number'
      } else if (value.match(/^\d{1,2}\/\d{1,2}\/\d{4}$/)) {
        cell.value = value
        cell.type = 'date'
      } else if (value.includes('ALL') || value.includes('€') || value.includes('$')) {
        cell.value = value
        cell.type = 'currency'
      } else {
        cell.value = value
        cell.type = 'text'
      }
      
      currentSheet.cells[address] = cell
      newSheets[activeSheet] = currentSheet
      
      return newSheets
    })
  }, [activeSheet])

  const formatCellValue = (cell: Cell): string => {
    if (!cell) return ''
    
    if (showFormulas && cell.formula) {
      return cell.formula
    }
    
    switch (cell.type) {
      case 'number':
        const num = parseFloat(cell.value)
        return isNaN(num) ? cell.value : num.toLocaleString('sq-AL')
      case 'currency':
        const curr = parseFloat(cell.value)
        return isNaN(curr) ? cell.value : albanianNumberFormat.format(curr)
      case 'date':
        try {
          const date = new Date(cell.value)
          return albanianDateFormat.format(date)
        } catch {
          return cell.value
        }
      default:
        return cell.value
    }
  }

  const addSheet = () => {
    const newSheet: Sheet = {
      name: `Fleta ${sheets.length + 1}`,
      cells: {},
      columns: 26,
      rows: 100
    }
    setSheets([...sheets, newSheet])
    setActiveSheet(sheets.length)
  }

  const albanianTemplates = [
    {
      name: 'Buxheti Familjar',
      data: {
        'A1': { value: 'BUXHETI FAMILJAR', type: 'text' as const, style: { bold: true, textAlign: 'center' as const } },
        'A3': { value: 'TË HYRAT', type: 'text' as const, style: { bold: true } },
        'A4': { value: 'Paga', type: 'text' as const },
        'B4': { value: '80000', type: 'currency' as const },
        'A5': { value: 'Të hyra shtesë', type: 'text' as const },
        'B5': { value: '15000', type: 'currency' as const },
        'A6': { value: 'Totali i të hyrave', type: 'text' as const, style: { bold: true } },
        'B6': { value: '=B4+B5', formula: '=B4+B5', type: 'currency' as const, style: { bold: true } },
        
        'A8': { value: 'SHPENZIMET', type: 'text' as const, style: { bold: true } },
        'A9': { value: 'Qiraja', type: 'text' as const },
        'B9': { value: '35000', type: 'currency' as const },
        'A10': { value: 'Ushqimi', type: 'text' as const },
        'B10': { value: '25000', type: 'currency' as const },
        'A11': { value: 'Transporti', type: 'text' as const },
        'B11': { value: '8000', type: 'currency' as const },
        'A12': { value: 'Totali i shpenzimeve', type: 'text' as const, style: { bold: true } },
        'B12': { value: '=B9+B10+B11', formula: '=B9+B10+B11', type: 'currency' as const, style: { bold: true } },
        
        'A14': { value: 'BILANCI', type: 'text' as const, style: { bold: true } },
        'B14': { value: '=B6-B12', formula: '=B6-B12', type: 'currency' as const, style: { bold: true } }
      }
    },
    {
      name: 'Lista e Produkteve',
      data: {
        'A1': { value: 'LISTA E PRODUKTEVE', type: 'text' as const, style: { bold: true, textAlign: 'center' as const } },
        'A3': { value: 'Kodi', type: 'text' as const, style: { bold: true } },
        'B3': { value: 'Emri i Produktit', type: 'text' as const, style: { bold: true } },
        'C3': { value: 'Sasia', type: 'text' as const, style: { bold: true } },
        'D3': { value: 'Çmimi', type: 'text' as const, style: { bold: true } },
        'E3': { value: 'Totali', type: 'text' as const, style: { bold: true } },
        
        'A4': { value: 'P001', type: 'text' as const },
        'B4': { value: 'Laptop Dell', type: 'text' as const },
        'C4': { value: '5', type: 'number' as const },
        'D4': { value: '150000', type: 'currency' as const },
        'E4': { value: '=C4*D4', formula: '=C4*D4', type: 'currency' as const },
        
        'A5': { value: 'P002', type: 'text' as const },
        'B5': { value: 'Miu Wireless', type: 'text' as const },
        'C5': { value: '10', type: 'number' as const },
        'D5': { value: '2500', type: 'currency' as const },
        'E5': { value: '=C5*D5', formula: '=C5*D5', type: 'currency' as const }
      }
    }
  ]

  const loadTemplate = (template: any) => {
    setSheets(prevSheets => {
      const newSheets = [...prevSheets]
      newSheets[activeSheet] = {
        ...newSheets[activeSheet],
        cells: template.data
      }
      return newSheets
    })
  }

  const exportToCSV = () => {
    const csv = []
    const maxRow = Math.max(...Object.keys(sheet.cells).map(addr => {
      const match = addr.match(/\d+/)
      return match ? parseInt(match[0]) : 0
    }))
    
    for (let row = 0; row < maxRow; row++) {
      const rowData = []
      for (let col = 0; col < sheet.columns; col++) {
        const address = getCellAddress(row, col)
        const cell = sheet.cells[address]
        rowData.push(cell ? cell.value : '')
      }
      csv.push(rowData.join(','))
    }
    
    const blob = new Blob([csv.join('\n')], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${sheet.name}.csv`
    a.click()
  }

  return (
    <div className="bg-gray-50 h-screen flex flex-col">
      {/* Toolbar */}
      <div className="bg-white border-b shadow-sm p-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <h2 className="text-lg font-bold text-gray-800">Tabelë Shqiptare</h2>
            
            {/* Templates */}
            <select
              onChange={(e) => {
                const template = albanianTemplates[parseInt(e.target.value)]
                if (template) loadTemplate(template)
              }}
              className="px-3 py-1 border rounded"
              defaultValue=""
            >
              <option value="">Zgjidhni shablon...</option>
              {albanianTemplates.map((template, index) => (
                <option key={index} value={index}>
                  {template.name}
                </option>
              ))}
            </select>

            <button
              onClick={() => setShowFormulas(!showFormulas)}
              className={`px-3 py-1 rounded ${showFormulas ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}
            >
              fx Formulat
            </button>
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={exportToCSV}
              className="px-3 py-1 bg-green-600 text-white rounded hover:bg-green-700"
            >
              📊 Eksporto CSV
            </button>
            <button
              onClick={() => window.print()}
              className="px-3 py-1 bg-red-600 text-white rounded hover:bg-red-700"
            >
              🖨️ Printo
            </button>
          </div>
        </div>
      </div>

      {/* Formula Bar */}
      {selectedCell && (
        <div className="bg-white border-b p-2 flex items-center space-x-4">
          <div className="font-mono font-bold">{selectedCell}</div>
          <input
            type="text"
            value={sheet.cells[selectedCell]?.formula || sheet.cells[selectedCell]?.value || ''}
            onChange={(e) => updateCell(selectedCell, e.target.value)}
            className="flex-1 px-3 py-1 border rounded"
            placeholder="Shkruani vlerën ose formulën..."
          />
        </div>
      )}

      {/* Spreadsheet */}
      <div className="flex-1 overflow-auto">
        <table className="w-full border-collapse">
          {/* Column Headers */}
          <thead>
            <tr>
              <th className="w-12 h-8 bg-gray-200 border border-gray-300"></th>
              {Array.from({ length: sheet.columns }, (_, col) => (
                <th
                  key={col}
                  className="min-w-24 h-8 bg-gray-200 border border-gray-300 text-xs font-bold"
                >
                  {String.fromCharCode(65 + col)}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {Array.from({ length: sheet.rows }, (_, row) => (
              <tr key={row}>
                {/* Row Header */}
                <td className="w-12 h-6 bg-gray-200 border border-gray-300 text-xs font-bold text-center">
                  {row + 1}
                </td>
                {/* Cells */}
                {Array.from({ length: sheet.columns }, (_, col) => {
                  const address = getCellAddress(row, col)
                  const cell = sheet.cells[address]
                  const isSelected = selectedCell === address
                  
                  return (
                    <td
                      key={address}
                      className={`min-w-24 h-6 border border-gray-300 p-1 text-xs ${
                        isSelected ? 'bg-blue-100 ring-2 ring-blue-500' : 'bg-white hover:bg-gray-50'
                      }`}
                      onClick={() => setSelectedCell(address)}
                      style={{
                        fontWeight: cell?.style?.bold ? 'bold' : 'normal',
                        fontStyle: cell?.style?.italic ? 'italic' : 'normal',
                        backgroundColor: cell?.style?.backgroundColor || (isSelected ? '#dbeafe' : 'white'),
                        color: cell?.style?.textColor || 'black',
                        textAlign: cell?.style?.textAlign || 'left'
                      }}
                    >
                      <input
                        type="text"
                        value={formatCellValue(cell)}
                        onChange={(e) => updateCell(address, e.target.value)}
                        className="w-full h-full bg-transparent border-none outline-none text-xs"
                        style={{ textAlign: cell?.style?.textAlign || 'left' }}
                      />
                    </td>
                  )
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Sheet Tabs */}
      <div className="bg-white border-t p-2 flex items-center space-x-2">
        {sheets.map((s, index) => (
          <button
            key={index}
            onClick={() => setActiveSheet(index)}
            className={`px-3 py-1 rounded text-sm ${
              activeSheet === index
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 hover:bg-gray-300'
            }`}
          >
            {s.name}
          </button>
        ))}
        <button
          onClick={addSheet}
          className="px-3 py-1 bg-green-600 text-white rounded text-sm hover:bg-green-700"
        >
          + Shto Fletë
        </button>
      </div>

      {/* Status Bar */}
      <div className="bg-gray-100 p-2 text-xs text-gray-600 flex justify-between">
        <div>
          Fleta: {sheet.name} | Qeliza e zgjedhur: {selectedCell || 'Asnjë'}
        </div>
        <div>
          Shqipëri | Format: A4 | Monedha: ALL
        </div>
      </div>
    </div>
  )
}

export default AlbanianSpreadsheet
