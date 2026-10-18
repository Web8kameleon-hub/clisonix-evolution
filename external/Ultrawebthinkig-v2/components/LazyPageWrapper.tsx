import React, { ReactNode } from 'react'

type LazyPageWrapperProps = {
  title: string
  description?: string
  gradient?: string
  children: ReactNode
}

export default function LazyPageWrapper({
  title,
  description,
  gradient,
  children,
}: LazyPageWrapperProps) {
  return (
    <main className="min-h-screen p-6 md:p-8">
      <section className="mx-auto max-w-7xl">
        <header
          className={`mb-6 rounded-xl border border-white/10 bg-gradient-to-r ${gradient ?? 'from-slate-700 to-slate-900'} p-6 text-white shadow-lg`}
        >
          <h1 className="text-2xl font-semibold md:text-3xl">{title}</h1>
          {description ? <p className="mt-2 text-sm text-white/85 md:text-base">{description}</p> : null}
        </header>
        <div className="rounded-xl border border-white/10 bg-black/20 p-4 md:p-6">{children}</div>
      </section>
    </main>
  )
}
