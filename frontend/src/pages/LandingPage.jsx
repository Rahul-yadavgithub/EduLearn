import React from 'react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { BookOpen, Brain, Target, TrendingUp, ChevronRight, GraduationCap, Sparkles } from 'lucide-react';

const LandingPage = () => {
  const features = [
    {
      icon: <BookOpen className="w-6 h-6" />,
      title: "Question Papers",
      description: "Access thousands of past papers from JEE, NEET, and school exams"
    },
    {
      icon: <Brain className="w-6 h-6" />,
      title: "AI Doubt Solving",
      description: "Get your doubts cleared with voice or text input"
    },
    {
      icon: <Target className="w-6 h-6" />,
      title: "Mock Tests",
      description: "Practice with real exam-like interface and timing"
    },
    {
      icon: <TrendingUp className="w-6 h-6" />,
      title: "Progress Tracking",
      description: "Track your improvement with detailed analytics"
    }
  ];

  return (
    <div className="min-h-screen bg-[#020617]" data-testid="landing-page">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 glass" data-testid="navbar">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <GraduationCap className="w-8 h-8 text-blue-500" />
            <span className="text-xl font-bold text-white font-['Outfit']">EduLearn</span>
          </div>
          <div className="flex items-center gap-4">
            <Link to="/login">
              <Button variant="ghost" className="text-slate-300 hover:text-white" data-testid="login-btn">
                Login
              </Button>
            </Link>
            <Link to="/register">
              <Button className="bg-blue-600 hover:bg-blue-700" data-testid="get-started-btn">
                Get Started
              </Button>
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-6" data-testid="hero-section">
        <div className="max-w-7xl mx-auto grid lg:grid-cols-2 gap-12 items-center">
          <div className="animate-fade-in-up">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-blue-500/10 border border-blue-500/20 mb-6">
              <Sparkles className="w-4 h-4 text-blue-400" />
              <span className="text-sm text-blue-400">AI-Powered Learning</span>
            </div>
            <h1 className="text-5xl lg:text-7xl font-bold text-white mb-6 font-['Outfit'] tracking-tight leading-tight">
              Master Your
              <span className="gradient-text"> Exams</span>
              <br />With Confidence
            </h1>
            <p className="text-lg text-slate-400 mb-8 max-w-lg leading-relaxed">
              Your comprehensive platform for JEE, NEET, and school exam preparation. 
              Practice with real papers, get real time doubt solving, and track your progress.
            </p>
            <div className="flex flex-wrap gap-4">
              <Link to="/register?role=student">
                <Button size="lg" className="bg-blue-600 hover:bg-blue-700 text-lg px-8 py-6" data-testid="join-student-btn">
                  Join as Student
                  <ChevronRight className="w-5 h-5 ml-2" />
                </Button>
              </Link>
              <Link to="/register?role=teacher">
                <Button size="lg" variant="outline" className="border-emerald-500/50 text-emerald-400 hover:bg-emerald-500/10 text-lg px-8 py-6" data-testid="join-teacher-btn">
                  Join as Teacher
                </Button>
              </Link>
            </div>
          </div>
          
          <div className="relative animate-fade-in-up stagger-2">
            <div className="absolute inset-0 bg-gradient-to-r from-blue-500/20 to-purple-500/20 rounded-3xl blur-3xl"></div>
            <img 
              src="https://images.unsplash.com/photo-1641203251058-3eb0ad540780?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2Mzl8MHwxfHNlYXJjaHwxfHxzdHVkZW50JTIwc3R1ZHlpbmclMjBuaWdodHxlbnwwfHx8fDE3NjY2NTc2ODV8MA&ixlib=rb-4.1.0&q=85"
              alt="Student studying"
              className="relative rounded-3xl shadow-2xl border border-slate-800"
              data-testid="hero-image"
            />
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 px-6" data-testid="features-section">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16 animate-fade-in-up">
            <h2 className="text-4xl font-bold text-white mb-4 font-['Outfit']">
              Everything You Need to Succeed
            </h2>
            <p className="text-slate-400 max-w-2xl mx-auto">
              Comprehensive tools designed to help you ace your competitive exams
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map((feature, index) => (
              <div 
                key={index}
                className={`p-6 rounded-2xl bg-slate-900/50 border border-slate-800 hover-lift animate-fade-in-up stagger-${index + 1}`}
                data-testid={`feature-card-${index}`}
              >
                <div className="w-12 h-12 rounded-xl bg-blue-500/10 flex items-center justify-center text-blue-400 mb-4">
                  {feature.icon}
                </div>
                <h3 className="text-xl font-semibold text-white mb-2 font-['Outfit']">{feature.title}</h3>
                <p className="text-slate-400">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Exam Types Section */}
      <section className="py-20 px-6 bg-slate-900/30" data-testid="exams-section">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-white mb-4 font-['Outfit']">
              Prepare for All Major Exams
            </h2>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8">
            {/* JEE Card */}
            <div className="group relative overflow-hidden rounded-2xl bg-gradient-to-br from-blue-900/50 to-blue-800/30 p-8 border border-blue-500/20 hover-lift" data-testid="jee-card">
              <div className="absolute top-0 right-0 w-32 h-32 bg-blue-500/10 rounded-full blur-3xl group-hover:bg-blue-500/20 transition-all"></div>
              <h3 className="text-2xl font-bold text-white mb-2 font-['Outfit']">JEE</h3>
              <p className="text-blue-200/70 mb-4">Engineering Entrance</p>
              <ul className="space-y-2 text-slate-300">
                <li>• JEE Mains Papers</li>
                <li>• JEE Advanced Papers</li>
                <li>• Mock Tests</li>
              </ul>
            </div>
            
            {/* NEET Card */}
            <div className="group relative overflow-hidden rounded-2xl bg-gradient-to-br from-emerald-900/50 to-emerald-800/30 p-8 border border-emerald-500/20 hover-lift" data-testid="neet-card">
              <div className="absolute top-0 right-0 w-32 h-32 bg-emerald-500/10 rounded-full blur-3xl group-hover:bg-emerald-500/20 transition-all"></div>
              <h3 className="text-2xl font-bold text-white mb-2 font-['Outfit']">NEET</h3>
              <p className="text-emerald-200/70 mb-4">Medical Entrance</p>
              <ul className="space-y-2 text-slate-300">
                <li>• Past Year Papers</li>
                <li>• Biology Focus</li>
                <li>• Full Length Tests</li>
              </ul>
            </div>
            
            {/* School Card */}
            <div className="group relative overflow-hidden rounded-2xl bg-gradient-to-br from-amber-900/50 to-amber-800/30 p-8 border border-amber-500/20 hover-lift" data-testid="school-card">
              <div className="absolute top-0 right-0 w-32 h-32 bg-amber-500/10 rounded-full blur-3xl group-hover:bg-amber-500/20 transition-all"></div>
              <h3 className="text-2xl font-bold text-white mb-2 font-['Outfit']">School</h3>
              <p className="text-amber-200/70 mb-4">Board Exams</p>
              <ul className="space-y-2 text-slate-300">
                <li>• Class 10 & 12</li>
                <li>• All Subjects</li>
                <li>• Chapter Tests</li>
              </ul>
            </div>
          </div>
        </div>
      </section>

          {/* CTA Section */}
      <section className="py-20 px-6" data-testid="cta-section">
        <div className="max-w-4xl mx-auto text-center">
          <div className="p-8 sm:p-12 rounded-3xl bg-gradient-to-br from-blue-900/30 to-slate-900/50 border border-blue-500/20">
            
            <h2 className="text-3xl sm:text-4xl font-bold text-white mb-4 font-['Outfit']">
              Ready to Start Your Journey?
            </h2>

            <p className="text-slate-400 mb-8 max-w-xl mx-auto">
              Join thousands of students who are already preparing smarter with LearnHub.
            </p>

            {/* CTA Button Wrapper */}
            <div className="flex justify-center">
              <Link to="/register" className="w-full sm:w-auto">
                <Button
                  size="lg"
                  className="
                    w-full sm:w-auto
                    max-w-xs
                    bg-blue-600 hover:bg-blue-700
                    text-base sm:text-lg
                    px-6 sm:px-12
                    py-4 sm:py-6
                    flex items-center justify-center
                    gap-2
                  "
                  data-testid="cta-btn"
                >
                  Start Learning Now
                  <ChevronRight className="w-5 h-5" />
                </Button>
              </Link>
            </div>

          </div>
        </div>
      </section>


      {/* Footer */}
      <footer className="py-8 px-6 border-t border-slate-800" data-testid="footer">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <GraduationCap className="w-6 h-6 text-blue-500" />
            <span className="text-lg font-semibold text-white font-['Outfit']">EduLearn</span>
          </div>
          <p className="text-slate-500 text-sm">
            © 2025 EduLearn. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;
