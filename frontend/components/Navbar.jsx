"use client";
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { BarChart3, TrendingUp, Building2, Landmark } from 'lucide-react';

export default function Navbar() {
  const pathname = usePathname();

  const links = [
    { href: '/', label: 'Dashboard', icon: <BarChart3 size={16} /> },
    { href: '/fred', label: 'FRED Macro', icon: <TrendingUp size={16} /> },
    { href: '/sec', label: 'SEC Fundamentals', icon: <Building2 size={16} /> },
    { href: '/treasury', label: 'Treasury', icon: <Landmark size={16} /> },
  ];

  return (
    <nav className="navbar">
      <Link href="/" className="navbar-brand">FinDash</Link>
      <div className="nav-links">
        {links.map(link => (
          <Link
            key={link.href}
            href={link.href}
            className={`nav-link ${pathname === link.href ? 'active' : ''}`}
            style={{ display: 'flex', alignItems: 'center', gap: '6px' }}
          >
            {link.icon}
            {link.label}
          </Link>
        ))}
      </div>
    </nav>
  );
}
