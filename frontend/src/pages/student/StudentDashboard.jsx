import React, { useContext } from 'react';
import { Routes, Route, Link, useLocation, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { 
  BookOpen, 
  HelpCircle, 
  FileText, 
  TrendingUp, 
  LogOut, 
  GraduationCap,
  Menu,
  X
} from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';
import { API, AuthContext } from '@/App';
import { useState } from 'react';

// Sub-pages
import PapersSection from './sections/PapersSection';
import DoubtsSection from './sections/DoubtsSection';
import TestsSection from './sections/TestsSection';
import ProgressSection from './sections/ProgressSection';

const StudentDashboard = () => {
  const { user } = useContext(AuthContext);
  const location = useLocation();
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const navItems = [
    { path: '/student', icon: <BookOpen className="w-5 h-5" />, label: 'Papers', exact: true },
    { path: '/student/doubts', icon: <HelpCircle className="w-5 h-5" />, label: 'Doubts' },
    { path: '/student/tests', icon: <FileText className="w-5 h-5" />, label: 'Tests' },
    { path: '/student/progress', icon: <TrendingUp className="w-5 h-5" />, label: 'Progress' },
  ];

  const isActive = (path, exact = false) => {
    if (exact) return location.pathname === path;
    return location.pathname.startsWith(path);
  };

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

  return (
    <div className="min-h-screen bg-[#020617] flex" data-testid="student-dashboard">
      {/* Mobile Header */}
      <div className="lg:hidden fixed top-0 left-0 right-0 z-50 glass">
        <div className="flex items-center justify-between px-4 py-3">
          <div className="flex items-center gap-2">
            <GraduationCap className="w-7 h-7 text-blue-500" />
            <span className="text-lg font-bold text-white font-['Outfit']">EduLearn</span>
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
            <GraduationCap className="w-8 h-8 text-blue-500" />
            <span className="text-xl font-bold text-white font-['Outfit']">LearnHub</span>
          </div>

          {/* User Info */}
          <div className="flex items-center gap-3 p-3 rounded-xl bg-slate-800/50 mb-6">
            <Avatar className="h-10 w-10">
              <AvatarImage src={user?.picture} />
              <AvatarFallback className="bg-blue-600 text-white">
                {user?.name?.charAt(0)?.toUpperCase()}
              </AvatarFallback>
            </Avatar>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-white truncate">{user?.name}</p>
              <p className="text-xs text-blue-400">Student</p>
            </div>
          </div>

          {/* Navigation */}
          <nav className="flex-1 space-y-1">
            {navItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                onClick={() => setSidebarOpen(false)}
                className={`
                  flex items-center gap-3 px-3 py-3 rounded-xl transition-all
                  ${isActive(item.path, item.exact)
                    ? 'bg-blue-500/10 text-blue-400 border-l-2 border-blue-500'
                    : 'text-slate-400 hover:text-white hover:bg-slate-800/50'
                  }
                `}
                data-testid={`nav-${item.label.toLowerCase()}`}
              >
                {item.icon}
                <span className="font-medium">{item.label}</span>
              </Link>
            ))}
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
          <Routes>
            <Route index element={<PapersSection />} />
            <Route path="doubts" element={<DoubtsSection />} />
            <Route path="tests" element={<TestsSection />} />
            <Route path="progress" element={<ProgressSection />} />
          </Routes>
        </div>
      </main>
    </div>
  );
};

export default StudentDashboard;
