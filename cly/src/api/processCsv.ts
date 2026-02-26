import { useMutation } from "@tanstack/react-query";
import { getApiBase } from "./client";

export interface ProcessCsvResult {
  /** Contenu CSV en texte (UTF-8). */
  content: string;
  /** Nom du fichier suggéré pour le téléchargement (ex. results_xxx.csv). */
  filename: string;
}

async function postProcessCsv(file: File): Promise<ProcessCsvResult> {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${getApiBase()}/process_csv`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    const detail = typeof data.detail === "string" ? data.detail : `HTTP ${res.status}`;
    throw new Error(detail);
  }

  const content = await res.text();
  const disposition = res.headers.get("Content-Disposition");
  const filename =
    disposition?.match(/filename=(.+)/)?.[1]?.replace(/^"|"$/g, "") ?? `results_${file.name}`;

  return { content, filename };
}

export function useProcessCsvMutation() {
  return useMutation({
    mutationFn: postProcessCsv,
  });
}
