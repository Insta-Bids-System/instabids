import { useEffect } from "react";
import InspirationDashboard from "@/components/inspiration/InspirationDashboard";

export default function InspirationDemo() {
  useEffect(() => {
    // Set up demo user for testing
    const demoUser = {
      id: "550e8400-e29b-41d4-a716-446655440001",
      name: "Demo Homeowner",
      email: "demo@instabids.com",
    };
    localStorage.setItem("DEMO_USER", JSON.stringify(demoUser));
    console.log("🔧 Demo user set up:", demoUser);
  }, []);

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Inspiration Board Demo</h1>
          <p className="text-gray-600">Test the inspiration board functionality with demo data</p>
        </div>

        <InspirationDashboard />
      </div>
    </div>
  );
}
