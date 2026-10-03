import Icon from "@/components/common/Icon";
import "./Pagination.css";

interface PaginationProps {
  page: number;
  totalPages: number;
  total: number;
  pageSize: number;
  onChange: (page: number) => void;
}

function Pagination({
  page,
  totalPages,
  total,
  pageSize,
  onChange,
}: PaginationProps) {
  if (total === 0) return null;

  const start = (page - 1) * pageSize + 1;
  const end = Math.min(page * pageSize, total);

  return (
    <div className="pagination">
      <span className="pagination-info">
        {start}–{end} de {total}
      </span>
      <div className="pagination-controls">
        <button
          className="pagination-btn"
          disabled={page === 1}
          onClick={() => onChange(page - 1)}
          aria-label="Página anterior"
        >
          <Icon name="arrowLeft" size={16} />
        </button>
        <span className="pagination-current">
          {page} / {totalPages}
        </span>
        <button
          className="pagination-btn"
          disabled={page === totalPages}
          onClick={() => onChange(page + 1)}
          aria-label="Página siguiente"
        >
          <Icon name="arrowRight" size={16} />
        </button>
      </div>
    </div>
  );
}

export default Pagination;
