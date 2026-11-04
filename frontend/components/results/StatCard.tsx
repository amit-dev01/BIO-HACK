"use client";

import React, { useEffect, useState } from "react";
import { LucideIcon, TrendingUp, TrendingDown, Minus } from "lucide-react";
import { cn } from "@/lib/utils";
import { motion } from "framer-motion";
import { useAnimationEngine } from "@/context/AnimationContext";

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
  cardIndex?: number;
}

/**
 * Animated Odometer Digit Column (Faster 0.85s & Silky Smooth Deceleration)
 */
function OdometerDigit({
  digit,
  delay = 0,
  duration = 0.85,
  isReduced = false,
}: {
  digit: number;
  delay?: number;
  duration?: number;
  isReduced?: boolean;
}) {
  const digitsArray = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9];

  if (isReduced) {
    return <span>{digit}</span>;
  }

  return (
    <span className="inline-block h-[1.15em] overflow-hidden relative">
      <motion.span
        initial={{ y: "0%" }}
        animate={{ y: `-${digit * 10}%` }}
        transition={{
          duration: duration,
          delay: delay,
          ease: [0.16, 1, 0.3, 1], // snappy organic deceleration
        }}
        className="inline-flex flex-col items-center"
      >
        {digitsArray.map((d) => (
          <span key={d} className="h-[1.15em] flex items-center justify-center">
            {d}
          </span>
        ))}
      </motion.span>
    </span>
  );
}

/**
 * Parses formatted value string (e.g. "124,500" or "88.4") into rolling digits and symbols
 */
function OdometerValue({
  val,
  isReduced = false,
}: {
  val: string | number;
  isReduced?: boolean;
}) {
  const str = String(val);
  const chars = str.split("");

  let digitCounter = 0;

  return (
    <span className="inline-flex items-baseline">
      {chars.map((char, i) => {
        const isDigit = /\d/.test(char);
        if (isDigit) {
          const digit = parseInt(char, 10);
          const currentDelay = 0.06 + digitCounter * 0.035;
          digitCounter++;
          return (
            <OdometerDigit
              key={i}
              digit={digit}
              delay={currentDelay}
              duration={0.85}
              isReduced={isReduced}
            />
          );
        }
        // Non-digit punctuation (commas, dots, symbols)
        return (
          <span key={i} className="inline-block">
            {char}
          </span>
        );
      })}
    </span>
  );
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
  cardIndex = 0,
}: StatCardProps) {
  const { isReduced } = useAnimationEngine();

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
  const targetOffset = circumference - (clampedPercent / 100) * circumference;

  return (
    <motion.div
      initial={
        !isReduced
          ? { opacity: 0, y: 24, rotateX: 6 }
          : { opacity: 1, y: 0, rotateX: 0 }
      }
      animate={{ opacity: 1, y: 0, rotateX: 0 }}
      transition={{
        duration: 0.35,
        delay: cardIndex * 0.05,
        ease: [0.16, 1, 0.3, 1],
      }}
      className="crystal-glass-card rounded-3xl shadow-2xl p-6 sm:p-7 border border-white/20 hover:border-emerald-400/40 transition-all duration-300 flex flex-col justify-between relative overflow-hidden group text-white"
    >
      {/* Specular sheen */}
      <div className="pointer-events-none absolute inset-x-0 top-0 h-[1px] bg-gradient-to-r from-transparent via-white/30 to-transparent" />

      {/* Animation 7: Subtle Diagonal Light Sweep Shimmer */}
      {!isReduced && (
        <div
          className="pointer-events-none absolute inset-0 -translate-x-full bg-gradient-to-r from-transparent via-white/10 to-transparent skew-x-12 animate-card-shimmer z-10"
          style={{ animationDelay: `${0.8 + cardIndex * 0.08}s` }}
        />
      )}

      {/* Top Row: Icon + Title */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="bg-emerald-500/20 text-emerald-400 border border-emerald-400/30 p-2.5 rounded-2xl shadow-inner group-hover:scale-105 transition-transform duration-200">
            <Icon className="w-5 h-5 text-emerald-400" />
          </div>
          <span className="text-xs sm:text-sm font-semibold text-white/70 uppercase tracking-wider">
            {title}
          </span>
        </div>

        {/* Trend Badge with spring bounce pop */}
        {trend && (
          <motion.div
            initial={!isReduced ? { scale: 0, opacity: 0 } : { scale: 1, opacity: 1 }}
            animate={{ scale: [0, 1.15, 1.0], opacity: 1 }}
            transition={{
              duration: 0.3,
              delay: 0.85 + cardIndex * 0.05,
              ease: [0.175, 0.885, 0.32, 1.275],
            }}
            className={cn(
              "inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold font-mono shadow-xs backdrop-blur-md",
              trend.direction === "up" && "bg-emerald-500/20 text-emerald-300 border border-emerald-400/40",
              trend.direction === "down" && "bg-amber-500/20 text-amber-300 border border-amber-400/40",
              trend.direction === "neutral" && "bg-white/10 text-white/80 border border-white/20"
            )}
          >
            {trend.direction === "up" && <TrendingUp className="w-3.5 h-3.5" />}
            {trend.direction === "down" && <TrendingDown className="w-3.5 h-3.5" />}
            {trend.direction === "neutral" && <Minus className="w-3.5 h-3.5" />}
            <span>{trend.text}</span>
          </motion.div>
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
                className="text-white/10"
                strokeWidth="8"
                stroke="currentColor"
                fill="transparent"
              />
              {/* Animated Progress filled circle */}
              <motion.circle
                cx="48"
                cy="48"
                r={radius}
                className="text-emerald-400 drop-shadow-[0_0_8px_rgba(52,211,153,0.5)]"
                strokeWidth="8"
                strokeDasharray={circumference}
                initial={{ strokeDashoffset: circumference }}
                animate={{ strokeDashoffset: targetOffset }}
                transition={{
                  duration: 0.95,
                  delay: 0.15 + cardIndex * 0.05,
                  ease: [0.16, 1, 0.3, 1],
                }}
                strokeLinecap="round"
                stroke="currentColor"
                fill="transparent"
              />
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
              <span className="text-2xl font-bold font-mono text-white">
                <OdometerValue val={formattedValue} isReduced={isReduced} />
                {unit && (
                  <motion.span
                    initial={!isReduced ? { opacity: 0, x: 10 } : { opacity: 1, x: 0 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.75 + cardIndex * 0.05, duration: 0.25 }}
                    className="text-base text-white/70 ml-0.5"
                  >
                    {unit}
                  </motion.span>
                )}
              </span>
            </div>
          </div>
        </div>
      ) : (
        <div className="my-2">
          <div className="flex items-baseline gap-2 flex-wrap">
            <span
              className={cn(
                "text-4xl md:text-5xl font-extrabold font-mono tracking-tight drop-shadow-sm",
                isCarbon ? "text-emerald-400" : "text-white"
              )}
            >
              <OdometerValue val={formattedValue} isReduced={isReduced} />
            </span>
            {unit && (
              <motion.span
                initial={!isReduced ? { opacity: 0, x: 15 } : { opacity: 1, x: 0 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{
                  delay: 0.75 + cardIndex * 0.05,
                  duration: 0.25,
                  ease: [0.16, 1, 0.3, 1],
                }}
                className="text-lg text-emerald-200/80 font-mono font-medium"
              >
                {unit}
              </motion.span>
            )}
          </div>
        </div>
      )}

      {/* Bottom: Subtitle */}
      {subtitle && (
        <p className="text-xs sm:text-sm text-white/60 mt-2 font-normal">
          {subtitle}
        </p>
      )}
    </motion.div>
  );
}

export default StatCard;
