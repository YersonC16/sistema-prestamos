import Skeleton from "./Skeleton";

interface SkeletonTableProps {
  rows?: number;
  columns?: number;
}

function SkeletonTable({ rows = 5, columns = 4 }: SkeletonTableProps) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
      {Array.from({ length: rows }).map((_, rowIndex) => (
        <div key={rowIndex} style={{ display: "flex", gap: "16px" }}>
          {Array.from({ length: columns }).map((_, colIndex) => (
            <Skeleton key={colIndex} height="20px" />
          ))}
        </div>
      ))}
    </div>
  );
}

export default SkeletonTable;
