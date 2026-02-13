import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Secure Handshake | ELYX Neural Terminal",
  description: "Authenticate with the ELYX autonomous intelligence network. Secure causal-chain verification.",
};

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}
