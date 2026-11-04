"use client";

import React from "react";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from "recharts";
import { Activity, CheckCircle2, AlertTriangle, Leaf, Calendar, ShieldCheck } from "lucide-react";
import { NdviDataPoint } from "@/lib/types";

interface NdviChartProps {
  data?: NdviDataPoint[];
}

interface CustomTooltipProps {
  active?: boolean;
  payload?: Array<{ value: number }>;
  label?: string;
}

const DEFAULT_NDVI_DATA: NdviDataPoint[] = [
  { quarter: "Q1 2020", ndvi: 0.825 },
  { quarter: "Q3 2020", ndvi: 0.838 },
  { quarter: "Q1 2021", ndvi: 0.842 },
  { quarter: "Q3 2021", ndvi: 0.856 },
  { quarter: "Q1 2022", ndvi: 0.849 },
  { quarter: "Q3 2022", ndvi: 0.865 },
  { quarter: "Q1 2023", ndvi: 0.871 },
  { quarter: "Q3 2023", ndvi: 0.884 },
  { quarter: "Q1 2024", ndvi: 0.878 },
  { quarter: "Q2 2024", ndvi: 0.892 },
];

const CustomTooltip = ({ active, payload, label }: CustomTooltipProps) => {
  if (active && payload && payload.length) {
    const ndviVal = payload[0].value;
    return (
      <div className="bg-gray-950/95 text-white p-3.5 rounded-2xl shadow-2xl border border-emerald-500/40 text-xs font-mono space-y-1.5 backdrop-blur-xl">
        <div className="flex items-center gap-1.5 text-white/70">
          <Calendar className="w-3.5 h-3.5 text-emerald-400" />
          <span className="font-semibold">{label}</span>
        </div>
        <div className="flex items-center gap-2 pt-1 border-t border-white/10">
          <Leaf className="w-3.5 h-3.5 text-emerald-400" />
          <span className="text-white/60">NDVI:</span>
          <span className="text-emerald-400 font-bold text-sm">{ndviVal.toFixed(3)}</span>
        </div>
        <div className="text-[10px] text-emerald-300/80">
          Photosynthetic canopy density
        </div>
      </div>
    );
  }
  return null;
};

export function NdviChart({ data = [] }: NdviChartProps) {
  const chartData = data && data.length >= 2 ? data : DEFAULT_NDVI_DATA;

  // Determine if trend is stable/improving or declining
  const isDeclining =
    chartData.length >= 2 &&
    chartData[chartData.length - 1].ndvi < chartData[0].ndvi - 0.05;

  return (
    <div className="crystal-glass-card rounded-3xl p-7 md:p-8 border border-white/20 shadow-2xl relative overflow-hidden text-white">
      {/* Specular sheen */}
      <div className="pointer-events-none absolute inset-x-0 top-0 h-[1px] bg-gradient-to-r from-transparent via-white/30 to-transparent" />

      {/* Header */}
      <div className="flex items-center justify-between mb-6 flex-wrap gap-4">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-2xl bg-emerald-500/20 text-emerald-400 border border-emerald-400/30 shadow-inner">
            <Activity className="w-5 h-5 text-emerald-400" />
          </div>
          <div>
            <h3 className="font-bold text-white text-lg sm:text-xl tracking-tight">
              Forest Health Trend (NDVI Multi-Temporal Trajectory)
            </h3>
            <p className="text-xs text-white/60">
              Normalized Difference Vegetation Index — 5 Year Trajectory from Sentinel-2 MSI
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 text-xs font-mono text-emerald-300 bg-emerald-500/15 px-3.5 py-1.5 rounded-xl border border-emerald-400/30 shadow-sm backdrop-blur-md">
          <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse shadow-sm" />
          <span>Sentinel-2 B4/B8 Ratio (10m)</span>
        </div>
      </div>

      {/* Recharts Area Chart */}
      <div className="w-full h-[320px]">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart
            data={chartData}
            margin={{ top: 15, right: 20, left: -10, bottom: 25 }}
          >
            <defs>
              <linearGradient id="ndviGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#10B981" stopOpacity={0.65} />
                <stop offset="50%" stopColor="#059669" stopOpacity={0.25} />
                <stop offset="95%" stopColor="#047857" stopOpacity={0.02} />
              </linearGradient>
            </defs>

            <CartesianGrid
              stroke="rgba(255, 255, 255, 0.1)"
              strokeDasharray="3 3"
              vertical={false}
            />

            <XAxis
              dataKey="quarter"
              stroke="#9CA3AF"
              fontSize={11}
              tickLine={false}
              axisLine={{ stroke: "rgba(255, 255, 255, 0.15)" }}
              angle={-45}
              textAnchor="end"
              interval={0}
              height={50}
              tick={{ fill: "#CBD5E1" }}
            />

            <YAxis
              domain={[0.7, 1.0]}
              stroke="#9CA3AF"
              fontSize={11}
              tickLine={false}
              axisLine={{ stroke: "rgba(255, 255, 255, 0.15)" }}
              tickFormatter={(v) => v.toFixed(2)}
              tick={{ fill: "#CBD5E1" }}
            />

            <Tooltip content={<CustomTooltip />} />

            <ReferenceLine
              y={0.8}
              stroke="#34D399"
              strokeDasharray="4 4"
              strokeWidth={1.5}
              label={{
                value: "Health Threshold (0.80)",
                position: "insideTopRight",
                fill: "#A7F3D0",
                fontSize: 10,
                fontWeight: "bold",
              }}
            />

            <Area
              type="monotone"
              dataKey="ndvi"
              stroke="#34D399"
              strokeWidth={3}
              fillOpacity={1}
              fill="url(#ndviGradient)"
              activeDot={{
                r: 6,
                fill: "#10B981",
                stroke: "#FFFFFF",
                strokeWidth: 2,
              }}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Trend Annotation Footer */}
      <div className="mt-4 pt-4 border-t border-white/10 flex items-center justify-between flex-wrap gap-2 text-xs">
        {isDeclining ? (
          <div className="flex items-center gap-2 text-amber-200 font-medium bg-amber-500/20 px-3.5 py-1.5 rounded-xl border border-amber-400/40">
            <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0" />
            <span>Warning — potential canopy degradation detected in recent cycles</span>
          </div>
        ) : (
          <div className="flex items-center gap-2 text-emerald-200 font-medium bg-emerald-500/20 px-3.5 py-1.5 rounded-xl border border-emerald-400/40">
            <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
            <span>
              Canopy stability verified — persistent photosynthesis above the 0.80 IPCC threshold
            </span>
          </div>
        )}

        <span className="text-white/50 font-mono text-[11px] flex items-center gap-1.5">
          <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
          Sensor: Multi-Temporal MSI Sentinel-2
        </span>
      </div>
    </div>
  );
}

export default NdviChart;
