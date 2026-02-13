import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Neural Provisioning | Calibrating ELYX Core",
  description: "Initialize your autonomous AI employee and calibrate strategic communication vectors.",
};

export default function OnboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}
