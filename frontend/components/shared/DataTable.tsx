import React from "react";

export interface Column<T> {
  header: string;
  accessor: (item: T) => React.ReactNode;
  className?: string;
}

export interface DataTableProps<T> {
  data: T[];
  columns: Column<T>[];
  keyExtractor: (item: T) => string;
}

export function DataTable<T>({
  data,
  columns,
  keyExtractor,
}: DataTableProps<T>) {
  return (
    <div className="w-full overflow-x-auto rounded-card border border-border bg-white">
      <table className="w-full text-left text-sm">
        <thead className="bg-forest-50/50 text-xs uppercase text-slate border-b border-border">
          <tr>
            {columns.map((col, idx) => (
              <th key={idx} className={`px-4 py-3 font-semibold ${col.className || ""}`}>
                {col.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-border">
          {data.map((item) => (
            <tr key={keyExtractor(item)} className="hover:bg-muted/30">
              {columns.map((col, cIdx) => (
                <td key={cIdx} className={`px-4 py-3 ${col.className || ""}`}>
                  {col.accessor(item)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default DataTable;

