"use client";

import React, { useState, useEffect } from "react";
import {
  Sparkles,
  ShieldCheck,
  FileCheck2,
  Send,
  Loader2,
  Bot,
  User,
  CheckCircle2,
  Info,
} from "lucide-react";
import { AnalysisResult } from "@/lib/types";
import { api } from "@/lib/api";

interface AiEcologicalSummaryProps {
  result: AnalysisResult;
}

interface Message {
  sender: "user" | "gemini";
  text: string;
}

export function AiEcologicalSummary({ result }: AiEcologicalSummaryProps) {
  const [narrative, setNarrative] = useState<any>(null);
  const [isLoadingNarrative, setIsLoadingNarrative] = useState(true);

  // Chat state
  const [messages, setMessages] = useState<Message[]>([
    {
      sender: "gemini",
      text: `Hello! I have analyzed the spaceborne telemetry for this ${result.forest_type || "forest"} tract (${(result.area_ha || 0).toLocaleString("en-US")} ha). Ask me anything about its biomass, carbon permanence, or Verra VCS registry compliance!`,
    },
  ]);
  const [inputQuestion, setInputQuestion] = useState("");
  const [isSending, setIsSending] = useState(false);
  const [interactionId, setInteractionId] = useState<string | undefined>(undefined);

  // Load narrative on mount
  useEffect(() => {
    let isMounted = true;
    setIsLoadingNarrative(true);

    api
      .getAiNarrative(result)
      .then((data) => {
        if (isMounted && data.narrative) {
          setNarrative(data.narrative);
        }
      })
      .catch((err) => {
        console.warn("Could not fetch AI narrative:", err);
      })
      .finally(() => {
        if (isMounted) setIsLoadingNarrative(false);
      });

    return () => {
      isMounted = false;
    };
  }, [result]);

  const handleSendMessage = async (customPrompt?: string) => {
    const question = customPrompt || inputQuestion.trim();
    if (!question || isSending) return;

    setInputQuestion("");
    setMessages((prev) => [...prev, { sender: "user", text: question }]);
    setIsSending(true);

    try {
      const data = await api.chatWithForest(result, question, interactionId);
      if (data && data.reply) {
        setMessages((prev) => [...prev, { sender: "gemini", text: data.reply }]);
        if (data.interaction_id) {
          setInteractionId(data.interaction_id);
        }
      }
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          sender: "gemini",
          text: "I could not complete the query right now. Please verify backend connection and try again.",
        },
      ]);
    } finally {
      setIsSending(false);
    }
  };

  const sampleQuestions = [
    "What is the estimated carbon revenue at $15/t?",
    "How does the canopy height compare to ecoregion average?",
    "Is this forest eligible for Verra VM0047?",
  ];

  return (
    <div className="crystal-glass-card rounded-3xl p-6 sm:p-8 shadow-2xl border border-white/20 text-white space-y-6 relative overflow-hidden">
      {/* Top Specular Shimmer */}
      <div className="pointer-events-none absolute inset-x-0 top-0 h-[1.5px] bg-gradient-to-r from-transparent via-white/70 to-transparent" />

      {/* Header */}
      <div className="flex items-center justify-between flex-wrap gap-4 border-b border-white/10 pb-5">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-emerald-500/30 to-purple-600/30 border border-emerald-400/40 flex items-center justify-center text-emerald-300 shadow-xl shadow-emerald-950/50">
            <Sparkles className="w-6 h-6 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center gap-2 flex-wrap">
              <h2 className="text-xl font-bold text-white tracking-tight drop-shadow-sm">
                AI Ecological Audit &amp; Verification Narrative
              </h2>
              <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-purple-500/20 text-purple-300 border border-purple-400/40 shadow-sm">
                <span className="w-1.5 h-1.5 rounded-full bg-purple-400 animate-ping" />
                Gemini 3.8 Flash
              </span>
            </div>
            <p className="text-xs text-white/60 mt-0.5">
              Grounded in NASA GEDI LiDAR &amp; Sentinel-2 spaceborne telemetry
            </p>
          </div>
        </div>
      </div>

      {/* Narrative Section */}
      {isLoadingNarrative ? (
        <div className="py-8 flex flex-col items-center justify-center text-center space-y-3">
          <Loader2 className="w-8 h-8 animate-spin text-emerald-400" />
          <p className="text-xs font-medium text-emerald-200/80">
            Gemini 3.8 Flash is analyzing spaceborne telemetry...
          </p>
        </div>
      ) : narrative ? (
        <div className="space-y-5">
          {/* Executive Summary */}
          <div className="bg-emerald-500/15 p-5 rounded-2xl border border-emerald-400/30 text-sm leading-relaxed text-emerald-100 shadow-inner">
            <p>{narrative.executive_summary}</p>
          </div>

          {/* 2-Column Evaluation Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 rounded-2xl bg-white/5 border border-white/10 space-y-2">
              <div className="flex items-center gap-2 text-xs font-bold text-emerald-300 uppercase tracking-wider">
                <ShieldCheck className="w-4 h-4 text-emerald-400" />
                <span>Carbon Permanence &amp; Risk</span>
              </div>
              <p className="text-xs text-white/80 leading-relaxed">
                {narrative.permanence_and_risk}
              </p>
            </div>

            <div className="p-4 rounded-2xl bg-white/5 border border-white/10 space-y-2">
              <div className="flex items-center gap-2 text-xs font-bold text-purple-300 uppercase tracking-wider">
                <FileCheck2 className="w-4 h-4 text-purple-400" />
                <span>Registry Compliance &amp; PDD Viability</span>
              </div>
              <p className="text-xs text-white/80 leading-relaxed">
                {narrative.registry_compliance}
              </p>
            </div>
          </div>

          {/* Key Highlights Chips */}
          {Array.isArray(narrative.key_highlights) && (
            <div className="flex flex-wrap gap-2 pt-1">
              {narrative.key_highlights.map((highlight: string, idx: number) => (
                <div
                  key={idx}
                  className="inline-flex items-center gap-1.5 px-3 py-1 rounded-xl bg-emerald-500/20 text-emerald-200 text-xs font-semibold border border-emerald-400/30 shadow-xs"
                >
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                  <span>{highlight}</span>
                </div>
              ))}
            </div>
          )}

          {narrative.notice && (
            <div className="text-[11px] text-white/50 flex items-center gap-1.5 pt-1">
              <Info className="w-3.5 h-3.5 shrink-0 text-emerald-400" />
              <span>{narrative.notice}</span>
            </div>
          )}
        </div>
      ) : null}

      {/* Interactive Chat with Forest Assistant */}
      <div className="border-t border-white/10 pt-6 space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Bot className="w-5 h-5 text-purple-400" />
            <h3 className="text-sm font-bold text-white tracking-tight">
              Ask Gemini About This Forest
            </h3>
          </div>
          <span className="text-[11px] text-white/50 font-mono">
            Telemetry Grounded Q&amp;A
          </span>
        </div>

        {/* Suggested Quick Prompts */}
        <div className="flex flex-wrap gap-2">
          {sampleQuestions.map((q, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => handleSendMessage(q)}
              disabled={isSending}
              className="text-[11px] px-3 py-1.5 rounded-full bg-white/10 hover:bg-emerald-500/25 hover:text-emerald-200 hover:border-emerald-400/40 border border-white/15 text-white/80 transition-all text-left shadow-xs"
            >
              &ldquo;{q}&rdquo;
            </button>
          ))}
        </div>

        {/* Chat History Box */}
        <div className="max-h-60 overflow-y-auto space-y-3 p-4 rounded-2xl bg-black/40 border border-white/15 text-xs shadow-inner">
          {messages.map((msg, idx) => (
            <div
              key={idx}
              className={`flex gap-2.5 ${
                msg.sender === "user" ? "justify-end" : "justify-start"
              }`}
            >
              {msg.sender === "gemini" && (
                <div className="w-6 h-6 rounded-full bg-purple-500/25 border border-purple-400/40 flex items-center justify-center text-purple-300 shrink-0 mt-0.5">
                  <Bot className="w-3.5 h-3.5" />
                </div>
              )}
              <div
                className={`max-w-[85%] p-3 rounded-2xl ${
                  msg.sender === "user"
                    ? "bg-emerald-600 text-white rounded-tr-none shadow-md"
                    : "bg-white/10 text-white shadow-sm border border-white/15 rounded-tl-none leading-relaxed"
                }`}
              >
                {msg.text}
              </div>
              {msg.sender === "user" && (
                <div className="w-6 h-6 rounded-full bg-emerald-500/25 border border-emerald-400/40 flex items-center justify-center text-emerald-300 shrink-0 mt-0.5">
                  <User className="w-3.5 h-3.5" />
                </div>
              )}
            </div>
          ))}
          {isSending && (
            <div className="flex gap-2.5 items-center text-emerald-300 text-xs italic">
              <Loader2 className="w-3.5 h-3.5 animate-spin text-purple-400" />
              <span>Gemini is thinking...</span>
            </div>
          )}
        </div>

        {/* Chat Input */}
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSendMessage();
          }}
          className="flex items-center gap-2"
        >
          <input
            type="text"
            value={inputQuestion}
            onChange={(e) => setInputQuestion(e.target.value)}
            placeholder="Ask a question (e.g. 'What is the fire risk here?')..."
            disabled={isSending}
            className="flex-1 px-4 py-2.5 rounded-xl border border-white/20 text-xs bg-black/30 text-white placeholder:text-white/40 focus:outline-none focus:ring-2 focus:ring-emerald-400 focus:border-transparent backdrop-blur-md"
          />
          <button
            type="submit"
            disabled={!inputQuestion.trim() || isSending}
            className="px-4 py-2.5 rounded-xl bg-purple-600 hover:bg-purple-500 disabled:opacity-40 text-white font-bold text-xs flex items-center gap-1.5 transition-all shadow-lg shadow-purple-950/50"
          >
            <span>Ask</span>
            <Send className="w-3.5 h-3.5" />
          </button>
        </form>
      </div>
    </div>
  );
}

export default AiEcologicalSummary;
