"use client";

import { Scatter } from 'react-chartjs-2';
import { Chart as ChartJS, LinearScale, PointElement, Tooltip, Legend } from 'chart.js';

ChartJS.register(LinearScale, PointElement, Tooltip, Legend);

interface GapScatterPlotProps {
  gaps: any[];
}

export default function GapScatterPlot({ gaps }: GapScatterPlotProps) {
  const data = {
    datasets: [
      {
        label: 'Gap Actions',
        data: gaps?.map(g => ({
          x: g.effort_hours || Math.random() * 40,
          y: g.score_gain || Math.random() * 30,
          raw: g // Pass raw data for tooltips
        })) || [],
        backgroundColor: '#c488fb', // Brand Purple
        pointBackgroundColor: '#c488fb',
        pointBorderColor: '#fff',
        pointHoverBackgroundColor: '#fff',
        pointHoverBorderColor: '#c488fb',
        pointRadius: 6,
        pointHoverRadius: 8,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      x: {
        title: { display: true, text: 'Effort (Hours)', color: '#94a3b8', font: { family: "'JetBrains Mono', monospace" } },
        min: 0,
        max: 40,
        grid: { color: 'rgba(255, 255, 255, 0.05)' },
        ticks: { color: '#94a3b8' }
      },
      y: {
        title: { display: true, text: 'Score Gained', color: '#94a3b8', font: { family: "'JetBrains Mono', monospace" } },
        min: 0,
        max: 30,
        grid: { color: 'rgba(255, 255, 255, 0.05)' },
        ticks: { color: '#94a3b8' }
      },
    },
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: 'rgba(13, 22, 47, 0.95)',
        titleFont: { family: "'JetBrains Mono', monospace" },
        bodyFont: { family: "'Inter', sans-serif" },
        borderColor: 'rgba(255, 255, 255, 0.1)',
        borderWidth: 1,
        callbacks: {
          label: (context: any) => {
            const point = context.raw.raw;
            return point?.action_type || `Action: ${context.raw.y}pts in ${context.raw.x}h`;
          }
        }
      },
    },
  };

  return (
    <div className="relative w-full h-full min-h-[300px]">
      {/* Quick Wins Quadrant Overlay (Top-Left: Low Effort < 20h, High Score > 15pts) */}
      <div className="absolute top-[5%] left-[5%] w-[45%] h-[45%] bg-[--color-brand-success] opacity-10 rounded-lg pointer-events-none border border-[--color-brand-success] shadow-[0_0_20px_rgba(33,254,169,0.3)]">
        <span className="absolute top-2 left-2 text-[10px] text-[--color-brand-success] font-mono tracking-widest opacity-80 uppercase">Quick Wins</span>
      </div>
      
      <Scatter data={data} options={options} />
    </div>
  );
}
