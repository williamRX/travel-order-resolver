import styled from "styled-components";

/* Même palette que Chat / Paramètres : blanc, noir, jaune, corail, turquoise, lavande */

/** Grille : 16 lignes, une ligne et une colonne de marge autour du contenu, l'intérieur scrollable */
export const CsvPageWrapper = styled.div`
  width: 100%;
  height: 100vh;
  background-color: #cc99ff;
  display: grid;
  grid-template-columns: 1fr minmax(0, 1000px) 1fr;
  grid-template-rows: 1fr repeat(14, minmax(0, 1fr)) 1fr;
  box-sizing: border-box;
`;

/** Cellule centrale : scrollable, spanne les lignes 2 à 16 (marge ligne 1 et 16) */
export const CsvContainer = styled.div`
  grid-column: 2;
  grid-row: 2 / 16;
  min-width: 0;
  min-height: 0;
  overflow-y: auto;
  overflow-x: hidden;
  background: #ffffff;
  border-radius: 20px;
  border: 4px solid #000000;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  box-sizing: border-box;
`;

/** Contenu à l'intérieur de la zone scrollable (padding ici pour ne pas couper les bords) */
export const CsvScrollContent = styled.div`
  padding: 40px;
  box-sizing: border-box;
`;

export const CsvHeader = styled.div`
  text-align: center;
  margin-bottom: 30px;
`;

export const CsvTitle = styled.h1`
  color: #cc99ff;
  font-size: 28px;
  margin-bottom: 10px;
  font-weight: bold;
  text-shadow:
    0 1px 0 #000000,
    1px 0 0 #000000,
    0 -1px 0 #000000,
    -1px 0 0 #000000;
`;

export const CsvSubtitle = styled.p`
  color: #000000;
  font-size: 16px;
`;

export const BackLink = styled.a`
  display: inline-block;
  margin-bottom: 20px;
  padding: 10px 20px;
  background: #ffffff;
  color: #cc99ff;
  text-decoration: none;
  border-radius: 12px;
  border: 2px solid #000000;
  font-weight: 600;
  transition:
    background 0.2s,
    color 0.2s;

  &:hover {
    background: #cc99ff;
    color: #ffffff;
  }
`;

export const InfoBox = styled.div`
  background: #ffffff;
  border: 2px solid #000000;
  border-left: 4px solid #cc99ff;
  padding: 15px;
  margin: 20px 0;
  border-radius: 12px;

  h3 {
    color: #cc99ff;
    margin-bottom: 10px;
    font-size: 16px;
    font-weight: bold;
  }

  ul {
    margin-left: 20px;
    color: #000000;
  }

  li {
    margin: 5px 0;
  }

  code {
    background: #ffffff;
    padding: 2px 6px;
    border-radius: 4px;
    border: 1px solid #000000;
    color: #000000;
  }
`;

export const UploadSection = styled.section`
  background: #ffffff;
  border: 2px solid #000000;
  border-radius: 14px;
  padding: 30px;
  margin-bottom: 30px;
`;

export const UploadSectionTitle = styled.h2`
  color: #cc99ff;
  margin-bottom: 20px;
  font-size: 22px;
  font-weight: bold;
`;

export const FileUpload = styled.div`
  display: flex;
  flex-direction: column;
  gap: 15px;
`;

export const FileInputLabel = styled.label`
  display: inline-block;
  padding: 15px 30px;
  background: #cc99ff;
  color: #ffffff;
  border-radius: 12px;
  border: 2px solid #000000;
  cursor: pointer;
  font-size: 16px;
  font-weight: bold;
  transition:
    transform 0.2s,
    box-shadow 0.2s;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  }

  input {
    position: absolute;
    opacity: 0;
    width: 0;
    height: 0;
  }
`;

export const FileName = styled.div`
  margin-top: 10px;
  color: #000000;
  font-size: 14px;
  padding: 10px 12px;
  background: #ffffff;
  border-radius: 12px;
  border: 2px solid #000000;
`;

export const ProcessButton = styled.button`
  padding: 14px 30px;
  background: #cc99ff;
  color: #ffffff;
  border: 2px solid #000000;
  border-radius: 14px;
  cursor: pointer;
  font-size: 16px;
  font-weight: bold;
  transition:
    transform 0.2s,
    box-shadow 0.2s;
  box-shadow: 0 2px 0 rgba(0, 0, 0, 0.1);

  &:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  }

  &:active:not(:disabled) {
    transform: translateY(0);
  }

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none;
  }
`;

export const CsvResults = styled.div`
  margin-top: 30px;
  padding: 20px;
  background: #ffffff;
  border-radius: 14px;
  border: 2px solid #000000;
  max-height: 500px;
  overflow-y: auto;
`;

export const CsvResultsTitle = styled.h3`
  color: #cc99ff;
  margin-bottom: 15px;
  font-size: 18px;
  font-weight: bold;
`;

export const ResultsPre = styled.pre`
  margin: 0;
  font-family: "Courier New", monospace;
  font-size: 13px;
  white-space: pre-wrap;
  word-wrap: break-word;
  background: #ffffff;
  padding: 15px;
  border-radius: 12px;
  border: 2px solid #000000;
  color: #000000;
`;

export const DownloadButton = styled.a`
  margin-top: 20px;
  padding: 12px 24px;
  background: #66ffcc;
  color: #000000;
  border: 2px solid #000000;
  border-radius: 14px;
  cursor: pointer;
  font-size: 16px;
  font-weight: bold;
  transition:
    transform 0.2s,
    box-shadow 0.2s;
  display: inline-block;
  text-decoration: none;
  box-shadow: 0 2px 0 rgba(0, 0, 0, 0.1);

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  }
`;

export const Spinner = styled.span`
  display: inline-block;
  width: 20px;
  height: 20px;
  border: 3px solid #000000;
  border-top: 3px solid #ffffff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-right: 10px;
  vertical-align: middle;

  @keyframes spin {
    0% {
      transform: rotate(0deg);
    }
    100% {
      transform: rotate(360deg);
    }
  }
`;
