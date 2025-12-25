import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  BookOpen, 
  FlaskConical, 
  School, 
  Play, 
  FileText, 
  Calendar,
  Clock,
  ChevronRight,
  Loader2
} from 'lucide-react';
import axios from 'axios';
import { API } from '@/App';
import { toast } from 'sonner';

const TestsSection = () => {
  const navigate = useNavigate();
  const [papers, setPapers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState('JEE');

  useEffect(() => {
    fetchPapers();
  }, [selectedCategory]);

  const fetchPapers = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API}/papers?exam_type=${selectedCategory}`, {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
        withCredentials: true
      });
      setPapers(response.data);
    } catch (error) {
      toast.error('Failed to fetch papers');
    } finally {
      setLoading(false);
    }
  };

  const startExam = (paperId) => {
    navigate(`/exam/${paperId}`);
  };

  const categories = [
    { 
      id: 'JEE', 
      label: 'Engineering', 
      icon: <BookOpen className="w-5 h-5" />,
      description: 'JEE Mains & Advanced'
    },
    { 
      id: 'NEET', 
      label: 'Medical', 
      icon: <FlaskConical className="w-5 h-5" />,
      description: 'NEET Preparation'
    },
    { 
      id: 'School', 
      label: 'School', 
      icon: <School className="w-5 h-5" />,
      description: 'Board Exams'
    },
  ];

  return (
    <div data-testid="tests-section">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white font-['Outfit'] mb-2">Practice Tests</h1>
        <p className="text-slate-400">Take mock tests to prepare for your exams</p>
      </div>

      {/* Category Cards */}
      <div className="grid md:grid-cols-3 gap-4 mb-8">
        {categories.map((cat) => (
          <button
            key={cat.id}
            onClick={() => setSelectedCategory(cat.id)}
            className={`p-6 rounded-xl border text-left transition-all ${
              selectedCategory === cat.id
                ? cat.id === 'JEE' 
                  ? 'bg-blue-500/10 border-blue-500/50' 
                  : cat.id === 'NEET'
                    ? 'bg-emerald-500/10 border-emerald-500/50'
                    : 'bg-amber-500/10 border-amber-500/50'
                : 'bg-slate-900/50 border-slate-800 hover:border-slate-700'
            }`}
            data-testid={`category-${cat.id.toLowerCase()}`}
          >
            <div className={`w-12 h-12 rounded-xl flex items-center justify-center mb-4 ${
              cat.id === 'JEE' 
                ? 'bg-blue-500/20 text-blue-400' 
                : cat.id === 'NEET'
                  ? 'bg-emerald-500/20 text-emerald-400'
                  : 'bg-amber-500/20 text-amber-400'
            }`}>
              {cat.icon}
            </div>
            <h3 className="text-lg font-semibold text-white mb-1">{cat.label}</h3>
            <p className="text-sm text-slate-400">{cat.description}</p>
          </button>
        ))}
      </div>

      {/* Papers List */}
      <Card className="bg-slate-900/50 border-slate-800">
        <CardHeader>
          <CardTitle className="text-lg font-['Outfit'] text-white">
            {selectedCategory} Papers
          </CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
            </div>
          ) : papers.length === 0 ? (
            <div className="text-center py-12">
              <FileText className="w-12 h-12 text-slate-600 mx-auto mb-4" />
              <p className="text-slate-400">No papers available for this category</p>
            </div>
          ) : (
            <div className="space-y-3">
              {papers.map((paper) => (
                <div
                  key={paper.paper_id}
                  className="flex items-center justify-between p-4 rounded-xl bg-slate-800/50 border border-slate-700/50 hover:border-slate-600 transition-all"
                  data-testid={`test-card-${paper.paper_id}`}
                >
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h4 className="font-medium text-white">{paper.title}</h4>
                      {paper.sub_type && (
                        <Badge variant="outline" className="text-xs border-slate-700 text-slate-400">
                          {paper.sub_type}
                        </Badge>
                      )}
                    </div>
                    <div className="flex items-center gap-4 text-sm text-slate-400">
                      <span className="flex items-center gap-1">
                        <BookOpen className="w-4 h-4" />
                        {paper.subject}
                      </span>
                      <span className="flex items-center gap-1">
                        <FileText className="w-4 h-4" />
                        {paper.questions?.length || 0} Questions
                      </span>
                      {paper.year && (
                        <span className="flex items-center gap-1">
                          <Calendar className="w-4 h-4" />
                          {paper.year}
                        </span>
                      )}
                    </div>
                  </div>
                  <Button 
                    className="bg-blue-600 hover:bg-blue-700"
                    onClick={() => startExam(paper.paper_id)}
                    data-testid={`start-test-${paper.paper_id}`}
                  >
                    <Play className="w-4 h-4 mr-2" />
                    Start
                  </Button>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default TestsSection;
