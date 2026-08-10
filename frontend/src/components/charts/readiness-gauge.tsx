"use client";

import { Doughnut } from 'react-chartjs-2';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';
import { Lock } from 'lucide-react';

ChartJS.register(ArcElement, Tooltip, Legend);

interface ReadinessGaugeProps {
  score: number;
  blockedByEvidence: boolean;
}

export default function ReadinessGauge({ score, blockedByEvidence }: ReadinessGaugeProps) {
  // If blocked, visually cap the chart rendering at 30 if it's over 30
  const renderScore = blockedByEvidence ? Math.min(score, 30) : score;
  const color = blockedByEvidence ? '#ff4a6b' : '#21fea9'; // Crimson if blocked, Emerald if verified

  const data = {
    labels: ['Readiness', 'Remaining'],
    datasets: [
      {
        data: [renderScore, 100 - renderScore],
        backgroundColor: [
          color,
          'rgba(255, 255, 255, 0.05)',
        ],
        borderWidth: 0,
        circumference: 180,
        rotation: 270,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    cutout: '80%',
    plugins: {
      legend: { display: false },
      tooltip: { enabled: false },
    },
  };

  return (
    <div className="relative w-full h-full flex flex-col items-center justify-end pb-8">
      <div className="absolute top-0 w-[200px] h-[200px]">
        <Doughnut data={data} options={options} />
      </div>
      
      {/* Center Text */}
      <div className="absolute top-[80px] flex flex-col items-center">
        <span className="text-5xl font-mono font-bold text-white tracking-tighter">
          {score}<span className="text-xl text-gray-500">/100</span>
        </span>
      </div>

      {/* 30% Guardrail Warning */}
      {blockedByEvidence && (
        <div className="mt-[100px] flex items-center gap-2 bg-[--color-brand-danger] bg-opacity-10 border border-[--color-brand-danger] border-opacity-30 rounded-full px-4 py-1.5 shadow-[0_0_10px_rgba(255,74,107,0.4)]">
          <Lock className="w-4 h-4 text-[--color-brand-danger]" />
          <span className="text-xs font-mono text-[--color-brand-danger] uppercase tracking-wider">Capped at 30 until proven</span>
        </div>
      )}
    </div>
  );
}
