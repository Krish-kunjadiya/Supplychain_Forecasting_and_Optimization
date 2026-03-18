import Link from 'next/link';

export default function Navbar() {
  return (
    <nav className="flex items-center justify-between p-4 bg-[#0A0F1E] border-b border-[rgba(255,255,255,0.08)]">
      <div className="text-xl font-bold text-white tracking-tight">
        SCF Optimization <span className="text-[#1F78FF]">System</span>
      </div>
    </nav>
  )
}
