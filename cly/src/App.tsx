import { AppContainer, AppContent } from "./styles/App.css";
import { useIsPortrait } from "./hooks/useIsPortrait";
import { Layout } from "./components/Layout";

export const App = () => {
  const isPortrait = useIsPortrait();
  return (
    <AppContainer>
      <AppContent $isPortrait={isPortrait}>
        <Layout />
      </AppContent>
    </AppContainer>
  );
};
