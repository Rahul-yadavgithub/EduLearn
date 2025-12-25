import React, { useState, useEffect, useContext } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Label } from '@/components/ui/label';
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from '@/components/ui/alert-dialog';
import { 
  Clock, 
  ChevronLeft, 
  ChevronRight, 
  Flag, 
  Send, 
  RotateCcw,
  Loader2,
  X
} from 'lucide-react';
import axios from 'axios';
import { API, AuthContext } from '@/App';
import { toast } from 'sonner';

const ExamPage = () => {
  const { paperId } = useParams();
  const navigate = useNavigate();
  const { user } = useContext(AuthContext);
  
  const [paper, setPaper] = useState(null);
  const [loading, setLoading] = useState(true);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState({});
  const [markedForReview, setMarkedForReview] = useState(new Set());
  const [timeRemaining, setTimeRemaining] = useState(0);
  const [showSubmitDialog, setShowSubmitDialog] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [startTime] = useState(Date.now());

  useEffect(() => {
    fetchPaper();
  }, [paperId]);

  useEffect(() => {
    if (!paper) return;

    const timer = setInterval(() => {
      setTimeRemaining(prev => {
        if (prev <= 1) {
          handleSubmit();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [paper]);

  const fetchPaper = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API}/papers/${paperId}`, {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
        withCredentials: true
      });
      setPaper(response.data);
      // Set timer based on questions (3 mins per question)
      setTimeRemaining(response.data.questions.length * 180);
    } catch (error) {
      toast.error('Failed to load paper');
      navigate('/student/tests');
    } finally {
      setLoading(false);
    }
  };

  const formatTime = (seconds) => {
    const hrs = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    if (hrs > 0) {
      return `${hrs}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const handleAnswerSelect = (questionId, option) => {
    setAnswers(prev => ({ ...prev, [questionId]: option }));
  };

  const clearResponse = () => {
    const questionId = paper.questions[currentQuestion].question_id;
    setAnswers(prev => {
      const newAnswers = { ...prev };
      delete newAnswers[questionId];
      return newAnswers;
    });
  };

  const toggleMarkForReview = () => {
    const questionId = paper.questions[currentQuestion].question_id;
    setMarkedForReview(prev => {
      const newSet = new Set(prev);
      if (newSet.has(questionId)) {
        newSet.delete(questionId);
      } else {
        newSet.add(questionId);
      }
      return newSet;
    });
  };

  const getQuestionStatus = (index) => {
    const questionId = paper.questions[index].question_id;
    if (index === currentQuestion) return 'current';
    if (markedForReview.has(questionId)) return 'marked';
    if (answers[questionId]) return 'answered';
    return 'unanswered';
  };

  const handleSubmit = async () => {
    setSubmitting(true);
    try {
      const timeTaken = Math.round((Date.now() - startTime) / 1000);
      const token = localStorage.getItem('token');
      
      const response = await axios.post(`${API}/tests/submit`, {
        paper_id: paperId,
        answers,
        time_taken: timeTaken
      }, {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
        withCredentials: true
      });

      toast.success('Test submitted successfully!');
      navigate(`/result/${response.data.result_id}`);
    } catch (error) {
      toast.error('Failed to submit test');
    } finally {
      setSubmitting(false);
      setShowSubmitDialog(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#020617] flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
      </div>
    );
  }

  if (!paper) return null;

  const currentQ = paper.questions[currentQuestion];
  const answeredCount = Object.keys(answers).length;
  const markedCount = markedForReview.size;

  return (
    <div className="exam-mode" data-testid="exam-page">
      {/* Header */}
      <header className="fixed top-0 left-0 right-0 z-50 glass border-b border-slate-800">
        <div className="flex items-center justify-between px-6 py-3">
          <div>
            <h1 className="text-lg font-bold text-white font-['Outfit']">{paper.title}</h1>
            <p className="text-sm text-slate-400">{paper.subject}</p>
          </div>
          
          <div className={`flex items-center gap-2 px-4 py-2 rounded-lg font-mono text-xl ${
            timeRemaining < 300 ? 'bg-red-500/20 text-red-400 timer-warning' : 'bg-slate-800 text-white'
          }`} data-testid="exam-timer">
            <Clock className="w-5 h-5" />
            {formatTime(timeRemaining)}
          </div>
          
          <Button 
            variant="destructive" 
            onClick={() => setShowSubmitDialog(true)}
            data-testid="submit-exam-btn"
          >
            <Send className="w-4 h-4 mr-2" />
            Submit Test
          </Button>
        </div>
      </header>

      {/* Main Content */}
      <div className="pt-20 pb-24 flex h-screen">
        {/* Question Area */}
        <div className="flex-1 overflow-y-auto p-6 lg:p-8">
          <div className="max-w-3xl mx-auto">
            {/* Question Header */}
            <div className="flex items-center justify-between mb-6">
              <Badge className="bg-slate-800 text-slate-300">
                Question {currentQuestion + 1} of {paper.questions.length}
              </Badge>
              {currentQ.difficulty && (
                <Badge className={`
                  ${currentQ.difficulty === 'Easy' ? 'bg-emerald-500/20 text-emerald-400' : ''}
                  ${currentQ.difficulty === 'Medium' ? 'bg-amber-500/20 text-amber-400' : ''}
                  ${currentQ.difficulty === 'Hard' ? 'bg-red-500/20 text-red-400' : ''}
                `}>
                  {currentQ.difficulty}
                </Badge>
              )}
            </div>

            {/* Question Text */}
            <div className="bg-slate-900/50 rounded-xl p-6 mb-6 border border-slate-800">
              <p className="text-lg text-white leading-relaxed" data-testid="question-text">
                {currentQ.question_text}
              </p>
            </div>

            {/* Options */}
            <RadioGroup
              value={answers[currentQ.question_id] || ''}
              onValueChange={(value) => handleAnswerSelect(currentQ.question_id, value)}
              className="space-y-3"
            >
              {Object.entries(currentQ.options).map(([key, value]) => (
                <Label
                  key={key}
                  htmlFor={`option-${key}`}
                  className={`flex items-center gap-4 p-4 rounded-xl border cursor-pointer transition-all ${
                    answers[currentQ.question_id] === key
                      ? 'border-blue-500 bg-blue-500/10'
                      : 'border-slate-700 hover:border-slate-600 bg-slate-900/50'
                  }`}
                  data-testid={`option-${key}`}
                >
                  <RadioGroupItem value={key} id={`option-${key}`} />
                  <span className="text-white">{key}. {value}</span>
                </Label>
              ))}
            </RadioGroup>

            {/* Action Buttons */}
            <div className="flex items-center gap-3 mt-8">
              <Button
                variant="outline"
                onClick={clearResponse}
                className="border-slate-700 text-slate-400 hover:bg-slate-800"
                data-testid="clear-response-btn"
              >
                <RotateCcw className="w-4 h-4 mr-2" />
                Clear Response
              </Button>
              <Button
                variant="outline"
                onClick={toggleMarkForReview}
                className={`${
                  markedForReview.has(currentQ.question_id)
                    ? 'border-amber-500 text-amber-400 bg-amber-500/10'
                    : 'border-slate-700 text-slate-400 hover:bg-slate-800'
                }`}
                data-testid="mark-review-btn"
              >
                <Flag className="w-4 h-4 mr-2" />
                {markedForReview.has(currentQ.question_id) ? 'Marked' : 'Mark for Review'}
              </Button>
            </div>
          </div>
        </div>

        {/* Question Palette - Desktop */}
        <aside className="hidden lg:block w-80 border-l border-slate-800 p-4 overflow-y-auto">
          <h3 className="text-sm font-medium text-slate-400 mb-4">Question Palette</h3>
          
          {/* Legend */}
          <div className="grid grid-cols-2 gap-2 mb-4 text-xs">
            <div className="flex items-center gap-2">
              <div className="w-6 h-6 rounded bg-emerald-500"></div>
              <span className="text-slate-400">Answered ({answeredCount})</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-6 h-6 rounded bg-amber-500"></div>
              <span className="text-slate-400">Marked ({markedCount})</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-6 h-6 rounded bg-blue-500"></div>
              <span className="text-slate-400">Current</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-6 h-6 rounded bg-slate-800"></div>
              <span className="text-slate-400">Not Visited</span>
            </div>
          </div>

          <div className="grid grid-cols-5 gap-2" data-testid="question-palette">
            {paper.questions.map((_, index) => {
              const status = getQuestionStatus(index);
              return (
                <button
                  key={index}
                  onClick={() => setCurrentQuestion(index)}
                  className={`w-10 h-10 rounded-lg text-sm font-medium transition-all
                    ${status === 'current' ? 'q-current' : ''}
                    ${status === 'answered' ? 'q-answered' : ''}
                    ${status === 'marked' ? 'q-marked' : ''}
                    ${status === 'unanswered' ? 'q-unanswered' : ''}
                  `}
                  data-testid={`q-btn-${index}`}
                >
                  {index + 1}
                </button>
              );
            })}
          </div>
        </aside>
      </div>

      {/* Navigation Footer */}
      <footer className="fixed bottom-0 left-0 right-0 z-50 glass border-t border-slate-800">
        <div className="flex items-center justify-between px-6 py-3">
          <Button
            variant="outline"
            onClick={() => setCurrentQuestion(prev => Math.max(0, prev - 1))}
            disabled={currentQuestion === 0}
            className="border-slate-700 text-slate-400"
            data-testid="prev-btn"
          >
            <ChevronLeft className="w-4 h-4 mr-2" />
            Previous
          </Button>
          
          <div className="text-sm text-slate-400">
            {answeredCount} / {paper.questions.length} answered
          </div>
          
          <Button
            onClick={() => setCurrentQuestion(prev => Math.min(paper.questions.length - 1, prev + 1))}
            disabled={currentQuestion === paper.questions.length - 1}
            className="bg-blue-600 hover:bg-blue-700"
            data-testid="next-btn"
          >
            Save & Next
            <ChevronRight className="w-4 h-4 ml-2" />
          </Button>
        </div>
      </footer>

      {/* Submit Confirmation Dialog */}
      <AlertDialog open={showSubmitDialog} onOpenChange={setShowSubmitDialog}>
        <AlertDialogContent className="bg-slate-900 border-slate-800">
          <AlertDialogHeader>
            <AlertDialogTitle className="text-white">Submit Test?</AlertDialogTitle>
            <AlertDialogDescription className="text-slate-400">
              <p className="mb-4">Are you sure you want to submit the test?</p>
              <div className="space-y-2 text-sm">
                <p>• Answered: {answeredCount} / {paper.questions.length}</p>
                <p>• Unattempted: {paper.questions.length - answeredCount}</p>
                <p>• Marked for Review: {markedCount}</p>
              </div>
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel className="bg-slate-800 border-slate-700 text-white hover:bg-slate-700">
              Continue Exam
            </AlertDialogCancel>
            <AlertDialogAction
              onClick={handleSubmit}
              disabled={submitting}
              className="bg-blue-600 hover:bg-blue-700"
            >
              {submitting ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Submitting...
                </>
              ) : (
                'Submit Test'
              )}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
};

export default ExamPage;
