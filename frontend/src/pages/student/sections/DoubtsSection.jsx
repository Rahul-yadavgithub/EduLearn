import React, { useState, useEffect, useRef, useContext } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { HelpCircle, Mic, MicOff, Send, Clock, CheckCircle, Loader2, MessageSquare } from 'lucide-react';
import axios from 'axios';
import { API, AuthContext } from '@/App';
import { toast } from 'sonner';

const DoubtsSection = () => {
  const { user } = useContext(AuthContext);
  const [doubts, setDoubts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [transcribing, setTranscribing] = useState(false);
  const mediaRecorderRef = useRef(null);
  const chunksRef = useRef([]);
  
  const [newDoubt, setNewDoubt] = useState({
    subject: '',
    question_text: ''
  });

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

  const handleSubmitDoubt = async () => {
    if (!newDoubt.subject || !newDoubt.question_text.trim()) {
      toast.error('Please select a subject and enter your doubt');
      return;
    }

    setSubmitting(true);
    try {
      const token = localStorage.getItem('token');
      await axios.post(`${API}/doubts`, newDoubt, {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
        withCredentials: true
      });
      toast.success('Doubt submitted successfully!');
      setNewDoubt({ subject: '', question_text: '' });
      fetchDoubts();
    } catch (error) {
      toast.error('Failed to submit doubt');
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
      toast.info('Recording started... Speak your doubt');
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

      setNewDoubt(prev => ({
        ...prev,
        question_text: prev.question_text + (prev.question_text ? ' ' : '') + response.data.text
      }));
      toast.success('Voice transcribed successfully!');
    } catch (error) {
      toast.error('Failed to transcribe audio');
    } finally {
      setTranscribing(false);
    }
  };

  const pendingDoubts = doubts.filter(d => d.status === 'pending');
  const answeredDoubts = doubts.filter(d => d.status === 'answered');

  return (
    <div data-testid="doubts-section">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white font-['Outfit'] mb-2">Ask a Doubt</h1>
        <p className="text-slate-400">Get your questions answered by expert teachers</p>
      </div>

      {/* New Doubt Form */}
      <Card className="bg-slate-900/50 border-slate-800 mb-8">
        <CardHeader>
          <CardTitle className="text-lg font-['Outfit'] text-white flex items-center gap-2">
            <HelpCircle className="w-5 h-5 text-blue-400" />
            Submit a New Doubt
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <Select
            value={newDoubt.subject}
            onValueChange={(value) => setNewDoubt({ ...newDoubt, subject: value })}
          >
            <SelectTrigger className="bg-slate-900 border-slate-700 text-white" data-testid="doubt-subject">
              <SelectValue placeholder="Select Subject" />
            </SelectTrigger>
            <SelectContent className="bg-slate-900 border-slate-700">
              <SelectItem value="Mathematics">Mathematics</SelectItem>
              <SelectItem value="Physics">Physics</SelectItem>
              <SelectItem value="Chemistry">Chemistry</SelectItem>
              <SelectItem value="Biology">Biology</SelectItem>
            </SelectContent>
          </Select>

          <div className="relative">
            <Textarea
              placeholder="Type your doubt here or use voice input..."
              className="min-h-[150px] bg-slate-950 border-slate-800 text-white placeholder:text-slate-500 pr-14"
              value={newDoubt.question_text}
              onChange={(e) => setNewDoubt({ ...newDoubt, question_text: e.target.value })}
              data-testid="doubt-text"
            />
            <button
              type="button"
              onClick={isRecording ? stopRecording : startRecording}
              disabled={transcribing}
              className={`absolute bottom-4 right-4 p-3 rounded-full transition-all ${
                isRecording 
                  ? 'bg-red-500 text-white recording-pulse' 
                  : 'bg-blue-500/20 text-blue-400 hover:bg-blue-500/30'
              }`}
              data-testid="voice-btn"
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

          <Button 
            className="w-full bg-blue-600 hover:bg-blue-700"
            onClick={handleSubmitDoubt}
            disabled={submitting}
            data-testid="submit-doubt-btn"
          >
            {submitting ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Submitting...
              </>
            ) : (
              <>
                <Send className="w-4 h-4 mr-2" />
                Submit Doubt
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {/* Doubts List */}
      <Tabs defaultValue="pending" className="w-full">
        <TabsList className="bg-slate-900 border border-slate-800">
          <TabsTrigger value="pending" className="data-[state=active]:bg-blue-500/20">
            <Clock className="w-4 h-4 mr-2" />
            Pending ({pendingDoubts.length})
          </TabsTrigger>
          <TabsTrigger value="answered" className="data-[state=active]:bg-emerald-500/20">
            <CheckCircle className="w-4 h-4 mr-2" />
            Answered ({answeredDoubts.length})
          </TabsTrigger>
        </TabsList>

        <TabsContent value="pending" className="mt-6">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
            </div>
          ) : pendingDoubts.length === 0 ? (
            <div className="text-center py-12">
              <MessageSquare className="w-12 h-12 text-slate-600 mx-auto mb-4" />
              <p className="text-slate-400">No pending doubts</p>
            </div>
          ) : (
            <div className="space-y-4">
              {pendingDoubts.map((doubt) => (
                <DoubtCard key={doubt.doubt_id} doubt={doubt} />
              ))}
            </div>
          )}
        </TabsContent>

        <TabsContent value="answered" className="mt-6">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
            </div>
          ) : answeredDoubts.length === 0 ? (
            <div className="text-center py-12">
              <MessageSquare className="w-12 h-12 text-slate-600 mx-auto mb-4" />
              <p className="text-slate-400">No answered doubts yet</p>
            </div>
          ) : (
            <div className="space-y-4">
              {answeredDoubts.map((doubt) => (
                <DoubtCard key={doubt.doubt_id} doubt={doubt} />
              ))}
            </div>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
};

const DoubtCard = ({ doubt }) => {
  const [expanded, setExpanded] = useState(false);

  return (
    <Card 
      className="bg-slate-900/50 border-slate-800"
      data-testid={`doubt-card-${doubt.doubt_id}`}
    >
      <CardContent className="p-4">
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-2">
              <Badge className="bg-slate-800 text-slate-300">{doubt.subject}</Badge>
              <Badge className={doubt.status === 'answered' ? 'status-answered' : 'status-pending'}>
                {doubt.status}
              </Badge>
            </div>
            <p className={`text-slate-300 ${expanded ? '' : 'line-clamp-2'}`}>
              {doubt.question_text}
            </p>
            {doubt.question_text.length > 150 && (
              <button
                onClick={() => setExpanded(!expanded)}
                className="text-blue-400 text-sm mt-1 hover:text-blue-300"
              >
                {expanded ? 'Show less' : 'Show more'}
              </button>
            )}
            <p className="text-xs text-slate-500 mt-2">
              {new Date(doubt.created_at).toLocaleDateString()}
            </p>
          </div>
        </div>

        {doubt.status === 'answered' && doubt.answer_text && (
          <div className="mt-4 pt-4 border-t border-slate-800">
            <p className="text-sm text-emerald-400 font-medium mb-2">Teacher's Answer:</p>
            <p className="text-slate-300">{doubt.answer_text}</p>
            {doubt.answer_image && (
              <img src={doubt.answer_image} alt="Solution" className="mt-2 rounded-lg max-w-full" />
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default DoubtsSection;
