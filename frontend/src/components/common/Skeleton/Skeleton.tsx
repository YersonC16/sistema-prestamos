import "./Skeleton.css";

interface SkeletonProps {
  width?: string;
  height?: string;
  borderRadius?: string;
}

function Skeleton({
  width = "100%",
  height = "16px",
  borderRadius = "4px",
}: SkeletonProps) {
  return <div className="skeleton" style={{ width, height, borderRadius }} />;
}

export default Skeleton;
