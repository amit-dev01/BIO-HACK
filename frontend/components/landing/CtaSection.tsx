import React from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";

export function CtaSection() {
  return (
    <section className="py-20 px-4 bg-forest text-white text-center">
      <div className="max-w-3xl mx-auto space-y-6">
        <h2 className="text-3xl sm:text-4xl font-bold">
          Ready to verify your forest carbon project?
        </h2>
        <p className="text-forest-100 max-w-xl mx-auto">
          Start analyzing your conservation plots or carbon offset project areas with instant satellite AI.
        </p>
        <div className="pt-2">
          <Button variant="secondary" size="lg" asChild>
            <Link href="/analyze">Start Free Analysis</Link>
          </Button>
        </div>
      </div>
    </section>
  );
}

export default CtaSection;

