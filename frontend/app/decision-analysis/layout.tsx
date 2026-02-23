import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Reality Hub | Matrix Simulations & Scenarios",
  description: "Manage and simulate business scenarios within the ELYX reality hub. High-fidelity causal forecasting.",
};

export default function RealityLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}
