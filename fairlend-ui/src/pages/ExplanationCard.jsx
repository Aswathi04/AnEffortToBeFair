export default function ExplanationCard({ explanation, stage }) {
  if (!explanation) return null;

  return (
    <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-xl">
      <h3 className="text-sm font-semibold text-blue-700 uppercase tracking-wide mb-2">
        AI Compliance Summary — {stage === "baseline" ? "Before Debiasing" : "After Debiasing"}
      </h3>
      <p className="text-sm text-gray-700 leading-relaxed">{explanation}</p>
    </div>
  );
}