import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { 
  MessageSquare, 
  Clock, 
  User, 
  Send, 
  Mic, 
  MicOff,
  Loader2,
  CheckCircle,
  BookOpen
} from 'lucide-react';
import axios from 'axios';
import { API } from '@/App';
import { toast } from 'sonner';

const DoubtSolvingSection = () => {
  const [doubts, setDoubts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedDoubt, setSelectedDoubt] = useState(null);
  const [answerText, setAnswerText] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [transcribing, setTranscribing] = useState(false);
  const mediaRecorderRef = useRef(null);
  const chunksRef = useRef([]);

  useEffect(() => {
    fetchDoubts();
  }, []);

  const fetchDoubts = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API}/doubts`, {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
        withCredentials: true
      });
      setDoubts(response.data);
    } catch (error) {
      toast.error('Failed to fetch doubts');
    } finally {
      setLoading(false);
    }
  };

  const handleAnswerDoubt = async () => {
    if (!answerText.trim()) {
      toast.error('Please enter an answer');
      return;
    }

    setSubmitting(true);
    try {
      const token = localStorage.getItem('token');
      await axios.put(`${API}/doubts/${selectedDoubt.doubt_id}/answer`, {
        answer_text: answerText
      }, {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
        withCredentials: true
      });

      toast.success('Answer submitted successfully!');
      setSelectedDoubt(null);
      setAnswerText('');
      fetchDoubts();
    } catch (error) {
      toast.error('Failed to submit answer');
    } finally {
      setSubmitting(false);
    }
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });
      mediaRecorderRef.current = mediaRecorder;
      chunksRef.current = [];

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunksRef.current.push(e.data);
        }
      };

      mediaRecorder.onstop = async () => {
        const blob = new Blob(chunksRef.current, { type: 'audio/webm' });
        stream.getTracks().forEach(track => track.stop());
        await transcribeAudio(blob);
      };

      mediaRecorder.start();
      setIsRecording(true);
      toast.info('Recording started...');
    } catch (error) {
      toast.error('Failed to access microphone');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const transcribeAudio = async (blob) => {
    setTranscribing(true);
    try {
      const formData = new FormData();
      formData.append('audio', blob, 'recording.webm');

      const token = localStorage.getItem('token');
      const response = await axios.post(`${API}/transcribe`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
          ...(token ? { Authorization: `Bearer ${token}` } : {})
        },
        withCredentials: true
      });

      setAnswerText(prev => prev + (prev ? ' ' : '') + response.data.text);
      toast.success('Voice transcribed!');
    } catch (error) {
      toast.error('Failed to transcribe audio');
    } finally {
      setTranscribing(false);
    }
  };

  const pendingDoubts = doubts.filter(d => d.status === 'pending');
  const answeredDoubts = doubts.filter(d => d.status === 'answered');

  return (
    <div data-testid="doubt-solving-section">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white font-['Outfit'] mb-2">Solve Student Doubts</h1>
        <p className="text-slate-400">Help students by answering their questions</p>
      </div>

      {/* Stats */}
      <div className="grid md:grid-cols-2 gap-4 mb-8">
        <Card className="bg-slate-900/50 border-slate-800">
          <CardContent className="p-6 flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-amber-500/20 flex items-center justify-center">
              <Clock className="w-6 h-6 text-amber-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-white">{pendingDoubts.length}</p>
              <p className="text-sm text-slate-400">Pending Doubts</p>
            </div>
          </CardContent>
        </Card>
        <Card className="bg-slate-900/50 border-slate-800">
          <CardContent className="p-6 flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-emerald-500/20 flex items-center justify-center">
              <CheckCircle className="w-6 h-6 text-emerald-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-white">{answeredDoubts.length}</p>
              <p className="text-sm text-slate-400">Answered</p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Pending Doubts */}
      <Card className="bg-slate-900/50 border-slate-800">
        <CardHeader>
          <CardTitle className="text-lg font-['Outfit'] text-white flex items-center gap-2">
            <MessageSquare className="w-5 h-5 text-emerald-400" />
            Pending Doubts
          </CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="w-8 h-8 animate-spin text-emerald-500" />
            </div>
          ) : pendingDoubts.length === 0 ? (
            <div className="text-center py-12">
              <CheckCircle className="w-12 h-12 text-emerald-500 mx-auto mb-4" />
              <p className="text-slate-400">All doubts have been answered!</p>
            </div>
          ) : (
            <div className="space-y-3">
              {pendingDoubts.map((doubt) => (
                <div
                  key={doubt.doubt_id}
                  className="p-4 rounded-xl bg-slate-800/50 border border-slate-700 hover:border-emerald-500/30 transition-all cursor-pointer"
                  onClick={() => {
                    setSelectedDoubt(doubt);
                    setAnswerText('');
                  }}
                  data-testid={`doubt-item-${doubt.doubt_id}`}
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <Badge className="bg-slate-700 text-slate-300">{doubt.subject}</Badge>
                        <Badge className="status-pending">{doubt.status}</Badge>
                      </div>
                      <p className="text-slate-300 line-clamp-2">{doubt.question_text}</p>
                      <div className="flex items-center gap-4 mt-3 text-sm text-slate-500">
                        <span className="flex items-center gap-1">
                          <User className="w-4 h-4" />
                          {doubt.student_name}
                        </span>
                        <span className="flex items-center gap-1">
                          <Clock className="w-4 h-4" />
                          {new Date(doubt.created_at).toLocaleDateString()}
                        </span>
                      </div>
                    </div>
                    <Button
                      className="bg-emerald-600 hover:bg-emerald-700"
                      onClick={(e) => {
                        e.stopPropagation();
                        setSelectedDoubt(doubt);
                        setAnswerText('');
                      }}
                      data-testid={`answer-btn-${doubt.doubt_id}`}
                    >
                      Answer
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Answer Dialog */}
      <Dialog open={!!selectedDoubt} onOpenChange={() => setSelectedDoubt(null)}>
        <DialogContent className="bg-slate-900 border-slate-800 max-w-2xl">
          <DialogHeader>
            <DialogTitle className="text-white">Answer Doubt</DialogTitle>
          </DialogHeader>
          
          {selectedDoubt && (
            <div className="space-y-4">
              {/* Question */}
              <div className="p-4 rounded-lg bg-slate-800/50">
                <div className="flex items-center gap-2 mb-2">
                  <Badge className="bg-slate-700 text-slate-300">{selectedDoubt.subject}</Badge>
                  <span className="text-sm text-slate-500">from {selectedDoubt.student_name}</span>
                </div>
                <p className="text-white">{selectedDoubt.question_text}</p>
              </div>

              {/* Answer Input */}
              <div className="relative">
                <Textarea
                  value={answerText}
                  onChange={(e) => setAnswerText(e.target.value)}
                  placeholder="Type your answer or use voice input..."
                  className="min-h-[150px] bg-slate-950 border-slate-800 text-white placeholder:text-slate-500 pr-14"
                  data-testid="answer-text"
                />
                <button
                  type="button"
                  onClick={isRecording ? stopRecording : startRecording}
                  disabled={transcribing}
                  className={`absolute bottom-4 right-4 p-3 rounded-full transition-all ${
                    isRecording 
                      ? 'bg-red-500 text-white recording-pulse' 
                      : 'bg-emerald-500/20 text-emerald-400 hover:bg-emerald-500/30'
                  }`}
                  data-testid="teacher-voice-btn"
                >
                  {transcribing ? (
                    <Loader2 className="w-5 h-5 animate-spin" />
                  ) : isRecording ? (
                    <MicOff className="w-5 h-5" />
                  ) : (
                    <Mic className="w-5 h-5" />
                  )}
                </button>
              </div>

              {isRecording && (
                <p className="text-sm text-red-400 animate-pulse">
                  Recording... Click the mic button to stop
                </p>
              )}
            </div>
          )}

          <DialogFooter>
            <Button 
              variant="outline" 
              onClick={() => setSelectedDoubt(null)}
              className="border-slate-700 text-slate-300"
            >
              Cancel
            </Button>
            <Button
              onClick={handleAnswerDoubt}
              disabled={submitting}
              className="bg-emerald-600 hover:bg-emerald-700"
              data-testid="submit-answer-btn"
            >
              {submitting ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Submitting...
                </>
              ) : (
                <>
                  <Send className="w-4 h-4 mr-2" />
                  Submit Answer
                </>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default DoubtSolvingSection;
