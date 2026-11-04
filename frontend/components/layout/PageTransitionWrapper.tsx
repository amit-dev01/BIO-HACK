"use client";

import React from "react";
import { motion, AnimatePresence } from "framer-motion";
import { usePathname } from "next/navigation";
import { useAnimationEngine } from "@/context/AnimationContext";

export function PageTransitionWrapper({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const { isReduced } = useAnimationEngine();

  if (isReduced) {
    return <>{children}</>;
  }

  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={pathname}
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -12 }}
        transition={{ duration: 0.3, ease: [0.16, 1.0, 0.3, 1.0] }}
        className="w-full flex-1 flex flex-col"
      >
        {children}
      </motion.div>
    </AnimatePresence>
  );
}

export default PageTransitionWrapper;

