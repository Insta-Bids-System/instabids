import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import ContractorDashboard from '@/components/contractor/ContractorDashboard';
import { useAuth } from '@/contexts/AuthContext';

export default function ContractorDashboardPage() {
  const navigate = useNavigate();
  const { user } = useAuth();

  return (
    <ContractorDashboard contractorId={user?.id} />
  );
}