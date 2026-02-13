import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Sovereign Directives | ELYX Terms of Service",
  description: "Legal parameters and intelligence directives governing the ELYX neural network.",
};

export default function TermsLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}
