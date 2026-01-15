// src/components/shared/PerformanceChart.jsx

import React, { useState, useEffect, useRef } from 'react';

const PerformanceChart = ({
  // Data configuration
  data = [],
  metrics = ['value'],
  labels = [],
  
  // Chart configuration
  type = 'line', // 'line', 'bar', 'area', 'pie', 'doughnut', 'gauge', 'sparkline'
  variant = 'default', // 'default', 'minimal', 'detailed', 'compact'
  size = 'medium', // 'small', 'medium', 'large'
  
  // Display options
  title = 'Performance Chart',
  subtitle = '',
  showLegend = true,
  showGrid = true,
  showAxes = true,
  showTooltip = true,
  showLabels = true,
  animated = true,
  
  // Styling
  colors = ['#17a2b8', '#28a745', '#ffc107', '#dc3545', '#6f42c1', '#fd7e14'],
  gradients = true,
  theme = 'dark',
  
  // Real-time options
  realTime = false,
  updateInterval = 1000,
  maxDataPoints = 50,
  
  // Interactive options
  interactive = true,
  zoomable = false,
  exportable = false,
  
  // Value formatting
  valueFormatter = (value) => value,
  labelFormatter = (label) => label,
  
  // Event handlers
  onDataPointClick = null,
  onLegendClick = null,
  onExport = null,
  
  // Custom styling
  className = '',
  style = {}
}) => {
  const chartRef = useRef(null);
  const canvasRef = useRef(null);
  const [chartData, setChartData] = useState(data);
  const [hoveredPoint, setHoveredPoint] = useState(null);
  const [selectedMetrics, setSelectedMetrics] = useState(metrics);
  const [isLoading, setIsLoading] = useState(false);

  // Chart dimensions and calculations
  const [dimensions, setDimensions] = useState({ width: 400, height: 300 });
  const padding = variant === 'minimal' ? 20 : variant === 'compact' ? 30 : 40;

  // Update dimensions on resize
  useEffect(() => {
    const updateDimensions = () => {
      if (chartRef.current) {
        const rect = chartRef.current.getBoundingClientRect();
        setDimensions({
          width: rect.width,
          height: rect.height
        });
      }
    };

    updateDimensions();
    window.addEventListener('resize', updateDimensions);
    return () => window.removeEventListener('resize', updateDimensions);
  }, []);

  // Real-time data updates
  useEffect(() => {
    if (!realTime) return;

    const interval = setInterval(() => {
      setChartData(prevData => {
        const newData = [...prevData];
        // Simulate new data point
        const newPoint = {
          timestamp: Date.now(),
          ...metrics.reduce((acc, metric) => ({
            ...acc,
            [metric]: Math.random() * 100
          }), {})
        };
        
        newData.push(newPoint);
        
        // Keep only maxDataPoints
        if (newData.length > maxDataPoints) {
          newData.shift();
        }
        
        return newData;
      });
    }, updateInterval);

    return () => clearInterval(interval);
  }, [realTime, updateInterval, maxDataPoints, metrics]);

  // Get chart bounds
  const getChartBounds = () => ({
    x: padding,
    y: padding,
    width: dimensions.width - padding * 2,
    height: dimensions.height - padding * 2
  });

  // Calculate data ranges
  const getDataRanges = () => {
    if (!chartData.length) return { minX: 0, maxX: 1, minY: 0, maxY: 1 };

    const values = chartData.flatMap(point => 
      selectedMetrics.map(metric => point[metric] || 0)
    );

    return {
      minX: 0,
      maxX: chartData.length - 1,
      minY: Math.min(...values) * 0.9,
      maxY: Math.max(...values) * 1.1
    };
  };

  // Convert data coordinates to canvas coordinates
  const dataToCanvas = (dataX, dataY) => {
    const bounds = getChartBounds();
    const ranges = getDataRanges();
    
    const x = bounds.x + (dataX - ranges.minX) / (ranges.maxX - ranges.minX) * bounds.width;
    const y = bounds.y + bounds.height - (dataY - ranges.minY) / (ranges.maxY - ranges.minY) * bounds.height;
    
    return { x, y };
  };

  // Render line chart
  const renderLineChart = (ctx) => {
    const bounds = getChartBounds();
    
    selectedMetrics.forEach((metric, metricIndex) => {
      const color = colors[metricIndex % colors.length];
      
      ctx.strokeStyle = color;
      ctx.lineWidth = 2;
      ctx.beginPath();
      
      chartData.forEach((point, index) => {
        const { x, y } = dataToCanvas(index, point[metric] || 0);
        
        if (index === 0) {
          ctx.moveTo(x, y);
        } else {
          ctx.lineTo(x, y);
        }
      });
      
      ctx.stroke();
      
      // Draw points
      if (showLabels || variant === 'detailed') {
        ctx.fillStyle = color;
        chartData.forEach((point, index) => {
          const { x, y } = dataToCanvas(index, point[metric] || 0);
          ctx.beginPath();
          ctx.arc(x, y, 3, 0, 2 * Math.PI);
          ctx.fill();
        });
      }
      
      // Fill area if area chart
      if (type === 'area') {
        const gradient = ctx.createLinearGradient(0, bounds.y, 0, bounds.y + bounds.height);
        gradient.addColorStop(0, color + '40');
        gradient.addColorStop(1, color + '00');
        
        ctx.fillStyle = gradient;
        ctx.beginPath();
        
        chartData.forEach((point, index) => {
          const { x, y } = dataToCanvas(index, point[metric] || 0);
          
          if (index === 0) {
            ctx.moveTo(x, bounds.y + bounds.height);
            ctx.lineTo(x, y);
          } else {
            ctx.lineTo(x, y);
          }
        });
        
        ctx.lineTo(dataToCanvas(chartData.length - 1, 0).x, bounds.y + bounds.height);
        ctx.closePath();
        ctx.fill();
      }
    });
  };

  // Render bar chart
  const renderBarChart = (ctx) => {
    const bounds = getChartBounds();
    const barWidth = bounds.width / chartData.length * 0.8;
    const barSpacing = bounds.width / chartData.length * 0.2;
    
    chartData.forEach((point, index) => {
      selectedMetrics.forEach((metric, metricIndex) => {
        const color = colors[metricIndex % colors.length];
        const value = point[metric] || 0;
        const { x, y } = dataToCanvas(index, value);
        const barHeight = bounds.y + bounds.height - y;
        
        ctx.fillStyle = color;
        ctx.fillRect(
          x - barWidth / 2,
          y,
          barWidth / selectedMetrics.length,
          barHeight
        );
      });
    });
  };

  // Render gauge chart
  const renderGaugeChart = (ctx) => {
    const centerX = dimensions.width / 2;
    const centerY = dimensions.height / 2;
    const radius = Math.min(dimensions.width, dimensions.height) / 3;
    
    const value = chartData.length ? chartData[chartData.length - 1][selectedMetrics[0]] || 0 : 0;
    const maxValue = getDataRanges().maxY;
    const angle = (value / maxValue) * Math.PI * 1.5 - Math.PI * 0.75;
    
    // Background arc
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.2)';
    ctx.lineWidth = 20;
    ctx.beginPath();
    ctx.arc(centerX, centerY, radius, -Math.PI * 0.75, Math.PI * 0.75);
    ctx.stroke();
    
    // Value arc
    ctx.strokeStyle = colors[0];
    ctx.lineWidth = 20;
    ctx.beginPath();
    ctx.arc(centerX, centerY, radius, -Math.PI * 0.75, angle);
    ctx.stroke();
    
    // Center value
    ctx.fillStyle = 'white';
    ctx.font = 'bold 24px Arial';
    ctx.textAlign = 'center';
    ctx.fillText(valueFormatter(value), centerX, centerY + 8);
  };

  // Render sparkline
  const renderSparkline = (ctx) => {
    if (!chartData.length) return;
    
    const metric = selectedMetrics[0];
    const color = colors[0];
    
    ctx.strokeStyle = color;
    ctx.lineWidth = 2;
    ctx.beginPath();
    
    chartData.forEach((point, index) => {
      const { x, y } = dataToCanvas(index, point[metric] || 0);
      
      if (index === 0) {
        ctx.moveTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }
    });
    
    ctx.stroke();
  };

  // Render grid
  const renderGrid = (ctx) => {
    if (!showGrid) return;
    
    const bounds = getChartBounds();
    const gridLines = 5;
    
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)';
    ctx.lineWidth = 1;
    
    // Horizontal grid lines
    for (let i = 0; i <= gridLines; i++) {
      const y = bounds.y + (bounds.height / gridLines) * i;
      ctx.beginPath();
      ctx.moveTo(bounds.x, y);
      ctx.lineTo(bounds.x + bounds.width, y);
      ctx.stroke();
    }
    
    // Vertical grid lines
    for (let i = 0; i <= gridLines; i++) {
      const x = bounds.x + (bounds.width / gridLines) * i;
      ctx.beginPath();
      ctx.moveTo(x, bounds.y);
      ctx.lineTo(x, bounds.y + bounds.height);
      ctx.stroke();
    }
  };

  // Render axes
  const renderAxes = (ctx) => {
    if (!showAxes) return;
    
    const bounds = getChartBounds();
    const ranges = getDataRanges();
    
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.3)';
    ctx.fillStyle = 'rgba(255, 255, 255, 0.7)';
    ctx.font = '10px Arial';
    ctx.lineWidth = 1;
    
    // X-axis
    ctx.beginPath();
    ctx.moveTo(bounds.x, bounds.y + bounds.height);
    ctx.lineTo(bounds.x + bounds.width, bounds.y + bounds.height);
    ctx.stroke();
    
    // Y-axis
    ctx.beginPath();
    ctx.moveTo(bounds.x, bounds.y);
    ctx.lineTo(bounds.x, bounds.y + bounds.height);
    ctx.stroke();
    
    // Y-axis labels
    const ySteps = 5;
    for (let i = 0; i <= ySteps; i++) {
      const value = ranges.minY + (ranges.maxY - ranges.minY) / ySteps * i;
      const y = bounds.y + bounds.height - (bounds.height / ySteps) * i;
      
      ctx.textAlign = 'right';
      ctx.fillText(valueFormatter(value), bounds.x - 5, y + 3);
    }
    
    // X-axis labels
    const xSteps = Math.min(chartData.length, 10);
    for (let i = 0; i < xSteps; i++) {
      const index = Math.floor(chartData.length / xSteps * i);
      const point = chartData[index];
      if (!point) continue;
      
      const x = bounds.x + (bounds.width / xSteps) * i;
      const label = point.label || point.timestamp 
        ? new Date(point.timestamp).toLocaleTimeString() 
        : index.toString();
      
      ctx.textAlign = 'center';
      ctx.fillText(labelFormatter(label), x, bounds.y + bounds.height + 15);
    }
  };

  // Main render function
  const renderChart = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, dimensions.width, dimensions.height);
    
    // Set canvas size
    canvas.width = dimensions.width;
    canvas.height = dimensions.height;
    
    if (type === 'sparkline') {
      renderSparkline(ctx);
      return;
    }
    
    renderGrid(ctx);
    renderAxes(ctx);
    
    switch (type) {
      case 'line':
      case 'area':
        renderLineChart(ctx);
        break;
      case 'bar':
        renderBarChart(ctx);
        break;
      case 'gauge':
        renderGaugeChart(ctx);
        break;
      default:
        renderLineChart(ctx);
    }
  };

  // Render chart when data or dimensions change
  useEffect(() => {
    renderChart();
  }, [chartData, dimensions, selectedMetrics, type, showGrid, showAxes]);

  // Handle mouse events
  const handleCanvasClick = (event) => {
    if (!onDataPointClick) return;
    
    const rect = canvasRef.current.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;
    
    // Find closest data point
    let closestPoint = null;
    let closestDistance = Infinity;
    
    chartData.forEach((point, index) => {
      selectedMetrics.forEach(metric => {
        const { x: pointX, y: pointY } = dataToCanvas(index, point[metric] || 0);
        const distance = Math.sqrt((x - pointX) ** 2 + (y - pointY) ** 2);
        
        if (distance < closestDistance && distance < 20) {
          closestDistance = distance;
          closestPoint = { point, index, metric };
        }
      });
    });
    
    if (closestPoint) {
      onDataPointClick(closestPoint);
    }
  };

  // Toggle metric visibility
  const toggleMetric = (metric) => {
    if (onLegendClick) {
      onLegendClick(metric);
    } else {
      setSelectedMetrics(prev => 
        prev.includes(metric) 
          ? prev.filter(m => m !== metric)
          : [...prev, metric]
      );
    }
  };

  // Export chart
  const handleExport = () => {
    if (!onExport) return;
    
    const canvas = canvasRef.current;
    const dataURL = canvas.toDataURL('image/png');
    onExport(dataURL);
  };

  return (
    <div 
      className={`
        performance-chart
        type-${type}
        variant-${variant}
        size-${size}
        theme-${theme}
        ${animated ? 'animated' : ''}
        ${interactive ? 'interactive' : ''}
        ${className}
      `}
      style={style}
      ref={chartRef}
    >
      {/* Header */}
      {variant !== 'minimal' && variant !== 'sparkline' && (
        <div className="chart-header">
          <div className="chart-title-section">
            <h3 className="chart-title">{title}</h3>
            {subtitle && <p className="chart-subtitle">{subtitle}</p>}
          </div>
          
          <div className="chart-controls">
            {realTime && (
              <div className="chart-status">
                <div className="status-indicator live" />
                <span>Live</span>
              </div>
            )}
            
            {exportable && (
              <button 
                className="chart-export"
                onClick={handleExport}
                title="Export chart"
              >
                <i className="fas fa-download" />
              </button>
            )}
          </div>
        </div>
      )}

      {/* Chart Canvas */}
      <div className="chart-container">
        <canvas
          ref={canvasRef}
          className="chart-canvas"
          onClick={interactive ? handleCanvasClick : undefined}
        />
        
        {isLoading && (
          <div className="chart-loading">
            <i className="fas fa-spinner fa-spin" />
            <span>Loading chart data...</span>
          </div>
        )}
      </div>

      {/* Legend */}
      {showLegend && variant !== 'minimal' && variant !== 'sparkline' && metrics.length > 1 && (
        <div className="chart-legend">
          {metrics.map((metric, index) => (
            <div
              key={metric}
              className={`
                legend-item
                ${selectedMetrics.includes(metric) ? 'active' : 'inactive'}
              `}
              onClick={() => toggleMetric(metric)}
            >
              <div 
                className="legend-color"
                style={{ backgroundColor: colors[index % colors.length] }}
              />
              <span className="legend-label">{metric}</span>
            </div>
          ))}
        </div>
      )}

      {/* Tooltip */}
      {showTooltip && hoveredPoint && (
        <div 
          className="chart-tooltip"
          style={{
            left: hoveredPoint.x,
            top: hoveredPoint.y
          }}
        >
          <div className="tooltip-content">
            <strong>{hoveredPoint.label}</strong>
            <br />
            {hoveredPoint.value}
          </div>
        </div>
      )}
    </div>
  );
};

export default PerformanceChart;
