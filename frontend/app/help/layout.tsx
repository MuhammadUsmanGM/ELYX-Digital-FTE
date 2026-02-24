import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Support Hub | System Knowledge Base",
  description: "Access support and technical documentation for the ELYX autonomous operations network.",
};

export default function HelpLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}
