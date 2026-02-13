import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Human-AI Collective | User & Agent Management",
  description: "Manage the synergy between human operators and autonomous ELYX agents within the mission collective.",
};

export default function UsersLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}
