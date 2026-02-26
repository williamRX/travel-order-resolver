import { useIsPortrait } from "../hooks/useIsPortrait";
import { LayoutContainer } from "../styles/Layout.css";
import { Hero } from "./Hero";
import { Chat } from "./Chat";

export const Layout = () => {
  const isPortrait = useIsPortrait();
  return (
    <LayoutContainer $isPortrait={isPortrait}>
      <Hero />
      <Chat />
    </LayoutContainer>
  );
};
