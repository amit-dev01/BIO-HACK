"use client";

import React, { useState, useEffect, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import {
  TreePine,
  Lock,
  Mail,
  User as UserIcon,
  ArrowRight,
  Loader2,
  AlertCircle,
  Sparkles,
  ShieldCheck,
  Globe2,
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { useAuth } from "@/context/AuthContext";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

function LoginForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const initialMode = searchParams.get("mode") === "signup" ? "signup" : "signin";

  const { signIn, signUp, signInWithGoogle, isLoading, isAuthenticated } = useAuth();

  const [mode, setMode] = useState<"signin" | "signup">(initialMode);
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // If already logged in, redirect to dashboard
  useEffect(() => {
    if (isAuthenticated) {
      router.push("/dashboard");
    }
  }, [isAuthenticated, router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage(null);

    if (!email || !email.includes("@")) {
      setErrorMessage("Please enter a valid email address.");
      return;
    }

    if (!password || password.length < 6) {
      setErrorMessage("Password must be at least 6 characters.");
      return;
    }

    try {
      if (mode === "signin") {
        await signIn(email, password);
      } else {
        await signUp(email, password, fullName || "Canopy Researcher");
      }
      router.push("/dashboard");
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Authentication failed. Please try again.";
      setErrorMessage(message);
    }
  };

  const handleGoogleSignIn = async () => {
    setErrorMessage(null);
    try {
      await signInWithGoogle();
      router.push("/dashboard");
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Google sign in failed.";
      setErrorMessage(message);
    }
  };

  const handleDemoSignIn = async () => {
    setErrorMessage(null);
    try {
      await signIn("elena.rostova@canopyai.earth", "password123");
      router.push("/dashboard");
    } catch {
      setErrorMessage("Demo sign-in failed.");
    }
  };

  return (
    <div className="relative min-h-screen flex items-center justify-center p-4 selection:bg-emerald-500 selection:text-white overflow-hidden">
      {/* 1. Deep Wild Jungle / Dense Rainforest Wallpaper (Vivid & Present) */}
      <div
        className="absolute inset-0 bg-cover bg-center select-none will-change-transform animate-canopy-breathe"
        style={{
          backgroundImage: `url('/images/jungle-dense.jpg')`,
          transformOrigin: "center center",
        }}
      />

      {/* 2. Soft Atmospheric Sunburst & Light Jungle Overlay (Never blacked out) */}
      <div className="absolute inset-0 bg-gradient-to-b from-black/45 via-black/20 to-black/55 pointer-events-none" />

      {/* 3. Ambient Living Sunbeams & Emerald Aura */}
      <div className="pointer-events-none absolute inset-0 overflow-hidden select-none">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[650px] h-[650px] bg-gradient-to-b from-emerald-400/20 via-green-500/10 to-transparent blur-3xl rounded-full" />
        <div className="absolute -top-32 left-1/4 w-40 h-[120vh] -rotate-[22deg] bg-gradient-to-b from-white/15 via-emerald-300/10 to-transparent blur-2xl animate-light-ray-drift" />
        <div className="absolute -top-32 right-1/4 w-48 h-[120vh] -rotate-[18deg] bg-gradient-to-b from-amber-200/15 via-white/5 to-transparent blur-3xl animate-light-ray-drift" />
      </div>

      {/* 4. Top-Left Floating Crystal Glass Navigation Pill */}
      <div className="absolute top-6 left-6 z-30">
        <Link
          href="/"
          className="crystal-glass px-4 py-2 rounded-2xl flex items-center gap-2.5 text-white hover:text-emerald-300 transition-all shadow-xl group hover:scale-105 active:scale-95"
        >
          <div className="p-1.5 rounded-xl bg-emerald-500/30 text-emerald-300 border border-emerald-400/40 group-hover:scale-110 transition-transform shadow-inner">
            <TreePine className="h-4 w-4 text-emerald-300" />
          </div>
          <span className="font-bold text-sm tracking-tight font-sans drop-shadow-sm">CanopyAI</span>
        </Link>
      </div>

      {/* 5. Ultra-Transparent Liquid Crystal Glass Card (Jungle visible through glass) */}
      <motion.div
        initial={{ opacity: 0, y: 30, scale: 0.95 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
        className="relative z-10 w-full max-w-md crystal-glass-card text-white rounded-3xl p-8 sm:p-10 my-8 overflow-hidden"
      >
        {/* Specular Top Reflection Highlight */}
        <div className="pointer-events-none absolute inset-x-0 top-0 h-[1.5px] bg-gradient-to-r from-transparent via-white/70 to-transparent" />

        {/* Card Header with Glowing Jungle Beacon */}
        <div className="text-center mb-7 space-y-3">
          <motion.div
            whileHover={{ scale: 1.1, rotate: 6 }}
            transition={{ type: "spring", stiffness: 400, damping: 20 }}
            className="inline-flex p-3 rounded-2xl bg-emerald-500/25 border border-emerald-400/50 text-emerald-300 shadow-xl relative"
          >
            <TreePine className="h-8 w-8 text-emerald-300 drop-shadow-[0_0_12px_rgba(52,211,153,0.8)]" />
            <span className="absolute -top-1 -right-1 flex h-3.5 w-3.5">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-80" />
              <span className="relative inline-flex rounded-full h-3.5 w-3.5 bg-emerald-400 shadow-lg" />
            </span>
          </motion.div>

          <h1 className="text-2xl sm:text-3xl font-black text-white tracking-tight drop-shadow-md">
            {mode === "signin" ? (
              <span>Jungle AI Portal</span>
            ) : (
              <span>Create Your Account</span>
            )}
          </h1>
          <p className="text-xs text-gray-200/90 leading-relaxed max-w-xs mx-auto drop-shadow-xs">
            {mode === "signin"
              ? "Access planetary forest plots, IPCC Tier-3 biomass analytics, and verified MRV audit dossiers."
              : "Join global conservation trusts calculating spaceborne biomass across wild tropical jungles."}
          </p>
        </div>

        {/* Liquid Crystal Glass Mode Switcher */}
        <div className="flex crystal-glass p-1.5 rounded-2xl mb-6">
          <button
            type="button"
            onClick={() => {
              setMode("signin");
              setErrorMessage(null);
            }}
            className={`flex-1 py-2 text-xs font-bold rounded-xl transition-all duration-200 cursor-pointer ${
              mode === "signin"
                ? "crystal-glass-btn text-white"
                : "text-gray-300 hover:text-white"
            }`}
          >
            Sign In
          </button>
          <button
            type="button"
            onClick={() => {
              setMode("signup");
              setErrorMessage(null);
            }}
            className={`flex-1 py-2 text-xs font-bold rounded-xl transition-all duration-200 cursor-pointer ${
              mode === "signup"
                ? "crystal-glass-btn text-white"
                : "text-gray-300 hover:text-white"
            }`}
          >
            Create Account
          </button>
        </div>

        {/* Error Alert */}
        <AnimatePresence>
          {errorMessage && (
            <motion.div
              initial={{ opacity: 0, y: -10, scale: 0.95 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: -10, scale: 0.95 }}
              className="mb-5 p-3.5 rounded-2xl bg-red-500/25 border border-red-500/50 text-red-200 text-xs flex items-center gap-2.5 backdrop-blur-md shadow-lg"
            >
              <AlertCircle className="w-4 h-4 text-red-400 shrink-0" />
              <span>{errorMessage}</span>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Authentication Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          {mode === "signup" && (
            <div className="space-y-1.5">
              <Label htmlFor="fullName" className="text-xs font-bold text-emerald-300 drop-shadow-xs">
                Full Name &amp; Title
              </Label>
              <div className="relative">
                <Input
                  id="fullName"
                  type="text"
                  placeholder="Dr. Elena Rostova"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  className="pl-10 h-11 crystal-glass-input rounded-2xl placeholder:text-gray-400 text-xs sm:text-sm font-medium"
                  required={mode === "signup"}
                />
                <UserIcon className="w-4 h-4 text-emerald-400 absolute left-3.5 top-3.5 pointer-events-none" />
              </div>
            </div>
          )}

          <div className="space-y-1.5">
            <Label htmlFor="email" className="text-xs font-bold text-emerald-300 drop-shadow-xs">
              Work Email
            </Label>
            <div className="relative">
              <Input
                id="email"
                type="email"
                placeholder="elena.rostova@canopyai.earth"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="pl-10 h-11 crystal-glass-input rounded-2xl placeholder:text-gray-400 text-xs sm:text-sm font-medium"
                required
              />
              <Mail className="w-4 h-4 text-emerald-400 absolute left-3.5 top-3.5 pointer-events-none" />
            </div>
          </div>

          <div className="space-y-1.5">
            <div className="flex items-center justify-between">
              <Label htmlFor="password" className="text-xs font-bold text-emerald-300 drop-shadow-xs">
                Password
              </Label>
              {mode === "signin" && (
                <button
                  type="button"
                  onClick={() => alert("Password reset link dispatched to your registered email.")}
                  className="text-[11px] text-emerald-300 hover:text-emerald-200 hover:underline font-medium transition-colors"
                >
                  Forgot password?
                </button>
              )}
            </div>
            <div className="relative">
              <Input
                id="password"
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="pl-10 h-11 crystal-glass-input rounded-2xl placeholder:text-gray-400 text-xs sm:text-sm font-medium"
                required
              />
              <Lock className="w-4 h-4 text-emerald-400 absolute left-3.5 top-3.5 pointer-events-none" />
            </div>
          </div>

          <Button
            type="submit"
            disabled={isLoading}
            className="w-full crystal-glass-btn text-white font-black h-12 rounded-2xl shadow-2xl transition-all duration-200 hover:scale-[1.02] active:scale-[0.98] gap-2 mt-2 text-sm tracking-wide"
          >
            {isLoading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Connecting to Satellite Network...</span>
              </>
            ) : (
              <>
                <span>{mode === "signin" ? "Sign In to CanopyAI" : "Launch Carbon Workspace"}</span>
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </Button>
        </form>

        {/* Divider */}
        <div className="relative my-6">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-white/20" />
          </div>
          <div className="relative flex justify-center text-[10px] uppercase tracking-widest font-mono">
            <span className="crystal-glass px-3.5 py-0.5 text-gray-300 rounded-full">
              Or continue with
            </span>
          </div>
        </div>

        {/* Social Google & Instant Demo Buttons */}
        <div className="space-y-3">
          <button
            type="button"
            onClick={handleGoogleSignIn}
            disabled={isLoading}
            className="w-full flex items-center justify-center gap-3 py-2.5 px-4 crystal-glass text-white text-xs font-bold hover:bg-white/15 transition-all shadow-lg hover:scale-[1.01] active:scale-[0.98] rounded-2xl"
          >
            <svg className="w-4 h-4" viewBox="0 0 24 24">
              <path
                fill="#4285F4"
                d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
              />
              <path
                fill="#34A853"
                d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
              />
              <path
                fill="#FBBC05"
                d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"
              />
              <path
                fill="#EA4335"
                d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"
              />
            </svg>
            <span>Continue with Google</span>
          </button>

          {/* Instant Demo Session */}
          <button
            type="button"
            onClick={handleDemoSignIn}
            disabled={isLoading}
            className="w-full flex items-center justify-center gap-2 py-2.5 px-4 rounded-2xl border border-emerald-400/40 bg-emerald-500/20 text-emerald-200 text-xs font-bold hover:bg-emerald-500/30 transition-all shadow-inner hover:scale-[1.01] active:scale-[0.98] backdrop-blur-xl"
          >
            <Sparkles className="w-3.5 h-3.5 text-amber-300" />
            <span>Instant Demo Session (Dr. Elena Rostova)</span>
          </button>
        </div>

        {/* Security Compliance Footer */}
        <div className="pt-6 border-t border-white/15 mt-6 flex items-center justify-center gap-2 text-[11px] text-gray-300 font-mono">
          <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
          <span>SOC-2 &amp; GDPR Compliant • Verra VCS MRV</span>
        </div>
      </motion.div>
    </div>
  );
}

export default function LoginPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen flex items-center justify-center bg-[#05180A] text-white">
          <Loader2 className="w-8 h-8 animate-spin text-emerald-400" />
        </div>
      }
    >
      <LoginForm />
    </Suspense>
  );
}
