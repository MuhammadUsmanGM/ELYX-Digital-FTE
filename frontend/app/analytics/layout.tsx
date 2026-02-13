import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Statistical Prophet | Data-Driven Foresight",
  description: "High-level performance analytics and statistical forecasting for autonomous entities.",
};

export default function AnalyticsLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}
