import { useCallback, useEffect, useRef, useState } from "react";
import { getErrorMessage } from "@/utils/errors";

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
  const requestId = useRef(0);

  const load = useCallback(() => {
    const currentRequest = ++requestId.current;
    const isCurrent = () =>
      isMounted.current && currentRequest === requestId.current;

    setIsLoading(true);
    setError(null);

    fetchFn()
      .then((result) => {
        if (isCurrent()) setData(result);
      })
      .catch((err: unknown) => {
        if (isCurrent())
          setError(getErrorMessage(err, "Error al cargar los datos"));
      })
      .finally(() => {
        if (isCurrent()) setIsLoading(false);
      });
  }, [fetchFn]);

  useEffect(() => {
    isMounted.current = true;
    // Patrón estándar de fetching: setIsLoading/setError se ejecutan de forma
    // síncrona al iniciar la carga para mostrar el Skeleton de inmediato.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    load();

    return () => {
      isMounted.current = false;
    };
  }, [load]);

  return { data, isLoading, error, refetch: load };
}
