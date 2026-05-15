"use client";
import { useEffect, useRef } from 'react';
import { createChart, ColorType } from 'lightweight-charts';

export const LightweightChart = ({
  data,
  chartType = 'area',
  colors: {
    backgroundColor = 'transparent',
    lineColor = '#3b82f6',
    textColor = '#94a3b8',
    areaTopColor = 'rgba(59, 130, 246, 0.35)',
    areaBottomColor = 'rgba(59, 130, 246, 0.0)',
    gridColor = 'rgba(148, 163, 184, 0.08)',
  } = {},
  height = 400,
}) => {
  const chartContainerRef = useRef();
  const chartRef = useRef(null);

  useEffect(() => {
    if (!chartContainerRef.current) return;

    const handleResize = () => {
      if (chartRef.current) {
        chartRef.current.applyOptions({ width: chartContainerRef.current.clientWidth });
      }
    };

    const chart = createChart(chartContainerRef.current, {
      layout: {
        background: { type: ColorType.Solid, color: backgroundColor },
        textColor,
        fontFamily: "'Inter', sans-serif",
      },
      grid: {
        vertLines: { color: gridColor },
        horzLines: { color: gridColor },
      },
      width: chartContainerRef.current.clientWidth,
      height,
      rightPriceScale: {
        borderVisible: false,
        scaleMargins: { top: 0.1, bottom: 0.1 },
      },
      timeScale: {
        borderVisible: false,
        timeVisible: false,
      },
      crosshair: {
        vertLine: { color: 'rgba(59, 130, 246, 0.3)', width: 1, style: 2 },
        horzLine: { color: 'rgba(59, 130, 246, 0.3)', width: 1, style: 2 },
      },
      handleScroll: { vertTouchDrag: false },
    });

    chartRef.current = chart;

    let series;
    if (chartType === 'line') {
      series = chart.addLineSeries({
        color: lineColor,
        lineWidth: 2,
        crosshairMarkerRadius: 4,
      });
    } else {
      series = chart.addAreaSeries({
        lineColor,
        topColor: areaTopColor,
        bottomColor: areaBottomColor,
        lineWidth: 2,
        crosshairMarkerRadius: 4,
      });
    }

    if (data && data.length > 0) {
      series.setData(data);
      chart.timeScale().fitContent();
    }

    window.addEventListener('resize', handleResize);
    return () => {
      window.removeEventListener('resize', handleResize);
      chart.remove();
    };
  }, [data, backgroundColor, lineColor, textColor, areaTopColor, areaBottomColor, gridColor, height, chartType]);

  return (
    <div
      ref={chartContainerRef}
      style={{ position: 'relative', width: '100%', height: `${height}px` }}
    />
  );
};
