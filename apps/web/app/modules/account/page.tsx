/**
 * Clisonix User Account & Billing Dashboard
 * Manage subscriptions, billing, profile settings
 */

"use client"

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { useTranslation, type Language } from '@/lib/i18n'

interface User {
  id: string
  name: string
  email: string
  avatar?: string
  plan: string
  company?: string
  phone?: string
  timezone: string
  language: string
  createdAt: string
}

interface Subscription {
  id: string
  plan: string
  status: 'active' | 'canceled' | 'past_due' | 'trialing'
  currentPeriodStart: string
  currentPeriodEnd: string
  cancelAtPeriodEnd: boolean
  amount: number
  currency: string
  interval: 'month' | 'year'
}

interface Invoice {
  id: string
  date: string
  amount: number
  currency: string
  status: 'paid' | 'pending' | 'failed'
  pdfUrl?: string
}

interface PaymentMethod {
  id: string
  type: 'card' | 'paypal' | 'bank'
  last4?: string
  brand?: string
  expiryMonth?: number
  expiryYear?: number
  isDefault: boolean
}

interface ApiKey {
  id: string
  key: string
  name: string
  createdAt: string
  lastUsed?: string
}

interface BillingAddress {
  line1: string
  line2?: string
  city: string
  state?: string
  postal_code: string
  country: string
  name?: string
  phone?: string
}

interface PlanOption {
  id: string
  productId: string
  name: string
  description?: string
  amount: number
  currency: string
  interval: 'month' | 'year'
  priceId: string
  features: string[]
  popular: boolean
  rank: number
}

interface LanguageOption {
  code: string
  name: string
}

interface TimezoneOption {
  id: string
  label: string
  offset: string
}

interface CountryOption {
  code: string
  name: string
}

interface ThemeOption {
  id: string
  name: string
}

interface NotificationCategoryOption {
  id: string
  label: string
  description: string
  defaultEnabled: boolean
}

type NotificationPreference = Record<string, boolean>

export default function AccountPage() {
  // i18n translation hook
  const { t, language, setLanguage, isLoaded } = useTranslation()
  const supportEmail = process.env.NEXT_PUBLIC_SUPPORT_EMAIL || ''

  const [activeTab, setActiveTab] = useState<'overview' | 'billing' | 'subscription' | 'security' | 'settings'>('overview')
  const [isLoading, setIsLoading] = useState(true)
  const [showUpgradeModal, setShowUpgradeModal] = useState(false)
  const [isCheckoutLoading, setIsCheckoutLoading] = useState(false)
  const [isSavingProfile, setIsSavingProfile] = useState(false)
  const [profileSaveMessage, setProfileSaveMessage] = useState<{type: 'success' | 'error', text: string} | null>(null)
  const [actionMessage, setActionMessage] = useState<{type: 'success' | 'error', text: string} | null>(null)
  const [isPortalLoading, setIsPortalLoading] = useState(false)
  const [isSubscriptionActionLoading, setIsSubscriptionActionLoading] = useState(false)
  const [busyPaymentMethodId, setBusyPaymentMethodId] = useState<string | null>(null)

  // User data - fetched from API
  const [user, setUser] = useState<User | null>(null)

  // Subscription - fetched from API (null = no active subscription)
  const [subscription, setSubscription] = useState<Subscription | null>(null)

  // Dynamic options and catalog data
  const [plans, setPlans] = useState<PlanOption[]>([])
  const [languageOptions, setLanguageOptions] = useState<LanguageOption[]>([])
  const [timezoneOptions, setTimezoneOptions] = useState<TimezoneOption[]>([])
  const [countryOptions, setCountryOptions] = useState<CountryOption[]>([])
  const [themeOptions, setThemeOptions] = useState<ThemeOption[]>([])
  const [notificationCategories, setNotificationCategories] = useState<NotificationCategoryOption[]>([])

  // Stripe checkout handler
  const handleUpgrade = async (priceId: string) => {
    setIsCheckoutLoading(true)
    setActionMessage(null)
    try {
      const response = await fetch('/api/billing/checkout', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          priceId,
          successUrl: `${window.location.origin}/modules/account?success=true`,
          cancelUrl: `${window.location.origin}/modules/account?canceled=true`,
        }),
      })

      const result = await response.json()
      const data = unwrapData<{ url?: string }>(result)

      if (result.success && data?.url) {
        // Redirect to Stripe Checkout
        window.location.href = data.url
      } else {
        console.error('Checkout error:', result.error)
        setActionMessage({ type: 'error', text: result?.error?.message || t('upgrade.paymentError') })
      }
    } catch (error) {
      console.error('Checkout error:', error)
      setActionMessage({ type: 'error', text: t('upgrade.connectionError') })
    } finally {
      setIsCheckoutLoading(false)
    }
  }

  const handleOpenBillingPortal = async () => {
    setIsPortalLoading(true)
    setActionMessage(null)
    try {
      const response = await fetch('/api/billing/portal', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          returnUrl: `${window.location.origin}/modules/account?portal=return`,
        }),
      })

      const result = await response.json()
      const data = unwrapData<{ url?: string }>(result)

      if (result.success && data?.url) {
        window.location.href = data.url
        return
      }

      setActionMessage({
        type: 'error',
        text: result?.error?.message || 'Billing portal is unavailable right now.',
      })
    } catch (error) {
      console.error('Billing portal error:', error)
      setActionMessage({ type: 'error', text: 'Failed to open billing portal.' })
    } finally {
      setIsPortalLoading(false)
    }
  }

  const handleCancelSubscription = async () => {
    if (!subscription) return
    if (!confirm('Cancel subscription at the end of the current billing period?')) return

    setIsSubscriptionActionLoading(true)
    setActionMessage(null)
    try {
      const response = await fetch('/api/billing/subscription', {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          subscriptionId: subscription.id,
          cancelAtPeriodEnd: true,
        }),
      })

      const result = await response.json()
      if (result.success) {
        setSubscription({ ...subscription, cancelAtPeriodEnd: true })
        setActionMessage({ type: 'success', text: 'Subscription will end at the close of the current billing cycle.' })
      } else {
        setActionMessage({ type: 'error', text: result?.error?.message || 'Unable to cancel subscription.' })
      }
    } catch (error) {
      console.error('Subscription cancel error:', error)
      setActionMessage({ type: 'error', text: 'Unable to cancel subscription.' })
    } finally {
      setIsSubscriptionActionLoading(false)
    }
  }

  // Save profile handler
  const handleSaveProfile = async () => {
    if (!user) return

    setIsSavingProfile(true)
    setProfileSaveMessage(null)

    try {
      const response = await fetch('/api/user/profile', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: user.name,
          email: user.email,
          company: user.company,
          phone: user.phone,
          language: user.language,
          timezone: user.timezone,
        }),
      })

      const result = await response.json()
      const data = unwrapData<User>(result)

      if (result.success) {
        setUser(data)
        setProfileSaveMessage({ type: 'success', text: t('settings.profileSaved') })
        setTimeout(() => setProfileSaveMessage(null), 3000)
      } else {
        setProfileSaveMessage({ type: 'error', text: t('settings.saveFailed') })
      }
    } catch (error) {
      console.error('Save profile error:', error)
      setProfileSaveMessage({ type: 'error', text: t('settings.connectionError') })
    } finally {
      setIsSavingProfile(false)
    }
  }

  // Invoices - fetched from API (empty = no invoices yet)
  const [invoices, setInvoices] = useState<Invoice[]>([])

  // Payment methods - fetched from API (empty = no payment methods)
  const [paymentMethods, setPaymentMethods] = useState<PaymentMethod[]>([])

  // Billing address - fetched from API
  const [billingAddress, setBillingAddress] = useState<BillingAddress | null>(null)
  const [showAddressModal, setShowAddressModal] = useState(false)
  const [isSavingAddress, setIsSavingAddress] = useState(false)

  // API Keys - managed by server API
  const [apiKeys, setApiKeys] = useState<ApiKey[]>([])
  const [isGeneratingKey, setIsGeneratingKey] = useState(false)
  const [copiedKeyId, setCopiedKeyId] = useState<string | null>(null)
  const [latestApiKeySecret, setLatestApiKeySecret] = useState<string | null>(null)

  // Handle generate new API key
  const handleGenerateApiKey = async () => {
    setIsGeneratingKey(true)
    setActionMessage(null)

    try {
      const response = await fetch('/api/security/api-keys', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: `API Key ${apiKeys.length + 1}` }),
      })

      const result = await response.json()
      const payload = unwrapData<{ key: ApiKey & { maskedKey?: string } }>(result)

      if (result.success && payload?.key) {
        setLatestApiKeySecret(payload.key.key)
        setApiKeys((prev) => [
          {
            ...payload.key,
            key: payload.key.maskedKey || payload.key.key,
          },
          ...prev,
        ])
        setActionMessage({ type: 'success', text: 'API key generated. Copy it now; it will not be shown again.' })
      } else {
        setActionMessage({ type: 'error', text: result?.error?.message || 'Failed to generate API key.' })
      }
    } catch (error) {
      console.error('API key generation error:', error)
      setActionMessage({ type: 'error', text: 'Failed to generate API key.' })
    } finally {
      setIsGeneratingKey(false)
    }
  }

  // Handle copy API key
  const handleCopyApiKey = async (key: ApiKey) => {
    try {
      await navigator.clipboard.writeText(key.key)
      setCopiedKeyId(key.id)
      setTimeout(() => setCopiedKeyId(null), 2000)
    } catch (error) {
      console.error('Failed to copy:', error)
    }
  }

  // Handle revoke API key
  const handleRevokeApiKey = async (keyId: string) => {
    if (!confirm(t('security.revokeConfirm'))) return

    try {
      const response = await fetch('/api/security/api-keys', {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ keyId }),
      })

      const result = await response.json()
      if (result.success) {
        setApiKeys(apiKeys.filter(k => k.id !== keyId))
      } else {
        setActionMessage({ type: 'error', text: result?.error?.message || 'Failed to revoke API key.' })
      }
    } catch (error) {
      console.error('API key revoke error:', error)
      setActionMessage({ type: 'error', text: 'Failed to revoke API key.' })
    }
  }

  const handleSetDefaultPaymentMethod = async (paymentMethodId: string) => {
    setBusyPaymentMethodId(paymentMethodId)
    setActionMessage(null)
    try {
      const response = await fetch('/api/billing/payment-methods', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ paymentMethodId }),
      })

      const result = await response.json()
      if (result.success) {
        setPaymentMethods(paymentMethods.map(method => ({
          ...method,
          isDefault: method.id === paymentMethodId,
        })))
        setActionMessage({ type: 'success', text: 'Default payment method updated.' })
      } else {
        setActionMessage({ type: 'error', text: result?.error?.message || 'Failed to update payment method.' })
      }
    } catch (error) {
      console.error('Set default payment method error:', error)
      setActionMessage({ type: 'error', text: 'Failed to update payment method.' })
    } finally {
      setBusyPaymentMethodId(null)
    }
  }

  const handleRemovePaymentMethod = async (paymentMethodId: string) => {
    if (!confirm('Remove this payment method?')) return

    setBusyPaymentMethodId(paymentMethodId)
    setActionMessage(null)
    try {
      const response = await fetch('/api/billing/payment-methods', {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ paymentMethodId }),
      })

      const result = await response.json()
      if (result.success) {
        setPaymentMethods(paymentMethods.filter(method => method.id !== paymentMethodId))
        setActionMessage({ type: 'success', text: 'Payment method removed.' })
      } else {
        setActionMessage({ type: 'error', text: result?.error?.message || 'Failed to remove payment method.' })
      }
    } catch (error) {
      console.error('Remove payment method error:', error)
      setActionMessage({ type: 'error', text: 'Failed to remove payment method.' })
    } finally {
      setBusyPaymentMethodId(null)
    }
  }

  const handleExportData = () => {
    const exportPayload = {
      user,
      subscription,
      invoices,
      paymentMethods,
      billingAddress,
      apiKeys,
      notificationPreferences,
      exportedAt: new Date().toISOString(),
    }

    const blob = new Blob([JSON.stringify(exportPayload, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `clisonix-account-export-${new Date().toISOString().slice(0, 10)}.json`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
    setActionMessage({ type: 'success', text: 'Account export downloaded.' })
  }

  const handleDeleteAccount = () => {
    if (!supportEmail) {
      setActionMessage({ type: 'error', text: 'Support email is not configured.' })
      return
    }

    const subject = encodeURIComponent('Delete account request')
    const body = encodeURIComponent(`Please review the deletion request for ${user?.email || ''}.\n\nUser: ${user?.name || ''}\nCompany: ${user?.company || ''}\nRequested at: ${new Date().toISOString()}`)
    window.location.href = `mailto:${supportEmail}?subject=${subject}&body=${body}`
  }

  // Preferences state
  const [preferencesMessage, setPreferencesMessage] = useState<{type: 'success' | 'error', text: string} | null>(null)
  const [detectedTimezone, setDetectedTimezone] = useState<string | null>(null)
  const [notificationPreferences, setNotificationPreferences] = useState<NotificationPreference>({})

  const unwrapData = <T,>(payload: unknown): T => {
    if (payload && typeof payload === 'object' && 'data' in payload) {
      return (payload as { data: T }).data
    }

    return payload as T
  }

  // Detect timezone automatically on mount
  useEffect(() => {
    try {
      const browserTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone
      setDetectedTimezone(browserTimezone)
    } catch (error) {
      console.log('Could not detect timezone:', error)
    }
  }, [])

  useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    const success = params.get('success')
    const canceled = params.get('canceled')
    const portal = params.get('portal')

    if (success === 'true') {
      setActionMessage({ type: 'success', text: 'Subscription checkout completed successfully.' })
    } else if (canceled === 'true') {
      setActionMessage({ type: 'error', text: 'Checkout was canceled.' })
    } else if (portal === 'return') {
      setActionMessage({ type: 'success', text: 'Returned from the billing portal.' })
    }
  }, [])

  // Handle language change with persistence
  const handleLanguageChange = (langCode: Language) => {
    if (!user) return
    setUser({...user, language: langCode})
    setLanguage(langCode)
    setPreferencesMessage({ type: 'success', text: `${t('preferences.languageChanged')} ${langCode.toUpperCase()}` })
    setTimeout(() => setPreferencesMessage(null), 2000)
  }

  useEffect(() => {
    if (!isLoaded) return
    setUser(prev => {
      if (!prev || prev.language === language) {
        return prev
      }
      return { ...prev, language }
    })
  }, [language, isLoaded])

  // Handle timezone change with persistence
  const handleTimezoneChange = (timezone: string) => {
    if (!user) return
    setUser({...user, timezone})
    setPreferencesMessage({ type: 'success', text: `${t('preferences.timezoneChanged')} ${timezone}` })
    setTimeout(() => setPreferencesMessage(null), 2000)
  }

  // Auto-detect and set timezone from browser
  const handleAutoDetectTimezone = () => {
    if (!user || !detectedTimezone) return
    setUser({...user, timezone: detectedTimezone})
    setPreferencesMessage({ type: 'success', text: `${t('preferences.timezoneChanged')} ${detectedTimezone}` })
    setTimeout(() => setPreferencesMessage(null), 3000)
  }

  const handleToggleNotification = async (notificationId: string) => {
    const nextPreferences = {
      ...notificationPreferences,
      [notificationId]: !notificationPreferences[notificationId],
    }

    setNotificationPreferences(nextPreferences)

    try {
      const response = await fetch('/api/user/notification-preferences', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ preferences: nextPreferences }),
      })

      const result = await response.json()
      if (!result.success) {
        setActionMessage({ type: 'error', text: result?.error?.message || 'Failed to update notification preferences.' })
      } else {
        setPreferencesMessage({ type: 'success', text: 'Notification preferences updated.' })
        setTimeout(() => setPreferencesMessage(null), 2000)
      }
    } catch (error) {
      console.error('Notification preference update failed:', error)
      setActionMessage({ type: 'error', text: 'Failed to update notification preferences.' })
    }
  }

  // Fetch user profile from API
  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const response = await fetch('/api/user/profile')
        const result = await response.json()
        const data = unwrapData<User>(result)
        if (result.success && data) {
          setUser(data)
        }
      } catch (error) {
        console.error('Failed to fetch profile:', error)
      } finally {
        setIsLoading(false)
      }
    }
    fetchProfile()
  }, [])

  // Fetch billing data from Stripe APIs
  useEffect(() => {
    const fetchBillingData = async () => {
      try {
        // Fetch all billing data in parallel
        const [subscriptionRes, invoicesRes, paymentMethodsRes, addressRes, plansRes, apiKeysRes] = await Promise.all([
          fetch('/api/billing/subscription'),
          fetch('/api/billing/invoices'),
          fetch('/api/billing/payment-methods'),
          fetch('/api/billing/billing-address'),
          fetch('/api/billing/plans'),
          fetch('/api/security/api-keys'),
        ])

        const [subscriptionData, invoicesData, paymentMethodsData, addressData, plansData, apiKeysData] = await Promise.all([
          subscriptionRes.json(),
          invoicesRes.json(),
          paymentMethodsRes.json(),
          addressRes.json(),
          plansRes.json(),
          apiKeysRes.json(),
        ])

        const subscriptionPayload = unwrapData<{ subscription: Subscription | null }>(subscriptionData)
        const invoicesPayload = unwrapData<{ invoices: Invoice[] }>(invoicesData)
        const paymentMethodsPayload = unwrapData<{ paymentMethods: PaymentMethod[] }>(paymentMethodsData)
        const addressPayload = unwrapData<{ billingAddress: BillingAddress | null }>(addressData)
        const plansPayload = unwrapData<{ plans: PlanOption[] }>(plansData)
        const apiKeysPayload = unwrapData<{ keys: ApiKey[] }>(apiKeysData)

        if (subscriptionData.success && subscriptionPayload?.subscription) {
          setSubscription(subscriptionPayload.subscription)
        }

        if (invoicesData.success && invoicesPayload?.invoices) {
          setInvoices(invoicesPayload.invoices)
        }

        if (paymentMethodsData.success && paymentMethodsPayload?.paymentMethods) {
          setPaymentMethods(paymentMethodsPayload.paymentMethods)
        }

        if (addressData.success && addressPayload?.billingAddress) {
          setBillingAddress(addressPayload.billingAddress)
        }

        if (plansData.success && plansPayload?.plans) {
          setPlans(plansPayload.plans)
        }

        if (apiKeysData.success && apiKeysPayload?.keys) {
          setApiKeys(apiKeysPayload.keys)
        }
      } catch (error) {
        console.error('Failed to fetch billing data:', error)
      }
    }

    fetchBillingData()
  }, [])

  useEffect(() => {
    const fetchDynamicOptions = async () => {
      try {
        const [languagesRes, timezonesRes, countriesRes, themesRes, notificationCategoriesRes, notificationPreferencesRes] = await Promise.all([
          fetch('/api/constants/languages'),
          fetch('/api/constants/timezones'),
          fetch('/api/constants/countries'),
          fetch('/api/constants/themes'),
          fetch('/api/user/notification-categories'),
          fetch('/api/user/notification-preferences'),
        ])

        const [languagesData, timezonesData, countriesData, themesData, notificationCategoriesData, notificationPreferencesData] = await Promise.all([
          languagesRes.json(),
          timezonesRes.json(),
          countriesRes.json(),
          themesRes.json(),
          notificationCategoriesRes.json(),
          notificationPreferencesRes.json(),
        ])

        const languagesPayload = unwrapData<{ languages: LanguageOption[] }>(languagesData)
        const timezonesPayload = unwrapData<{ timezones: TimezoneOption[] }>(timezonesData)
        const countriesPayload = unwrapData<{ countries: CountryOption[] }>(countriesData)
        const themesPayload = unwrapData<{ themes: ThemeOption[] }>(themesData)
        const notificationCategoriesPayload = unwrapData<{ categories: NotificationCategoryOption[] }>(notificationCategoriesData)
        const notificationPreferencesPayload = unwrapData<{ preferences: NotificationPreference }>(notificationPreferencesData)

        if (languagesData.success && languagesPayload?.languages) {
          setLanguageOptions(languagesPayload.languages)
        }

        if (timezonesData.success && timezonesPayload?.timezones) {
          setTimezoneOptions(timezonesPayload.timezones)
        }

        if (countriesData.success && countriesPayload?.countries) {
          setCountryOptions(countriesPayload.countries)
        }

        if (themesData.success && themesPayload?.themes) {
          setThemeOptions(themesPayload.themes)
        }

        if (notificationCategoriesData.success && notificationCategoriesPayload?.categories) {
          setNotificationCategories(notificationCategoriesPayload.categories)
          setNotificationPreferences(() => {
            const next: NotificationPreference = {
              ...(notificationPreferencesPayload?.preferences || {}),
            }
            for (const category of notificationCategoriesPayload.categories) {
              if (typeof next[category.id] !== 'boolean') {
                next[category.id] = category.defaultEnabled
              }
            }
            return next
          })
        }
      } catch (error) {
        console.error('Failed to fetch dynamic account options:', error)
      }
    }

    fetchDynamicOptions()
  }, [])

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString(user?.language || undefined, {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    })
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'text-green-400 bg-green-400/10'
      case 'paid': return 'text-green-400 bg-green-400/10'
      case 'trialing': return 'text-violet-400 bg-violet-400/10'
      case 'canceled': return 'text-red-400 bg-red-400/10'
      case 'past_due': return 'text-yellow-400 bg-yellow-400/10'
      case 'pending': return 'text-yellow-400 bg-yellow-400/10'
      case 'failed': return 'text-red-400 bg-red-400/10'
      default: return 'text-gray-400 bg-gray-400/10'
    }
  }

  const getPlanColor = (plan: string) => {
    switch (plan) {
      case 'free': return 'from-gray-500 to-gray-600'
      case 'starter': return 'from-violet-500 to-violet-600'
      case 'professional': return 'from-purple-500 to-purple-600'
      case 'enterprise': return 'from-orange-500 to-orange-600'
      default: return 'from-gray-500 to-gray-600'
    }
  }

  const formatMoney = (amount: number, currency: string) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency,
      maximumFractionDigits: 2,
    }).format(amount)
  }

  const resolveCurrentPlanId = () => {
    if (!subscription?.plan) {
      return user.plan
    }

    const match = plans.find((plan) => plan.name.toLowerCase() === subscription.plan.toLowerCase())
    return match?.id || user.plan
  }

  const getYearlyPlanPriceId = () => {
    if (!subscription) {
      return null
    }

    const currentMatch = plans.find((plan) => plan.name.toLowerCase() === subscription.plan.toLowerCase())
    if (!currentMatch) {
      return null
    }

    const yearlyMatch = plans.find((plan) => plan.productId === currentMatch.productId && plan.interval === 'year')
    return yearlyMatch?.priceId || null
  }

  // Wait for i18n to load from localStorage to prevent hydration mismatch
  if (!isLoaded || isLoading || !user) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-violet-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-400">Loading...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white">
      {/* Header */}
      <header className="border-b border-white/10 bg-black/20 backdrop-blur-xl sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Link href="/modules" className="text-gray-400 hover:text-white transition-colors">
                {t('nav.back')}
              </Link>
              <div className="w-px h-6 bg-white/20"></div>
              <h1 className="text-xl font-semibold">👤 {t('account.title')}</h1>
            </div>
            <div className="flex items-center gap-3">
              <div className={`px-3 py-1 rounded-full text-sm font-medium bg-gradient-to-r ${getPlanColor(subscription?.plan?.toLowerCase() || user.plan)}`}>
                {subscription?.plan || (user.plan.charAt(0).toUpperCase() + user.plan.slice(1))} Plan
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {actionMessage && (
          <div className={`mb-6 rounded-xl border px-4 py-3 ${
            actionMessage.type === 'success'
              ? 'border-green-500/30 bg-green-500/10 text-green-300'
              : 'border-red-500/30 bg-red-500/10 text-red-300'
          }`}>
            {actionMessage.text}
          </div>
        )}

        {/* Profile Card */}
        <div className="bg-white/5 rounded-2xl border border-white/10 p-6 mb-8">
          <div className="flex items-center gap-6">
            <div className="w-20 h-20 rounded-full bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center text-3xl font-bold">
              {user.name.charAt(0)}
            </div>
            <div className="flex-1">
              <h2 className="text-2xl font-bold">{user.name}</h2>
              <p className="text-gray-400">{user.email}</p>
              {user.company && <p className="text-gray-500 text-sm mt-1">🏢 {user.company}</p>}
            </div>
            <button
              onClick={() => setActiveTab('settings')}
              className="px-4 py-2 bg-white/10 hover:bg-white/20 rounded-lg transition-colors"
            >
              ✏️ {t('account.editProfile')}
            </button>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex gap-2 mb-8 overflow-x-auto pb-2">
          {[
            { id: 'overview', label: t('tabs.overview'), icon: '📊' },
            { id: 'subscription', label: t('tabs.subscription'), icon: '💳' },
            { id: 'billing', label: t('tabs.billing'), icon: '🧾' },
            { id: 'security', label: t('tabs.security'), icon: '🔒' },
            { id: 'settings', label: t('tabs.settings'), icon: '⚙️' }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as typeof activeTab)}
              className={`px-4 py-2 rounded-lg font-medium whitespace-nowrap transition-all ${
                activeTab === tab.id
                  ? 'bg-violet-600 text-white'
                  : 'bg-white/5 text-gray-400 hover:bg-white/10 hover:text-white'
              }`}
            >
              {tab.icon} {tab.label}
            </button>
          ))}
        </div>

        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Current Plan */}
            <div className="bg-white/5 rounded-2xl border border-white/10 p-6">
              <h3 className="text-lg font-semibold mb-4">{t('overview.currentPlan')}</h3>
              {subscription ? (
                <>
                  <div className={`p-4 rounded-xl bg-gradient-to-r ${getPlanColor(user.plan)} mb-4`}>
                    <div className="text-2xl font-bold">{subscription.plan}</div>
                    <div className="text-white/80">€{subscription.amount}/{subscription.interval === 'month' ? t('subscription.perMonth').replace('/', '') : t('subscription.perYear').replace('/', '')}</div>
                  </div>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-400">{t('overview.status')}:</span>
                      <span className={`px-2 py-0.5 rounded-full text-xs ${getStatusColor(subscription.status)}`}>
                        {subscription.status === 'active' ? t('common.active') : subscription.status}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">{t('overview.expires')}:</span>
                      <span>{formatDate(subscription.currentPeriodEnd)}</span>
                    </div>
                  </div>
                </>
              ) : (
                <div className="p-4 rounded-xl bg-gray-700/50 mb-4 text-center">
                  <div className="text-xl font-bold text-gray-400">{t('overview.free')}</div>
                  <div className="text-sm text-gray-500">{t('overview.noSubscription')}</div>
                </div>
              )}
              <button
                onClick={() => setShowUpgradeModal(true)}
                className="w-full mt-4 px-4 py-2 bg-violet-600 hover:bg-violet-500 rounded-lg font-medium transition-colors"
              >
                🚀 {subscription ? t('overview.upgradePlan') : t('overview.choosePlan')}
              </button>
            </div>

            {/* Usage Stats */}
            <div className="bg-white/5 rounded-2xl border border-white/10 p-6">
              <h3 className="text-lg font-semibold mb-4">{t('overview.usage')}</h3>
              <div className="text-center py-6 text-gray-400">
                <div className="text-4xl mb-2">📊</div>
                <div>{t('overview.usageStats')}</div>
              </div>
            </div>

            {/* Quick Actions */}
            <div className="bg-white/5 rounded-2xl border border-white/10 p-6">
              <h3 className="text-lg font-semibold mb-4">{t('overview.quickActions')}</h3>
              <div className="space-y-3">
                <button
                  onClick={() => setActiveTab('subscription')}
                  className="w-full flex items-center gap-3 px-4 py-3 bg-white/5 hover:bg-white/10 rounded-lg transition-colors text-left"
                >
                  <span className="text-2xl">📊</span>
                  <div>
                    <div className="font-medium">{t('overview.manageSubscription')}</div>
                    <div className="text-sm text-gray-400">{t('overview.viewPlan')}</div>
                  </div>
                </button>
                <button
                  onClick={() => setActiveTab('settings')}
                  className="w-full flex items-center gap-3 px-4 py-3 bg-white/5 hover:bg-white/10 rounded-lg transition-colors text-left"
                >
                  <span className="text-2xl">⚙️</span>
                  <div>
                    <div className="font-medium">{t('overview.profileSettings')}</div>
                    <div className="text-sm text-gray-400">{t('overview.editInfo')}</div>
                  </div>
                </button>
                <button
                  onClick={() => setActiveTab('security')}
                  className="w-full flex items-center gap-3 px-4 py-3 bg-white/5 hover:bg-white/10 rounded-lg transition-colors text-left"
                >
                  <span className="text-2xl">🔒</span>
                  <div>
                    <div className="font-medium">{t('overview.securitySettings')}</div>
                    <div className="text-sm text-gray-400">{t('overview.passwordAnd2FA')}</div>
                  </div>
                </button>
                <a href={supportEmail ? `mailto:${supportEmail}` : undefined} className="w-full flex items-center gap-3 px-4 py-3 bg-white/5 hover:bg-white/10 rounded-lg transition-colors text-left">
                  <span className="text-2xl">📧</span>
                  <div>
                    <div className="font-medium">{t('overview.contactSupport')}</div>
                    <div className="text-sm text-gray-400">{supportEmail || t('common.inactive')}</div>
                  </div>
                </a>
              </div>
            </div>
          </div>
        )}

        {/* Subscription Tab */}
        {activeTab === 'subscription' && (
          <div className="space-y-6">
            {/* Current Subscription */}
            <div className="bg-white/5 rounded-2xl border border-white/10 p-6">
              <h3 className="text-lg font-semibold mb-4">{t('subscription.current')}</h3>
              {subscription ? (
                <>
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div className="p-4 bg-white/5 rounded-xl">
                      <div className="text-gray-400 text-sm mb-1">{t('subscription.plan')}</div>
                      <div className="text-xl font-bold">{subscription.plan}</div>
                    </div>
                    <div className="p-4 bg-white/5 rounded-xl">
                      <div className="text-gray-400 text-sm mb-1">{t('subscription.price')}</div>
                      <div className="text-xl font-bold">€{subscription.amount}<span className="text-sm font-normal text-gray-400">{subscription.interval === 'month' ? t('subscription.perMonth') : t('subscription.perYear')}</span></div>
                    </div>
                    <div className="p-4 bg-white/5 rounded-xl">
                      <div className="text-gray-400 text-sm mb-1">{t('subscription.status')}</div>
                      <div className={`inline-block px-2 py-1 rounded-full text-sm ${getStatusColor(subscription.status)}`}>
                        {subscription.status === 'active' ? '✓ ' + t('common.active') : subscription.status}
                      </div>
                    </div>
                    <div className="p-4 bg-white/5 rounded-xl">
                      <div className="text-gray-400 text-sm mb-1">{t('subscription.renews')}</div>
                      <div className="text-xl font-bold">{formatDate(subscription.currentPeriodEnd)}</div>
                    </div>
                  </div>
                  <div className="flex gap-3 mt-6">
                    <button
                      onClick={() => setShowUpgradeModal(true)}
                      className="px-6 py-2 bg-violet-600 hover:bg-violet-500 rounded-lg font-medium transition-colors"
                    >
                      🚀 {t('subscription.upgrade')}
                    </button>
                    <button
                      onClick={() => {
                        const yearlyPlanPriceId = getYearlyPlanPriceId()
                        if (yearlyPlanPriceId) {
                          void handleUpgrade(yearlyPlanPriceId)
                        }
                      }}
                      disabled={isCheckoutLoading || !getYearlyPlanPriceId()}
                      className="px-6 py-2 bg-white/10 hover:bg-white/20 disabled:opacity-50 rounded-lg font-medium transition-colors"
                    >
                      {t('subscription.switchToYearly')}
                    </button>
                    <button
                      onClick={handleCancelSubscription}
                      disabled={isSubscriptionActionLoading}
                      className="px-6 py-2 bg-red-600/20 hover:bg-red-600/30 disabled:opacity-50 text-red-400 rounded-lg font-medium transition-colors"
                    >
                      {t('subscription.cancel')}
                    </button>
                  </div>
                </>
              ) : (
                <div className="text-center py-8">
                  <div className="text-gray-400 mb-4">{t('subscription.noActive')}</div>
                  <button
                    onClick={() => setShowUpgradeModal(true)}
                    className="px-6 py-3 bg-violet-600 hover:bg-violet-500 rounded-lg font-medium transition-colors"
                  >
                    🚀 {t('overview.choosePlan')}
                  </button>
                </div>
              )}
            </div>

            {/* Available Plans */}
            <div>
              <h3 className="text-lg font-semibold mb-4">{t('subscription.availablePlans')}</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {plans.map(plan => (
                  <div
                    key={plan.priceId}
                    className={`relative p-6 rounded-2xl border transition-all ${
                      resolveCurrentPlanId() === plan.id
                        ? 'bg-violet-600/20 border-violet-500'
                        : 'bg-white/5 border-white/10 hover:border-white/30'
                    }`}
                  >
                    {plan.popular && (
                      <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-1 bg-purple-600 rounded-full text-xs font-medium">
                        {t('subscription.mostPopular')}
                      </div>
                    )}
                    <div className="text-lg font-bold mb-2">{plan.name}</div>
                    <div className="text-3xl font-bold mb-4">
                      {formatMoney(plan.amount, plan.currency)}
                      <span className="text-sm font-normal text-gray-400">{plan.interval === 'month' ? t('subscription.perMonth') : t('subscription.perYear')}</span>
                    </div>
                    <ul className="space-y-2 mb-6">
                      {plan.features.slice(0, 5).map((feature, index) => (
                        <li key={index} className="flex items-center gap-2 text-sm text-gray-300">
                          <span className="text-green-400">✓</span>
                          {feature}
                        </li>
                      ))}
                      {plan.features.length > 5 && (
                        <li className="text-sm text-gray-500">+{plan.features.length - 5} {t('subscription.more')}</li>
                      )}
                    </ul>
                    {resolveCurrentPlanId() === plan.id ? (
                      <button disabled className="w-full py-2 bg-white/10 rounded-lg font-medium text-gray-400 cursor-not-allowed">
                        {t('subscription.currentPlan')}
                      </button>
                    ) : (
                      <button
                        onClick={() => void handleUpgrade(plan.priceId)}
                        disabled={isCheckoutLoading}
                        className="w-full py-2 bg-violet-600 hover:bg-violet-500 rounded-lg font-medium transition-colors"
                      >
                        {plan.amount >= (subscription?.amount || 0) ? t('subscription.upgrade') : t('subscription.downgrade')}
                      </button>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Billing Tab */}
        {activeTab === 'billing' && (
          <div className="space-y-6">
            {/* Payment Methods */}
            <div className="bg-white/5 rounded-2xl border border-white/10 p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold">{t('billing.paymentMethods')}</h3>
                <button
                  onClick={handleOpenBillingPortal}
                  disabled={isPortalLoading}
                  className="px-4 py-2 bg-violet-600 hover:bg-violet-500 disabled:opacity-50 rounded-lg font-medium transition-colors"
                >
                  {t('billing.addMethod')}
                </button>
              </div>
              <div className="space-y-3">
                {paymentMethods.length > 0 ? (
                  paymentMethods.map(method => (
                    <div key={method.id} className="flex items-center justify-between p-4 bg-white/5 rounded-xl">
                      <div className="flex items-center gap-4">
                        <div className="text-3xl">
                          {method.type === 'card' ? '💳' : method.type === 'paypal' ? '🅿️' : '🏦'}
                        </div>
                        <div>
                          <div className="font-medium">
                            {method.brand} •••• {method.last4}
                          </div>
                          <div className="text-sm text-gray-400">
                            {t('billing.expires')} {method.expiryMonth}/{method.expiryYear}
                          </div>
                        </div>
                        {method.isDefault && (
                          <span className="px-2 py-1 bg-green-500/20 text-green-400 text-xs rounded-full">
                            {t('billing.default')}
                          </span>
                        )}
                      </div>
                      <div className="flex gap-2">
                        {!method.isDefault && (
                          <button
                            onClick={() => handleSetDefaultPaymentMethod(method.id)}
                            disabled={busyPaymentMethodId === method.id}
                            className="px-3 py-1 bg-white/10 hover:bg-white/20 disabled:opacity-50 rounded-lg text-sm transition-colors"
                          >
                            Set default
                          </button>
                        )}
                        <button
                          onClick={handleOpenBillingPortal}
                          disabled={isPortalLoading}
                          className="px-3 py-1 bg-white/10 hover:bg-white/20 disabled:opacity-50 rounded-lg text-sm transition-colors"
                        >
                          {t('common.edit')}
                        </button>
                        <button
                          onClick={() => handleRemovePaymentMethod(method.id)}
                          disabled={busyPaymentMethodId === method.id}
                          className="px-3 py-1 bg-red-600/20 hover:bg-red-600/30 disabled:opacity-50 text-red-400 rounded-lg text-sm transition-colors"
                        >
                          {t('billing.remove')}
                        </button>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="text-center py-8 text-gray-400">
                    <div className="text-4xl mb-2">💳</div>
                    <div>{t('billing.noMethods')}</div>
                    <div className="text-sm mt-1">{t('billing.addCardToSubscribe')}</div>
                  </div>
                )}
              </div>
            </div>

            {/* Billing Address */}
            <div className="bg-white/5 rounded-2xl border border-white/10 p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold">{t('billing.billingAddress')}</h3>
                <button
                  onClick={() => setShowAddressModal(true)}
                  className="px-4 py-2 bg-white/10 hover:bg-white/20 rounded-lg font-medium transition-colors"
                >
                  ✏️ {t('common.edit')}
                </button>
              </div>
              {billingAddress ? (
                <div className="text-gray-300 space-y-1">
                  {billingAddress.name && <p className="font-medium">{billingAddress.name}</p>}
                  <p>{billingAddress.line1}</p>
                  {billingAddress.line2 && <p>{billingAddress.line2}</p>}
                  <p>{billingAddress.city}, {billingAddress.postal_code}</p>
                  {billingAddress.state && <p>{billingAddress.state}</p>}
                  <p>{billingAddress.country}</p>
                  {billingAddress.phone && <p className="text-gray-400 mt-2">📞 {billingAddress.phone}</p>}
                </div>
              ) : (
                <div className="text-gray-400 text-center py-4">
                  <p>{t('billing.addressOnFirstPayment')}</p>
                </div>
              )}
            </div>

            {/* Invoices */}
            <div className="bg-white/5 rounded-2xl border border-white/10 p-6">
              <h3 className="text-lg font-semibold mb-4">{t('billing.invoiceHistory')}</h3>
              {invoices.length > 0 ? (
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="text-left text-gray-400 text-sm border-b border-white/10">
                        <th className="pb-3 font-medium">{t('billing.invoice')}</th>
                        <th className="pb-3 font-medium">{t('billing.date')}</th>
                        <th className="pb-3 font-medium">{t('billing.amount')}</th>
                        <th className="pb-3 font-medium">{t('subscription.status')}</th>
                        <th className="pb-3 font-medium">{t('billing.actions')}</th>
                      </tr>
                    </thead>
                    <tbody>
                      {invoices.map(invoice => (
                        <tr key={invoice.id} className="border-b border-white/5">
                          <td className="py-4 font-mono text-sm">{invoice.id}</td>
                          <td className="py-4">{formatDate(invoice.date)}</td>
                          <td className="py-4 font-medium">€{invoice.amount}</td>
                          <td className="py-4">
                            <span className={`px-2 py-1 rounded-full text-xs ${getStatusColor(invoice.status)}`}>
                              {invoice.status === 'paid' ? t('billing.paid') : invoice.status}
                            </span>
                          </td>
                          <td className="py-4">
                            {invoice.pdfUrl ? (
                              <a
                                href={invoice.pdfUrl}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="px-3 py-1 bg-white/10 hover:bg-white/20 rounded-lg text-sm transition-colors inline-block"
                              >
                                {t('billing.downloadPDF')}
                              </a>
                            ) : (
                              <button
                                disabled
                                className="px-3 py-1 bg-white/5 text-gray-500 rounded-lg text-sm cursor-not-allowed"
                              >
                                {t('billing.downloadPDF')}
                              </button>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="text-center py-8 text-gray-400">
                  <div className="text-4xl mb-2">🧾</div>
                  <div>{t('billing.noInvoices')}</div>
                  <div className="text-sm mt-1">{t('billing.invoicesAfterPayment')}</div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Security Tab */}
        {activeTab === 'security' && (
          <div className="space-y-6">
            {/* Password */}
            <div className="bg-white/5 rounded-2xl border border-white/10 p-6">
              <h3 className="text-lg font-semibold mb-4">🔐 {t('security.password')}</h3>
              <p className="text-gray-400 mb-4">{t('security.twoFactorDesc')}</p>
              <button
                onClick={() => setActionMessage({ type: 'success', text: 'Use the authenticated security center to change your password.' })}
                className="px-6 py-2 bg-violet-600 hover:bg-violet-500 rounded-lg font-medium transition-colors"
              >
                {t('security.changePassword')}
              </button>
            </div>

            {/* Two-Factor Auth */}
            <div className="bg-white/5 rounded-2xl border border-white/10 p-6">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-semibold mb-2">🛡️ {t('security.twoFactor')}</h3>
                  <p className="text-gray-400">{t('security.twoFactorDesc')}</p>
                </div>
                <div className="flex items-center gap-4">
                  <span className="px-3 py-1 bg-red-500/20 text-red-400 rounded-full text-sm">{t('security.disabled')}</span>
                  <button
                    onClick={() => setActionMessage({ type: 'success', text: 'Two-factor authentication can be enabled from the identity provider security screen.' })}
                    className="px-6 py-2 bg-green-600 hover:bg-green-500 rounded-lg font-medium transition-colors"
                  >
                    {t('security.enable')}
                  </button>
                </div>
              </div>
            </div>

            {/* Active Sessions */}
            <div className="bg-white/5 rounded-2xl border border-white/10 p-6">
              <h3 className="text-lg font-semibold mb-4">📱 {t('security.activeSessions')}</h3>
              <div className="space-y-3">
                <div className="flex items-center justify-between p-4 bg-white/5 rounded-xl">
                  <div className="flex items-center gap-4">
                    <span className="text-2xl">💻</span>
                    <div>
                      <div className="font-medium">{t('security.currentSession')}</div>
                      <div className="text-sm text-gray-400">{t('security.thisBrowser')}</div>
                    </div>
                    <span className="px-2 py-1 bg-green-500/20 text-green-400 text-xs rounded-full">
                      {t('common.active')}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* API Keys */}
            <div className="bg-white/5 rounded-2xl border border-white/10 p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold">🔑 {t('security.apiKeys')}</h3>
                <button
                  onClick={handleGenerateApiKey}
                  disabled={isGeneratingKey}
                  className="px-4 py-2 bg-violet-600 hover:bg-violet-500 disabled:bg-violet-600/50 disabled:cursor-not-allowed rounded-lg font-medium transition-colors flex items-center gap-2"
                >
                  {isGeneratingKey ? (
                    <>
                      <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"/>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
                      </svg>
                      {t('common.loading')}
                    </>
                  ) : (
                    t('security.generateKey')
                  )}
                </button>
              </div>
              {latestApiKeySecret && (
                <div className="mb-4 rounded-lg border border-yellow-500/30 bg-yellow-500/10 p-3">
                  <p className="text-sm text-yellow-200 mb-2">Copy this API key now. For security reasons it is shown only once.</p>
                  <div className="font-mono text-xs text-yellow-100 break-all mb-3">{latestApiKeySecret}</div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleCopyApiKey({ id: 'latest', key: latestApiKeySecret, name: 'Latest', createdAt: new Date().toISOString() })}
                      className="px-3 py-1 bg-white/10 hover:bg-white/20 rounded-lg text-sm transition-colors"
                    >
                      {t('security.copy')}
                    </button>
                    <button
                      onClick={() => setLatestApiKeySecret(null)}
                      className="px-3 py-1 bg-white/10 hover:bg-white/20 rounded-lg text-sm transition-colors"
                    >
                      {t('common.close')}
                    </button>
                  </div>
                </div>
              )}
              {apiKeys.length > 0 ? (
                <div className="space-y-3">
                  {apiKeys.map(apiKey => (
                    <div key={apiKey.id} className="flex items-center justify-between p-4 bg-white/5 rounded-xl">
                      <div className="flex-1 min-w-0">
                        <div className="font-medium">{apiKey.name}</div>
                        <div className="font-mono text-sm text-gray-400 truncate">
                          {apiKey.key}
                        </div>
                        <div className="text-xs text-gray-500 mt-1">
                          {t('security.created')}: {new Date(apiKey.createdAt).toLocaleDateString()}
                        </div>
                      </div>
                      <div className="flex gap-2 ml-4">
                        <button
                          onClick={() => handleCopyApiKey(apiKey)}
                          disabled={apiKey.key.includes('*')}
                          className="px-3 py-1 bg-white/10 hover:bg-white/20 rounded-lg text-sm transition-colors"
                        >
                          {copiedKeyId === apiKey.id ? t('security.copied') : t('security.copy')}
                        </button>
                        <button
                          onClick={() => handleRevokeApiKey(apiKey.id)}
                          className="px-3 py-1 bg-red-600/20 hover:bg-red-600/30 text-red-400 rounded-lg text-sm transition-colors"
                        >
                          {t('security.revoke')}
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-6 text-gray-400">
                  <div className="text-4xl mb-2">🔑</div>
                  <div>{t('security.noKeys')}</div>
                  <div className="text-sm mt-1">{t('security.generateToUse')}</div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Settings Tab */}
        {activeTab === 'settings' && (
          <div className="space-y-6">
            {/* Profile Settings */}
            <div className="bg-white/5 rounded-2xl border border-white/10 p-6">
              <h3 className="text-lg font-semibold mb-4">👤 {t('settings.profileInfo')}</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm text-gray-400 mb-2">{t('settings.fullName')}</label>
                  <input
                    type="text"
                    value={user.name}
                    onChange={(e) => setUser({...user, name: e.target.value})}
                    className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg focus:outline-none focus:border-violet-500"
                  />
                </div>
                <div>
                  <label className="block text-sm text-gray-400 mb-2">{t('settings.email')}</label>
                  <input
                    type="email"
                    value={user.email}
                    onChange={(e) => setUser({...user, email: e.target.value})}
                    className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg focus:outline-none focus:border-violet-500"
                  />
                </div>
                <div>
                  <label className="block text-sm text-gray-400 mb-2">{t('settings.company')}</label>
                  <input
                    type="text"
                    value={user.company || ''}
                    onChange={(e) => setUser({...user, company: e.target.value})}
                    className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg focus:outline-none focus:border-violet-500"
                  />
                </div>
                <div>
                  <label className="block text-sm text-gray-400 mb-2">{t('settings.phone')}</label>
                  <input
                    type="tel"
                    value={user.phone || ''}
                    onChange={(e) => setUser({...user, phone: e.target.value})}
                    className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg focus:outline-none focus:border-violet-500"
                  />
                </div>
              </div>
              <div className="mt-6 flex flex-col gap-3">
                <button
                  onClick={handleSaveProfile}
                  disabled={isSavingProfile}
                  className="w-full md:w-auto px-8 py-3 bg-violet-600 hover:bg-violet-500 disabled:bg-violet-600/50 disabled:cursor-not-allowed rounded-lg font-medium transition-colors flex items-center justify-center gap-2"
                >
                  {isSavingProfile ? (
                    <>
                      <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"/>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
                      </svg>
                      <span>{t('settings.savingChanges')}</span>
                    </>
                  ) : (
                    <span>{t('settings.saveChanges')}</span>
                  )}
                </button>
                {profileSaveMessage && (
                  <div className={`p-3 rounded-lg text-center ${
                    profileSaveMessage.type === 'success'
                      ? 'bg-green-500/20 border border-green-500/30 text-green-400'
                      : 'bg-red-500/20 border border-red-500/30 text-red-400'
                  }`}>
                    {profileSaveMessage.text}
                  </div>
                )}
              </div>
            </div>

            {/* Preferences */}
            <div className="bg-white/5 rounded-2xl border border-white/10 p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold">⚙️ {t('preferences.title')}</h3>
                {preferencesMessage && (
                  <span className={`text-sm px-3 py-1 rounded-full ${
                    preferencesMessage.type === 'success' ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
                  }`}>
                    {preferencesMessage.text}
                  </span>
                )}
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Language Selection */}
                <div className="space-y-3">
                  <label className="block text-sm font-medium text-white">🌐 {t('preferences.language')}</label>
                  <p className="text-xs text-gray-400 -mt-2">{t('preferences.languageDesc')}</p>
                  <div className="grid grid-cols-2 gap-2">
                    {languageOptions.map(lang => (
                      <button
                        key={lang.code}
                        onClick={() => {
                          handleLanguageChange(lang.code as Language)
                        }}
                        className={`flex items-center gap-2 px-3 py-2 rounded-lg border transition-all ${
                          user.language === lang.code
                            ? 'bg-violet-600/30 border-violet-500 text-white'
                            : 'bg-white/5 border-white/10 text-gray-300 hover:border-white/30'
                        }`}
                      >
                        <span className="text-sm">{lang.name}</span>
                        {user.language === lang.code && <span className="ml-auto text-violet-400">✓</span>}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Timezone Selection */}
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <div>
                      <label className="block text-sm font-medium text-white">🕐 {t('preferences.timezone')}</label>
                      <p className="text-xs text-gray-400">{t('preferences.timezoneDesc')}</p>
                    </div>
                    {detectedTimezone && (
                      <button
                        onClick={handleAutoDetectTimezone}
                        className="px-3 py-1 text-xs bg-purple-600/30 hover:bg-purple-600/50 border border-purple-500/50 text-purple-300 rounded-lg transition-all"
                      >
                        {t('preferences.autoDetect')}
                      </button>
                    )}
                  </div>
                  {detectedTimezone && user.timezone !== detectedTimezone && (
                    <div className="p-2 bg-yellow-500/10 border border-yellow-500/30 rounded-lg text-xs text-yellow-400">
                      {t('preferences.detectedZone')}: <strong>{detectedTimezone}</strong>
                    </div>
                  )}
                  <div className="space-y-2 max-h-48 overflow-y-auto">
                    {timezoneOptions.map(zone => (
                      <button
                        key={zone.id}
                        onClick={() => handleTimezoneChange(zone.id)}
                        className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg border transition-all ${
                          user.timezone === zone.id
                            ? 'bg-violet-600/30 border-violet-500 text-white'
                            : 'bg-white/5 border-white/10 text-gray-300 hover:border-white/30'
                        }`}
                      >
                        <span className="text-sm flex-1 text-left">{zone.label}</span>
                        <span className="text-xs text-gray-400">{zone.offset}</span>
                        {user.timezone === zone.id && <span className="text-violet-400">✓</span>}
                      </button>
                    ))}
                  </div>
                </div>
              </div>

              {/* Theme & Display */}
              <div className="mt-6 pt-6 border-t border-white/10">
                <h4 className="text-sm font-medium text-white mb-4">🎨 {t('preferences.theme')}</h4>
                <p className="text-xs text-gray-400 mb-3">{t('preferences.themeDesc')}</p>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                  {themeOptions.map((theme) => (
                    <button key={theme.id} className="flex items-center gap-3 px-4 py-3 bg-white/5 border border-white/10 rounded-lg hover:border-white/30 transition-all">
                      <div className="text-left">
                        <div className="text-sm font-medium">{theme.name}</div>
                        <div className="text-xs text-gray-500">{theme.id}</div>
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Notifications */}
            <div className="bg-white/5 rounded-2xl border border-white/10 p-6">
              <h3 className="text-lg font-semibold mb-4">🔔 {t('notifications.title')}</h3>
              <div className="space-y-4">
                {notificationCategories.map(item => (
                  <div key={item.id} className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
                    <div>
                      <div className="font-medium">{item.label}</div>
                      <div className="text-sm text-gray-400">{item.description}</div>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={notificationPreferences[item.id] ?? false}
                        onChange={() => {
                          void handleToggleNotification(item.id)
                        }}
                        className="sr-only peer"
                      />
                      <div className="w-11 h-6 bg-gray-600 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:bg-violet-600 after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all"></div>
                    </label>
                  </div>
                ))}
              </div>
            </div>

            {/* Danger Zone */}
            <div className="bg-red-900/20 rounded-2xl border border-red-500/30 p-6">
              <h3 className="text-lg font-semibold mb-4 text-red-400">{t('danger.title')}</h3>
              <div className="space-y-4">
                <div className="flex items-center justify-between p-4 bg-white/5 rounded-lg">
                  <div>
                    <div className="font-medium">{t('danger.exportData')}</div>
                    <div className="text-sm text-gray-400">{t('danger.exportDataDesc')}</div>
                  </div>
                  <button
                    onClick={handleExportData}
                    className="px-4 py-2 bg-white/10 hover:bg-white/20 rounded-lg font-medium transition-colors"
                  >
                    {t('danger.download')}
                  </button>
                </div>
                <div className="flex items-center justify-between p-4 bg-white/5 rounded-lg">
                  <div>
                    <div className="font-medium text-red-400">{t('danger.deleteAccount')}</div>
                    <div className="text-sm text-gray-400">{t('danger.deleteAccountDesc')}</div>
                  </div>
                  <button
                    onClick={handleDeleteAccount}
                    className="px-4 py-2 bg-red-600 hover:bg-red-500 rounded-lg font-medium transition-colors"
                  >
                    {t('danger.deleteButton')}
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Upgrade Modal - Professional Pricing */}
      {showUpgradeModal && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-gradient-to-b from-slate-800 to-slate-900 rounded-2xl w-full max-w-4xl border border-white/10 overflow-hidden">
            {/* Header */}
            <div className="bg-gradient-to-r from-violet-600 to-purple-600 px-8 py-6">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-2xl font-bold">{t('upgrade.title')}</h2>
                  <p className="text-violet-100 mt-1">{t('upgrade.subtitle')}</p>
                </div>
                <button
                  onClick={() => setShowUpgradeModal(false)}
                  className="w-10 h-10 rounded-full bg-white/20 hover:bg-white/30 flex items-center justify-center transition-colors"
                >
                  ×
                </button>
              </div>
            </div>

            {/* Pricing Cards */}
            <div className="p-8">
              <div className="grid md:grid-cols-3 gap-6">
                {plans.slice(0, 3).map((plan) => (
                  <div
                    key={plan.priceId}
                    className={`rounded-xl p-6 border transition-all ${
                      plan.popular
                        ? 'bg-gradient-to-b from-violet-600/20 to-purple-600/20 border-2 border-violet-500 relative'
                        : 'bg-white/5 border border-white/10 hover:border-violet-500/50'
                    }`}
                  >
                    {plan.popular && (
                      <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-4 py-1 bg-gradient-to-r from-violet-500 to-purple-500 rounded-full text-xs font-bold">
                        {t('subscription.mostPopular')}
                      </div>
                    )}
                    <div className="text-center mb-6">
                      <h3 className="text-xl font-bold mt-2">{plan.name}</h3>
                      <div className="mt-4">
                        <span className="text-4xl font-bold">{formatMoney(plan.amount, plan.currency)}</span>
                        <span className="text-gray-400">{plan.interval === 'month' ? t('subscription.perMonth') : t('subscription.perYear')}</span>
                      </div>
                    </div>
                    <ul className="space-y-3 mb-6 text-sm">
                      {plan.features.slice(0, 6).map((feature, index) => (
                        <li key={index} className="flex items-center gap-2"><span className="text-green-400">✓</span>{feature}</li>
                      ))}
                    </ul>
                    {resolveCurrentPlanId() === plan.id ? (
                      <button disabled className="w-full py-3 bg-white/10 rounded-lg font-medium text-gray-400 cursor-not-allowed">
                        {t('subscription.currentPlan')}
                      </button>
                    ) : (
                      <button
                        onClick={() => void handleUpgrade(plan.priceId)}
                        disabled={isCheckoutLoading}
                        className="w-full py-3 bg-violet-600 hover:bg-violet-500 disabled:opacity-50 rounded-lg font-medium transition-colors"
                      >
                        {isCheckoutLoading ? t('upgrade.processing') : t('upgrade.upgradeNow')}
                      </button>
                    )}
                  </div>
                ))}
              </div>

              {/* Footer */}
              <div className="mt-8 text-center">
                <p className="text-gray-400 text-sm">
                  💳 Secure payment via Stripe • 🔄 Cancel anytime • 📧 Questions? {supportEmail ? <a href={`mailto:${supportEmail}`} className="text-violet-400 hover:underline">{supportEmail}</a> : t('common.inactive')}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Billing Address Modal */}
      {showAddressModal && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 rounded-2xl border border-white/10 max-w-lg w-full p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold">{t('billing.editAddress')}</h2>
              <button
                onClick={() => setShowAddressModal(false)}
                className="text-gray-400 hover:text-white text-2xl"
              >
                ×
              </button>
            </div>
            <form
              onSubmit={async (e) => {
                e.preventDefault()
                const form = e.target as HTMLFormElement
                const formData = new FormData(form)

                setIsSavingAddress(true)
                try {
                  const response = await fetch('/api/billing/billing-address', {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                      name: formData.get('name'),
                      line1: formData.get('line1'),
                      line2: formData.get('line2') || undefined,
                      city: formData.get('city'),
                      state: formData.get('state') || undefined,
                      postal_code: formData.get('postal_code'),
                      country: formData.get('country'),
                      phone: formData.get('phone') || undefined,
                    }),
                  })

                  const result = await response.json()
                  if (result.success) {
                    setBillingAddress({
                      name: formData.get('name') as string,
                      line1: formData.get('line1') as string,
                      line2: formData.get('line2') as string || undefined,
                      city: formData.get('city') as string,
                      state: formData.get('state') as string || undefined,
                      postal_code: formData.get('postal_code') as string,
                      country: formData.get('country') as string,
                      phone: formData.get('phone') as string || undefined,
                    })
                    setShowAddressModal(false)
                  } else {
                    alert(result.error || t('settings.saveFailed'))
                  }
                } catch (error) {
                  console.error('Error saving address:', error)
                  alert(t('settings.connectionError'))
                } finally {
                  setIsSavingAddress(false)
                }
              }}
              className="space-y-4"
            >
              <div>
                <label className="block text-sm text-gray-400 mb-1">{t('billing.fullName')}</label>
                <input
                  type="text"
                  name="name"
                  defaultValue={billingAddress?.name || ''}
                  className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg focus:outline-none focus:border-violet-500"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-1">{t('billing.addressLine1')} *</label>
                <input
                  type="text"
                  name="line1"
                  required
                  defaultValue={billingAddress?.line1 || ''}
                  className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg focus:outline-none focus:border-violet-500"
                  placeholder={t('billing.streetAddress')}
                />
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-1">{t('billing.addressLine2')}</label>
                <input
                  type="text"
                  name="line2"
                  defaultValue={billingAddress?.line2 || ''}
                  className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg focus:outline-none focus:border-violet-500"
                  placeholder={t('billing.aptSuite')}
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm text-gray-400 mb-1">{t('billing.city')} *</label>
                  <input
                    type="text"
                    name="city"
                    required
                    defaultValue={billingAddress?.city || ''}
                    className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg focus:outline-none focus:border-violet-500"
                  />
                </div>
                <div>
                  <label className="block text-sm text-gray-400 mb-1">{t('billing.postalCode')} *</label>
                  <input
                    type="text"
                    name="postal_code"
                    required
                    defaultValue={billingAddress?.postal_code || ''}
                    className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg focus:outline-none focus:border-violet-500"
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm text-gray-400 mb-1">{t('billing.stateRegion')}</label>
                  <input
                    type="text"
                    name="state"
                    defaultValue={billingAddress?.state || ''}
                    className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg focus:outline-none focus:border-violet-500"
                  />
                </div>
                <div>
                  <label className="block text-sm text-gray-400 mb-1">{t('billing.country')} *</label>
                  <select
                    name="country"
                    required
                    defaultValue={billingAddress?.country || countryOptions[0]?.code || ''}
                    className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg focus:outline-none focus:border-violet-500"
                  >
                    {countryOptions.map((country) => (
                      <option key={country.code} value={country.code}>{country.name}</option>
                    ))}
                  </select>
                </div>
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-1">{t('billing.phone')}</label>
                <input
                  type="tel"
                  name="phone"
                  defaultValue={billingAddress?.phone || ''}
                  className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg focus:outline-none focus:border-violet-500"
                  placeholder={t('billing.phone')}
                />
              </div>
              <div className="flex gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowAddressModal(false)}
                  className="flex-1 py-2 bg-white/10 hover:bg-white/20 rounded-lg font-medium transition-colors"
                >
                  {t('common.cancel')}
                </button>
                <button
                  type="submit"
                  disabled={isSavingAddress}
                  className="flex-1 py-2 bg-violet-600 hover:bg-violet-500 disabled:bg-violet-600/50 rounded-lg font-medium transition-colors flex items-center justify-center gap-2"
                >
                  {isSavingAddress ? (
                    <>
                      <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"/>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
                      </svg>
                      {t('common.saving')}
                    </>
                  ) : (
                    t('common.save')
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}







