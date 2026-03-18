import Link from 'next/link';
import { LayoutDashboard, UploadCloud, Box, PackageSearch, Activity, TrendingUp } from 'lucide-react';

export default function Sidebar() {
  const links = [
    { href: '/', label: 'Overview', icon: LayoutDashboard },
    { href: '/dashboard', label: 'Results Dashboard', icon: Activity },
    { href: '/upload', label: 'Live Pipeline', icon: UploadCloud },
    { href: '/models', label: 'Model Analysis', icon: TrendingUp },
    { href: '/inventory', label: 'Inventory Policy', icon: Box },
    { href: '/sku', label: 'SKU Explorer', icon: PackageSearch },
    { href: '/predict', label: 'Live Inference', icon: Activity }
  ];

  return (
    <aside className="w-64 bg-[#0A0F1E] h-screen border-r border-[rgba(255,255,255,0.08)] p-4 flex flex-col gap-2">
      {links.map(l => {
        const Icon = l.icon;
        return (
          <Link key={l.href} href={l.href} className="flex items-center gap-3 text-gray-300 hover:text-white hover:bg-[rgba(255,255,255,0.04)] p-3 rounded-lg transition-all">
            <Icon size={20} />
            <span className="font-medium text-sm">{l.label}</span>
          </Link>
        )
      })}
    </aside>
  )
}
