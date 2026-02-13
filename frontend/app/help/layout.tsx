import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Support Terminal | Neural Knowledge Base",
  description: "Access support and technical documentation for the ELYX autonomous intelligence network.",
};

export default function HelpLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}
