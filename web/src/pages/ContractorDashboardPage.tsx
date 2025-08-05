import { useNavigate } from "react-router-dom";
import ContractorDashboard from "@/components/contractor/ContractorDashboard";
import { useAuth } from "@/contexts/AuthContext";
import { BidCardProvider } from "@/contexts/BidCardContext";

export default function ContractorDashboardPage() {
  const _navigate = useNavigate();
  const { user } = useAuth();

  return (
    <BidCardProvider>
      <ContractorDashboard contractorId={user?.id} />
    </BidCardProvider>
  );
}
