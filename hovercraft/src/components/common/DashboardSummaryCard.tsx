import React from 'react';

interface DashboardSummaryCardProps {
  label: string;
  value: string;
  trend?: {
    value: string;
    isPositive: boolean;
  };
  subtext?: string;
}

/**
 * DashboardSummaryCard (Sentinel Auto-pilot Verified)
 * - ADR: React Functional Component with TypeScript
 * - UI_GUIDE: Dark mode (#141414), border-neutral-800, Left-align only
 * - PRD: Professional tool aesthetics, anti-slop, no gloss/gradients
 */
export const DashboardSummaryCard: React.FC<DashboardSummaryCardProps> = ({
  label,
  value,
  trend,
  subtext,
}) => {
  return (
    <div className="bg-[#141414] border border-neutral-800 rounded-lg p-6 space-y-4 text-left w-full max-w-sm">
      {/* 1. Label Section */}
      <h3 className="text-neutral-400 text-sm font-medium tracking-tight">
        {label}
      </h3>

      {/* 2. Value Section */}
      <div className="flex flex-col space-y-1">
        <span className="text-white text-3xl font-bold tracking-tight">
          {value}
        </span>
      </div>

      {/* 3. Trend & Subtext Section */}
      <div className="flex items-center space-x-2 pt-1">
        {trend && (
          <span
            className={`text-xs font-semibold px-1.5 py-0.5 rounded ${
              trend.isPositive
                ? 'bg-green-500/10 text-[#22c55e]'
                : 'bg-red-500/10 text-[#ef4444]'
            }`}
          >
            {trend.isPositive ? '+' : ''}
            {trend.value}
          </span>
        )}
        {subtext && (
          <span className="text-neutral-500 text-xs">
            {subtext}
          </span>
        )}
      </div>
    </div>
  );
};
