import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { 
  TrendingUp, 
  Target, 
  Award, 
  BarChart3,
  CheckCircle,
  XCircle,
  Clock,
  Loader2
} from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';
import axios from 'axios';
import { API } from '@/App';
import { toast } from 'sonner';

const ProgressSection = () => {
  const [progress, setProgress] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchProgress();
  }, []);

  const fetchProgress = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API}/progress`, {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
        withCredentials: true
      });
      setProgress(response.data);
    } catch (error) {
      toast.error('Failed to fetch progress');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
      </div>
    );
  }

  if (!progress || progress.total_tests === 0) {
    return (
      <div data-testid="progress-section">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white font-['Outfit'] mb-2">Your Progress</h1>
          <p className="text-slate-400">Track your improvement over time</p>
        </div>
        
        <div className="text-center py-20">
          <BarChart3 className="w-16 h-16 text-slate-600 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-white mb-2">No tests taken yet</h3>
          <p className="text-slate-400">Start taking tests to see your progress</p>
        </div>
      </div>
    );
  }

  const subjectData = Object.entries(progress.subject_performance || {}).map(([subject, data]) => ({
    subject,
    accuracy: data.accuracy,
    total: data.total,
    correct: data.correct
  }));

  const trendData = progress.improvement_trend?.map((item, index) => ({
    test: `Test ${index + 1}`,
    score: item.score,
    accuracy: item.accuracy
  })) || [];

  return (
    <div data-testid="progress-section">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white font-['Outfit'] mb-2">Your Progress</h1>
        <p className="text-slate-400">Track your improvement over time</p>
      </div>

      {/* Stats Cards */}
      <div className="grid md:grid-cols-4 gap-4 mb-8">
        <Card className="bg-slate-900/50 border-slate-800">
          <CardContent className="p-6">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-xl bg-blue-500/20 flex items-center justify-center">
                <Target className="w-6 h-6 text-blue-400" />
              </div>
              <div>
                <p className="text-sm text-slate-400">Tests Taken</p>
                <p className="text-2xl font-bold text-white">{progress.total_tests}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-slate-900/50 border-slate-800">
          <CardContent className="p-6">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-xl bg-emerald-500/20 flex items-center justify-center">
                <Award className="w-6 h-6 text-emerald-400" />
              </div>
              <div>
                <p className="text-sm text-slate-400">Avg Score</p>
                <p className="text-2xl font-bold text-white">{progress.average_score}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-slate-900/50 border-slate-800">
          <CardContent className="p-6">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-xl bg-amber-500/20 flex items-center justify-center">
                <TrendingUp className="w-6 h-6 text-amber-400" />
              </div>
              <div>
                <p className="text-sm text-slate-400">Avg Accuracy</p>
                <p className="text-2xl font-bold text-white">{progress.average_accuracy}%</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-slate-900/50 border-slate-800">
          <CardContent className="p-6">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-xl bg-purple-500/20 flex items-center justify-center">
                <BarChart3 className="w-6 h-6 text-purple-400" />
              </div>
              <div>
                <p className="text-sm text-slate-400">Best Subject</p>
                <p className="text-2xl font-bold text-white">
                  {subjectData.length > 0 
                    ? subjectData.reduce((a, b) => a.accuracy > b.accuracy ? a : b).subject?.substring(0, 4)
                    : 'N/A'
                  }
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid lg:grid-cols-2 gap-6 mb-8">
        {/* Progress Trend Chart */}
        <Card className="bg-slate-900/50 border-slate-800">
          <CardHeader>
            <CardTitle className="text-lg font-['Outfit'] text-white">Score Trend</CardTitle>
          </CardHeader>
          <CardContent>
            {trendData.length > 0 ? (
              <ResponsiveContainer width="100%" height={250}>
                <LineChart data={trendData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                  <XAxis dataKey="test" stroke="#64748b" fontSize={12} />
                  <YAxis stroke="#64748b" fontSize={12} />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: '#0f172a', 
                      border: '1px solid #1e293b',
                      borderRadius: '8px'
                    }} 
                  />
                  <Line 
                    type="monotone" 
                    dataKey="score" 
                    stroke="#3b82f6" 
                    strokeWidth={2}
                    dot={{ fill: '#3b82f6' }}
                  />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-[250px] flex items-center justify-center text-slate-500">
                No trend data available
              </div>
            )}
          </CardContent>
        </Card>

        {/* Subject Performance */}
        <Card className="bg-slate-900/50 border-slate-800">
          <CardHeader>
            <CardTitle className="text-lg font-['Outfit'] text-white">Subject Performance</CardTitle>
          </CardHeader>
          <CardContent>
            {subjectData.length > 0 ? (
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={subjectData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                  <XAxis dataKey="subject" stroke="#64748b" fontSize={12} />
                  <YAxis stroke="#64748b" fontSize={12} />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: '#0f172a', 
                      border: '1px solid #1e293b',
                      borderRadius: '8px'
                    }} 
                  />
                  <Bar dataKey="accuracy" fill="#10b981" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-[250px] flex items-center justify-center text-slate-500">
                No subject data available
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Recent Results */}
      <Card className="bg-slate-900/50 border-slate-800">
        <CardHeader>
          <CardTitle className="text-lg font-['Outfit'] text-white">Recent Results</CardTitle>
        </CardHeader>
        <CardContent>
          {progress.recent_results?.length > 0 ? (
            <div className="space-y-3">
              {progress.recent_results.slice(0, 5).map((result) => (
                <div
                  key={result.result_id}
                  className="flex items-center justify-between p-4 rounded-xl bg-slate-800/50"
                  data-testid={`result-${result.result_id}`}
                >
                  <div>
                    <h4 className="font-medium text-white">{result.paper_title}</h4>
                    <div className="flex items-center gap-4 mt-1 text-sm text-slate-400">
                      <span className="flex items-center gap-1">
                        <CheckCircle className="w-4 h-4 text-emerald-400" />
                        {result.correct_answers} correct
                      </span>
                      <span className="flex items-center gap-1">
                        <XCircle className="w-4 h-4 text-red-400" />
                        {result.wrong_answers} wrong
                      </span>
                      <span className="flex items-center gap-1">
                        <Clock className="w-4 h-4" />
                        {Math.round(result.time_taken / 60)} min
                      </span>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-2xl font-bold text-white">{result.score}</p>
                    <Badge className={`${result.accuracy >= 60 ? 'bg-emerald-500/20 text-emerald-400' : 'bg-amber-500/20 text-amber-400'}`}>
                      {result.accuracy}% Accuracy
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-slate-500">
              No results yet
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default ProgressSection;
