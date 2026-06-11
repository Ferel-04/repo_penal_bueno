"use client";

import Link from "next/link";
import React, { useEffect, useMemo, useRef, useState } from "react";
import { API_BASE_URL } from "../../api-url";
import ThemeToggle from "../../theme-toggle";
import {
  createReviewDraft,
  parseImportedReview,
  ReviewCatalogItem,
  ReviewDecision,
  ReviewPayload,
  ReviewRecord,
  ReviewStatus,
  toValidationRecord,
} from "./review-utils";

const statusLabels: Record<ReviewStatus, string> = {
  pending: "Pendiente",
  approved: "Aprobada",
  rejected: "Rechazada",
};

function shortHash(value?: string | null) {
  return value ? value.slice(0, 12) : "sin hash";
}

function statusClasses(status: ReviewStatus) {
  if (status === "approved") {
    return "border-emerald-300 bg-emerald-50 text-emerald-800 dark:border-emerald-700 dark:bg-emerald-950 dark:text-emerald-200";
  }
  if (status === "rejected") {
    return "border-red-300 bg-red-50 text-red-800 dark:border-red-700 dark:bg-red-950 dark:text-red-200";
  }
  return "border-amber-300 bg-amber-50 text-amber-800 dark:border-amber-700 dark:bg-amber-950 dark:text-amber-200";
}

function DiligenceReviewCard({
  item,
  decision,
  onChange,
}: {
  item: ReviewCatalogItem;
  decision: ReviewDecision;
  onChange: (decision: ReviewDecision) => void;
}) {
  const stale = decision.fingerprint !== item.review_fingerprint;

  function updateStatus(status: ReviewStatus) {
    onChange({ ...decision, fingerprint: item.review_fingerprint, status });
  }

  return (
    <article className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm dark:border-neutral-700 dark:bg-neutral-900">
      <div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <div className="flex flex-wrap items-center gap-2">
            <span className="font-mono text-xs text-slate-500 dark:text-neutral-400">
              {item.diligence_id}
            </span>
            <span
              className={`rounded border px-2 py-0.5 text-xs font-semibold ${
                item.display_group === "grounded"
                  ? "border-emerald-300 bg-emerald-50 text-emerald-800 dark:border-emerald-700 dark:bg-emerald-950 dark:text-emerald-200"
                  : "border-slate-300 bg-slate-50 text-slate-700 dark:border-neutral-600 dark:bg-neutral-800 dark:text-neutral-300"
              }`}
            >
              {item.display_group === "grounded" ? "Fuente verificada" : "Preliminar"}
            </span>
          </div>
          <h2 className="mt-2 text-lg font-semibold text-slate-950 dark:text-white">
            {item.step}
          </h2>
          {item.legal_basis ? (
            <p className="mt-1 text-sm text-slate-600 dark:text-neutral-300">
              {item.legal_basis}
            </p>
          ) : null}
        </div>
        <span className={`w-fit rounded border px-3 py-1 text-xs font-semibold ${statusClasses(decision.status)}`}>
          {statusLabels[decision.status]}
        </span>
      </div>

      {stale ? (
        <p className="mt-4 rounded border border-red-300 bg-red-50 p-3 text-sm text-red-800 dark:border-red-700 dark:bg-red-950 dark:text-red-200">
          La huella importada ya no coincide. Selecciona nuevamente una decision para
          vincularla con la version actual.
        </p>
      ) : null}

      <dl className="mt-4 grid gap-3 text-sm sm:grid-cols-2">
        <div>
          <dt className="font-semibold text-slate-800 dark:text-neutral-100">Finalidad</dt>
          <dd className="mt-1 text-slate-600 dark:text-neutral-300">{item.purpose}</dd>
        </div>
        <div>
          <dt className="font-semibold text-slate-800 dark:text-neutral-100">Condicion</dt>
          <dd className="mt-1 text-slate-600 dark:text-neutral-300">
            {item.applicability_condition}
          </dd>
        </div>
        <div>
          <dt className="font-semibold text-slate-800 dark:text-neutral-100">Autoridad</dt>
          <dd className="mt-1 text-slate-600 dark:text-neutral-300">
            {item.responsible_authority}
          </dd>
        </div>
        <div>
          <dt className="font-semibold text-slate-800 dark:text-neutral-100">
            Resultado esperado
          </dt>
          <dd className="mt-1 text-slate-600 dark:text-neutral-300">
            {item.expected_result}
          </dd>
        </div>
      </dl>

      <div className="mt-4 space-y-2">
        <h3 className="text-sm font-semibold text-slate-900 dark:text-neutral-100">
          Fundamentos
        </h3>
        {item.foundations.length > 0 ? (
          item.foundations.map((foundation) => (
            <div
              key={`${foundation.source_name}-${foundation.article_number}-${foundation.foundation_type}`}
              className="rounded border border-slate-200 bg-slate-50 p-3 text-xs text-slate-600 dark:border-neutral-700 dark:bg-neutral-800 dark:text-neutral-300"
            >
              <p className="font-semibold text-slate-900 dark:text-neutral-100">
                {foundation.source_name}, articulo {foundation.article_number}
                {foundation.fractions.length > 0
                  ? `, fracciones ${foundation.fractions.join(", ")}`
                  : ""}
              </p>
              <p className="mt-1">{foundation.reason}</p>
              <div className="mt-2 flex flex-wrap gap-3 font-mono text-[11px]">
                <span>Version: {foundation.source_version ?? "sin version"}</span>
                <span>Hash: {shortHash(foundation.content_hash)}</span>
                {foundation.source_url ? (
                  <a
                    href={foundation.source_url}
                    target="_blank"
                    rel="noreferrer"
                    className="font-sans font-semibold underline underline-offset-2"
                  >
                    Fuente oficial
                  </a>
                ) : null}
              </div>
            </div>
          ))
        ) : (
          <p className="rounded border border-amber-200 bg-amber-50 p-3 text-xs text-amber-800 dark:border-amber-800 dark:bg-amber-950 dark:text-amber-200">
            Sin fuente especifica suficiente. Aprobarla no cambia su clasificacion preliminar.
          </p>
        )}
      </div>

      <div className="mt-4 rounded border border-slate-200 p-4 dark:border-neutral-700">
        <fieldset>
          <legend className="text-sm font-semibold text-slate-900 dark:text-neutral-100">
            Dictamen
          </legend>
          <div className="mt-3 flex flex-wrap gap-2">
            {(["pending", "approved", "rejected"] as ReviewStatus[]).map((status) => (
              <label
                key={status}
                className={`cursor-pointer rounded border px-3 py-2 text-sm ${
                  decision.status === status
                    ? statusClasses(status)
                    : "border-slate-200 bg-white text-slate-600 dark:border-neutral-600 dark:bg-neutral-900 dark:text-neutral-300"
                }`}
              >
                <input
                  type="radio"
                  name={`status-${item.diligence_id}`}
                  checked={decision.status === status}
                  onChange={() => updateStatus(status)}
                  className="mr-2"
                />
                {statusLabels[status]}
              </label>
            ))}
          </div>
        </fieldset>
        <label className="mt-4 block text-sm font-semibold text-slate-900 dark:text-neutral-100">
          Observaciones
          <textarea
            value={decision.observations}
            onChange={(event) =>
              onChange({ ...decision, observations: event.target.value })
            }
            className="mt-2 min-h-24 w-full rounded border border-slate-300 bg-white p-3 font-normal text-slate-900 outline-none focus:border-slate-700 dark:border-neutral-600 dark:bg-neutral-800 dark:text-neutral-100"
            placeholder="Razones, condiciones o cambios requeridos..."
          />
        </label>
        <p className="mt-3 break-all font-mono text-[11px] text-slate-500 dark:text-neutral-400">
          Huella actual: {item.review_fingerprint}
        </p>
      </div>
    </article>
  );
}

export default function FamilyViolenceReviewPage() {
  const [payload, setPayload] = useState<ReviewPayload | null>(null);
  const [record, setRecord] = useState<ReviewRecord | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [validating, setValidating] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    async function loadReview() {
      try {
        const response = await fetch(`${API_BASE_URL}/review/family-violence`);
        const data = (await response.json()) as ReviewPayload & { detail?: string };
        if (!response.ok) {
          throw new Error(data.detail || "No se pudo cargar el catalogo de revision.");
        }
        setPayload(data);
        setRecord(createReviewDraft(data));
      } catch (requestError) {
        setError(
          requestError instanceof Error
            ? requestError.message
            : "No se pudo conectar con el backend local.",
        );
      } finally {
        setLoading(false);
      }
    }

    void loadReview();
  }, []);

  const decisionsById = useMemo(
    () => new Map(record?.decisions.map((decision) => [decision.diligence_id, decision])),
    [record],
  );

  function updateDecision(nextDecision: ReviewDecision) {
    if (!record) return;
    setRecord({
      ...record,
      decisions: record.decisions.map((decision) =>
        decision.diligence_id === nextDecision.diligence_id
          ? nextDecision
          : decision,
      ),
    });
    setMessage(null);
  }

  async function importDraft(file: File) {
    if (!payload) return;
    try {
      const imported = parseImportedReview(await file.text(), payload.catalog);
      setRecord(imported);
      setError(null);
      setMessage("Borrador importado. Revisa las huellas antes de validarlo.");
    } catch (importError) {
      setError(
        importError instanceof Error ? importError.message : "No se pudo importar el archivo.",
      );
    } finally {
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  }

  async function validateAndDownload() {
    if (!record) return;
    setValidating(true);
    setError(null);
    setMessage(null);

    try {
      const candidate = toValidationRecord(record);
      const response = await fetch(`${API_BASE_URL}/review/family-violence/validate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(candidate),
      });
      const data = (await response.json()) as {
        valid?: boolean;
        record?: ReviewRecord;
        detail?: string | Array<{ msg: string }>;
      };
      if (!response.ok || !data.record) {
        const detail = Array.isArray(data.detail)
          ? data.detail.map((item) => item.msg).join("; ")
          : data.detail;
        throw new Error(detail || "El registro no supero la validacion.");
      }

      const blob = new Blob([`${JSON.stringify(data.record, null, 2)}\n`], {
        type: "application/json",
      });
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = "family_violence.json";
      anchor.click();
      URL.revokeObjectURL(url);
      setRecord(data.record);
      setMessage("Registro validado y descargado. No se escribio ningun archivo en el servidor.");
    } catch (validationError) {
      setError(
        validationError instanceof Error
          ? validationError.message
          : "No se pudo validar el registro.",
      );
    } finally {
      setValidating(false);
    }
  }

  return (
    <main className="min-h-screen bg-slate-100 text-slate-950 dark:bg-neutral-950 dark:text-neutral-50">
      <div className="mx-auto w-full max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
        <header className="border-b border-slate-300 pb-5 dark:border-neutral-700">
          <div className="flex items-start justify-between gap-4">
            <div>
              <Link
                href="/"
                className="text-sm font-semibold text-slate-600 underline underline-offset-4 dark:text-neutral-300"
              >
                Volver al analisis
              </Link>
              <h1 className="mt-3 text-3xl font-semibold">
                Revision juridica: violencia familiar
              </h1>
              <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600 dark:text-neutral-300">
                Valida cada diligencia contra sus fundamentos y casos sinteticos. La
                descarga se genera localmente y debe incorporarse al repositorio mediante
                control de versiones.
              </p>
            </div>
            <ThemeToggle />
          </div>
        </header>

        {loading ? (
          <p className="py-10 text-sm text-slate-600 dark:text-neutral-300">
            Cargando catalogo...
          </p>
        ) : null}
        {error ? (
          <p className="mt-6 rounded border border-red-300 bg-red-50 p-4 text-sm text-red-800 dark:border-red-700 dark:bg-red-950 dark:text-red-200">
            {error}
          </p>
        ) : null}
        {message ? (
          <p className="mt-6 rounded border border-emerald-300 bg-emerald-50 p-4 text-sm text-emerald-800 dark:border-emerald-700 dark:bg-emerald-950 dark:text-emerald-200">
            {message}
          </p>
        ) : null}

        {payload && record ? (
          <>
            <section className="mt-6 rounded-lg border border-slate-200 bg-white p-5 shadow-sm dark:border-neutral-700 dark:bg-neutral-900">
              <div className="grid gap-4 md:grid-cols-2">
                <label className="text-sm font-semibold">
                  Nombre de la persona revisora
                  <input
                    value={record.reviewer_name}
                    onChange={(event) =>
                      setRecord({ ...record, reviewer_name: event.target.value })
                    }
                    className="mt-2 w-full rounded border border-slate-300 bg-white p-3 font-normal outline-none focus:border-slate-700 dark:border-neutral-600 dark:bg-neutral-800"
                    placeholder="Nombre completo"
                  />
                </label>
                <label className="text-sm font-semibold">
                  Fecha de revision
                  <input
                    type="datetime-local"
                    value={
                      record.reviewed_at
                        ? new Date(record.reviewed_at).toISOString().slice(0, 16)
                        : ""
                    }
                    onChange={(event) =>
                      setRecord({
                        ...record,
                        reviewed_at: event.target.value
                          ? new Date(event.target.value).toISOString()
                          : null,
                      })
                    }
                    className="mt-2 w-full rounded border border-slate-300 bg-white p-3 font-normal outline-none focus:border-slate-700 dark:border-neutral-600 dark:bg-neutral-800"
                  />
                </label>
              </div>
              <div className="mt-5 flex flex-wrap gap-3">
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="application/json,.json"
                  className="hidden"
                  onChange={(event) => {
                    const file = event.target.files?.[0];
                    if (file) void importDraft(file);
                  }}
                />
                <button
                  type="button"
                  onClick={() => fileInputRef.current?.click()}
                  className="rounded border border-slate-300 bg-white px-4 py-2 text-sm font-semibold hover:bg-slate-50 dark:border-neutral-600 dark:bg-neutral-800 dark:hover:bg-neutral-700"
                >
                  Importar borrador
                </button>
                <button
                  type="button"
                  disabled={validating}
                  onClick={() => void validateAndDownload()}
                  className="rounded bg-slate-950 px-4 py-2 text-sm font-semibold text-white hover:bg-slate-800 disabled:bg-slate-400 dark:bg-slate-50 dark:text-slate-950 dark:hover:bg-neutral-200"
                >
                  {validating ? "Validando..." : "Validar y descargar JSON"}
                </button>
              </div>
            </section>

            <section className="mt-8">
              <h2 className="text-xl font-semibold">Casos sinteticos de control</h2>
              <div className="mt-4 grid gap-4 lg:grid-cols-2">
                {payload.synthetic_cases.map((reviewCase) => (
                  <article
                    key={reviewCase.case_id}
                    className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm dark:border-neutral-700 dark:bg-neutral-900"
                  >
                    <p className="font-mono text-xs text-slate-500">{reviewCase.case_id}</p>
                    <h3 className="mt-1 font-semibold">{reviewCase.title}</h3>
                    <p className="mt-2 text-sm leading-6 text-slate-600 dark:text-neutral-300">
                      {reviewCase.facts}
                    </p>
                    <p className="mt-3 rounded border border-slate-200 bg-slate-50 p-3 text-xs leading-5 text-slate-700 dark:border-neutral-700 dark:bg-neutral-800 dark:text-neutral-300">
                      <span className="font-semibold">Criterio: </span>
                      {reviewCase.review_focus}
                    </p>
                  </article>
                ))}
              </div>
            </section>

            <section className="mt-8">
              <div className="flex flex-wrap items-end justify-between gap-3">
                <div>
                  <h2 className="text-xl font-semibold">Matriz de diligencias</h2>
                  <p className="mt-1 text-sm text-slate-600 dark:text-neutral-300">
                    {payload.catalog.length} diligencias sujetas a dictamen.
                  </p>
                </div>
                <p className="text-sm text-slate-600 dark:text-neutral-300">
                  Aprobadas:{" "}
                  {record.decisions.filter((item) => item.status === "approved").length} ·
                  Rechazadas:{" "}
                  {record.decisions.filter((item) => item.status === "rejected").length} ·
                  Pendientes:{" "}
                  {record.decisions.filter((item) => item.status === "pending").length}
                </p>
              </div>
              <div className="mt-4 space-y-5">
                {payload.catalog.map((item) => {
                  const decision = decisionsById.get(item.diligence_id);
                  return decision ? (
                    <DiligenceReviewCard
                      key={item.diligence_id}
                      item={item}
                      decision={decision}
                      onChange={updateDecision}
                    />
                  ) : (
                    <p
                      key={item.diligence_id}
                      className="rounded border border-red-300 bg-red-50 p-3 text-sm text-red-800"
                    >
                      Falta una decision para {item.diligence_id}.
                    </p>
                  );
                })}
              </div>
            </section>
          </>
        ) : null}
      </div>
    </main>
  );
}
