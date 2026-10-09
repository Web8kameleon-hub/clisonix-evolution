interface SuggestedQuestionsProps {
  visible: boolean;
  title: string;
  questions: string[];
  onPickQuestion: (question: string) => void;
}

export function SuggestedQuestions({ visible, title, questions, onPickQuestion }: SuggestedQuestionsProps) {
  if (!visible) return null;

  return (
    <div className="max-w-2xl mx-auto w-full px-4 sm:px-6 pb-3">
      <p className="text-xs text-gray-400 mb-2.5 font-medium">{title}</p>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
        {questions.map((question, idx) => (
          <button
            key={idx}
            onClick={() => onPickQuestion(question)}
            className="text-left text-sm text-gray-600 bg-white hover:bg-emerald-50 hover:text-emerald-700 rounded-xl px-4 py-3 transition-all border border-gray-100 hover:border-emerald-200 hover:shadow-sm"
          >
            {question}
          </button>
        ))}
      </div>
    </div>
  );
}
