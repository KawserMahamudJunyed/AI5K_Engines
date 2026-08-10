"use client";

import { Radar } from 'react-chartjs-2';
import { Chart as ChartJS, RadialLinearScale, PointElement, LineElement, Filler, Tooltip, Legend } from 'chart.js';

ChartJS.register(RadialLinearScale, PointElement, LineElement, Filler, Tooltip, Legend);

interface DimensionRadarProps {
  dimensions: {
    positioning_alignment: number;
    evidence_quality: number;
    keyword_coverage: number;
    portfolio_strength: number;
    profile_completeness: number;
  };
}

export default function DimensionRadar({ dimensions }: DimensionRadarProps) {
  const data = {
    labels: [
      'Positioning (22%)',
      'Evidence Q. (22%)',
      'Keyword Cov. (15%)',
      'Portfolio (15%)',
      'Completeness (10%)',
      'Conversion (8%)',
      'Pricing (8%)'
    ],
    datasets: [
      {
        label: 'Current Profile',
        data: [
          dimensions.positioning_alignment || 0,
          dimensions.evidence_quality || 0,
          dimensions.keyword_coverage || 0,
          dimensions.portfolio_strength || 0,
          dimensions.profile_completeness || 0,
          70, // Mock fallback for un-computed values
          80  // Mock fallback
        ],
        backgroundColor: 'rgba(196, 136, 251, 0.15)', // Transparent Brand Purple
        borderColor: '#5b98f7', // Brand Blue
        pointBackgroundColor: '#5b98f7',
        pointBorderColor: '#fff',
        pointHoverBackgroundColor: '#fff',
        pointHoverBorderColor: '#5b98f7',
        borderWidth: 2,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      r: {
        angleLines: { color: 'rgba(255, 255, 255, 0.1)' },
        grid: { color: '#1e293b' }, // Dark slate grid
        pointLabels: {
          color: '#94a3b8',
          font: { family: "'JetBrains Mono', monospace", size: 11 },
        },
        ticks: {
          display: false,
          min: 0,
          max: 100,
          stepSize: 20
        },
      },
    },
    plugins: {
      legend: { display: false },
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
    <div className="w-full h-full min-h-[300px]">
      <Radar data={data} options={options} />
    </div>
  );
}
