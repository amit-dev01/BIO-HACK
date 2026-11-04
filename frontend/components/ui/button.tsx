import * as React from "react";
import { Slot } from "@radix-ui/react-slot";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const buttonVariants = cva(
  "inline-flex items-center justify-center whitespace-nowrap text-sm font-medium focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 rounded-button transition-all duration-200 hover:scale-[1.02] active:scale-[0.97] hover:shadow-[0_4px_20px_rgba(76,175,80,0.22)] active:transition-transform select-none cursor-pointer",
  {
    variants: {
      variant: {
        default: "bg-forest text-white hover:bg-forest/90 shadow-xs",
        destructive: "bg-destructive text-white hover:bg-destructive/90 shadow-xs",
        outline:
          "border border-input bg-background hover:bg-muted hover:text-charcoal shadow-xs",
        secondary: "bg-leaf text-white hover:bg-leaf/90 shadow-xs",
        ghost: "hover:bg-muted hover:text-charcoal",
        link: "text-forest underline-offset-4 hover:underline hover:scale-100 hover:shadow-none",
      },
      size: {
        default: "h-10 px-4 py-2",
        sm: "h-9 rounded-md px-3",
        lg: "h-11 rounded-md px-8 text-base",
        icon: "h-10 w-10",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : "button";
    return (
      <Comp
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        {...props}
      />
    );
  }
);
Button.displayName = "Button";

export { Button, buttonVariants };
