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
import { Activity, CheckCircle2, AlertTriangle } from "lucide-react";
import { NdviDataPoint } from "@/lib/types";

interface NdviChartProps {
  data?: NdviDataPoint[];
}

interface CustomTooltipProps {
  active?: boolean;
  payload?: Array<{ value: number }>;
  label?: string;
}

const CustomTooltip = ({ active, payload, label }: CustomTooltipProps) => {
  if (active && payload && payload.length) {
    const ndviVal = payload[0].value;
    return (
      <div className="bg-gray-900 text-white p-3 rounded-xl shadow-xl border border-gray-700 text-xs font-mono space-y-1">
        <p className="font-semibold text-gray-300">Quarter: {label}</p>
        <p className="text-green-400 font-bold text-sm">NDVI: {ndviVal.toFixed(3)}</p>
      </div>
    );
  }
  return null;
};

export function NdviChart({ data = [] }: NdviChartProps) {
  // Determine if trend is stable/improving or declining
  const isDeclining =
    data.length >= 2 && data[data.length - 1].ndvi < data[0].ndvi - 0.05;

  return (
    <div className="bg-white rounded-xl shadow-md border border-gray-100 p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-2.5">
          <div className="p-2.5 rounded-xl bg-green-50 text-green-700 border border-green-200/60">
            <Activity className="w-5 h-5 text-green-600" />
          </div>
          <div>
            <h3 className="font-bold text-gray-900 text-lg tracking-tight">
              Forest Health Trend (NDVI)
            </h3>
            <p className="text-xs text-gray-400">
              Normalized Difference Vegetation Index — 5 Year Trend
            </p>
          </div>
        </div>

        <div className="hidden sm:flex items-center gap-2 text-xs font-mono text-gray-500 bg-gray-50 px-3 py-1.5 rounded-lg border border-gray-200/60">
          <span className="w-2 h-2 rounded-full bg-green-500" />
          <span>Sentinel-2 B4/B8 Ratio</span>
        </div>
      </div>

      {/* Recharts Area Chart */}
      <div className="w-full h-[300px]">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart
            data={data}
            margin={{ top: 10, right: 20, left: -10, bottom: 25 }}
          >
            <defs>
              <linearGradient id="ndviGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#22C55E" stopOpacity={0.4} />
                <stop offset="95%" stopColor="#DCFCE7" stopOpacity={0.05} />
              </linearGradient>
            </defs>

            <CartesianGrid stroke="#F3F4F6" strokeDasharray="3 3" vertical={false} />

            <XAxis
              dataKey="quarter"
              stroke="#9CA3AF"
              fontSize={11}
              tickLine={false}
              axisLine={{ stroke: "#E5E7EB" }}
              angle={-45}
              textAnchor="end"
              interval={1}
            />

            <YAxis
              domain={[0.7, 1.0]}
              stroke="#9CA3AF"
              fontSize={11}
              tickLine={false}
              axisLine={{ stroke: "#E5E7EB" }}
              tickFormatter={(v) => v.toFixed(2)}
            />

            <Tooltip content={<CustomTooltip />} />

            <ReferenceLine
              y={0.8}
              stroke="#9CA3AF"
              strokeDasharray="4 4"
              label={{
                value: "Health Threshold (0.80)",
                position: "insideTopRight",
                fill: "#6B7280",
                fontSize: 10,
              }}
            />

            <Area
              type="monotone"
              dataKey="ndvi"
              stroke="#22C55E"
              strokeWidth={2}
              fillOpacity={1}
              fill="url(#ndviGradient)"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Trend Annotation */}
      <div className="mt-4 pt-4 border-t border-gray-100 flex items-center justify-between flex-wrap gap-2 text-xs">
        {isDeclining ? (
          <div className="flex items-center gap-1.5 text-amber-700 font-medium">
            <AlertTriangle className="w-4 h-4 text-amber-600" />
            <span>⚠️ Warning — potential degradation detected</span>
          </div>
        ) : (
          <div className="flex items-center gap-1.5 text-green-700 font-medium">
            <CheckCircle2 className="w-4 h-4 text-green-600" />
            <span>
              ✅ Stable — no significant degradation detected over the analysis period
            </span>
          </div>
        )}

        <span className="text-gray-400 font-mono text-[11px]">
          Sensor: Multi-Temporal MSI Sentinel-2
        </span>
      </div>
    </div>
  );
}

export default NdviChart;
