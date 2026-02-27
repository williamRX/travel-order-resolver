import { useState } from "react";
import { Link } from "react-router-dom";
import { useProcessCsvMutation } from "../api/processCsv";
import {
  CsvPageWrapper,
  CsvContainer,
  CsvScrollContent,
  CsvHeader,
  CsvTitle,
  CsvSubtitle,
  BackLink,
  InfoBox,
  UploadSection,
  UploadSectionTitle,
  FileUpload,
  FileInputLabel,
  FileName,
  ProcessButton,
  CsvResults,
  CsvResultsTitle,
  ResultsPre,
  DownloadButton,
  Spinner,
} from "../styles/CsvUpload.css";

export const CsvUpload = () => {
  const [fileName, setFileName] = useState<string>("");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [resultContent, setResultContent] = useState<string | null>(null);
  const [downloadUrl, setDownloadUrl] = useState<string | null>(null);
  const [downloadFilename, setDownloadFilename] = useState<string>("results.csv");

  const processCsv = useProcessCsvMutation();

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      setFileName(
        `Fichier sélectionné: ${file.name} (${(file.size / 1024).toFixed(2)} KB)`,
      );
      setResultContent(null);
      setDownloadUrl(null);
    }
  };

  const handleProcess = async () => {
    if (!selectedFile) return;
    try {
      const result = await processCsv.mutateAsync(selectedFile);
      setResultContent(result.content);
      const blob = new Blob([result.content], {
        type: "text/csv;charset=utf-8;",
      });
      const url = URL.createObjectURL(blob);
      setDownloadUrl(url);
      setDownloadFilename(result.filename);
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Erreur lors du traitement";
      alert("Erreur lors du traitement: " + message);
    }
  };

  return (
    <CsvPageWrapper>
      <CsvContainer>
        <CsvScrollContent>
          <BackLink as={Link} to="/">
          ← Retour au chatbot
        </BackLink>

        <CsvHeader>
          <CsvTitle>📄 Traitement par fichier CSV</CsvTitle>
          <CsvSubtitle>
            Uploadez un fichier CSV pour traiter plusieurs phrases en une fois
          </CsvSubtitle>
        </CsvHeader>

        <InfoBox>
          <h3>📋 Format d'entrée</h3>
          <ul>
            <li>
              Format : <code>sentenceID,sentence</code> (une ligne par phrase)
            </li>
            <li>
              Exemple : <code>1,Je vais de Paris à Lyon</code>
            </li>
            <li>Le fichier doit être encodé en UTF-8</li>
          </ul>
        </InfoBox>

        <InfoBox>
          <h3>📤 Format de sortie</h3>
          <ul>
            <li>
              Phrase valide :{" "}
              <code>sentenceID,Departure,Step1,Step2,...,Destination</code>
            </li>
            <li>
              Phrase invalide : <code>sentenceID,INVALID</code>
            </li>
            <li>
              Si le pathfinding est activé, les étapes intermédiaires seront
              incluses
            </li>
          </ul>
        </InfoBox>

        <UploadSection>
          <UploadSectionTitle>📁 Sélectionner un fichier CSV</UploadSectionTitle>
          <FileUpload>
            <FileInputLabel>
              <input
                type="file"
                accept=".csv"
                onChange={handleFileSelect}
                aria-label="Choisir un fichier CSV"
              />
              📁 Choisir un fichier CSV
            </FileInputLabel>
            {fileName && <FileName>{fileName}</FileName>}
            <ProcessButton
              type="button"
              onClick={handleProcess}
              disabled={!selectedFile || processCsv.isPending}
            >
              {processCsv.isPending ? (
                <>
                  <Spinner />
                  Traitement en cours...
                </>
              ) : (
                "🔄 Traiter le fichier CSV"
              )}
            </ProcessButton>
          </FileUpload>
        </UploadSection>

        {resultContent != null && (
          <CsvResults>
            <CsvResultsTitle>📊 Résultats</CsvResultsTitle>
            <ResultsPre>{resultContent}</ResultsPre>
            {downloadUrl && (
              <DownloadButton
                href={downloadUrl}
                download={downloadFilename}
                onClick={() => {
                  setTimeout(() => URL.revokeObjectURL(downloadUrl), 100);
                }}
              >
                💾 Télécharger les résultats
              </DownloadButton>
            )}
          </CsvResults>
        )}
        </CsvScrollContent>
      </CsvContainer>
    </CsvPageWrapper>
  );
};
