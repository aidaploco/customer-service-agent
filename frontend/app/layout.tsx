import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Brightloop — Agent Dev Console',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark" suppressHydrationWarning>
      <body className="bg-white dark:bg-slate-950 text-slate-900 dark:text-slate-100 antialiased">{children}</body>
    </html>
  )
}
