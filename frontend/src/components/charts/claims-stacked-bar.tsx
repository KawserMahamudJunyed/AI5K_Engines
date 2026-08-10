"use client";

import { Bar } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Tooltip, Legend } from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip, Legend);

interface ClaimsStackedBarProps {
  claims: any[];
}

export default function ClaimsStackedBar({ claims }: ClaimsStackedBarProps) {
  // T1-T4 (Verified) vs T5-T8 (Self-Declared)
  const t1t4Count = claims?.filter(c => ['T1', 'T2', 'T3', 'T4'].includes(c.tier)).length || 0;
  const t5t8Count = claims?.filter(c => ['T5', 'T6', 'T7', 'T8'].includes(c.tier)).length || 0;

  const data = {
    labels: ['Claims Provenance'],
    datasets: [
      {
        label: 'Verified Proof (T1-T4)',
        data: [t1t4Count],
        backgroundColor: '#21fea9', // Electric Green
        barThickness: 40,
        borderRadius: { topLeft: 4, bottomLeft: 4 },
      },
      {
        label: 'Self-Declared (T5-T8)',
        data: [t5t8Count],
        backgroundColor: '#50dffb', // Vibrant Cyan
        barThickness: 40,
        borderRadius: { topRight: 4, bottomRight: 4 },
      },
    ],
  };

  const options = {
    indexAxis: 'y' as const,
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      x: {
        stacked: true,
        display: false, // Hide the bottom axis for a clean look
      },
      y: {
        stacked: true,
        display: false, // Hide the side axis
      },
    },
    plugins: {
      legend: {
        position: 'bottom' as const,
        labels: {
          color: '#94a3b8',
          font: { family: "'JetBrains Mono', monospace", size: 12 },
          usePointStyle: true,
          pointStyle: 'circle',
        }
      },
      tooltip: {
        backgroundColor: 'rgba(13, 22, 47, 0.9)',
        titleFont: { family: "'JetBrains Mono', monospace" },
        bodyFont: { family: "'Inter', sans-serif" },
        borderColor: 'rgba(255, 255, 255, 0.1)',
        borderWidth: 1,
      },
    },
  };

  return (
    <div className="w-full h-full min-h-[150px] flex flex-col justify-center">
      <Bar data={data} options={options} />
    </div>
  );
}
