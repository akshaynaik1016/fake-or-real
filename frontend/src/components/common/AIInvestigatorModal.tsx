import React, { useState, useRef, useEffect } from 'react';
import { Bot, Send, X, ShieldAlert, Sparkles, CheckCircle2, Terminal } from 'lucide-react';
import { askAIInvestigator } from '../../api/client';

interface AIInvestigatorModalProps {
  scanId: string;
  isOpen: boolean;
  onClose: () => void;
}

interface ChatMessage {
  sender: 'user' | 'assistant';
  text: string;
  evidenceReferenced?: string[];
}

export const AIInvestigatorModal: React.FC<AIInvestigatorModalProps> = ({ scanId, isOpen, onClose }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      sender: 'assistant',
      text: "Hello! I am your deterministic Safety Investigator (fallback mode). I answer questions strictly grounded in the forensic evidence collected for this opportunity. Ask me anything, or tap a sample question below."
    }
  ]);
  const [inputQuestion, setInputQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (isOpen) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, isOpen]);

  if (!isOpen) return null;

  const quickPrompts = [
    "Why is this suspicious?",
    "Is this company genuine?",
    "Why is the domain risky?",
    "What information should I avoid sharing?",
    "Which finding is the most serious?"
  ];

  const handleSend = async (qText?: string) => {
    const query = qText || inputQuestion;
    if (!query.trim() || loading) return;

    const userMsg: ChatMessage = { sender: 'user', text: query };
    setMessages(prev => [...prev, userMsg]);
    setInputQuestion('');
    setLoading(true);

    try {
      const res = await askAIInvestigator(scanId, query);
      const assistantMsg: ChatMessage = {
        sender: 'assistant',
        text: res.answer,
        evidenceReferenced: res.evidence_referenced
      };
      setMessages(prev => [...prev, assistantMsg]);
    } catch (e) {
      setMessages(prev => [
        ...prev,
        { sender: 'assistant', text: "Unable to process inquiry. Please review the evidence checklist directly." }
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div 
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-in fade-in duration-200"
      onClick={onClose}
    >
      <div 
        className="w-full max-w-2xl bg-cyber-bg border border-cyber-border rounded-3xl shadow-2xl flex flex-col h-[620px] overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        
        {/* Header */}
        <div className="px-6 py-4 border-b border-cyber-border flex items-center justify-between bg-cyber-surface/80">
          <div className="flex items-center space-x-3">
            <div className="p-2.5 rounded-2xl bg-purple-500/15 border border-purple-500/40 text-purple-300 shadow-[0_0_15px_rgba(139,92,246,0.25)]">
              <Bot className="w-6 h-6 text-purple-400" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h3 className="font-extrabold text-white text-base tracking-wide">AI Forensic Investigator</h3>
                <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 font-bold">
                  Evidence-Grounded
                </span>
              </div>
              <p className="text-xs text-slate-400 font-mono mt-0.5">Strictly answers using observed facts, DNS, and identity records</p>
            </div>
          </div>
          <button 
            type="button"
            onClick={onClose}
            className="p-2 rounded-xl text-slate-400 hover:text-white hover:bg-cyber-surface transition-colors cursor-pointer"
            aria-label="Close Modal"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Chat message history */}
        <div className="flex-1 p-5 overflow-y-auto space-y-4">
          {messages.map((msg, i) => (
            <div
              key={i}
              className={`flex flex-col ${msg.sender === 'user' ? 'items-end' : 'items-start'}`}
            >
              <div
                className={`max-w-[85%] p-4 rounded-2xl text-xs sm:text-sm leading-relaxed ${
                  msg.sender === 'user'
                    ? 'bg-gradient-to-r from-cyan-500 to-blue-600 text-slate-950 font-semibold rounded-tr-none shadow-md'
                    : 'bg-cyber-surface border border-cyber-border text-slate-200 rounded-tl-none shadow-sm'
                }`}
              >
                <p className="whitespace-pre-line">{msg.text}</p>
                {msg.evidenceReferenced && msg.evidenceReferenced.length > 0 && (
                  <div className="mt-3 pt-2.5 border-t border-slate-700/60 text-[11px] text-cyan-300 font-mono">
                    <span className="font-bold block mb-1 text-slate-300 uppercase tracking-wider text-[10px]">Referenced Evidence:</span>
                    <ul className="list-disc list-inside space-y-1">
                      {msg.evidenceReferenced.map((ev, idx) => (
                        <li key={idx} className="line-clamp-2">{ev}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          ))}

          {loading && (
            <div className="flex items-center space-x-2.5 text-xs text-cyan-300 p-3 bg-cyber-surface/60 rounded-2xl border border-cyber-border max-w-sm font-mono">
              <Sparkles className="w-4 h-4 animate-spin text-cyber-cyan" />
              <span>Querying verified forensic evidence graph...</span>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Quick prompt suggestions */}
        <div className="px-5 py-2.5 border-t border-cyber-border/60 bg-cyber-surface/50 flex items-center gap-2 overflow-x-auto">
          {quickPrompts.map((prompt, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => handleSend(prompt)}
              className="text-[11px] whitespace-nowrap px-3 py-1.5 rounded-full bg-cyber-card border border-cyber-border text-slate-300 hover:text-cyan-300 hover:border-cyber-cyan/50 hover:bg-cyan-950/20 transition-all cursor-pointer font-medium"
            >
              {prompt}
            </button>
          ))}
        </div>

        {/* Input box */}
        <div className="p-4 border-t border-cyber-border bg-cyber-surface/90 flex items-center space-x-2.5">
          <input
            type="text"
            value={inputQuestion}
            onChange={(e) => setInputQuestion(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Ask why this is suspicious, if company is genuine, etc..."
            className="flex-1 bg-cyber-bg border border-cyber-border rounded-xl px-4 py-2.5 text-xs sm:text-sm text-white placeholder-slate-500 focus:outline-none focus:border-cyber-cyan focus:ring-1 focus:ring-cyber-cyan"
          />
          <button
            type="button"
            onClick={() => handleSend()}
            disabled={loading || !inputQuestion.trim()}
            className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-slate-950 font-black text-xs uppercase tracking-wider disabled:opacity-50 transition-all flex items-center space-x-1.5 cursor-pointer shadow-md"
          >
            <span>Ask</span>
            <Send className="w-3.5 h-3.5 text-slate-950" />
          </button>
        </div>
      </div>
    </div>
  );
};
