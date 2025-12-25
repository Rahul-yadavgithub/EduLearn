import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { BookOpen, Search, Filter, Play, FileText, Calendar, Loader2 } from 'lucide-react';
import axios from 'axios';
import { API } from '@/App';
import { toast } from 'sonner';

const PapersSection = () => {
  const navigate = useNavigate();
  const [papers, setPapers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState({
    subject: '',
    exam_type: '',
    year: ''
  });

  useEffect(() => {
    fetchPapers();
  }, [filters]);

  const fetchPapers = async () => {
    try {
      const params = new URLSearchParams();
      if (filters.subject) params.append('subject', filters.subject);
      if (filters.exam_type) params.append('exam_type', filters.exam_type);
      if (filters.year) params.append('year', filters.year);

      const token = localStorage.getItem('token');
      const response = await axios.get(`${API}/papers?${params.toString()}`, {
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

  const filteredPapers = papers.filter(paper => 
    paper.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    paper.subject.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const getExamTypeColor = (type) => {
    switch (type) {
      case 'JEE': return 'bg-blue-500/20 text-blue-400 border-blue-500/30';
      case 'NEET': return 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30';
      case 'School': return 'bg-amber-500/20 text-amber-400 border-amber-500/30';
      default: return 'bg-slate-500/20 text-slate-400 border-slate-500/30';
    }
  };

  const startExam = (paperId) => {
    navigate(`/exam/${paperId}`);
  };

  return (
    <div data-testid="papers-section">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white font-['Outfit'] mb-2">Question Papers</h1>
        <p className="text-slate-400">Browse and practice from our collection of papers</p>
      </div>

      {/* Filters */}
      <div className="flex flex-col lg:flex-row gap-4 mb-8">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500" />
          <Input
            placeholder="Search papers..."
            className="pl-10 bg-slate-900 border-slate-700 text-white"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            data-testid="search-papers"
          />
        </div>
        
        <div className="flex gap-3">
          <Select
            value={filters.subject}
            onValueChange={(value) => setFilters({ ...filters, subject: value === 'all' ? '' : value })}
          >
            <SelectTrigger className="w-40 bg-slate-900 border-slate-700 text-white" data-testid="filter-subject">
              <SelectValue placeholder="Subject" />
            </SelectTrigger>
            <SelectContent className="bg-slate-900 border-slate-700">
              <SelectItem value="all">All Subjects</SelectItem>
              <SelectItem value="Physics">Physics</SelectItem>
              <SelectItem value="Chemistry">Chemistry</SelectItem>
              <SelectItem value="Mathematics">Mathematics</SelectItem>
              <SelectItem value="Biology">Biology</SelectItem>
            </SelectContent>
          </Select>

          <Select
            value={filters.exam_type}
            onValueChange={(value) => setFilters({ ...filters, exam_type: value === 'all' ? '' : value })}
          >
            <SelectTrigger className="w-40 bg-slate-900 border-slate-700 text-white" data-testid="filter-exam-type">
              <SelectValue placeholder="Exam Type" />
            </SelectTrigger>
            <SelectContent className="bg-slate-900 border-slate-700">
              <SelectItem value="all">All Types</SelectItem>
              <SelectItem value="JEE">JEE</SelectItem>
              <SelectItem value="NEET">NEET</SelectItem>
              <SelectItem value="School">School</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Papers Grid */}
      {loading ? (
        <div className="flex items-center justify-center py-20">
          <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
        </div>
      ) : filteredPapers.length === 0 ? (
        <div className="text-center py-20">
          <FileText className="w-16 h-16 text-slate-600 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-white mb-2">No papers found</h3>
          <p className="text-slate-400">Try adjusting your filters or search query</p>
        </div>
      ) : (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredPapers.map((paper) => (
            <Card 
              key={paper.paper_id} 
              className="bg-slate-900/50 border-slate-800 hover-lift"
              data-testid={`paper-card-${paper.paper_id}`}
            >
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between gap-2">
                  <CardTitle className="text-lg font-['Outfit'] text-white line-clamp-2">
                    {paper.title}
                  </CardTitle>
                  <Badge className={`shrink-0 ${getExamTypeColor(paper.exam_type)}`}>
                    {paper.exam_type}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex items-center gap-4 text-sm text-slate-400">
                    <div className="flex items-center gap-1">
                      <BookOpen className="w-4 h-4" />
                      {paper.subject}
                    </div>
                    {paper.year && (
                      <div className="flex items-center gap-1">
                        <Calendar className="w-4 h-4" />
                        {paper.year}
                      </div>
                    )}
                  </div>
                  
                  <div className="flex items-center gap-2 text-sm text-slate-500">
                    <FileText className="w-4 h-4" />
                    {paper.questions?.length || 0} Questions
                  </div>

                  {paper.sub_type && (
                    <Badge variant="outline" className="text-xs border-slate-700 text-slate-400">
                      {paper.sub_type}
                    </Badge>
                  )}
                  
                  {paper.class_level && (
                    <Badge variant="outline" className="text-xs border-slate-700 text-slate-400">
                      Class {paper.class_level}
                    </Badge>
                  )}

                  <Button 
                    className="w-full mt-4 bg-blue-600 hover:bg-blue-700"
                    onClick={() => startExam(paper.paper_id)}
                    data-testid={`start-exam-${paper.paper_id}`}
                  >
                    <Play className="w-4 h-4 mr-2" />
                    Start Practice
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};

export default PapersSection;
