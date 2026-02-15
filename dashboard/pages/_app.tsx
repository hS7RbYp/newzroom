import React, { useState } from 'react'
import type { AppProps } from 'next/app'
import '../styles/globals.css'

export default function App({ Component, pageProps }: AppProps) {
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center">
            <h1 className="text-3xl font-bold text-gray-900">
              📰 Newsroom AI - Approval Dashboard
            </h1>
            <div className="flex gap-2 text-sm text-gray-600">
              <span className="px-3 py-1 bg-green-100 text-green-800 rounded">
                Live
              </span>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
        <Component {...pageProps} />
      </main>

      <footer className="bg-gray-100 mt-12 py-4 text-center text-sm text-gray-600">
        <p>Newsroom AI Article Approval System • Built with Next.js & FastAPI</p>
      </footer>
    </div>
  )
}
