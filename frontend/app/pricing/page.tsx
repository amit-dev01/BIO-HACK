"use client";

import React, { useState } from "react";
import Link from "next/link";
import Navbar from "@/components/layout/Navbar";
import Footer from "@/components/layout/Footer";
import { Check, X, Sparkles, HelpCircle, ArrowRight, ShieldCheck } from "lucide-react";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

export default function PricingPage() {
  const [annualBilling, setAnnualBilling] = useState(true);

  const tiers = [
    {
      name: "Explorer",
      badge: "Free forever",
      priceMonthly: 0,
      priceAnnual: 0,
      description: "Ideal for students, researchers, and small woodland owners exploring carbon potential.",
      features: [
        { text: "3 analyses/month", included: true },
        { text: "Satellite data only (Sentinel-2 & GEDI)", included: true },
        { text: "Watermarked PDF reports", included: true },
        { text: "Email support", included: true },
        { text: "Basic NDVI trends (1 year)", included: true },
        { text: "Drone image upload & fusion", included: false },
        { text: "API access", included: false },
        { text: "Custom allometric equations", included: false },
      ],
      ctaText: "Get Started Free",
      ctaHref: "/login?mode=signup&plan=free",
      ctaVariant: "outline" as const,
      popular: false,
    },
    {
      name: "Developer",
      subName: "Pro",
      badge: "Most Popular",
      priceMonthly: 99,
      priceAnnual: 79,
      description: "For forest carbon developers, conservation trusts, and certified auditors needing high precision.",
      features: [
        { text: "Unlimited analyses", included: true },
        { text: "Drone image upload & multi-sensor fusion", included: true },
        { text: "Full PDF reports (no watermark)", included: true },
        { text: "NDVI time-series history (5 years)", included: true },
        { text: "API access (100 calls/month)", included: true },
        { text: "Priority support (24h response)", included: true },
        { text: "Pre-feasibility VCS credit estimator", included: true },
        { text: "Custom allometric equations", included: false },
      ],
      ctaText: "Start Pro Trial",
      ctaHref: "/login?mode=signup&plan=pro",
      ctaVariant: "default" as const,
      popular: true,
    },
    {
      name: "Portfolio",
      subName: "Enterprise",
      badge: "Enterprise Grade",
      priceMonthly: 599,
      priceAnnual: 499,
      description: "For institutional carbon aggregators, verifiers, and multi-national forestry operators.",
      features: [
        { text: "Everything in Pro included", included: true },
        { text: "Unlimited API access & webhooks", included: true },
        { text: "100+ site portfolio monitoring", included: true },
        { text: "Custom allometric biomass models", included: true },
        { text: "White-label & co-branded reports", included: true },
        { text: "Dedicated ecological account manager", included: true },
        { text: "SSO & enterprise team RBAC", included: true },
        { text: "On-premise / private cloud deploy option", included: true },
      ],
      ctaText: "Contact Sales",
      ctaHref: "mailto:sales@canopyai.earth?subject=Enterprise%20Plan%20Inquiry",
      ctaVariant: "outline" as const,
      popular: false,
    },
  ];

  const faqs = [
    {
      question: "Can I cancel anytime?",
      answer:
        "Yes, absolutely. You can cancel or change your subscription tier at any time with a single click from your account dashboard. If you cancel, your account remains active with all paid features until the end of the current billing cycle.",
    },
    {
      question: "What satellite data do you use?",
      answer:
        "We fuse multi-sensor observations from European Space Agency's Sentinel-2 MSI (10m multispectral), NASA's spaceborne GEDI LiDAR (3D vertical canopy profile), JAXA's ALOS PALSAR-2 (L-band synthetic aperture radar that penetrates clouds), and high-resolution PlanetScope imagery.",
    },
    {
      question: "How accurate are the estimates?",
      answer:
        "Our allometric ML models achieve a validated R² > 0.91 correlation with ground-truth Forest Inventory and Analysis (FIA) plots. Each report provides 95% statistical confidence intervals and Tier 3 IPCC compliance metrics.",
    },
    {
      question: "Do you offer discounts for NGOs?",
      answer:
        "Yes! We offer a 50% discount for non-profit conservation groups, academic institutions, students, and indigenous community land trusts. Contact our support team to verify your non-profit or research affiliation.",
    },
    {
      question: "Can I use this for carbon credit verification?",
      answer:
        "CanopyAI reports are engineered to align with Verra VCS methodologies (such as VM0007 and VM0047) and Gold Standard guidelines. They provide standard-compliant stratification, biomass tables, and uncertainty bounds to fast-track your Project Design Document (PDD) validation.",
    },
  ];

  return (
    <div className="flex flex-col min-h-screen bg-[#F5F5F0] text-gray-900">
      <Navbar />

      <main className="flex-1 pt-24 pb-20">
        {/* Header Section */}
        <div className="max-w-4xl mx-auto px-4 text-center">
          <Badge className="bg-green-100 text-green-800 hover:bg-green-100 border-green-200 mb-4 px-3 py-1 font-mono text-xs">
            Simple, Transparent Pricing
          </Badge>
          <h1 className="text-4xl sm:text-5xl font-extrabold tracking-tight text-gray-900">
            Simple, Transparent Pricing
          </h1>
          <p className="mt-4 text-lg text-gray-500 max-w-2xl mx-auto">
            Start free. Scale when you&apos;re ready. Transparent ecological intelligence for any forest size.
          </p>

          {/* Billing Toggle (Monthly / Annual) */}
          <div className="mt-8 inline-flex items-center gap-3 bg-white p-1.5 rounded-full border border-gray-200 shadow-xs">
            <button
              type="button"
              onClick={() => setAnnualBilling(false)}
              className={`px-4 py-1.5 rounded-full text-xs font-semibold transition-all ${
                !annualBilling
                  ? "bg-forest text-white shadow-xs"
                  : "text-gray-600 hover:text-gray-900"
              }`}
            >
              Monthly Billing
            </button>
            <button
              type="button"
              onClick={() => setAnnualBilling(true)}
              className={`px-4 py-1.5 rounded-full text-xs font-semibold flex items-center gap-1.5 transition-all ${
                annualBilling
                  ? "bg-forest text-white shadow-xs"
                  : "text-gray-600 hover:text-gray-900"
              }`}
            >
              <span>Annual Billing</span>
              <span className="bg-green-200 text-green-900 text-[10px] px-1.5 py-0.5 rounded-full font-bold">
                Save 20%
              </span>
            </button>
          </div>
        </div>

        {/* Pricing Cards Grid */}
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 mt-12 grid grid-cols-1 md:grid-cols-3 gap-8 items-stretch">
          {tiers.map((tier) => {
            const price = annualBilling ? tier.priceAnnual : tier.priceMonthly;
            return (
              <div
                key={tier.name}
                className={`relative flex flex-col justify-between bg-white rounded-2xl p-8 transition-all duration-300 ${
                  tier.popular
                    ? "border-2 border-green-600 shadow-2xl md:-translate-y-2 ring-4 ring-green-600/10"
                    : "border border-gray-200 shadow-md hover:shadow-lg"
                }`}
              >
                {/* Popular Badge */}
                {tier.popular && (
                  <div className="absolute -top-3.5 right-6">
                    <span className="bg-green-600 text-white text-xs font-bold px-3 py-1 rounded-full shadow-sm flex items-center gap-1">
                      <Sparkles className="w-3.5 h-3.5" />
                      Most Popular
                    </span>
                  </div>
                )}

                <div>
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="text-xl font-bold text-gray-900">
                      {tier.name}{" "}
                      {tier.subName && (
                        <span className="text-green-700 text-sm font-semibold">
                          ({tier.subName})
                        </span>
                      )}
                    </h3>
                  </div>

                  <p className="text-xs text-gray-500 min-h-[36px] mb-6">
                    {tier.description}
                  </p>

                  {/* Price */}
                  <div className="mb-6 pb-6 border-b border-gray-100">
                    <div className="flex items-baseline gap-1">
                      <span className="text-4xl font-extrabold text-gray-900">
                        ${price}
                      </span>
                      <span className="text-sm font-medium text-gray-500">
                        /month
                      </span>
                    </div>
                    <p className="text-xs text-gray-400 mt-1">
                      {tier.priceMonthly === 0
                        ? "Free forever"
                        : annualBilling
                        ? `Billed annually ($${price * 12}/yr)`
                        : "Billed monthly"}
                    </p>
                  </div>

                  {/* Feature List */}
                  <div className="space-y-3 mb-8">
                    <p className="text-xs font-bold text-gray-900 uppercase tracking-wider">
                      Included Features
                    </p>
                    <ul className="space-y-2.5">
                      {tier.features.map((feature, idx) => (
                        <li key={idx} className="flex items-start gap-2.5 text-xs">
                          {feature.included ? (
                            <div className="p-0.5 rounded-full bg-green-100 text-green-700 mt-0.5 shrink-0">
                              <Check className="w-3.5 h-3.5" />
                            </div>
                          ) : (
                            <div className="p-0.5 rounded-full bg-gray-100 text-gray-400 mt-0.5 shrink-0">
                              <X className="w-3.5 h-3.5" />
                            </div>
                          )}
                          <span
                            className={
                              feature.included
                                ? "text-gray-700 font-medium"
                                : "text-gray-400"
                            }
                          >
                            {feature.text}
                          </span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>

                {/* Call to Action Button */}
                <div className="pt-4 border-t border-gray-100">
                  <Button
                    className={`w-full font-semibold transition-all ${
                      tier.popular
                        ? "bg-green-600 hover:bg-green-700 text-white text-base py-6 shadow-md hover:shadow-lg"
                        : tier.name === "Explorer"
                        ? "border-green-600 text-green-700 hover:bg-green-50"
                        : "bg-gray-900 hover:bg-black text-white py-5"
                    }`}
                    variant={tier.popular ? "default" : tier.name === "Explorer" ? "outline" : "default"}
                    asChild
                  >
                    <Link href={tier.ctaHref} className="flex items-center justify-center gap-2">
                      <span>{tier.ctaText}</span>
                      <ArrowRight className="w-4 h-4" />
                    </Link>
                  </Button>
                </div>
              </div>
            );
          })}
        </div>

        {/* Enterprise Callout Banner */}
        <div className="max-w-4xl mx-auto px-4 mt-16">
          <div className="bg-gradient-to-r from-green-900 via-forest to-green-900 text-white rounded-2xl p-8 flex flex-col md:flex-row items-center justify-between gap-6 shadow-lg">
            <div className="space-y-1">
              <span className="text-xs uppercase tracking-wider text-green-300 font-bold">
                Custom Deployments
              </span>
              <h3 className="text-xl font-bold">Need custom LiDAR calibration or sovereign hosting?</h3>
              <p className="text-xs text-green-100 max-w-lg">
                We partner with national forestry ministries and carbon registries for sovereign country-scale data deployments and custom allometry.
              </p>
            </div>
            <Button
              className="bg-white text-forest hover:bg-green-50 font-bold shrink-0"
              asChild
            >
              <a href="mailto:enterprise@canopyai.earth">Speak with an Ecologist</a>
            </Button>
          </div>
        </div>

        {/* FAQ Section with shadcn Accordion */}
        <div id="faq" className="max-w-3xl mx-auto px-4 sm:px-6 mt-24">
          <div className="text-center mb-10">
            <h2 className="text-3xl font-extrabold text-gray-900">
              Frequently Asked Questions
            </h2>
            <p className="mt-2 text-sm text-gray-500">
              Everything you need to know about our science, tiers, and data licensing.
            </p>
          </div>

          <Accordion type="single" collapsible className="space-y-4">
            {faqs.map((faq, index) => (
              <AccordionItem
                key={index}
                value={`faq-${index}`}
                className="bg-white rounded-xl border border-gray-200 px-6 shadow-xs"
              >
                <AccordionTrigger className="text-left font-semibold text-gray-900 hover:text-green-700 py-4">
                  {faq.question}
                </AccordionTrigger>
                <AccordionContent className="text-gray-600 text-sm leading-relaxed pb-4 pt-1">
                  {faq.answer}
                </AccordionContent>
              </AccordionItem>
            ))}
          </Accordion>
        </div>
      </main>

      <Footer />
    </div>
  );
}
