import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { 
  Trophy, 
  Target, 
  Clock, 
  CheckCircle, 
  XCircle, 
  BarChart3,
  ArrowLeft,
  Home,
  Loader2
} from 'lucide-react';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend } from 'recharts';
import axios from 'axios';
import { API } from '@/App';
import { toast } from 'sonner';

const ResultPage = () => {
  const { resultId } = useParams();
  const navigate = useNavigate();
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchResult();
  }, [resultId]);

  const fetchResult = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API}/tests/results/${resultId}`, {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
        withCredentials: true
      });
      setResult(response.data);
    } catch (error) {
      toast.error('Failed to load result');
      navigate('/student/tests');
    } finally {
      setLoading(false);
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}m ${secs}s`;
  };

  const getScoreGrade = (accuracy) => {
    if (accuracy >= 80) return { grade: 'Excellent', color: 'text-emerald-400', bg: 'bg-emerald-500/20' };
    if (accuracy >= 60) return { grade: 'Good', color: 'text-blue-400', bg: 'bg-blue-500/20' };
    if (accuracy >= 40) return { grade: 'Average', color: 'text-amber-400', bg: 'bg-amber-500/20' };
    return { grade: 'Needs Improvement', color: 'text-red-400', bg: 'bg-red-500/20' };
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#020617] flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
      </div>
    );
  }

  if (!result) return null;

  const pieData = [
    { name: 'Correct', value: result.correct_answers, color: '#10b981' },
    { name: 'Wrong', value: result.wrong_answers, color: '#ef4444' },
    { name: 'Unattempted', value: result.unattempted, color: '#64748b' },
  ].filter(d => d.value > 0);

  const scoreInfo = getScoreGrade(result.accuracy);

  return (
    <div className="min-h-screen bg-[#020617] p-6 lg:p-8" data-testid="result-page">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <Button
            variant="ghost"
            onClick={() => navigate('/student/tests')}
            className="text-slate-400 hover:text-white"
            data-testid="back-btn"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Tests
          </Button>
          <Button
            onClick={() => navigate('/student')}
            className="bg-blue-600 hover:bg-blue-700"
            data-testid="home-btn"
          >
            <Home className="w-4 h-4 mr-2" />
            Dashboard
          </Button>
        </div>

        {/* Score Card */}
        <Card className="bg-slate-900/50 border-slate-800 mb-8 overflow-hidden">
          <div className="relative">
            <div className="absolute inset-0 bg-gradient-to-r from-blue-600/20 to-purple-600/20"></div>
            <CardContent className="relative p-8 text-center">
              <div className={`inline-flex items-center gap-2 px-4 py-2 rounded-full ${scoreInfo.bg} mb-4`}>
                <Trophy className={`w-5 h-5 ${scoreInfo.color}`} />
                <span className={`font-medium ${scoreInfo.color}`}>{scoreInfo.grade}</span>
              </div>
              
              <h1 className="text-5xl font-bold text-white mb-2 font-['Outfit']" data-testid="score">
                {result.score}
              </h1>
              <p className="text-slate-400 mb-4">Total Score</p>
              
              <div className="flex items-center justify-center gap-8 text-sm">
                <div className="text-center">
                  <p className="text-2xl font-bold text-white">{result.accuracy}%</p>
                  <p className="text-slate-400">Accuracy</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-white">{formatTime(result.time_taken)}</p>
                  <p className="text-slate-400">Time Taken</p>
                </div>
              </div>
            </CardContent>
          </div>
        </Card>

        {/* Stats Grid */}
        <div className="grid md:grid-cols-4 gap-4 mb-8">
          <Card className="bg-slate-900/50 border-slate-800">
            <CardContent className="p-4 text-center">
              <div className="w-10 h-10 rounded-lg bg-slate-800 flex items-center justify-center mx-auto mb-2">
                <Target className="w-5 h-5 text-blue-400" />
              </div>
              <p className="text-2xl font-bold text-white">{result.total_questions}</p>
              <p className="text-xs text-slate-400">Total Questions</p>
            </CardContent>
          </Card>
          
          <Card className="bg-slate-900/50 border-slate-800">
            <CardContent className="p-4 text-center">
              <div className="w-10 h-10 rounded-lg bg-emerald-500/20 flex items-center justify-center mx-auto mb-2">
                <CheckCircle className="w-5 h-5 text-emerald-400" />
              </div>
              <p className="text-2xl font-bold text-emerald-400">{result.correct_answers}</p>
              <p className="text-xs text-slate-400">Correct</p>
            </CardContent>
          </Card>
          
          <Card className="bg-slate-900/50 border-slate-800">
            <CardContent className="p-4 text-center">
              <div className="w-10 h-10 rounded-lg bg-red-500/20 flex items-center justify-center mx-auto mb-2">
                <XCircle className="w-5 h-5 text-red-400" />
              </div>
              <p className="text-2xl font-bold text-red-400">{result.wrong_answers}</p>
              <p className="text-xs text-slate-400">Wrong</p>
            </CardContent>
          </Card>
          
          <Card className="bg-slate-900/50 border-slate-800">
            <CardContent className="p-4 text-center">
              <div className="w-10 h-10 rounded-lg bg-slate-800 flex items-center justify-center mx-auto mb-2">
                <BarChart3 className="w-5 h-5 text-slate-400" />
              </div>
              <p className="text-2xl font-bold text-slate-400">{result.unattempted}</p>
              <p className="text-xs text-slate-400">Skipped</p>
            </CardContent>
          </Card>
        </div>

        <div className="grid lg:grid-cols-2 gap-6">
          {/* Pie Chart */}
          <Card className="bg-slate-900/50 border-slate-800">
            <CardHeader>
              <CardTitle className="text-lg font-['Outfit'] text-white">Performance Breakdown</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={250}>
                <PieChart>
                  <Pie
                    data={pieData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={100}
                    paddingAngle={2}
                    dataKey="value"
                  >
                    {pieData.map((entry, index) => (
                      <Cell key={index} fill={entry.color} />
                    ))}
                  </Pie>
                  <Legend 
                    verticalAlign="bottom" 
                    formatter={(value) => <span className="text-slate-300">{value}</span>}
                  />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Subject-wise Performance */}
          <Card className="bg-slate-900/50 border-slate-800">
            <CardHeader>
              <CardTitle className="text-lg font-['Outfit'] text-white">Subject-wise Performance</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {Object.entries(result.subject_wise || {}).map(([subject, data]) => {
                const accuracy = data.total > 0 ? Math.round((data.correct / data.total) * 100) : 0;
                return (
                  <div key={subject}>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-slate-300">{subject}</span>
                      <span className="text-sm text-slate-400">
                        {data.correct}/{data.total} ({accuracy}%)
                      </span>
                    </div>
                    <Progress value={accuracy} className="h-2" />
                  </div>
                );
              })}
              {Object.keys(result.subject_wise || {}).length === 0 && (
                <p className="text-center text-slate-500">No subject-wise data available</p>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Paper Info */}
        <Card className="bg-slate-900/50 border-slate-800 mt-6">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-medium text-white">{result.paper_title}</h3>
                <p className="text-sm text-slate-400">{result.exam_type} • {result.subject}</p>
              </div>
              <p className="text-sm text-slate-500">
                {new Date(result.created_at).toLocaleDateString()}
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default ResultPage;
