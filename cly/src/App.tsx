import { Routes, Route } from "react-router-dom";
import { AppContainer, AppContent } from "./styles/App.css";
import { useIsPortrait } from "./hooks/useIsPortrait";
import { Layout } from "./components/Layout";
import { CsvUpload } from "./components/CsvUpload";

export const App = () => {
  const isPortrait = useIsPortrait();
  return (
    <AppContainer>
      <Routes>
        <Route
          path="/"
          element={
            <AppContent $isPortrait={isPortrait}>
              <Layout />
            </AppContent>
          }
        />
        <Route path="/csv" element={<CsvUpload />} />
      </Routes>
    </AppContainer>
  );
};
