import { useEffect, useState, useRef } from "react";
import { BrowserRouter, Routes, Route, Navigate, useLocation, useNavigate } from "react-router-dom";
import axios from "axios";
import { Toaster } from "@/components/ui/sonner";

// Pages
import LandingPage from "@/pages/LandingPage";
import LoginPage from "@/pages/LoginPage";
import RegisterPage from "@/pages/RegisterPage";
import StudentDashboard from "@/pages/student/StudentDashboard";
import TeacherDashboard from "@/pages/teacher/TeacherDashboard";
import ExamPage from "@/pages/student/ExamPage";
import ResultPage from "@/pages/student/ResultPage";
import AuthCallback from "@/pages/AuthCallback";
import AdminDashboard from "@/pages/admin/AdminDashboard";
import PendingApprovalPage from "@/pages/PendingApprovalPage";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
export const API = `${BACKEND_URL}/api`;

// Auth Context
export const AuthContext = React.createContext(null);

import React from 'react';

// Protected Route Component
const ProtectedRoute = ({ children, allowedRoles }) => {
  const location = useLocation();
  const navigate = useNavigate();
  const [isAuthenticated, setIsAuthenticated] = useState(
    location.state?.user ? true : null
  );
  const [user, setUser] = useState(location.state?.user || null);
  const [loading, setLoading] = useState(!location.state?.user);

  useEffect(() => {
    if (location.state?.user) {
      setUser(location.state.user);
      setIsAuthenticated(true);
      setLoading(false);
      return;
    }

    const checkAuth = async () => {
      const token = localStorage.getItem("token");
      
      try {
        const response = await axios.get(`${API}/auth/me`, {
          headers: token ? { Authorization: `Bearer ${token}` } : {},
          withCredentials: true,
        });
        setUser(response.data);
        setIsAuthenticated(true);
      } catch (error) {
        setIsAuthenticated(false);
        localStorage.removeItem("token");
        navigate("/login", { replace: true });
      } finally {
        setLoading(false);
      }
    };

    checkAuth();
  }, [location.state, navigate]);

  if (loading) {
    return (
      <div className="min-h-screen bg-[#020617] flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-slate-400">Loading...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  // Check if teacher is approved
  if (user?.role === "teacher" && user?.is_approved === false) {
    return <PendingApprovalPage user={user} />;
  }

  if (allowedRoles && !allowedRoles.includes(user?.role)) {
    if (user?.role === "admin") {
      return <Navigate to="/admin" replace />;
    }
    return <Navigate to={user?.role === "teacher" ? "/teacher" : "/student"} replace />;
  }

  return (
    <AuthContext.Provider value={{ user, setUser }}>
      {children}
    </AuthContext.Provider>
  );
};

// App Router
function AppRouter() {
  const location = useLocation();
  
  // Check for session_id in URL fragment (Google OAuth callback)
  if (location.hash?.includes('session_id=')) {
    return <AuthCallback />;
  }

  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/auth/callback" element={<AuthCallback />} />
      
      {/* Admin Routes */}
      <Route
        path="/admin/*"
        element={
          <ProtectedRoute allowedRoles={["admin"]}>
            <AdminDashboard />
          </ProtectedRoute>
        }
      />
      
      {/* Student Routes */}
      <Route
        path="/student/*"
        element={
          <ProtectedRoute allowedRoles={["student"]}>
            <StudentDashboard />
          </ProtectedRoute>
        }
      />
      
      {/* Teacher Routes */}
      <Route
        path="/teacher/*"
        element={
          <ProtectedRoute allowedRoles={["teacher"]}>
            <TeacherDashboard />
          </ProtectedRoute>
        }
      />
      
      {/* Exam Route */}
      <Route
        path="/exam/:paperId"
        element={
          <ProtectedRoute allowedRoles={["student"]}>
            <ExamPage />
          </ProtectedRoute>
        }
      />
      
      {/* Result Route */}
      <Route
        path="/result/:resultId"
        element={
          <ProtectedRoute allowedRoles={["student"]}>
            <ResultPage />
          </ProtectedRoute>
        }
      />
      
      {/* Fallback */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

function App() {
  // Seed data on first load
  useEffect(() => {
    const seedData = async () => {
      try {
        await axios.post(`${API}/seed`);
      } catch (error) {
        console.log("Seed data may already exist");
      }
    };
    seedData();
  }, []);

  return (
    <BrowserRouter>
      <AppRouter />
      <Toaster position="top-right" richColors />
    </BrowserRouter>
  );
}

export default App;
