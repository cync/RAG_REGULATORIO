import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Agente Regulatório - RAG Pix e Open Finance',
  description: 'Sistema RAG especializado em regulação do Banco Central do Brasil',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="pt-BR">
      <body>{children}</body>
    </html>
  )
}

