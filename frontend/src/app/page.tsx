'use client'

import { useState } from 'react'

interface ChatResponse {
  answer: string
  sources: Array<{
    fonte: string
    norma: string
    numero_norma: string
    artigo: string | null
    ano: number
    tema: string
    url: string | null
  }>
  citations: string[]
  has_sufficient_context: boolean
  timestamp: string
}

export default function Home() {
  const [question, setQuestion] = useState('')
  const [domain, setDomain] = useState<'pix' | 'open_finance'>('pix')
  const [response, setResponse] = useState<ChatResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!question.trim()) return

    setLoading(true)
    setError(null)
    setResponse(null)

    try {
      const res = await fetch(`${apiUrl}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question, domain }),
      })

      if (!res.ok) {
        const errorText = await res.text()
        throw new Error(`Erro ${res.status}: ${errorText || res.statusText}`)
      }

      const data = await res.json()
      
      // Validar estrutura da resposta
      if (!data.answer) {
        throw new Error('Resposta inválida do servidor')
      }
      
      setResponse(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao processar consulta')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Agente Regulatório
          </h1>
          <p className="text-lg text-gray-600">
            Sistema RAG especializado em Pix e Open Finance - Banco Central do Brasil
          </p>
        </div>

        {/* Chat Container */}
        <div className="bg-white rounded-lg shadow-xl p-6 mb-6">
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Domain Selector */}
            <div>
              <label htmlFor="domain" className="block text-sm font-medium text-gray-700 mb-2">
                Domínio:
              </label>
              <select
                id="domain"
                value={domain}
                onChange={(e) => setDomain(e.target.value as 'pix' | 'open_finance')}
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              >
                <option value="pix">Pix</option>
                <option value="open_finance">Open Finance</option>
              </select>
            </div>

            {/* Question Input */}
            <div>
              <label htmlFor="question" className="block text-sm font-medium text-gray-700 mb-2">
                Sua Pergunta:
              </label>
              <textarea
                id="question"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="Ex: Quais são as obrigações de um PSP no Pix?"
                rows={4}
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                required
              />
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading || !question.trim()}
              className="w-full bg-indigo-600 text-white py-3 px-6 rounded-md font-medium hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? 'Processando...' : 'Enviar Pergunta'}
            </button>
          </form>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <p className="text-red-800">{error}</p>
          </div>
        )}

        {/* Response */}
        {response && (
          <div className="bg-white rounded-lg shadow-xl p-6 space-y-6">
            <div>
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">Resposta:</h2>
              <div className="prose max-w-none">
                <p className="text-gray-700 whitespace-pre-wrap">{response.answer}</p>
              </div>
            </div>

            {/* Citations */}
            {response.citations.length > 0 && (
              <div className="border-t pt-4">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Citações Normativas:</h3>
                <ul className="list-disc list-inside space-y-1">
                  {response.citations.map((citation, idx) => (
                    <li key={idx} className="text-gray-600">{citation}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Sources */}
            {response.sources.length > 0 && (
              <div className="border-t pt-4">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  Documentos Utilizados ({response.sources.length}):
                </h3>
                <div className="space-y-2">
                  {response.sources.map((source, idx) => (
                    <div key={idx} className="bg-gray-50 rounded p-3 text-sm">
                      <p className="font-medium text-gray-900">
                        {source.norma} {source.numero_norma}/{source.ano}
                        {source.artigo && ` - Art. ${source.artigo}`}
                      </p>
                      <p className="text-gray-600 text-xs mt-1">
                        Fonte: {source.fonte} | Tema: {source.tema}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Context Warning */}
            {!response.has_sufficient_context && (
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                <p className="text-yellow-800 text-sm">
                  ⚠️ A resposta pode não ter base normativa suficiente nos documentos indexados.
                </p>
              </div>
            )}
          </div>
        )}

        {/* Footer */}
        <div className="text-center mt-8 text-sm text-gray-500">
          <p>
            ⚠️ Este sistema é uma ferramenta de auxílio à consulta normativa.
            <br />
            Não substitui consultoria jurídica especializada.
          </p>
        </div>
      </div>
    </div>
  )
}

