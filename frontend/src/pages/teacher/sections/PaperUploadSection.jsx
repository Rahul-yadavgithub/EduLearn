import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { 
  Upload, 
  Plus, 
  Trash2, 
  FileText,
  Loader2,
  CheckCircle
} from 'lucide-react';
import axios from 'axios';
import { API } from '@/App';
import { toast } from 'sonner';

const PaperUploadSection = () => {
  const [uploading, setUploading] = useState(false);
  const [formData, setFormData] = useState({
    title: '',
    subject: '',
    exam_type: '',
    sub_type: '',
    class_level: '',
    year: new Date().getFullYear().toString(),
    language: 'English',
    questions: [createEmptyQuestion()]
  });

  function createEmptyQuestion() {
    return {
      question_id: `q_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      question_text: '',
      options: { A: '', B: '', C: '', D: '' },
      correct_answer: 'A',
      explanation: '',
      difficulty: 'Medium'
    };
  }

  const addQuestion = () => {
    setFormData(prev => ({
      ...prev,
      questions: [...prev.questions, createEmptyQuestion()]
    }));
  };

  const removeQuestion = (index) => {
    if (formData.questions.length <= 1) {
      toast.error('At least one question is required');
      return;
    }
    setFormData(prev => ({
      ...prev,
      questions: prev.questions.filter((_, i) => i !== index)
    }));
  };

  const updateQuestion = (index, field, value) => {
    setFormData(prev => ({
      ...prev,
      questions: prev.questions.map((q, i) => {
        if (i !== index) return q;
        if (field.startsWith('option_')) {
          const optionKey = field.split('_')[1];
          return { ...q, options: { ...q.options, [optionKey]: value } };
        }
        return { ...q, [field]: value };
      })
    }));
  };

    const handleSubmit = async () => {
      // ----------------------------
      // VALIDATION
      // ----------------------------
      if (!formData.title || !formData.subject || !formData.exam_type) {
        toast.error('Please fill all required fields');
        return;
      }

      if (!Array.isArray(formData.questions)) {
        toast.error('Invalid questions format');
        return;
      }

      const emptyQuestions = formData.questions.filter(
        q =>
          !q.question_text ||
          !q.options?.A ||
          !q.options?.B ||
          !q.options?.C ||
          !q.options?.D
      );

      if (emptyQuestions.length > 0) {
        toast.error('Please complete all questions');
        return;
      }

      // ----------------------------
      // SUBMIT
      // ----------------------------
      setUploading(true);

      try {
        const token = localStorage.getItem('token');

        const response = await axios.post(
          `${API}/papers`,
          formData,
          {
            headers: token ? { Authorization: `Bearer ${token}` } : {},
          }
        );

        console.log('✅ Paper create response:', response?.data);

        toast.success(
          response?.data?.message || 'Paper published successfully!'
        );

        // ----------------------------
        // RESET FORM (SAFE)
        // ----------------------------
        setFormData({
          title: '',
          subject: '',
          exam_type: '',
          sub_type: '',
          class_level: '',
          year: new Date().getFullYear().toString(),
          language: 'English',
          questions: [createEmptyQuestion()],
        });

      } catch (error) {
        console.error('❌ Paper creation failed:', error);

        toast.error(
          error.response?.data?.detail ||
          error.message ||
          'Paper may be created, but response failed'
        );

      } finally {
        setUploading(false);
      }
    };


  return (
    <div data-testid="paper-upload-section">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white font-['Outfit'] mb-2">Upload Question Paper</h1>
        <p className="text-slate-400">Create and upload papers for students to practice</p>
      </div>

      {/* Paper Details Form */}
      <Card className="bg-slate-900/50 border-slate-800 mb-6">
        <CardHeader>
          <CardTitle className="text-lg font-['Outfit'] text-white flex items-center gap-2">
            <FileText className="w-5 h-5 text-emerald-400" />
            Paper Details
          </CardTitle>
        </CardHeader>
        <CardContent className="grid md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label className="text-slate-300">Paper Title *</Label>
            <Input
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              placeholder="e.g., JEE Mains 2024 Physics"
              className="bg-slate-900 border-slate-700 text-white"
              data-testid="paper-title"
            />
          </div>

          <div className="space-y-2">
            <Label className="text-slate-300">Subject *</Label>
            <Select
              value={formData.subject}
              onValueChange={(value) => setFormData({ ...formData, subject: value })}
            >
              <SelectTrigger className="bg-slate-900 border-slate-700 text-white" data-testid="upload-subject">
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

          <div className="space-y-2">
            <Label className="text-slate-300">Exam Type *</Label>
            <Select
              value={formData.exam_type}
              onValueChange={(value) => setFormData({ ...formData, exam_type: value, sub_type: '', class_level: '' })}
            >
              <SelectTrigger className="bg-slate-900 border-slate-700 text-white" data-testid="upload-exam-type">
                <SelectValue placeholder="Select Exam Type" />
              </SelectTrigger>
              <SelectContent className="bg-slate-900 border-slate-700">
                <SelectItem value="JEE">JEE</SelectItem>
                <SelectItem value="NEET">NEET</SelectItem>
                <SelectItem value="School">School</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {formData.exam_type === 'JEE' && (
            <div className="space-y-2">
              <Label className="text-slate-300">Sub Type</Label>
              <Select
                value={formData.sub_type}
                onValueChange={(value) => setFormData({ ...formData, sub_type: value })}
              >
                <SelectTrigger className="bg-slate-900 border-slate-700 text-white">
                  <SelectValue placeholder="Select Sub Type" />
                </SelectTrigger>
                <SelectContent className="bg-slate-900 border-slate-700">
                  <SelectItem value="JEE Mains">JEE Mains</SelectItem>
                  <SelectItem value="JEE Advanced">JEE Advanced</SelectItem>
                </SelectContent>
              </Select>
            </div>
          )}

          {formData.exam_type === 'School' && (
            <div className="space-y-2">
              <Label className="text-slate-300">Class</Label>
              <Select
                value={formData.class_level}
                onValueChange={(value) => setFormData({ ...formData, class_level: value })}
              >
                <SelectTrigger className="bg-slate-900 border-slate-700 text-white">
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

          <div className="space-y-2">
            <Label className="text-slate-300">Year</Label>
            <Input
              value={formData.year}
              onChange={(e) => setFormData({ ...formData, year: e.target.value })}
              placeholder="e.g., 2024"
              className="bg-slate-900 border-slate-700 text-white"
              data-testid="paper-year"
            />
          </div>

          <div className="space-y-2">
            <Label className="text-slate-300">Language</Label>
            <Select
              value={formData.language}
              onValueChange={(value) => setFormData({ ...formData, language: value })}
            >
              <SelectTrigger className="bg-slate-900 border-slate-700 text-white">
                <SelectValue placeholder="Select Language" />
              </SelectTrigger>
              <SelectContent className="bg-slate-900 border-slate-700">
                <SelectItem value="English">English</SelectItem>
                <SelectItem value="Hindi">Hindi</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Questions */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold text-white font-['Outfit']">
            Questions ({formData.questions.length})
          </h2>
          <Button
            onClick={addQuestion}
            variant="outline"
            className="border-emerald-500/50 text-emerald-400 hover:bg-emerald-500/10"
            data-testid="add-question-btn"
          >
            <Plus className="w-4 h-4 mr-2" />
            Add Question
          </Button>
        </div>

        {formData.questions.map((question, index) => (
          <Card key={question.question_id} className="bg-slate-900/50 border-slate-800">
            <CardHeader className="flex flex-row items-center justify-between py-3">
              <CardTitle className="text-base font-['Outfit'] text-white">
                Question {index + 1}
              </CardTitle>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => removeQuestion(index)}
                className="text-slate-400 hover:text-red-400 hover:bg-red-500/10"
                data-testid={`remove-q-${index}`}
              >
                <Trash2 className="w-4 h-4" />
              </Button>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label className="text-slate-300">Question Text *</Label>
                <Textarea
                  value={question.question_text}
                  onChange={(e) => updateQuestion(index, 'question_text', e.target.value)}
                  placeholder="Enter the question..."
                  className="bg-slate-900 border-slate-700 text-white"
                  data-testid={`q-text-${index}`}
                />
              </div>

              <div className="grid md:grid-cols-2 gap-4">
                {['A', 'B', 'C', 'D'].map((opt) => (
                  <div key={opt} className="space-y-2">
                    <Label className="text-slate-300">Option {opt} *</Label>
                    <Input
                      value={question.options[opt]}
                      onChange={(e) => updateQuestion(index, `option_${opt}`, e.target.value)}
                      placeholder={`Option ${opt}`}
                      className="bg-slate-900 border-slate-700 text-white"
                      data-testid={`q-${index}-opt-${opt}`}
                    />
                  </div>
                ))}
              </div>

              <div className="grid md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label className="text-slate-300">Correct Answer *</Label>
                  <Select
                    value={question.correct_answer}
                    onValueChange={(value) => updateQuestion(index, 'correct_answer', value)}
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

                <div className="space-y-2">
                  <Label className="text-slate-300">Difficulty</Label>
                  <Select
                    value={question.difficulty}
                    onValueChange={(value) => updateQuestion(index, 'difficulty', value)}
                  >
                    <SelectTrigger className="bg-slate-900 border-slate-700 text-white">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent className="bg-slate-900 border-slate-700">
                      <SelectItem value="Easy">Easy</SelectItem>
                      <SelectItem value="Medium">Medium</SelectItem>
                      <SelectItem value="Hard">Hard</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="space-y-2">
                <Label className="text-slate-300">Explanation (Optional)</Label>
                <Textarea
                  value={question.explanation}
                  onChange={(e) => updateQuestion(index, 'explanation', e.target.value)}
                  placeholder="Explain the answer..."
                  className="bg-slate-900 border-slate-700 text-white"
                />
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Submit Button */}
      <div className="mt-8">
        <Button
          onClick={handleSubmit}
          disabled={uploading}
          className="w-full bg-emerald-600 hover:bg-emerald-700 py-6 text-lg"
          data-testid="upload-paper-btn"
        >
          {uploading ? (
            <>
              <Loader2 className="w-5 h-5 mr-2 animate-spin" />
              Uploading Paper...
            </>
          ) : (
            <>
              <Upload className="w-5 h-5 mr-2" />
              Upload Paper
            </>
          )}
        </Button>
      </div>
    </div>
  );
};

export default PaperUploadSection;
