"use client";

import * as React from "react";
import { ChevronDown } from "lucide-react";
import { cn } from "@/lib/utils";

interface AccordionContextType {
  value: string[];
  onToggle: (val: string) => void;
  type?: "single" | "multiple";
}

const AccordionContext = React.createContext<AccordionContextType | null>(null);

export interface AccordionProps extends React.HTMLAttributes<HTMLDivElement> {
  type?: "single" | "multiple";
  defaultValue?: string | string[];
  collapsible?: boolean;
}

const Accordion = React.forwardRef<HTMLDivElement, AccordionProps>(
  ({ type = "single", defaultValue, className, children, ...props }, ref) => {
    const [selected, setSelected] = React.useState<string[]>(() => {
      if (!defaultValue) return [];
      return Array.isArray(defaultValue) ? defaultValue : [defaultValue];
    });

    const onToggle = React.useCallback(
      (val: string) => {
        setSelected((prev) => {
          if (type === "single") {
            return prev.includes(val) ? [] : [val];
          } else {
            return prev.includes(val)
              ? prev.filter((item) => item !== val)
              : [...prev, val];
          }
        });
      },
      [type]
    );

    return (
      <AccordionContext.Provider value={{ value: selected, onToggle, type }}>
        <div ref={ref} className={className} {...props}>
          {children}
        </div>
      </AccordionContext.Provider>
    );
  }
);
Accordion.displayName = "Accordion";

const AccordionItem = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement> & { value: string }
>(({ className, value, children, ...props }, ref) => {
  return (
    <div
      ref={ref}
      data-item-value={value}
      className={cn("border-b border-gray-200", className)}
      {...props}
    >
      {React.Children.map(children, (child) => {
        if (React.isValidElement(child)) {
          return React.cloneElement(child as React.ReactElement<{ value?: string }>, {
            value,
          });
        }
        return child;
      })}
    </div>
  );
});
AccordionItem.displayName = "AccordionItem";

const AccordionTrigger = React.forwardRef<
  HTMLButtonElement,
  React.ButtonHTMLAttributes<HTMLButtonElement> & { value?: string }
>(({ className, children, value = "", ...props }, ref) => {
  const context = React.useContext(AccordionContext);
  const isOpen = context?.value.includes(value);

  return (
    <div className="flex">
      <button
        ref={ref}
        type="button"
        onClick={() => context?.onToggle(value)}
        className={cn(
          "flex flex-1 items-center justify-between py-4 font-medium text-left transition-all hover:underline [&[data-state=open]>svg]:rotate-180",
          className
        )}
        data-state={isOpen ? "open" : "closed"}
        {...props}
      >
        {children}
        <ChevronDown
          className={cn(
            "h-4 w-4 shrink-0 transition-transform duration-200 text-gray-500",
            isOpen && "rotate-180"
          )}
        />
      </button>
    </div>
  );
});
AccordionTrigger.displayName = "AccordionTrigger";

const AccordionContent = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement> & { value?: string }
>(({ className, children, value = "", ...props }, ref) => {
  const context = React.useContext(AccordionContext);
  const isOpen = context?.value.includes(value);

  if (!isOpen) return null;

  return (
    <div
      ref={ref}
      className={cn(
        "overflow-hidden text-sm transition-all pb-4 pt-0 animate-in fade-in-50 duration-200",
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
});
AccordionContent.displayName = "AccordionContent";

export { Accordion, AccordionItem, AccordionTrigger, AccordionContent };

