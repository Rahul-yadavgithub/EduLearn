import React, { useContext, useState, useEffect } from 'react';
import { Routes, Route, Link, useLocation, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  Users, 
  LogOut, 
  GraduationCap,
  Menu,
  X,
  CheckCircle,
  XCircle,
  Clock,
  Loader2
} from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';
import { API, AuthContext } from '@/App';

const AdminDashboard = () => {
  const { user } = useContext(AuthContext);
  const location = useLocation();
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [pendingTeachers, setPendingTeachers] = useState([]);
  const [allTeachers, setAllTeachers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchTeachers();
  }, []);

  const fetchTeachers = async () => {
    try {
      const token = localStorage.getItem('token');
      const headers = token ? { Authorization: `Bearer ${token}` } : {};
      
      const [pendingRes, allRes] = await Promise.all([
        axios.get(`${API}/admin/pending-teachers`, { headers, withCredentials: true }),
        axios.get(`${API}/admin/all-teachers`, { headers, withCredentials: true })
      ]);
      
      setPendingTeachers(pendingRes.data);
      setAllTeachers(allRes.data);
    } catch (error) {
      toast.error('Failed to fetch teachers');
    } finally {
      setLoading(false);
    }
  };

  const handleApproval = async (userId, approve) => {
    try {
      const token = localStorage.getItem('token');
      await axios.post(`${API}/admin/approve-teacher`, 
        { user_id: userId, approve },
        { 
          headers: token ? { Authorization: `Bearer ${token}` } : {},
          withCredentials: true 
        }
      );
      
      toast.success(approve ? 'Teacher approved successfully' : 'Teacher access revoked');
      fetchTeachers();
    } catch (error) {
      toast.error('Failed to update teacher status');
    }
  };

  const handleLogout = async () => {
    try {
      await axios.post(`${API}/auth/logout`, {}, { withCredentials: true });
    } catch (error) {}
    localStorage.removeItem('token');
    toast.success('Logged out successfully');
    navigate('/', { replace: true });
  };

  return (
    <div className="min-h-screen bg-[#020617] flex" data-testid="admin-dashboard">
      {/* Mobile Header */}
      <div className="lg:hidden fixed top-0 left-0 right-0 z-50 glass">
        <div className="flex items-center justify-between px-4 py-3">
          <div className="flex items-center gap-2">
            <GraduationCap className="w-7 h-7 text-purple-500" />
            <span className="text-lg font-bold text-white font-['Outfit']">Admin Panel</span>
          </div>
          <Button variant="ghost" size="icon" onClick={() => setSidebarOpen(!sidebarOpen)}>
            {sidebarOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </Button>
        </div>
      </div>

      {/* Sidebar */}
      <aside className={`
        fixed lg:static inset-y-0 left-0 z-40
        w-64 bg-slate-900/50 border-r border-slate-800
        transform transition-transform duration-300 ease-in-out
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
        pt-16 lg:pt-0
      `}>
        <div className="flex flex-col h-full p-4">
          {/* Logo */}
          <div className="hidden lg:flex items-center gap-2 px-2 py-4 mb-4">
            <GraduationCap className="w-8 h-8 text-purple-500" />
            <span className="text-xl font-bold text-white font-['Outfit']">Admin Panel</span>
          </div>

          {/* User Info */}
          <div className="flex items-center gap-3 p-3 rounded-xl bg-slate-800/50 mb-6">
            <Avatar className="h-10 w-10">
              <AvatarFallback className="bg-purple-600 text-white">A</AvatarFallback>
            </Avatar>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-white truncate">{user?.name}</p>
              <p className="text-xs text-purple-400">Administrator</p>
            </div>
          </div>

          {/* Navigation */}
          <nav className="flex-1 space-y-1">
            <Link
              to="/admin"
              onClick={() => setSidebarOpen(false)}
              className="flex items-center gap-3 px-3 py-3 rounded-xl bg-purple-500/10 text-purple-400 border-l-2 border-purple-500"
              data-testid="nav-teachers"
            >
              <Users className="w-5 h-5" />
              <span className="font-medium">Teacher Management</span>
            </Link>
          </nav>

          {/* Logout Button */}
          <Button
            variant="ghost"
            className="justify-start gap-3 text-slate-400 hover:text-red-400 hover:bg-red-500/10 mt-auto"
            onClick={handleLogout}
            data-testid="logout-btn"
          >
            <LogOut className="w-5 h-5" />
            Logout
          </Button>
        </div>
      </aside>

      {/* Backdrop for mobile */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-30 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Main Content */}
      <main className="flex-1 min-h-screen pt-16 lg:pt-0">
        <div className="p-6 lg:p-8">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-white font-['Outfit'] mb-2">Teacher Management</h1>
            <p className="text-slate-400">Approve or manage teacher accounts</p>
          </div>

          {/* Stats Cards */}
          <div className="grid md:grid-cols-3 gap-4 mb-8">
            <Card className="bg-slate-900/50 border-slate-800">
              <CardContent className="p-6 flex items-center gap-4">
                <div className="w-12 h-12 rounded-xl bg-amber-500/20 flex items-center justify-center">
                  <Clock className="w-6 h-6 text-amber-400" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-white">{pendingTeachers.length}</p>
                  <p className="text-sm text-slate-400">Pending Approval</p>
                </div>
              </CardContent>
            </Card>
            
            <Card className="bg-slate-900/50 border-slate-800">
              <CardContent className="p-6 flex items-center gap-4">
                <div className="w-12 h-12 rounded-xl bg-emerald-500/20 flex items-center justify-center">
                  <CheckCircle className="w-6 h-6 text-emerald-400" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-white">
                    {allTeachers.filter(t => t.is_approved).length}
                  </p>
                  <p className="text-sm text-slate-400">Approved Teachers</p>
                </div>
              </CardContent>
            </Card>
            
            <Card className="bg-slate-900/50 border-slate-800">
              <CardContent className="p-6 flex items-center gap-4">
                <div className="w-12 h-12 rounded-xl bg-purple-500/20 flex items-center justify-center">
                  <Users className="w-6 h-6 text-purple-400" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-white">{allTeachers.length}</p>
                  <p className="text-sm text-slate-400">Total Teachers</p>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Pending Teachers */}
          {pendingTeachers.length > 0 && (
            <Card className="bg-slate-900/50 border-slate-800 mb-6">
              <CardHeader>
                <CardTitle className="text-lg font-['Outfit'] text-white flex items-center gap-2">
                  <Clock className="w-5 h-5 text-amber-400" />
                  Pending Approval ({pendingTeachers.length})
                </CardTitle>
              </CardHeader>
              <CardContent>
                {loading ? (
                  <div className="flex items-center justify-center py-8">
                    <Loader2 className="w-8 h-8 animate-spin text-purple-500" />
                  </div>
                ) : (
                  <div className="space-y-3">
                    {pendingTeachers.map((teacher) => (
                      <div
                        key={teacher.user_id}
                        className="flex items-center justify-between p-4 rounded-xl bg-slate-800/50 border border-amber-500/30"
                        data-testid={`pending-teacher-${teacher.user_id}`}
                      >
                        <div className="flex items-center gap-4">
                          <Avatar className="h-12 w-12">
                            <AvatarImage src={teacher.picture} />
                            <AvatarFallback className="bg-amber-600 text-white">
                              {teacher.name?.charAt(0)?.toUpperCase()}
                            </AvatarFallback>
                          </Avatar>
                          <div>
                            <p className="font-medium text-white">{teacher.name}</p>
                            <p className="text-sm text-slate-400">{teacher.email}</p>
                            <p className="text-xs text-slate-500">
                              Registered: {new Date(teacher.created_at).toLocaleDateString()}
                            </p>
                          </div>
                        </div>
                        <div className="flex gap-2">
                          <Button
                            onClick={() => handleApproval(teacher.user_id, true)}
                            className="bg-emerald-600 hover:bg-emerald-700"
                            data-testid={`approve-${teacher.user_id}`}
                          >
                            <CheckCircle className="w-4 h-4 mr-2" />
                            Approve
                          </Button>
                          <Button
                            variant="outline"
                            onClick={() => handleApproval(teacher.user_id, false)}
                            className="border-red-500/50 text-red-400 hover:bg-red-500/10"
                            data-testid={`reject-${teacher.user_id}`}
                          >
                            <XCircle className="w-4 h-4 mr-2" />
                            Reject
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          )}

          {/* All Teachers */}
          <Card className="bg-slate-900/50 border-slate-800">
            <CardHeader>
              <CardTitle className="text-lg font-['Outfit'] text-white flex items-center gap-2">
                <Users className="w-5 h-5 text-purple-400" />
                All Teachers
              </CardTitle>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="flex items-center justify-center py-8">
                  <Loader2 className="w-8 h-8 animate-spin text-purple-500" />
                </div>
              ) : allTeachers.length === 0 ? (
                <div className="text-center py-12">
                  <Users className="w-12 h-12 text-slate-600 mx-auto mb-4" />
                  <p className="text-slate-400">No teachers registered yet</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {allTeachers.filter(t => t.is_approved).map((teacher) => (
                    <div
                      key={teacher.user_id}
                      className="flex items-center justify-between p-4 rounded-xl bg-slate-800/50"
                      data-testid={`teacher-${teacher.user_id}`}
                    >
                      <div className="flex items-center gap-4">
                        <Avatar className="h-12 w-12">
                          <AvatarImage src={teacher.picture} />
                          <AvatarFallback className="bg-emerald-600 text-white">
                            {teacher.name?.charAt(0)?.toUpperCase()}
                          </AvatarFallback>
                        </Avatar>
                        <div>
                          <p className="font-medium text-white">{teacher.name}</p>
                          <p className="text-sm text-slate-400">{teacher.email}</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        <Badge className="bg-emerald-500/20 text-emerald-400">Approved</Badge>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleApproval(teacher.user_id, false)}
                          className="border-red-500/50 text-red-400 hover:bg-red-500/10"
                          data-testid={`revoke-${teacher.user_id}`}
                        >
                          Revoke Access
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
};

export default AdminDashboard;
