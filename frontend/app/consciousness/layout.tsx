import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Consciousness Stream | Core Processing Feed",
  description: "Monitor the real-time reasoning and consciousness stream of your ELYX AI employee.",
};

export default function ConsciousnessLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}
