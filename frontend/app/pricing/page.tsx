'use client';

import Link from 'next/link';
import { Check, CreditCard } from 'lucide-react';

const PACKAGES = [
  { name: 'Basic', credits: 5, price: '£9.99', features: ['5 Assessments', 'All domains', 'PDF export', 'Email support'] },
  { name: 'Standard', credits: 15, price: '£24.99', features: ['15 Assessments', 'All domains', 'PDF export', 'Priority support', 'API access'], popular: true },
  { name: 'Premium', credits: 50, price: '£49.99', features: ['50 Assessments', 'All domains', 'PDF export', 'Priority support', 'API access', 'White-label reports'] },
];

export default function PricingPage() {
  return (
    <main className="min-h-screen bg-legal-dark py-16 px-4">
      <div className="max-w-5xl mx-auto text-center">
        <h1 className="text-3xl font-bold text-white mb-4">Pricing</h1>
        <p className="text-gray-400 mb-12">Choose the package that fits your practice</p>
        <div className="grid md:grid-cols-3 gap-6">
          {PACKAGES.map((pkg) => (
            <div key={pkg.name} className={`saif-card relative ${pkg.popular ? 'border-saif-500' : ''}`}>
              {pkg.popular && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-saif-600 text-white text-xs font-bold px-3 py-1 rounded-full">
                  Most Popular
                </div>
              )}
              <h3 className="text-xl font-bold text-white">{pkg.name}</h3>
              <p className="text-3xl font-bold text-saif-400 my-3">{pkg.price}</p>
              <p className="text-gray-400 text-sm mb-4">{pkg.credits} credits</p>
              <ul className="space-y-2 text-left text-sm text-gray-300 mb-6">
                {pkg.features.map((f) => (
                  <li key={f} className="flex items-center gap-2">
                    <Check className="w-4 h-4 text-green-400 shrink-0" /> {f}
                  </li>
                ))}
              </ul>
              <button className="saif-btn-primary w-full flex items-center justify-center gap-2">
                <CreditCard className="w-4 h-4" /> Select
              </button>
            </div>
          ))}
        </div>
        <p className="text-gray-500 text-sm mt-8">
          All purchases are final. Credits do not expire.{' '}
          <Link href="/" className="text-saif-400 hover:underline">Back to home</Link>
        </p>
      </div>
    </main>
  );
}
