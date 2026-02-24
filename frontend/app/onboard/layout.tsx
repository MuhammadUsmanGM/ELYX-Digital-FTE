import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "System Provisioning | Configuring ELYX Core",
  description: "Initialize your autonomous AI employee and configure strategic communication channels.",
};

export default function OnboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}
