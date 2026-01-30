import React, { useEffect, useRef } from 'react';
import { Chart as ChartJS, ChartConfiguration, registerables } from 'chart.js';

ChartJS.register(...registerables);

interface MetricChartProps {
  type: 'line' | 'bar' | 'doughnut' | 'area';
  data: any;
  options?: any;
  height?: number;
  className?: string;
}

export const MetricChart: React.FC<MetricChartProps> = ({
  type,
  data,
  options,
  height = 300,
  className = '',
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const chartRef = useRef<ChartJS | null>(null);

  useEffect(() => {
    if (!canvasRef.current) return;

    const ctx = canvasRef.current.getContext('2d');
    if (!ctx) return;

    // Destroy previous chart
    if (chartRef.current) {
      chartRef.current.destroy();
    }

    // Default options for dark theme
    const defaultOptions = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          labels: {
            color: '#E4E7EB',
            font: { family: 'Inter, sans-serif', size: 12 },
          },
        },
        tooltip: {
          backgroundColor: '#1E2749',
          titleColor: '#E4E7EB',
          bodyColor: '#9CA3AF',
          borderColor: '#3B82F6',
          borderWidth: 1,
        },
      },
      scales: type !== 'doughnut' ? {
        x: {
          ticks: { color: '#9CA3AF' },
          grid: { color: '#2D3748' },
        },
        y: {
          ticks: { color: '#9CA3AF' },
          grid: { color: '#2D3748' },
        },
      } : undefined,
    };

    const config: ChartConfiguration = {
      type: type === 'area' ? 'line' : type,
      data: {
        ...data,
        datasets: data.datasets?.map((dataset: any) => ({
          ...dataset,
          backgroundColor: type === 'area' 
            ? `${dataset.borderColor}33` 
            : dataset.backgroundColor,
          fill: type === 'area',
        })),
      },
      options: { ...defaultOptions, ...options },
    };

    chartRef.current = new ChartJS(ctx, config);

    return () => {
      if (chartRef.current) {
        chartRef.current.destroy();
      }
    };
  }, [type, data, options]);

  return (
    <div className={className} style={{ height }}>
      <canvas ref={canvasRef} />
    </div>
  );
};
