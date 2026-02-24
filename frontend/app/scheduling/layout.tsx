import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Workflow Timeline | Operational History & Logs",
  description: "Access the operational logs and task execution history of the ELYX system.",
};

export default function SchedulingLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}
