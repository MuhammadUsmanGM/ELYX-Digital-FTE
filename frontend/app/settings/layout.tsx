import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Core Calibration | Neural System Settings",
  description: "Configure neural core parameters and system-wide settings for the ELYX platform.",
};

export default function SettingsLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}
