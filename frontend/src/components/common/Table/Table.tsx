import type { KeyboardEvent, ReactNode } from "react";
import "./Table.css";

export interface TableColumn<T> {
  key: string;
  label: string;
  render?: (row: T) => ReactNode;
}

interface TableProps<T> {
  columns: TableColumn<T>[];
  data: T[];
  keyExtractor: (row: T) => string | number;
  emptyMessage?: string;
  onRowClick?: (row: T) => void;
}

function readCell<T>(row: T, column: TableColumn<T>): ReactNode {
  if (column.render) return column.render(row);
  const value = (row as unknown as Record<string, unknown>)[column.key];
  return value === null || value === undefined || value === ""
    ? "—"
    : String(value);
}

function Table<T>({
  columns,
  data,
  keyExtractor,
  emptyMessage = "Sin datos disponibles",
  onRowClick,
}: TableProps<T>) {
  if (data.length === 0) {
    return <p className="table-empty">{emptyMessage}</p>;
  }

  const handleKey = (row: T) => (event: KeyboardEvent<HTMLElement>) => {
    if (event.key === "Enter" && onRowClick) onRowClick(row);
  };

  return (
    <div className="table-wrapper">
      <table className="table-desktop">
        <thead>
          <tr>
            {columns.map((column) => (
              <th key={column.key}>{column.label}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row) => (
            <tr
              key={keyExtractor(row)}
              className={onRowClick ? "table-row-clickable" : undefined}
              onClick={onRowClick ? () => onRowClick(row) : undefined}
              onKeyDown={onRowClick ? handleKey(row) : undefined}
              tabIndex={onRowClick ? 0 : undefined}
            >
              {columns.map((column) => (
                <td key={column.key}>{readCell(row, column)}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>

      <div className="table-mobile">
        {data.map((row) => (
          <div
            className={`table-card ${onRowClick ? "table-row-clickable" : ""}`}
            key={keyExtractor(row)}
            onClick={onRowClick ? () => onRowClick(row) : undefined}
            onKeyDown={onRowClick ? handleKey(row) : undefined}
            tabIndex={onRowClick ? 0 : undefined}
          >
            {columns.map((column) => (
              <div className="table-card-row" key={column.key}>
                <span className="table-card-label">{column.label}</span>
                <span className="table-card-value">
                  {readCell(row, column)}
                </span>
              </div>
            ))}
          </div>
        ))}
      </div>
    </div>
  );
}

export default Table;
