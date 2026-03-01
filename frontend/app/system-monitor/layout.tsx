import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "System Monitor | Core Processing Feed",
  description: "Monitor the real-time reasoning and processing stream of your ELYX AI employee.",
};

export default function SystemMonitorLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}
