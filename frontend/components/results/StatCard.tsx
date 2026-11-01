"use client";

import React from "react";
import { LucideIcon, TrendingUp, TrendingDown, Minus } from "lucide-react";
import { cn } from "@/lib/utils";

export interface StatTrend {
  direction: "up" | "down" | "neutral";
  text: string;
  color?: string;
}

export interface StatCardProps {
  title: string;
  value: string | number;
  unit?: string;
  subtitle?: string;
  icon: LucideIcon;
  trend?: StatTrend;
  variant?: "default" | "ring";
  isCarbon?: boolean;
}

export function StatCard({
  title,
  value,
  unit,
  subtitle,
  icon: Icon,
  trend,
  variant = "default",
  isCarbon = false,
}: StatCardProps) {
  // Format numeric values
  const formattedValue =
    typeof value === "number"
      ? value.toLocaleString()
      : !isNaN(Number(value))
      ? Number(value).toLocaleString()
      : value;

  // Percentage value for ring variant
  const numericVal =
    typeof value === "number" ? value : parseFloat(String(value)) || 0;
  const clampedPercent = Math.min(100, Math.max(0, numericVal));

  // Circular progress calculations (radius = 36, circumference = 2 * PI * 36 ≈ 226.19)
  const radius = 36;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset =
    circumference - (clampedPercent / 100) * circumference;

  return (
    <div className="bg-white rounded-xl shadow-md p-6 border border-gray-100 hover:shadow-lg transition-all duration-300 flex flex-col justify-between">
      {/* Top Row: Icon + Title */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="bg-green-100 text-green-700 p-2.5 rounded-xl shadow-xs">
            <Icon className="w-5 h-5 text-green-700" />
          </div>
          <span className="text-xs sm:text-sm font-semibold text-gray-500 uppercase tracking-wider">
            {title}
          </span>
        </div>

        {/* Trend Badge if provided */}
        {trend && (
          <div
            className={cn(
              "inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold font-mono",
              trend.direction === "up" && "bg-green-50 text-green-700 border border-green-200",
              trend.direction === "down" && "bg-amber-50 text-amber-700 border border-amber-200",
              trend.direction === "neutral" && "bg-gray-100 text-gray-700 border border-gray-200"
            )}
          >
            {trend.direction === "up" && <TrendingUp className="w-3.5 h-3.5" />}
            {trend.direction === "down" && <TrendingDown className="w-3.5 h-3.5" />}
            {trend.direction === "neutral" && <Minus className="w-3.5 h-3.5" />}
            <span>{trend.text}</span>
          </div>
        )}
      </div>

      {/* Middle: Value & Unit or Ring */}
      {variant === "ring" ? (
        <div className="py-2 flex items-center justify-center">
          <div className="relative w-28 h-28 flex items-center justify-center">
            <svg className="w-full h-full transform -rotate-90" viewBox="0 0 96 96">
              {/* Background track circle */}
              <circle
                cx="48"
                cy="48"
                r={radius}
                className="text-gray-100"
                strokeWidth="8"
                stroke="currentColor"
                fill="transparent"
              />
              {/* Progress filled circle */}
              <circle
                cx="48"
                cy="48"
                r={radius}
                className="text-green-600 transition-all duration-1000 ease-out"
                strokeWidth="8"
                strokeDasharray={circumference}
                strokeDashoffset={strokeDashoffset}
                strokeLinecap="round"
                stroke="currentColor"
                fill="transparent"
              />
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
              <span className="text-2xl font-bold font-mono text-gray-900">
                {formattedValue}
                {unit && <span className="text-base text-gray-500">{unit}</span>}
              </span>
            </div>
          </div>
        </div>
      ) : (
        <div className="my-2">
          <div className="flex items-baseline gap-2 flex-wrap">
            <span
              className={cn(
                "text-4xl md:text-5xl font-bold font-mono tracking-tight",
                isCarbon ? "text-green-700" : "text-gray-900"
              )}
            >
              {formattedValue}
            </span>
            {unit && (
              <span className="text-lg text-gray-500 font-mono font-medium">
                {unit}
              </span>
            )}
          </div>
        </div>
      )}

      {/* Bottom: Subtitle */}
      {subtitle && (
        <p className="text-xs sm:text-sm text-gray-400 mt-2 font-normal">
          {subtitle}
        </p>
      )}
    </div>
  );
}

export default StatCard;

