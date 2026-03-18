import './globals.css'
import { Inter, JetBrains_Mono } from 'next/font/google'
import Navbar from '@/components/layout/Navbar'
import Sidebar from '@/components/layout/Sidebar'

const inter = Inter({ subsets: ['latin'], variable: '--font-inter' })
const jetbrains = JetBrains_Mono({ subsets: ['latin'], variable: '--font-mono' })

export const metadata = {
  title: 'Supply Chain Forecasting & Optimization',
  description: 'AI powered supply chain analysis',
}

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className={`${inter.variable} ${jetbrains.variable} font-sans bg-[#0A0F1E] text-white`}>
        <div className="flex h-screen w-full">
          <Sidebar />
          <div className="flex flex-col flex-1 h-full">
            <Navbar />
            <main className="flex-1 overflow-auto">
              {children}
            </main>
          </div>
        </div>
      </body>
    </html>
  )
}
