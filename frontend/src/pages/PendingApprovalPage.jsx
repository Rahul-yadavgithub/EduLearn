import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Clock, GraduationCap, LogOut, RefreshCw } from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';
import { API } from '@/App';

const PendingApprovalPage = ({ user }) => {
  const navigate = useNavigate();

  const handleLogout = async () => {
    try {
      await axios.post(`${API}/auth/logout`, {}, { withCredentials: true });
    } catch (error) {
      // Continue logout even if API fails
    }
    localStorage.removeItem('token');
    toast.success('Logged out successfully');
    navigate('/', { replace: true });
  };

  const handleRefresh = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API}/auth/me`, {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
        withCredentials: true
      });
      
      if (response.data.is_approved) {
        toast.success('Your account has been approved!');
        navigate('/teacher', { state: { user: response.data }, replace: true });
      } else {
        toast.info('Your account is still pending approval');
      }
    } catch (error) {
      toast.error('Failed to check approval status');
    }
  };

  return (
    <div className="min-h-screen bg-[#020617] flex items-center justify-center p-6" data-testid="pending-approval-page">
      <Card className="bg-slate-900/50 border-slate-800 max-w-md w-full">
        <CardContent className="p-8 text-center">
          <div className="w-20 h-20 rounded-full bg-amber-500/20 flex items-center justify-center mx-auto mb-6">
            <Clock className="w-10 h-10 text-amber-400" />
          </div>
          
          <h1 className="text-2xl font-bold text-white mb-2 font-['Outfit']">
            Account Pending Approval
          </h1>
          
          <p className="text-slate-400 mb-6">
            Welcome, <span className="text-white font-medium">{user?.name}</span>! Your teacher account is currently being reviewed by our admin team.
          </p>
          
          <div className="bg-amber-500/10 border border-amber-500/30 rounded-lg p-4 mb-6">
            <p className="text-amber-400 text-sm">
              You'll be able to access the teacher dashboard once your account is approved. This usually takes 24-48 hours.
            </p>
          </div>
          
          <div className="flex flex-col gap-3">
            <Button
              onClick={handleRefresh}
              className="w-full bg-emerald-600 hover:bg-emerald-700"
              data-testid="check-status-btn"
            >
              <RefreshCw className="w-4 h-4 mr-2" />
              Check Approval Status
            </Button>
            
            <Button
              variant="outline"
              onClick={handleLogout}
              className="w-full border-slate-700 text-slate-400 hover:text-red-400 hover:border-red-500/50"
              data-testid="logout-btn"
            >
              <LogOut className="w-4 h-4 mr-2" />
              Logout
            </Button>
          </div>
          
          <div className="mt-6 pt-6 border-t border-slate-800">
            <div className="flex items-center justify-center gap-2 text-slate-500">
              <GraduationCap className="w-5 h-5" />
              <span className="text-sm">LearnHub Teacher Portal</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default PendingApprovalPage;
