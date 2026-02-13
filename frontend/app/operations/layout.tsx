import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Operational Pulse | Autonomous Oversight",
  description: "Oversee active autonomous tasks and operation logs within the ELYX intelligence core.",
};

export default function OperationsLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}
