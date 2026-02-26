import { QueryClient } from "@tanstack/react-query";

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      networkMode: "always",
      staleTime: 1000 * 60 * 15, // 15 minutes par défaut
      gcTime: 1000 * 60 * 30, // Garder en cache 30 minutes (anciennement cacheTime)
      retry: 3,
      refetchOnWindowFocus: false, // Éviter les refetch inutiles
      refetchInterval: 30 * 1000, // Refresh toutes les 30s
      placeholderData: (previousData: unknown) => previousData, // Ne pas remplacer par vide pendant le refetch
    },
    mutations: {
      networkMode: "always",
      retry: 0,
      onSuccess: () => {
        // TODO Add a default success toast when Toasts are reworked to be programmaticly triggered
      },
      onError: (error: Error) => {
        // TODO Add an error toast with automatic translation when Toasts are reworked to be programmaticly triggered
        // TODO Add handler to logout on unauthorized error (401)
        console.error(error);
      },
    },
  },
});
