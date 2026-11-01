"use client";

import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Download, FileText, ChevronDown } from "lucide-react";
import { AnalysisResult } from "@/lib/types";
import { api } from "@/lib/api";

export interface ExportReportButtonProps {
  result: AnalysisResult;
}

export function ExportReportButton({ result }: ExportReportButtonProps) {
  const [dropdownOpen, setDropdownOpen] = useState(false);

  const handleExportJson = () => {
    const dataStr =
      "data:text/json;charset=utf-8," +
      encodeURIComponent(JSON.stringify(result, null, 2));
    const downloadAnchor = document.createElement("a");
    downloadAnchor.setAttribute("href", dataStr);
    downloadAnchor.setAttribute(
      "download",
      `canopy-report-${result.analysis_id}.json`
    );
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
    setDropdownOpen(false);
  };

  const handleDownloadPdf = () => {
    const pdfUrl = api.getReportPdfUrl(result.analysis_id);
    window.open(pdfUrl, "_blank");
    setDropdownOpen(false);
  };

  return (
    <div className="relative inline-block text-left">
      <Button
        onClick={() => setDropdownOpen(!dropdownOpen)}
        variant="outline"
        size="sm"
        className="flex items-center gap-1.5 bg-white shadow-xs"
      >
        <Download className="h-4 w-4 text-green-700" />
        <span>Export Report</span>
        <ChevronDown className="h-3 w-3 text-gray-400" />
      </Button>

      {dropdownOpen && (
        <div
          className="absolute right-0 mt-2 w-48 rounded-xl bg-white shadow-xl border border-gray-100 py-1.5 z-50 animate-in fade-in zoom-in-95"
          onMouseLeave={() => setDropdownOpen(false)}
        >
          <button
            type="button"
            onClick={handleDownloadPdf}
            className="w-full flex items-center gap-2.5 px-4 py-2 text-xs font-medium text-gray-700 hover:bg-green-50 hover:text-green-700 text-left"
          >
            <FileText className="w-4 h-4 text-red-500" />
            <span>Download Audit PDF</span>
          </button>
          <button
            type="button"
            onClick={handleExportJson}
            className="w-full flex items-center gap-2.5 px-4 py-2 text-xs font-medium text-gray-700 hover:bg-green-50 hover:text-green-700 text-left"
          >
            <Download className="w-4 h-4 text-gray-400" />
            <span>Export Raw JSON</span>
          </button>
        </div>
      )}
    </div>
  );
}

export default ExportReportButton;
