import { useMemo, useState, useEffect } from "react";

export function usePagination<T>(items: T[], pageSize = 10) {
  const [page, setPage] = useState(1);
  const totalPages = Math.max(1, Math.ceil(items.length / pageSize));

  useEffect(() => {
    if (page > totalPages) {
      // Si la lista se filtra y la página actual queda fuera de rango,
      // vuelve a la 1. Es seguro: no depende de su propio resultado.
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setPage(1);
    }
  }, [totalPages, page]);

  const pageItems = useMemo(() => {
    const start = (page - 1) * pageSize;
    return items.slice(start, start + pageSize);
  }, [items, page, pageSize]);

  return { page, setPage, totalPages, pageItems, total: items.length };
}
