import "./Table.css";

export interface TableColumn<T> {
  key: keyof T;
  label: string;
  render?: (row: T) => React.ReactNode;
}

interface TableProps<T> {
  columns: TableColumn<T>[];
  data: T[];
  keyExtractor: (row: T) => string | number;
  emptyMessage?: string;
}

function Table<T>({
  columns,
  data,
  keyExtractor,
  emptyMessage = "Sin datos disponibles",
}: TableProps<T>) {
  if (data.length === 0) {
    return <p className="table-empty">{emptyMessage}</p>;
  }

  return (
    <div className="table-wrapper">
      <table className="table-desktop">
        <thead>
          <tr>
            {columns.map((col) => (
              <th key={String(col.key)}>{col.label}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row) => (
            <tr key={keyExtractor(row)}>
              {columns.map((col) => (
                <td key={String(col.key)}>
                  {col.render ? col.render(row) : String(row[col.key])}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>

      <div className="table-mobile">
        {data.map((row) => (
          <div className="table-card" key={keyExtractor(row)}>
            {columns.map((col) => (
              <div className="table-card-row" key={String(col.key)}>
                <span className="table-card-label">{col.label}</span>
                <span className="table-card-value">
                  {col.render ? col.render(row) : String(row[col.key])}
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
