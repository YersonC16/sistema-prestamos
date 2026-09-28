import { useEffect, useRef, useState, useCallback } from "react";

interface UseFetchResult<T> {
  data: T | null;
  isLoading: boolean;
  error: string | null;
  refetch: () => void;
}

export function useFetch<T>(fetchFn: () => Promise<T>): UseFetchResult<T> {
  const [data, setData] = useState<T | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const isMounted = useRef(true);

  const load = useCallback(() => {
    setIsLoading(true);
    setError(null);

    fetchFn()
      .then((result) => {
        if (isMounted.current) setData(result);
      })
      .catch((err) => {
        if (isMounted.current)
          setError(err.message ?? "Error al cargar los datos");
      })
      .finally(() => {
        if (isMounted.current) setIsLoading(false);
      });
  }, [fetchFn]);

  useEffect(() => {
    isMounted.current = true;
    // Patrón estándar de fetching: setIsLoading/setError se ejecutan de forma
    // síncrona al iniciar la carga (para mostrar el Skeleton de inmediato).
    // No genera renders en cascada porque no depende de su propio resultado.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    load();

    return () => {
      isMounted.current = false;
    };
  }, [load]);

  return { data, isLoading, error, refetch: load };
}
