import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Service Terms | ELYX Operational Framework",
  description: "Legal parameters and operational directives governing the ELYX system network.",
};

export default function TermsLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}
