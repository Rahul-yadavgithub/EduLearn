import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Sparkles, 
  FileText, 
  Download, 
  RefreshCw, 
  Edit, 
  Eye,
  Loader2,
  CheckCircle,
  BookOpen,
  Brain,
  Upload,
  History,
  Send
} from 'lucide-react';
import axios from 'axios';
import { API } from '@/App';
import { toast } from 'sonner';

const PaperGeneratorSection = () => {
  const [generating, setGenerating] = useState(false);
  const [generationStep, setGenerationStep] = useState('');
  const [generatedQuestions, setGeneratedQuestions] = useState(null);
  const [showPreview, setShowPreview] = useState(false);
  const [editingQuestion, setEditingQuestion] = useState(null);
  const [generatedPapers, setGeneratedPapers] = useState([]);
  const [loadingHistory, setLoadingHistory] = useState(true);
  const [showPublishDialog, setShowPublishDialog] = useState(false);
  const [publishData, setPublishData] = useState({
    title: '',
    year: new Date().getFullYear().toString()
  });
  
  const [formData, setFormData] = useState({
    num_questions: 10,
    subject: '',
    difficulty: '',
    purpose: '',
    sub_type: '',
    class_level: '',
    language: 'English',
    reference_content: ''
  });

  const generationSteps = [
    'Analyzing syllabus...',
    'Reading reference material...',
    'Generating questions...',
    'Creating answer keys...',
    'Finalizing paper...'
  ];

  useEffect(() => {
    fetchGeneratedPapers();
  }, []);

  const fetchGeneratedPapers = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API}/generated-papers`, {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
        withCredentials: true
      });
      setGeneratedPapers(response.data);
    } catch (error) {
      console.error('Failed to fetch generated papers');
    } finally {
      setLoadingHistory(false);
    }
  };

  const handleGenerate = async () => {
    if (!formData.subject || !formData.difficulty || !formData.purpose) {
      toast.error('Please fill all required fields');
      return;
    }

    setGenerating(true);
    setGeneratedQuestions(null);

    // Simulate step progress
    for (let i = 0; i < generationSteps.length; i++) {
      setGenerationStep(generationSteps[i]);
      await new Promise(resolve => setTimeout(resolve, 1000));
    }

    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(`${API}/generate-paper`, formData, {
        headers: token ? { Authorization: `Bearer ${token}` } : {}
      });

      setGeneratedQuestions(response.data);
      toast.success('Paper generated successfully!');
      fetchGeneratedPapers(); // Refresh history
      
      // Auto-download PDF
      handleDownloadGenerated(response.data.gen_paper_id);
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to generate paper');
    } finally {
      setGenerating(false);
      setGenerationStep('');
    }
  };

  const handleSaveQuestion = (index, updatedQuestion) => {
    setGeneratedQuestions(prev => ({
      ...prev,
      questions: prev.questions.map((q, i) => i === index ? updatedQuestion : q)
    }));
    setEditingQuestion(null);
    toast.success('Question updated');
  };

  const handleDownload = (format) => {
    const content = generatedQuestions.questions.map((q, i) => 
      `Q${i + 1}. ${q.question_text}\n` +
      `A) ${q.options.A}\n` +
      `B) ${q.options.B}\n` +
      `C) ${q.options.C}\n` +
      `D) ${q.options.D}\n` +
      `Answer: ${q.correct_answer}\n\n`
    ).join('');

    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `question_paper.${format === 'PDF' ? 'txt' : 'txt'}`;
    a.click();
    URL.revokeObjectURL(url);
    toast.success(`Downloaded as ${format}`);
  };

  const handleDownloadGenerated = async (genPaperId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API}/generated-papers/${genPaperId}/download`, {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
        withCredentials: true,
        responseType: 'blob'
      });
      
      const url = URL.createObjectURL(response.data);
      const a = document.createElement('a');
      a.href = url;
      a.download = `generated_paper_${genPaperId}.pdf`;
      a.click();
      URL.revokeObjectURL(url);
      toast.success('PDF downloaded successfully!');
    } catch (error) {
      toast.error('Failed to download PDF');
    }
  };

  const handlePublish = async () => {
    if (!publishData.title) {
      toast.error('Please enter a title for the paper');
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(`${API}/generated-papers/${generatedQuestions.gen_paper_id}/publish`, {
        title: publishData.title,
        subject: generatedQuestions.metadata.subject,
        exam_type: generatedQuestions.metadata.exam_type,
        sub_type: formData.sub_type,
        class_level: formData.class_level,
        year: publishData.year,
        questions: generatedQuestions.questions,
        language: generatedQuestions.metadata.language
      }, {
        headers: token ? { Authorization: `Bearer ${token}` } : {}
      });

      toast.success('Paper published for students!');
      setShowPublishDialog(false);
      fetchGeneratedPapers();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to publish paper');
    }
  };

  const loadHistoryPaper = async (genPaperId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API}/generated-papers/${genPaperId}`, {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
        withCredentials: true
      });
      
      setGeneratedQuestions({
        gen_paper_id: response.data.gen_paper_id,
        questions: response.data.questions,
        metadata: {
          num_questions: response.data.num_questions,
          subject: response.data.subject,
          difficulty: response.data.difficulty,
          exam_type: response.data.exam_type,
          language: response.data.language
        }
      });
      
      setFormData(prev => ({
        ...prev,
        subject: response.data.subject,
        difficulty: response.data.difficulty,
        purpose: response.data.exam_type,
        sub_type: response.data.sub_type || '',
        class_level: response.data.class_level || '',
        language: response.data.language
      }));
      
      toast.success('Paper loaded from history');
    } catch (error) {
      toast.error('Failed to load paper');
    }
  };

  return (
    <div data-testid="paper-generator-section">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white font-['Outfit'] mb-2">
          <span className="gradient-text-teacher">AI</span> Question Paper Generator
        </h1>
        <p className="text-slate-400">Generate exam-quality question papers with AI</p>
      </div>

      <Tabs defaultValue="generate" className="w-full">
        <TabsList className="bg-slate-900 border border-slate-800 mb-6">
          <TabsTrigger value="generate" className="data-[state=active]:bg-emerald-500/20">
            <Sparkles className="w-4 h-4 mr-2" />
            Generate New
          </TabsTrigger>
          <TabsTrigger value="history" className="data-[state=active]:bg-emerald-500/20">
            <History className="w-4 h-4 mr-2" />
            History ({generatedPapers.length})
          </TabsTrigger>
        </TabsList>

        <TabsContent value="generate">
          <div className="grid lg:grid-cols-2 gap-8">
            {/* Configuration Form */}
            <Card className="bg-slate-900/50 border-slate-800">
              <CardHeader>
                <CardTitle className="text-lg font-['Outfit'] text-white flex items-center gap-2">
                  <Sparkles className="w-5 h-5 text-emerald-400" />
                  Configuration
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Number of Questions */}
                <div className="space-y-2">
                  <Label className="text-slate-300">Number of Questions</Label>
                  <Input
                    type="number"
                    min={5}
                    max={50}
                    value={formData.num_questions}
                    onChange={(e) => setFormData({ ...formData, num_questions: parseInt(e.target.value) || 10 })}
                    className="bg-slate-900 border-slate-700 text-white"
                    data-testid="num-questions"
                  />
                </div>

                {/* Subject */}
                <div className="space-y-2">
                  <Label className="text-slate-300">Subject *</Label>
                  <Select
                    value={formData.subject}
                    onValueChange={(value) => setFormData({ ...formData, subject: value })}
                  >
                    <SelectTrigger className="bg-slate-900 border-slate-700 text-white" data-testid="gen-subject">
                      <SelectValue placeholder="Select Subject" />
                    </SelectTrigger>
                    <SelectContent className="bg-slate-900 border-slate-700">
                      <SelectItem value="Physics">Physics</SelectItem>
                      <SelectItem value="Chemistry">Chemistry</SelectItem>
                      <SelectItem value="Mathematics">Mathematics</SelectItem>
                      <SelectItem value="Biology">Biology</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                {/* Difficulty */}
                <div className="space-y-2">
                  <Label className="text-slate-300">Difficulty Level *</Label>
                  <Select
                    value={formData.difficulty}
                    onValueChange={(value) => setFormData({ ...formData, difficulty: value })}
                  >
                    <SelectTrigger className="bg-slate-900 border-slate-700 text-white" data-testid="gen-difficulty">
                      <SelectValue placeholder="Select Difficulty" />
                    </SelectTrigger>
                    <SelectContent className="bg-slate-900 border-slate-700">
                      <SelectItem value="Easy">Easy</SelectItem>
                      <SelectItem value="Medium">Medium</SelectItem>
                      <SelectItem value="Hard">Hard</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                {/* Purpose */}
                <div className="space-y-2">
                  <Label className="text-slate-300">Purpose *</Label>
                  <Select
                    value={formData.purpose}
                    onValueChange={(value) => setFormData({ ...formData, purpose: value, sub_type: '', class_level: '' })}
                  >
                    <SelectTrigger className="bg-slate-900 border-slate-700 text-white" data-testid="gen-purpose">
                      <SelectValue placeholder="Select Purpose" />
                    </SelectTrigger>
                    <SelectContent className="bg-slate-900 border-slate-700">
                      <SelectItem value="JEE">JEE</SelectItem>
                      <SelectItem value="NEET">NEET</SelectItem>
                      <SelectItem value="School">School</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                {/* Conditional: JEE Sub-type */}
                {formData.purpose === 'JEE' && (
                  <div className="space-y-2">
                    <Label className="text-slate-300">Exam Type</Label>
                    <Select
                      value={formData.sub_type}
                      onValueChange={(value) => setFormData({ ...formData, sub_type: value })}
                    >
                      <SelectTrigger className="bg-slate-900 border-slate-700 text-white" data-testid="gen-subtype">
                        <SelectValue placeholder="Select Exam Type" />
                      </SelectTrigger>
                      <SelectContent className="bg-slate-900 border-slate-700">
                        <SelectItem value="JEE Mains">JEE Mains</SelectItem>
                        <SelectItem value="JEE Advanced">JEE Advanced</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                )}

                {/* Conditional: School Class */}
                {formData.purpose === 'School' && (
                  <div className="space-y-2">
                    <Label className="text-slate-300">Class</Label>
                    <Select
                      value={formData.class_level}
                      onValueChange={(value) => setFormData({ ...formData, class_level: value })}
                    >
                      <SelectTrigger className="bg-slate-900 border-slate-700 text-white" data-testid="gen-class">
                        <SelectValue placeholder="Select Class" />
                      </SelectTrigger>
                      <SelectContent className="bg-slate-900 border-slate-700">
                        {[...Array(8)].map((_, i) => (
                          <SelectItem key={i + 5} value={String(i + 5)}>Class {i + 5}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                )}

                {/* Language */}
                <div className="space-y-2">
                  <Label className="text-slate-300">Language</Label>
                  <Select
                    value={formData.language}
                    onValueChange={(value) => setFormData({ ...formData, language: value })}
                  >
                    <SelectTrigger className="bg-slate-900 border-slate-700 text-white" data-testid="gen-language">
                      <SelectValue placeholder="Select Language" />
                    </SelectTrigger>
                    <SelectContent className="bg-slate-900 border-slate-700">
                      <SelectItem value="English">English</SelectItem>
                      <SelectItem value="Hindi">Hindi</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                {/* Reference Content */}
                <div className="space-y-2">
                  <Label className="text-slate-300">Reference Content (Optional)</Label>
                  <Textarea
                    placeholder="Paste reference material, topics, or specific content to base questions on..."
                    className="min-h-[100px] bg-slate-900 border-slate-700 text-white placeholder:text-slate-500"
                    value={formData.reference_content}
                    onChange={(e) => setFormData({ ...formData, reference_content: e.target.value })}
                    data-testid="gen-reference"
                  />
                </div>

                {/* Generate Button */}
                <Button
                  onClick={handleGenerate}
                  disabled={generating}
                  className="w-full bg-emerald-600 hover:bg-emerald-700"
                  data-testid="generate-btn"
                >
                  {generating ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Generating...
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-4 h-4 mr-2" />
                      Generate Paper
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>

            {/* Generation Status / Preview */}
            <div className="space-y-6">
              {/* Generation Progress */}
              {generating && (
                <Card className="bg-slate-900/50 border-slate-800 overflow-hidden">
                  <div className="relative">
                    <div className="absolute inset-0 opacity-20">
                      <div className="w-full h-full bg-gradient-to-br from-emerald-500/20 to-blue-500/20"></div>
                    </div>
                    <CardContent className="relative p-8 text-center">
                      <Brain className="w-16 h-16 text-emerald-400 mx-auto mb-4 animate-pulse" />
                      <h3 className="text-xl font-semibold text-white mb-2">Generating Questions</h3>
                      <p className="text-emerald-400 text-lg animate-pulse" data-testid="generation-step">
                        {generationStep}
                      </p>
                      <div className="mt-6 flex justify-center gap-2">
                        {generationSteps.map((step, i) => (
                          <div
                            key={i}
                            className={`w-2 h-2 rounded-full ${
                              generationSteps.indexOf(generationStep) >= i
                                ? 'bg-emerald-500'
                                : 'bg-slate-700'
                            }`}
                          />
                        ))}
                      </div>
                    </CardContent>
                  </div>
                </Card>
              )}

              {/* Generated Questions Preview */}
              {generatedQuestions && !generating && (
                <Card className="bg-slate-900/50 border-slate-800">
                  <CardHeader className="flex flex-row items-center justify-between">
                    <CardTitle className="text-lg font-['Outfit'] text-white flex items-center gap-2">
                      <CheckCircle className="w-5 h-5 text-emerald-400" />
                      Paper Generated
                    </CardTitle>
                    <div className="flex gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setShowPreview(true)}
                        className="border-slate-700 text-slate-300"
                        data-testid="preview-btn"
                      >
                        <Eye className="w-4 h-4 mr-2" />
                        Preview
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={handleGenerate}
                        className="border-slate-700 text-slate-300"
                        data-testid="regenerate-btn"
                      >
                        <RefreshCw className="w-4 h-4 mr-2" />
                        Regenerate
                      </Button>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-center gap-4 mb-4 text-sm text-slate-400">
                      <Badge className="bg-emerald-500/20 text-emerald-400">
                        {generatedQuestions.metadata?.num_questions} Questions
                      </Badge>
                      <Badge className="bg-slate-800 text-slate-300">
                        {generatedQuestions.metadata?.subject}
                      </Badge>
                      <Badge className="bg-slate-800 text-slate-300">
                        {generatedQuestions.metadata?.difficulty}
                      </Badge>
                    </div>

                    {/* Question List */}
                    <div className="space-y-3 max-h-[300px] overflow-y-auto">
                      {generatedQuestions.questions?.slice(0, 5).map((q, index) => (
                        <div
                          key={index}
                          className="p-4 rounded-lg bg-slate-800/50 border border-slate-700"
                          data-testid={`generated-q-${index}`}
                        >
                          <div className="flex items-start justify-between gap-2">
                            <p className="text-sm text-slate-300 line-clamp-2">
                              <span className="font-medium text-white">Q{index + 1}.</span> {q.question_text}
                            </p>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => setEditingQuestion({ index, question: q })}
                              className="shrink-0 text-slate-400 hover:text-white"
                            >
                              <Edit className="w-4 h-4" />
                            </Button>
                          </div>
                          <p className="text-xs text-emerald-400 mt-2">Answer: {q.correct_answer}</p>
                        </div>
                      ))}
                      {generatedQuestions.questions?.length > 5 && (
                        <p className="text-center text-slate-500 text-sm">
                          + {generatedQuestions.questions.length - 5} more questions
                        </p>
                      )}
                    </div>

                    {/* Action Buttons */}
                    <div className="flex gap-3 mt-6">
                      <Button
                        onClick={() => handleDownloadGenerated(generatedQuestions.gen_paper_id)}
                        className="flex-1 bg-emerald-600 hover:bg-emerald-700"
                        data-testid="download-pdf-btn"
                      >
                        <Download className="w-4 h-4 mr-2" />
                        Download PDF
                      </Button>
                      <Button
                        onClick={() => {
                          setPublishData({
                            title: `${generatedQuestions.metadata?.subject} - ${generatedQuestions.metadata?.exam_type}`,
                            year: new Date().getFullYear().toString()
                          });
                          setShowPublishDialog(true);
                        }}
                        className="flex-1 bg-blue-600 hover:bg-blue-700"
                        data-testid="publish-btn"
                      >
                        <Send className="w-4 h-4 mr-2" />
                        Publish for Students
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Empty State */}
              {!generating && !generatedQuestions && (
                <Card className="bg-slate-900/50 border-slate-800">
                  <CardContent className="p-12 text-center">
                    <FileText className="w-16 h-16 text-slate-600 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-white mb-2">No Paper Generated Yet</h3>
                    <p className="text-slate-400">
                      Configure the options and click Generate to create a question paper
                    </p>
                  </CardContent>
                </Card>
              )}
            </div>
          </div>
        </TabsContent>

        <TabsContent value="history">
          <Card className="bg-slate-900/50 border-slate-800">
            <CardHeader>
              <CardTitle className="text-lg font-['Outfit'] text-white flex items-center gap-2">
                <History className="w-5 h-5 text-emerald-400" />
                Previously Generated Papers
              </CardTitle>
            </CardHeader>
            <CardContent>
              {loadingHistory ? (
                <div className="flex items-center justify-center py-12">
                  <Loader2 className="w-8 h-8 animate-spin text-emerald-500" />
                </div>
              ) : generatedPapers.length === 0 ? (
                <div className="text-center py-12">
                  <FileText className="w-12 h-12 text-slate-600 mx-auto mb-4" />
                  <p className="text-slate-400">No papers generated yet</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {generatedPapers.map((paper) => (
                    <div
                      key={paper.gen_paper_id}
                      className="flex items-center justify-between p-4 rounded-xl bg-slate-800/50 border border-slate-700"
                      data-testid={`history-paper-${paper.gen_paper_id}`}
                    >
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <h4 className="font-medium text-white">
                            {paper.subject} - {paper.exam_type}
                          </h4>
                          {paper.is_published && (
                            <Badge className="bg-blue-500/20 text-blue-400">Published</Badge>
                          )}
                        </div>
                        <div className="flex items-center gap-4 text-sm text-slate-400">
                          <span>{paper.num_questions} Questions</span>
                          <span>{paper.difficulty}</span>
                          <span>{new Date(paper.created_at).toLocaleDateString()}</span>
                        </div>
                      </div>
                      <div className="flex gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => loadHistoryPaper(paper.gen_paper_id)}
                          className="border-slate-700 text-slate-300"
                        >
                          <Eye className="w-4 h-4 mr-2" />
                          Load
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleDownloadGenerated(paper.gen_paper_id)}
                          className="border-slate-700 text-slate-300"
                        >
                          <Download className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Edit Question Dialog */}
      <Dialog open={!!editingQuestion} onOpenChange={() => setEditingQuestion(null)}>
        <DialogContent className="bg-slate-900 border-slate-800 max-w-2xl">
          <DialogHeader>
            <DialogTitle className="text-white">Edit Question {editingQuestion?.index + 1}</DialogTitle>
          </DialogHeader>
          {editingQuestion && (
            <EditQuestionForm
              question={editingQuestion.question}
              onSave={(q) => handleSaveQuestion(editingQuestion.index, q)}
              onCancel={() => setEditingQuestion(null)}
            />
          )}
        </DialogContent>
      </Dialog>

      {/* Full Preview Dialog */}
      <Dialog open={showPreview} onOpenChange={setShowPreview}>
        <DialogContent className="bg-slate-900 border-slate-800 max-w-4xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="text-white">Paper Preview</DialogTitle>
          </DialogHeader>
          {generatedQuestions && (
            <div className="space-y-6 py-4">
              {generatedQuestions.questions?.map((q, index) => (
                <div key={index} className="p-4 bg-slate-800/50 rounded-lg">
                  <p className="text-white mb-4">
                    <span className="font-bold">Q{index + 1}.</span> {q.question_text}
                  </p>
                  <div className="grid grid-cols-2 gap-2">
                    {Object.entries(q.options).map(([key, value]) => (
                      <p key={key} className={`text-sm ${key === q.correct_answer ? 'text-emerald-400' : 'text-slate-400'}`}>
                        {key}) {value}
                      </p>
                    ))}
                  </div>
                  {q.explanation && (
                    <p className="text-xs text-slate-500 mt-3 pt-3 border-t border-slate-700">
                      <span className="text-emerald-400">Explanation:</span> {q.explanation}
                    </p>
                  )}
                </div>
              ))}
            </div>
          )}
        </DialogContent>
      </Dialog>

      {/* Publish Dialog */}
      <Dialog open={showPublishDialog} onOpenChange={setShowPublishDialog}>
        <DialogContent className="bg-slate-900 border-slate-800">
          <DialogHeader>
            <DialogTitle className="text-white">Publish Paper for Students</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label className="text-slate-300">Paper Title *</Label>
              <Input
                value={publishData.title}
                onChange={(e) => setPublishData({ ...publishData, title: e.target.value })}
                placeholder="Enter paper title"
                className="bg-slate-900 border-slate-700 text-white"
              />
            </div>
            <div className="space-y-2">
              <Label className="text-slate-300">Year</Label>
              <Input
                value={publishData.year}
                onChange={(e) => setPublishData({ ...publishData, year: e.target.value })}
                placeholder="e.g., 2024"
                className="bg-slate-900 border-slate-700 text-white"
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowPublishDialog(false)} className="border-slate-700 text-slate-300">
              Cancel
            </Button>
            <Button onClick={handlePublish} className="bg-blue-600 hover:bg-blue-700">
              <Send className="w-4 h-4 mr-2" />
              Publish
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

const EditQuestionForm = ({ question, onSave, onCancel }) => {
  const [editedQuestion, setEditedQuestion] = useState({ ...question });

  return (
    <div className="space-y-4">
      <div className="space-y-2">
        <Label className="text-slate-300">Question Text</Label>
        <Textarea
          value={editedQuestion.question_text}
          onChange={(e) => setEditedQuestion({ ...editedQuestion, question_text: e.target.value })}
          className="bg-slate-900 border-slate-700 text-white"
        />
      </div>
      
      {Object.entries(editedQuestion.options).map(([key, value]) => (
        <div key={key} className="space-y-2">
          <Label className="text-slate-300">Option {key}</Label>
          <Input
            value={value}
            onChange={(e) => setEditedQuestion({
              ...editedQuestion,
              options: { ...editedQuestion.options, [key]: e.target.value }
            })}
            className="bg-slate-900 border-slate-700 text-white"
          />
        </div>
      ))}

      <div className="space-y-2">
        <Label className="text-slate-300">Correct Answer</Label>
        <Select
          value={editedQuestion.correct_answer}
          onValueChange={(value) => setEditedQuestion({ ...editedQuestion, correct_answer: value })}
        >
          <SelectTrigger className="bg-slate-900 border-slate-700 text-white">
            <SelectValue />
          </SelectTrigger>
          <SelectContent className="bg-slate-900 border-slate-700">
            <SelectItem value="A">A</SelectItem>
            <SelectItem value="B">B</SelectItem>
            <SelectItem value="C">C</SelectItem>
            <SelectItem value="D">D</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <DialogFooter>
        <Button variant="outline" onClick={onCancel} className="border-slate-700 text-slate-300">
          Cancel
        </Button>
        <Button onClick={() => onSave(editedQuestion)} className="bg-emerald-600 hover:bg-emerald-700">
          Save Changes
        </Button>
      </DialogFooter>
    </div>
  );
};

export default PaperGeneratorSection;
