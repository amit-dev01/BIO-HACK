"use client";

import React, { useState, useEffect, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import { TreePine, Lock, Mail, User as UserIcon, ArrowRight, Loader2, AlertCircle, Sparkles } from "lucide-react";
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
    <div className="relative min-h-screen flex items-center justify-center p-4 selection:bg-green-500 selection:text-white">
      {/* High-resolution Forest Background with Overlay */}
      <div
        className="absolute inset-0 bg-cover bg-center z-0"
        style={{
          backgroundImage: `url('https://images.unsplash.com/photo-1511497584788-87676104235f?auto=format&fit=crop&w=2000&q=80')`,
        }}
      >
        <div className="absolute inset-0 bg-black/60 backdrop-blur-xs" />
      </div>

      {/* Top Left Navigation Link */}
      <div className="absolute top-6 left-6 z-20">
        <Link
          href="/"
          className="flex items-center gap-2 text-white/90 hover:text-white transition-colors group"
        >
          <div className="p-1.5 rounded-lg bg-white/20 backdrop-blur-md group-hover:bg-white/30 transition-colors">
            <TreePine className="h-5 w-5 text-green-400" />
          </div>
          <span className="font-bold text-lg tracking-tight">CanopyAI</span>
        </Link>
      </div>

      {/* Centered Auth Card */}
      <div className="relative z-10 w-full max-w-md bg-white rounded-2xl shadow-2xl p-8 border border-gray-100 my-8">
        {/* Card Header */}
        <div className="text-center mb-6">
          <div className="inline-flex p-3 rounded-2xl bg-green-50 text-forest mb-3 border border-green-100 shadow-xs">
            <TreePine className="h-8 w-8 text-[#1B5E20]" />
          </div>
          <h1 className="text-2xl font-extrabold text-gray-900 tracking-tight">
            {mode === "signin" ? "Welcome to CanopyAI" : "Create Your Account"}
          </h1>
          <p className="text-xs text-gray-500 mt-1">
            {mode === "signin"
              ? "Sign in to access your forest plots, MRV audits, and biomass analytics."
              : "Start monitoring forest carbon and calculating spaceborne biomass today."}
          </p>
        </div>

        {/* Tab Toggle */}
        <div className="flex bg-gray-100 p-1 rounded-xl mb-6">
          <button
            type="button"
            onClick={() => {
              setMode("signin");
              setErrorMessage(null);
            }}
            className={`flex-1 py-2 text-xs font-semibold rounded-lg transition-all ${
              mode === "signin"
                ? "bg-white text-gray-900 shadow-xs"
                : "text-gray-500 hover:text-gray-900"
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
            className={`flex-1 py-2 text-xs font-semibold rounded-lg transition-all ${
              mode === "signup"
                ? "bg-white text-gray-900 shadow-xs"
                : "text-gray-500 hover:text-gray-900"
            }`}
          >
            Create Account
          </button>
        </div>

        {/* Error Alert */}
        {errorMessage && (
          <div className="mb-4 p-3 rounded-xl bg-red-50 border border-red-200 text-red-700 text-xs flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{errorMessage}</span>
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          {mode === "signup" && (
            <div className="space-y-1.5">
              <Label htmlFor="fullName">Full Name</Label>
              <div className="relative">
                <Input
                  id="fullName"
                  type="text"
                  placeholder="Dr. Elena Rostova"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  className="pl-9"
                  required={mode === "signup"}
                />
                <UserIcon className="w-4 h-4 text-gray-400 absolute left-3 top-3 pointer-events-none" />
              </div>
            </div>
          )}

          <div className="space-y-1.5">
            <Label htmlFor="email">Work Email</Label>
            <div className="relative">
              <Input
                id="email"
                type="email"
                placeholder="name@organization.earth"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="pl-9"
                required
              />
              <Mail className="w-4 h-4 text-gray-400 absolute left-3 top-3 pointer-events-none" />
            </div>
          </div>

          <div className="space-y-1.5">
            <div className="flex items-center justify-between">
              <Label htmlFor="password">Password</Label>
              {mode === "signin" && (
                <button
                  type="button"
                  onClick={() => alert("Password reset link sent to registered email.")}
                  className="text-[11px] text-green-700 hover:underline font-medium"
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
                className="pl-9"
                required
              />
              <Lock className="w-4 h-4 text-gray-400 absolute left-3 top-3 pointer-events-none" />
            </div>
          </div>

          <Button
            type="submit"
            disabled={isLoading}
            className="w-full bg-green-600 hover:bg-green-700 text-white font-semibold py-2.5 rounded-xl shadow-md transition-all gap-2"
          >
            {isLoading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Authenticating...</span>
              </>
            ) : (
              <>
                <span>{mode === "signin" ? "Sign In" : "Get Started"}</span>
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </Button>
        </form>

        {/* Divider */}
        <div className="relative my-6">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-gray-200" />
          </div>
          <div className="relative flex justify-center text-xs uppercase">
            <span className="bg-white px-3 text-gray-400 font-medium">Or continue with</span>
          </div>
        </div>

        {/* Social Google Login Button */}
        <div className="space-y-2.5">
          <button
            type="button"
            onClick={handleGoogleSignIn}
            disabled={isLoading}
            className="w-full flex items-center justify-center gap-3 py-2.5 px-4 border border-gray-300 rounded-xl bg-white text-gray-700 text-xs font-semibold hover:bg-gray-50 transition-colors shadow-xs"
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

          {/* Quick Demo One-Click Login */}
          <button
            type="button"
            onClick={handleDemoSignIn}
            disabled={isLoading}
            className="w-full flex items-center justify-center gap-2 py-2 px-4 border border-green-200 bg-green-50 text-green-800 rounded-xl text-xs font-semibold hover:bg-green-100 transition-colors"
          >
            <Sparkles className="w-3.5 h-3.5 text-green-600" />
            <span>Instant Demo Login (Dr. Elena Rostova)</span>
          </button>
        </div>

        {/* Footer Note */}
        <p className="text-[11px] text-gray-400 text-center mt-6">
          By signing in, you agree to our Terms of Service and Privacy Policy. All remote sensing datasets adhere to open science guidelines.
        </p>
      </div>
    </div>
  );
}

export default function LoginPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen flex items-center justify-center bg-gray-900 text-white">
          <Loader2 className="w-8 h-8 animate-spin text-green-500" />
        </div>
      }
    >
      <LoginForm />
    </Suspense>
  );
}
