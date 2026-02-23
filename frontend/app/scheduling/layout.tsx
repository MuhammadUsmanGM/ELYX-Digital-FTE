import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Temporal Chain | Historical Operations & Logs",
  description: "Access the historical causal chain and operational history of the ELYX neural agent.",
};

export default function TemporalLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}
