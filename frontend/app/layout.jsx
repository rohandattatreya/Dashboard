import './globals.css';
import Navbar from '../components/Navbar';

export const metadata = {
  title: 'FinDash — Macro & Fundamental Dashboard',
  description: 'Comprehensive macroeconomic and fundamental financial data from FRED, SEC EDGAR, and Treasury Direct.',
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet" />
      </head>
      <body>
        <Navbar />
        <main className="container">
          {children}
        </main>
      </body>
    </html>
  );
}
