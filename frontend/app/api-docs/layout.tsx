import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Developer Terminal | Integrated API Documentation",
  description: "Technical instructions and API references for integrating the ELYX neural network.",
};

export default function ApiDocsLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}
