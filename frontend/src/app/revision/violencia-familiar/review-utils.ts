export type ReviewStatus = "pending" | "approved" | "rejected";

export type ReviewFoundation = {
  source_name: string;
  article_number: string;
  fractions: string[];
  foundation_type: string;
  reason: string;
  source_version?: string | null;
  last_reform_date?: string | null;
  source_url?: string | null;
  content_hash?: string | null;
};

export type ReviewCatalogItem = {
  diligence_id: string;
  step: string;
  legal_basis: string | null;
  display_group: "grounded" | "preliminary";
  foundation_status: "source_verified" | "unverified";
  legal_review_status: ReviewStatus;
  purpose: string;
  applicability_condition: string;
  responsible_authority: string;
  priority: string;
  expected_result: string;
  warnings: string[];
  foundations: ReviewFoundation[];
  review_fingerprint: string;
  review_is_current: boolean;
  review_observations: string;
};

export type SyntheticReviewCase = {
  case_id: string;
  title: string;
  facts: string;
  review_focus: string;
  expected_active_diligence_ids?: string[];
  expected_inactive_diligence_ids?: string[];
  expected_trigger?: string;
  expected_foundation?: string;
};

export type ReviewDecision = {
  diligence_id: string;
  fingerprint: string;
  status: ReviewStatus;
  observations: string;
};

export type ReviewRecord = {
  schema_version: 1;
  crime_type: "violencia_familiar";
  reviewer_name: string;
  reviewed_at: string | null;
  decisions: ReviewDecision[];
};

export type ReviewPayload = {
  schema_version: 1;
  crime_type: "violencia_familiar";
  catalog: ReviewCatalogItem[];
  synthetic_cases: SyntheticReviewCase[];
  stored_record: ReviewRecord;
};

export function createReviewDraft(payload: ReviewPayload): ReviewRecord {
  const stored = new Map(
    payload.stored_record.decisions.map((decision) => [decision.diligence_id, decision]),
  );

  return {
    schema_version: 1,
    crime_type: "violencia_familiar",
    reviewer_name: payload.stored_record.reviewer_name || "",
    reviewed_at: payload.stored_record.reviewed_at || new Date().toISOString(),
    decisions: payload.catalog.map((item) => {
      const decision = stored.get(item.diligence_id);
      const isCurrent = decision?.fingerprint === item.review_fingerprint;
      return {
        diligence_id: item.diligence_id,
        fingerprint: item.review_fingerprint,
        status: isCurrent ? decision.status : "pending",
        observations: isCurrent ? decision.observations : "",
      };
    }),
  };
}

export function parseImportedReview(
  text: string,
  catalog: ReviewCatalogItem[],
): ReviewRecord {
  const parsed: unknown = JSON.parse(text);
  if (!isRecord(parsed)) {
    throw new Error("El archivo no contiene un objeto JSON valido.");
  }
  if (parsed.schema_version !== 1 || parsed.crime_type !== "violencia_familiar") {
    throw new Error("El archivo no corresponde al esquema de violencia familiar.");
  }
  if (!Array.isArray(parsed.decisions)) {
    throw new Error("El archivo no contiene una lista de decisiones.");
  }

  const knownIds = new Set(catalog.map((item) => item.diligence_id));
  const decisions = parsed.decisions.map((value) => parseDecision(value, knownIds));
  if (new Set(decisions.map((decision) => decision.diligence_id)).size !== decisions.length) {
    throw new Error("El archivo contiene decisiones duplicadas.");
  }

  return {
    schema_version: 1,
    crime_type: "violencia_familiar",
    reviewer_name:
      typeof parsed.reviewer_name === "string" ? parsed.reviewer_name : "",
    reviewed_at:
      typeof parsed.reviewed_at === "string" ? parsed.reviewed_at : null,
    decisions,
  };
}

export function toValidationRecord(record: ReviewRecord): ReviewRecord {
  const reviewedAt = record.reviewed_at
    ? new Date(record.reviewed_at)
    : new Date();

  if (Number.isNaN(reviewedAt.getTime())) {
    throw new Error("La fecha de revision no es valida.");
  }

  return {
    ...record,
    reviewer_name: record.reviewer_name.trim(),
    reviewed_at: reviewedAt.toISOString(),
    decisions: record.decisions.map((decision) => ({
      ...decision,
      observations: decision.observations.trim(),
    })),
  };
}

function parseDecision(value: unknown, knownIds: Set<string>): ReviewDecision {
  if (!isRecord(value) || typeof value.diligence_id !== "string") {
    throw new Error("Una decision no tiene un identificador valido.");
  }
  if (!knownIds.has(value.diligence_id)) {
    throw new Error(`Diligencia desconocida: ${value.diligence_id}`);
  }
  if (
    value.status !== "pending" &&
    value.status !== "approved" &&
    value.status !== "rejected"
  ) {
    throw new Error(`Estado invalido para ${value.diligence_id}.`);
  }
  if (typeof value.fingerprint !== "string") {
    throw new Error(`Falta la huella de ${value.diligence_id}.`);
  }

  return {
    diligence_id: value.diligence_id,
    fingerprint: value.fingerprint,
    status: value.status,
    observations:
      typeof value.observations === "string" ? value.observations : "",
  };
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}
