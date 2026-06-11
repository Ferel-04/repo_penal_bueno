"use client";

import React, { useState } from "react";
import ThemeToggle from "./theme-toggle";

type LegalArticle = {
  article_number: string;
  content: string;
  source_name: string;
  content_hash?: string | null;
  source_version?: string | null;
  last_reform_date?: string | null;
  classification: string;
  match_reason?: string;
};

type CandidateGroups = {
  penal_articles: LegalArticle[];
  procedural_foundations: LegalArticle[];
  victim_rights: LegalArticle[];
  constitutional_foundations: LegalArticle[];
  human_review_warnings: string[];
};

type InvestigationStep = {
  step: string;
  legal_basis: string;
  urgent: boolean;
  category: string;
};

type AnalyzeResponse = {
  facts_summary: string;
  detected_legal_topics: string[];
  structured_facts: Record<string, string | boolean | null> | null;
  candidate_articles: CandidateGroups;
  missing_questions: string[];
  human_review_required: boolean;
  analysis_engine: "local_llm" | "deterministic_fallback";
  legal_assignment_engine: "deterministic_rules";
  detected_crime_type: string;
  crime_subtype: string | null;
  crime_display_name: string;
  investigation_steps: InvestigationStep[];
};

const API_URL = "http://127.0.0.1:8000/analyze";

const sampleFacts =
  "La víctima refiere violencia y amenazas. Solicita medida de protección, asesoría jurídica y reparación integral.";

const groupLabels: Array<{
  key: keyof Omit<CandidateGroups, "human_review_warnings">;
  title: string;
}> = [
  { key: "penal_articles", title: "Artículos penales" },
  { key: "procedural_foundations", title: "Fundamentos procesales" },
  { key: "victim_rights", title: "Derechos de víctima" },
  { key: "constitutional_foundations", title: "Fundamentos constitucionales" },
];

function formatClassification(value: string) {
  return value.replaceAll("_", " ");
}

function shortHash(hash?: string | null) {
  return hash ? hash.slice(0, 10) : "sin hash";
}

function ArticleCard({ article }: { article: LegalArticle }) {
  const versionParts = [article.source_version, article.last_reform_date].filter(Boolean);

  return (
    <article className="rounded-md border border-slate-200 bg-white p-4 shadow-sm dark:border-neutral-700 dark:bg-neutral-900">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-neutral-400">
            {article.source_name}
          </p>
          <h3 className="mt-1 text-base font-semibold text-slate-950 dark:text-neutral-50">
            Artículo {article.article_number}
          </h3>
        </div>
        <span className="w-fit rounded border border-slate-300 bg-slate-50 px-2 py-1 text-xs font-medium text-slate-700 dark:border-neutral-600 dark:bg-neutral-800 dark:text-neutral-300">
          {formatClassification(article.classification)}
        </span>
      </div>

      <p className="mt-3 whitespace-pre-line text-sm leading-6 text-slate-700 dark:text-neutral-300">
        {article.content}
      </p>

      <div className="mt-4 flex flex-wrap gap-2 text-xs text-slate-600 dark:text-neutral-400">
        <span className="rounded border border-slate-200 bg-slate-50 px-2 py-1 font-mono dark:border-neutral-700 dark:bg-neutral-800">
          {shortHash(article.content_hash)}
        </span>
        {versionParts.length > 0 ? (
          <span className="rounded border border-slate-200 bg-slate-50 px-2 py-1 dark:border-neutral-700 dark:bg-neutral-800">
            {versionParts.join(" · ")}
          </span>
        ) : null}
      </div>
    </article>
  );
}

function ChevronIcon({ open }: { open: boolean }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 20 20"
      fill="currentColor"
      className={`h-5 w-5 shrink-0 text-slate-400 transition-transform duration-200 dark:text-neutral-500 ${open ? "rotate-180" : ""}`}
      aria-hidden="true"
    >
      <path
        fillRule="evenodd"
        d="M5.22 8.22a.75.75 0 0 1 1.06 0L10 11.94l3.72-3.72a.75.75 0 1 1 1.06 1.06l-4.25 4.25a.75.75 0 0 1-1.06 0L5.22 9.28a.75.75 0 0 1 0-1.06Z"
        clipRule="evenodd"
      />
    </svg>
  );
}

function CollapsibleSection({
  title,
  badge,
  defaultOpen = true,
  children,
}: {
  title: string;
  badge?: React.ReactNode;
  defaultOpen?: boolean;
  children: React.ReactNode;
}) {
  const [open, setOpen] = useState(defaultOpen);

  return (
    <div>
      <button
        type="button"
        onClick={() => setOpen((prev) => !prev)}
        className="flex w-full items-center justify-between gap-3 py-3 text-left"
        aria-expanded={open}
      >
        <div className="flex items-center gap-3">
          <h2 className="text-lg font-semibold text-slate-950 dark:text-neutral-50">{title}</h2>
          {badge}
        </div>
        <ChevronIcon open={open} />
      </button>
      {open ? children : null}
    </div>
  );
}

function ArticleGroup({
  title,
  articles,
}: {
  title: string;
  articles: LegalArticle[];
}) {
  return (
    <section className="border-t border-slate-200 dark:border-neutral-700">
      <CollapsibleSection
        title={title}
        badge={
          <span className="rounded border border-slate-200 bg-slate-50 px-2 py-1 text-xs text-slate-600 dark:border-neutral-700 dark:bg-neutral-800 dark:text-neutral-400">
            {articles.length}
          </span>
        }
      >
        {articles.length > 0 ? (
          <div className="grid gap-3 pb-4">
            {articles.map((article) => (
              <ArticleCard
                article={article}
                key={`${article.source_name}-${article.article_number}-${article.content_hash}`}
              />
            ))}
          </div>
        ) : (
          <p className="pb-4 text-sm text-slate-500 dark:text-neutral-400">Sin coincidencias para este grupo.</p>
        )}
      </CollapsibleSection>
    </section>
  );
}

const categoryOrder = ["cautelar", "testimonio", "pericial", "inspeccion", "documental", "diligencia"] as const;

const categoryLabels: Record<string, string> = {
  cautelar: "Medidas cautelares",
  testimonio: "Testimonios y entrevistas",
  pericial: "Peritajes",
  inspeccion: "Inspección",
  documental: "Documental",
  diligencia: "Otras diligencias",
};

function InvestigationStepsSection({
  steps,
  detectedCrimeType,
}: {
  steps: InvestigationStep[];
  detectedCrimeType: string;
}) {
  if (steps.length === 0) {
    return (
      <section className="rounded-md border border-slate-200 bg-white px-4 py-6 shadow-sm dark:border-neutral-700 dark:bg-neutral-900">
        <h2 className="text-lg font-semibold text-slate-950 dark:text-neutral-50">
          Diligencias mínimas de investigación
        </h2>
        <p className="mt-3 text-sm text-slate-500 dark:text-neutral-400">
          Sin diligencias sugeridas para este tipo de delito.
        </p>
      </section>
    );
  }

  const urgentCount = steps.filter((s) => s.urgent).length;

  const grouped = new Map<string, InvestigationStep[]>();
  for (const cat of categoryOrder) {
    const catSteps = steps.filter((s) => s.category === cat);
    if (catSteps.length > 0) {
      grouped.set(cat, catSteps);
    }
  }

  const uncategorized = steps.filter(
    (s) => !categoryOrder.includes(s.category as (typeof categoryOrder)[number]),
  );
  if (uncategorized.length > 0) {
    grouped.set("other", uncategorized);
  }

  return (
    <section className="rounded-md border border-slate-200 bg-white px-4 py-6 shadow-sm dark:border-neutral-700 dark:bg-neutral-900">
      <CollapsibleSection
        title="Diligencias mínimas de investigación"
        badge={
          <span className="rounded border border-slate-200 bg-slate-50 px-2 py-1 text-xs text-slate-600 dark:border-neutral-700 dark:bg-neutral-800 dark:text-neutral-400">
            {steps.length} diligencias · {urgentCount} urgentes
          </span>
        }
      >
        {detectedCrimeType === "unknown" ? (
          <p className="mb-4 rounded border border-amber-300 bg-amber-50 px-3 py-2 text-xs text-amber-700 dark:border-amber-700 dark:bg-amber-950 dark:text-amber-300">
            Diligencias genéricas — selecciona el tipo de delito para ver las específicas.
          </p>
        ) : null}

        <div className="space-y-6 pb-2">
          {Array.from(grouped.entries()).map(([cat, catSteps]) => (
            <div key={cat}>
              <h3 className="mb-2 text-sm font-semibold text-slate-800 dark:text-neutral-200">
                {categoryLabels[cat] ?? cat}
              </h3>
              <ul className="space-y-3">
                {catSteps.map((step, idx) => (
                  <li
                    key={`${cat}-${idx}`}
                    className="rounded-md border border-slate-200 bg-slate-50 p-3 dark:border-neutral-700 dark:bg-neutral-800"
                  >
                    <div className="flex items-start gap-2">
                      {step.urgent ? (
                        <span className="mt-0.5 inline-block h-2 w-2 shrink-0 rounded-full bg-red-500" />
                      ) : (
                        <span className="mt-0.5 inline-block h-2 w-2 shrink-0 rounded-full bg-slate-300 dark:bg-neutral-600" />
                      )}
                      <div>
                        <p className="text-sm leading-6 text-slate-900 dark:text-neutral-100">
                          {step.step}
                          {step.urgent ? (
                            <span className="ml-2 inline-block rounded bg-red-100 px-1.5 py-0.5 text-xs font-semibold uppercase text-red-700 dark:bg-red-950 dark:text-red-300">
                              Urgente
                            </span>
                          ) : null}
                        </p>
                        <p className="mt-1 text-xs leading-5 text-slate-500 dark:text-neutral-400">
                          {step.legal_basis}
                        </p>
                      </div>
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </CollapsibleSection>
    </section>
  );
}

export default function Home() {
  const [facts, setFacts] = useState(sampleFacts);
  const [crimeType, setCrimeType] = useState<string>("");
  const [result, setResult] = useState<AnalyzeResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const cleanFacts = facts.trim();

    if (!cleanFacts) {
      setError("Captura los hechos antes de analizar.");
      setResult(null);
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(API_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ facts: cleanFacts, crime_type: crimeType || null }),
      });

      const payload = await response.json();

      if (!response.ok) {
        throw new Error(payload.detail || "No se pudo completar el análisis.");
      }

      setResult(payload);
    } catch (requestError) {
      setResult(null);
      setError(
        requestError instanceof Error
          ? requestError.message
          : "No se pudo conectar con el backend local.",
      );
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-slate-100 text-slate-950 dark:bg-neutral-950 dark:text-neutral-50">
      <div className="mx-auto flex w-full max-w-6xl flex-col gap-8 px-4 py-6 sm:px-6 lg:px-8">
        <header className="flex flex-col gap-3 border-b border-slate-300 pb-5 dark:border-neutral-700">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-sm font-medium text-slate-600 dark:text-neutral-400">
                Demo local con IA opcional
              </p>
              <h1 className="mt-1 text-3xl font-semibold tracking-normal text-slate-950 dark:text-neutral-50">
                Asistente Penal MVP
              </h1>
            </div>
            <ThemeToggle />
          </div>
          <p className="max-w-3xl text-sm leading-6 text-slate-700 dark:text-neutral-300">
            Herramienta de apoyo. No sustituye criterio jurídico profesional.
          </p>
        </header>

        <section className="grid gap-6 lg:grid-cols-[minmax(0,0.92fr)_minmax(0,1.08fr)]">
          <form
            onSubmit={handleSubmit}
            className="rounded-md border border-slate-200 bg-white p-4 shadow-sm dark:border-neutral-700 dark:bg-neutral-900"
          >
            <label htmlFor="facts" className="text-sm font-semibold text-slate-950 dark:text-neutral-50">
              Hechos
            </label>
            <textarea
              id="facts"
              value={facts}
              onChange={(event) => setFacts(event.target.value)}
              className="mt-3 min-h-64 w-full resize-y rounded-md border border-slate-300 bg-white p-3 text-sm leading-6 text-slate-900 outline-none transition focus:border-slate-700 focus:ring-2 focus:ring-slate-200 dark:border-neutral-600 dark:bg-neutral-800 dark:text-neutral-100 dark:focus:border-neutral-400 dark:focus:ring-neutral-700"
              placeholder="Describe los hechos relevantes..."
            />
            <div className="mt-3">
              <label htmlFor="crimeType" className="text-sm font-semibold text-slate-950 dark:text-neutral-50">
                Tipo de delito (opcional)
              </label>
              <select
                id="crimeType"
                value={crimeType}
                onChange={(event) => setCrimeType(event.target.value)}
                className="mt-1 w-full rounded-md border border-slate-300 bg-white p-2 text-sm text-slate-900 outline-none transition focus:border-slate-700 focus:ring-2 focus:ring-slate-200 dark:border-neutral-600 dark:bg-neutral-800 dark:text-neutral-100 dark:focus:border-neutral-400 dark:focus:ring-neutral-700"
              >
                <option value="">Detectar automáticamente</option>
                <option value="robo">Robo</option>
                <option value="lesiones">Lesiones</option>
                <option value="homicidio">Homicidio</option>
                <option value="violacion">Violación</option>
                <option value="violencia_familiar">Violencia Familiar</option>
                <option value="fraude">Fraude</option>
              </select>
            </div>
            <div className="mt-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <button
                type="submit"
                disabled={isLoading}
                className="rounded-md bg-slate-950 px-4 py-2 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:bg-slate-400 dark:bg-slate-50 dark:text-slate-950 dark:hover:bg-neutral-200 dark:disabled:bg-neutral-600"
              >
                {isLoading ? "Analizando..." : "Analizar"}
              </button>
              <span className="text-xs text-slate-500 dark:text-neutral-400">
                Backend esperado: 127.0.0.1:8000
              </span>
            </div>
            {error ? (
              <p className="mt-4 rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-700 dark:border-red-800 dark:bg-red-950 dark:text-red-300">
                {error}
              </p>
            ) : null}
          </form>

          <section className="rounded-md border border-slate-200 bg-white p-4 shadow-sm dark:border-neutral-700 dark:bg-neutral-900">
            <h2 className="text-lg font-semibold text-slate-950 dark:text-neutral-50">Resumen</h2>
            {result ? (
              <div className="mt-4 space-y-4">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="rounded-md bg-slate-900 px-3 py-1 text-sm font-semibold text-white dark:bg-slate-100 dark:text-slate-900">
                    {result.crime_display_name}
                  </span>
                  {result.crime_subtype ? (
                    <span className="rounded border border-slate-300 bg-slate-50 px-2 py-1 text-xs text-slate-600 dark:border-neutral-600 dark:bg-neutral-800 dark:text-neutral-300">
                      {result.crime_subtype.replaceAll("_", " ")}
                    </span>
                  ) : null}
                  {result.detected_crime_type === "unknown" ? (
                    <span className="rounded border border-amber-300 bg-amber-50 px-2 py-1 text-xs text-amber-700 dark:border-amber-700 dark:bg-amber-950 dark:text-amber-300">
                      Selecciona el tipo de delito manualmente
                    </span>
                  ) : null}
                </div>
                <p className="text-sm leading-6 text-slate-700 dark:text-neutral-300">{result.facts_summary}</p>
                <div>
                  <h3 className="text-sm font-semibold text-slate-950 dark:text-neutral-50">Temas detectados</h3>
                  {result.detected_legal_topics.length > 0 ? (
                    <div className="mt-2 flex flex-wrap gap-2">
                      {result.detected_legal_topics.map((topic) => (
                        <span
                          key={topic}
                          className="rounded border border-slate-200 bg-slate-50 px-2 py-1 text-xs text-slate-700 dark:border-neutral-700 dark:bg-neutral-800 dark:text-neutral-300"
                        >
                          {topic}
                        </span>
                      ))}
                    </div>
                  ) : (
                    <p className="mt-2 text-sm text-slate-500 dark:text-neutral-400">Sin temas detectados.</p>
                  )}
                </div>
                <div>
                  <h3 className="text-sm font-semibold text-slate-950 dark:text-neutral-50">Motor de análisis</h3>
                  <div className="mt-2 flex flex-wrap gap-2">
                    <span className="rounded border border-slate-200 bg-slate-50 px-2 py-1 text-xs text-slate-700 dark:border-neutral-700 dark:bg-neutral-800 dark:text-neutral-300">
                      Extractor:{" "}
                      {result.analysis_engine === "local_llm"
                        ? "Ollama local"
                        : "Reglas deterministas"}
                    </span>
                    <span className="rounded border border-slate-200 bg-slate-50 px-2 py-1 text-xs text-slate-700 dark:border-neutral-700 dark:bg-neutral-800 dark:text-neutral-300">
                      Asignación legal: reglas deterministas
                    </span>
                  </div>
                </div>
                <div>
                  <h3 className="text-sm font-semibold text-slate-950 dark:text-neutral-50">
                    Hechos estructurados por IA
                  </h3>
                  {result.structured_facts ? (
                    <pre className="mt-2 overflow-auto rounded-md border border-slate-200 bg-slate-950 p-3 text-xs leading-5 text-slate-50 dark:border-neutral-700 dark:bg-neutral-800 dark:text-neutral-200">
                      {JSON.stringify(result.structured_facts, null, 2)}
                    </pre>
                  ) : (
                    <p className="mt-2 text-sm text-slate-500 dark:text-neutral-400">
                      No se usó extractor local; se aplicó fallback determinista.
                    </p>
                  )}
                </div>
                <div>
                  <h3 className="text-sm font-semibold text-slate-950 dark:text-neutral-50">Preguntas faltantes</h3>
                  {result.missing_questions.length > 0 ? (
                    <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-slate-700 dark:text-neutral-300">
                      {result.missing_questions.map((question) => (
                        <li key={question}>{question}</li>
                      ))}
                    </ul>
                  ) : (
                    <p className="mt-2 text-sm text-slate-500 dark:text-neutral-400">Sin preguntas sugeridas.</p>
                  )}
                </div>
              </div>
            ) : (
              <p className="mt-4 text-sm leading-6 text-slate-500 dark:text-neutral-400">
                Captura hechos y ejecuta el análisis para ver artículos candidatos y
                advertencias.
              </p>
            )}
          </section>
        </section>

        {result ? (
          <InvestigationStepsSection
            steps={result.investigation_steps}
            detectedCrimeType={result.detected_crime_type}
          />
        ) : null}

        {result ? (
          <section className="rounded-md border border-slate-200 bg-white px-4 shadow-sm dark:border-neutral-700 dark:bg-neutral-900">
            {groupLabels.map((group) => (
              <ArticleGroup
                key={group.key}
                title={group.title}
                articles={result.candidate_articles[group.key]}
              />
            ))}

            <section className="border-t border-slate-200 dark:border-neutral-700">
              <CollapsibleSection title="Advertencias de revisión humana" defaultOpen={false}>
                <ul className="list-disc space-y-2 pl-5 pb-4 text-sm leading-6 text-slate-700 dark:text-neutral-300">
                  {result.candidate_articles.human_review_warnings.map((warning) => (
                    <li key={warning}>{warning}</li>
                  ))}
                </ul>
              </CollapsibleSection>
            </section>
          </section>
        ) : null}
      </div>
    </main>
  );
}
