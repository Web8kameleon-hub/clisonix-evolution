/**
 * UTT Dashboard - Universal Token Terminal
 * EuroWeb Platform - Solana ALB Integration
 * 
 * @author Ledjan Ahmati (100% Owner)
 * @contact dealsjona@gmail.com
 * @version 8.1.0 Ultra
 * @license MIT
 */

'use client'

import { fmt2, fmtAddress, fmtLocale } from '@/lib/utils/number'
import { motion } from 'framer-motion'
import React, { useEffect, useState } from 'react'

interface UTTInfo {
  network: string
  mint: string
  decimals: number
  euroPerALB: number
  bridge: string
  bridgeBalanceALB: number
  transfersEnabled: boolean
  status: string
}

interface PhysicalToken {
  tokenId: string
  serial: string
  owner?: string
  issuedAt: number
  expiresAt?: number
  valueEUR: number
}

const UTTDashboard: React.FC = () => {
  const [uttInfo, setUttInfo] = useState<UTTInfo | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState<'overview' | 'transfer' | 'physical' | 'audit'>('overview')

  // Form states
  const [transferForm, setTransferForm] = useState({ to: '', amount: '' })
  const [physicalForm, setPhysicalForm] = useState({ tokenId: '', serial: '', owner: '' })
  const [verifyData, setVerifyData] = useState('')

  useEffect(() => {
    loadUTTInfo()
  }, [])

  const loadUTTInfo = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await fetch('/api/utt/info')

      // Check if response is JSON
      const contentType = response.headers.get('content-type')
      if (!contentType || !contentType.includes('application/json')) {
        const text = await response.text()
        setError(`API returned HTML instead of JSON. Status: ${response.status}. This usually means the route was not found.`)
        return
      }

      const data = await response.json()

      if (response.ok) {
        setUttInfo(data)
      } else {
        setError(data.error || 'Failed to load UTT info')
      }
    } catch (err: any) {
      if (err.message.includes('Unexpected token')) {
        setError('API returned invalid JSON (probably HTML error page). Check if the API route exists.')
      } else {
        setError(err.message || 'Network error')
      }
    } finally {
      setLoading(false)
    }
  }

  const handleTransfer = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    try {
      const response = await fetch('/api/utt/transfer', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          to: transferForm.to,
          amount: parseFloat(transferForm.amount)
        })
      })

      const data = await response.json()

      if (response.ok) {
        alert(`Transfer successful!\nSignature: ${data.signature}\nExplorer: ${data.explorer}`)
        setTransferForm({ to: '', amount: '' })
        loadUTTInfo() // Refresh balance
      } else {
        setError(data.error || 'Transfer failed')
      }
    } catch (err: any) {
      setError(err.message || 'Transfer error')
    } finally {
      setLoading(false)
    }
  }

  const handleSignPhysical = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    try {
      const response = await fetch('/api/utt/sign-physical', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          tokenId: physicalForm.tokenId,
          serial: physicalForm.serial,
          owner: physicalForm.owner || undefined,
          expiresAt: Date.now() + 365 * 24 * 60 * 60 * 1000 // 1 year
        })
      })

      const data = await response.json()

      if (response.ok) {
        const jsonData = JSON.stringify(data, null, 2)
        setVerifyData(jsonData)
        alert('Physical token signed successfully! Check the verification section.')
        setPhysicalForm({ tokenId: '', serial: '', owner: '' })
      } else {
        setError(data.error || 'Signing failed')
      }
    } catch (err: any) {
      setError(err.message || 'Signing error')
    } finally {
      setLoading(false)
    }
  }

  const handleVerifyPhysical = async () => {
    if (!verifyData.trim()) {
      setError('Please enter verification data')
      return
    }

    setLoading(true)
    setError(null)

    try {
      const response = await fetch('/api/utt/verify-physical', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: verifyData
      })

      const data = await response.json()

      if (response.ok) {
        const status = data.valid ? '✅ VALID' : '❌ INVALID'
        alert(`Verification Result: ${status}\n\nChecks:\n${Object.entries(data.checks || {}).map(([k, v]) => `${k}: ${v ? '✅' : '❌'}`).join('\n')}`)
      } else {
        setError(data.error || 'Verification failed')
      }
    } catch (err: any) {
      setError(err.message || 'Verification error')
    } finally {
      setLoading(false)
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'operational': return '#22c55e'
      case 'bridge_not_configured': return '#f59e0b'
      case 'error': return '#ef4444'
      default: return '#6b7280'
    }
  }

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #1e40af 0%, #3730a3 25%, #581c87 50%, #7c2d12 75%, #dc2626 100%)',
      color: '#f8fafc',
      padding: '24px',
      fontFamily: 'system-ui, -apple-system, sans-serif'
    }}>
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        style={{
          background: 'rgba(0, 0, 0, 0.4)',
          backdropFilter: 'blur(20px)',
          border: '1px solid rgba(59, 130, 246, 0.3)',
          borderRadius: '16px',
          padding: '24px',
          marginBottom: '24px',
          textAlign: 'center'
        }}
      >
        <h1 style={{
          fontSize: '36px',
          fontWeight: 800,
          background: 'linear-gradient(45deg, #3b82f6, #8b5cf6, #ef4444)',
          backgroundClip: 'text',
          WebkitBackgroundClip: 'text',
          color: 'transparent',
          margin: 0,
          marginBottom: '8px'
        }}>
          🪙 UTT Dashboard - Universal Token Terminal
        </h1>
        <p style={{
          margin: 0,
          fontSize: '18px',
          color: '#cbd5e1',
          fontWeight: 500
        }}>
          Solana ALB Integration & Physical Token Management
        </p>
      </motion.div>

      {/* System Status */}
      {uttInfo && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          style={{
            background: 'rgba(0, 0, 0, 0.4)',
            backdropFilter: 'blur(20px)',
            border: '1px solid rgba(59, 130, 246, 0.3)',
            borderRadius: '16px',
            padding: '24px',
            marginBottom: '24px'
          }}
        >
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: '16px'
          }}>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '12px', color: '#94a3b8', marginBottom: '4px' }}>Network</div>
              <div style={{ fontSize: '16px', fontWeight: 600, color: '#3b82f6' }}>
                {uttInfo.network.toUpperCase()}
              </div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '12px', color: '#94a3b8', marginBottom: '4px' }}>Bridge Balance</div>
              <div style={{ fontSize: '16px', fontWeight: 600, color: '#22c55e' }}>
                {fmt2(uttInfo?.bridgeBalanceALB)} ALB
              </div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '12px', color: '#94a3b8', marginBottom: '4px' }}>EUR per ALB</div>
              <div style={{ fontSize: '16px', fontWeight: 600, color: '#f59e0b' }}>
                €{fmtLocale(uttInfo?.euroPerALB)}
              </div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '12px', color: '#94a3b8', marginBottom: '4px' }}>Status</div>
              <div style={{
                fontSize: '16px',
                fontWeight: 600,
                color: getStatusColor(uttInfo.status)
              }}>
                {uttInfo.transfersEnabled ? '🟢 ACTIVE' : '🟡 SHADOW'}
              </div>
            </div>
          </div>
        </motion.div>
      )}

      {/* Tab Navigation */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        style={{
          background: 'rgba(0, 0, 0, 0.4)',
          backdropFilter: 'blur(20px)',
          border: '1px solid rgba(59, 130, 246, 0.3)',
          borderRadius: '12px',
          padding: '16px',
          marginBottom: '24px',
          display: 'flex',
          justifyContent: 'center',
          gap: '12px'
        }}
      >
        {(['overview', 'transfer', 'physical', 'audit'] as const).map(tab => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            style={{
              background: activeTab === tab ? '#3b82f6' : 'rgba(0, 0, 0, 0.3)',
              color: activeTab === tab ? '#fff' : '#cbd5e1',
              border: 'none',
              padding: '8px 20px',
              borderRadius: '8px',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: 600,
              textTransform: 'capitalize',
              transition: 'all 0.2s ease'
            }}
          >
            {tab === 'overview' ? '📊 Overview' :
              tab === 'transfer' ? '💸 Transfer' :
                tab === 'physical' ? '🪙 Physical Tokens' : '📋 Audit'}
          </button>
        ))}
      </motion.div>

      {/* Content Area */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        style={{
          background: 'rgba(0, 0, 0, 0.4)',
          backdropFilter: 'blur(20px)',
          border: '1px solid rgba(59, 130, 246, 0.3)',
          borderRadius: '16px',
          padding: '24px',
          marginBottom: '24px'
        }}
      >
        {/* Overview Tab */}
        {activeTab === 'overview' && uttInfo && (
          <div>
            <h3 style={{ fontSize: '20px', fontWeight: 600, marginBottom: '20px' }}>
              📊 System Overview
            </h3>
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
              gap: '20px'
            }}>
              <div style={{
                background: 'rgba(59, 130, 246, 0.1)',
                border: '1px solid #3b82f6',
                borderRadius: '12px',
                padding: '20px'
              }}>
                <h4 style={{ color: '#3b82f6', marginBottom: '12px' }}>🌐 Network Info</h4>
                <div style={{ fontSize: '14px', color: '#cbd5e1', lineHeight: '1.6' }}>
                  <div>Network: {uttInfo.network}</div>
                  <div>Mint: {fmtAddress(uttInfo?.mint)}</div>
                  <div>Decimals: {uttInfo.decimals}</div>
                  <div>Bridge: {fmtAddress(uttInfo?.bridge)}</div>
                </div>
              </div>

              <div style={{
                background: 'rgba(34, 197, 94, 0.1)',
                border: '1px solid #22c55e',
                borderRadius: '12px',
                padding: '20px'
              }}>
                <h4 style={{ color: '#22c55e', marginBottom: '12px' }}>💰 Economics</h4>
                <div style={{ fontSize: '14px', color: '#cbd5e1', lineHeight: '1.6' }}>
                  <div>1 ALB = €{fmtLocale(uttInfo?.euroPerALB)}</div>
                  <div>Bridge Balance: {fmt2(uttInfo?.bridgeBalanceALB)} ALB</div>
                  <div>Total Value: €{fmtLocale((uttInfo?.bridgeBalanceALB ?? 0) * (uttInfo?.euroPerALB ?? 0))}</div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Transfer Tab */}
        {activeTab === 'transfer' && (
          <div>
            <h3 style={{ fontSize: '20px', fontWeight: 600, marginBottom: '20px' }}>
              💸 ALB Transfer
            </h3>

            {!uttInfo?.transfersEnabled && (
              <div style={{
                background: 'rgba(245, 158, 11, 0.1)',
                border: '1px solid #f59e0b',
                borderRadius: '8px',
                padding: '16px',
                marginBottom: '20px',
                color: '#f59e0b'
              }}>
                🔒 Transfers are currently disabled (Shadow Mode). Only verification functions are active.
              </div>
            )}

            <form onSubmit={handleTransfer} style={{ maxWidth: '400px' }}>
              <div style={{ marginBottom: '16px' }}>
                <label style={{ display: 'block', fontSize: '14px', color: '#cbd5e1', marginBottom: '4px' }}>
                  Receiver Wallet Address
                </label>
                <input
                  type="text"
                  value={transferForm.to}
                  onChange={(e) => setTransferForm(prev => ({ ...prev, to: e.target.value }))}
                  placeholder="Solana wallet address..."
                  style={{
                    width: '100%',
                    padding: '12px',
                    background: 'rgba(0, 0, 0, 0.3)',
                    border: '1px solid rgba(59, 130, 246, 0.3)',
                    borderRadius: '8px',
                    color: '#f8fafc',
                    fontSize: '14px'
                  }}
                  required
                />
              </div>

              <div style={{ marginBottom: '20px' }}>
                <label style={{ display: 'block', fontSize: '14px', color: '#cbd5e1', marginBottom: '4px' }}>
                  Amount (ALB)
                </label>
                <input
                  type="number"
                  step="0.000001"
                  min="0"
                  value={transferForm.amount}
                  onChange={(e) => setTransferForm(prev => ({ ...prev, amount: e.target.value }))}
                  placeholder="0.000000"
                  style={{
                    width: '100%',
                    padding: '12px',
                    background: 'rgba(0, 0, 0, 0.3)',
                    border: '1px solid rgba(59, 130, 246, 0.3)',
                    borderRadius: '8px',
                    color: '#f8fafc',
                    fontSize: '14px'
                  }}
                  required
                />
              </div>

              <button
                type="submit"
                disabled={loading || !uttInfo?.transfersEnabled}
                style={{
                  background: uttInfo?.transfersEnabled ? '#3b82f6' : '#6b7280',
                  color: '#fff',
                  border: 'none',
                  padding: '12px 24px',
                  borderRadius: '8px',
                  fontSize: '14px',
                  fontWeight: 600,
                  cursor: uttInfo?.transfersEnabled ? 'pointer' : 'not-allowed',
                  opacity: loading ? 0.7 : 1
                }}
              >
                {loading ? 'Processing...' : 'Send ALB'}
              </button>
            </form>
          </div>
        )}

        {/* Physical Tokens Tab */}
        {activeTab === 'physical' && (
          <div>
            <h3 style={{ fontSize: '20px', fontWeight: 600, marginBottom: '20px' }}>
              🪙 Physical Token Management
            </h3>

            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
              gap: '24px'
            }}>
              {/* Sign Physical Token */}
              <div>
                <h4 style={{ fontSize: '16px', fontWeight: 600, marginBottom: '16px', color: '#3b82f6' }}>
                  🔏 Sign Physical Token
                </h4>
                <form onSubmit={handleSignPhysical}>
                  <div style={{ marginBottom: '12px' }}>
                    <input
                      type="text"
                      value={physicalForm.tokenId}
                      onChange={(e) => setPhysicalForm(prev => ({ ...prev, tokenId: e.target.value }))}
                      placeholder="Token ID (e.g., ALB-0001)"
                      style={{
                        width: '100%',
                        padding: '8px',
                        background: 'rgba(0, 0, 0, 0.3)',
                        border: '1px solid rgba(59, 130, 246, 0.3)',
                        borderRadius: '6px',
                        color: '#f8fafc',
                        fontSize: '14px'
                      }}
                      required
                    />
                  </div>
                  <div style={{ marginBottom: '12px' }}>
                    <input
                      type="text"
                      value={physicalForm.serial}
                      onChange={(e) => setPhysicalForm(prev => ({ ...prev, serial: e.target.value }))}
                      placeholder="Serial Number (e.g., S-0001)"
                      style={{
                        width: '100%',
                        padding: '8px',
                        background: 'rgba(0, 0, 0, 0.3)',
                        border: '1px solid rgba(59, 130, 246, 0.3)',
                        borderRadius: '6px',
                        color: '#f8fafc',
                        fontSize: '14px'
                      }}
                      required
                    />
                  </div>
                  <div style={{ marginBottom: '16px' }}>
                    <input
                      type="text"
                      value={physicalForm.owner}
                      onChange={(e) => setPhysicalForm(prev => ({ ...prev, owner: e.target.value }))}
                      placeholder="Owner Wallet (optional)"
                      style={{
                        width: '100%',
                        padding: '8px',
                        background: 'rgba(0, 0, 0, 0.3)',
                        border: '1px solid rgba(59, 130, 246, 0.3)',
                        borderRadius: '6px',
                        color: '#f8fafc',
                        fontSize: '14px'
                      }}
                    />
                  </div>
                  <button
                    type="submit"
                    disabled={loading}
                    style={{
                      background: '#3b82f6',
                      color: '#fff',
                      border: 'none',
                      padding: '8px 16px',
                      borderRadius: '6px',
                      fontSize: '14px',
                      fontWeight: 600,
                      cursor: 'pointer',
                      opacity: loading ? 0.7 : 1
                    }}
                  >
                    {loading ? 'Signing...' : 'Sign Token'}
                  </button>
                </form>
              </div>

              {/* Verify Physical Token */}
              <div>
                <h4 style={{ fontSize: '16px', fontWeight: 600, marginBottom: '16px', color: '#22c55e' }}>
                  🔐 Verify Physical Token
                </h4>
                <div style={{ marginBottom: '12px' }}>
                  <textarea
                    value={verifyData}
                    onChange={(e) => setVerifyData(e.target.value)}
                    placeholder="Paste signed token data (JSON) here..."
                    rows={6}
                    style={{
                      width: '100%',
                      padding: '8px',
                      background: 'rgba(0, 0, 0, 0.3)',
                      border: '1px solid rgba(34, 197, 94, 0.3)',
                      borderRadius: '6px',
                      color: '#f8fafc',
                      fontSize: '12px',
                      fontFamily: 'monospace',
                      resize: 'vertical'
                    }}
                  />
                </div>
                <button
                  onClick={handleVerifyPhysical}
                  disabled={loading || !verifyData.trim()}
                  style={{
                    background: '#22c55e',
                    color: '#fff',
                    border: 'none',
                    padding: '8px 16px',
                    borderRadius: '6px',
                    fontSize: '14px',
                    fontWeight: 600,
                    cursor: 'pointer',
                    opacity: loading || !verifyData.trim() ? 0.7 : 1
                  }}
                >
                  {loading ? 'Verifying...' : 'Verify Token'}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Audit Tab */}
        {activeTab === 'audit' && (
          <div>
            <h3 style={{ fontSize: '20px', fontWeight: 600, marginBottom: '20px' }}>
              📋 System Audit & Logs
            </h3>
            <div style={{
              background: 'rgba(0, 0, 0, 0.3)',
              border: '1px solid rgba(59, 130, 246, 0.3)',
              borderRadius: '8px',
              padding: '16px',
              fontFamily: 'monospace',
              fontSize: '12px',
              color: '#cbd5e1'
            }}>
              <div>📅 System Status: {uttInfo?.status}</div>
              <div>🌐 Network: {uttInfo?.network}</div>
              <div>🔐 Bridge Configured: {uttInfo?.bridge !== 'not_configured' ? 'Yes' : 'No'}</div>
              <div>💸 Transfers Enabled: {uttInfo?.transfersEnabled ? 'Yes' : 'No (Shadow Mode)'}</div>
              <div>⏰ Last Update: {new Date().toISOString()}</div>
              <div style={{ marginTop: '12px', color: '#94a3b8' }}>
                🔍 Detailed audit logs are written to console and will be implemented
                in the next phase with hash-chain verification.
              </div>
            </div>
          </div>
        )}
      </motion.div>

      {/* Error Display */}
      {error && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          style={{
            background: 'rgba(239, 68, 68, 0.1)',
            border: '1px solid #ef4444',
            borderRadius: '8px',
            padding: '16px',
            marginBottom: '24px',
            color: '#fecaca'
          }}
        >
          ❌ {error}
          <button
            onClick={() => setError(null)}
            style={{
              float: 'right',
              background: 'none',
              border: 'none',
              color: '#ef4444',
              cursor: 'pointer',
              fontSize: '18px'
            }}
          >
            ×
          </button>
        </motion.div>
      )}

      {/* Refresh Button */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
        style={{
          textAlign: 'center',
          marginBottom: '24px'
        }}
      >
        <button
          onClick={loadUTTInfo}
          disabled={loading}
          style={{
            background: loading ? '#6b7280' : 'rgba(59, 130, 246, 0.2)',
            border: '1px solid #3b82f6',
            color: '#3b82f6',
            padding: '8px 16px',
            borderRadius: '8px',
            fontSize: '14px',
            fontWeight: 600,
            cursor: loading ? 'not-allowed' : 'pointer',
            transition: 'all 0.2s ease'
          }}
        >
          {loading ? '🔄 Loading...' : '🔄 Refresh Status'}
        </button>
      </motion.div>

      {/* Footer */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.6 }}
        style={{
          padding: '16px',
          background: 'rgba(0, 0, 0, 0.4)',
          backdropFilter: 'blur(20px)',
          border: '1px solid rgba(59, 130, 246, 0.3)',
          borderRadius: '12px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          fontSize: '14px'
        }}
      >
        <div style={{ color: '#3b82f6' }}>
          🪙 UTT - Universal Token Terminal Active
        </div>
        <div style={{ color: '#cbd5e1' }}>
          🌐 EuroWeb Platform v8.1.0 | Solana Integration | {uttInfo?.transfersEnabled ? 'Live Mode' : 'Shadow Mode'}
        </div>
        <div style={{ color: '#3b82f6' }}>
          ⚡ {new Date().toLocaleTimeString()} | ALB Mode
        </div>
      </motion.div>
    </div>
  )
}

export default UTTDashboard

