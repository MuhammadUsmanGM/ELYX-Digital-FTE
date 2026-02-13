import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Mission Control | ELYX Operations Dashboard",
  description: "Operational oversight for ELYX autonomous decision chains and neural task management.",
};

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}
